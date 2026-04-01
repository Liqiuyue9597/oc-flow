"""
oc-flow 状态管理器

负责：
1. 本地状态读写（JSON）
2. 飞书多维表格同步（云端备份）
3. 日志记录
4. 心跳管理
"""

import json
import asyncio
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any


OC_FLOW_ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = OC_FLOW_ROOT / "state"
MEMORY_DIR = OC_FLOW_ROOT / "memory"
LOGS_DIR = OC_FLOW_ROOT / "logs"


@dataclass
class WorkerStatus:
    """工人状态"""
    id: str
    session_key: str
    status: str  # idle, busy, stopped
    current_task: Optional[str] = None
    last_heartbeat: str = ""
    completed_tasks: int = 0
    
    def __post_init__(self):
        if not self.last_heartbeat:
            self.last_heartbeat = datetime.now().isoformat()


@dataclass
class Task:
    """任务定义"""
    id: str
    subject: str
    description: str
    status: str = "pending"  # pending, in_progress, completed, failed
    assigned_to: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    result: Optional[str] = None


@dataclass
class Team:
    """团队定义"""
    name: str
    task: str
    worker_count: int
    status: str = "running"  # running, paused, stopped
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    workers: List[str] = field(default_factory=list)
    progress: Dict[str, Any] = field(default_factory=dict)


