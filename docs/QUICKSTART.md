# oc-flow 快速开始指南

## 5 分钟上手

### 1. 安装

```bash
git clone https://github.com/LuckyYou/oc-flow.git
cd oc-flow
pip install -r requirements.txt
```

### 2. 查看状态

```bash
python core/cli.py status
```

**输出示例：**
```
📊 oc-flow 状态

活跃团队：0
总工人：0
空闲：0 | 忙碌：0
```

### 3. 创建团队

```bash
python core/cli.py team 3 "测试任务"
```

**输出示例：**
```
✅ 团队已启动

团队名称：team-20260401-013600
任务：测试任务
工人数量：3

工人列表：
👷 Worker-0: 空闲
👷 Worker-1: 空闲
👷 Worker-2: 空闲
```

### 4. 任务规划

```bash
python core/cli.py plan "实现一个待办事项应用"
```

**输出示例：**
```
✅ 任务规划完成

目标：实现一个待办事项应用

子任务清单：
1. 分析需求
   ⏱️ 10 分钟

2. 设计方案
   ⏱️ 15 分钟

3. 实现功能
   ⏱️ 30 分钟

4. 测试验证
   ⏱️ 15 分钟

预计总耗时：70 分钟
复杂度：medium
```

### 5. 持久执行

```bash
python core/cli.py ralph "分析 50 个 GitHub 项目"
```

**输出示例：**
```
✅ 已启动持久任务

任务 ID：ralph-20260401-013600
任务：分析 50 个 GitHub 项目
状态：运行中

执行中，请稍候...
```

---

## 下一步

- 阅读 [README.md](../README.md) 了解完整功能
- 查看 [docs/](./) 目录获取更多文档
- 运行测试：`python -m pytest tests/`

---

**有问题？** 提交 Issue 或联系作者 @LuckyYou
