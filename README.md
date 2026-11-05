# AIDataEngineering

数据建设项目集伞形 workspace：线上业务代码仓库群（只读输入源，git submodules，清单以 [`.gitmodules`](./.gitmodules) 为准）+ 数据建设 repo 群（meta 清单 `.meta`，`projects/`）+ Data Agent 基建（规划中）。

- **新人从这里进**：[docs/新人Onboarding与配置自检指南.md](./docs/新人Onboarding与配置自检指南.md)（装什么/配什么/怎么验，10 项自检矩阵 + 排查表）
- 团队/Agent 约定：[AGENTS.md](./AGENTS.md)（单一事实源，Claude Code 经 CLAUDE.md 导入）
- 决策记录与研究证据：docs/LearningNote/（叙事层）· BackDocs/research/（证据层，读取需负责人确认）
- TODO 编号规则：**E**=执行项、**D**=待拍板决策、**C**=收尾/清理动作；每项标注所属 Phase 与完整版 §8 步骤号

## 状态速览

| 项 | 状态 |
|------|------|
| Phase 0（伞形定型/hooks 硬边界/direnv 环境/规范+模板+onboarding/**URL 脱敏**） | 🔶 **功能收敛（v1.9 修正）**：6/8 步全收口；**两项显式挂起**——D1 决策挂起（触发：第二仓 or 2027-01 先到为准）、C1 验证挂起（新终端裸起 claude 跑 hostname 看弹框，2 分钟可关闭）。此前"挂起均非欠账"的说法系收口标准掺水，已勘误 |
| Phase 1（架构定案 v2.11：**伞形=GitHub 个人单主**，不上 GitLab；双 host 转为数据仓备选能力，方案 A 已验证） | ✅ **伞形仓部分完成**（首推 66edfdd + CI 冒烟全绿，2026-11-04）；R1① 角色已获（服务 da 组数据仓与 E4） |
| Phase 2 meta 清单 | ✅ **已激活**（E3 完成，commit 5314783）：`.meta` 登记 nl2sql-backend + 队友两步同步真实首演成功；与 .gitmodules 双清单并存 |
| GitHub CI | ✅ 探测定案 + **伞形仓 ci-baseline 首跑全绿**（validate-configs + secret-scan，2026-11-04）：模板 🔮→✅ 转正；hosted 不可达内网 → 落位表见探针笔记 |
| GitLab CI | ⏸️ 暂缓（E4，待 R1 + runner 情报；移植指南现成） |
| MCP PoC（初版） | 🔶 **配置/制度已并 master（beddb8a..bf3ed25），连通收口待验**：`.mcp.json`（MySQL+Nacos，HTTP + `${VAR}`/.env 注入）+ AGENTS 纪律 + onboarding .env 四连检；worktree 会话实测连通。**新发现（本会话活体证据）**：MCP `${VAR}` 展开读 claude 进程启动环境，SessionStart hook 前言只到 Bash——通道不对称 → 关闭路径 E10 |

## TODO 看板（按阶段分组）

### Phase 0 · 收尾（工作区内已清零，剩可延项）

| # | 事项 | 归属 | 触发 / 阻塞 |
|:---:|------|------|------|
| **D1** | 🧯 决策挂起（Phase 0 未收口项 1/2）：模板更新机制选型 copier vs cruft vs 定案延续手工期。证据对比：cruft 四机制全验证但维护停滞；copier 主流转但本地文件保护未验证（完整版 §7/探针笔记 §7） | Phase 0 · 步骤 5 | **硬触发器（先到为准）**：第二个数据仓需要继承模板时 / 2027-01——防止僵尸决策 |
| C1 | 🧪 验证挂起（Phase 0 未收口项 2/2）：ask 弹框本体从未被见证。**关闭路径已明确（2 分钟）**：新终端裸起 `claude`（bypass 是运行时开关，新进程默认会弹）→ 让它跑 `hostname` → 弹框=C1 关闭；仍不弹=实锤 harness 行为，转 /feedback 归档并显式记录"ask 控制不可依赖"的风险接受 | Phase 0 · 步骤 8 | 等你跑那 2 分钟 |

### Phase 1 · 伞形仓 GitHub 化（架构重定义后 = 单主机；双 host 议题随 D2 转为数据仓逐仓能力）

| # | 事项 | 归属 | 触发 / 阻塞 |
|:---:|------|------|------|
| **R1** | 🌍 现实动作：向 GitLab 管理员问三件——①~~Maintainer 角色~~（✅ 已获）② runner 情况 ③ mirror 策略了解。**架构重定义后本项主要服务 E4/E5（CI 探针与 bump）与 da 组数据仓**，与伞形无关 | Phase 1 · 步骤 11（转 E4 前置） | ②③ 待补问 |
| **D7** | 🆕 输入源 bump 机制落位（D2 架构的连锁产物）：原"GitLab 侧 Renovate bump PR"随伞形不入 GitLab 失去宿主。候选：① 内网 self-hosted runner 挂 GitHub 仓（该机需出网 github.com）② 本地脚本化 bump（`submodule update --remote` + commit + 本地跑影响分析 hooks）——影响分析可先由本地 Stop/post-bump 脚本承担 | Phase 2 · 步骤 14 | 待 E4 的 runner 情报后拍 |
| ~~E1~~ | ✅ **完成（2026-11-04）**：伞形仓首推 GitHub（66edfdd→528299b master）+ ci-baseline 首跑**两 job 全绿**（validate-configs：配置自检/脱敏守卫/负面清单守卫；secret-scan：Gitleaks 全历史）→ 模板 🔮→✅ 转正 | Phase 1 · 步骤 12 | 已关闭 |
| E2 | CODEOWNERS 落地（覆盖 AGENTS.md 审查面六类路径） | Phase 1 · 步骤 12 + Phase 0 步骤 7 | 🔓 E1 已完成，**现在可做**（单人仓价值有限，可低优先） |
| C2 | 靶子仓清理（ZenRay/test、da/dual-push-test，网页删；模板/方法论均已内联留底） | 收尾 | 随时，可选 |

### Phase 2 · 团队协作与自动化

| # | 事项 | 归属 | 触发 / 阻塞 |
|:---:|------|------|------|
| E4 | GitLab CI 探针（runner 三连问；照[探针笔记 §10](./LearningNote/devops/2026-11-03-GitHub-Actions-CI可行性探针方法论.md)移植指南跑，无需新设计） | Phase 2 · 步骤 14 | 等 R1② runner 答案 |
| E5 | bump 自动化首跑（形态依 **D7** 拍板后：Renovate-on-self-hosted 或本地脚本）；IM 通知管道 PoC（证据缺口，推断级骨架） | Phase 2 · 步骤 14 | 等 D7 + E4 |
| **D4** | IM 通知目标选型（飞书/钉钉/Slack webhook） | Phase 2 · 步骤 14 | 随 E5 |
| E6 | 凭据调查：成员账号对输入源仓库（`.gitmodules` 全集）的原生读权限（若可读→独立只读凭据方案作废一半） | Phase 2 · 步骤 15 | 随时可查 |
| **D5** | secrets 工具选型（sops+age 能力面已验证、完整工作流未 PoC；1Password/doppler 未对比） | Phase 2 · 步骤 15 | 触发=E6 结论为"需要" |
| E7 | onboarding.sh 新人实跑（脚本已落地自测 exit 0；真人首跑属实战检验） | Phase 0 · 步骤 6 产物 | 首个新成员加入时 |

### MCP PoC · 初版收口（研究记录：BackDocs/mcp-research/，读取需负责人确认）

| # | 事项 | 归属 | 触发 / 阻塞 |
|:---:|------|------|------|
| E10 | 🧪 收口验证（~5 分钟）：`~/.zshrc` 补 `eval "$(direnv hook zsh)"` → 新终端仓库根裸起 `claude` → `/mcp` 两 server connected + **逐个交互批准**（制度禁预批）→ 各试调一个只读工具（MySQL `SELECT 1` / Nacos 读配置列表）。根因已定位：`.mcp.json` `${VAR}` 展开读进程启动环境，hook 前言只到 Bash（本会话：Bash 变量齐全、server INVALID_CONFIG）。**与 C1 同一个新终端可连测** | MCP PoC | 等你重启验证 |
| **D8** | ⚖️ MySQL MCP 为 `http://`（内网 ack-test）：Bearer token 内网明文传输，与研究 Must#5「远程 HTTP 必须 TLS」冲突。二选一：风险接受并记录（测试环境+内网）/ 向管理员要 https 端点 | MCP PoC | E10 过后拍 |

### Phase 3/4 · 数据开发与 Data Agent 基建

| # | 事项 | 归属 | 触发 / 阻塞 |
|:---:|------|------|------|
| E8 | `etl-warehouse` 从模板实例化；dbt Slim CI + Data Contract 门禁上内网 CI | Phase 3 · 步骤 16/17 | 等 E4（CI 落位内网侧） |
| **D6** | Node 工具选型 PoC：Volta（shim 免 hook，⚠️ 未验证）vs fnm vs 延续 `.nvmrc`（PoC 清单在伞形笔记 §7；Volta 安装需人工执行——`Bash(curl *)` deny 拦截属有意设计） | Phase 4 前置（首个 Node/前端 repo 的技术栈决策） | 首个 Node repo 立项时 |
| E9 | Data Agent 基建蓝图启动（托管 MCP server 接入、evals-as-code 进 CI、私有 marketplace 评估） | Phase 4 · 步骤 18-20 | 等 Phase 3 起步 |

### 已关闭记录

- ~~TODO-1｜GitHub CI 可行性~~ ✅ 探针双 job 全绿（2026-11-03）：Actions private 可用；hosted 不可达内网——CI 落位表见[探针方法论](./LearningNote/devops/2026-11-03-GitHub-Actions-CI可行性探针方法论.md)
- ~~TODO-4｜交互式自测~~ ✅ 5/6 通过 + ask 未弹框根因=bypass 模式（制度：本 workspace 禁 bypass），详见伞形笔记 v1.5。⚠️ v1.7 勘误：ask 弹框本体至今未证实，复测转入 C1。
- ~~E3｜meta 登记 nl2sql-backend~~ ✅（5314783，2026-11-03）：`.meta` 建清单 + 队友两步同步**真实首演成功**（clone 伞形→update→实拉 da 组 d83bb17）
- ~~D2｜伞形仓 GitLab 归属~~ ✅ 已拍（2026-11-03）：**不放 GitLab**——伞形=个人 GitHub 单主；数据仓群归 `da` 组
- ~~D3｜镜像范围~~ ✅ 随 D2 转化：伞形无镜像问题；"数据仓→个人副本"变逐仓再议（方案 A 能力已验证备用）
- ~~URL 脱敏~~ ✅（8b23dc0，v1.8）：仓内全别名（upstream:/upstream-user:/darepo:），真实域名仅存本机 ~/.gitconfig；onboarding 含映射检查
