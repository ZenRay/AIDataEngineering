# 新人 Onboarding 与配置自检指南

> **给谁看**：第一次在这套 workspace 上干活的人（人或 AI 助手的新会话都一样）。
> **花多久**：读 20 分钟 + 动手 30 分钟（含 §4 自检）。
> **配好了的判据**：§6 验收全绿。任何一步卡住查 §5 排查表。
> 姊妹文档：为什么这样设计 →《伞形工作区环境初始化决策记录》（docs/LearningNote）；规矩原文 → [AGENTS.md](../AGENTS.md)。

---

## 0. 五分钟心智模型

```
AIDataEngineering/                    ← 伞形仓：只管规则/清单/文档，不装业务代码
├── .gitmodules    清单①：8 个只读输入源（submodule 指针，锁 commit）
├── .meta          清单②：数据建设 repo（团队成员共同开发的那些）
├── AGENTS.md      规则：所有 AI 编码 Agent 的共享约定（入口：CLAUDE.md 一行导入）
├── .claude/
│   ├── settings.json  门禁：deny（绝对拒）/ ask（逐次弹框问人）/ allow（放行）
│   └── hooks/         保安：Agent 每次动工具前先过一遍脚本（exit 2 = 拦）
├── .envrc             环境：direnv 方案（详见笔记《环境工具链》）
├── scripts/onboarding.sh   新人自动化引导（会把你缺什么全查一遍）
└── docs/repo-template/     新数据仓的内容母本
```

**理解这套设计的两把钥匙**：

1. **"讲道理"不可靠，"门禁"才可靠**——写进 AGENTS.md 的规则，AI 可能不听；写进 `.claude/settings.json` 的 deny/ask 由客户端强制执行，AI 没有选择权。**必须防的事全在门禁层，AGENTS.md 只是第三层兜底。**
2. **仓里的仓库地址全是别名**（`upstream:` `upstream-user:` `darepo:`）——真实内网域名只存在每人本机的 `~/.gitconfig` 里，永不入库。没配映射 = 什么仓都拉不下来（§1 教你配）。

---

## 1. 前置准备

### 1.1 本机装什么

| 工具 | 最低版本 | 用来干什么 | **缺了会怎样** |
|------|------|------|------|
| git | ≥2.4 | 一切的基础 | —— |
| **jq** | 1.7 | hooks 脚本解析 stdin | 🔴 **保护静默失效**（hook 崩溃但不拦截，不报错）——装完必自检 §4-9 |
| direnv | 2.3x | 进目录自动切环境变量 | Agent 环境注入失效 |
| Node + npm | ≥18 | 装 meta | 无法 bootstrap 数据仓 |
| meta（`npm i -g meta`） | 2.2.25 | 多仓清单同步 | 只有伞形仓视角，拉不齐数据仓 |
| claude CLI | **≥1.0.111** | AI 编码 Agent | 低于此版本有已披露的配置注入漏洞（CVE-2025-59536），**不许用** |

### 1.2 向负责人要什么（两件，别客气）

1. **三条别名映射命令**（`git config --global url."…".insteadOf "upstream:"` ×3）——因为真实内网地址故意不进仓库，只能人肉/内网渠道传递。拿到后直接粘贴执行。
2. **账号权限**：内网 GitLab 账号 + SSH key 上传 + `da` 组（数据仓）与输入源仓库的读权限。

### 1.3 网络前提

在**可达内网**的环境操作（办公网/VPN/代理）。伞形仓本体在 GitHub，但 `.gitmodules` 指向的内网仓在公网环境下拉不动——不是配置坏了，是物理事实。

---

## 2. Onboarding 流程（照做即可）

```bash
# ① clone 伞形仓（GitHub 上的个人/团队镜像仓，找负责人要地址）
git clone <伞形仓 GitHub 地址> AIDataEngineering && cd AIDataEngineering

# ② 配置别名映射（§1.2 拿到的三条命令，粘贴执行）

# ③ 跑引导脚本——它会检查 §1.1 全部工具、扫描提交配置的负面清单、
#    带你过一遍"先审查后信任"、初始化全部子仓、direnv 放行
./scripts/onboarding.sh

# ④ 按脚本末尾提示：在仓库根启动 claude → 弹窗出现时先对照 §3 的
#    "trust 前须知"再看是否点信任

# ⑤ 跑 §4 自检矩阵（10 项），全绿 = 环境就绪
```

⚠️ **顺序铁律：clone → 看配置 → 再 trust**。仓库里的 `.claude/settings.json`、hooks 脚本属于"拿到就会执行"的文件——先花 5 分钟把它们读完（你有权审查为你机器配置的每一个人），确认没问题再点信任。

---

## 3. 配置地图：什么文件在哪、谁能改

| 文件 | 作用 | 改它的规矩 |
|------|------|------|
| `AGENTS.md` / `CLAUDE.md` | AI 行为约定 | 常规 PR 审查 |
| `.claude/settings.json` | 门禁规则（deny/ask/allow）+ hooks 注册 | 🔴 **强制双人审**（它决定所有 Agent 能碰什么；负面清单：禁 `enable*` 预批键、禁 env 端点覆盖） |
| `.claude/hooks/*.sh` | 保安脚本 | 🔴 同上——提交的脚本=拿到即执行 |
| `.gitmodules` / `.meta` | 两张清单 | bump/登记走约定流程（AGENTS.md「新增 repo」） |
| `.envrc` | 环境变量 | 敏感值**禁止**明文写入（走注入工具，问负责人） |
| `~/.gitconfig`（本机！） | 别名映射 | 每台机器配一次，**永不入库** |
| `.claude/settings.local.json`（本机） | 你个人的放宽/偏好 | gitignored；**团队保护禁止只写在这里**（clone 即生效的必须是仓内 deny/ask） |

