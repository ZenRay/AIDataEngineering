# 顶层脚本回归测试

从仓库根目录运行（仅需 Python 3 标准库；本机已在 3.11、3.12、3.14 验证）：

```bash
python3 -B -I scripts/run-script-tests.py
```

测试入口在发现零个测试时返回非零，即使 Python 版本默认将空测试视为成功。测试使用合成配置和临时目录。onboarding 测试复制脚本，使用真实 Git 仅解析临时合成配置，其余 Git 操作及 meta、direnv 均用假工具；不会运行真实 onboarding、初始化真实子模块或授权真实环境。顶层 CI 配置已加入该测试和 shell 语法检查；真实 CI 运行结果须以实际回执为准。

模板 GitHub CI 配置自检的回归测试从模板 workflow 中提取该步骤，在临时目录使用 Bash 的 CI 选项运行有效和无效输入，并用旧版 `&&` 写法确认反例可被检测。提取器只接受当前约定的步骤名和 YAML 文本布局；布局变化时测试会失败并需同步维护，不替代 YAML 语义校验或真实 Actions 运行。不会运行模板中的依赖安装、pytest 或 secret scan 步骤。
