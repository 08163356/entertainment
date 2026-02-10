# 模板库

> **高效 Prompt 模板和文档模板，提高 Agent 效率**

---

## 目录结构

```
templates/
├── prompts/               # Prompt 模板
│   ├── task-delegation.md # 任务委托模板
│   ├── code-review.md     # 代码审查模板
│   └── bug-report.md      # Bug 报告模板
│
├── documents/             # 文档模板
│   ├── architecture.md    # 架构设计文档模板
│   ├── api.md             # API 文档模板
│   └── test-plan.md       # 测试计划模板
│
└── code/                  # 代码模板
    ├── service.md         # 服务类模板
    ├── controller.md      # 控制器模板
    └── test.md            # 测试用例模板
```

---

## Prompt 模板示例

### 任务委托模板

```markdown
## TASK
{任务描述}

## EXPECTED OUTCOME
{期望输出}

## REQUIRED SKILLS
{所需技能}

## REQUIRED TOOLS
{所需工具}

## MUST DO
{必须做的事}

## MUST NOT DO
{禁止的事}

## CONTEXT
{背景信息}
```

### 代码审查模板

```markdown
## 审查范围
{文件列表}

## 审查重点
- [ ] 功能正确性
- [ ] 安全性
- [ ] 性能
- [ ] 可维护性

## 问题清单
| 文件:行号 | 问题 | 严重程度 | 建议 |
|-----------|------|----------|------|

## 结论
{通过/需修改/不通过}
```

---

## 如何使用

### Agent 自动引用

Agent 在执行任务时会自动加载相关模板：

```
Orchestrator 委派任务 → 加载 task-delegation.md
QA 代码审查 → 加载 code-review.md
```

### 自定义模板

1. 在对应目录创建新模板
2. 遵循命名规范 `{功能}.md`
3. 在 Agent 配置中引用

---

## 模板开发指南

### 好的模板特征

- 结构清晰，易于填充
- 覆盖常见场景
- 有明确的必填和选填项
- 包含示例

### 模板格式规范

```markdown
# {模板名称}

## 用途
{模板的使用场景}

## 模板内容
{可直接复用的模板}

## 使用示例
{填充后的示例}

## 注意事项
{使用时的注意点}
```
