# AIDataEngineering 项目集约定

> 本文件是所有 AI 编码 Agent（Claude Code / Codex / Cursor 等）的共享规则单一事实源。
> Claude Code 经同目录 CLAUDE.md（`@AGENTS.md`）导入；子仓库可有自己的 AGENTS.md（最近文件优先 / 惰性加载）。
> 本文件是上下文约定，**不具强制力**——硬性边界由 `.claude/settings.json` 的 deny/ask 规则与 hooks 强制。

## 仓库结构

- `submodules/`：git submodules，线上业务代码**只读输入源**（锁 commit 指针，统一跟踪 master 分支）。
  数仓开发从中提取表结构/业务逻辑/埋点，并需感知上游变更。
  **禁止在其中提交/推送**；指针 bump 只能通过专门的 bump 提交/PR（CI 接入后将运行影响分析）。
- `projects/`：数据建设 repo（meta 清单管理、各自独立 remote/分支；Phase 2 启用，本目录被顶层 gitignore）。
- `BackDocs/`：个人存档区（**长期受限目录**）：读取需用户当场确认（ask 规则弹框，逐次确认）；
  `BackDocs/archive/` 绝对禁止读取（deny）；整个目录禁止修改（deny + hooks）。不主动索引、不引用其内容。
- `docs/`：项目集级文档。
- 顶层 repo 只管文档与 Agent 配置，**不吸收任何子项目代码**。

## 新增 repo 流程（两条路线，判据 = 我们是否向该 repo 提交代码）

**只读上游输入源** → 注册为 submodule：

```bash
git submodule add <repo-url> submodules/<name>
git submodule set-branch --branch master submodules/<name>
git config -f .gitmodules submodule.submodules/<name>.ignore dirty
git commit -m "chore: add upstream input source <name>"
```

**主动开发的数据建设 repo** → 放 projects/ 并登记进 meta 清单（Phase 2+，需先 `npm i -g meta`）：

```bash
meta project import projects/<name> <repo-url>   # 自动更新 .meta 与 .gitignore
git commit -m "chore: register data repo <name>"
```

## Git 纪律

- 任何 commit/push 前先执行 `git rev-parse --show-toplevel` 确认所在仓库（有 Agent 跨仓库提交到错误仓库的官方事故先例）。
- 子仓库（submodules/、projects/ 下）的提交在其自身目录内进行，遵循其自身分支规范。
- 不 force push、不直接推主干，除非用户明确要求。
- meta 团队增量同步是**两步**：`git pull`（拉新 .meta 清单）→ `meta git update`（clone 本地缺失的子仓库）。`meta git update` 不会拉取清单本身。
- 双 host（GitHub+GitLab，Phase 1）启用后：多 push URL 非原子，push 后须确认两个 host 均成功；mirror host 制度性只读。

## 跨工具桥接（Codex 特别注意）

Codex **不会**自动读取子目录的嵌套 AGENTS.md（只拼接项目根→启动目录链）：
**进入 `submodules/<repo>/` 或 `projects/<repo>/` 工作或计划改动前，必须先读取该目录下的 AGENTS.md（如存在）**。
Claude Code / Cursor 有惰性加载机制可自动获得子目录指令，但显式先读同样推荐。

## 配置审查制度（安全红线）

以下文件一经提交即是「clone 即获得的执行面」（CVE-2025-59536 先例：提交的 settings + 恶意 .mcp.json 可在 trust 确认前执行命令）。
**变更必须走 PR 审查；单人开发期暂由提交人 `git show` 自行复核**：

- `.claude/settings.json`（尤其 hooks、env、permissions 段）
- `.claude/hooks/**`、`.claude/skills/**`（allowed-tools 与 `!` 注入命令逐项过目）
- `.mcp.json`、`.codex/config.toml`（未来启用时）

**负面清单（提交的配置中禁止出现）**：

- `enableAllProjectMcpServers` / `enabledMcpjsonServers` 键（MCP 审批必须由每个成员交互完成）
- `env` 中 `ANTHROPIC_BASE_URL` 等凭据/端点覆盖类变量

**新成员 onboarding 顺序**：clone → 人工审查上述配置 → 再启动 Claude Code 并 trust（trust 前权限提示偏多属正常，deny/ask 保护已生效）。

## 环境工具链

**待定**（Phase 0 步骤 4：mise vs direnv 二选一，官方不支持二者共存）。
决定后更新本节，并向 `.claude/settings.json` 回填对应配置（direnv 路线：SessionStart + CwdChanged 双 hook 写 `$CLAUDE_ENV_FILE`；mise 路线：Agent 命令用 `mise exec --` 包装约定）。

## 上下文隔离

- 处理某子项目时，优先阅读该子项目自己的 AGENTS.md / README。
- 跨子项目改动须先列出影响范围并征得用户确认。
