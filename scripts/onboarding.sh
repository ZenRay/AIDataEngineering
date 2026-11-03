#!/usr/bin/env bash
# AIDataEngineering onboarding 脚本 —— 新成员 clone 后、首次启动 claude 前各跑一次
# 制度依据：《专项》§6.7（五问题：trust 单向门 / 仓库下发不了的配置 / fail-open 依赖 / 版本下限 / bootstrap 杂务）
# 铁律：本脚本不代替人做 trust——它完成"审查前置"，trust 由成员随后启动 claude 时亲手点击
set -uo pipefail
cd "$(git rev-parse --show-toplevel)" || exit 1
FAIL=0
ok()   { echo "  ✓ $1"; }
bad()  { echo "  ✗ $1"; FAIL=1; }
warn() { echo "  ! $1"; }

echo "== 1/7 工具链与版本 =="
command -v git >/dev/null && ok "git $(git --version | awk '{print $3}')" || bad "缺 git"
command -v jq  >/dev/null && ok "jq $(jq --version)" || bad "缺 jq —— hooks 脚本硬依赖，缺失时保护会静默失效（fail-open，笔记 §6.3 bug①）；安装：sudo apt install jq"
command -v direnv >/dev/null && ok "direnv $(direnv --version)" || bad "缺 direnv（环境方案 D 依赖）：参考 direnv.net 安装"
if command -v claude >/dev/null 2>&1; then
  V=$(claude --version 2>/dev/null | head -1 | awk '{print $1}')
  if [ "$(printf '%s\n1.0.111\n' "${V:-0}" | sort -V | head -1)" = "1.0.111" ]; then
    ok "Claude Code ${V}（≥1.0.111，CVE-2025-59536 修复下限）"
  else
    bad "Claude Code ${V} < 1.0.111：先升级（提交配置攻击面的修复版本下限）"
  fi
else
  warn "未检测到 claude CLI——仅做 repo 开发可忽略；使用 Agent 前先安装"
fi
command -v meta >/dev/null && ok "meta $(meta --version 2>/dev/null | head -1)" || warn "meta 未装（Phase 2 多仓 bootstrap 需要）：npm i -g meta"

echo "== 2/7 提交配置负面清单扫描 =="
for f in .claude/settings.json .mcp.json; do
  [ -f "$f" ] || continue
  if grep -Eq 'enableAllProjectMcpServers|enabledMcpjsonServers' "$f"; then
    bad "$f 含 MCP 预批键（负面清单禁止——MCP 审批必须每成员交互完成，CVE-2025-59536）"
  else ok "$f 无预批键"; fi
  if grep -q 'ANTHROPIC_BASE_URL' "$f"; then bad "$f 含 ANTHROPIC_BASE_URL 端点覆盖（禁止）"; fi
done

echo "== 3/7 人工配置审查（不可跳过）=="
echo "  trust 前需过目的文件："
for p in .claude/settings.json .claude/hooks/*.sh .claude/skills .mcp.json .codex/config.toml scripts/onboarding.sh; do
  [ -e "$p" ] && echo "    $p"
done
if [ "${1:-}" != "--reviewed" ]; then
  printf "  已完成人工审查？（输入 yes 继续——审查是人的判断，脚本不能代劳）> "
  read -r ans
  [ "$ans" = "yes" ] || { echo "  已中止：顺序必须是 clone → 审查 → trust。"; exit 1; }
fi

echo "== 4/7 仓库 bootstrap =="
git submodule update --init --recursive && ok "submodules 初始化完成" || bad "submodule init 失败（检查网络/SSH key 对 git.biaoguoworks.com 的可达性）"
if [ -f .meta ] && command -v meta >/dev/null; then
  meta git update && ok "meta 清单同步完成（注意：新清单要先 git pull，meta git update 不拉清单）" || warn "meta git update 失败"
else
  warn "尚无 .meta 或 meta 未装 —— Phase 2 首个数据 repo 登记后此步自动生效"
fi

echo "== 5/7 环境激活（方案 D：direnv）=="
while IFS= read -r e; do
  direnv allow "$(dirname "$e")" >/dev/null 2>&1 && ok "direnv allow $(dirname "$e")" || bad "direnv allow 失败：$(dirname "$e")"
done < <(find . -name .envrc -not -path './submodules/*' -not -path './docs/repo-template/*' -not -path './.git/*' 2>/dev/null)
if command -v direnv >/dev/null && ! grep -rq 'direnv hook' ~/.bashrc ~/.zshrc ~/.profile 2>/dev/null; then
  warn "shell rc 未见 direnv hook——交互终端需要：eval \"\$(direnv hook bash)\"（Agent 侧走 settings.json 双 hook，不依赖此项）"
fi

echo "== 6/7 用户级可选项（仓库下发不了，需手动，勿代劳）=="
echo "  [可选] AGENTS.md 与 CLAUDE.local.md 共存：需在 ~/.claude/settings.json 设"
echo "         pluginConfigs['cc-plugin-agents-md@builtin'].options.instructionFiles = \"claude-md-and-agents-md\""
echo "         （项目级设置该键被忽略——《专项》§3.4；不设则维持默认：本仓禁建 CLAUDE.local.md）"
echo "  [可选] OTel 遥测开启只能在 shell/用户级：CLAUDE_CODE_ENABLE_TELEMETRY=1 + OTEL_*（仓库提交的配置只能关不能开——《专项》§6.6）"

echo "== 7/7 完成 → 后续人工步骤 =="
echo "  1) 在仓库根启动 claude（首次会弹 trust——点信任；此时 deny/ask 保护已在，allow 自 trust 起生效）"
echo "  2) 执行学习笔记 §6.4 六项交互式自测（ask 弹框项需默认模式，勿在 bypass 下测）"
echo "  3) MCP servers 将在首次使用时逐个弹框批准（团队不能预批，这是设计而非缺陷）"
echo "  ⚠ 制度：本 workspace 禁用 bypass/自动接受模式——它会令所有 ask 软约束失效（v1.5 实测教训）"
exit $FAIL
