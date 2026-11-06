---
title: CODEOWNERS 配置与维护教程
create_time: 2026-11-06 11:58:54
update_time: 2026-11-06 12:15:18
category: practice
subcategory: workflow
documentType: tutorial
purpose: tutorial
status: active
project: AIDataEngineering
tags: [CODEOWNERS, 代码审查, GitHub, GitLab, 团队协作]
project-description: AI 数据工程项目集 - CODEOWNERS 配置与维护新手教程
---

# CODEOWNERS 配置与维护教程

> **目标读者**：新加入团队、需要维护仓库审查流程的开发者
>
> **前置条件**：Git 基础、熟悉 GitHub/GitLab PR 流程

---

## 0. 迭代须知

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-11-06 | 初版：基于伞形仓 CODEOWNERS 实践整理 |

**修改规则**：
- 更新 CODEOWNERS 语法或平台特性时，标注适用的 GitHub/GitLab 版本
- 添加新的路径模式时，提供实际案例
- 平台行为变化时，更新"验证方法"章节

---

## 1. 什么是 CODEOWNERS

CODEOWNERS 是一个配置文件，用于定义代码库中不同路径的**默认审查者**。当有人提交 Pull Request 时，平台会根据修改的文件路径自动分配审查者。

### 核心价值

- **明确责任**：每个模块都有明确的负责人
- **自动分配**：减少手动选择审查者的工作量
- **质量保障**：确保关键代码由合适的人审查
- **知识传递**：新成员知道该向谁请教特定模块

---

## 2. 文件位置与命名

### GitHub

```
.github/CODEOWNERS
```

### GitLab

```
.gitlab/CODEOWNERS
或
CODEOWNERS（仓库根目录）
```

**注意**：
- 文件名必须全大写 `CODEOWNERS`
- GitHub 推荐放在 `.github/` 目录下
- GitLab 可以放在 `.gitlab/` 或根目录

---

## 3. 语法与模式

### 基本规则

```codeowners
# 注释行以 # 开头

# 模式 所有者
*.js     @user1 @user2
```

### 模式匹配规则

| 模式 | 含义 | 示例 |
|------|------|------|
| `*` | 匹配任意字符（不含 `/`） | `*.js` 匹配所有 JS 文件 |
| `**` | 匹配任意字符（含 `/`） | `docs/**` 匹配 docs 下所有文件 |
| `/` | 目录分隔符 | `/src/` 只匹配根目录下的 src |
| `!` | 排除模式 | `!docs/README.md` 排除特定文件 |
| `@` | 用户名或团队名前缀 | `@username` 或 `@org/team-name` |

### 匹配优先级

**后定义的模式覆盖先定义的模式**

```codeowners
# 先定义的规则
*.js     @team-frontend

# 后定义的规则（覆盖上面的）
docs/*.js @team-docs
```

在 `docs/example.js` 的 PR 中，审查者是 `@team-docs`（不是 `@team-frontend`）。

---

## 4. 实际案例：伞形仓 CODEOWNERS

以下是我们项目的真实配置：

```codeowners
# 默认：所有变更需要至少一个审查者
* @ZenRay

# Agent 配置变更需要特别关注（安全红线）
AGENTS.md @ZenRay
CLAUDE.md @ZenRay
.claude/ @ZenRay

# 基础设施变更
.gitmodules @ZenRay
.meta @ZenRay
.gitignore @ZenRay

# 文档变更可以自审
docs/LearningNote/ @ZenRay
README.md @ZenRay

# 输入源配置（高风险）
submodules/ @ZenRay

# 数据仓注册（高风险）
projects/ @ZenRay
```

### 设计思路

1. **默认兜底**：`* @ZenRay` 确保所有文件都有审查者
2. **高风险标注**：`.claude/`、`submodules/`、`projects/` 明确标记为高风险
3. **文档自审**：`docs/LearningNote/` 和 `README.md` 允许自审

---

## 5. 团队协作场景

### 场景 1：多人团队

```codeowners
# 前端代码
src/components/ @alice @bob
src/styles/     @charlie

# 后端代码
src/api/        @dave @eve
src/database/   @frank

# 文档
docs/           @grace

# 默认
*               @tech-leads
```

### 场景 2：使用 GitHub 团队

```codeowners
# 整个团队
*.go    @org/backend-team

# 多个团队
*.js    @org/frontend-team @org/qa-team
```

**前提**：团队必须在 GitHub 组织中创建，且仓库有访问权限。

### 场景 3：混合模式

```codeowners
# 关键配置文件（需要多人审查）
.github/workflows/  @admin-team @security-team
package.json        @tech-leads

# 普通代码
src/                @dev-team

# 文档
docs/               @docs-team @anyone
```

---

## 6. 验证方法

### 步骤 1：检查语法

```bash
# GitHub 没有官方语法检查工具
# 可以通过提交 PR 测试自动分配是否正确
```

**手动验证**：
1. 创建一个测试分支
2. 修改特定路径的文件
3. 提交 PR
4. 检查审查者是否自动分配正确

### 步骤 2：测试不同路径

```bash
# 创建测试文件
mkdir -p test/{src,docs,.claude}
touch test/src/code.js
touch test/docs/readme.md
touch test/.claude/settings.json

# 分别提交 PR，验证审查者分配
```

### 步骤 3：验证覆盖规则

