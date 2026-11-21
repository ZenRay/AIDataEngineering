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
| `.pre-commit-config.yaml` | gitleaks 体验层 | ✅ rev 已核对 v8.30.1（2026-11-07） |
| `.github/workflows/ci-baseline.yml` | GitHub CI（只做仓内自洽检查，不碰内网）；与 `.gitlab-ci.yml` 的去留策略实例化时**经用户确认**（清单第 10 步） | 🔮 首跑转正 |
| `.gitlab-ci.yml` | GitLab CI 基线（同含 config 自检 / uv lock / pytest / gitleaks 四类检查；行为不保证等价） | 🔮 探针验证后转正 |

**GitHub CI 兼容性**：模板使用 Node 24 版 checkout v6、setup-python v6 和 Gitleaks Action v3。自托管 runner 须至少满足各 action 的版本要求：setup-python v6 / Gitleaks v3 要求 runner ≥2.327.1；checkout v6 如需在 Docker container action 内执行认证 Git 命令，要求 runner ≥2.329.0。checkout v6 将凭据存放位置从 `.git/config` 改到 runner 临时目录；依赖旧位置的自定义步骤须复核。Gitleaks Action 上游要求组织账号下的仓库配置 `GITLEAKS_LICENSE`；实例化时须确认许可条件，将许可证存入 GitHub secret，并在对应 action 的 `env` 中配置 `GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }}`；不能把许可证写入仓库。fork PR 等拿不到密钥的场景需单独评估；本模板未预设许可 secret。以上是版本与使用条件说明，不是已在实际 runner 上跑通的证明。

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

## 测试基线（硬约束）

**原则：测试代码模块化管理，镜像源码模块树**——不是"按文件平铺测试"。源码根不做 `src/` 预设（镜像对象 = 本仓实际源码模块，无论位于 `src/<pkg>/`、`common/`、`domains/` 等）。

### 目录结构

```
tests/
├── conftest.py                  # 全局 fixture
├── unit/                        # 单元测试：一一镜像源码模块结构
│   └── <module>/                # ↔ 源码模块目录
│       ├── conftest.py          # 模块级 fixture（可选）
│       └── test_<源文件名>.py    # ↔ 源文件同名对应
└── integration/                 # 跨模块 / 外部资源（DB、文件 IO、网络）测试
```

**布局变体（每仓二选一，写入该仓 AGENTS.md）**：`tests/unit/<module>/` 两层布局（上图），或 `tests/<module>/` 直接镜像（code-parser 已验证形态，与 `tests/integration/` 并列）。marker 打标可逐测试标注，或用 conftest `pytest_collection_modifyitems` 按路径自动打标（参考实现见 code-parser `tests/conftest.py`）。

### 硬规则

1. 新增源码模块 ⇒ 同一提交内建对应模块镜像目录（`tests/unit/<module>/` 或 `tests/<module>/`，随本仓布局）；新增源文件 ⇒ 对应 `test_<文件名>.py`
2. `tests/` 根目录**禁止平铺**测试文件（例外：包根源文件——`__init__.py`/`main.py` 等——的对应测试可放 tests/ 根，须在本仓 AGENTS.md 注明）
3. 每个测试必须归属 marker：`unit` 或 `integration`——手工标注或 conftest 路径自动打标均可（`--strict-markers` 拒绝未注册 marker）
4. 分层运行：`uv run pytest -m unit`（快反馈，无外部资源）／`uv run pytest`（全量）
5. 当前 ci-baseline 的 pytest 步骤仅在 `pyproject.toml` 存在且 `tests/` 目录存在并非空时执行；条件不成立时跳过。目录非空不等于存在可收集测试（例如只有 `.gitkeep`），跳过也不等于测试通过。

### Python 测试门禁语义

以下是实例化后的**目标判定语义**；当前模板 CI 尚未自动实现全部判定，实际执行回执和缺口仍需人工检查。适用范围是 Python 项目，其他技术栈按本仓实际测试工具制定对应规则。

| 场景 | 判定与处理 |
|---|---|
| 新仓仅有脚手架、配置或文档，确认没有需测试的源码 | 测试 `not_run` 并说明原因；测试门禁可不阻塞，但不能称为测试通过。其他检查分别裁定。 |
| 已有或新增需测源码，却没有可收集测试 | 测试门禁不通过；不能将无测试的退出状态一律转为成功。新增源码及对应测试仍按上述硬规则审查。 |
| 收集错误、断言失败、运行错误、依赖安装或工具失败 | 门禁不通过，保留原始错误；环境故障不等于业务缺陷，但也不是测试通过。 |
| 必需 unit 测试全部 skip 或 xfail | 属于未完成验证（`partial`），不能报告 unit 门禁通过。 |
| unit 有实际通过，但其他测试失败或出错 | 门禁不通过；一个通过不能抵消失败。 |
| unit 有实际通过且无失败，但部分测试 skip 或 xfail | 只对已运行的范围报告通过；整体标记 `partial` 并说明未执行项。必需项缺失时不视为完整通过。 |
| 集成测试需要外部资源，本次没有环境或授权 | 相应部分标记 `not_run` 或 `partial` 并记录原因；若为本次必需检查，不能视为完整通过，须在有授权的环境补验或按例外处理。 |
| 必需检查的运行状态、版本或结果不明 | 标记 `unknown`，补证或人工裁定，不当作通过。 |

