# oc-flow 与 OpenClaw 集成指南

> 让 OpenClaw 从"单轮对话"变成"长周期任务执行"

---

## 🎯 集成价值

| OpenClaw 原有能力 | + oc-flow 后 |
|------------------|-------------|
| 单轮对话，无法跟踪长任务 | ✅ 持久化状态，支持跨天任务 |
| 每次重启丢失上下文 | ✅ 断点续传，重启后恢复 |
| 只能串行执行 | ✅ 多团队并行，任务队列 |
| 状态不透明 | ✅ 飞书多维表格实时查看 |
| 重复任务每次重说 | ✅ Agent 角色复用，工作流模板 |

---

## 📦 安装方式

### 方式 1：作为 OpenClaw Skill（推荐）

将 oc-flow 安装为 OpenClaw 的自定义技能：

```bash
# 1. 克隆到 OpenClaw skills 目录
cd ~/.openclaw/workspace/skills
git clone https://github.com/Liqiuyue9597/oc-flow.git

# 2. 创建技能入口
ln -s oc-flow/core/cli.py ocflow

# 3. 安装依赖
cd oc-flow
pip install -r requirements.txt
```

**使用方式：**
```bash
# 在 OpenClaw 对话中
/ocflow status
/ocflow plan "任务描述"
/ocflow ralph "长任务"
```

---

### 方式 2：作为独立服务

将 oc-flow 作为后台服务运行，OpenClaw 通过 CLI 调用：

```bash
# 1. 安装到独立目录
git clone https://github.com/Liqiuyue9597/oc-flow.git /opt/oc-flow
cd /opt/oc-flow
pip install -r requirements.txt

# 2. 创建系统命令
ln -s /opt/oc-flow/core/cli.py /usr/local/bin/ocflow

# 3. 配置环境变量
echo "export OC_FLOW_BITABLE_TOKEN=xxxxx" >> ~/.bashrc
echo "export OC_FLOW_FEISHU_CHANNEL=oc_xxx" >> ~/.bashrc
```

**使用方式：**
```bash
# 在 OpenClaw 对话中通过 exec 调用
exec ocflow status
exec ocflow plan "任务"
```

---

### 方式 3：集成到 OpenClaw 网关（高级）

将 oc-flow 集成到 OpenClaw Gateway，作为原生命令：

```bash
# 1. 复制核心模块到 OpenClaw
cp -r oc-flow/core ~/.openclaw/core/ocflow
cp -r oc-flow/workflows ~/.openclaw/workflows/

# 2. 在 Gateway 中注册命令
# 编辑 ~/.openclaw/gateway/config.py
COMMANDS['ocflow'] = '~/.openclaw/core/ocflow/cli.py'
```

---

## 🔧 配置方式

### 环境变量配置

在 OpenClaw Gateway 环境中配置：

```bash
# 编辑 Gateway 环境
openclaw gateway env set OC_FLOW_BITABLE_TOKEN=xxxxx
openclaw gateway env set OC_FLOW_FEISHU_CHANNEL=oc_xxx
openclaw gateway env set OC_FLOW_LOG_LEVEL=INFO

# 重启 Gateway
openclaw gateway restart
```

### 配置文件方式

创建 `~/.openclaw/workspace/.ocflow/config.json`：

```json
{
  "feishu": {
    "bitable_token": "xxxxx",
    "channel": "oc_xxx"
  },
  "limits": {
    "max_concurrent_teams": 5,
    "heartbeat_interval": 10
  },
  "logging": {
    "level": "INFO",
    "retention_days": 7
  }
}
```

---

## 💡 使用场景

### 场景 1：在 OpenClaw 中启动长任务

**传统方式：**
```
用户：帮我分析 100 个 GitHub 项目

Act: 好的，开始分析...
（执行到第 37 个，服务器重启）
（进度丢失，需要重新开始）
```

**使用 oc-flow：**
```
用户：$ralph 分析 100 个 GitHub 项目

Act: ✅ 已启动持久任务
  任务 ID：ralph-20260401-104100
  进度：37/100
  💾 状态已保存

（服务器重启）

用户：继续之前的任务

Act: 💾 检测到未完成任务
  从第 38 个继续执行...
```

---

### 场景 2：多任务并行

**传统方式：**
```
用户：帮我做 A、B、C 三个任务

Act: 好的，先做 A...
（完成 A）
现在做 B...
（完成 B）
最后做 C...
```

