# AIDataEngineering

数据建设项目集伞形 workspace：8 个线上业务代码仓库（只读输入源，git submodules）+ 数据建设 repo 群（meta 清单，`projects/`）+ Data Agent 基建（规划中）。

- 团队/Agent 约定：[AGENTS.md](./AGENTS.md)（单一事实源，Claude Code 经 CLAUDE.md 导入）
- 决策记录与研究证据：docs/LearningNote/（叙事层）· BackDocs/research/（证据层，读取需负责人确认）
- TODO 编号规则：**E**=执行项、**D**=待拍板决策、**C**=收尾/清理动作；每项标注所属 Phase 与完整版 §8 步骤号

## 状态速览

| 项 | 状态 |
|------|------|
| Phase 0（伞形定型/hooks 硬边界/direnv 环境/规范+模板+onboarding） | ✅ 全部落地（commits 1ae2a39…249682f），仅剩 D1/C1 两个可延项 |
| Phase 1（GitLab 团队主 + GitHub 个人副本，多 push URL 方案 A） | 📌 定案 + 机制已端到端验证；唯一阻塞 = 现实角色问题（R1） |
| Phase 2 meta 清单 | ✅ 前置三验已过，登记动作无硬依赖可提前（E3） |
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
| **R1** | 🌍 现实动作：向 GitLab 管理员一次问三件——① 伞形/数据 repo 目标组的 **Maintainer 角色** ② 组内 runner 情况 ③ mirror 策略了解 | Phase 1 · 步骤 11 | **全局钥匙**：解锁 E4/E5 + Phase 1 生产 |
| **D2** | 伞形 repo 在 GitLab 的归属组（建议独立子组如 `da/ai-data-eng`，权限边界干净） | Phase 1 · 步骤 12 | 随 R1 一并定 |
| **D3** | 镜像范围拍板（建议：起步**只镜像伞形 repo**；8 个业务输入源永不镜像=已定；数据 repo 逐个再议） | Phase 1 · 步骤 9 | 建议即拍 |
| E1 | 生产执行：GitLab 建库 → GitHub 建 private 副本 → 副本 owner 机器三条命令 → 首推对账（**一并完成**：GitLab 分支首推最后验证 + ci-baseline 冒烟 🔮→✅） | Phase 1 · 步骤 12 | 等 R1 |
| E2 | CODEOWNERS 落地（覆盖 AGENTS.md 审查面六类路径） | Phase 1 · 步骤 12 + Phase 0 步骤 7 | 等 E1（repo 上有远端才能建） |
| C2 | 靶子仓清理（ZenRay/test、da/dual-push-test，网页删；模板/方法论均已内联留底） | 收尾 | 随时，可选 |

### Phase 2 · 团队协作与自动化

| # | 事项 | 归属 | 触发 / 阻塞 |
|:---:|------|------|------|
| E3 | `meta project import projects/nl2sql-backend` 登记 + 本地模拟队友两步同步首跑 | Phase 2 · 步骤 13 | **无硬依赖，可提前于 Phase 1** |
| E4 | GitLab CI 探针（runner 三连问；照[探针笔记 §10](./LearningNote/devops/2026-11-03-GitHub-Actions-CI可行性探针方法论.md)移植指南跑，无需新设计） | Phase 2 · 步骤 14 | 等 R1 的 runner 答案 |
| E5 | Renovate bump PR 首跑（输入源指针更新→影响分析）；IM 通知管道 PoC（证据缺口，推断级骨架） | Phase 2 · 步骤 14 | 等 E4 |
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
