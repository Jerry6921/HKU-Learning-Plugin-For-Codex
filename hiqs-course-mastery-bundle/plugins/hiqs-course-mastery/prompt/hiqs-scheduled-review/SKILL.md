---
name: hiqs-scheduled-review
description: Run a daily silent check of Moodle and connected HKU Outlook email with immediate alerts for new actionable course items, or produce a weekly digest of confirmed course deadlines that are still incomplete.
---

# HIQS 定时检查

由宿主按香港时间触发。根据任务选择每日同步或每周汇总。课程范围和写入授权以定时任务的设置为准。

## 每日静默检查

1. 每天运行一次。先用 `list_materials` 和 `get_information` 核对基线。按 `hiqs-course-information` 同步授权范围内的 Moodle 课程，等 `sync_moodle` 返回后读 `get_sync_status`。在每日任务也授权查阅 HKU 邮箱时，按 [HKU 邮箱查阅](../hiqs-course-information/references/hku-email.md) 独立检查当前课程的邮件。
2. Moodle 侧对照同步前后的清单，读新增或改动的活动、公告和相关附件。邮件侧从上次成功检查邮箱的时间开始搜索。首次运行或无记录时，检查本次计划运行前 24 小时至今；已知某轮遗漏时回查遗漏时段。将时间范围和课程范围一起用于搜索。
3. 查找首次出现的作业、测验、考试、报名等需要处理的事项。用 Moodle 活动 ID、已有 `item_id` 或课程与事项的对应关系合并两个来源。根据此前可见的通知记录判断是否已提示。只有来源增加、内容重复或同一邮件线程转发时沿用原事项，引用两个来源。
4. 核实有新增事项时，在本次运行立即通知。逐项给出课程、事项、截止时间和出处。官方已宣布但未给日期时标记「日期待确认」。两处通知冲突时标明差异，有明确且适用的官方更正时以更正为准。授权范围均检查成功且没有新增事项时，静默结束。
5. 登录失效、邮箱未连接、部分采集失败或无法读到关键证据时，继续检查可用的来源和课程。需要用户介入时，说明受影响的来源和所需操作。记录实际查阅范围及未查明的部分，供后续补查。
6. 事实写入和 Apple 投影分别按 `hiqs-course-information` 的校验、授权与读回流程执行。通知可直接引用本轮核实的来源。

## 每周待完成 due 汇总

1. 用 `get_information` 读取已确认的课程事项。选出 `date_status: confirmed` 且有 `due_at` 或 `due_on` 的待办。保留确实需要完成的作业、报告和其他任务，按资料核实其截止日期与来源。
2. 把这些课程事项的 `item_id` 交给 `get_apple_reminder_completion`。完成状态为 `false` 的条目进入汇总，为 `true` 的条目略过。状态为 `null` 的条目注明待核实。工具优先读取 HIQS 提醒事项，并用已有归档补核已移出的过期项。权限、列表配置或读取失败时注明原因。
3. 按香港时间先列逾期未完成，再按截止时间列其余未完成事项。每项给出课程、事项、截止日期或时间及来源。只有日期时保留日期精度。每周输出一次，覆盖完整且没有未完成事项时简短报告。若核验不全，附待核实项及原因。
