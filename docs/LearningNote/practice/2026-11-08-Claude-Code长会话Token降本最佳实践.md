---
title: Claude Code 长会话 Token 降本最佳实践
create_time: 2026-11-08 09:59:42
update_time: 2026-11-08 17:40:20
category: practice
subcategory: workflow
documentType: best-practice
purpose: explanation
status: active
project: AIDataEngineering
tags: [Claude Code, Token优化, subagent, 上下文管理, 审查流程, 成本控制]
project-description: AI 数据工程项目集 - code-parser Phase 2 长会话的 Agent 协作与 Token 成本优化实践
snapshot_date: 2026-11-08
snapshot_env: Claude Code background session，Opus 5 主会话，code-parser Phase 2
snapshot_source: 当前会话的 subagent usage 通知、任务报告、审查记录与真实数据重跑记录
---

# Claude Code 长会话 Token 降本最佳实践

> 这篇笔记记录 code-parser Phase 2 长会话的真实消耗模式。目标不是单纯选择更便宜的模型，而是在保留 TDD、真实数据验证和独立审查的前提下，减少重复上下文、无效循环和过度验证。

## 版本历史

| 版本 | 时间 | 变更摘要 |
|---|---|---|
| 1.0 | 2026-11-08 09:59 | 基于 T9 前半程的 subagent usage、审查循环和重建记录整理降本框架 |
| 1.1 | 2026-11-08 17:40 | 补充 T9 最终收口实战：主控内联、分层门禁、单次双服务重建与精确断言效果 |

## 验证状态总表

| 结论 | 验证方式 | 绑定条件 | 失效风险 | 复核动作 |
|---|---|---|---|---|
| 已知四次 subagent 小计 332,070 tokens | ✅ 会话 usage 通知逐项相加 | 仅涵盖通知中明确报告的四次调用 | 不是会话总量或账单 Token | 新会话重新按 usage 通知统计，不跨口径比较 |
| T9 收口可不新增 subagent | ✅ 本次主控内联执行记录 | 缺陷范围已收敛、已有 review findings 和回归测试 | 新任务或高风险架构变化仍可能需要独立 reviewer | 先判断任务是否仍是确定性收口 |
| 分层门禁可避免失败状态触发昂贵重建 | ✅ 4 → 64 → 257 测试全部通过后才重建 | 测试能够覆盖本轮产品代码变化 | fixture 漏掉真实源码形态 | 最终仍保留一次 fresh 真实数据门禁 |
| 验证器改动不要求重建产品数据库 | ✅ 增加 Citic 精确断言后只重跑查询脚本 | 产品代码和数据库内容未变化 | 验证器可能查询错误身份 | symbol ID/FQN 分离并使用全等查询 |
| 本轮优化节省了具体多少 Token | ⚠️ 未量化 | 没有优化阶段完整 usage 总量及可比基线 | 用流程次数冒充 Token 数会误导 | 后续任务记录主会话与 subagent 的同口径 usage |

> 修改规则：更新量化结论前必须核对本表的口径和绑定条件；无法同口径测量时只报告“减少了哪些重复工作”，不虚构节省比例。本文是流程与案例笔记，执行状态以 code-parser 的 Phase 2 ledger 和测试报告为准。

## 一、问题现象与本次会话证据

T9 枚举语义收口经历了实现、审查、重审和修复。仅工具通知中明确报告的四次 subagent 消耗如下：

| 工作 | `subagent_tokens` |
|---|---:|
| 枚举语义实现与真实数据调查 | 160,505 |
| 第一次 reviewer（没有产出有效审查结论） | 58,641 |
| reviewer 重新审查 | 62,123 |
| Fix Round 1 | 50,801 |
| **已知小计** | **332,070** |

这个小计有严格边界：

- 只统计通知中明确给出的四次 `subagent_tokens`；
- 不包含主会话 Token；
- 不包含 T1–T9 更早的实现者和 reviewer；
- 不包含压缩摘要、工具结果、缓存读写等其他口径；
- 不是账单金额，也不能直接等同于 API 的最终计费 Token。

因此，332,070 的意义不是“本会话总成本”，而是证明了一个事实：**复杂任务中，subagent 的重复上下文建立和审查循环可以远高于用户最终看到的回答长度。**

本轮还有三个放大器：

