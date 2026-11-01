#!/usr/bin/env bash
# confirm-push.sh — PreToolUse (Bash) 对 git push 要求人工确认
# 输出 permissionDecision=ask JSON（第六轮已验证：ask 弹人工确认框并展示 reason）
# 已知局限（官方 best-effort）：命令解析无法覆盖全部形态（别名/包装脚本/间接调用），
#   前缀规则 "Bash(git push:*)" 同样拦不住 `git -C <dir> push` 等变体——
#   因此这里采用双 token 宽松匹配（命令同时含 git 与 push 词即 ask）：
#   ask 语义下过匹配只是多一次人工确认，漏匹配才是真风险（第三层由 AGENTS.md 纪律兜底）。
set -u

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null) || COMMAND=""

# 词边界用纯 bash ERE 实现（bash 正则不支持 \b）：token 前后须为非字母数字/_/- 或行首尾
if [[ "$COMMAND" =~ (^|[^[:alnum:]_-])git([^[:alnum:]_-]|$) && "$COMMAND" =~ (^|[^[:alnum:]_-])push([^[:alnum:]_-]|$) ]]; then
  cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"ask","permissionDecisionReason":"git push 是远端不可逆操作，按伞形仓库约定需要人工确认后再执行（双 host 启用后还需确认两侧均成功）"}}
JSON
fi
exit 0
