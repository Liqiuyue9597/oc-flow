# oc-flow 用户使用指南

> 让 AI 从"手把手教做事"变成"一句话委托完成"

---

## 🎯 什么是 oc-flow？

oc-flow 是一个**工作流引擎**，帮你把复杂任务交给 AI 自动完成。

**对比传统方式：**

| 传统方式 | 使用 oc-flow |
|---------|-------------|
| "帮我分析这个项目，先看 README，再看代码结构..." | `$plan 分析这个项目` |
| 需要时刻盯着 AI 执行 | 启动后自动执行，定期推送进度 |
| 中断后需要重新开始 | 支持断点续传 |
| 无法并行处理多任务 | 支持多团队并行 |

---

## 🚀 快速开始（5 分钟）

### 步骤 1：安装

```bash
# 克隆仓库
git clone https://github.com/Liqiuyue9597/oc-flow.git
cd oc-flow

# 安装依赖
pip install -r requirements.txt
```

### 步骤 2：基础使用（无需配置）

```bash
# 查看状态
python core/cli.py status

# 创建团队
python core/cli.py team 3 "测试任务"

# 任务规划
python core/cli.py plan "实现一个待办事项应用"
```

**这就够了！** 基础功能无需任何配置即可使用。

---

## 📊 进阶使用（可选配置）

### 场景 1：我想看到可视化进度

**配置飞书多维表格：**

1. 创建飞书多维表格（任意空白表格）
2. 复制 Token（从浏览器 URL）
3. 设置环境变量：

```bash
export OC_FLOW_BITABLE_TOKEN=xxxxx
```

4. 使用：

```bash
python -c "from core.feishu_integration import sync_to_feishu; import asyncio; asyncio.run(sync_to_feishu())"
```

**效果：** 所有状态自动同步到飞书表格，可实时查看。

---

### 场景 2：我想在飞书群里接收通知

**配置飞书机器人：**

1. 在飞书群添加机器人
2. 获取群 ID（`oc_xxx`）
3. 设置环境变量：

```bash
export OC_FLOW_BITABLE_TOKEN=xxxxx
export OC_FLOW_FEISHU_CHANNEL=oc_xxxxxxxxxxxx
```

4. 使用：

```bash
# 发送状态卡片到群
python -c "from core.feishu_integration import sync_to_feishu; import asyncio; asyncio.run(sync_to_feishu('oc_xxx'))"
```

**效果：** 群聊中自动收到状态卡片、进度更新。

---

### 场景 3：我想自动化（定时任务）

**配置 Cron：**

```bash
# 每分钟同步一次状态到飞书
crontab -e

# 添加以下行
*/1 * * * * cd /path/to/oc-flow && python -c "from core.feishu_integration import sync_to_feishu; import asyncio; asyncio.run(sync_to_feishu('oc_xxx'))"
```

**效果：** 自动同步，无需手动操作。

---

## 💡 使用场景示例

### 场景 1：竞品分析

**任务：** 分析 3 个竞品的功能、价格、优缺点

**传统方式：**
```
帮我分析一下竞品 A、B、C
先看看他们的官网
然后对比功能列表
再看看价格
最后生成一个表格
...
```

**使用 oc-flow：**
```bash
$plan 竞品分析：产品 A vs 产品 B vs 产品 C
```

**自动分解为：**
1. 收集三个产品的功能列表（10 分钟）
2. 对比价格模型（5 分钟）
3. 分析优缺点（15 分钟）
4. 生成推荐表格（10 分钟）
5. 发送到飞书群（5 分钟）

**预计总耗时：** 45 分钟

---

### 场景 2：批量处理

**任务：** 分析 100 个 GitHub 项目

**传统方式：**
```
帮我看看这个 GitHub 项目
（等待完成）
再看下一个
（重复 100 次...）
```

**使用 oc-flow：**
```bash
$ralph 分析 100 个 GitHub Trending 项目
```

**效果：**
- ✅ 自动逐个分析
- ✅ 每 10 秒推送进度
- ✅ 中断后可恢复
- ✅ 完成后生成报告

