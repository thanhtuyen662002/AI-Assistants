# 09 — Checklist và runbook: Zalo cá nhân

## Trạng thái

Chỉ plan/spec, chưa runtime/credentials/deployment. Chủ dự án đã xác nhận personal Zalo: **không hỏi OA ID/App/OA token nữa**. WhatsApp giữ Cloud API giả định. Không có automation/agent được tự khởi chạy bởi tài liệu. Hai clip vẫn thiếu nội dung cho SB-00.

## Input registry

| Đầu vào | Việc cần làm / gate |
|---|---|
| Account Zalo cá nhân do chủ dự án sở hữu | Owner chủ động cho phép controlled test, xem unofficial/account-risk/terms; tự scan QR, không gửi password/OTP/cookie qua chat/Git |
| Máy/server bridge và quyền vận hành | Long-running Node/container, secret storage, encrypted volume/spool, TLS/internal service identity, owner shutdown/revoke |
| Các thread CSKH được xử lý | Owner chọn allowlist/purpose; mặc định nhóm/bạn bè/gia đình/history không ingest; không dump toàn bộ danh bạ |
| Cách chủ tài khoản dùng mobile/PC/Web | SB-27 test listener collision/self-event visibility; chưa biết thì không auto ngoài console; đây là capability cần test, không hỏi lại loại account |
| Ngành hàng/KB/policy/CRM | Owner duyệt nguồn/hiệu lực; mock synthetic khi thiếu, không bịa giá/order thật |
| Meta app/WABA/phone/scopes | Official WhatsApp test/live setup; không suy từ personal Zalo sang WhatsApp Web |
| Rates/budget/model/privacy | WhatsApp rate card hiện hành; model/data processing/retention/region; per-account budget; unknown cost không 0 |
| Support staffing/giờ làm/SLA | Handoff thực sự có người nhận, outside-hours route và manual fallback |
| Retention/consent/deletion | Quyền xử lý chat CSKH và dữ liệu gửi model; không đồng ý xử lý mọi tin riêng chỉ vì owner QR login |
| Video/transcript hợp lệ | SB-00 đối chiếu; không ngăn module độc lập nhưng source caveat còn giữ |

## Setup local và controlled account

Local mặc định mock, personal enabled=false, auto OFF; DB runtime least privilege, secret refs, synthetic KB/order/thread. Pin versions/lockfile; lint/typecheck/contracts/build khi scaffold có thật. Personal bridge không live login từ CI. Auth owner/admin bảo vệ QR screen, no-store/TTL và logs không secret.

SB-27 review upstream/dependencies/risk trước real QR; chủ account tự scan đúng màn hình do mình kiểm soát. Chọn một account được phép và recipients đồng ý; không tự động yêu cầu tạo tài khoản giả hoặc chuyển hàng loạt account. Người dùng vẫn giữ quyền tắt bridge/revoke session. Không scale nhiều listener cùng account; test mới gây session collision phải được phối hợp với owner.

Sau login verify đúng account UID/binding, thread allowlist, own-message observation, actual receive/send IDs, revoke, network/process errors, gap reporting. Không gọi đây là sandbox do Zalo cấp. Không chạy backend stress-test 10 msg/s vào Zalo thật; toàn bộ load/chaos dùng mocks trừ vài kiểm chứng account được duyệt.

WhatsApp staging riêng với test number/recipient/template, official webhook signature/capability/rates. Chưa có credentials thì mock-only chứ không skipped=passed.

## Rollout

OFF/SHADOW trước; COPILOT do nhân viên duyệt nhưng **nếu dùng personal bridge vẫn có account risk**. Manual copilot không dùng bridge: người tự cung cấp đoạn chat cần thiết, xem draft/source, tự gửi app chính thức; không claim auto-sync.