**使用 oc-flow：**
```
用户：$team 3:executor 并行执行 A、B、C

Act: ✅ 已启动 3 人团队
  👷 Worker-1: 任务 A
  👷 Worker-2: 任务 B
  👷 Worker-3: 任务 C
  
  预计完成时间：10 分钟（vs 30 分钟）
```

---

### 场景 3：任务规划 + 执行

**完整流程：**

```
用户：$plan 开发一个博客系统

Act: ✅ 任务规划完成
  📋 7 个子任务：
  1. 分析需求 - 10 分钟
  2. 设计数据库 - 15 分钟
  3. 实现用户系统 - 30 分钟
  4. 实现文章管理 - 30 分钟
  5. 实现评论系统 - 20 分钟
  6. 前端界面 - 40 分钟
  7. 测试部署 - 25 分钟
  
  查看进度：[飞书多维表格链接]

用户：$ralph 执行这个规划

Act: ✅ 已启动持久任务
  开始执行任务 1/7...
  💾 每完成一步自动保存进度
```

---

## 🤖 Agent 角色集成

### 在 OpenClaw 中使用 oc-flow Agent

创建 `~/.openclaw/workspace/agents/ocflow-architect.md`：

```markdown
# 角色：oc-flow 架构师

## 职责
- 分析系统架构
- 设计 oc-flow 工作流
- 优化任务分解

## 触发词
"ocflow"、"工作流"、"任务分解"、"持久执行"

## 工具
- oc-flow CLI
- 飞书多维表格
- 状态管理器
```

**使用示例：**
```
/architect 帮我设计一个数据分析工作流

## 方案

使用 oc-flow `$plan` 命令：

1. 数据收集阶段（$ralph）
2. 数据清洗阶段（$team 3）
3. 数据分析阶段（$plan）
4. 报告生成阶段（$ralph）
```

---

## 📊 飞书集成配置

### 步骤 1：创建飞书应用

参考 [FEISHU-SETUP.md](./FEISHU-SETUP.md)

### 步骤 2：配置 OpenClaw

在 OpenClaw 中配置飞书集成：

```bash
# 编辑 OpenClaw 配置
nano ~/.openclaw/gateway/config.yaml

# 添加飞书配置
feishu:
  enabled: true
  bitable_token: "xxxxx"
  channel: "oc_xxx"
```

### 步骤 3：测试集成

```bash
# 在 OpenClaw 对话中
/ocflow status --feishu

# 检查飞书是否收到消息
```

---

## 🔄 工作流示例

### 工作流 1：每日自动报告

创建 `~/.openclaw/cron/jobs.json`：

```json
{
  "jobs": [
    {
      "name": "daily-standup",
      "schedule": "0 9 * * *",
      "command": "ocflow status --feishu",
      "description": "每日早上 9 点发送状态报告"
    }
  ]
}
```

**效果：** 每天早上 9 点自动发送 oc-flow 状态到飞书群。

---

### 工作流 2：自动任务监控

创建 `~/.openclaw/workspace/scripts/monitor-ocflow.sh`：

```bash
#!/bin/bash

# 每 5 分钟检查一次 oc-flow 状态
while true; do
  status=$(ocflow status --json)
  
  # 如果有任务完成，发送通知
  if echo "$status" | jq '.completed_tasks > 0'; then
    ocflow status --feishu
  fi
  
  sleep 300
done
```

**配置为系统服务：**
```bash
sudo systemctl create monitor-ocflow
sudo systemctl start monitor-ocflow
```

---

### 工作流 3：任务完成自动归档

创建 `~/.openclaw/workflows/archive-completed.py`：

```python
#!/usr/bin/env python3
"""
任务完成自动归档工作流

监听 oc-flow 状态，当任务完成时：
1. 导出结果到飞书文档
2. 清理本地状态
3. 发送完成通知
"""

from ocflow.core import state_manager
from feishu_integration import FeishuIntegration

def archive_completed_tasks():
    teams = state_manager.list_teams()
    
    for team in teams:
        if team.status == "completed":
            # 导出到飞书文档
            export_to_feishu_doc(team)
            
            # 发送通知
            send_completion_notification(team)
            
            # 清理状态
            state_manager.stop_team(team.name)

if __name__ == "__main__":
    archive_completed_tasks()
```

---

## 🎨 消息卡片示例

### 1. OpenClaw + oc-flow 状态卡片

