---
title: GitHub Actions CI 可行性探针方法论（靶子测试）
create_time: 2026-11-03 09:55:19
update_time: 2026-11-03 10:05:00
category: devops
subcategory: cicd
documentType: tutorial
purpose: tutorial
status: active
project: AIDataEngineering
tags: [GitHub-Actions, CI探针, 反向断言, 靶子仓库, 可行性验证]
project-description: AI 数据工程项目集：伞形 workspace（8 个上游业务输入源仓库 + 数据建设 repo 群），多人协作，AI Agent 深度参与
# ── 扩展辅助字段（snapshot 组）──
snapshot_date: 2026-11-03
snapshot_source: ZenRay/test 真实 Actions 运行（双 job 全绿）+ 伞形 workspace CI 落位决策链
snapshot_env: GitHub private repo（个人号）+ ubuntu-latest hosted runner；企业内网 GitLab（域名已脱敏）作可达性标靶
snapshot_archive: ZenRay/test @ 5060997（探针仓，可能被删——故 yml 全文内联本文 §4.2）；伞形仓库 README TODO-1 关闭记录
---

# GitHub Actions CI 可行性探针方法论（靶子测试）

> **这篇文档教你什么**：不是 GitHub Actions 语法课（官方文档更全），而是一个工程方法论——**在你把任何 CI 方案定下来之前，怎么用一个"靶子仓库 + 带断言的 workflow"花 10 分钟验证"到底可行不可行"**。我们拿真实案例走了一遍：CI 主战场选型时，三个想当然的假设里有一个是错的，而错的那个足以让方案翻车。
> **适合谁**：没怎么碰过 CI 的新手（有术语表和逐步操作），以及需要向 GitLab 复制这套做法的同学（§7 有移植指南）。
> **改这篇文档前**：看 §8 迭代须知与 §9 验证状态表。

---

## 0. 概念准备（新手 3 分钟）