1. 实现者生成了长报告，并读取真实 Java 源码、测试、SQLite 数据和双服务运行结果；
2. reviewer 同时消费 brief、报告、完整 diff 和历史约束，其中存在重复信息；
3. casaba 与 demeter-order-service 被多次完整重建，曾产生约 188 KB 和 218 KB 的日志输出。

## 二、Token 消耗由什么构成

### 2.1 长上下文的复利效应

一条新消息本身可能很短，但模型还需要处理当前可见上下文，包括：

- 项目级 `AGENTS.md` 与安全约束；
- spec、plan、progress ledger；
- task brief、实现报告、review findings；
- 文件读取结果、diff 和测试输出；
- 压缩后的历史摘要。

上下文越长，后续每个决策回合的输入越重。Prompt caching 可以降低部分重复前缀的实际费用和延迟，但不能把新增内容、变化的后缀或新 subagent 的上下文变成零成本。

### 2.2 Subagent 是新的执行席位

Fresh subagent 不继承主会话的理解。它必须重新读取任务约束和代码。它的优势是隔离与独立判断，代价是重新建立上下文。

Resume subagent 也不是永远更省。恢复同一 agent 可以保留任务理解，但当其上下文已经很大，或者它连续受错误结论锚定时，每轮恢复会继续携带历史负担。本项目 ledger 已记录同一实现者多轮报告失实的案例，说明“永远 resume”既可能贵，也可能降低判断质量。

### 2.3 报告、日志和 diff 的重复

同一事实如果同时存在于以下位置，会被多次读取：

- progress ledger；
- task report；
- annotation backlog；
- review package；
- 用户汇报。

完整日志也有类似问题。解析器的数百 KB warning 对最终裁决的价值通常低于一张汇总表，但会占据大量上下文。

### 2.4 反复验证同一代码状态

高质量验证是必要成本，重复验证同一状态则是浪费。典型浪费包括：

- 只改 Markdown 后重跑完整 pytest；
- 每个小修复都重建两个真实服务数据库；
- reviewer 没有产出有效结论后原样重新派发；
- focused test、模块测试、全量测试在没有代码变化时重复执行。

### 2.5 模型选择会影响单价，也会影响回合数

便宜模型不一定带来更低总成本。复杂任务如果需要更多回合、更长解释或多次返工，总成本可能反而上升。模型选择应同时看：

- 单次 Token 成本；
- 完成任务需要的回合数；
- 错误或返工概率；
- 任务是否需要跨文件判断和架构推理。

## 三、核心原则

### 原则 1：先优化流程，再降低模型能力

最优先消除的是无效 reviewer、重复报告、过量日志和重复全量重跑。这些通常不牺牲质量。直接把所有工作降到更便宜的模型，属于有质量权衡的后手。

### 原则 2：上下文只传“完成当前决策所需的信息”

任务 brief 应包含需求、接口和边界，不复制整个项目历史。完整证据放入文件，主会话和 subagent 通过路径读取。返回主会话时只给状态、测试摘要、报告路径和 concerns。

### 原则 3：验证深度与风险匹配

验证不能取消，但应分层：

- 开发循环：focused tests；
- 模块完成：模块测试；
- 代码状态收口：完整测试；
- 真实数据门禁：任务末尾完整重跑；
- 文档或空格修改：`git diff --check`，不重跑无关测试。

### 原则 4：独立审查用在高价值边界

独立 reviewer 对跨层数据流、增量一致性、SQL 持久化和启发式置信度很有价值。机械改名、格式修正和单一断言不一定需要最强 reviewer。审查席位应与 diff 的风险相匹配。

### 原则 5：用阶段边界切断历史负担

Compaction 能缓解上下文窗口压力，但不会退还已经消耗的 Token。稳定阶段完成后开启新会话，并让新会话读取少量权威文件，通常比继续携带全部历史更经济。

## 四、判断框架：风险 × 上下文 × 验证

### 4.1 先判断任务风险

| 任务类型 | 示例 | 推荐执行方式 |
|---|---|---|
| 机械型 | 单文件字段改名、明确的一行修复 | 主代理或低成本模型，focused test |
| 常规集成型 | 多文件数据传播、明确接口实现 | Sonnet 级实现者，任务末尾完整测试 |
| 高判断型 | 架构设计、复杂根因、启发式准确性 | Opus 级模型，独立审查 |
| 高风险门禁型 | 增量一致性、跨服务关联、持久化语义 | 实现者 + 独立 reviewer + 真实数据验证 |