```
┌─────────────────────────────┐
│ 🤖 OpenClaw + oc-flow 状态  │
├─────────────────────────────┤
│ 活跃对话：3                 │
│ 活跃团队：2                 │
│ 待处理任务：15              │
├─────────────────────────────┤
│ 当前执行：                  │
│ - 团队 A: 分析 GitHub 项目     │
│ - 团队 B: 竞品分析           │
└─────────────────────────────┘
```

### 2. 任务完成通知

```
┌─────────────────────────────┐
│ ✅ 任务完成通知             │
├─────────────────────────────┤
│ 任务：分析 100 个 GitHub 项目   │
│ 耗时：2 小时 30 分钟          │
│ 结果：生成分析报告          │
├─────────────────────────────┤
│ 查看报告：[飞书文档链接]    │
└─────────────────────────────┘
```

---

## 🐛 故障排查

### 问题 1：ocflow 命令不识别

**症状：** `ocflow: command not found`

**解决：**
```bash
# 检查路径
which ocflow

# 如果不存在，创建软链接
ln -s /path/to/oc-flow/core/cli.py /usr/local/bin/ocflow

# 或者使用完整路径
python /path/to/oc-flow/core/cli.py
```

### 问题 2：飞书推送失败

**症状：** `Failed to send card to Feishu`

**解决：**
```bash
# 检查 Token
echo $OC_FLOW_BITABLE_TOKEN

# 检查网络
curl https://open.feishu.cn

# 查看详细日志
export OC_FLOW_LOG_LEVEL=DEBUG
ocflow status --feishu
```

### 问题 3：OpenClaw 重启后状态丢失

**症状：** OpenClaw 重启后 oc-flow 团队状态消失

**解决：**
```bash
# 检查状态文件
cat ~/.openclaw/workspace/.oc-flow/state/active-teams.json

# 如果文件存在但状态丢失，手动恢复
python -c "from ocflow.core import state_manager; state_manager.load_state()"

# 配置自动保存（每任务完成时）
export OC_FLOW_SAVE_INTERVAL=1
```

---

## 📚 最佳实践

### 1. 任务命名规范

```bash
# ✅ 好的命名（包含日期和描述）
$ralph 2026-04-01 竞品分析
$team 3 2026-04-01 测试修复

# ❌ 避免模糊命名
$ralph 分析项目
$team 3 测试
```

### 2. 定期清理

```bash
# 每天清理已完成的团队
0 2 * * * ocflow cleanup completed

# 每周清理旧日志
0 3 * * 0 rm ~/.openclaw/workspace/.oc-flow/logs/*.log.*
```

### 3. 监控资源

```bash
# 监控内存占用
watch -n 60 "ps aux | grep ocflow | awk '{print $6}'"

# 如果超过 500MB，减少并发数
export OC_FLOW_MAX_TEAMS=3
```

### 4. 备份状态

```bash
# 每小时备份状态到云存储
0 * * * * rclone copy ~/.openclaw/workspace/.oc-flow/state onedrive:backup/ocflow/
```

---

## 🔗 相关资源

- **[USER-GUIDE.md](./USER-GUIDE.md)** - oc-flow 完整使用指南
- **[FEISHU-SETUP.md](./FEISHU-SETUP.md)** - 飞书配置详解
- **[OpenClaw 文档](https://docs.openclaw.ai)** - OpenClaw 官方文档
- **[GitHub 仓库](https://github.com/Liqiuyue9597/oc-flow)** - 源代码和 Issues

---

## 🎯 快速参考卡片

```bash
# 安装
git clone https://github.com/Liqiuyue9597/oc-flow.git
cd oc-flow && pip install -r requirements.txt

# 基础使用
ocflow status              # 查看状态
ocflow plan "任务"         # 任务规划
ocflow ralph "任务"        # 持久执行
ocflow team 3 "任务"       # 创建团队

# 飞书集成
export OC_FLOW_BITABLE_TOKEN=xxxxx
export OC_FLOW_FEISHU_CHANNEL=oc_xxx
ocflow status --feishu     # 推送到飞书

# OpenClaw 集成
# 方式 1：作为 Skill
~/.openclaw/workspace/skills/oc-flow/core/cli.py

# 方式 2：作为服务
/opt/oc-flow/core/cli.py

# 方式 3：集成到 Gateway
~/.openclaw/core/ocflow/cli.py
```

---

**开始集成吧！** 🚀

有任何问题，欢迎提交 Issue：https://github.com/Liqiuyue9597/oc-flow/issues

---

**最后更新：** 2026-04-01  
**作者：** Act 🧗🏽‍♀️