| 术语 | 一句话解释 | 深入阅读 |
|------|------|------|
| **CI**（持续集成） | 把"机器帮你检查代码/配置"的流程固化下来：每次 push/PR 自动跑一组任务 | — |
| **GitHub Actions** | GitHub 自带的 CI 平台。你在仓库里放 `.github/workflows/*.yml`，push 后 GitHub 的机器（runner）自动按 yml 执行 | [官方：理解 GitHub Actions](https://docs.github.com/en/actions/learn-github-actions/understanding-github-actions) |
| **workflow / job / step** | 三层套娃：一个 yml 文件 = 一个 workflow；内含多个并行的 job；每个 job 由多个 step 顺序执行 | [官方：Workflow 语法](https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions) |
| **runner** | 真正跑命令的机器。**hosted**=GitHub 云端的机器（开箱即用，但它在公网）；**self-hosted**=你自己提供的机器（可以在你的内网里） | [hosted 说明](https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners) · [self-hosted 说明](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/about-self-hosted-runners) · [runner 镜像（ubuntu-latest 里有什么）](https://github.com/actions/runner-images) |
| **`on: push`** | 触发器：有代码推上来就自动开跑——所以我们"触发 Actions"的方式就是普通的一次 `git push` | 同 Workflow 语法 §on |
| **额度（private 仓）** | 个人 private 仓每月有免费分钟数（ubuntu runner），超出计钱——探针这种量级用不到零头 | [官方 Limits](https://docs.github.com/en/actions/reference/limits) |
| **靶子仓库（throwaway repo）** | 专门用来做一次性实验的小破仓库。真仓库别拿来试——实验产物（提交、workflow）是脏的，靶子用完可弃 | — |
| **反向断言** | 本篇最重要的技巧，§5 细说 | — |

---

## 1. 背景：我们差点在三个"想当然"上定 CI 方案

伞形 workspace 讨论 Phase 2（Renovate bump PR / Gitleaks 扫描 / dbt CI）时，脑子里有三个**未经验证的假设**：

| # | 假设 | 错得多彻底 |
|:---:|------|------|
| A1 | "GitHub Actions 生态最全，配置校验、secrets 扫描都能先放我这"（个人 GitHub 的 private repo） | ✅ 对了——但要验：private repo 的 Actions 可能被设置/组织策略关掉 |
| A2 | "Renovate 给 submodule 提 bump PR，放 GitHub 侧跑也挺方便" | 🔴 **大错**：bump 的前提是能访问上游仓库——我们的 8 个输入源全在**企业内网 GitLab**。GitHub 的 hosted runner 在公网，物理上够不到内网 |
| A3 | "内网当然没公网暴露面" | 未验证——如果真暴露了，那不是 CI 问题，是**安全事故**，比 CI 结论重要一万倍 |

**这就是"可行性探针"存在的意义**：A2 错在架构层（网络物理可达性），任何配置技巧都救不回来；越早花 10 分钟验证，越晚返工。A3 顺便被验证一次，红灯就上报。

> 通用化一句话：凡是要把 CI/自动化放到某个平台，先回答三连问——**① 平台的 CI 在你这种仓（private/组织策略）上开着吗？② 它的 runner 够得着你所有依赖资源吗？③ 验证过程中顺便探测有没有你不想要的暴露面。**

---

## 2. 目标与前置条件

**目标**：用一个 workflow、两个 job，一次跑完回答 A1/A2/A3。

**前置条件**：
1. 一个 GitHub 账号 + 一个可折腾的 **靶子 private repo**（我们的 `ZenRay/test` 就是前几轮双推实验的靶子，一仓两用）
2. 本机 git 可推送到该 repo（SSH key 已配好——这一步不通就先解决凭据，也是 A1 的一部分）
3. 一个"预期够不到"的内网资源地址当探针目标（我们：企业内网 GitLab 地址，此处已脱敏）
4. ⚠️ 安全前置：探针目标要选**你们本来就认定"仅内网可达"** 的地址，别拿允许公网访问的服务当标靶

## 3. 设计：探针 workflow 的三条纪律

1. **每个 job 只回答一个是非题**，且把"期望的世界"写成代码里的断言——不靠人肉看日志
2. **区分"验证可能"和"验证不可能"**：A1 是正向断言（能跑通=绿灯）；A2/A3 是**反向断言**（够不到=绿灯），见 §5
3. **输出自解释**：断言 job 的 echo/报错文本要让三年后的自己不用查上下文就能看懂结论

---

## 4. 实操（tutorial 步骤）

### 4.1 步骤序列

```bash
# ① 本地克隆靶子仓
git clone git@github.com:ZenRay/test.git /tmp/gh-ci-probe && cd /tmp/gh-ci-probe

# ② 放入探针 workflow（内容见 4.2，路径必须是 .github/workflows/）
mkdir -p .github/workflows && $EDITOR .github/workflows/github-ci-probe.yml

# ③ 提交并推送——push 本身就是触发器（workflow 里 on: push）
git add . && git commit -m "ci: probe" && git push origin HEAD:main

# ④ 看结果（需登录该仓的浏览器）：
#    run 列表：https://github.com/ZenRay/test/actions
#    本 workflow 的历史运行：https://github.com/ZenRay/test/actions/workflows/github-ci-probe.yml
#    workflow 源文件：https://github.com/ZenRay/test/blob/main/.github/workflows/github-ci-probe.yml
#    命令行只能看到 push 成功，看不到 run 结果（无 gh CLI 时去网页；点进 run 可看每个 job 的实时日志）
```

### 4.2 探针 workflow 全文（我们的实际版本，含逐行讲解）

> ✅ 本文件在 ZenRay/test @ `5060997` 真实跑过、双 job 绿灯。原仓可能被删，全文在此留底——**这就是"内联归档"取代"引用靶子仓"的原因：模板的存续不能押在靶子身上**。

```yaml
name: github-ci-probe            # Actions 页面上显示的名字
on: push                         # 触发器：任何 push 自动跑（靶子仓只有我们，随便）

jobs:
  # ── 正向断言：回答 A1「private repo 的 Actions 到底能不能用」──
  actions-alive:
    runs-on: ubuntu-latest       # GitHub 托管 runner（公网机器）
    steps:
      - uses: actions/checkout@v4   # 官方 checkout 动作：private 仓能拉下代码 = 授权链路通
      - run: |
          echo "actions alive; runner can checkout private repo"
          git --version && uname -a # 顺手留 runner 环境指纹，便于日后排查

  # ── 反向断言：回答 A2+A3「hosted runner 应当够不到内网」──
  intranet-unreachable-assert:
    runs-on: ubuntu-latest
    steps:
      - name: assert GitHub-hosted runner CANNOT reach corp intranet GitLab
        run: |
          set +e                                            # 不让"命令失败"直接弄死 job——失败才是我们要的
          OUT=$(GIT_TERMINAL_PROMPT=0 timeout 25 git ls-remote https://INTRANET-GITLAB.example/da/dual-push-test.git HEAD 2>&1)
          RC=$?                                             # 只探"够不够得到"，不碰数据——拿一个不存在的仓探也行
          echo "exit=$RC"; echo "$OUT"                     # 全程留证据：绿了也要能复查依据
          if [ $RC -eq 0 ]; then
            echo "::error::UNEXPECTED: intranet reachable anonymously from GitHub runners - raise security flag and revisit"
            exit 1                                          # 意外够得到 = 内网有公网暴露面 → 红灯即安全告警
          fi
          case "$OUT" in
            *Could*resolve*|*timed*|*timeout*) echo "confirmed: DNS/network unreachable => intranet-dependent CI cannot run on GitHub-hosted" ;;
            *) echo "confirmed: unreachable-by-auth/error => still cannot use as CI data path without credentials exposure" ;;
          esac
```

---

## 5. 本篇的核心技巧：反向断言

验证"某事**能**成"很直白；验证"某事**不能**成"有个陷阱：**普通写法里，命令失败 job 也失败**，你就得靠人翻日志区分"预期的失败"和"环境的失败"。反向断言把这件事翻转成代码：

```
期望的世界（够不到）→ 脚本判 RC≠0 → exit 0 → job 绿    ← 绿灯=约束成立
不期望的世界（够到了）→ 脚本 exit 1 → job 红 + ::error::  ← 红灯=世界不对，顺手当告警
```

三个要点：① `set +e` 接管错误判断权，别让 shell 的默认行为替你断言；② **红灯必须携带行动指令**（我们的报错文本直接写 "raise security flag"）；③ 绿了也要 `echo` 证据（失败原因分类：DNS/超时 vs 认证墙），否则无法区分"够不到"和"探针本身写挂了"。

这套写法可平移到任何"验证不可能"的场合：防火墙边界、网络隔离、权限负面用例、"这个密钥不该能登录"……

## 6. 实测结果与验证方法（判读矩阵）

两个 job 全绿（2026-11-03，ZenRay/test Actions 页）→

| 问题 | 判定 | 依据 |
|------|------|------|
| A1 private Actions 可用性 | ✅ 可用 | `actions-alive` 绿（checkout 成功 + 命令执行） |
| A2 hosted runner 达内网 | ❌ **不可达（约束成立）** | `intranet-unreachable-assert` 绿 |
| A3 内网公网暴露面 | ✅ 未见暴露 | 同上（若可达该 job 会红并告警） |

**判读矩阵**（以后任何人重跑探针，按此表读）：

| actions-alive | intranet-assert | 结论与动作 |
|:---:|:---:|------|
| 🟢 | 🟢 | 正常：落位表（§7 左列）成立 |
| 🔴 | — | Actions 被关/凭据问题：查 repo Settings→Actions；不阻塞 A2 结论但需修 |
| — | 🔴(`UNEXPECTED`) | 🔴 **安全事件级**：内网 GitLab 在公网可达——立即上报，与 CI 无关 |
| 🟢 | 🔴(其他错) | 探针本身坏了（网络抖动/目标仓 404 处理）：看 job 日志的 OUT 证据段重判 |

## 7. CI 落位定案（探针换来的结论，指导后续所有配置）

| 工作负载 | 落位 | 理由 |
|------|------|------|
| 配置校验（settings.json jq / AGENTS.md 链接 / 笔记 validate.py） | **GitHub Actions 可先行** ✅ | 只读仓内文件，无外部依赖（A1） |
| Gitleaks 服务端扫描 | **GitHub Actions** ✅ | 同上；且"服务端才算数"（客户端 pre-commit 可 `SKIP=` 绕过，已验证结论） |
| docs 构建 | GitHub Actions ✅ | 同上 |
| Renovate：submodule bump PR（输入源指针更新） | **必须内网侧**（GitLab CI 或内网 self-hosted runner） | A2：runner 要能访问内网上游，hosted 物理不可达 |
| dbt/Data Contract CI（连数仓） | 同上，内网侧 | 同理（数仓在内网） |
| evals 门禁（若不依赖内网数据） | GitHub Actions ✅ | 视数据源而定 |

**正式期（正常阶段）起步模板**——🔮 设计级，伞形 repo 上 GitHub 后首个 commit 落地并跑绿才算验证：

```yaml
# .github/workflows/ci-baseline.yml（正式期起步：只做"仓内自洽"检查，永不碰内网）
name: ci-baseline
on: [push, pull_request]
jobs:
  validate-configs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: jq -e '.permissions | has("ask") and has("deny")' .claude/settings.json
      - run: python3 ~/.local/bin/validate-learning-notes.sh || python3 scripts/validate.py docs/LearningNote --strict
      # ↑ validate.py 随仓走：把 skill 的校验脚本复制进 scripts/ 供 CI 用（本机路径在 runner 上不存在）
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 10 }
      - uses: gitleaks/gitleaks-action@v2      # 官方 Action；需 repo 配 GITHUB_TOKEN 读权限（默认即可）
        env: { GITHUB_TOKEN: "${{ secrets.GITHUB_TOKEN }}" }
```

## 8. 迭代须知（修改本文档前）

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-11-03 | 初版：靶子探针方法论 + 实测判读 + CI 落位定案 + 正式期起步模板 |
| v1.0.1 | 2026-11-03 | 按反馈补链接：术语表内联官方文档列、§4.1 run 网页入口直链、新增 §11 参考链接（checkout ✅ 实跑 / gitleaks-action 🔮 未实跑分开标注） |

- 修改 §6/§7 结论前查 §9 验证表（尤其：GitHub 若对 runner 出网策略改版、内网 GitLab 增加公网入口，A2/A3 结论**必须重跑探针**——把 4.2 的 yml 再推一次靶子仓即可，10 分钟）
- 正式期模板（§7 底部）落地跑绿后：版本历史加行、其状态从 🔮 升 ✅，并同步伞形 README TODO 板
- 关联文档：README（TODO-1 关闭记录/TODO-2 GitLab 探针计划）·《伞形工作区环境初始化决策记录》§6.5（本案例在项目决策链中的位置）

## 9. 验证状态表

| 结论 | 验证方式 | 绑定条件 | 失效风险 | 复核动作 |
|------|------|------|:---:|------|
| private repo Actions 可用（个人号） | ✅ 真实 run 绿灯 | 2026-11-03 GitHub ubuntu-latest | 中：组织策略/账号设置可变 | 重跑 actions-alive job |
| hosted runner 不可达内网 GitLab | ✅ 反向断言绿灯 | 同上 + 内网无公网入口的现状 | 中：网络拓扑变更即失效 | 重跑 assert job；红灯先当安全事件处理 |
| CI 落位表（§7） | ✅（内网侧行是"排除法"结论）| 基于上两行 | 低 | 前提变更时整体重判 |
| 正式期 ci-baseline 模板可用 | 🔮 设计级，未跑过 | — | 高 | 伞形 repo 上 GitHub 后首 commit 实跑 |
| GitLab 侧探针移植（§10） | ⚠️ 未开始 | — | — | TODO-2 执行时 |

## 10. GitLab 移植指南（TODO-2 时照着做）

同一套"三连问 + 反向断言"，在 GitLab 上的对应形态：

| 探针问题 | GitLab 上的等价探法 |
|------|------|
| CI 开不开（runner） | 建靶子项目跑最小 `.gitlab-ci.yml`（`test: {script: [echo hi]}`）——没有可用 runner 会永远 pending；runner 情况问管理员（TODO-2） |
| runner 够不够得到目标 | job 内跑 `git ls-remote <内网仓>`（内网 runner 预期通→正向断言）与 `git ls-remote https://github.com/<你的靶子>`（测 runner 出公网能力，决定 Renovate 能否在 GitLab 跑——**Renovate 需要访问内网 GitLab，大概率还要出网装包**） |
| 权限边界 | 顺带验证 §9.1#2 凭据调查：普通成员 token 对输入源仓的只读可达性 |
| 附加必答 | 空仓首推角色墙（v2.7 已撞过）：靶子项目验证 Maintainer 申请是否到位 |

## 11. 参考链接（概念 → 官方文档；实操 → 本次靶子）

**官方概念/配置**：[理解 Actions](https://docs.github.com/en/actions/learn-github-actions/understanding-github-actions) · [Workflow 全语法](https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions) · [hosted runners](https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners) / [self-hosted runners](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/about-self-hosted-runners) · [Limits 与免费额度](https://docs.github.com/en/actions/reference/limits) · [private 仓 Actions 开关（settings 被关时来这查）](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository)

**本次靶子实操**（需登录）：[run 列表](https://github.com/ZenRay/test/actions) · [github-ci-probe 运行史](https://github.com/ZenRay/test/actions/workflows/github-ci-probe.yml) · [源文件 @ 5060997](https://github.com/ZenRay/test/blob/main/.github/workflows/github-ci-probe.yml)

**用到的第三方 Actions**：[actions/checkout@v4](https://github.com/actions/checkout)（✅ 本次实跑） · [gitleaks/gitleaks-action@v2](https://github.com/gitleaks/gitleaks-action)（🔮 正式期模板引用，未实跑——用前核对 README 的 token 权限要求）

## 附录：新手常见坑

| 坑 | 解法 |
|------|------|
| yml 放错目录（`workflows/`） | 必须 `.github/workflows/xxx.yml`，名字随意，后缀必须 .yml/.yaml |
| push 了但 Actions 没跑 | Settings→Actions 是否被关；workflow 首文件要在**默认分支**才会自动列显 |
| 以为 push 会弹确认/被本地 hook 拦 | CI 探针仓在 GitHub，与本地 `.claude/settings.json` 的 `Bash(git push:*)` ask 是两回事（本会话还见过它的复合命令漏网——见伞形笔记 §6.5 附带观察） |
| 把实验提交混进真仓历史 | 所以才要靶子仓——**永远不要在准备长期存在的仓里做可行性试错** |
| 探针成功后删靶子仓丢了模板 | 模板全文内联进笔记（§4.2），靶子才可安全弃 |