这里的模型名称是 2026-11-08 的会话快照。未来模型能力或价格变化时，应按“机械 / 标准 / 高判断”角色重新映射，而不是永久绑定具体名称。

### 4.2 再判断上下文策略

| 当前情况 | 选择 |
|---|---|
| 同一任务的第 1–2 次小修，原 agent 理解可靠 | Resume，避免重复建立上下文 |
| 原 agent 已有超长上下文或连续错误锚定 | 换 fresh agent，只给 findings 和必要文件 |
| 新任务与旧任务边界清晰 | 新会话或 fresh agent |
| 多个修改共享同一数据流和文件 | 合并成一个任务，避免重复读取 |
| 多个任务真正独立且用户明确需要并行 | 并行，但不要让多个实现者写同一工作区 |

### 4.3 最后决定验证深度

```text
改动一小步
  → focused RED/GREEN
  → 若仍在同一代码状态，继续 focused test
  → 代码实现完成后跑一次完整 suite
  → reviewer 有代码修复时，再跑一次完整 suite
  → 最终只做一次真实双服务门禁
```

关键不是机械限制次数，而是**一个新的、可能影响行为的代码状态需要验证；纯文档状态不需要重复验证代码。**

## 五、推荐做法

### 5.1 每个稳定阶段开启新会话

T9 收口后，T11/T12 应在新会话开始。新会话只读取：

```text
AGENTS.md
Phase 2 spec
Phase 2 plan
progress.md
当前任务 brief
```

不要复制此前几十轮对话，也不要要求新会话重新总结 T1–T9。

### 5.2 保留一个权威进度账本

`progress.md` 只记录：

- 任务状态；
- commit 或工作树边界；
- 已裁决的设计决策；
- 未解决 concerns；
- 下一步入口。

详细测试输出留在 task report，业务标注缺口留在 annotation backlog。三者不要重复整段内容。

### 5.3 限制 subagent 输入和返回

推荐 contract：

```text
输入：brief path + report path + 必要接口说明 + 只读/禁止事项
返回：status + changed files + one-line tests + report path + concerns
```

详细证据写入报告文件，不把 500 行报告全文返回主会话。报告建议控制在 100–150 行；大 SQL 结果保存为附属文件，只展示聚合指标和少量样本。

### 5.4 一名实现者 + 一次有效 reviewer

常规任务默认：

```text
实现者
→ 主代理检查 diff 与测试
→ 独立 reviewer 一次
→ 仅在有 Critical/Important finding 时进入 fix round
```

reviewer 没有产出有效结论时，先修正 prompt、diff package 或输入路径，不要原样重跑。Scoped re-review 只看修复 diff 和原 findings，不重读整个任务历史。

### 5.5 测试分层

开发过程中：

```bash
pytest tests/extraction/test_target.py -q
```

模块完成时：

```bash
pytest tests/extraction/ tests/storage/ -q
```

代码状态收口时：

```bash
pytest tests/ -q
ruff check src tests
ruff format --check src tests
git diff --check
```

纯文档修改只需要相关文档校验和 `git diff --check`。如果 reviewer 修了生产代码，需要对新代码状态重新跑完整测试。

### 5.6 真实数据重跑只放在门禁点

开发阶段使用真实源码形态裁剪出的 fixture。任务完成后再执行 casaba 和 demeter-order-service 的 fresh rebuild。

日志使用 `ERROR` 或重定向到文件，主会话只读取：

```text
files / symbols / relationships
tables / columns / enum fields
coverage / conflicts / pending
关键样本 LIMIT 5–10
```

只有指标异常时才按错误类型读取日志片段。

### 5.7 分层选择模型

推荐基线：

| 角色 | 模型策略 |
|---|---|
| 明确、机械、单文件实现 | Haiku 或同级低成本模型 |
| 常规多文件实现 | Sonnet 或同级标准模型 |
| 复杂根因、架构裁决 | Opus 或同级高能力模型 |
| 最终高风险审查 | 高能力模型 |
| 小范围 fix re-review | 低到标准模型 |

在没有评测数据时，不要把模型降级当作“免费优化”。先记录返工次数和通过率，再决定是否保留该模型分层。

### 5.8 控制状态沟通频率

长任务依赖完成通知，不用频繁轮询。只在以下节点向用户报告：

- 根因已经证实；
- 出现需要裁决的阻塞；
- reviewer 找到关键问题；
- 最终验证完成。

