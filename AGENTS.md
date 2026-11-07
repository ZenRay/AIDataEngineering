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
- 顶层 repo 只管文档与 Agent 配置，**不吸收任何子项目代码**。定位：**个人 workspace**——唯一主场 = 个人 GitHub private（不上 GitLab）；团队数据 repo 群归 GitLab `da` 组（与伞形分置），后续数据仓在 `projects/` 下按需 clone。

## 新增 repo 流程（两条路线，判据 = 我们是否向该 repo 提交代码）

**只读上游输入源** → 注册为 submodule：

```bash
git submodule add <repo-url> submodules/<name>
git submodule set-branch --branch master submodules/<name>
git config -f .gitmodules submodule.submodules/<name>.ignore dirty
git commit -m "chore: add upstream input source <name>"
```

**主动开发的数据建设 repo** → 以 `docs/repo-template/` 为母本实例化，登记进 meta 清单（需先 `npm i -g meta`）：

```bash
cp -r docs/repo-template projects/<name> && rm projects/<name>/README.md   # 手工期（copier/cruft 选型后替换）
meta project import projects/<name> <repo-url>   # 自动更新 .meta 与 .gitignore
git commit -m "chore: register data repo <name>"
```

分层规范见 `docs/子项目Agent配置规范.md`。

> ⚠️ GitLab 首推注意：自建实例对新仓库默认分支有保护——**空仓库首次 push 需 Maintainer 角色**（与 commit 署名无关：认证=SSH key，授权=项目角色）。新 repo 首推前先解决角色或由管理员执行。

## Git 纪律

- 任何 commit/push 前先执行 `git rev-parse --show-toplevel` 确认所在仓库（有 Agent 跨仓库提交到错误仓库的官方事故先例）。
- 子仓库（submodules/、projects/ 下）的提交在其自身目录内进行，遵循其自身分支规范。
- 不 force push、不直接推主干，除非用户明确要求。
- **默认分支**：伞形仓与新建数据仓的默认分支统一为 `master`（`git init -b master`）；上游 submodule 统一跟踪 master。存量仓的历史分支名（如 data-warehouse 的 main）保持不改，各仓分支模型写入其自身 AGENTS.md。
- meta 团队增量同步是**两步**：`git pull`（拉新 .meta 清单）→ `meta git update`（clone 本地缺失的子仓库）。`meta git update` 不会拉取清单本身。
- Repo 远端与双 host：伞形 repo = **GitHub 个人单主**（无双推）。**数据 repo**：GitLab(da) 为团队主；需要个人副本时才配多 push URL（方案 A，仅副本 owner 机器、SSH URL）——非原子，push 后逐 URL 核对；**分支 push 不携带 tag**，同步副本需显式 `git push origin --tags`；副本仓不设写协作者（天然只读）。
- **URL 脱敏（入库前既定）**：`.gitmodules`/`.meta` 一律使用别名前缀（`upstream:`=输入源组、`upstream-user:`=user 组、`darepo:`=数据仓组），真实域名只存在于各机器本机的 `~/.gitconfig`（`url.*.insteadOf` 映射，永不入库/推送）。新机器首次配置：向负责人索取三条 `git config --global` 映射命令（走内网/线下渠道）；`scripts/onboarding.sh` 会检查该映射。**改过 `.gitmodules` 的 URL 后，每台机器须跑一次 `git submodule sync`**——否则子模块本机仍用旧 URL（2026-11-04 首次 bump 实战踩过，指南 Q8）。
- 伞形仓 `.gitmodules` 指针最终指向内网 GitLab——`git submodule update --init` 仅在可达内网（VPN/代理）且已配映射的机器可完成。

### 提交规范（伞形仓与数据仓通用；团队数据仓自有规范时从其规范）

