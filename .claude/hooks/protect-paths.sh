#!/usr/bin/env bash
# protect-paths.sh — PreToolUse (Edit|Write) 拦截写入保护路径
# 保护对象：submodules/（只读上游 submodule）、BackDocs/（个人存档长期受限区）
# 依据（第六轮已验证的官方机制）：
#   - hooks-guide "Block edits to protected files" 官方示例模式（stdin JSON + jq + exit 2）
#   - tool_input.file_path 总是预展开 ~ 与相对路径的绝对路径（无法用路径写法绕过）
#   - Windows/Git Bash 下路径为反斜杠，比较前必须归一化
#   - exit 2 = 阻断且 stderr 反馈给 Claude；exit 0 ≠ 批准（继续正常权限流程，deny 规则兜底）
set -u

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null) || FILE_PATH=""
[ -z "$FILE_PATH" ] && exit 0

# 反斜杠归一化（Windows / Git Bash）
FILE_PATH="${FILE_PATH//\\//}"
# 防御性回退：CLAUDE_PROJECT_DIR 未设置时退回 $PWD——避免 set -u 崩溃导致 exit 1
# （exit 1 属"非阻断错误"，保护会失效放行；宁可 fail-safe 继续匹配）
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$PWD}"
PROJECT_DIR="${PROJECT_DIR//\\//}"

# 前缀锚定匹配（比子串匹配精确，避免误伤名字含 submodules 的合法路径）
# 分层说明：BackDocs 非 archive 部分的「写」由 settings.json ask 规则逐次弹框确认，本 hook 不拦
# （hook 的 exit 2 先于权限检查——若在此拦截，ask 永远弹不出来）；此处只拦绝对禁改区。
if [[ "$FILE_PATH" == "$PROJECT_DIR/submodules/"* || "$FILE_PATH" == "$PROJECT_DIR/BackDocs/archive/"* ]]; then
  echo "Blocked: $FILE_PATH 命中绝对保护路径（submodules/ 为只读上游 submodule；BackDocs/archive/ 为绝对禁改区）。BackDocs 其他内容的修改走 settings.json 的 ask 逐次确认。" >&2
  exit 2
fi
exit 0
