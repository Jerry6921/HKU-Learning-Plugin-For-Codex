# HKU Learning Plugin For Codex

把香港大学 Moodle 课件同步到 Mac，再在 Codex 里查作业要求、复习讲义，或把已确认的课程截止日期加入 Apple 提醒事项与日历。查课程事实时，插件会回读本机资料，回答可附 Moodle 活动、文件及页码等出处。

当前插件版本为 **0.2.1**。在 Codex 中显示为 **HIQS + Course Mastery**。

## 快速开始

准备 macOS、Codex CLI、Python 3.11 或更新版本，以及可访问课程的 HKU 账户。当前锁定依赖在 Python 3.14 上验证。

```sh
git clone https://github.com/Jerry6921/HKU-Learning-Plugin-For-Codex.git
cd HKU-Learning-Plugin-For-Codex/hiqs-course-mastery-bundle
/bin/sh ./plugins/hiqs-course-mastery/program/scripts/run-hiqs.sh --setup
codex plugin marketplace add .
codex plugin add hiqs-course-mastery@hiqs-local
```

使用 ZIP 时，从解压目录执行最后三个命令。安装完成后在 Codex 打开新聊天。

### 连接 Moodle

先安装 Chromium，再在打开的 HKU 页面完成登录和多重认证。

```sh
HIQS_RUNTIME="$HOME/Library/Application Support/HIQS Course Mastery/0.2.0/venv"
"$HIQS_RUNTIME/bin/python" -m playwright install chromium
"$HIQS_RUNTIME/bin/hsas" login-moodle
```

回到 Codex，可以直接问：

> 同步这门课的 Moodle 资料。找出最新作业的截止时间、提交要求和占分，附上我可以回查的出处。

### 连接 Apple 提醒事项和日历

如需把课程安排同步给 Apple，在 macOS 14 或更新版本上准备 Swift 工具链，然后运行以下命令并按系统提示授权。

```sh
"$HIQS_RUNTIME/bin/hsas" apple connect
```

在 Codex 里先预览已确认事项，再按授权同步。插件使用专用 HIQS 日历和提醒事项列表，写入后在本机读回核对。[Apple 接入和同步规则](program/docs/apple-integration.md)

## 使用示例

| 工作流 | 可以怎么问 |
| --- | --- |
| 查课件和考核 | 查这次小测的范围，列出对应讲义和页码。 |
| Course Mastery 辅导 | 用这节课的讲义给我一张知识地图，再出一道应用题。等我答完再反馈。 |
| 定时检查 | 每天静默同步一次，发现新增作业或测验时通知我。每周汇总已有明确截止日期且未完成的事项。 |

定时检查由 Codex 或其他宿主的定时任务触发。每周汇总需要宿主能读取提醒事项的完成状态。无法核实时会标明缺口。[定时检查提示词](prompt/hiqs-scheduled-review/SKILL.md)

需要复制教学提示词时，可打开合并版 Markdown，里面包含主提示词及课程与考核参考。[Course Mastery Coach 提示词](../../../docs/Course-Mastery-Coach-Prompt.md)

## 数据和目录

Moodle 快照、浏览器登录状态、课程事实库和 Apple 回执存放在本机。默认资料目录是 `~/Library/Application Support/HSAS`。使用自定义目录时，让 Codex 和登录命令读取同一个 `HSAS_DATA_DIR`。已有 HIQS 资料和 Apple 配置沿用原有 JSON 格式。

- `program/` 包含 Moodle 采集、课件检索、课程事实校验和 Apple 同步程序。[程序目录](program/)
- `prompt/` 包含课程资料操作、定时检查及教学工作流。[技能目录](prompt/)

后端基于 HIQS 2.12.0，源提交为 `e04eca5ae357d6723f46195d4dd81cca0d0bb5d9`。[许可](program/LICENSE) · [第三方声明](program/THIRD_PARTY_NOTICES.md)
