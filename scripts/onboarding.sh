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

# MCP 特定检查（2026-11 新增）
if [ -f .mcp.json ]; then
  ok ".mcp.json 存在（项目级 MCP 配置）"
  # The credential checker runs only after the human review checkpoint below.
  warn ".mcp.json 凭据检查将在人工审查后进行；未检出不代表安全"
else
  warn ".mcp.json 不存在（MCP PoC 评估阶段，后续按需创建）"
fi

# 检查 .env 文件（敏感配置）
if [ -f .env ]; then
  ok ".env 文件存在（敏感配置已隔离 ✓）"
  # 检查 .env 是否被 gitignore
  if git check-ignore .env >/dev/null 2>&1; then
    ok ".env 已被 gitignore 忽略（安全 ✓）"
  else
    bad ".env 未被 gitignore 忽略！请立即添加到 .gitignore（敏感信息泄露风险）"
  fi
else
  warn ".env 文件不存在——MCP 服务器无法连接"
  if [ -f .env.example ]; then
    echo "    请执行: cp .env.example .env && 编辑 .env 填入真实配置"
  fi
fi

# 检查 .envrc 是否正确引用 .env
if grep -q 'source .env' .envrc 2>/dev/null; then
  ok ".envrc 正确引用 .env 文件 ✓"
else
  bad ".envrc 未引用 .env 文件——环境变量将无法加载"
fi

echo "== 3/7 人工配置审查（不可跳过）=="
echo "  trust 前需过目的文件："
for p in .claude/settings.json .claude/hooks/*.sh .claude/skills .mcp.json .codex/config.toml scripts/onboarding.sh scripts/check-mcp-config.py; do
  [ -e "$p" ] && echo "    $p"
done
if [ "${1:-}" != "--reviewed" ]; then
  printf "  已完成人工审查？（输入 yes 继续——审查是人的判断，脚本不能代劳）> "
  read -r ans
  [ "$ans" = "yes" ] || { echo "  已中止：顺序必须是 clone → 审查 → trust。"; exit 1; }
fi

# Inspect common patterns without printing configuration values.
if [ -f .mcp.json ]; then
  if ! command -v python3 >/dev/null 2>&1; then
    bad "缺 python3：无法检查 .mcp.json 常见凭据模式，需人工审查"
    echo "  已中止：未完成配置检查，不执行 bootstrap。"
    exit 1
  elif python3 -I scripts/check-mcp-config.py .mcp.json; then
    ok ".mcp.json 常见凭据模式未检出；仍需人工审查"
  else
    bad ".mcp.json 检查未通过或无法读取/解析；需人工审查"
    echo "  已中止：未完成配置检查，不执行 bootstrap。"
    exit 1
  fi
fi

# Prevent bootstrap when any earlier mandatory check has failed.
if [ "$FAIL" -ne 0 ]; then
  echo "  已中止：前置检查未通过，不执行 bootstrap 或环境授权。"
  exit 1
fi

echo "== 4/7 仓库 bootstrap =="
# 伞形仓的 .gitmodules/.meta 使用 URL 别名（upstream: / upstream-user: / darepo: / scm:），
# 真实地址只存在于每人本机的 ~/.gitconfig（insteadOf 映射，不入仓不推送）。
# 首次配置：向伞形仓负责人索取四条 git config --global 映射命令（经内网/线下渠道传递）。
MISSING_ALIASES=""
for a in upstream: upstream-user: darepo: scm:; do
  if ! git config --global --get-regexp '^url\..*\.insteadof$' 2>/dev/null | awk -v alias="$a" '$NF == alias { found=1 } END { exit !found }'; then
    MISSING_ALIASES="$MISSING_ALIASES $a"
  fi
done
if [ -n "$MISSING_ALIASES" ]; then
  bad "缺少 URL 别名映射 ——$MISSING_ALIASES —— submodule/meta 将无法解析！请向负责人索取对应的 insteadOf 配置命令并执行后重跑本脚本"
  echo "  已中止：别名检查未通过，不执行 bootstrap。"
  exit 1
else
  ok "URL 别名映射已配置（upstream:/upstream-user:/darepo:/scm: 全部就绪）"
fi
git submodule update --init --recursive && ok "submodules 初始化完成" || bad "submodule init 失败（检查内网/代理可达性与 SSH key；伞形仓用别名 URL，见上方映射检查）"
if [ -f .meta ] && command -v meta >/dev/null; then
  meta git update && ok "meta 清单同步完成（注意：新清单要先 git pull，meta git update 不拉清单）" || warn "meta git update 失败"
else
  warn "尚无 .meta 或 meta 未装 —— Phase 2 首个数据 repo 登记后此步自动生效"
fi

echo "== 5/7 环境激活（方案 D：direnv）=="
while IFS= read -r e; do
  direnv allow "$(dirname "$e")" >/dev/null 2>&1 && ok "direnv allow $(dirname "$e")" || bad "direnv allow 失败：$(dirname "$e")"
done < <(find . \( -path './BackDocs' -o -path './submodules' -o -path './docs/repo-template' -o -path './.git' \) -prune -o -type f -name .envrc -print 2>/dev/null)
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
