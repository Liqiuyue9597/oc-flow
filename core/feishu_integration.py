"""
oc-flow 飞书集成

功能：
1. 飞书多维表格同步（状态备份）
2. 飞书消息卡片（状态展示）
3. 飞书机器人命令（CLI 集成）
"""

import json
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List


# ========== 飞书多维表格 Schema ==========

BITABLE_SCHEMA = {
    "teams": {
        "table_name": "团队状态",
        "fields": {
            "team_name": {"type": 1, "name": "团队名称"},  # 1 = 文本
            "task": {"type": 1, "name": "任务"},
            "worker_count": {"type": 2, "name": "工人数量"},  # 2 = 数字
            "status": {"type": 3, "name": "状态", "options": ["running", "paused", "stopped"]},  # 3 = 单选
            "created_at": {"type": 5, "name": "创建时间"},  # 5 = 日期
            "progress": {"type": 1, "name": "进度 (JSON)"}
        }
    },
    "workers": {
        "table_name": "工人状态",
        "fields": {
            "worker_id": {"type": 1, "name": "工人 ID"},
            "team_name": {"type": 1, "name": "所属团队"},
            "status": {"type": 3, "name": "状态", "options": ["idle", "busy", "stopped"]},
            "current_task": {"type": 1, "name": "当前任务"},
            "last_heartbeat": {"type": 5, "name": "最后心跳"},
            "completed_tasks": {"type": 2, "name": "完成任务数"}
        }
    },
    "tasks": {
        "table_name": "任务队列",
        "fields": {
            "task_id": {"type": 1, "name": "任务 ID"},
            "queue_name": {"type": 1, "name": "队列名称"},
            "subject": {"type": 1, "name": "主题"},
            "status": {"type": 3, "name": "状态", "options": ["pending", "in_progress", "completed", "failed"]},
            "assigned_to": {"type": 1, "name": "分配给"},
            "created_at": {"type": 5, "name": "创建时间"},
            "result": {"type": 1, "name": "结果"}
        }
    }
}


# ========== 消息卡片模板 ==========

def create_status_card(summary: Dict[str, Any]) -> dict:
    """
    创建状态卡片（飞书消息格式）
    
    返回飞书消息卡片 JSON
    """
    return {
        "config": {
            "wide_screen_mode": True
        },
        "header": {
            "template": "blue",
            "title": {
                "content": "📊 oc-flow 状态",
                "tag": "plain_text"
            }
        },
        "elements": [
            {
                "tag": "div",
                "fields": [
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**活跃团队**\n{summary['active_teams']}"
                        }
                    },
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**总工人**\n{summary['total_workers']}"
                        }
                    },
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**空闲**\n{summary['idle_workers']}"
                        }
                    },
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**忙碌**\n{summary['busy_workers']}"
                        }
                    }
                ]
            },
            {
                "tag": "hr"
            },
            {
                "tag": "note",
                "elements": [
                    {
                        "tag": "plain_text",
                        "content": f"更新时间：{summary['timestamp']}"
                    }
                ]
            }
        ]
    }


def create_team_status_card(team_name: str, team_data: dict, workers: List[dict]) -> dict:
    """创建团队状态卡片"""
    worker_lines = []
    for worker in workers:
        emoji = {"idle": "✅", "busy": "⏳", "stopped": "⏸️"}.get(worker.get("status", ""), "❓")
        task_info = f" - {worker.get('current_task', '')}" if worker.get("current_task") else ""
        worker_lines.append(f"{emoji} {worker['worker_id']}: {worker['status']}{task_info}")
    
    return {
        "config": {
            "wide_screen_mode": True
        },
        "header": {
            "template": "green",
            "title": {
                "content": f"👥 团队：{team_name}",
                "tag": "plain_text"
            }
        },
        "elements": [
            {
                "tag": "div",
                "fields": [
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**任务**\n{team_data.get('task', 'N/A')}"
                        }
                    },
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**状态**\n{team_data.get('status', 'unknown')}"
                        }
                    },
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**工人**\n{len(workers)}"
                        }
                    }
                ]
            },
            {
                "tag": "divider"
            },
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "\n".join(worker_lines) if worker_lines else "暂无工人"
                }
            }
        ]
    }


def create_plan_result_card(result: dict) -> dict:
    """创建任务规划结果卡片"""
    subtasks = result.get("subtasks", [])
    analysis = result.get("analysis", {})
    
    task_lines = []
    for i, task in enumerate(subtasks, 1):
        deps = f" (依赖：{', '.join(task.get('dependencies', []))})" if task.get("dependencies") else ""
        task_lines.append(f"{i}. **{task['title']}**{deps}")
        task_lines.append(f"   {task['description']}")
        task_lines.append(f"   ⏱️ {task['estimated_minutes']}分钟\n")
    
    return {
        "config": {
            "wide_screen_mode": True
        },
        "header": {
            "template": "blue",
            "title": {
                "content": "✅ 任务规划完成",
                "tag": "plain_text"
            }
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**目标：** {analysis.get('goal', 'N/A')}\n\n**子任务清单：**\n" + "\n".join(task_lines)
                }
            },
            {
                "tag": "hr"
            },
            {
                "tag": "div",
                "fields": [
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**预计耗时**\n{analysis.get('estimated_total_minutes', 0)}分钟"
                        }
                    },
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**复杂度**\n{analysis.get('complexity', 'unknown')}"
                        }
                    }
                ]
            }
        ]
    }


