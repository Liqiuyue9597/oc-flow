# 飞书集成配置指南

本指南介绍如何配置 oc-flow 与飞书的集成，包括多维表格状态同步和消息卡片推送。

---

## 📋 前置条件

1. **飞书开放平台应用** - 已创建企业自建应用
2. **权限配置** - 已配置以下权限：
   - 多维表格读写权限
   - 消息发送权限
   - 机器人配置
3. **Python 环境** - 已安装 oc-flow 依赖

---

## 🔧 步骤 1：创建飞书应用

### 1.1 访问飞书开放平台

打开 https://open.feishu.cn/ 并登录企业账号

### 1.2 创建企业自建应用

1. 点击「企业管理」→「应用开发」
2. 点击「创建应用」
3. 填写应用信息：
   - 应用名称：`oc-flow`
   - 应用图标：（可选）
   - 应用描述：`OpenClaw 工作流引擎`

### 1.3 配置权限

在「权限管理」中添加以下权限：

| 权限名称 | 权限标识 | 用途 |
|---------|---------|------|
| 多维表格 | `bitable:app` | 创建和管理多维表格 |
| 多维表格数据 | `bitable:app_table_record` | 读写记录 |
| 消息 | `im:message` | 发送消息 |
| 群组机器人 | `im:chat` | 管理群聊 |

**重要：** 权限申请后需要管理员审批。

---

## 📊 步骤 2：配置多维表格

### 方案 A：自动创建（推荐）

oc-flow 会自动创建所需的表结构：

```bash
export OC_FLOW_BITABLE_TOKEN=<你的多维表格 Token>
python core/cli.py status
```

第一次运行时会自动创建以下表：
- 团队状态
- 工人状态
- 任务队列

### 方案 B：手动创建

1. 创建新的多维表格
2. 添加 3 个数据表，结构如下：

#### 表 1：团队状态

| 字段名 | 字段类型 | 说明 |
|-------|---------|------|
| 团队名称 | 文本 | 团队唯一标识 |
| 任务 | 文本 | 当前任务描述 |
| 工人数量 | 数字 | 工人数量 |
| 状态 | 单选 | running/paused/stopped |
| 创建时间 | 日期 | 创建时间戳 |
| 进度 (JSON) | 文本 | JSON 格式进度数据 |

#### 表 2：工人状态

| 字段名 | 字段类型 | 说明 |
|-------|---------|------|
| 工人 ID | 文本 | 工人唯一标识 |
| 所属团队 | 文本 | 所属团队名称 |
| 状态 | 单选 | idle/busy/stopped |
| 当前任务 | 文本 | 当前执行的任务 |
| 最后心跳 | 日期 | 最后心跳时间 |
| 完成任务数 | 数字 | 累计完成任务数 |

#### 表 3：任务队列

| 字段名 | 字段类型 | 说明 |
|-------|---------|------|
| 任务 ID | 文本 | 任务唯一标识 |
| 队列名称 | 文本 | 所属队列 |
| 主题 | 文本 | 任务主题 |
| 状态 | 单选 | pending/in_progress/completed/failed |
| 分配给 | 文本 | 负责人 |
| 创建时间 | 日期 | 创建时间戳 |
| 结果 | 文本 | 执行结果 |

---

## 🤖 步骤 3：配置飞书机器人

### 3.1 添加机器人到群

1. 在飞书群中点击右上角「设置」
2. 选择「添加机器人」
3. 选择「自定义机器人」
4. 填写机器人信息：
   - 名称：`oc-flow`
   - 头像：（可选）
   - Webhook 地址：（暂时不需要）

### 3.2 获取群 ID

1. 在群设置中查看群信息
2. 复制群 ID（格式：`oc_xxxxxxxxxxxx`）

---

## 🔐 步骤 4：配置环境变量

### Linux/Mac

```bash
# 多维表格 Token（从浏览器 URL 获取）
export OC_FLOW_BITABLE_TOKEN=xxxxx

# 飞书群 ID（用于推送状态）
export OC_FLOW_FEISHU_CHANNEL=oc_xxxxxxxxxxxx

# 日志级别（可选）
export OC_FLOW_LOG_LEVEL=INFO
```

