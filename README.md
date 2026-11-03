# AIDataEngineering

数据建设项目集伞形 workspace：8 个线上业务代码仓库（只读输入源，git submodules）+ 数据建设 repo 群（meta 清单，`projects/`）+ Data Agent 基建（规划中）。

- 团队/Agent 约定：[AGENTS.md](./AGENTS.md)（单一事实源，Claude Code 经 CLAUDE.md 导入）
- 决策记录与研究证据：docs/LearningNote/（叙事层）· BackDocs/research/（证据层，读取需负责人确认）

## 状态速览

| 项 | 状态 |
|------|------|
| Phase 0（伞形定型/hooks 硬边界/direnv 环境路线） | ✅ 已落地（commit 1ae2a39…cc860d7） |
| Phase 0 收尾三件（onboarding 脚本 / 子项目规范 / repo 模板内容） | ✅ 2026-11-03（`scripts/onboarding.sh`、`docs/子项目Agent配置规范.md`、`docs/repo-template/`）；仅剩 **copier/cruft 选型** 一个决策点 |
| Phase 1（GitLab 团队主 + GitHub 个人副本，多 push URL） | 📌 定案 + 机制已验证；生产执行待 GitLab Maintainer 角色 |
| Phase 2 meta 清单 | ✅ 前置三验已过（Node 24 / 嵌套路径 / 两步同步），待登记 nl2sql-backend |
| GitHub CI | ✅ **已定案**（2026-11-03 探针实测）：private repo Actions 可用；托管 runner **不可达内网**——内网依赖工作负载（Renovate bump / dbt CI）不能上 GitHub hosted（TODO-1 关闭） |
| GitLab CI | ⏸️ 暂缓（见 TODO-2）；长期备选 = 内网 self-hosted runner 挂 GitHub（该机需可出网 github.com，待评估） |

## TODO

- ~~**TODO-1｜GitHub CI 可行性验证**~~ ✅ **已关闭（2026-11-03，探针双 job 全绿）**：
  - **结论 1**：个人 GitHub 的 private repo Actions 默认可用（ubuntu-latest，免费额度内）。
  - **结论 2**：GitHub hosted runner **无法访问内网 GitLab**（探针 `intranet-unreachable-assert` 按设计通过）→ CI 工作负载落位定案：
    - **可放 GitHub Actions**：配置审查类（settings.json/AGENTS.md 校验、validate.py 笔记检查）、**Gitleaks 服务端扫描**（硬兜底）、docs 构建、不依赖内网数据的 evals 门禁
    - **不能放 GitHub hosted**：Renovate submodule bump（需拉内网上游）、dbt 连数仓 CI → 归 GitLab（TODO-2）或内网 self-hosted runner（远期，需该机出网 github.com）
  - 探针载体：`ZenRay/test` @ `5060997`；**模板与完整方法论（反向断言/判读矩阵/GitLab 移植指南）已内联归档**：[CI 探针方法论笔记](./LearningNote/devops/2026-11-03-GitHub-Actions-CI可行性探针方法论.md)——靶子仓删除不影响模板存续
- **TODO-2｜GitLab CI 暂缓项**（待两把钥匙：runner 可用性确认 + Maintainer 角色）：① Renovate bump PR 自动化（输入源 submodule 指针更新 → 触发影响分析 CI）；② IM webhook 通知管道（研究结论中的证据缺口，落地需 PoC）；③ runner 基建调研（组内现有项目如何跑 CI）。解锁后回填本表。
- **TODO-3｜凭据管理调查**：确认团队成员账号对 8 个输入源仓库的原生读权限（若有，独立只读凭据方案作废一半）；个人 GitHub 侧凭据已实测为 SSH 路线。
- ~~**TODO-4｜交互式自测**~~ ✅ **已完成（2026-11-03，笔记 v1.5）**：5/6 通过（含 direnv 双 hook 端到端实测、deny 全路径拦截实测）；push-ask 未弹框根因 = 会话处于 **bypass 模式**（官方语义：bypass 下 ask 自动放行、deny 仍强制——配置无缺陷）。**制度结论**：bypass 禁用场景 = onboarding 新人 / 未审查仓库 / 敏感 workspace；ask 弹框本体可在默认模式复验（可选尾差）。
