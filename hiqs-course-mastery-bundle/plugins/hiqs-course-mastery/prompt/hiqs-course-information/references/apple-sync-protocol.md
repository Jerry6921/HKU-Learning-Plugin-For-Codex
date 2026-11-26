# 同步 Apple 提醒事项与日历

- 用 `get_apple_sync_status` 查现有连接和回执。首次连接由用户在终端执行 `hsas apple connect` 并完成 macOS 授权。
- 用 `get_apple_sync_projection` 预览已确认且当前有效的课程事实。检查计划的新增、更新与已不符合条件的 HIQS 管理记录。只有授权覆盖本次投影时才调用 `sync_apple(confirmed=true)`。
- 核对回执的 `status`、`verification.status` 和 `matched/expected`。分别报告本机持久化验证和 iCloud 跨设备可见性。部分失败先看回执再决定安全重试。
