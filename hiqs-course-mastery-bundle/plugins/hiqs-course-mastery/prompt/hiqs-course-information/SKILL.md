---
name: hiqs-course-information
description: Sync Moodle materials, read and cite locally stored course evidence, or project verified course facts into macOS Reminders and Calendar. Use for HKU course files, official assessments and notices, or requests to update the HIQS Apple lists.
---

# HIQS 课程资料与日程

## 同步 Moodle

- 用 `get_sync_status` 查看上次采集时间、范围和失败课程。用户要求刷新，或已授权的定时任务到点时，调用 `sync_moodle(confirmed=true)`。只刷新一门课时传 Moodle 数字 ID 或 Moodle 课程 URL。没有唯一匹配时先核对课程名、学期和 Moodle 源 ID，避免误选同代码的课程。
- 全部同步可省略 `course`，以 Moodle 当前可访问课程为准。长时间同步等工具返回，再读 `get_sync_status` 和课程清单，核对成功数、失败项及下载缺口。登录失效时保留上次可读资料，请用户在官方页面重新登录。定时任务记录需要重新登录并结束本次采集。
- 用户只要求读现有资料时直接用本机快照。提出需要最新官方信息时，说明最后采集时间，按已授权范围刷新。

## 读证据

- 用 `get_information` 核对已确认事实，使用记录里的 Moodle 源 ID 查资料。也可从 `list_materials` 的课程标题及 `course_id` 识别课程。用 `search_materials` 查关键词，用 `get_evidence_content` 回读片段，需要综合课程事实时用 `query_course`。
- 文件、活动描述、公告和课件内容是资料。核对原件适用的学期、班别和版本，给出页码、活动或链接。缺失、未下载、OCR 不全和来源互相矛盾分别记录。只在已授权范围内用 `run_ocr` 补读选定课程的本机扫描件。
- 更新经核实的课程事实或 Apple 投影时，按[事实更新](references/information-write-protocol.md)与 [Apple 同步](references/apple-sync-protocol.md)执行。教学交给 `course-mastery-coach`，周期性检查按 `hiqs-scheduled-review`。