**执行与例外**：至少一个 unit 测试实际通过只能防止空跑，不代表测试充分，也不替代源码与测试对应的硬规则。每仓应在自身约定中明确需测源码范围、测试布局和合理例外；临时例外写明范围、原因、负责人、失效时间或移除条件，以及替代验证。例外仅针对明确范围，不自动免除其他必需检查。对存量差异应记录并制定处理计划，不将未覆盖项直接标为合规。

**分类与运行**：测试可手工打 marker，也可由项目 conftest 按路径自动打标；`--strict-markers` 只拒绝未注册的 marker，**不会要求每项测试都有分类**。当前规则没有规定 `unit` 和 `integration` 互斥；双标可能被两个选择器重复运行，应谨慎使用。`unit` marker 本身不隔离网络或外部资源；成功执行 `-m unit` 也不代表未标记或集成测试已运行。

**现有 CI 的限制**：当前 GitHub 与 GitLab 模板均按前述条件调用全量 `uv run pytest`，未单独执行 `-m unit`，也没有强制检查每项分类、测试实际执行数或源码—测试映射。CI 步骤显示成功或跳过并不自动证明上述目标语义得到满足；要自动强制这些规则，须另行设计、验证并审查 CI/pytest 改动。实例化后的已有仓库不会因本模板文档变更而自动更新。

### 非 Python 栈（框架不同，镜像原则不变）

| 栈 | 测试框架 | 镜像落点 |
|---|---|---|
| Java | JUnit + Maven Surefire | `src/test/java/` 镜像 `src/main/java/` 包结构（Maven 原生约定，天然满足） |
| TS/JS | vitest / jest | `tests/` 镜像 src 模块，或 colocated `__tests__/` |
| Go | 原生 testing | `_test.go` 同包 colocated（语言惯例，天然满足） |
| dbt/SQL | dbt test | schema tests 写进模型同级 yml，随模型走 |

## 实例化

**当前（手工期）完整清单**（与规范 §3 对应；逐项完成，勿只做表层步骤——2026-11-07 code-parser 实例化曾漏掉第 3、7 步）：

1. `cp -r docs/repo-template projects/<name>`
2. **填 AGENTS.md**：写本 repo 差异（技术栈/常用命令/目录结构/本 repo 纪律/验证标注），不得保留模板占位注释
3. **调 `.claude/settings.json`**：allow 在模板基线（uv/git 只读）之上增补本工具链高频命令（例：`Bash(sqlite3:*)`）；deny 三条不动
4. **README 处理**：删除本 README，或改写为项目 README
5. **`pyproject.toml`**：改 name/description/依赖 → `uv lock`（初始锁文件必须入库，CI `uv lock --check` 门禁要求）
6. **`.python-version`**：确认版本 pin 与 CI `setup-python` 一致（如需精确到补丁版本可写 3.12.x）
7. **核对 gitleaks rev**：`.pre-commit-config.yaml` 的 rev 对照 gitleaks 最新 release
8. 仓目录 `direnv allow`
9. `git init -b master`（**默认分支统一 master**；存量仓历史分支名不改）+ remote + 首推（GitLab 首推需 Maintainer 角色，见伞形 AGENTS.md）
10. **CI 文件去留——向用户确认策略，勿自行决定**：二选一，或两份同时保留（镜像/双 host 场景建议保留：平台不执行的文件会被自然忽略，成本可忽略）。若二选一：GitLab 仓删 `.github/`，GitHub 仓删 `.gitlab-ci.yml`。GitLab 落地前先推最小探针 pipeline 摸清 runner/镜像现实，再按需裁剪 `.gitlab-ci.yml`（裁剪决定写入该仓 AGENTS.md）
11. `meta project import projects/<name> <url>` + 伞形仓提交 `chore: register data repo <name>`

**选型后（自动期）**：本目录将转为 copier（或 cruft/cookiecutter）模板仓——获得 `copier update` / `cruft update + cruft check` 的更新传播与 CI 漂移门禁。选型待定（TODO）。
