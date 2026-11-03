# 子项目模板（repo-template）

`projects/<name>` 新 repo 的内容母本。使用方式与纪律见 [../子项目Agent配置规范.md](../子项目Agent配置规范.md)。

## 文件清单

| 文件 | 作用 | 状态 |
|------|------|:---:|
| `AGENTS.md` | 本 repo 差异规则（技术栈/命令/纪律），通用规则在伞形根 | 必填 |
| `CLAUDE.md` | 固定一行 `@AGENTS.md` | 勿改 |
| `.claude/settings.json` | **自包含**的 repo 级 allow + 本地 deny（双轨制：根启动时不加载，独立 clone//cd 生效） | 按栈调整 allow |
| `.envrc` | direnv 环境变量（方案 D） | 敏感值禁明文 |
| `.gitignore` | venv/env/local 配置一律不入库；`uv.lock` 必须入库 | 基本不动 |
| `.pre-commit-config.yaml` | gitleaks 体验层 | ⚠️ rev 需核对 |
| `.github/workflows/ci-baseline.yml` | 正式期 CI（只做仓内自洽检查，不碰内网） | 🔮 首跑转正 |

## 实例化

- **当前（手工期）**：`cp -r docs/repo-template projects/<name>`，删除本 README，按规范 §3 走完登记与提交
- **选型后（自动期）**：本目录将转为 copier（或 cruft/cookiecutter）模板仓——获得 `copier update` / `cruft update + cruft check` 的更新传播与 CI 漂移门禁。选型待定（TODO）。
