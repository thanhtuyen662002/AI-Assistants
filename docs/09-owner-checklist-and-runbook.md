# 09 — Owner checklist và đường vận hành v3

[Đầu vào cần chốt](../MASTER_PLAN.md#inputs), [runbook và chi phí](../MASTER_PLAN.md#operations), [release checks](07-quality-security-operations.md). Đây là checklist giao việc, không xác nhận đã có credentials hoặc hạ tầng.

## Đầu vào tối thiểu

| Input | Người quyết định | Khi chưa có |
|---|---|---|
| Ngành hàng, 5 hành trình, câu nào được auto | Business owner + support lead | Synthetic domain; không bịa chính sách thật |
| 10–20 FAQ/tài liệu có owner/ngày hiệu lực/quyền dùng | Knowledge owner | Demo vault và nguồn giả |
| CRM/order/catalog/API scopes | Business/technical owner | Mock typed adapter, live evidence blocked |
| Zalo account/recipient đồng ý test và risk review | Account owner | Không login; SB-27 audit/mock trước, manual fallback |
| Loại account WhatsApp và Cloud API path | Account owner | Keep assumption, không tự đổi sang WhatsApp Web |
| Nhân viên trực, giờ làm, SLA/handoff ngoài giờ | Support lead | Không chạy khách thật khi thiếu tuyến hỗ trợ |
| Model/provider, xử lý dữ liệu, retention và spend cap | Owner/privacy/operations | Fake model, unknown budget/rates không auto-send |
| Domain/hosting/secrets/backup approvals | Operations + owner | Local scripts/deployment templates; không mua/provision |

Thông tin đã chốt như Zalo cá nhân không hỏi lại. Credentials nhập secret manager, không commit và không yêu cầu dán vào chat. Trạng thái input phải gắn owner/deadline do owner chốt, không tự hứa lịch.

## Runbook tóm tắt

Suspected leak/unauthorized action: OFF phạm vi ảnh hưởng, bảo toàn audit tối thiểu, incident owner điều tra, không gửi PII trong alert. Session restricted/revoked/collision: pause bridge sender, owner theo flow chính thức; không loop né chặn. Unresolved personal gap: không auto resume sau reconnect, đối soát/đánh dấu coverage thật.

Queue lỗi: durable receipts/spool còn trong limits, dispatcher phục hồi dedup; không drop ACKed events. Spool đầy: degraded và auto stop, alert metadata. Send timeout có thể accepted: unknown/reconcile, không retry mù. KB sai: revoke registry/epoch, chặn intents dùng nguồn cũ; publish bản sửa sau review/eval. Human takeover race: OFF bot scope, kiểm ownership và sender arbitration trước bật lại.

Deletion failure: tombstone chặn đọc trước, retry purge có evidence. Backup restore: network cô lập, senders OFF, apply suppression/ACL hiện tại trước reconnect. Rollback app giữ schema compatibility; rollback wiki không hồi sinh nguồn đã revoke/xóa. Kill switch không hứa thu hồi tin đã in-flight.

## Trước mở auto

Gate đúng kênh phải pass, owner sign-off theo release/cohort, có staff nhận handoff, cost cap và kill switch được drill. Manual/bridge-copilot không tự chuyển auto do chạy lâu hoặc vì hết sprint. Tăng cohort phải review dữ liệu đủ mẫu, không theo lịch tự động. Owner brief SB-32 ban đầu là nút tạo báo cáo; lịch chỉ khi có yêu cầu mới rõ ràng.