**进度卡片示例：**
```
🔄 持久执行中
任务：分析 100 个 GitHub Trending 项目
████████████░░░░░░ 63%
63/100  running
```

---

### 场景 3：团队协作

**任务：** 修复 20 个测试用例

**传统方式：**
```
帮我修复这些测试
（AI 一个一个修，很慢）
```

**使用 oc-flow：**
```bash
$team 5:executor 修复所有测试用例
```

**效果：**
- ✅ 创建 5 人团队
- ✅ 并行处理不同模块
- ✅ 实时查看每人进度

**团队状态卡片：**
```
👥 团队：team-20260401-103600
任务：修复所有测试用例
状态：running
工人：5

✅ worker-1: idle
⏳ worker-2: busy - 测试模块 A
⏳ worker-3: busy - 测试模块 B
✅ worker-4: idle
⏳ worker-5: busy - 测试模块 C
```

---

## 📋 完整命令参考

### 基础命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `status` | 查看当前状态 | `python core/cli.py status` |
| `team N "task"` | 创建 N 人团队 | `python core/cli.py team 3 "修复测试"` |
| `plan "task"` | 任务分解 | `python core/cli.py plan "竞品分析"` |
| `ralph "task"` | 持久执行 | `python core/cli.py ralph "分析 100 个项目"` |

### 飞书集成命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `status --feishu` | 推送到飞书 | `python core/cli.py status --feishu` |
| `plan --feishu` | 规划并推送卡片 | `python core/cli.py plan "task" --feishu` |
| `ralph --feishu` | 执行并定期推送 | `python core/cli.py ralph "task" --feishu` |

---

## 🎨 输出示例

### 1. 状态查询输出

```bash
$ python core/cli.py status

📊 oc-flow 状态

活跃团队：1
总工人：3
空闲：2 | 忙碌：1

更新时间：2026-04-01T10:36:00
```

### 2. 任务规划输出

```bash
$ python core/cli.py plan "实现一个博客系统"

✅ 任务规划完成

目标：实现一个博客系统

子任务清单：
1. 分析需求
   理解功能需求和用户群体
   ⏱️ 10 分钟

2. 设计数据库结构
   设计用户、文章、评论表
   ⏱️ 15 分钟

3. 实现用户系统
   注册、登录、权限管理
   ⏱️ 30 分钟

4. 实现文章管理
   创建、编辑、删除文章
   ⏱️ 30 分钟

5. 实现评论系统
   评论、回复、审核
   ⏱️ 20 分钟

6. 前端界面
   响应式设计
   ⏱️ 40 分钟

7. 测试部署
   单元测试、部署到服务器
   ⏱️ 25 分钟

预计总耗时：170 分钟
复杂度：high
```

### 3. 持久执行输出

```bash
$ python core/cli.py ralph "分析 50 个 AI 项目"

✅ 已启动持久任务

任务 ID：ralph-20260401-103600
任务：分析 50 个 AI 项目
状态：运行中

执行中，请稍候...

⏳ 执行步骤 1/50
  完成步骤 1
💾 已保存检查点：步骤 1

⏳ 执行步骤 2/50
  完成步骤 2
💾 已保存检查点：步骤 2

...

✅ 任务完成：ralph-20260401-103600
```

---

## 🤖 Agent 角色使用

oc-flow 预置了 3 个 Agent 角色，可在对话中直接使用：

### `/architect` - 架构师

**用途：** 系统架构分析、技术选型

**示例：**
```
/architect 帮我分析一下当前系统架构

## 现状分析

当前系统架构：
- 状态管理器 (state_manager.py) - 单例模式
- 本地 JSON 存储 + 飞书多维表格备份
- 心跳机制：10 秒间隔

## 问题诊断

1. 单点故障风险
   - 位置：state_manager.py:45
   - 问题：单例模式在进程重启后状态丢失
   ...
```

### `/reviewer` - 审查员

**用途：** 代码审查、质量评估

**示例：**
```
/reviewer 审查一下 state_manager.py 的代码

## 审查结果

### ✅ 优点
- 单例模式实现正确
- 状态保存逻辑完整

### ⚠️ 问题
- 第 45 行：未处理异常
- 第 78 行：缺少日志
...
```

