"""
oc-flow 状态管理器测试
"""

import pytest
import sys
from pathlib import Path

# 添加 core 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from state_manager import state_manager, Task, Team, WorkerStatus


class TestStateManager:
    """状态管理器测试"""
    
    def test_singleton(self):
        """测试单例模式"""
        from state_manager import StateManager
        sm1 = StateManager()
        sm2 = StateManager()
        assert sm1 is sm2
    
    def test_create_team(self):
        """测试创建团队"""
        team = state_manager.create_team(
            name="test-team",
            task="测试任务",
            worker_count=3
        )
        assert team.name == "test-team"
        assert team.worker_count == 3
        assert team.status == "running"
    
    def test_register_worker(self):
        """测试注册工人"""
        worker = state_manager.register_worker(
            worker_id="test-worker-1",
            session_key="session-123"
        )
        assert worker.id == "test-worker-1"
        assert worker.status == "idle"
    
    def test_update_worker_status(self):
        """测试更新工人状态"""
        state_manager.register_worker("test-worker-2", "session-456")
        state_manager.update_worker_status("test-worker-2", "busy", "task-1")
        
        worker = state_manager.get_worker("test-worker-2")
        assert worker.status == "busy"
        assert worker.current_task == "task-1"
    
    def test_heartbeat(self):
        """测试心跳"""
        import time
        state_manager.register_worker("test-worker-3", "session-789")
        
        before = state_manager.get_worker("test-worker-3").last_heartbeat
        time.sleep(0.1)
        state_manager.heartbeat("test-worker-3")
        after = state_manager.get_worker("test-worker-3").last_heartbeat
        
        assert after > before
    
    def test_task_queue(self):
        """测试任务队列"""
        state_manager.create_queue("test-queue")
        
        task = Task(
            id="task-1",
            subject="测试任务",
            description="这是一个测试任务"
        )
        state_manager.add_task("test-queue", task)
        
        progress = state_manager.get_queue_progress("test-queue")
        assert progress["total"] == 1
        assert progress["pending"] == 1
    
    def test_get_state_summary(self):
        """测试获取状态摘要"""
        from state_manager import get_state_summary
        
        summary = get_state_summary()
        assert "active_teams" in summary
        assert "total_workers" in summary
        assert "idle_workers" in summary
        assert "busy_workers" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
