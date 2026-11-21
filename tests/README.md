# 顶层脚本回归测试

从仓库根目录运行（仅需 Python 3 标准库；本机已在 3.11、3.12、3.14 验证）：

```bash
python3 -B -I scripts/run-script-tests.py
```

测试入口在发现零个测试时返回非零，即使 Python 版本默认将空测试视为成功。测试使用合成配置和临时目录。onboarding 测试复制脚本，使用真实 Git 仅解析临时合成配置，其余 Git 操作及 meta、direnv 均用假工具；不会运行真实 onboarding、初始化真实子模块或授权真实环境。顶层 CI 配置已加入该测试和 shell 语法检查；真实 CI 运行结果须以实际回执为准。
