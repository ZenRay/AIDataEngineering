# 子项目 Agent 配置规范

> 适用于 `projects/` 下所有数据建设 repo 的 Agent 配置分层约定。执行层摘要见伞形 `AGENTS.md`；论证与验证细节见 `BackDocs/research/Agent配置与环境管理研究.md` §2/§4/§5（下称《专项》）。内容自 `docs/repo-template/` 的说明同步维护。

## 1. 三条铁律（全部 ✅ 已验证机制）

1. **双轨制**：从伞形根启动会话时，子 repo 的 `.claude/settings.json` **不加载**（官方设计）。因此——
   - **硬边界（deny/ask/hooks）必须写在伞形顶层** settings.json（clone 即生效层）
   - 子 repo 的 settings.json 只为**独立 clone / `/cd` 进入**场景服务，内容**自包含**、只放本 repo 的 allow 体验优化与本地加固
2. **机制层优先**：必须防的写 deny（全模式生效，bypass 也拦）；"许可可解锁"的写 ask（逐次弹框；bypass 模式自动放行——制度上本 workspace 禁用 bypass）；CLAUDE.md/AGENTS.md 里的文字**不是**防护。
3. **单一事实源**：每个 repo 一份 `AGENTS.md`（只写本 repo 差异：技术栈、命令、规范），`CLAUDE.md` 固定一行 `@AGENTS.md`。不建 `CLAUDE.local.md`（会静默禁用 AGENTS.md 加载，除非用户级 instructionFiles——默认不设）。

## 2. 配置项 × 放置（摘要，全表见《专项》§2.4）

| 文件 | 伞形顶层 | 子 repo | 提交 |
|------|:---:|:---:|:---:|
| AGENTS.md（含 Codex 桥接段） | ✅ | ✅ 只写差异 | 均提交，PR 审查 |
| CLAUDE.md（`@AGENTS.md`） | ✅ | ✅ | 提交 |
| .claude/settings.json | ✅ 全部硬边界 + 汇总 allow | ✅ 自包含 allow | 提交，强制审查 |
| settings.local.json / CLAUDE.local.md | 个人 | — | **禁止提交** |
| .claude/skills/（团队命令统一用 skills 布局，commands 已 legacy） | 项目集级 | ✅ repo 级 | 提交，逐项审 allowed-tools 与 `!` 注入 |
| .mcp.json（凭据一律 `${VAR}`，禁明文；禁 enable* 键） | ✅ 根会话只认项目根的 | ✅ 服务 standalone | 提交，强制审查 |
| sandbox 配置 | ❌ 个人级 local/用户级 | ❌ | 组织强制走 managed（暂无基建） |
| direnv `.envrc` | ✅ | ✅（父子继承 `source_up` 语义【待实测】） | 提交（`.direnv/` 不提交） |

## 3. 新建子 repo 操作流程

```bash
# ① 以模板实例化（copier/cruft 选型前：手工复制；选型后：copier copy <模板仓 URL> projects/<name> --VCS-ref latest 或 cruft create）
cp -r docs/repo-template projects/<name> && rm -f projects/<name>/README.md  # 手工期（亦可改写为项目 README 代替删除）
# ② 填内容——按 docs/repo-template/README.md「实例化」节完整清单逐项打勾，勿只做表层步骤：
#    AGENTS.md 写本 repo 差异；settings.json allow 增补本工具链高频命令（deny 不动）；
#    pyproject 改 name/依赖后 uv lock；核对 gitleaks rev
# ③ 登记与提交
git -C projects/<name> init && git -C projects/<name> remote add origin <url>
meta project import projects/<name> <url> && git commit -m "chore: register data repo <name>"
```

## 4. 安全红线（子 repo 作者必知）

- 提交的任何 Agent 配置（settings/hooks/skills/.mcp.json/.codex/config.toml）= "clone 即执行面"，变更走 PR 审查（CVE-2025-59536 教训）
- hooks 脚本永远 **fail-safe**（出错时宁可阻断）：只有 exit 2 才阻断，非零≠阻断
- 凭据不进文件、不进 env 键明文；sops/1Password 注入路线见《专项》§6.5（sops 完整工作流【待 PoC】）
- Node/Python 环境：Python 走 uv（`.python-version`，禁手工 pip）；Node 待 PoC 定案（候选 Volta/fnm），定案前用 `.nvmrc`
- 首个 workflow 上 GitHub 属"🔮→✅ 冒烟"：跑绿后更新 README 状态板（这不是探针，探针只在**换平台/换网络域**时跑，方法论见探针笔记 §1-5）
