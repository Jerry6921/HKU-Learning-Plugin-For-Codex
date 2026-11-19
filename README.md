# HIQS · HKU Information Query System

HIQS 帮助香港大学学生把 Moodle 课件、SIS 课程信息和 Class Planner 课表整理成可查证的学习资料。你可以问「这份作业什么时候交、占多少分、要求在哪里写的？」，也可以用同一批资料制作复习笔记、规划班别组合，或把已确认的截止日期加入 Apple 日历和提醒事项。

AI Agent 按 Skill 阅读和解释资料。Python 服务负责下载、检索、校验与保存。Notion 可用作课程工作台，Apple 日历和提醒事项可接收已确认且仍有效的日程与待办。也可以直接在本机只读查看器中打开课件和检查同步状态。

## 四个学习工作流

| 你可以用 HIQS 做什么 | Skill | MCP profile |
| --- | --- | --- |
| 查课表、考核、截止日期和占分，并回到原课程页面或课件核对出处。 | [课程信息](skills/hiqs-course-information/SKILL.md) | `course-information` |
| 从讲义和可用试题生成英文教材式笔记、题目对应表和快速复习资料。长任务可从本地检查点继续。 | [学习笔记](skills/hiqs-course-notes/SKILL.md) | `course-notes` |
| 同时比较 lecture、tutorial 和 lab 的完整组合，检查时间冲突和资格。实际选课由前台 Agent 在用户授权的候选范围内执行，并从 SIS 对账。 | [课程规划](skills/hiqs-course-planning/SKILL.md) | `course-planning` |
| 在 Notion 浏览课程档案、课件原件和笔记，并检查同步与文件上传结果。 | [Notion 工作台](skills/hiqs-notion-workspace/SKILL.md) | `notion-workspace` |

## 快速开始

准备 Python 3.11 或更新版本（需支持 SQLite FTS5），以及支持本地 stdio MCP 的 Agent。访问 HKU 受限资料时，需要有资料访问权限的 HKU 账户。

```bash
git clone https://github.com/Jerry6921/HSAS.git
cd HSAS
python3 -m venv .venv
.venv/bin/python -m pip install -c requirements.lock -e .
.venv/bin/python scripts/install_agent_skills.py
.venv/bin/hsas list-status
```

Skill 安装器默认使用 `$CODEX_HOME/skills`，未设置时使用 `~/.codex/skills`。安装后开启新的 Agent 会话。其他 Agent 可以通过 `--destination` 指定其技能目录，或按客户端的安装方式导入 [`skills/`](skills/)。

在 MCP 客户端添加一个 **stdio** 服务，将启动命令设为仓库中 `.venv/bin/hiqs-mcp` 的绝对路径，参数设为 `--profile course-information`。使用其他工作流时，从上表选择对应 profile。登录和原生权限配置可通过对应 CLI 命令操作，或在需要时由用户使用完整 MCP 工具面 `--profile full`。[MCP 工具分类](contracts/mcp-tool-profiles.json)

首次采集前安装 Chromium，并在打开的 HKU 登录页面亲自完成 SSO 和 MFA。

```bash
.venv/bin/python -m playwright install chromium
.venv/bin/hsas login
```

登录后，可以在 Agent 中发出第一个任务。

> 同步我有权限访问的本学期课程。先告诉我哪些来源更新成功，再整理本周的作业截止日期、占分和提交要求。每项附上可以回查的来源，标出还有哪些需要确认。

## 查看资料与配置同步

- **本机查看器**。运行 `.venv/bin/hsas serve`，在浏览器查看最新课件、原件与提取文本、来源是否过期，以及 Apple 日程是否已跟上课程事实。查看器只读，默认地址为 `http://127.0.0.1:8765`。[查看器设计](docs/adr/0002-local-viewer.md)
- **Notion**。可配置独立集成来同步课程档案和原件，并用 `.venv/bin/hsas notion check` 检查连接。笔记正文由 Agent 通过 Notion 连接器发布到对应课程页，随后读回核对。[Notion 配置](docs/notion-integration.md)
- **Apple 日历和提醒事项**。可在有 Swift 工具链、iCloud 账户和 EventKit 权限的 macOS 14+ 上设置。同步会在专用 HIQS 日历和提醒事项列表中读回核验本机写入。[Apple 配置与核验](docs/apple-integration.md)

## 信息如何被核对

采集器保留原文件及来源，并为 PDF、PPTX 和 DOCX 提取文本。检索命中尽量保留课程、活动、页码、幻灯片或表格位置。Agent 审阅变更后提交课程事实，服务校验并保存，通过读回核验记录处理进度。未知或冲突的日期、地点和要求会保留各自的状态。对于需要据此行动的截止日期或考试安排，可以沿引用回到校方页面核对。

浏览器会话、下载资料、事实库、笔记检查点和同步回执保存在本机私有运行目录。可用 `hsas list-status` 查看资料路径，或用 `HSAS_DATA_DIR` 指定独立的数据目录。向 Notion 或 Apple 发送的数据取决于你配置的连接与同步范围。第三方服务的实际核验日期与已知限制见 [集成记录](docs/integrations.md)。

## 开发与分发

```bash
.venv/bin/python -m pip install -c requirements.lock -e '.[dev]'
.venv/bin/python scripts/check_all.py
.venv/bin/python scripts/package_agent_skills.py --output dist/hiqs-agent-skills.zip
```

`check_all.py` 检查代码、已提交的接口合同和离线测试。ZIP 包包含可单独安装的产品 Skills。Skills 通过 MCP 调用 `HIQSPort` 提供的本地 Python 服务，CLI 与只读查看器共用这些服务。[架构](ARCHITECTURE.md) · [贡献指南](CONTRIBUTING.md) · [更新记录](CHANGELOG.md)

## 许可证

HIQS 软件采用 [PolyForm Noncommercial License 1.0.0](LICENSE)。经课程平台获取的材料仍适用原有版权和使用条件。