中间状态写入 ledger，避免每次状态询问都让主会话重新处理长上下文。

### 5.9 T9 最终收口实战：四层门禁与单次重建

T9 已完成过实现、Fix Round 1 和独立 review，剩余工作是一个已定位的身份契约缺陷及最终验证。此时再启动 fresh implementer/reviewer 会重复读取数百行 brief、报告和 diff，因此采用主控内联：**不新增 subagent，只执行已经明确的修复与门禁。**

执行链路如下：

```text
验证器先分离 symbol ID 与 FQN
  → C2 focused tests：4 passed
  → enum/DDL 模块：64 passed
  → 全量 suite：257 passed
  → Ruff + diff check
  → casaba / demeter 各一次 fresh rebuild
  → 一份精确查询脚本完成全部数据库断言
  → 只在产品代码再变化时重新 rebuild
```

关键控制点：

1. **先便宜后昂贵。** C2 的 4 个测试失败时立即停止，不进入 64 个模块测试、257 个全量测试或真实服务重建。
2. **产品状态与验证器状态分离。** 增加 `CiticTransferRequestStatus` 精确断言只改变查询脚本，因此只重跑查询，不重新解析两个服务。
3. **身份字段分离。** `symbols.symbol_id` 使用 `java:{fqn}`，`column_metadata.enum_class` 使用裸 FQN。验证器分别持有两个键，避免把查询工具自身的错误误判为产品缺陷。
4. **完整输出落盘。** 双服务 rebuild 日志和完整 JSON 保存在临时证据文件中，主会话只读取 60 余行重建摘要和断言汇总。
5. **只做一次真实重建。** 代码测试、lint 和 diff 全绿后，才生成两个全新数据库；旧数据库不覆盖，防止新旧证据混淆。

本轮可验证效果：

| 项目 | 结果 |
|---|---|
| 新增 subagent | 0 |
| focused / 模块 / 全量测试 | 4 / 64 / 257 passed |
| fresh rebuild | casaba 1 次、demeter-order-service 1 次 |
| 重复 rebuild | 0 |
| casaba 解析 | 2381/2381 files，0 failure |
| demeter 解析 | 2129/2129 files，0 failure |
| 四重点枚举精确关联数 | 32 / 29 / 6 / 4 |
| `enum_class` 错存 `java:` 前缀 | 0 |
| 分类不一致、数字 label、malformed C2 | 均为 0 |

质量没有因降本而缩减：分层门禁额外发现并修复了 C2 将 symbol ID 写入 FQN 列的问题；`PaymentStatusEnum` 从混合身份下只能精确查到 3 个直接关联字段，修复后统一 FQN 可查到全部 4 个。与此同时，重复 business code 身份、C2 的 `confidence=0.5`、详细 javadoc 优先规则和 submodule 只读边界都由 fresh 数据断言覆盖。

本次不能给出“节省了 N% Token”的数字，因为优化阶段没有完整、同口径的主会话 usage 基线。能够严谨报告的是：**没有新增执行席位，没有重复真实重建，没有把大日志灌入上下文，也没有因验证脚本增强而重跑产品流水线。**

## 六、反例与为什么昂贵

### 反例 1：所有角色都用最强模型

```text
Opus 实现 → Opus 审查 → Opus 修复 → Opus 再审查
```

问题：机械步骤也按最高单价执行，而且每个角色都重新读取上下文。

改进：标准模型实现，高能力模型只承担复杂诊断和最终高风险审查。

### 反例 2：每个小修复都双服务重跑

问题：解析、SQLite 落库和日志生成重复发生，输出又进入会话。

改进：fixture 钉死行为，最终门禁再 fresh rebuild。只有真实数据暴露 fixture 未覆盖的形态时，才提前重跑。

### 反例 3：报告复制源码、diff 和全部 SQL 行

问题：同一事实存在三份，主会话和 reviewer 都要重复读取。

改进：源码由 diff 表达；报告只写证据索引、命令、指标、少量样本和 concerns。

### 反例 4：Compaction 等于成本清零

问题：Compaction 只是把早期历史变成摘要，已经发生的消耗不会消失，摘要和后续内容仍需处理。

改进：在阶段边界创建新会话，用权威文件恢复状态。

### 反例 5：同一 agent 无限 resume

问题：超长上下文继续膨胀，错误结论也可能成为锚点。

