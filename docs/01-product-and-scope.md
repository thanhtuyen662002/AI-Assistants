# 01 — Phạm vi hiện hành v3

Nguồn quyết định: [MASTER_PLAN §1](../MASTER_PLAN.md#scope), [đầu vào owner](../MASTER_PLAN.md#inputs). Trang này thay baseline cũ; không dùng nội dung OA trong lịch sử Git làm yêu cầu hiện hành.

Zalo cá nhân đã xác nhận. WhatsApp Cloud API chưa được xác nhận loại tài khoản; thiếu thông tin thì dùng mock, không tự chuyển loại account. Một doanh nghiệp pilot, text CSKH 1:1, tiếng Việt.

MVP: FAQ có nguồn, preference riêng từng khách, tra đơn read-only có xác minh, ticket idempotent, handoff dừng bot; có workflow nạp/sửa/duyệt/publish wiki. Tri thức doanh nghiệp khác dữ liệu riêng của khách; không đưa transcript vào shared wiki.

Voice/OCR, nhóm/bulk marketing, graph database riêng, autonomous runtime multi-agent, fine-tune chat khách, hoàn tiền tự động và billing SaaS ngoài MVP. SB-19/26/32 là V1 tùy chọn; chỉ bật feature khi acceptance riêng đạt.

Các mục tiêu chất lượng ở [release gates](../planning/release-gates.json) là mục tiêu chưa đo, không SLA hoặc xác suất thành công đã chứng minh. Manual copilot, bridge-copilot, auto và mock là trạng thái khác nhau, phải báo đúng.
