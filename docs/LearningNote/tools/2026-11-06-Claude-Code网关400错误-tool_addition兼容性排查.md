---
title: Claude Code 网关 400 错误根因排查：tool_addition 块兼容性故障
create_time: 2026-11-06 14:09:23
update_time: 2026-11-06 14:09:23
category: tools
subcategory: debugging
documentType: problem-solving
purpose: how-to
status: active
project: AIDataEngineering
tags: [Claude Code, Anthropic API, tool_addition, 网关兼容性, 阿里云百炼, 系统性排查, 会话取证]
project-description: AI 数据工程项目集 - Claude Code 经第三方 Anthropic 兼容网关使用时 400 错误的取证、根因与修复
# ── 扩展辅助字段（tool 组）──
tool_name: claude-code
tool_version: 2.1.319
tool_docs_url: https://code.claude.com/docs
---

# Claude Code 网关 400 错误根因排查：tool_addition 块兼容性故障

> **适用场景**：Claude Code 经第三方 Anthropic 兼容网关（阿里云百炼 token-plan、one-api/new-api 类 relay 等）使用时，会话突然所有消息报 `API Error: 400 Request body format invalid`，resume 无效、新开会话恢复。
>
> **前置条件**：了解 Claude Code 会话 JSONL 日志位置（`~/.claude/projects/<项目路径转义名>/<sessionId>.jsonl`）、基本 curl/python 请求能力。

---

## 0. 迭代须知

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-11-06 | 初版：完整取证闭环，根因字段级确证，修复开关实测有效 |

**修改规则**：
- 本文结论绑定 **Claude Code 2.1.318/2.1.319** 与 **阿里云百炼 token-plan 网关（2026-11-06 行为）**；任一侧升级后，先按「验证方法」章节复测再改结论
- 过时内容标注 "⚠️ 已过时（原验证条件：…）" 而非直接删除
- 每次修改同步 frontmatter `update_time` 与上表

**文档分工**：本文 = 问题→根因→解法→验证 的完整案例；通用配置约定见仓库 AGENTS.md；排查方法论可独立复用于其他网关兼容性故障。

---

## 1. 问题描述

**症状**（2026-11-06 实战）：

- 一个跨 4 天、多次 resume 的长会话（累积 ~947K tokens 上下文）在执行笔记保存任务中途，**每条消息都返回 `API Error: 400 Request body format invalid`**，间隔 20–50 秒重试全部失败
- **resume 该会话（含换供应商后）依旧全部 400**；新开 `/clear` 会话完全正常
- 故障发生前一步的任务产物"保存了一半"：文件已写盘，后续校验/索引步骤未执行（因为需要下一轮 API 往返）
- 报错窗口内夹杂一次 `403 Insufficient account balance`——**这是旧供应商余额耗尽的独立并发事件，与 400 不同因**（当时正在切换供应商），排查时注意区分，勿被带偏

**环境**：

- Claude Code 2.1.318/2.1.319，`ANTHROPIC_BASE_URL` 指向阿里云百炼 token-plan Anthropic 兼容端点（`token-plan.cn-beijing.maas.aliyuncs.com/apps/anthropic`），模型 `qwen3.8-max[1M]`/`qwen3.7-plus[1M]`
- `CLAUDE_CODE_MAX_CONTEXT_TOKENS=983616`（近 1M 才触发自动压缩）

---

## 2. 根因分析

**一句话结论（✅ 已验证，字段级确证）**：

> Claude Code 2.1.x 的 **inline tools 特性**（beta `inline-tools-2026-09-15` / `mid-conversation-tool-changes-2026-07-01`）在**会话压缩（auto-compact）后的上下文重建**中，向 messages 数组注入 `role: "system"` 消息，内含 **`tool_addition` 内容块**（宣告 `EnterWorktree` 等 deferred tool 的 `tool_definition`）。阿里云百炼网关（及本案旧供应商 relay）的 Anthropic 兼容层**不支持该块类型**，schema 校验直接拒绝：`400 {"code":"InvalidParameter","message":"Request body format invalid"}`——不进模型、秒级失败（181–616ms）。

**完整因果链**：

