# oc-flow

> OpenClaw 工作流引擎 —— 让 AI 从"手把手教做事"变成"一句话委托完成"

**版本：** 0.1.0  
**状态：** MVP 完成  
**启动时间：** 2026-04-01

---

## 🎯 核心价值

| 痛点 | oc-flow 解决方案 |
|------|----------------|
| 复杂任务难以分解 | `$plan` 自动规划 |
| 长任务容易中断 | `$ralph` 持久化执行 |
| 并行任务无法协调 | `$team` 多会话编排 |
| 状态不透明 | 实时状态查询 |
| 重复工作流每次都重说 | Agent 角色可复用 |

---

## 🚀 快速开始

### 安装

```bash
git clone https://github.com/Liqiuyue9597/oc-flow.git
cd oc-flow
pip install -r requirements.txt
```

### 基本使用（无需配置）

```bash
# 查看状态
python core/cli.py status

# 任务规划
python core/cli.py plan "竞品分析：产品 A vs 产品 B"

# 持久执行
python core/cli.py ralph "分析 100 个 GitHub 项目"

# 团队协作
python core/cli.py team 3 "修复所有测试"
```

### 飞书集成（可选）

```bash
export OC_FLOW_BITABLE_TOKEN=xxxxx
export OC_FLOW_FEISHU_CHANNEL=oc_xxx
```

📖 **详细使用指南：** [docs/USER-GUIDE.md](docs/USER-GUIDE.md)

---

## 📁 项目结构
cd oc-flow
```



```
oc-flow/
├── core/
│   ├── state_manager.py    # 状态管理核心
│   └── cli.py              # 命令行接口
├── workflows/
│   ├── plan.py             # 任务分解工作流
│   └── ralph.py            # 持久执行工作流
├── agents/
│   ├── architect.md        # 架构师角色
│   ├── reviewer.md         # 审查员角色
│   └── executor.md         # 执行者角色
├── state/                  # 运行时状态存储
├── memory/                 # 项目记忆
├── logs/                   # 执行日志
├── tests/                  # 测试用例
├── docs/                   # 文档
├── README.md
├── requirements.txt
└── LICENSE
```

---

## 🛠️ 核心功能

### 1. 状态管理器 (`core/state_manager.py`)

- **单例模式** - 全局唯一状态实例
- **团队管理** - 创建/停止/查询团队
- **工人管理** - 注册/状态更新/心跳
- **任务队列** - 创建/认领/完成
- **日志记录** - 自动记录所有操作

**使用示例：**

```python
from core.state_manager import state_manager, get_state_summary

# 获取状态摘要
summary = get_state_summary()
print(f"活跃团队：{summary['active_teams']}")

# 创建团队
team = state_manager.create_team("demo-team", "分析项目", 3)

# 注册工人
worker = state_manager.register_worker("worker-1", "session-key-123")

# 更新状态
state_manager.update_worker_status("worker-1", "busy", "task-1")

# 心跳
state_manager.heartbeat("worker-1")
```

### 2. 任务规划工作流 (`workflows/plan.py`)

自动将复杂任务分解为可执行的子任务：

- 任务分析
- 自动分解
- 依赖关系管理
- 时间估算
- URL 内容自动获取

**使用示例：**

```bash
python cli.py plan "竞品分析：obsidian-memos vs QuickAdd"
```

**输出：**

```
✅ 任务规划完成

目标：竞品分析：obsidian-memos vs QuickAdd

子任务清单：
1. 收集两个插件的功能列表
   ⏱️ 10 分钟

2. 对比价格模型
   ⏱️ 5 分钟

3. 分析优缺点
   ⏱️ 15 分钟

4. 生成推荐表格
   ⏱️ 10 分钟

预计总耗时：40 分钟
复杂度：medium
```

### 3. 持久执行工作流 (`workflows/ralph.py`)

支持长任务的可靠执行：

- 心跳循环（10 秒）
- 检查点保存
- 断点续传
- 错误恢复

**使用示例：**

```bash
python cli.py ralph "分析 100 个 GitHub 项目"
```

**特性：**

- ✅ 任务中断后可恢复
- ✅ 进度实时保存
- ✅ 服务器重启不丢失状态

---

## 🤖 Agent 角色

oc-flow 预置了 3 个核心 Agent 角色：

### `/architect` - 架构师

**职责：** 系统架构分析、技术选型、方案设计

**触发词：** "架构"、"设计"、"方案"、"对比"、"选型"

### `/reviewer` - 审查员

**职责：** 代码审查、质量评估、风险识别

**触发词：** "审查"、"review"、"检查"、"问题"

### `/executor` - 执行者

**职责：** 任务实现、代码编写、测试修复

**触发词：** "实现"、"编写"、"修复"、"完成"

---

## 📊 状态查询

### 命令行查询

```bash
python cli.py status
```

### 程序化查询

```python
from core.state_manager import get_state_summary

