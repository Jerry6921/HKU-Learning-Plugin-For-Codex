# HKU Learning Plugin For Codex

把 HKU Moodle 课件同步到 Mac，在 Codex 里查课程要求、复习讲义，并把已确认的截止日期同步到 Apple 提醒事项和日历。

[完整安装指南](hiqs-course-mastery-bundle/plugins/hiqs-course-mastery/README.md) · [Course Mastery 提示词](docs/Course-Mastery-Coach-Prompt.md) · [软件许可](LICENSE)

## 快速开始

准备 macOS、Codex CLI、Python 3.11 或更新版本，以及能访问课程的 HKU 账户。当前锁定依赖已在 Python 3.14 上验证。

```sh
git clone https://github.com/Jerry6921/HKU-Learning-Plugin-For-Codex.git
cd HKU-Learning-Plugin-For-Codex/hiqs-course-mastery-bundle
/bin/sh ./plugins/hiqs-course-mastery/program/scripts/run-hiqs.sh --setup
codex plugin marketplace add .
codex plugin add hiqs-course-mastery@hiqs-local
```

首次采集前，安装 Chromium 并在打开的 HKU 页面完成登录。

```sh
HIQS_RUNTIME="$HOME/Library/Application Support/HIQS Course Mastery/0.2.0/venv"
"$HIQS_RUNTIME/bin/python" -m playwright install chromium
"$HIQS_RUNTIME/bin/hsas" login-moodle
```

在 Codex 打开新聊天，试试这个问题：

> 同步这门课的 Moodle 资料。找出下一份作业的截止时间、占分和提交要求，附上我能回查的出处。

## 能做什么

| 工作流 | 使用示例 |
| --- | --- |
| **查课程资料** | 找出小测范围，列出相关讲义和页码。 |
| **Course Mastery 辅导** | 根据讲义画一张知识地图，出一道应用题，等我答完再反馈。 |
| **同步 Apple 日程** | 预览已确认的待办和日程，再同步到专用 HIQS 列表。 |
| **定时检查** | 每天静默同步 Moodle，有新增事项就通知。每周汇总截止日期已确认且仍未完成的事项。 |

Apple 接入需要 macOS 14 或更新版本、Swift 工具链和系统授权。每日检查和每周汇总由宿主定时任务触发。每周汇总需要读取提醒事项的完成状态。[Apple 接入说明](hiqs-course-mastery-bundle/plugins/hiqs-course-mastery/program/docs/apple-integration.md) · [定时检查提示词](hiqs-course-mastery-bundle/plugins/hiqs-course-mastery/prompt/hiqs-scheduled-review/SKILL.md)

## 课程规划

仓库保留独立的 `course-planning` MCP profile 和技能，供比较 lecture、tutorial 与 lab 组合、检查时间冲突。它有单独的设置入口。真实 SIS 选课还没有实际验证。[课程规划 Skill](skills/hiqs-course-planning/SKILL.md) · [实现与验证记录](docs/course-planning-implementation.md)

## 本机数据

Moodle 原文件、文本索引、浏览器会话、课程事实和 Apple 同步回执默认保存在 `~/Library/Application Support/HSAS`。可通过 `HSAS_DATA_DIR` 指定其他目录。查课件时，可通过回答中的来源回到原文件或 Moodle 活动核对。课程材料仍适用原有版权和访问条件。

## 开发

插件目录的 `program/` 提供同步、检索和 Apple 接入，`prompt/` 提供课程资料、定时检查和教学工作流。[插件目录](hiqs-course-mastery-bundle/plugins/hiqs-course-mastery/) · [HIQS 架构](ARCHITECTURE.md) · [贡献指南](CONTRIBUTING.md)