### `/executor` - 执行者

**用途：** 任务实现、代码编写

**示例：**
```
/executor 实现一个任务分解功能

## 实现方案

将创建 `workflows/plan.py`，包含：
1. 任务分析函数
2. 分解逻辑
3. 依赖管理
...
```

---

## 🔧 故障排查

### 问题 1：命令不识别

**症状：** `python core/cli.py` 报错

**解决：**
```bash
# 检查 Python 版本
python --version  # 需要 3.8+

# 重新安装依赖
pip install -r requirements.txt --upgrade
```

### 问题 2：飞书同步失败

**症状：** `sync_to_feishu()` 报错

**解决：**
```bash
# 检查 Token 是否正确
echo $OC_FLOW_BITABLE_TOKEN

# 检查网络连接
curl https://open.feishu.cn

# 查看详细错误
export OC_FLOW_LOG_LEVEL=DEBUG
```

### 问题 3：内存占用高

**症状：** 服务器内存紧张

**解决：**
```bash
# 查看当前团队数
python core/cli.py status

# 停止不需要的团队
python core/cli.py team shutdown team-name

# 限制最大并发数（编辑配置文件）
MAX_CONCURRENT_TEAMS=3
```

---

## 📚 更多资源

- **[README.md](../README.md)** - 项目总览
- **[QUICKSTART.md](./QUICKSTART.md)** - 5 分钟快速开始
- **[FEISHU-SETUP.md](./FEISHU-SETUP.md)** - 飞书详细配置
- **[GitHub 仓库](https://github.com/Liqiuyue9597/oc-flow)** - 源代码和 Issues

---

## 💬 常见问题

### Q: 我需要飞书才能使用吗？

**A:** 不需要！基础功能（任务规划、持久执行）无需任何配置。飞书是可选的，用于可视化和通知。

### Q: 支持哪些 AI 模型？

**A:** oc-flow 本身不绑定特定 AI 模型，可与任何 AI 助手配合使用（Claude、GPT-4、通义千问等）。

### Q: 最多支持多少个并行任务？

**A:** 默认限制 5 个并发团队（避免内存溢出），可通过配置调整。

### Q: 中断后如何恢复？

**A:** `$ralph` 命令支持自动恢复。重启后运行相同命令，会自动从断点继续。

### Q: 可以自定义工作流吗？

**A:** 可以！在 `workflows/` 目录下创建新的 Python 文件，定义你的工作流逻辑。

---

## 🎯 最佳实践

### 1. 任务命名规范

```bash
# ✅ 好的命名
$plan 竞品分析：产品 A vs 产品 B
$ralph 分析 100 个 GitHub AI 项目

# ❌ 避免模糊命名
$plan 分析项目
$ralph 处理数据
```

### 2. 合理设置团队规模

```bash
# 小任务（<30 分钟）
$team 1 "简单任务"

# 中等任务（1-2 小时）
$team 3 "中等任务"

# 大任务（>2 小时）
$team 5 "大型任务"
```

### 3. 定期检查状态

```bash
# 每 30 分钟查看一次
watch -n 1800 "python core/cli.py status"

# 或者配置飞书自动推送
export OC_FLOW_FEISHU_CHANNEL=oc_xxx
```

### 4. 清理旧任务

```bash
# 每天清理已完成的团队
python core/cli.py team shutdown completed-teams

# 清理旧日志
rm logs/*.log.*
```

---

## 🚀 进阶技巧

### 技巧 1：组合使用

```bash
# 先规划，再执行
$plan 分析 50 个项目
$ralph 执行规划结果

# 先分解，再分配
$plan 开发新功能
$team 5 "实现规划的功能"
```

### 技巧 2：批量操作

```bash
# 批量创建团队
for i in {1..5}; do
  python core/cli.py team 3 "模块$i"
done
```

### 技巧 3：监控脚本

创建 `monitor.sh`：

```bash
#!/bin/bash
while true; do
  python core/cli.py status
  sleep 300  # 每 5 分钟
done
```

---

**开始使用吧！** 🎉

有任何问题，欢迎提交 Issue：https://github.com/Liqiuyue9597/oc-flow/issues
