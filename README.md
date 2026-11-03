# AIDataEngineering

数据建设项目集伞形 workspace：8 个线上业务代码仓库（只读输入源，git submodules）+ 数据建设 repo 群（meta 清单，`projects/`）+ Data Agent 基建（规划中）。

- 团队/Agent 约定：[AGENTS.md](./AGENTS.md)（单一事实源，Claude Code 经 CLAUDE.md 导入）
- 决策记录与研究证据：docs/LearningNote/（叙事层）· BackDocs/research/（证据层，读取需负责人确认）
- TODO 编号规则：**E**=执行项、**D**=待拍板决策、**C**=收尾/清理动作；每项标注所属 Phase 与完整版 §8 步骤号

## 状态速览

| 项 | 状态 |
|------|------|
| Phase 0（伞形定型/hooks 硬边界/direnv 环境/规范+模板+onboarding） | ✅ 全部落地（commits 1ae2a39…249682f），仅剩 D1/C1 两个可延项 |
| Phase 1（架构定案 v2.11：**伞形=GitHub 个人单主**，不上 GitLab；双 host 转为数据仓备选能力，方案 A 已验证） | 🔓 R1① 角色已获得；待 E1：GitHub 建空 private 仓给 URL 即推 |
| Phase 2 meta 清单 | ✅ **已激活**（E3 完成，commit 5314783）：`.meta` 登记 nl2sql-backend + 队友两步同步真实首演成功；与 .gitmodules 双清单并存 |
| GitHub CI | ✅ 探测定案（TODO-1）：Actions 可用 / hosted 不可达内网 → 落位表见探针笔记 |
| GitLab CI | ⏸️ 暂缓（E4，待 R1 + runner 情报；移植指南现成） |

## TODO 看板（按阶段分组）

### Phase 0 · 收尾（工作区内已清零，剩可延项）

| # | 事项 | 归属 | 触发 / 阻塞 |
|:---:|------|------|------|
| **D1** | 模板更新机制选型：copier vs cruft vs 继续手工期（证据对比：cruft 四机制全验证但维护停滞；copier 主流转但本地文件保护未验证——见完整版 §7/探针笔记 §7） | Phase 0 · 步骤 5（手工期已可用，本决策仅决定"转自动期"） | **可显式延后**：第二个 repo 需要同步模板时再拍 |
| C1 | ask 弹框本体复验——🔶 **v1.7 挂起**：本环境三连探针（push 三形态/受限读/hostname 对照）零弹框，"manual" 实为自动放行族，非配置问题 | Phase 0 · 步骤 8 | 待能在真默认模式弹框的会话复测；若新进程仍不问 → 属 harness 行为，转 /feedback |

### Phase 1 · 双 host 生产执行（唯一硬阻塞在现实世界）

| # | 事项 | 归属 | 触发 / 阻塞 |
|:---:|------|------|------|
| **R1** | 🌍 现实动作：向 GitLab 管理员问三件——① Maintainer 角色 ② runner 情况 ③ mirror 策略 | Phase 1 · 步骤 11 | 🔓 **① 已获得（2026-11-03）**；②③ 随 E4 补问 |
| ~~**D2**~~ | 伞形 repo GitLab 归属 | Phase 1 · 步骤 12 | ✅ **已拍（2026-11-03）：不放 GitLab**——伞形=个人 GitHub 单主；数据仓群归 `da` 组（Maintainer 已获） |
| ~~**D3**~~ | 镜像范围 | Phase 1 · 步骤 9 | ✅ 随 D2 转化：伞形无镜像问题；"数据仓→个人 GitHub 副本"变逐仓再议项（方法已验证） |
| **D7** | 🆕 输入源 bump 机制落位（D2 架构的连锁产物）：原"GitLab 侧 Renovate bump PR"随伞形不入 GitLab 失去宿主。候选：① 内网 self-hosted runner 挂 GitHub 仓（该机需出网 github.com）② 本地脚本化 bump（`submodule update --remote` + commit + 本地跑影响分析 hooks）——影响分析可先由本地 Stop/post-bump 脚本承担 | Phase 2 · 步骤 14 | 待 E4 的 runner 情报后拍 |
| E1 | 生产执行（简化为单主机）：**GitHub 建空 private repo**（建议名 `AIDataEngineering`；**不要**勾 README/gitignore 初始化）→ 给我 SSH 地址 → 我 `remote add` + 首推 + ci-baseline 冒烟（🔮→✅，Gitleaks+配置校验首跑） | Phase 1 · 步骤 12 | **只差你建库**（其余全就绪） |
| E2 | CODEOWNERS 落地（覆盖 AGENTS.md 审查面六类路径） | Phase 1 · 步骤 12 + Phase 0 步骤 7 | 等 E1（repo 上有远端才能建） |
| C2 | 靶子仓清理（ZenRay/test、da/dual-push-test，网页删；模板/方法论均已内联留底） | 收尾 | 随时，可选 |