- 格式：`<type>(<scope>): <English subject>`——**subject 用英文**（祈使语气、无句号）；body 可选，可用中文。
- type 白名单：`feat / fix / docs / chore / refactor / revert`；安全类提交收编为 `fix(security):` / `chore(security):`；Merge 提交保留 git 默认生成。
- scope 可选；下列固定格式提交必带（CI 影响分析将依赖其解析）。
- **无机器人尾注**：commit message 不写 Co-Authored-By / Generated-with 类 trailer（对所有 Agent 生效）。
- 固定格式（三类特殊提交）：
  - 新增只读输入源：`chore: add upstream input source <name>`
  - 注册数据仓：`chore: register data repo <name>`
  - submodule 指针 bump：`chore(submodules): bump <name> to <short-sha>`（单独 bump 提交/PR，CI 接入后据此运行影响分析）
- 强制层：单人期为指令层软约束（不引入 commitlint/hook）；规范只约束增量，**不改写存量历史**。
- 代码工件语言：代码内**注释与 docstring 一律英文**；中文仅用于面向人的文档（README/docs/学习笔记）。各语言工具基线见 `docs/repo-template/README.md`「语言基线」节。

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

**新成员 onboarding**：入口文档 = `docs/新人Onboarding与配置自检指南.md`（心智模型、安装清单、配置地图、10 项自检矩阵、故障排查、验收标准）；顺序 clone → 配别名映射 → `scripts/onboarding.sh` → 人工审查 → 启动 Claude Code 并 trust（trust 前提示偏多属正常）。制度：**本 workspace 禁用 bypass/自动接受模式**（ask 软约束会全部失效）。

## MCP 使用纪律（2026-11 新增）

MCP（Model Context Protocol）服务器代表**任意代码执行**，工具行为描述应被视为不可信。基于 MCP 安全模型研究（详见 `BackDocs/mcp-research/mcp-research-synthesis.md`），制定以下纪律：

**强制要求**：
- ✅ `.mcp.json` 变更必须走 PR 审查（与 `.claude/settings.json` 同等对待）
- ✅ 禁止在 `.mcp.json` 或 `.envrc` 中硬编码凭据（连接字符串、API key、密码）
- ✅ HTTP 传输的 MCP 服务器必须绑定到 127.0.0.1（本地开发）或使用 TLS（远程）
- ✅ 凭据必须通过 Authorization 头传递，**禁止**出现在 URL 查询字符串中
- ✅ 新增 MCP 服务器前必须完成安全评估（来源、权限范围、数据传输）

**当前配置**（2026-11-05 PoC 初版，worktree 会话实测连通）：
- 项目级 `.mcp.json`：`bg-mysql-mcp`（MySQL 连接器）+ `bg-nacos-mcp-test`（Nacos 配置中心），均测试环境
- 传输类型：Streamable HTTP（远程）；凭据经 `Authorization: Bearer` 头传递
- 凭据注入：`.mcp.json` 一律 `${VAR}` 展开；真实值只存本机 `.env`（gitignore，永不入库），`.envrc` source `.env`
- ⚠️ **启动环境要求**：`${VAR}` 展开发生在 **claude 进程启动时**（读进程环境）；SessionStart hook 的 `CLAUDE_ENV_FILE` 前言只作用于 Bash 工具，**到不了 MCP 配置**。必须从 direnv 已加载的 shell 启动 claude（zsh 需 `~/.zshrc` 含 `eval "$(direnv hook zsh)"`），否则 server 报 INVALID_CONFIG（2026-11-05 实测：Bash 内变量齐全而 MCP 展开为空——通道不对称）

**禁用配置**：
- 🚫 `enableAllProjectMcpServers`（批量启用，违反逐一审批原则）
- 🚫 `enabledMcpjsonServers`（预先批准列表，违反交互审批原则）
- 🚫 未经审查的第三方 MCP 服务器
- 🚫 令牌传递（token passthrough）——每个 MCP 服务器必须验证自己的令牌

**Onboarding 检查**：
新成员必须执行 `scripts/onboarding.sh` 中的 MCP 配置验证步骤（检查 `.mcp.json` 存在、`.envrc` 配置完整、无硬编码凭据）。

**技术细节**（详见研究报告）：
- 协议版本：MCP 2026-07-28（无状态架构）
- 传输机制：stdio（本地）/ Streamable HTTP（远程）
- 安全模型：Origin 头验证、OAuth 2.1（HTTP）、每客户端同意流程
- 防御层级：机制层（settings.json）+ 保安层（hooks）+ 指令层（本文件）

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