```
4 天长会话 → 上下文 947K 逼近上限(983,616)
  → 最后一笔写入(Write 工具结果入历史)触发紧急压缩
  → 压缩摘要调用(~950K input)成功 [顺带打穿旧供应商余额 → 独立的 403]
  → 压缩后重建上下文：deferred_tools_delta / agent_listing_delta / invoked_skills
    被渲染为 role:system + tool_addition 块（inline-tools beta 格式）
  → 网关校验拒绝该块类型 → 400
  → Claude Code 无状态重发架构：每条新消息重发完整历史（毒块常驻）→ 条条 400
  → resume 从会话状态重建 → 同样注入 tool_addition → 同样 400
  → 新会话无中途工具变更 → 无 tool_addition → 健康
```

**关键机制说明**：

1. **无状态重发**：Claude Code 每条消息把完整对话历史重新 POST 给网关。一旦某个请求体成分有毒，毒不会自愈——这解释了"任何消息都是 400"以及为何只有新开会话能解决
2. **`tool_addition` 是 2026 新 beta 块类型**，非 Anthropic API 传统标准块；第三方兼容网关普遍未实现。请求 beta 头中的 `inline-tools-2026-09-15`、`mid-conversation-tool-changes-2026-07-01` 是其标志
3. **`api-request-blob` 日志条目只是诊断快照，不是 resume 的重建源**——tool_addition 在请求组装时从会话工具状态**实时再生成**（证据：修改 JSONL 中 blob 后 resume 依旧 400；且请求链引用的 blob hash `c5d33e5a…` 在所有会话文件中根本不存在，组装器照样能构造出该消息）
4. 压缩点前后的**尺寸对比排除容量因素**：毒请求体仅 ~80K tokens，而同网关同期正常接受了 179K tokens 的请求——"小的被拒、大的通过"是**结构性拒绝**的典型指纹

---

## 3. 排查过程与取证方法论（可复用）

按 systematic-debugging「先取证后假设、假设必须可证伪」执行，全程排除法 + 对照实验：

| 步骤 | 手段 | 结果 |
|------|------|------|
| ① 读错误与时间线 | 会话 JSONL 中 `isApiErrorMessage` 条目 + `usage` 字段 | 锁定故障边界 = 压缩点（947K → 压缩 → 3 秒后首 400）；发现 403 为独立事件 |
| ② 尺寸假设 | 对比毒体组件大小 vs 正常会话 usage | **证伪**（毒体更小） |
| ③ 字段矩阵重放 T1–T7 | 微型合成请求逐个加 `context_management`/`output_config`/`thinking`/`metadata`/`cache_control`/beta头 | 全 200，**顶层字段全部排除** |
| ④ 结构矩阵重放 S1–S8 | 连续 user、孤儿 tool_result、空 text 块、多块 system/user | 全 200，**经典结构违规全部排除**（该网关出奇宽容） |
| ⑤ thinking 签名假设 V1–V5 | 空签名/缺签名/伪签名 thinking 块重放 | 全 200，**证伪** |
| ⑥ 请求体考古 | 发现 JSONL 中 `api-request-blob` 条目（内容寻址存储的 wire 消息原文）+ `api-request` 的 base/keep/tail 链 | 发现 7 条 `role:system` 且块构成为 `text+tool_addition` 的异常消息 |
| ⑦ 决定性重放 V6b | 从 blob 提取**真实 tool_addition 块**嵌入最小请求体 | **400，错误逐字符一致**（rid=`7bdc3126-cfe5-489b-870f-e40ca76d9a4a`）；对照 V6a（同消息去掉该块）→ 200 |
| ⑧ 开关考古 | `grep -a` 扫描 claude 二进制找 env 名 + 解析语义 | 发现 `CLAUDE_CODE_INLINE_TOOLS`（默认启用，env 可关） |
| ⑨ 终极验证 | `CLAUDE_CODE_INLINE_TOOLS=0 claude --resume <毒会话> -p …` | **exit=0，正常回复**——根因与解法双重确证 |

**方法论要点**：

- **会话 JSONL 是最重要的取证现场**：`usage`（上下文规模）、`isApiErrorMessage`（错误时间线）、`attachment`/`api-request`/`api-request-blob`（请求组装线索）都在里面
- **合成重放是网关兼容性排查的利器**：微型请求体（几十 tokens）逐变量测试，成本趋零、结论干净；注意**变量隔离**（本案曾意外引入模型变量：headless resume 默认用 `ANTHROPIC_MODEL` 而非会话模型，需 `--model` 对齐后重测）
- **被拒请求通常不计费**，重放实验可放心做；被接受的对照请求才有 token 成本
- **诊断手段要合规**：本案曾尝试本地 MITM 代理抓请求体，被工作区安全护栏（`ANTHROPIC_BASE_URL` 端点覆盖拦截规则）正确阻断——改走"blob 考古 + 合成重放"同样拿到确证，且零护栏冲突
- 凭据纪律：token 一律从环境变量读取（`os.environ`），不进命令行参数（防 `ps` 泄露）、不进日志

