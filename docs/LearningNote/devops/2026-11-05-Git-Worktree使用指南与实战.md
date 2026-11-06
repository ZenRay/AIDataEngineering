# Git Worktree 使用指南与实战

> **日期**：2026-11-05  
> **适用场景**：需要在同一仓库的多个分支间频繁切换、并行开发  
> **前置知识**：Git 基础（分支、commit、checkout）  
> **阅读时间**：20 分钟 + 30 分钟实操

---

## 0. 为什么需要 Worktree？

### 痛点场景

想象你正在 `feature-A` 分支开发，突然：
- 🚨 线上 bug 需要紧急修复（要在 `master` 分支）
- 👀 同事请你 review 他的 `feature-B` 分支代码
- 🧪 想测试另一个分支的运行效果

**传统方案**：`git stash` → `git checkout` → 干活 → `git checkout` → `git stash pop`

**问题**：
1. 频繁切换容易丢失上下文
2. stash 多了管理混乱
3. 无法同时运行两个分支的服务对比效果
4. 切换时未提交的更改可能冲突

### Worktree 方案

**一个仓库，多个工作目录**——每个目录对应一个分支，互不干扰，同时工作！

---

## 1. 核心概念

### 1.1 什么是 Worktree

Git Worktree 允许你从**同一个仓库**创建多个**独立的工作目录**，每个目录检出不同的分支。

```
┌─────────────────────────────────────┐
│   .git/  (唯一的仓库数据库)          │
│   ├── objects/                      │
│   ├── refs/                         │
│   └── worktrees/        ← worktree 元数据
│       ├── branch-A/                 │
│       └── branch-B/                 │
└─────────────────────────────────────┘
        ↑               ↑
        │               │
   ┌────┴────┐     ┌────┴────┐
   │worktree1│     │worktree2│
   │(master) │     │(dev-xxx)│
   └─────────┘     └─────────┘
```

**关键特性**：
- ✅ 共享同一个 `.git` 仓库（节省空间）
- ✅ 每个 worktree 有独立的工作目录
- ✅ 不能有两个 worktree 同时检出同一分支（防止冲突）
- ✅ commit、push、pull 在所有 worktree 中都能工作

### 1.2 Worktree vs Clone

| 维度 | Worktree | Clone |
|------|----------|-------|
| 磁盘占用 | 共享 `.git`，省空间 | 完整拷贝，占空间 |
| 分支同步 | 自动同步（同一仓库） | 需要 fetch/pull |
| 适用场景 | 同仓库多分支并行 | 完全独立的工作副本 |
| commit 可见性 | 立即可见 | 需要 push/pull |

---

## 2. 基础命令

### 2.1 创建 Worktree

```bash
# 创建新分支并检出到新 worktree
git worktree add <路径> -b <新分支名>

# 检出已存在的分支到新 worktree
git worktree add <路径> <已存在分支>

# 示例：在当前目录的父目录创建 worktree
git worktree add ../my-project-hotfix -b hotfix/urgent-fix
git worktree add ../my-project-review feature/colleagues-branch
```

### 2.2 查看所有 Worktree

```bash
git worktree list
```

输出示例：
```
/home/user/my-project              abc1234 [master]
/home/user/my-project-hotfix       def5678 [hotfix/urgent-fix]
/home/user/my-project-review       ghi9012 [feature/colleagues-branch]
```

### 2.3 删除 Worktree

```bash
# 方式 1：先删除目录，再清理元数据
rm -rf <worktree路径>
git worktree prune

# 方式 2：先移除引用，再删除目录（推荐）
git worktree remove <worktree路径>

# 强制删除（有未提交更改时）
git worktree remove --force <worktree路径>
```

### 2.4 移动 Worktree

```bash
# 移动 worktree 到新位置
git worktree move <旧路径> <新路径>
```

---

## 3. 实战：本项目的 Worktree 结构

### 3.1 当前项目的 Worktree

查看我们项目的 worktree：

```bash
cd /home/ray/Documents/BiaoGuoRepo/AIDataEngineering
git worktree list
```

**当前结构**：
```
/home/ray/Documents/BiaoGuoRepo/
├── AIDataEngineering/          ← 主工作目录（dw-poc 分支）
└── AIDataEngineering-mcp/      ← worktree（master 分支）
```

### 3.2 实际使用场景

**场景 1：紧急修复 master 分支的 bug**

```bash
# 在主工作目录（dw-poc 分支）创建 master worktree
cd /home/ray/Documents/BiaoGuoRepo/AIDataEngineering
git worktree add ../AIDataEngineering-hotfix master

# 进入 hotfix worktree
cd ../AIDataEngineering-hotfix

# 创建 hotfix 分支并修复
git checkout -b hotfix/critical-bug
# ... 修复代码 ...
git commit -m "fix: 修复关键 bug"
git push origin hotfix/critical-bug

# 修复完成后，可以删除 worktree
cd ../AIDataEngineering
git worktree remove ../AIDataEngineering-hotfix
```

**场景 2：Review 同事的分支**

```bash
# 假设同事的分支是 feature/new-module
git fetch origin
git worktree add ../AIDataEngineering-review origin/feature/new-module

# 进入 review worktree
cd ../AIDataEngineering-review

# 可以直接运行、测试、查看效果
# 发现问题可以直接在这个 worktree 修复并 push

# Review 完成
cd ../AIDataEngineering
git worktree remove ../AIDataEngineering-review
```

### 3.3 本项目的注意事项

⚠️ **Submodule 处理**：

Worktree 不会自动初始化 submodule，需要手动：

```bash
cd <新创建的 worktree>
git submodule update --init --recursive
```

⚠️ **环境变量**：

每个 worktree 都需要单独 `direnv allow`：

