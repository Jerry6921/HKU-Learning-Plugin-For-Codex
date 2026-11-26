---
name: hiqs-scheduled-review
description: Run a daily silent Moodle sync with immediate alerts for new actionable course items, or produce a weekly digest of confirmed course deadlines that are still incomplete.
---

# HIQS 定时检查

由宿主按香港时间触发。根据任务选择每日同步或每周汇总。课程范围和写入授权以定时任务的设置为准。

## 每日静默同步

1. 每天运行一次。用 `list_materials` 和 `get_information` 确立当前资料和事项的基线。按 `hiqs-course-information` 同步授权范围内的 Moodle 课程，等 `sync_moodle` 返回，再读 `get_sync_status`。
2. 检查本轮成功更新的课程。对照同步前的清单、已知事项和本轮来源变化，回读新增或改动的活动、公告及已下载的附件。找出首次出现的作业、测验、考试、报名或其他需要处理的课程事项。用 Moodle 活动 ID 或已有的 `item_id` 合并重复来源。
3. 核实有新增事项时，在本次运行立即通知。逐项给出课程、事项、已核实的截止日期或时间及来源。官方已宣布事项但未给日期时标记「日期待确认」。核实后没有新增事项时，本轮静默结束。
4. 登录失效或部分同步失败时保留可用资料，检查已成功的课程。有问题需要用户介入时，说明受影响的课程和所需操作。把成功检查的范围与尚未查明的范围说清楚。
5. 日期事实和 Apple 投影分别按 `hiqs-course-information` 的校验、授权与读回流程处理。通知可直接引用本轮核实的来源。

## 每周待完成 due 汇总

1. 用 `get_information` 读取已确认的课程事项。选出 `date_status: confirmed` 且有 `due_at` 或 `due_on` 的待办。保留确实需要完成的作业、报告和其他任务，按资料核实其截止日期与来源。
2. 把这些课程事项的 `item_id` 交给 `get_apple_reminder_completion`。完成状态为 `false` 的条目进入汇总，为 `true` 的条目略过。状态为 `null` 的条目注明待核实。工具优先读取 HIQS 提醒事项，并用已有归档补核已移出的过期项。权限、列表配置或读取失败时注明原因。
3. 按香港时间先列逾期未完成，再按截止时间列其余未完成事项。每项给出课程、事项、截止日期或时间及来源。只有日期时保留日期精度。每周输出一次，覆盖完整且没有未完成事项时简短报告。若核验不全，附待核实项及原因。