**核心重放脚本**（V6b，可直接复用）：

```python
# tool_addition 块兼容性探针：400=网关不支持该块；200=已支持（可考虑撤掉开关）
import json, os, urllib.request, urllib.error
BASE = os.environ["DIAG_BASE_URL"]           # 如 https://.../apps/anthropic
TOKEN = os.environ["ANTHROPIC_AUTH_TOKEN"]   # 从环境读取，勿硬编码
body = {
    "model": "qwen3.8-max", "max_tokens": 64, "stream": True,
    "messages": [
        {"role": "user", "content": "只回复数字 1"},
        {"role": "system", "content": [
            {"type": "text", "text": "工具变更"},
            {"type": "tool_addition", "tool": {"type": "tool_definition",
                "definition": {"name": "ProbeTool", "description": "probe",
                               "input_schema": {"type": "object", "properties": {}}}}}],
        },
        {"role": "user", "content": "只回复数字 1"}]}
req = urllib.request.Request(BASE.rstrip("/") + "/v1/messages?beta=true",
    data=json.dumps(body).encode(), method="POST",
    headers={"content-type": "application/json", "anthropic-version": "2023-06-01",
             "x-api-key": TOKEN,
             "anthropic-beta": "inline-tools-2026-09-15"})
try:
    with urllib.request.urlopen(req, timeout=60) as r:
        print("HTTP", r.status, "→ 网关已支持 tool_addition")
except urllib.error.HTTPError as e:
    print("HTTP", e.code, e.read(300).decode(errors="replace"), "→ 不支持，需保持开关关闭")
```

> 注：真实故障中的 `tool_addition` 块结构为 `{"type":"tool_addition","tool":{"type":"tool_definition","definition":{name,description,input_schema,…}}}`，取自会话 JSONL 的 `api-request-blob` 条目原文。

---

## 4. 解决方案

### 4.1 立即修复（✅ 已验证，2026-11-06）

`~/.claude/settings.json`（用户级、不入 git）的 `env` 段添加：

```json
{
  "env": {
    "CLAUDE_CODE_INLINE_TOOLS": "0"
  }
}
```

- 语义（二进制考古确认）：该特性默认开启（`CLAUDE_CODE_INLINE_TOOLS !== false`），env 显式赋值优先于特性灰度开关；`"0"` 与 `"false"` 均实测有效
- **生效条件：重启 Claude Code**（env 在进程启动时读取；已运行的会话不受益）
- 副作用评估：inline tools 只是"会话中途工具变更的增量通知"传输优化，关闭后回退为传统全量 tools 数组传输，功能无损、token 略增
- 实测效果：加开关后，原毒会话 `claude --resume` 直接恢复正常（exit=0）

### 4.2 预防纪律（网关环境通用）

1. **少让会话走到紧急压缩**：压缩后的上下文重建是 tool_addition 注入点。长任务勤 `/clear`；`CLAUDE_CODE_MAX_CONTEXT_TOKENS` 不必顶满 1M（压缩摘要调用本身一口吞 ~950K input tokens，按量计费下是单次巨额消费，还可能打穿 relay 余额——本案 403 的成因）
2. **🔮 推断级**：会话中途加载 deferred tools（ToolSearch）、中途接入/重连 MCP 同为工具集变更，理论上也是 tool_addition 触发源；开关关闭后无虞，未关开关的网关环境应避免
3. 跨多天的工作不要滚在一个会话里 resume，用笔记/交接文档续接上下文（本仓库 LearningNote 制度即是）

### 4.3 上报与追踪

- 向阿里云百炼反馈：Anthropic 兼容端点不支持 `tool_addition` 内容块（beta `inline-tools-2026-09-15`），错误信息 `InvalidParameter: Request body format invalid` 过于笼统（未指明字段）
- 证据 request_id：`7bdc3126-cfe5-489b-870f-e40ca76d9a4a`、`b07ec72e-66ce-4597-875d-065185516f37`（2026-11-06）
- 追踪 Claude Code 官方 changelog：若未来版本对非 Anthropic 端点自动降级（不发 tool_addition），可撤销开关

