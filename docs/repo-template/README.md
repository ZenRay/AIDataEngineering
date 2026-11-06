# 子项目模板（repo-template）

`projects/<name>` 新 repo 的内容母本。使用方式与纪律见 [../子项目Agent配置规范.md](../子项目Agent配置规范.md)。

## 文件清单

| 文件 | 作用 | 状态 |
|------|------|:---:|
| `AGENTS.md` | 本 repo 差异规则（技术栈/命令/纪律），通用规则在伞形根 | 必填 |
| `CLAUDE.md` | 固定一行 `@AGENTS.md` | 勿改 |
| `.claude/settings.json` | **自包含**的 repo 级 allow + 本地 deny（双轨制：根启动时不加载，独立 clone//cd 生效） | 按栈调整 allow |
| `.envrc` | direnv 环境变量（方案 D）；`dotenv` 行注释放开即读本机 `.env` | 敏感值禁明文 |
| `.env.example` | 敏感变量 schema 文档（真实值只在本机 `.env`，永不入库） | 按栈补齐 |
| `.python-version` | uv Python 版本 pin（与 CI 3.12 对齐） | 按仓调整，改后 `uv sync` |
| `pyproject.toml` | uv 项目脚手架 + ruff 基线（语言基线的落点） | 实例化改 name/依赖后 `uv lock` |
| `.gitignore` | venv/env/local 配置一律不入库；`uv.lock` 必须入库 | 基本不动 |
| `.pre-commit-config.yaml` | gitleaks 体验层 | ⚠️ rev 需核对 |
| `.github/workflows/ci-baseline.yml` | 正式期 CI（只做仓内自洽检查，不碰内网） | 🔮 首跑转正 |

## 语言基线（可选参考）

**原则：规范本体 = 仓内工具配置**（formatter/linter 进各语言配置文件），本节只做选型指针——实例化时按仓语言复制基线配置，不另抄规范正文。

| 语言 | 格式化 | Lint | 配置锚点 |
|---|---|---|---|
| Python | ruff format | ruff（`select = ["E","F","I","N","W"]`、line-length 100 起步） | `pyproject.toml [tool.ruff]`（data-warehouse 已验证基线） |
| TypeScript / JavaScript | Prettier | ESLint（+ typescript-eslint） | `.prettierrc` / `eslint.config.js` |
| Java | Spotless + google-java-format | Checkstyle | `pom.xml` 插件段 |
| Go | gofmt / goimports | golangci-lint | `.golangci.yml` |
| SQL | sqlfluff（显式 dialect） | sqlfluff | `.sqlfluff` |

**代码语言约定**：注释与 docstring 一律英文；中文仅用于面向人的 page 文档（README、docs 站点、学习笔记）。

**提交规范**：跟随伞形 AGENTS.md「提交规范」节（英文 subject、Conventional Commits、无机器人尾注、固定格式提交）；团队数据仓自有规范时优先。

## 实例化

- **当前（手工期）**：`cp -r docs/repo-template projects/<name>`，删除本 README，改 `pyproject.toml` name/description/依赖后运行 `uv lock`（生成初始锁文件，CI `uv lock --check` 门禁要求入库），在仓目录 `direnv allow`，按规范 §3 走完登记与提交
- **选型后（自动期）**：本目录将转为 copier（或 cruft/cookiecutter）模板仓——获得 `copier update` / `cruft update + cruft check` 的更新传播与 CI 漂移门禁。选型待定（TODO）。