---

## 4. 自检矩阵：怎么知道配置生效了（核心，10 项）

> 弹框类测试（②③⑤）需在**默认模式**下进行（别开 bypass/自动接受——见 §5 Q4）。

| # | 验什么 | 怎么测 | 期望看到 | 不对时 |
|:---:|------|------|------|:---:|
| 1 | 输入源只读 | 让 Agent：把一行字写进 `submodules/<任意仓>/t.txt` | 收到 `Blocked: …命中绝对保护路径`，文件不存在 | §5-Q1 |
| 2 | 受限区读写问人 | 让 Agent：读 `BackDocs/research/` 任意文件名（负责人会给）；再试写 | **各弹一次确认框**，理由提到受限目录/ask；点一次拒绝，Agent 应收到拒绝反馈并停手 | §5-Q2 |
| 3 | archive 绝对禁 | 让 Agent：读 `BackDocs/archive/` 任意文件 | **直接拒绝、连弹框都没有** | §5-Q2 |
| 4 | push 拦一道 | 在有远端的仓里让 Agent `git push` | 弹框（理由含"远端不可逆操作"）——注意复合命令（`cd x && git push`）拦不住是已知设计边界，别当安全边界用 | 记录即可 |
| 5 | Bash 重定向也被拦 | 让 Agent 跑 `echo a > submodules/css/x.txt` | 权限拒绝（deny 覆盖重定向目标） | §5-Q1 |
| 6 | direnv 注入 | 让 Agent 跑 `echo $DIRENV_DIR` | 输出含本仓路径（`-`开头=已 allow） | §5-Q3 |
| 7 | cd 跟随 | 在含 `.envrc` 的子仓里让 Agent 再跑一次 | 值变为该子目录 | §5-Q3 |
| 8 | 清单齐 | `git submodule status`（行数应与 `.gitmodules` 段数一致）+ `meta git update` 无报错 | 全部就位；别名解析正常即 `~/.gitconfig` OK | §5-Q5 |
| 9 | hooks 自身完好 | `echo '{"tool_input":{"command":"git push"}}' \| .claude/hooks/confirm-push.sh` | 打印一段含 `"permissionDecision":"ask"` 的 JSON | 装 jq！§1.1 |
| 10 | 仓端 CI（若已接 GitHub） | push 后看 Actions | `ci-baseline` 绿 | 找负责人 |

## 5. 常见问题排查表

| 症状 | 最可能原因 | 动作 |
|------|------|------|
| Q1 写 submodules 竟然成功了 | jq 没装（hook 崩溃）或 settings 被改 | 跑 §4-9；`git log -3 .claude/` 看配置有没有被动过 |
| Q2 该弹框的不弹、直接通过 | ① 会话开了 bypass/自动接受 ② ask 环境性问题（见 Q6） | shift+tab 切回默认重试；仍不弹记入已知项（ask 属体验层，deny 活着即安全线未破，对照 §4-1/3/5） |
| Q3 DIRENV_DIR 为空 | direnv 未装/全局 hook 缺/该目录没 allow | 重跑 `./scripts/onboarding.sh`（它管 allow）；zsh/bash rc 加 `eval "$(direnv hook …)"` |
| Q4 bypass 模式是什么为什么禁 | 一键让所有"问人"变自动放行（deny 仍拦），方便但危险 | 本 workspace 制度禁用（理由：新人/未审查场景全靠 ask 兜着）；测完敏感操作就切回 |
| Q5 拉仓报 `upstream:xxx does not appear to be a git repository` | 别名映射没配 | 补 §1.2-1 三条命令 |
| Q6 新人自测全过但以前的人记录说"没弹框" | 历史环境差异（版本/模式），不是你的错 | 以你 §4 的实测为准并在笔记追加一行环境时点 |
| Q7 Actions 红 | 模板演进/依赖了内网资源（设计上不该有） | 对照 ci-baseline："只做仓内自洽"是唯一契约 |
| Q8 bump/fetch 时索要 HTTP 账号密码、或报 `could not read Username` | `.gitmodules` 改过（如脱敏换别名）但未同步到子模块**本机** config——fetch 用的是本机 URL | `git submodule sync` 一次即可（把 .gitmodules 的 URL 刷进各子模块本机）；本仓 2026-11-04 首次 bump 实战踩过 |

---

## 6. 验收标准（什么算配好了）

- [ ] §4 的 1、3、5、6、7、8、9 必绿（硬防护+环境+清单）
- [ ] §4 的 2、4 弹框：**弹框本体已验证**（2026-11-05 裸起会话人见证，C1 已关闭）。若你的会话不弹 → 先查**启动方式**：harness/IDE/自动通过族拉起的会话可能不弹，新终端裸起 `claude` 会弹；仍不弹按 Q2 处理并记录（**不阻塞验收**，因为硬防护= deny 层已证）
- [ ] `git status --short` 输出干净、`git log --oneline -1` 能看到最近约定
- [ ] 通读过 AGENTS.md 的「仓库结构」「Git 纪律」「配置审查制度」三节，有异议已提出
