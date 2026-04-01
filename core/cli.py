"""
oc-flow CLI - 命令行接口

提供飞书机器人命令的本地模拟和测试
"""

import asyncio
import json
from datetime import datetime
from typing import Optional
from pathlib import Path


from state_manager import state_manager, get_state_summary, Task


# ========== 命令处理 ==========

async def cmd_status(args: str = ""):
    """/oc-flow status - 查看状态"""
    summary = get_state_summary()
    
    content = "📊 **oc-flow 状态**\n\n"
    content += f"**活跃团队：** {summary['active_teams']}\n"
    content += f"**总工人：** {summary['total_workers']}\n"
    content += f"**空闲：** {summary['idle_workers']} | **忙碌：** {summary['busy_workers']}\n"
    content += f"\n_更新时间：{summary['timestamp']}_\n"
    
    # 显示团队详情
    teams = state_manager.list_teams()
    if teams:
        content += "\n**团队列表：**\n"
        for team in teams:
            content += f"- {team.name}: {team.status} ({team.task})\n"
    
    print(content)
    return content


async def cmd_team_create(args: str):
    """/oc-flow team N:role "task" - 创建团队"""
    # 解析参数：3 "测试任务"
    import re
    match = re.match(r'(\d+)\s+"([^"]+)"', args)
    if not match:
        print(f"❌ 参数格式错误，应为：N \"task\"")
        return None
    
    n_workers = int(match.group(1))
    task = match.group(2)
    team_name = f"team-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    team = state_manager.create_team(team_name, task, n_workers)
    
    # 注册虚拟工人
    for i in range(n_workers):
        worker_id = f"{team_name}-worker-{i}"
        state_manager.register_worker(worker_id, f"session-{worker_id}")
    
    content = f"✅ **团队已启动**\n\n"
    content += f"**团队名称：** {team_name}\n"
    content += f"**任务：** {task}\n"
    content += f"**工人数量：** {n_workers}\n\n"
    content += "**工人列表：**\n"
    
    for i in range(n_workers):
        content += f"👷 Worker-{i}: 空闲\n"
    
    print(content)
    return content


async def cmd_team_status(args: str):
    """/oc-flow team status - 查看团队状态"""
    team_name = args.strip()
    team = state_manager.get_team(team_name)
    
    if not team:
        content = f"❌ 团队不存在：{team_name}"
        print(content)
        return content
    
    # 获取团队成员
    workers = [
        w for w in state_manager.workers.values()
        if w.id.startswith(team_name)
    ]
    
    content = f"📊 **团队状态：{team_name}**\n\n"
    content += f"**任务：** {team.task}\n"
    content += f"**状态：** {team.status}\n"
    content += f"**工人：** {len(workers)}\n\n"
    
    if workers:
        content += "**工人状态：**\n"
        for worker in workers:
            emoji = {"idle": "✅", "busy": "⏳", "stopped": "⏸️"}.get(worker.status, "❓")
            task_info = f" - {worker.current_task}" if worker.current_task else ""
            content += f"{emoji} {worker.id}: {worker.status}{task_info}\n"
    
    print(content)
    return content


async def cmd_team_shutdown(args: str):
    """/oc-flow team shutdown - 关闭团队"""
    team_name = args.strip()
    team = state_manager.get_team(team_name)
    
    if not team:
        content = f"❌ 团队不存在：{team_name}"
        print(content)
        return content
    
    state_manager.stop_team(team_name)
    
    # 停止所有工人
    for worker_id in list(state_manager.workers.keys()):
        if worker_id.startswith(team_name):
            state_manager.update_worker_status(worker_id, "stopped")
    
    content = f"✅ **团队已关闭**\n\n"
    content += f"团队：{team_name}\n"
    content += f"释放工人：{len([w for w in state_manager.workers if w.startswith(team_name)])}\n"
    
    print(content)
    return content


async def cmd_plan(args: str):
    """$plan - 任务规划"""
    from workflows.plan import plan_workflow, format_plan_result
    
    # 去除引号
    task_description = args.strip('"\'')
    result = await plan_workflow(task_description)
    message = format_plan_result(result)
    
    print(message)
    return message


async def cmd_ralph(args: str):
    """$ralph - 持久执行"""
    from workflows.ralph import ralph_execute, example_execute
    
    task_description = args.strip('"\'')
    task_id = f"ralph-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    content = f"✅ **已启动持久任务**\n\n"
    content += f"**任务 ID：** {task_id}\n"
    content += f"**任务：** {task_description}\n"
    content += f"**状态：** 运行中\n\n"
    content += "_执行中，请稍候..._\n"
    
    print(content)
    
    # 启动执行（示例用 5 步）
    await ralph_execute(
        task_id=task_id,
        task_description=task_description,
        total_steps=5,
        execute_func=example_execute
    )
    
    return content


# ========== 命令分发 ==========

COMMANDS = {
    "status": cmd_status,
    "team": cmd_team_create,
    "team status": cmd_team_status,
    "team shutdown": cmd_team_shutdown,
    "plan": cmd_plan,
    "ralph": cmd_ralph,
}


async def dispatch_command(command: str, *args, **kwargs):
    """分发命令到对应处理函数"""
    if command not in COMMANDS:
        print(f"❌ 未知命令：{command}")
        print(f"可用命令：{', '.join(COMMANDS.keys())}")
        return None
    
    handler = COMMANDS[command]
    return await handler(*args, **kwargs)


# ========== 主程序 ==========

async def main():
    """交互式 CLI"""
    print("=" * 60)
    print("oc-flow CLI - 输入命令或输入 'quit' 退出")
    print("=" * 60)
    print("\n可用命令:")
    print("  status                  - 查看状态")
    print("  team N \"task\"          - 创建团队")
    print("  team status <name>      - 查看团队状态")
    print("  team shutdown <name>    - 关闭团队")
    print("  plan \"description\"     - 任务规划")
    print("  ralph \"description\"    - 持久执行")
    print("=" * 60)
    
    while True:
        try:
            user_input = input("\noc-flow> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == "quit":
                print("👋 再见！")
                break
            
            # 解析命令
            parts = user_input.split(maxsplit=1)
            command = parts[0]
            args = parts[1] if len(parts) > 1 else ""
            
            # 执行命令
            if args:
                await dispatch_command(command, args)
            else:
                await dispatch_command(command)
            
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 错误：{e}")


if __name__ == "__main__":
    asyncio.run(main())