### Phase 2 · 团队协作与自动化

| # | 事项 | 归属 | 触发 / 阻塞 |
|:---:|------|------|------|
| E3 | ~~meta 登记 nl2sql-backend~~ ✅ **已完成（5314783）**：`.meta` 建清单 + **队友两步同步真实首演成功**（clone 伞形→update→实拉 GitLab d83bb17） | Phase 2 · 步骤 13 | — |
| E4 | GitLab CI 探针（runner 三连问；照[探针笔记 §10](./LearningNote/devops/2026-11-03-GitHub-Actions-CI可行性探针方法论.md)移植指南跑，无需新设计） | Phase 2 · 步骤 14 | 等 R1 的 runner 答案 |
| E5 | bump 自动化首跑（形态依 **D7** 拍板后：Renovate-on-self-hosted 或本地脚本）；IM 通知管道 PoC（证据缺口，推断级骨架） | Phase 2 · 步骤 14 | 等 D7 + E4 |
| **D4** | IM 通知目标选型（飞书/钉钉/Slack webhook） | Phase 2 · 步骤 14 | 随 E5 |
| E6 | 凭据调查：成员账号对 8 输入源的原生读权限（若可读→独立只读凭据方案作废一半） | Phase 2 · 步骤 15 | 随时可查 |
| **D5** | secrets 工具选型（sops+age 能力面已验证、完整工作流未 PoC；1Password/doppler 未对比） | Phase 2 · 步骤 15 | 触发=E6 结论为"需要" |
| E7 | onboarding.sh 新人实跑（脚本已落地自测 exit 0；真人首跑属实战检验） | Phase 0 · 步骤 6 产物 | 首个新成员加入时 |

### Phase 3/4 · 数据开发与 Data Agent 基建

| # | 事项 | 归属 | 触发 / 阻塞 |
|:---:|------|------|------|
| E8 | `etl-warehouse` 从模板实例化；dbt Slim CI + Data Contract 门禁上内网 CI | Phase 3 · 步骤 16/17 | 等 E4（CI 落位内网侧） |
| **D6** | Node 工具选型 PoC：Volta（shim 免 hook，⚠️ 未验证）vs fnm vs 延续 `.nvmrc`（PoC 清单在伞形笔记 §7；Volta 安装需人工执行——`Bash(curl *)` deny 拦截属有意设计） | Phase 4 前置（首个 Node/前端 repo 的技术栈决策） | 首个 Node repo 立项时 |
| E9 | Data Agent 基建蓝图启动（托管 MCP server 接入、evals-as-code 进 CI、私有 marketplace 评估） | Phase 4 · 步骤 18-20 | 等 Phase 3 起步 |

### 已关闭记录

- ~~TODO-1｜GitHub CI 可行性~~ ✅ 探针双 job 全绿（2026-11-03）：Actions private 可用；hosted 不可达内网——CI 落位表见[探针方法论](./LearningNote/devops/2026-11-03-GitHub-Actions-CI可行性探针方法论.md)
- ~~TODO-4｜交互式自测~~ ✅ 5/6 通过 + ask 未弹框根因=bypass 模式（制度：本 workspace 禁 bypass），详见伞形笔记 v1.5。⚠️ **v1.7 勘误**：历史所有"弹框批准"表述经复核均无法与"模式自动放行"区分——ask 弹框本体至今未证实，复测转入 C1（挂起条件见 Phase 0 表）。