def create_ralph_progress_card(state: dict) -> dict:
    """创建 Ralph 执行进度卡片"""
    progress = state.get("progress_percent", 0)
    current = state.get("current_step", 0)
    total = state.get("total_steps", 0)
    
    # 进度条
    bar_length = 20
    filled = int(bar_length * progress / 100)
    progress_bar = "█" * filled + "░" * (bar_length - filled)
    
    return {
        "config": {
            "wide_screen_mode": True
        },
        "header": {
            "template": "orange" if progress < 100 else "green",
            "title": {
                "content": "🔄 持久执行中" if progress < 100 else "✅ 执行完成",
                "tag": "plain_text"
            }
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**任务：** {state.get('task_description', 'N/A')}\n\n"
                }
            },
            {
                "tag": "progress_bar",
                "progress": progress,
                "color": "green" if progress == 100 else "blue"
            },
            {
                "tag": "div",
                "fields": [
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**进度**\n{progress_bar}\n{current}/{total}"
                        }
                    },
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**状态**\n{state.get('status', 'unknown')}"
                        }
                    }
                ]
            },
            {
                "tag": "hr"
            },
            {
                "tag": "note",
                "elements": [
                    {
                        "tag": "plain_text",
                        "content": f"最后心跳：{state.get('last_heartbeat', 'N/A')}"
                    }
                ]
            }
        ]
    }


# ========== 飞书 API 封装 ==========

class FeishuIntegration:
    """飞书集成类"""
    
    def __init__(self, app_token: Optional[str] = None):
        """
        初始化飞书集成
        
        参数：
        - app_token: 飞书多维表格 Token（可选）
        """
        self.app_token = app_token
        self.bitable_tables = {}  # 缓存表 ID
    
    async def init_bitable(self) -> bool:
        """
        初始化多维表格（创建表结构）
        
        使用 feishu_bitable_app_table 工具
        """
        if not self.app_token:
            print("⚠️ 未配置多维表格 Token，跳过初始化")
            return False
        
        try:
            # 导入飞书工具
            from feishu_bitable_app_table import feishu_bitable_app_table
            
            # 创建/获取表
            for key, schema in BITABLE_SCHEMA.items():
                # 检查表是否存在（简化处理：直接创建）
                result = feishu_bitable_app_table(
                    action="create",
                    app_token=self.app_token,
                    table={
                        "name": schema["table_name"],
                        "fields": [
                            {"field_name": field["name"], "type": field["type"]}
                            for field in schema["fields"].values()
                        ]
                    }
                )
                
                if result and "table_id" in result:
                    self.bitable_tables[key] = result["table_id"]
                    print(f"✅ 创建表：{schema['table_name']} ({result['table_id']})")
            
            return True
        except Exception as e:
            print(f"❌ 初始化多维表格失败：{e}")
            return False
    
    async def sync_team_to_bitable(self, team) -> Optional[str]:
        """同步团队到多维表格"""
        if not self.app_token or "teams" not in self.bitable_tables:
            return None
        
        try:
            from feishu_bitable_app_table_record import feishu_bitable_app_table_record
            
            record_id = feishu_bitable_app_table_record(
                action="create",
                app_token=self.app_token,
                table_id=self.bitable_tables["teams"],
                fields={
                    "团队名称": team.name,
                    "任务": team.task,
                    "工人数量": team.worker_count,
                    "状态": team.status,
                    "创建时间": int(datetime.fromisoformat(team.created_at).timestamp() * 1000),
                    "进度 (JSON)": json.dumps(team.progress, ensure_ascii=False) if team.progress else ""
                }
            )
            
            print(f"  同步团队：{team.name} → {record_id}")
            return record_id
        except Exception as e:
            print(f"  ❌ 同步团队失败：{e}")
            return None
    
    async def sync_worker_to_bitable(self, worker_id: str, worker) -> Optional[str]:
        """同步工人到多维表格"""
        if not self.app_token or "workers" not in self.bitable_tables:
            return None
        
        try:
            from feishu_bitable_app_table_record import feishu_bitable_app_table_record
            
            record_id = feishu_bitable_app_table_record(
                action="create",
                app_token=self.app_token,
                table_id=self.bitable_tables["workers"],
                fields={
                    "工人 ID": worker.id,
                    "所属团队": worker_id.split("-")[0] if "-" in worker_id else "unknown",
                    "状态": worker.status,
                    "当前任务": worker.current_task or "",
                    "最后心跳": int(datetime.fromisoformat(worker.last_heartbeat).timestamp() * 1000),
                    "完成任务数": worker.completed_tasks
                }
            )
            
            print(f"  同步工人：{worker_id} → {record_id}")
            return record_id
        except Exception as e:
            print(f"  ❌ 同步工人失败：{e}")
            return None
    
    async def sync_state_to_bitable(self, state_manager):
        """
        同步状态到多维表格
        
        参数：
        - state_manager: 状态管理器实例
        """
        if not self.app_token:
            print("⚠️ 未配置多维表格 Token，跳过同步")
            return
        
        # 初始化（如果还没初始化）
        if not self.bitable_tables:
            await self.init_bitable()
        
        if not self.bitable_tables:
            return
        
        print("📊 开始同步状态到多维表格...")
        
        # 同步团队
        teams = state_manager.list_teams()
        for team in teams:
            await self.sync_team_to_bitable(team)
        
        # 同步工人
        for worker_id, worker in state_manager.workers.items():
            await self.sync_worker_to_bitable(worker_id, worker)
        
        print("✅ 状态同步完成")
    
    async def send_card(self, channel: str, card: dict, msg_type: str = "interactive") -> bool:
        """
        发送卡片到飞书群
        
        参数：
        - channel: 飞书群 ID (oc_xxx)
        - card: 卡片 JSON
        - msg_type: 消息类型
        
        使用 feishu_im_user_message 工具
        """
        try:
            from feishu_im_user_message import feishu_im_user_message
            
            result = feishu_im_user_message(
                action="send",
                msg_type=msg_type,
                receive_id_type="chat_id",
                receive_id=channel,
                content=json.dumps(card, ensure_ascii=False)
            )
            
            print(f"✅ 发送卡片到 {channel}")
            return True
        except Exception as e:
            print(f"❌ 发送卡片失败：{e}")
            return False
    
    async def send_text(self, channel: str, text: str) -> bool:
        """发送文本消息到飞书群"""
        try:
            from feishu_im_user_message import feishu_im_user_message
            
            result = feishu_im_user_message(
                action="send",
                msg_type="text",
                receive_id_type="chat_id",
                receive_id=channel,
                content=json.dumps({"text": text}, ensure_ascii=False)
            )
            
            print(f"✅ 发送文本到 {channel}")
            return True
        except Exception as e:
            print(f"❌ 发送文本失败：{e}")
            return False