AUTO_LOW_RISK chỉ sau QA/account risk/terms/privacy/capability sign-off, thread+intent allowlist và owner explicit enable. Gap chưa đối soát, self events không quan sát chắc trong cách dùng nhiều client, expired session, account challenge/restriction hoặc stale fencing epoch đều chặn auto. Reconnect không tự resume. Canary 5%→25%→100% hội thoại **đủ điều kiện** là đề xuất, không lịch tự chạy hoặc 100% mọi hoạt động account.

Kill switch per global/tenant/binding, kiểm cả sender và bridge. Pending cancel, in-flight không hứa thu hồi. Khi disconnect/revoke: fence epoch, stop listener, revoke bridge identity, purge QR/session/cached credential, chặn queued sends. Dữ liệu CSKH lưu theo retention/verification, không xóa audit cần thiết tùy tiện. Owner acceptance không là Zalo chấp thuận hoặc cam kết no-ban.

## Chi phí

Total = infrastructure + model tokens + embeddings/rerank + storage/backup/egress/observability + verified channel/BSP/tax costs nếu có. Personal không kế thừa biểu phí OA nhưng không suy mọi chi phí=0. Rate unavailable=unknown; budget reservation và actual reconciliation tách. Soft cap 80%/hard cap theo owner approve; không chuyển model chưa được duyệt hoặc giảm safety để tiết kiệm.

Input: turns/segments/tokens/tools/cases/KB changes, market, rate effective dates/currency, hardware and support capacity. Policy limits do platform và app budget khác nhau; tốc độ chậm không bảo đảm tránh khóa. Không thêm anti-detection/proxy rotation/account farming để bảo vệ doanh thu.

## Sự cố và phản ứng

| Sự cố | Phản ứng |
|---|---|
| Account cảnh báo/challenge/restricted | Pause bridge/send, báo owner; dùng quy trình chính thức hoặc manual copilot, không né xác thực/chặn |
| Owner mở Zalo Web làm listener dừng | Mark session_conflict/coverage gap, pause auto, phối hợp owner; không reconnect loop giành phiên |
| Session expired/revoked | Fence generation/epoch, stop sends, owner QR lại hợp lệ; không log cookie hoặc tự reset state |
| Mobile/PC manual reply không xuất hiện | Disable AUTO cho use mode đó; manual takeover trước gửi, kiểm capability, không hứa bot biết hết |
| Stale lease/2 listener | Reject old epoch ingest/send, stop instance lỗi; active/passive recovery có kiểm soát |
| DB/queue down | Encrypted bounded spool/durable inbox; metrics/gap, recover dedup; spool full báo lỗi không âm thầm mất |
| Listener offline/gap | Đối soát capability/history nếu có; thiếu evidence giữ gap, no auto-reply historical messages |
| Outbox unknown | Không retry mù; đối soát IDs/status/manual, audit kết quả |
| KB sai hoặc privacy leak | OFF affected intents/account; revoke nguồn/credentials khi cần; minimal audit, incident owner; no transcripts trong alert |
| Delete/purge lỗi | Tombstone chặn đọc ngay; retry purge trong DB/vector/cache/spool/jobs/objects; restore suppression |
| Model outage/cost cap | Bounded fallback approved hoặc draft/handoff; không bịa câu trả lời/source |
| Deploy lỗi | Auto OFF, rollback compatible image/config; không reverse migration phá dữ liệu |

## Restore và release evidence

RPO≤24h/RTO≤4h là mục tiêu pilot chưa đo. Backup DB/objects/spool cần thiết mã hóa, retention/key recovery tách quyền. Restore cô lập, sender/listener OFF; áp deletion suppression trước connect, không replay send backlog hàng loạt. Không khôi phục session đã revoked từ backup; owner reauthorize khi cần.

Bàn giao: commit/image/model/prompt/policy/KB versions; real command/test evidence; personal capability+account risk+terms record, QR/session redaction, self-event/gap tests, WhatsApp verification/rates, purge/restore/kill switch/UAT và support owner. Dữ liệu thật không ở repo public. Chưa đạt thì báo cụ thể MOCK_ONLY/REAL_ACCOUNT_BLOCKED, không production-ready.
