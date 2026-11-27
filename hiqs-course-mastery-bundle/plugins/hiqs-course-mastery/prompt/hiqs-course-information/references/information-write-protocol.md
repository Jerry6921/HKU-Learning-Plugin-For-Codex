# 更新已确认课程事实

1. 用 `get_information` 核对现有记录。复核 Moodle 变化时，用 `get_pending_changes` 获取目标课程的 review batch，按 full 或 incremental 范围读原件。从邮件核实的事项按 [HKU 邮箱查阅](hku-email.md) 回读原通知。
2. 保留稳定的 `course_id`、Moodle 源 ID 和 `item_id`。按 `get_information_update_schema` 填完整的新版本记录，复制仍有效的原字段。省略整条记录会保留现有事实。对更新的课程，在 `material_sections` 保留现有 Moodle 归档别名，并按 `list_materials` 整理完整当前清单。保持相同的本机路径或源 URL，每份当前资料归入一个小节。
3. 给截止时间、开始结束、地点及重复安排保存可回查的来源。只知道日期时用 `due_on`，知道具体时点时用 `due_at`。仅在来源核实且适用时使用 `date_status: confirmed`，冲突和未知值如实记录，重复规则例外附证据。
4. 调用 `validate_information_update`，检查 `quality_audit` 和 `ready_to_apply`。向用户或定时任务报告建议变更与出处。只有覆盖该变更的授权才可调用 `apply_information_update(confirmed=true)`。已完整复核的 Moodle batch 可随更新传入 `review_batches.moodle`。若 batch 已过时，重新导出并回读证据。
5. 已完整复核且确定没有事实变化的 batch，在授权范围内用 `acknowledge_pending_changes` 并传 `reviewed_no_information_change=true`、`confirmed=true`。未复核的资料保持待处理。
6. 用 `get_information` 回读。Canonical `information.json` 通过现有验证和写入工具维护，内容只记录课程事实。
