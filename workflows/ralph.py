"""
$ralph - 持久执行工作流

功能：
1. 启动长任务执行
2. 心跳循环（每 10 秒）
3. 状态持久化（每任务完成）
4. 断点续传（重启后恢复）
"""

import asyncio
import json
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Callable, Any
from pathlib import Path


@dataclass
class RalphState:
    """Ralph 执行状态"""
    task_id: str
    task_description: str
    status: str  # running, paused, completed, failed
    current_step: int = 0
    total_steps: int = 0
    progress_percent: int = 0
    last_heartbeat: str = ""
    checkpoint_data: dict = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if not self.last_heartbeat:
            self.last_heartbeat = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "task_description": self.task_description,
            "status": self.status,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "progress_percent": self.progress_percent,
            "last_heartbeat": self.last_heartbeat,
            "checkpoint_data": self.checkpoint_data or {},
            "error_message": self.error_message
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'RalphState':
        return cls(**data)


RALPH_STATE_DIR = Path(__file__).resolve().parent.parent / "state" / "ralph"


class RalphExecutor:
    """持久执行器"""
    
    def __init__(self):
        self.state: Optional[RalphState] = None
        self.running = False
        self._heartbeat_task: Optional[asyncio.Task] = None
    
    async def start(
        self,
        task_id: str,
        task_description: str,
        total_steps: int,
        execute_func: Callable,
        checkpoint_interval: int = 1
    ):
        """
        启动持久执行
        
        参数：
        - task_id: 任务 ID
        - task_description: 任务描述
        - total_steps: 总步骤数
        - execute_func: 执行函数 (async)
        - checkpoint_interval: 检查点间隔（每 N 步保存一次）
        """
        # 1. 初始化状态
        self.state = RalphState(
            task_id=task_id,
            task_description=task_description,
            status="running",
            total_steps=total_steps
        )
        
        # 2. 启动心跳循环
        self.running = True
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        # 3. 执行任务
        try:
            for step in range(total_steps):
                if not self.running:
                    print(f"⏸️ 任务已暂停：{task_id}")
                    break
                
                self.state.current_step = step
                self.state.progress_percent = int((step + 1) / total_steps * 100)
                
                # 执行步骤
                print(f"⏳ 执行步骤 {step + 1}/{total_steps}")
                result = await execute_func(step, self.state)
                
                # 保存检查点
                if (step + 1) % checkpoint_interval == 0:
                    self.state.checkpoint_data = {"last_result": result}
                    await self._save_state()
                    print(f"💾 已保存检查点：步骤 {step + 1}")
            
            # 完成
            self.state.status = "completed"
            self.state.progress_percent = 100
            await self._save_state()
            print(f"✅ 任务完成：{task_id}")
            
        except Exception as e:
            self.state.status = "failed"
            self.state.error_message = str(e)
            await self._save_state()
            print(f"❌ 任务失败：{task_id} - {e}")
            raise
        
        finally:
            self.running = False
            if self._heartbeat_task:
                self._heartbeat_task.cancel()
                try:
                    await self._heartbeat_task
                except asyncio.CancelledError:
                    pass
    
    async def _heartbeat_loop(self, interval: int = 10):
        """心跳循环"""
        while self.running:
            if self.state:
                self.state.last_heartbeat = datetime.now().isoformat()
                await self._save_state()
            await asyncio.sleep(interval)
    
    async def _save_state(self):
        """保存状态到文件"""
        if not self.state:
            return
        
        RALPH_STATE_DIR.mkdir(parents=True, exist_ok=True)
        state_file = RALPH_STATE_DIR / f"{self.state.task_id}.json"
        
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(self.state.to_dict(), f, indent=2, ensure_ascii=False)
    
    async def load_state(self, task_id: str) -> Optional[RalphState]:
        """从文件加载状态（用于恢复）"""
        state_file = RALPH_STATE_DIR / f"{task_id}.json"
        
        if not state_file.exists():
            return None
        
        with open(state_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        self.state = RalphState.from_dict(data)
        return self.state
    
    def pause(self):
        """暂停执行"""
        self.running = False
        if self.state:
            self.state.status = "paused"
    
    async def resume(self, execute_func: Callable):
        """恢复执行"""
        if not self.state or self.state.status != "paused":
            raise ValueError("没有可恢复的暂停任务")
        
        self.running = True
        self.state.status = "running"
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        try:
            # 从断点继续
            for step in range(self.state.current_step, self.state.total_steps):
                if not self.running:
                    break
                
                self.state.current_step = step
                self.state.progress_percent = int((step + 1) / self.state.total_steps * 100)
                
                print(f"⏳ 恢复执行：步骤 {step + 1}/{self.state.total_steps}")
                result = await execute_func(step, self.state)
                
                if (step + 1) % 5 == 0:
                    self.state.checkpoint_data = {"last_result": result}
                    await self._save_state()
            
            self.state.status = "completed"
            self.state.progress_percent = 100
            await self._save_state()
            
        except Exception as e:
            self.state.status = "failed"
            self.state.error_message = str(e)
            await self._save_state()
            raise
        
        finally:
            self.running = False
            if self._heartbeat_task:
                self._heartbeat_task.cancel()


async def ralph_execute(
    task_id: str,
    task_description: str,
    total_steps: int,
    execute_func: Callable,
    resume: bool = False
):
    """
    $ralph 命令入口
    
    参数：
    - task_id: 任务 ID
    - task_description: 任务描述
    - total_steps: 总步骤数
    - execute_func: 执行函数
    - resume: 是否恢复之前的任务
    """
    executor = RalphExecutor()
    
    if resume:
        # 恢复之前的任务
        state = await executor.load_state(task_id)
        if state and state.status == "paused":
            print(f"💾 恢复任务：{task_id} (进度：{state.progress_percent}%)")
            await executor.resume(execute_func)
        else:
            print(f"⚠️ 没有可恢复的任务，重新开始")
            await executor.start(task_id, task_description, total_steps, execute_func)
    else:
        # 新任务
        await executor.start(task_id, task_description, total_steps, execute_func)


# ========== 示例用法 ==========

async def example_execute(step: int, state: RalphState):
    """示例执行函数"""
    await asyncio.sleep(2)  # 模拟工作
    print(f"  完成步骤 {step + 1}")
    return f"步骤 {step + 1} 结果"


if __name__ == "__main__":
    # 测试
    async def main():
        await ralph_execute(
            task_id="test-ralph-1",
            task_description="测试持久执行",
            total_steps=5,
            execute_func=example_execute
        )
    
    asyncio.run(main())