### Windows

```cmd
set OC_FLOW_BITABLE_TOKEN=xxxxx
set OC_FLOW_FEISHU_CHANNEL=oc_xxxxxxxxxxxx
set OC_FLOW_LOG_LEVEL=INFO
```

### 永久配置（推荐）

添加到 `~/.bashrc` 或 `~/.zshrc`：

```bash
echo 'export OC_FLOW_BITABLE_TOKEN=xxxxx' >> ~/.bashrc
echo 'export OC_FLOW_FEISHU_CHANNEL=oc_xxxxxxxxxxxx' >> ~/.bashrc
source ~/.bashrc
```

---

## ✅ 步骤 5：测试集成

### 测试 1：查看状态

```bash
python core/cli.py status
```

**预期输出：**
```
📊 oc-flow 状态

活跃团队：0
总工人：0
空闲：0 | 忙碌：0
```

### 测试 2：同步到飞书

```bash
python -c "from core.feishu_integration import sync_to_feishu; import asyncio; asyncio.run(sync_to_feishu())"
```

**预期：**
- 多维表格中出现数据
- 飞书群中收到状态卡片

### 测试 3：创建团队

```bash
python core/cli.py team 3 "测试任务"
```

然后再次同步到飞书，查看多维表格是否更新。

---

## 🎨 消息卡片示例

### 状态卡片

```
┌─────────────────────────────┐
│  📊 oc-flow 状态            │
├─────────────────────────────┤
│  活跃团队    总工人         │
│     1          3            │
│  空闲        忙碌           │
│     2          1            │
├─────────────────────────────┤
│  更新时间：2026-04-01T10:00 │
└─────────────────────────────┘
```

### 任务规划卡片

```
┌─────────────────────────────┐
│  ✅ 任务规划完成            │
├─────────────────────────────┤
│  目标：竞品分析             │
│                             │
│  子任务清单：               │
│  1. 收集功能列表            │
│  2. 对比价格模型            │
│  3. 分析优缺点              │
│                             │
│  预计耗时    复杂度         │
│    40 分钟     medium       │
└─────────────────────────────┘
```

### 持久执行进度卡片

```
┌─────────────────────────────┐
│  🔄 持久执行中              │
├─────────────────────────────┤
│  任务：分析 100 个 GitHub 项目   │
│                             │
│  ████████████░░░░░░░░ 37%   │
│                             │
│  进度        状态           │
│  37/100      running        │
├─────────────────────────────┤
│  最后心跳：2026-04-01T10:05 │
└─────────────────────────────┘
```

---

## 🐛 常见问题

### Q1: 多维表格 Token 在哪里？

**A:** 从浏览器 URL 中获取：
```
https://xxx.feishu.cn/bitables/xxxxxx?base=xxxxxx
                                      ↑ 这就是 Token
```

### Q2: 权限不足怎么办？

**A:** 
1. 联系企业管理员审批权限
2. 或者使用个人飞书账号创建应用

### Q3: 机器人不回复消息？

**A:** 
1. 检查机器人是否在群内
2. 检查权限配置
3. 查看日志：`logs/` 目录

### Q4: 同步失败？

**A:** 
1. 检查 Token 是否正确
2. 检查网络连接
3. 查看详细错误日志

---

## 📚 进阶使用

### 自动同步

配置定时任务，每分钟同步一次：

```bash
# crontab -e
*/1 * * * * cd /path/to/oc-flow && python -c "from core.feishu_integration import sync_to_feishu; import asyncio; asyncio.run(sync_to_feishu('$CHANNEL'))"
```

### 自定义卡片

编辑 `core/feishu_integration.py` 中的卡片模板函数：

```python
def create_status_card(summary: Dict[str, Any]) -> dict:
    # 自定义卡片内容
    ...
```

### Webhook 集成

配置飞书事件订阅，实现双向同步（待实现）。

---

## 📞 获取帮助

- 查看 [README.md](../README.md) 了解完整功能
- 提交 Issue: https://github.com/Liqiuyue9597/oc-flow/issues
- 飞书开放平台文档：https://open.feishu.cn/document/

---

**最后更新：** 2026-04-01
