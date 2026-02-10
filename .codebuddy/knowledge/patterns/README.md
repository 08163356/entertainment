# 技术模式库

> **沉淀成功的技术模式，供 Agent 参考和复用**

---

## 目录结构

```
patterns/
├── architecture/          # 架构模式
│   ├── layered.md         # 分层架构
│   ├── microservices.md   # 微服务架构
│   └── event-driven.md    # 事件驱动架构
│
├── design/                # 设计模式
│   ├── creational/        # 创建型模式
│   ├── structural/        # 结构型模式
│   └── behavioral/        # 行为型模式
│
├── code/                  # 代码模式
│   ├── error-handling.md  # 错误处理模式
│   ├── validation.md      # 输入验证模式
│   └── caching.md         # 缓存模式
│
└── tech-stack/            # 技术栈模式
    ├── frontend.md        # 前端技术栈
    ├── backend.md         # 后端技术栈
    └── database.md        # 数据库选型
```

---

## 如何使用

### Agent 引用

Researcher Agent 在收集信息时会自动检索此目录：

```
/team:design 设计用户系统

→ Researcher 检索 patterns/architecture/ 获取架构参考
→ Architect 基于参考设计方案
```

### 人工查阅

直接阅读对应的 markdown 文件获取模式详情。

---

## 如何贡献

### 添加新模式

1. 在对应目录创建新文件
2. 遵循模板格式
3. 提交 PR 并说明来源

### 模板格式

```markdown
# {模式名称}

## 适用场景
- 场景 1
- 场景 2

## 模式描述
[描述模式的核心思想]

## 实现示例
[代码示例]

## 优缺点

### 优点
- ...

### 缺点
- ...

## 参考资料
- [链接1]
- [链接2]
```

---

## 注意事项

⚠️ **重要提醒**

根据团队 AI 使用策略：
- 此知识库内容必须由人工编写和审核
- 禁止直接使用 AI 生成的内容
- 所有贡献需说明来源
