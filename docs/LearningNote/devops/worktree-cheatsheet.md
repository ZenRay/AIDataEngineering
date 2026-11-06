# Git Worktree 快速参考卡

> 打印这张小抄贴在工位上！

## 核心命令

```bash
# 创建（新分支）
git worktree add <路径> -b <新分支>

# 创建（已有分支）
git worktree add <路径> <已存在分支>

# 查看所有
git worktree list

# 删除
git worktree remove <路径>

# 清理（删除目录后）
git worktree prune
```

## 本项目的 Worktree

```bash
# 查看当前所有 worktree
git worktree list
```

**输出示例**：
```
AIDataEngineering/                      c21decf [dw-poc]
AIDataEngineering-mcp/                  f4d6004 [master]
AIDataEngineering-learn-worktree/       c21decf [learning/worktree-demo]
```

## 常用场景

### 1. 紧急修复 master

```bash
git worktree add ../AIDataEngineering-hotfix master
cd ../AIDataEngineering-hotfix
# 修复... commit... push...
cd ../AIDataEngineering
git worktree remove ../AIDataEngineering-hotfix
```

### 2. Review 同事分支

```bash
git fetch origin
git worktree add ../AIDataEngineering-review origin/feature/xxx
cd ../AIDataEngineering-review
# 运行、测试、review
cd ../AIDataEngineering
git worktree remove ../AIDataEngineering-review
```

## ⚠️ 注意

1. **Submodule 要手动初始化**：
   ```bash
   cd <新 worktree>
   git submodule update --init --recursive
   ```

2. **direnv 要单独 allow**：
   ```bash
   cd <新 worktree>
   direnv allow
   ```

3. **不能有两个 worktree 检出同一分支**

## 完整文档

详见：[Git Worktree 使用指南与实战](2026-11-05-Git-Worktree使用指南与实战.md)
