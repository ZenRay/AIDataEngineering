# 🌳 Git Worktree 学习资源导航

> 欢迎来到 Git Worktree 学习中心！所有资源已就绪，可以开始学习了。

---

## 📚 学习资源

### 🎯 新手入门路径（推荐顺序）

```
1. 先看这个 ↓
   📖 2026-11-05-Worktree学习成果总结.md
   （了解全貌和环境状态）

2. 然后看这个 ↓
   🎨 worktree-diagram.html
   （用浏览器打开，直观理解）

3. 深入学习 ↓
   📖 2026-11-05-Git-Worktree使用指南与实战.md
   （完整文档，包含所有细节）

4. 随时查阅 ↓
   📋 worktree-cheatsheet.md
   （快速参考卡，打印出来）
```

---

## 📂 文件清单

| 文件 | 用途 | 何时查看 |
|------|------|----------|
| `2026-11-05-Worktree学习成果总结.md` | 学习环境总览 | 开始学习前 |
| `2026-11-05-Git-Worktree使用指南与实战.md` | 完整教程 | 系统学习时 |
| `worktree-cheatsheet.md` | 快速参考 | 日常使用时 |
| `worktree-diagram.html` | 可视化图表 | 理解概念时 |
| `README-worktree.md` | 本文件 | 找资源时 |

---

## 🌲 当前 Worktree 环境

```bash
git worktree list
```

输出：
```
AIDataEngineering/                      [dw-poc]         ← 主工作目录
AIDataEngineering-learn/                [learn-worktree]
AIDataEngineering-learn-worktree/       [learning/worktree-demo]  ← 🎯 学习专用
AIDataEngineering-mcp/                  [master]
.worktrees/data-lineage/                [feature/data-lineage]
```

---

## 🚀 快速开始

```bash
# 1. 进入学习专用 worktree
cd /home/ray/Documents/BiaoGuoRepo/AIDataEngineering-learn-worktree

# 2. 开始练习！
git status
echo "Learning worktree" > test.txt
git add test.txt
git commit -m "learning: first commit"

# 3. 查看效果
cd ..
ls AIDataEngineering-learn-worktree/test.txt
ls AIDataEngineering/test.txt  # 不存在（不同分支）
```

---

## 💡 核心概念

**Git Worktree = 一个仓库，多个工作目录**

```
┌─────────────────────┐
│   .git/ (共享)       │
└─────────────────────┘
         ↓
    ┌────┴────┬─────────┬─────────┐
    ↓         ↓         ↓         ↓
  master    dev-A     dev-B    hotfix
  (目录1)   (目录2)   (目录3)   (目录4)
```

**优势**：
- ✅ 无需频繁 stash/checkout
- ✅ 可以同时运行多个分支
- ✅ 保持上下文，不丢失工作
- ✅ 共享仓库，节省空间

---

## 📝 速查命令

```bash
# 创建
git worktree add <路径> -b <新分支>

# 查看
git worktree list

# 删除
git worktree remove <路径>

# 清理
git worktree prune
```

---

## ⚠️ 注意

1. **新 worktree 必须初始化**：
   ```bash
   git submodule update --init --recursive
   direnv allow
   ```

2. **不能有两个 worktree 检出同一分支**

3. **用完记得清理**：
   ```bash
   git worktree remove <路径>
   ```

---

## 🔗 更多资源

- **Git 官方文档**：https://git-scm.com/docs/git-worktree
- **学习笔记索引**：`docs/LearningNote/index.md`
- **AGENTS.md**：查看 Git 纪律章节

---

**开始你的 Worktree 学习之旅吧！** 🎉