改进：同一任务早期小修可以 resume；连续失实、上下文过大或修复轮较深时，换 fresh agent，并只交付原 findings 与局部 diff。

### 反例 6：文档改动后重跑全部代码测试

问题：没有产生新的代码状态，却重复支付验证成本。

改进：文档走文档校验；生产代码变化才触发代码 suite。

## 七、T11/T12 可复用执行模板

### 7.1 会话启动

```text
目标：仅执行 T11/T12，不重做 T1–T9。
权威输入：AGENTS.md、spec、plan、progress.md、当前 brief。
边界：submodules 只读；不 commit/push；真实结果必须提供人工样本。
```

### 7.2 T11 字段操作提取

```text
1. Sonnet 级实现者读取 T11 brief
2. 使用真实源码形态 fixture 做 RED/GREEN
3. focused tests
4. 完成实现后一次 full suite
5. 一次 casaba fresh rebuild 与 LIMIT 10 样本
6. 一次独立 reviewer
7. 有 Critical/Important 才进入 fix round
```

### 7.3 T12 状态机提取

```text
1. 新任务、fresh 实现者
2. 复用 T11 已稳定接口，不复制 T11 历史报告
3. 状态与转换 fixture RED/GREEN
4. 完成后一次 full suite
5. 一次 casaba fresh rebuild
6. 一次独立 reviewer
```

### 7.4 联合门禁

T11/T12 都完成后再执行：

- 完整 pytest；
- Ruff；
- `git diff --check`；
- casaba + demeter-order-service 双服务门禁；
- 一次跨任务最终审查。

如果任务级 reviewer 已覆盖所有代码状态，联合门禁仍用于证明组合后的最终分支，而不是重复每个任务的全部调查。

## 八、验证方法与节省效果观察表

降本措施不能只凭感觉判断。每个任务记录以下最小指标：

| 指标 | 记录方式 |
|---|---|
| subagent 数量 | implementer / reviewer / fix reviewer 分开统计 |
| `subagent_tokens` | 取任务通知中的 usage；缺失时标记未知 |
| fix round 数量 | 0、1、2… |
| full suite 次数 | 只统计完整测试 |
| 真实服务 rebuild 次数 | 按服务和数据库记录 |
| 无效运行 | 无产出 reviewer、重复命令、错误输入导致的重跑 |
| 质量结果 | reviewer Critical/Important 数、最终门禁结果 |

推荐比较两个相似任务：

```text
基线任务：总 subagent_tokens / 交付质量 / 返工轮数
优化任务：总 subagent_tokens / 交付质量 / 返工轮数
```

只有在质量门禁相当时，Token 下降才是有效优化。不能通过减少必要测试、隐藏 concerns 或降低真实数据覆盖来制造“节省”。

## 九、执行前后检查清单

### 执行前

- [ ] 任务是否值得使用 subagent？
- [ ] brief 是否只包含当前任务所需信息？
- [ ] 是否明确了禁止事项和只读边界？
- [ ] 是否按任务风险选择模型？
- [ ] 是否定义 focused test、完整测试和真实数据门禁？
- [ ] 是否设置停止条件，避免无限 fix loop？

### 执行中

- [ ] 详细结果是否写文件而不是贴回主会话？
- [ ] 是否只在代码状态变化后重跑完整测试？
- [ ] 是否先用 fixture，再做真实全量重跑？
- [ ] 日志是否降噪或重定向？
- [ ] agent 连续失实或上下文过大时，是否停止无限 resume？

### 执行后

- [ ] 是否记录 subagent Token、轮数和重跑次数？
- [ ] 是否保留了独立质量门禁？
- [ ] 是否把最终状态写入权威 ledger？
- [ ] 是否删除或避免复制临时长报告？
- [ ] 稳定阶段结束后，是否应开启新会话？

## 十、结论

长会话 Token 消耗过快，通常不是某一条回答太长，而是以下乘法效应：

```text
长上下文 × 多执行席位 × 多轮修复 × 重复验证 × 大型工具输出
```

最优先的优化不是取消审查或测试，而是：

1. 在稳定阶段切换新会话；
2. 缩小 subagent 输入与返回；
3. 让模型能力匹配任务风险；
4. focused test 驱动开发，完整 suite 和真实重跑放在门禁点；
5. 对无效 reviewer、重复日志和深度 resume 及时止损。

这样可以保留真实数据抽样、TDD 和独立审查带来的质量，同时显著减少不产生新证据的 Token 消耗。