```bash
# 创建一个同时匹配多个模式的文件
# 例如：修改 docs/LearningNote/README.md
# 应该匹配 docs/LearningNote/ 规则（如果定义了）
# 而不是默认的 * 规则
```

### 步骤 4：验证团队分配

```bash
# 如果使用了 @org/team-name
# 确保团队成员都能收到审查请求
# 确保非团队成员不会被错误分配
```

---

## 7. 常见错误与排查

### 错误 1：模式不生效

**现象**：修改文件后，审查者没有自动分配

**排查**：
1. 检查文件名是否正确（`CODEOWNERS` 全大写）
2. 检查文件位置（`.github/CODEOWNERS`）
3. 检查模式语法（是否有拼写错误）
4. 检查用户名（`@username` 是否正确）

### 错误 2：审查者分配错误

**现象**：修改了 A 路径，但分配了 B 路径的审查者

**排查**：
1. 检查模式覆盖顺序（后定义的覆盖先定义的）
2. 检查模式匹配范围（`*` vs `**` 的区别）
3. 检查是否有更具体的模式匹配了该文件

### 错误 3：团队成员未收到通知

**现象**：分配了 `@org/team-name`，但成员没有收到邮件

**排查**：
1. 检查团队是否在 GitHub 组织中创建
2. 检查仓库是否对团队有访问权限
3. 检查成员的 GitHub 通知设置
4. 检查成员的邮箱是否验证

### 错误 4：GitLab CODEOWNERS 不生效

**现象**：GitLab 没有自动分配审查者

**排查**：
1. 检查 GitLab 版本（需要 Premium 或更高）
2. 检查文件位置（`.gitlab/CODEOWNERS` 或根目录 `CODEOWNERS`）
3. 检查项目设置（是否启用了 CODEOWNERS 功能）

---

## 8. 维护指南

### 定期更新

- **新成员加入**：更新相关路径的审查者
- **成员离职**：移除其用户名，分配给替代者
- **模块重组**：更新路径模式以匹配新结构
- **团队调整**：更新 GitHub 团队成员

### 版本控制

```bash
# CODEOWNERS 应该纳入版本控制
git add .github/CODEOWNERS
git commit -m "chore: 更新 CODEOWNERS 审查者列表"
git push
```

### 变更记录

建议在 PR 描述中说明 CODEOWNERS 的变更原因：

```markdown
## CODEOWNERS 变更

- 添加 @new-member 到 src/frontend/ 审查者
- 移除 @departed-member（已离职）
- 原因：团队调整，@new-member 接管前端开发
```

---

## 9. 最佳实践

### ✅ 推荐做法

1. **默认兜底**：使用 `* @default-reviewers` 确保所有文件都有审查者
2. **高风险标注**：对安全敏感的路径（如 `.github/workflows/`）明确标注
3. **文档自审**：对低风险文档（如 `docs/`）允许自审
4. **使用团队**：优先使用 `@org/team-name` 而非个人用户名
5. **定期审查**：每月检查一次 CODEOWNERS 是否过时

### ❌ 避免做法

1. **过度细分**：不要为每个文件定义审查者（维护成本高）
2. **遗漏默认**：不要忘记 `* @default-reviewers` 兜底规则
3. **硬编码个人**：避免只写个人用户名（成员离职会导致规则失效）
4. **忽视验证**：提交前一定要测试模式是否生效
5. **长期不更新**：团队变化后要及时更新 CODEOWNERS

---

## 10. 平台差异对比

| 特性 | GitHub | GitLab |
|------|--------|--------|
| 文件位置 | `.github/CODEOWNERS` | `.gitlab/CODEOWNERS` 或根目录 |
| 团队支持 | ✅ `@org/team-name` | ✅ `@group/subgroup` |
| 覆盖规则 | 后定义覆盖先定义 | 后定义覆盖先定义 |
| 验证工具 | 无官方工具 | 无官方工具 |
| 版本要求 | 所有版本 | Premium 或更高 |
| 自动合并 | 可配置 | 可配置 |

---

## 11. 相关资源

- [GitHub CODEOWNERS 文档](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
- [GitLab CODEOWNERS 文档](https://docs.gitlab.com/ee/user/project/codeowners/)
- [本项目 CODEOWNERS 实例](../../.github/CODEOWNERS)

---

## 12. 快速参考卡片

```
┌─────────────────────────────────────────┐
│         CODEOWNERS 快速参考             │
├─────────────────────────────────────────┤
│ 文件位置                                │
│   GitHub: .github/CODEOWNERS            │
│   GitLab: .gitlab/CODEOWNERS            │
│                                         │
│ 基本语法                                │
│   *.js @user1         # 所有 JS 文件    │
│   /src/ @team         # src 目录        │
│   docs/** @docs-team  # docs 下所有     │
│                                         │
│ 覆盖规则                                │
│   后定义的覆盖先定义的                    │
│                                         │
│ 验证方法                                │
│   1. 创建测试分支                        │
│   2. 修改目标文件                        │
│   3. 提交 PR                            │
│   4. 检查审查者分配                      │
│                                         │
│ 最佳实践                                │
│   ✓ 默认兜底 * @default                 │
│   ✓ 高风险路径明确标注                   │
│   ✓ 使用团队而非个人                     │
│   ✓ 定期更新维护                        │
└─────────────────────────────────────────┘
```

---

**最后更新**：2026-11-06  
**维护者**：数据团队