# ========== 飞书机器人命令处理 ==========

async def handle_feishu_command(command: str, args: str, channel: str) -> Optional[str]:
    """
    处理飞书机器人命令
    
    参数：
    - command: 命令名（如 "status", "team"）
    - args: 命令参数
    - channel: 飞书群 ID
    
    返回：消息 ID
    """
    from cli import dispatch_command
    
    feishu = FeishuIntegration()
    
    try:
        # 执行命令
        result = await dispatch_command(command, args)
        
        # 根据命令类型发送不同格式的消息
        if command == "status":
            from state_manager import get_state_summary
            summary = get_state_summary()
            card = create_status_card(summary)
            await feishu.send_card(channel, card)
        
        elif command == "plan":
            from workflows.plan import plan_workflow, format_plan_result
            result = await plan_workflow(args)
            card = create_plan_result_card(result)
            await feishu.send_card(channel, card)
        
        elif command == "ralph":
            # Ralph 命令会异步执行，先发送确认消息
            await feishu.send_text(channel, f"🚀 已启动持久任务：{args}")
            # 实际执行在后台进行
        
        else:
            # 纯文本回复
            if result:
                await feishu.send_text(channel, result)
        
        return result
    
    except Exception as e:
        error_msg = f"❌ 命令执行失败：{e}"
        await feishu.send_text(channel, error_msg)
        return None


# ========== Ralph 状态推送 ==========

async def push_ralph_progress(channel: str, state: dict):
    """
    推送 Ralph 执行进度到飞书
    
    参数：
    - channel: 飞书群 ID
    - state: Ralph 状态字典
    """
    feishu = FeishuIntegration()
    card = create_ralph_progress_card(state)
    await feishu.send_card(channel, card)


# ========== 快捷函数 ==========

async def sync_to_feishu(channel: Optional[str] = None):
    """快捷同步到飞书"""
    from state_manager import state_manager
    
    feishu = FeishuIntegration()
    
    # 同步到多维表格
    await feishu.sync_state_to_bitable(state_manager)
    
    # 发送状态卡片到群
    if channel:
        from state_manager import get_state_summary
        summary = get_state_summary()
        card = create_status_card(summary)
        await feishu.send_card(channel, card)


# ========== 配置示例 ==========

def get_feishu_config_from_env() -> dict:
    """从环境变量获取飞书配置"""
    import os
    
    return {
        "app_token": os.getenv("OC_FLOW_BITABLE_TOKEN"),
        "channel": os.getenv("OC_FLOW_FEISHU_CHANNEL"),
        "log_level": os.getenv("OC_FLOW_LOG_LEVEL", "INFO")
    }


if __name__ == "__main__":
    # 测试
    async def test():
        feishu = FeishuIntegration()
        
        # 测试卡片创建
        summary = {
            "active_teams": 1,
            "total_workers": 3,
            "idle_workers": 2,
            "busy_workers": 1,
            "timestamp": datetime.now().isoformat()
        }
        
        card = create_status_card(summary)
        print("✅ 状态卡片创建成功")
        print(json.dumps(card, indent=2, ensure_ascii=False)[:500])
    
    asyncio.run(test())
