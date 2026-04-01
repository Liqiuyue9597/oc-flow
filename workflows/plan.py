"""
$plan - 任务分解工作流

功能：
1. 分析复杂任务
2. 分解为可执行的子任务
3. 创建飞书任务清单
4. 发送通知到飞书群
5. 自动识别 URL 并获取内容
"""

import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional
import json
import re


@dataclass
class SubTask:
    """子任务定义"""
    id: str
    title: str
    description: str
    estimated_minutes: int
    dependencies: List[str] = None
    assignee: Optional[str] = None
    
    def to_feishu_task(self) -> dict:
        """转换为飞书任务格式"""
        return {
            "summary": self.title,
            "description": self.description,
            "due": {
                "timestamp": int((datetime.now() + timedelta(minutes=self.estimated_minutes)).timestamp() * 1000)
            }
        }


def extract_urls(text: str) -> List[str]:
    """提取文本中的 URL"""
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.findall(url_pattern, text)

async def fetch_url_content(url: str) -> Optional[str]:
    """获取 URL 内容"""
    try:
        # 使用 subprocess 调用 web_fetch
        import subprocess
        result = subprocess.run(
            ['python3', '-c', f'''
import asyncio
from web_fetch import web_fetch

async def fetch():
    result = await web_fetch("{url}", extractMode="markdown")
    print(result.get("text", "")[:5000] if result else "")

asyncio.run(fetch())
            '''],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout.strip()
    except Exception as e:
        return f"无法获取内容：{e}"

async def analyze_task(task_description: str) -> dict:
    """
    分析任务描述
    
    返回：
    {
        "goal": str,  # 任务目标
        "requirements": List[str],  # 关键要求
        "deliverables": List[str],  # 交付物
        "complexity": str,  # low/medium/high
        "estimated_total_minutes": int,
        "context": dict  # 额外上下文（如 URL 内容）
    }
    """
    # 提取 URL
    urls = extract_urls(task_description)
    context = {}
    
    if urls:
        # 获取 URL 内容
        for url in urls:
            content = await fetch_url_content(url)
            if content:
                context[url] = content[:2000]  # 限制长度
    
    # 基于 URL 内容生成更准确的任务分析
    if urls:
        return {
            "goal": f"分析：{urls[0]}",
            "requirements": ["获取网页内容", "分析项目结构", "生成分析报告"],
            "deliverables": ["项目分析报告", "优化建议"],
            "complexity": "medium",
            "estimated_total_minutes": 30,
            "context": context
        }
    
    # 默认分析
    return {
        "goal": task_description[:50] + "...",
        "requirements": ["需求 1", "需求 2"],
        "deliverables": ["交付物 1"],
        "complexity": "medium",
        "estimated_total_minutes": 30,
        "context": context
    }


async def decompose_task(task_description: str, context: dict = None) -> List[SubTask]:
    """
    分解任务为子任务
    
    返回：
    List[SubTask] - 子任务列表
    """
    urls = extract_urls(task_description)
    
    # 如果有 URL，生成针对性的任务分解
    if urls and context:
        return [
            SubTask(
                id="task-1",
                title="访问并获取网页内容",
                description=f"获取 {urls[0]} 的内容",
                estimated_minutes=5,
                dependencies=[]
            ),
            SubTask(
                id="task-2",
                title="分析项目技术栈",
                description="识别使用的前端框架、后端技术、构建工具等",
                estimated_minutes=10,
                dependencies=["task-1"]
            ),
            SubTask(
                id="task-3",
                title="分析项目结构",
                description="查看文件目录结构、核心模块",
                estimated_minutes=10,
                dependencies=["task-1"]
            ),
            SubTask(
                id="task-4",
                title="评估代码质量",
                description="检查代码规范、测试覆盖、文档完整性",
                estimated_minutes=15,
                dependencies=["task-2", "task-3"]
            ),
            SubTask(
                id="task-5",
                title="生成分析报告",
                description="输出完整的项目分析报告",
                estimated_minutes=10,
                dependencies=["task-4"]
            ),
            SubTask(
                id="task-6",
                title="提供优化建议",
                description="根据分析结果提供改进建议",
                estimated_minutes=10,
                dependencies=["task-5"]
            )
        ]
    
    # 默认分解
    return [
        SubTask(
            id="task-1",
            title="分析需求",
            description="理解任务目标和关键要求",
            estimated_minutes=10,
            dependencies=[]
        ),
        SubTask(
            id="task-2",
            title="设计方案",
            description="制定实施方案",
            estimated_minutes=15,
            dependencies=["task-1"]
        ),
        SubTask(
            id="task-3",
            title="实现功能",
            description="按方案实现",
            estimated_minutes=30,
            dependencies=["task-2"]
        ),
        SubTask(
            id="task-4",
            title="测试验证",
            description="测试并修复问题",
            estimated_minutes=15,
            dependencies=["task-3"]
        )
    ]


async def plan_workflow(
    task_description: str,
    channel: Optional[str] = None
) -> dict:
    """
    完整的工作流规划
    
    参数：
    - task_description: 任务描述
    - channel: 飞书群 ID（可选）
    
    返回：
    {
        "tasklist_name": str,
        "tasklist_id": str,
        "subtasks": List[SubTask],
        "analysis": dict,
        "message": str
    }
    """
    from state_manager import state_manager
    
    # 1. 分析任务（包含 URL 获取）
    analysis = await analyze_task(task_description)
    
    # 2. 分解子任务（使用 context）
    subtasks = await decompose_task(task_description, analysis.get('context'))
    
    # 3. 创建任务队列
    tasklist_name = f"plan-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    state_manager.create_queue(tasklist_name)
    
    # 4. 添加任务到队列
    for subtask in subtasks:
        from state_manager import Task
        task = Task(
            id=subtask.id,
            subject=subtask.title,
            description=subtask.description
        )
        state_manager.add_task(tasklist_name, task)
    
    # 5. 生成消息
    message = f"✅ 已创建任务清单「{tasklist_name}」\n"
    message += f"📋 共 {len(subtasks)} 个子任务：\n"
    
    for i, subtask in enumerate(subtasks, 1):
        deps = f" (依赖：{', '.join(subtask.dependencies)})" if subtask.dependencies else ""
        message += f"  {i}. {subtask.title} - {subtask.estimated_minutes}分钟{deps}\n"
    
    message += f"\n⏱️ 预计总耗时：{analysis['estimated_total_minutes']}分钟"
    message += f"\n📊 复杂度：{analysis['complexity']}"
    
    return {
        "tasklist_name": tasklist_name,
        "tasklist_id": tasklist_name,  # 本地版本用名称作为 ID
        "subtasks": subtasks,
        "analysis": analysis,
        "message": message
    }


def format_plan_result(result: dict) -> str:
    """格式化规划结果为飞书消息卡片"""
    subtasks = result["subtasks"]
    analysis = result["analysis"]
    
    # 简化版：纯文本格式
    content = f"✅ **任务规划完成**\n\n"
    content += f"**目标：** {analysis['goal']}\n\n"
    content += f"**子任务清单：**\n"
    
    for i, task in enumerate(subtasks, 1):
        status = "⏸️" if task.dependencies else "✅"
        content += f"{status} {i}. **{task.title}**\n"
        content += f"   {task.description}\n"
        content += f"   ⏱️ {task.estimated_minutes}分钟\n\n"
    
    content += f"**预计总耗时：** {analysis['estimated_total_minutes']}分钟\n"
    content += f"**复杂度：** {analysis['complexity']}"
    
    return content


# ========== CLI 命令 ==========

async def cmd_plan(task_description: str, channel: Optional[str] = None):
    """$plan 命令入口"""
    print(f"📋 开始规划任务：{task_description}")
    
    result = await plan_workflow(task_description, channel)
    message = format_plan_result(result)
    
    print("\n" + message)
    
    # TODO: 发送到飞书群
    # if channel:
    #     await feishu.message.send(channel, message)
    
    return result


if __name__ == "__main__":
    # 测试
    asyncio.run(cmd_plan("实现 oc-flow 工作流层"))
