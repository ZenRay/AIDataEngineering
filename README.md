# AIDataEngineering

数据建设项目集伞形 workspace：8 个线上业务代码仓库（只读输入源，git submodules）+ 数据建设 repo 群（meta 清单，`projects/`）+ Data Agent 基建（规划中）。

- 团队/Agent 约定：[AGENTS.md](./AGENTS.md)（单一事实源，Claude Code 经 CLAUDE.md 导入）
- 决策记录与研究证据：docs/LearningNote/（叙事层）· BackDocs/research/（证据层，读取需负责人确认）

## 状态速览

| 项 | 状态 |
|------|------|
| Phase 0（伞形定型/hooks 硬边界/direnv 环境路线） | ✅ 已落地（commit 1ae2a39…cc860d7） |
| Phase 1（GitLab 团队主 + GitHub 个人副本，多 push URL） | 📌 定案 + 机制已验证；生产执行待 GitLab Maintainer 角色 |
| Phase 2 meta 清单 | ✅ 前置三验已过（Node 24 / 嵌套路径 / 两步同步），待登记 nl2sql-backend |
| GitHub CI | 🔬 探针验证中（见 TODO-1） |
| GitLab CI | ⏸️ 暂缓（见 TODO-2） |

## TODO

- **TODO-1｜GitHub CI 可行性验证**（进行中，2026-11-03）：经 `ZenRay/test` 探针验证 ① private repo Actions 可用性与免费额度；② **托管 runner 不可达内网资源**（`git.biaoguoworks.com`）的架构约束——决定了 Renovate submodule bump / dbt CI 这类"需要内网仓库或数仓"的工作负载**不能**放 GitHub hosted runner，只能：GitLab CI（待 TODO-2 解锁）/ 内网 self-hosted runner 挂 GitHub（需出网到 github.com，待评估）/ 本地脚本化（过渡）。探针 job 语义：`intranet-unreachable-assert` 通过 = 约束成立。
- **TODO-2｜GitLab CI 暂缓项**（待两把钥匙：runner 可用性确认 + Maintainer 角色）：① Renovate bump PR 自动化（输入源 submodule 指针更新 → 触发影响分析 CI）；② IM webhook 通知管道（研究结论中的证据缺口，落地需 PoC）；③ runner 基建调研（组内现有项目如何跑 CI）。解锁后回填本表。
- **TODO-3｜凭据管理调查**：确认团队成员账号对 8 个输入源仓库的原生读权限（若有，独立只读凭据方案作废一半）；个人 GitHub 侧凭据已实测为 SSH 路线。
- **TODO-4｜交互式自测**（hooks 项）：新会话执行学习笔记 §6.4 清单（permissions 已实战验证；hooks 不热加载，需新会话复测 git push 弹框）。
