# HKU Learning Plugin For Codex

用 HKU Moodle 课件在 Codex 里学一门课，再把需要完成的事汇总成清单。插件自带 **Course Mastery Coach** 和 **定时检查**，可以按课件辅导，也可以安排定期同步和提醒。

[快速开始](#快速开始) · [完整安装指南](hiqs-course-mastery-bundle/plugins/hiqs-course-mastery/README.md) · [软件许可](LICENSE)

## Course Mastery Coach

从本学期讲义、教程和考核资料出发。可以先生成一张带课件出处的知识地图，再按章节讲解。每次练习先出题，等你独立作答后再指出关键错误，安排变式题和隔时复测。想深入一节时，也可以请教练推荐对应的 Moodle 阅读。

> 用这章讲义给我一张知识地图，标出关键页码。先出一道应用题，等我答完再讲。

[教学 Skill](hiqs-course-mastery-bundle/plugins/hiqs-course-mastery/prompt/course-mastery-coach/SKILL.md) · [复制完整教学提示词](docs/Course-Mastery-Coach-Prompt.md)

## 定时检查与截止事项

- **每天一次**静默同步 Moodle。发现新增作业、测验、考试等需要处理的事项时，当次通知并附来源。没有新增事项时保持静默。
- **每周一次**汇总截止日期已确认、且核实仍未完成的事项。逾期事项排在前面，每条附课程、截止时间和来源。

安装后可在宿主中分别设置每日和每周的触发时间。每周汇总需要读取 Apple 提醒事项的完成状态。无法核实的项会标明状态待核实。[定时检查 Skill](hiqs-course-mastery-bundle/plugins/hiqs-course-mastery/prompt/hiqs-scheduled-review/SKILL.md)

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

## 查课件与同步 Apple 日程

也可以直接查小测范围、作业占分和提交要求，或预览并同步已确认的待办和日程。Apple 接入需要 macOS 14 或更新版本、Swift 工具链和系统授权。[Apple 接入说明](hiqs-course-mastery-bundle/plugins/hiqs-course-mastery/program/docs/apple-integration.md)

## 课程规划

仓库保留独立的 `course-planning` MCP profile 和技能，供比较 lecture、tutorial 与 lab 组合、检查时间冲突。它有单独的设置入口。真实 SIS 选课还没有实际验证。[课程规划 Skill](skills/hiqs-course-planning/SKILL.md) · [实现与验证记录](docs/course-planning-implementation.md)

## 本机数据

Moodle 原文件、文本索引、浏览器会话、课程事实和 Apple 同步回执默认保存在 `~/Library/Application Support/HSAS`。可通过 `HSAS_DATA_DIR` 指定其他目录。查课件时，可通过回答中的来源回到原文件或 Moodle 活动核对。课程材料仍适用原有版权和访问条件。

## 开发

插件目录的 `program/` 提供同步、检索和 Apple 接入，`prompt/` 提供课程资料、定时检查和教学工作流。[插件目录](hiqs-course-mastery-bundle/plugins/hiqs-course-mastery/) · [HIQS 架构](ARCHITECTURE.md) · [贡献指南](CONTRIBUTING.md)