```bash
cd <新创建的 worktree>
direnv allow
```

---

## 4. 高级用法

### 4.1 临时 Worktree（实验性更改）

想尝试一个大胆的重构，但不确定是否保留？

```bash
# 创建临时 worktree
git worktree add ../experiment-refactor -b experiment/new-architecture

# 在 worktree 中随意更改、commit
cd ../experiment-refactor
# ... 大量实验性更改 ...

# 方案 A：实验成功，合并回主分支
cd ../main-project
git merge experiment/new-architecture

# 方案 B：实验失败，丢弃
git worktree remove ../experiment-refactor
git branch -D experiment/new-architecture
```

### 4.2 Worktree 与 Stash 的配合

```bash
# 在主 worktree 有未完成的更改
# 创建新 worktree 处理紧急任务
git worktree add ../urgent-task master

cd ../urgent-task
# ... 完成紧急任务 ...

# 回来继续之前的工作
cd ../main-project
# 之前的更改还在！
```

### 4.3 IDE 集成

**VS Code**：
- 直接用 VS Code 打开不同的 worktree 目录
- 每个 worktree 有独立的扩展状态和设置

**Cursor**：
- 同样支持，每个 worktree 可以有独立的 Claude Code 会话

---

## 5. 常见陷阱与排查

### 5.1 分支冲突

**问题**：尝试创建 worktree 时检出已检出的分支

```bash
$ git worktree add ../test master
fatal: 'master' is already checked out at '/home/user/main'
```

**解决**：
- 切换到 detached HEAD：`git worktree add --detach ../test master`
- 或创建新分支：`git worktree add ../test -b new-branch master`

### 5.2 Worktree 删除不干净

**问题**：删除了目录但 `git worktree list` 还显示

**解决**：
```bash
git worktree prune  # 清理已删除的 worktree 引用
```

### 5.3 Submodule 状态异常

**问题**：新 worktree 中 submodule 显示为未初始化

**解决**：
```bash
cd <worktree>
git submodule update --init --recursive
```

---

## 6. 最佳实践

### 6.1 命名规范

```bash
# 推荐：在仓库名后加后缀
git worktree add ../<仓库名>-<用途> <分支>

# 示例
git worktree add ../AIDataEngineering-hotfix master
git worktree add ../AIDataEngineering-review feature/xxx
git worktree add ../AIDataEngineering-experiment -b experiment/xxx
```

### 6.2 位置选择

```bash
# 推荐：放在主仓库的父目录（便于管理）
/home/user/projects/
├── my-project/              ← 主仓库
├── my-project-hotfix/       ← worktree
└── my-project-review/       ← worktree
```

### 6.3 定期清理

```bash
# 查看哪些 worktree 可以清理
git worktree list

# 清理已删除目录的引用
git worktree prune

# 批量删除不再需要的 worktree
git worktree remove <路径1> <路径2>
```

---

## 7. 实操练习

### 练习 1：创建你的第一个 Worktree

```bash
cd /home/ray/Documents/BiaoGuoRepo/AIDataEngineering

# 创建一个实验性 worktree
git worktree add ../AIDataEngineering-learning -b learning/my-first-worktree

# 查看 worktree 列表
git worktree list

# 进入新 worktree
cd ../AIDataEngineering-learning

# 查看当前分支
git branch --show-current

# 做一些更改
echo "# Learning Worktree" > TEST.md
git add TEST.md
git commit -m "test: 学习 worktree 操作"

# 切回主工作目录
cd ../AIDataEngineering

# 查看更改是否可见（应该不可见，因为不同分支）
ls TEST.md  # 应该报错：文件不存在

# 清理练习
cd ../AIDataEngineering
git worktree remove ../AIDataEngineering-learning
git branch -D learning/my-first-worktree
```

### 练习 2：多分支并行开发

```bash
# 假设你要同时开发两个特性
cd /home/ray/Documents/BiaoGuoRepo/AIDataEngineering

# 创建两个 worktree
git worktree add ../AIDataEngineering-featureA -b feature/A
git worktree add ../AIDataEngineering-featureB -b feature/B

# 在 featureA 工作
cd ../AIDataEngineering-featureA
echo "Feature A" > featureA.md
git add featureA.md && git commit -m "feat: A"

# 在 featureB 工作
cd ../AIDataEngineering-featureB
echo "Feature B" > featureB.md
git add featureB.md && git commit -m "feat: B"

# 回到主目录查看
cd ../AIDataEngineering
git log --oneline --all --graph

# 清理
cd ../AIDataEngineering
git worktree remove ../AIDataEngineering-featureA
git worktree remove ../AIDataEngineering-featureB
git branch -D feature/A feature/B
```

---

## 8. 总结

### Worktree 的适用场景

✅ **适合用 Worktree**：
- 需要在多个分支间频繁切换
- 同时运行多个分支的服务对比
- 长时间并行开发多个特性
- Review 同事的分支并运行测试

❌ **不适合用 Worktree**：
- 只是偶尔切换分支（用 stash 即可）
- 需要完全独立的仓库副本（用 clone）
- 磁盘空间紧张（每个 worktree 需要额外空间）

### 关键要点

1. **一个仓库，多个工作目录**——共享 `.git`，节省空间
2. **不能有两个 worktree 检出同一分支**——防止冲突
3. **Submodule 和 direnv 需要单独初始化**——常见遗漏点
4. **定期 `git worktree prune`**——保持清洁

---

## 参考资料

- [Git 官方文档 - Worktree](https://git-scm.com/docs/git-worktree)
- [Atlassian Git Tutorial - Worktree](https://www.atlassian.com/git/tutorials/dotfiles/worktree)
- 本项目的实际 worktree 结构：`/home/ray/Documents/BiaoGuoRepo/AIDataEngineering-mcp`