### 4.4 备选开关（未实测，⚠️）

- `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS`：更宽的实验特性总开关（二进制中存在，语义为"experimental betas are off"），会连带关闭其他 beta，不作首选
- `CLAUDE_CODE_DROP_UNAVAILABLE_DEFERRED_TOOL`：与 deferred tool 相关，语义未深挖

---

## 5. 验证方法

修复后（或网关/Claude Code 任一升级后）按序复测：

1. **开关生效检查**：新建会话执行一次会触发工具集变化的操作（或 resume 旧毒会话），确认无 400
2. **毒会话救援验证**：`CLAUDE_CODE_INLINE_TOOLS=0 claude --resume <原故障sessionId> --model <对齐模型> -p "只回复收到"` → 预期 exit=0 且正常回复
3. **网关支持度探针**：运行 §3 的重放脚本 → 400=仍需保持开关；200=网关已支持，可评估撤开关
4. **错误指纹识别**（免工具速判）：`400 Request body format invalid` + 秒级失败 + 发生在压缩/resume/工具集变更之后 + 新会话正常 → 优先怀疑本故障模式

---

## 6. 反例：被证伪的修复路径

| 无效方法 | 为什么无效 |
|----------|-----------|
| 编辑会话 JSONL 剔除 blob 中的 tool_addition（实测 ❌） | `api-request-blob` 只是请求诊断日志；resume 时 tool_addition 从会话工具状态**实时再生成**，改日志不改源头 |
| resume / 换模型 / 换供应商 | 毒在请求体组装侧，与模型（qwen3.7-plus 与 3.8-max 均拒）、供应商（两代网关均拒）无关 |
| 调低/调高 MAX_CONTEXT_TOKENS 当"修复" | 只影响触发概率（预防），不能修复已中毒的会话 |
| 归因"余额不足" | 403 是旧供应商独立事件；余额充足的新供应商对同一毒体照样 400 |

---

## 7. 验证状态总表

| 结论 | 验证方式 | 绑定版本/条件 | 失效风险 | 复核动作 |
|------|----------|----------------|----------|----------|
| tool_addition 块是 400 根因 | ✅ V6b 真实块重放精确复现错误（含错误码），对照去块 → 200 | CC 2.1.318/319 × 百炼 token-plan 2026-11-06 | 网关升级支持后失效（好事） | 跑 §3 探针脚本 |
| `CLAUDE_CODE_INLINE_TOOLS=0` 可关闭注入 | ✅ 毒会话 resume 实测恢复（"0"/"false" 均有效） | CC 2.1.319 | CC 大版本重构特性开关 | 二进制 grep 确认 env 名仍存在 |
| blob 手术不能救会话 | ✅ 实测剔除后 resume 依旧 400 | CC 2.1.319 | 低 | 无需 |
| 尺寸/顶层字段/经典结构违规/thinking 签名均非本案原因 | ✅ 20 个合成对照请求全 200 | 百炼 token-plan 2026-11-06 | 网关校验收紧时结论可能变化 | 重跑 T/S/V 矩阵 |
| 中途 ToolSearch/MCP 接入也触发 tool_addition | 🔮 机制推断（同属工具集变更路径），未实测 | CC 2.1.319 | 中 | 【待实测】关开关前后各做一次 ToolSearch 观察 |
| 403 为旧供应商余额事件 | ✅ 用户确认切换供应商背景 + 时间线吻合 | — | 无 | 无需 |
| `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` 可作备选 | ⚠️ 仅二进制字符串证据，未实测 | CC 2.1.319 | 中 | 【待实测】 |

---

## 8. 相关资源

- 会话取证现场：`~/.claude/projects/-home-ray-Documents-BiaoGuoRepo-AIDataEngineering/{c4823643,06509e0c}.jsonl`（故障时间线 2026-11-06 11:58–12:13 本地）
- 诊断脚本存档：`/tmp/cc-diag-proxy/replay_{matrix,struct,thinking,tooladd}.py`（⚠️ /tmp 重启即失；核心脚本已内联 §3，其余可按需重写）
- 关联笔记：[CODEOWNERS 配置与维护教程](../practice/2026-11-06-CODEOWNERS配置与维护教程.md)（本次故障中断的任务产物，已在健康会话中补完）
- Claude Code 设置文档：https://code.claude.com/docs

---

**最后更新**：2026-11-06
**维护者**：ZenRay（数据团队）