summary = get_state_summary()
print(summary)
```

**输出示例：**

```json
{
  "active_teams": 1,
  "total_workers": 3,
  "idle_workers": 2,
  "busy_workers": 1,
  "timestamp": "2026-04-01T01:36:00+08:00"
}
```

---

## 🔧 配置

### 约束条件

| 参数 | 值 | 说明 |
|------|-----|------|
| 最大并发团队 | 5 | 避免内存溢出 |
| 心跳间隔 | 10 秒 | 状态同步频率 |
| 状态保存频率 | 每任务完成 | 防止进度丢失 |
| 日志保留 | 7 天 | 自动清理 |

### 环境变量（可选）

```bash
# 飞书多维表格 Token（用于云端备份）
export OC_FLOW_BITABLE_TOKEN=xxx

# 日志级别
export OC_FLOW_LOG_LEVEL=INFO
```

---

## 💡 使用场景

### 场景 1：竞品分析

```bash
$plan 竞品分析：产品 A vs 产品 B vs 产品 C
```

**自动分解为：**
1. 收集三个产品的功能列表（10 分钟）
2. 对比价格模型（5 分钟）
3. 分析优缺点（15 分钟）
4. 生成推荐表格（10 分钟）

### 场景 2：批量处理

```bash
$ralph 分析 100 个 GitHub Trending 项目
```

**特性：**
- ✅ 自动逐个分析
- ✅ 每 10 秒推送进度
- ✅ 中断后可恢复

### 场景 3：团队协作

```bash
$team 5:executor 修复所有测试用例
```

**效果：**
- ✅ 创建 5 人团队并行处理
- ✅ 实时查看每人进度
- ✅ 自动任务分配

---

## 🐛 故障排查

### 问题 1：状态丢失

**症状：** 服务器重启后团队状态消失

**检查：**
```bash
cat state/active-teams.json
```

**解决：**
1. 检查文件权限
2. 确认 `save_state()` 被调用
3. 查看日志：`logs/`

### 问题 2：工人卡住

**症状：** 工人状态一直为 busy

**检查：**
```bash
cat state/worker-status.json
# 查看 last_heartbeat 时间
```

**解决：**
```python
# 手动重置工人状态
state_manager.update_worker_status("worker-1", "idle")
```

### 问题 3：内存占用高

**检查：**
```bash
free -h
```

**解决：**
1. 减少并发团队数（≤5）
2. 停止完成的团队
3. 清理旧日志

---

## 📈 开发路线图

### 阶段 1：基础框架 ✅
- [x] 创建项目结构
- [x] 实现状态管理器
- [x] 创建 3 个核心 Agent 角色

### 阶段 2：核心工作流 ✅
- [x] `$plan` - 任务分解
- [x] `$ralph` - 持久执行
- [x] CLI 状态查询

### 阶段 3：飞书集成（进行中）
- [ ] 飞书多维表格 Schema
- [ ] 飞书消息卡片
- [ ] 飞书机器人命令

### 阶段 4：优化与文档
- [ ] 性能优化
- [ ] 用户文档
- [ ] 示例工作流

---

## 🧪 测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行单个测试
python -m pytest tests/test_state_manager.py -v
```

---

## 🤖 OpenClaw 集成

oc-flow 可与 OpenClaw 无缝集成，提供长周期任务执行能力：

```bash
# 在 OpenClaw 对话中
/ocflow status
/ocflow plan "竞品分析"
/ocflow ralph "分析 100 个项目"
```

**集成方式：**
- ✅ 作为 OpenClaw Skill 安装
- ✅ 作为独立服务运行
- ✅ 集成到 Gateway 原生命令

📖 **详细指南：** [docs/OPENCLAW-INTEGRATION.md](docs/OPENCLAW-INTEGRATION.md)

---

## 📚 文档导航

| 文档 | 说明 | 适合人群 |
|------|------|---------|
| [docs/USER-GUIDE.md](docs/USER-GUIDE.md) | 📘 完整使用指南 | 👉 所有用户 |
| [docs/QUICKSTART.md](docs/QUICKSTART.md) | ⚡ 5 分钟快速开始 | 新手 |
| [docs/OPENCLAW-INTEGRATION.md](docs/OPENCLAW-INTEGRATION.md) | 🤖 OpenClaw 集成 | OpenClaw 用户 |
| [docs/FEISHU-SETUP.md](docs/FEISHU-SETUP.md) | 📊 飞书集成配置 | 需要可视化 |
| [docs/IMPLEMENTATION-COMPLETE.md](docs/IMPLEMENTATION-COMPLETE.md) | ✅ 实现详情 | 开发者 |

---

## 📄 License

MIT

---

**最后更新：** 2026-04-01  
**作者：** Liqiuyue9597  
**仓库：** https://github.com/Liqiuyue9597/oc-flow
