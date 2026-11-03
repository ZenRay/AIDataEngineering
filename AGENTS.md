# AIDataEngineering 项目集约定

> 本文件是所有 AI 编码 Agent（Claude Code / Codex / Cursor 等）的共享规则单一事实源。
> Claude Code 经同目录 CLAUDE.md（`@AGENTS.md`）导入；子仓库可有自己的 AGENTS.md（最近文件优先 / 惰性加载）。
> 本文件是上下文约定，**不具强制力**——硬性边界由 `.claude/settings.json` 的 deny/ask 规则与 hooks 强制。

## 仓库结构

- `submodules/`：git submodules，线上业务代码**只读输入源**（锁 commit 指针，统一跟踪 master 分支）。
  数仓开发从中提取表结构/业务逻辑/埋点，并需感知上游变更。
  **禁止在其中提交/推送**；指针 bump 只能通过专门的 bump 提交/PR（CI 接入后将运行影响分析）。
- `projects/`：数据建设 repo（meta 清单管理、各自独立 remote/分支；Phase 2 启用，本目录被顶层 gitignore）。
- `BackDocs/`：个人存档区（**长期受限目录**）：读取与修改均需用户当场确认（ask 规则逐次弹框）；
  `BackDocs/archive/` 读写均绝对禁止（deny + hooks）。不主动索引、不主动引用其内容。
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

> ⚠️ GitLab 首推注意：自建实例对新仓库默认分支有保护——**空仓库首次 push 需 Maintainer 角色**（与 commit 署名无关：认证=SSH key，授权=项目角色）。新 repo 首推前先解决角色或由管理员执行。

## Git 纪律

- 任何 commit/push 前先执行 `git rev-parse --show-toplevel` 确认所在仓库（有 Agent 跨仓库提交到错误仓库的官方事故先例）。
- 子仓库（submodules/、projects/ 下）的提交在其自身目录内进行，遵循其自身分支规范。
- 不 force push、不直接推主干，除非用户明确要求。
- meta 团队增量同步是**两步**：`git pull`（拉新 .meta 清单）→ `meta git update`（clone 本地缺失的子仓库）。`meta git update` 不会拉取清单本身。
- 双 host（GitLab 团队主 + GitHub 个人副本，Phase 1 定案=多 push URL，仅副本 owner 机器配置、SSH URL）：非原子，push 后逐 URL 核对两侧结果；**分支 push 不携带 tag**，需同步副本时显式 `git push origin --tags`；副本 repo 不设写权限协作者（天然只读）。

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

## 环境工具链（已定：方案 D — direnv 路线）

**分工**（决策依据见 BackDocs/research 研究文档 §4，mise 因官方不支持与 direnv 共存而出局）：

- 环境变量 / PATH / 凭据注入 → **direnv**：`.envrc` 提交入库；每台机器每目录一次性 `direnv allow`
- Python 版本 + venv + lock → **uv**：各子项目为独立 uv 项目（不用 uv workspace）；`uv python pin` 写 `.python-version`；纪律：**不要在 .venv 里手工 pip install**（会被下次 `uv sync` 剪除），依赖变更一律走 pyproject + uv lock；uv.lock 提交
- Node 版本 → **待 PoC 选型**（候选：Volta（shim 免 hook，Agent 非交互 shell 友好，未验证）或 fnm + `.node-version`）；定案前 Node 项目暂用 `.nvmrc`
- **不引入 mise**（官方明确与 direnv 共存 unsupported）

**Agent 环境注入（官方机制，已配置）**：顶层 `.claude/settings.json` 的 SessionStart + CwdChanged 双 hook 执行 `direnv export bash > "$CLAUDE_ENV_FILE"`——Agent 每条 Bash 命令自动携带当前目录环境；`/cd` 进子 repo 后自动重载。

**命令纪律（Agent 与脚本都要遵守）**：

- 每条 Bash 命令都是新 shell：**export 不跨调用保留**——多步依赖写成单条命令，或依赖 CLAUDE_ENV_FILE 前言注入
- CI / 非交互脚本用 `direnv exec <dir> <cmd>` 或 `eval "$(direnv export bash)"` 显式加载（hook 式自动加载只在交互 shell 生效）
- 成员 shell rc 文件的交互专属段需加非交互 guard（`[[ $- != *i* ]] && return`），防止破坏 Agent 的 Bash 工具

**新成员 onboarding（环境部分）**：安装 direnv → 全局 shell hook → 在含 `.envrc` 的每个目录 `direnv allow` → （未来由 onboarding 脚本自动化）。

## 上下文隔离

- 处理某子项目时，优先阅读该子项目自己的 AGENTS.md / README。
- 跨子项目改动须先列出影响范围并征得用户确认。