class StateManager:
    """状态管理器（单例）"""
    
    _instance: Optional['StateManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.teams: Dict[str, Team] = {}
        self.workers: Dict[str, WorkerStatus] = {}
        self.task_queues: Dict[str, List[Task]] = {}
        self._initialized = True
        
        # 加载现有状态
        self.load_state()
    
    def load_state(self):
        """从本地 JSON 加载状态"""
        try:
            # 加载团队状态
            teams_file = STATE_DIR / "active-teams.json"
            if teams_file.exists():
                data = json.loads(teams_file.read_text())
                self.teams = {
                    name: Team(**team_data) 
                    for name, team_data in data.get("teams", {}).items()
                }
            
            # 加载工人状态
            workers_file = STATE_DIR / "worker-status.json"
            if workers_file.exists():
                data = json.loads(workers_file.read_text())
                self.workers = {
                    wid: WorkerStatus(**w_data)
                    for wid, w_data in data.get("workers", {}).items()
                }
            
            # 加载任务队列
            queue_file = STATE_DIR / "task-queue.json"
            if queue_file.exists():
                data = json.loads(queue_file.read_text())
                self.task_queues = {
                    qname: [Task(**t) for t in tasks]
                    for qname, tasks in data.get("queues", {}).items()
                }
            
            self.log("State loaded")
        except Exception as e:
            self.log(f"Failed to load state: {e}", level="ERROR")
    
    def save_state(self):
        """保存状态到本地 JSON"""
        try:
            # 保存团队状态
            teams_data = {
                "teams": {name: asdict(team) for name, team in self.teams.items()},
                "last_updated": datetime.now().isoformat()
            }
            (STATE_DIR / "active-teams.json").write_text(
                json.dumps(teams_data, indent=2, ensure_ascii=False)
            )
            
            # 保存工人状态
            workers_data = {
                "workers": {wid: asdict(w) for wid, w in self.workers.items()},
                "last_updated": datetime.now().isoformat()
            }
            (STATE_DIR / "worker-status.json").write_text(
                json.dumps(workers_data, indent=2, ensure_ascii=False)
            )
            
            # 保存任务队列
            queue_data = {
                "queues": {
                    qname: [asdict(t) for t in tasks]
                    for qname, tasks in self.task_queues.items()
                },
                "last_updated": datetime.now().isoformat()
            }
            (STATE_DIR / "task-queue.json").write_text(
                json.dumps(queue_data, indent=2, ensure_ascii=False)
            )
            
            self.log("State saved")
        except Exception as e:
            self.log(f"Failed to save state: {e}", level="ERROR")
    
    def log(self, message: str, level: str = "INFO"):
        """记录日志"""
        timestamp = datetime.now().isoformat()
        log_file = LOGS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.log"
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
    
    # ========== 团队管理 ==========
    
    def create_team(self, name: str, task: str, worker_count: int) -> Team:
        """创建团队"""
        team = Team(name=name, task=task, worker_count=worker_count)
        self.teams[name] = team
        self.save_state()
        self.log(f"Team created: {name} ({worker_count} workers)")
        return team
    
    def get_team(self, name: str) -> Optional[Team]:
        """获取团队"""
        return self.teams.get(name)
    
    def list_teams(self) -> List[Team]:
        """列出所有团队"""
        return list(self.teams.values())
    
    def stop_team(self, name: str):
        """停止团队"""
        if name in self.teams:
            self.teams[name].status = "stopped"
            self.save_state()
            self.log(f"Team stopped: {name}")
    
    # ========== 工人管理 ==========
    
    def register_worker(self, worker_id: str, session_key: str) -> WorkerStatus:
        """注册工人"""
        worker = WorkerStatus(id=worker_id, session_key=session_key, status="idle")
        self.workers[worker_id] = worker
        self.save_state()
        self.log(f"Worker registered: {worker_id}")
        return worker
    
    def get_worker(self, worker_id: str) -> Optional[WorkerStatus]:
        """获取工人状态"""
        return self.workers.get(worker_id)
    
    def update_worker_status(
        self,
        worker_id: str,
        status: str,
        current_task: Optional[str] = None
    ):
        """更新工人状态"""
        if worker_id in self.workers:
            worker = self.workers[worker_id]
            worker.status = status
            worker.current_task = current_task
            worker.last_heartbeat = datetime.now().isoformat()
            if status == "idle" and current_task is None:
                worker.completed_tasks += 1
            self.save_state()
    
    def heartbeat(self, worker_id: str):
        """心跳更新"""
        if worker_id in self.workers:
            self.workers[worker_id].last_heartbeat = datetime.now().isoformat()
    
    def get_idle_workers(self) -> List[WorkerStatus]:
        """获取空闲工人"""
        return [w for w in self.workers.values() if w.status == "idle"]
    
    # ========== 任务管理 ==========
    
    def create_queue(self, queue_name: str):
        """创建任务队列"""
        if queue_name not in self.task_queues:
            self.task_queues[queue_name] = []
            self.save_state()
            self.log(f"Queue created: {queue_name}")
    
    def add_task(self, queue_name: str, task: Task):
        """添加任务到队列"""
        self.create_queue(queue_name)
        self.task_queues[queue_name].append(task)
        self.save_state()
        self.log(f"Task added to {queue_name}: {task.subject}")
    
    def claim_task(self, queue_name: str, worker_id: str) -> Optional[Task]:
        """工人认领任务"""
        if queue_name not in self.task_queues:
            return None
        
        queue = self.task_queues[queue_name]
        for task in queue:
            if task.status == "pending":
                task.status = "in_progress"
                task.assigned_to = worker_id
                self.save_state()
                self.log(f"Task claimed by {worker_id}: {task.subject}")
                return task
        
        return None
    
    def complete_task(self, queue_name: str, task_id: str, result: str):
        """完成任务"""
        if queue_name not in self.task_queues:
            return
        
        for task in self.task_queues[queue_name]:
            if task.id == task_id:
                task.status = "completed"
                task.completed_at = datetime.now().isoformat()
                task.result = result
                self.save_state()
                self.log(f"Task completed: {task.subject}")
                break
    
    def get_queue_progress(self, queue_name: str) -> Dict[str, int]:
        """获取队列进度"""
        if queue_name not in self.task_queues:
            return {}
        
        queue = self.task_queues[queue_name]
        return {
            "total": len(queue),
            "pending": sum(1 for t in queue if t.status == "pending"),
            "in_progress": sum(1 for t in queue if t.status == "in_progress"),
            "completed": sum(1 for t in queue if t.status == "completed"),
            "failed": sum(1 for t in queue if t.status == "failed"),
        }


# 全局单例
state_manager = StateManager()


# ========== 工具函数 ==========

def get_state_summary() -> Dict[str, Any]:
    """获取状态摘要（用于 /oc-flow status）"""
    teams = state_manager.list_teams()
    workers = list(state_manager.workers.values())
    
    return {
        "active_teams": len([t for t in teams if t.status == "running"]),
        "total_workers": len(workers),
        "idle_workers": len([w for w in workers if w.status == "idle"]),
        "busy_workers": len([w for w in workers if w.status == "busy"]),
        "timestamp": datetime.now().isoformat(),
    }


async def start_heartbeat_loop(worker_id: str, interval: int = 10):
    """启动心跳循环（后台任务）"""
    while True:
        state_manager.heartbeat(worker_id)
        await asyncio.sleep(interval)
