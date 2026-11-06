# <repo 名> — 子项目约定

> 本文件只写**本 repo 的差异**；项目集通用规则见伞形 repo 根 AGENTS.md（双轨制：伞形根启动会话时本文件经惰性加载，独立 clone 时经启动加载）。

## 技术栈与命令
<!-- 例：Python 3.12 (uv)｜`uv sync` 装依赖｜`uv run pytest` 测试｜`uv run dbt build --select state:modified+ --defer --state target/` CI 语义 -->

## 目录结构
<!-- 例：src/ 源码｜tests/ 测试｜dbt/ models... -->

## 本 repo 纪律
<!-- 例：dbt 模型改动必须带 test；测试硬镜像（tests/unit/<module>/ ↔ 源码模块，新增模块必须带测试目录，见模板 README「测试基线」）；禁止手工 pip install（uv sync 会剪除）；分支模型 main + PR -->

## 验证标注
<!-- 沿用项目集体系：✅ 已验证 / ⚠️ 未验证 / 🔮 推断 /【待实测】 -->
