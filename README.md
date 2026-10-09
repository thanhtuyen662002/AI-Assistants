# AI-Assistants — Bộ não thứ hai cho Agent CSKH

**Phạm vi đã được chủ dự án đính chính: dùng tài khoản Zalo cá nhân đang sử dụng, KHÔNG phải Zalo Official Account.** WhatsApp giữ phương án Business Platform / Cloud API trong baseline; loại tài khoản WhatsApp chưa được chủ dự án xác nhận riêng.

> **PLANNING — chưa có ứng dụng, kết nối tài khoản hoặc deployment chạy thật.** Bản sửa ngày 2026-10-09 thay thiết kế Zalo OA trước đây bằng Zalo Personal Bridge. Không cần tạo OA, Zalo App hay lấy OA token để triển khai nhánh Zalo này.
>
> **Cảnh báo:** connector Zalo cá nhân ứng viên `zca-js` là thư viện không chính thức, có rủi ro tài khoản bị hạn chế/khóa. Đăng nhập QR hoặc nhân viên duyệt tin không biến connector thành API được Zalo chấp thuận. Không hứa tránh khóa tài khoản. Đọc [quyết định và nguồn](docs/10-zalo-personal-decision.md).
>
> Hai clip TikTok vẫn chưa lấy được nội dung để đối chiếu. Thiết kế là đề xuất độc lập; không có kết luận được gán cho clip. SB-00 vẫn blocked.

## Bắt đầu

Agent điều phối đọc [AGENTS.md](AGENTS.md), [quyết định Zalo cá nhân](docs/10-zalo-personal-decision.md), [backlog](docs/06-delivery-plan.md) và [prompt giao việc](docs/08-agent-prompts.md). Bắt đầu SB-01/SB-02; sau contracts SB-03, làm **SB-27 — kiểm chứng Zalo Personal** sớm trước adapter SB-07. Các phần bộ nhớ, CRM và console tiếp tục bằng mock khi chưa có account test.

## Bản đồ tài liệu

| Tài liệu | Nội dung |
|---|---|
| [00 — Sources](docs/00-source-review.md) | Nguồn video còn thiếu; tài liệu bên ngoài và mức kiểm chứng |
| [01 — Scope](docs/01-product-and-scope.md) | MVP, giới hạn dữ liệu cá nhân, tự động hóa và mục tiêu |
| [02 — Architecture](docs/02-architecture.md) | Personal bridge chạy thường trực, WhatsApp webhook, inbox/outbox, runtime |
| [03 — Second brain](docs/03-second-brain.md) | Các lớp bộ nhớ, RAG, sửa/xóa, identity, học có duyệt |
| [04 — Channels](docs/04-channel-integrations.md) | QR/session/listener Zalo cá nhân; WhatsApp Cloud API; policy riêng |
| [05 — Contracts](docs/05-data-and-api-contracts.md) | Dữ liệu, API, normalized event v2 và tools |
| [06 — Delivery](docs/06-delivery-plan.md) | 28 task, vai trò, phụ thuộc và acceptance |
| [07 — Quality](docs/07-quality-security-operations.md) | Kiểm thử, bảo mật, account risk, release gates |
| [08 — Prompts](docs/08-agent-prompts.md) | Prompt triển khai/review cho coding agents |
| [09 — Operations](docs/09-owner-checklist-and-runbook.md) | Tài khoản, bảo vệ session, rollout, rollback, vận hành |
| [10 — Personal decision](docs/10-zalo-personal-decision.md) | Đính chính yêu cầu, lựa chọn connector và giới hạn đã xác minh |
| [contracts/](contracts/) | Event v2 hiện hành; decision v1; event v1 chỉ lưu lịch sử, không dùng cho personal |
| [planning/backlog.json](planning/backlog.json) | Task DAG máy đọc được |
| [evals/golden-cases.jsonl](evals/golden-cases.jsonl) | Seed test tổng hợp; chưa phải test application đã chạy |

## Kiến trúc đích

```text
Zalo cá nhân → Personal Bridge (QR / session / listener)
                                  ↓ authenticated internal ingest
WhatsApp Cloud API → verified webhook
                                  ↓
                    durable inbox → queue
                                  ↓
   Phân quyền + khách hàng + trạng thái nhân viên tiếp quản
                                  ↓
    Tri thức đã duyệt + ký ức riêng khách + dữ liệu CRM mới
                                  ↓
             Agent đề xuất → validator → outbox
                                  ↓
       Channel gates → bridge sender / WhatsApp sender
```

Nền tảng đề xuất: TypeScript monorepo, Next.js console, Fastify API, Node.js worker và **dịch vụ bridge chạy thường trực**, PostgreSQL + pgvector, Redis + BullMQ, object storage S3-compatible. Không đặt listener Zalo trong function ngắn hạn. Adapter độc lập để thay connector mà không thay bộ não.

Bộ nhớ gồm ngữ cảnh phiên, KB doanh nghiệp, facts riêng của khách, lịch sử case và playbook. Giá/tồn kho/đơn hàng lấy API nguồn, không dùng vector như dữ liệu thời gian thực. Không tự gộp khách đa kênh, không học chính sách từ lời khách, không đọc chéo người, không tự hoàn tiền.

## Giới hạn bắt buộc cho Zalo cá nhân

Chỉ tài khoản do chủ dự án sở hữu/ủy quyền. Chủ tài khoản tự quét QR trên giao diện quản trị được bảo vệ; không gửi mật khẩu, OTP, cookie hay QR đăng nhập vào chat/GitHub. Chỉ các cuộc trò chuyện CSKH 1:1 đã được chọn; mặc định không nhập toàn bộ danh bạ, nhóm, lịch sử và tin gia đình/bạn bè vào bộ nhớ.

Một listener đang hoạt động cho mỗi tài khoản; mất phiên/xung đột/nghi hạn chế thì dừng gửi và báo người vận hành. Không giả định nhận lại đủ tin lúc offline. Nếu chưa chứng minh quan sát được tin nhân viên gửi từ thiết bị khác, không bật AUTO_LOW_RISK trên tài khoản sử dụng song song ngoài console.

Không áp cửa sổ/biểu phí OA cho tài khoản cá nhân; cũng không coi là gửi không giới hạn. Không spam, tự động kết bạn hàng loạt, quét số điện thoại, vượt CAPTCHA, đổi tài khoản/proxy để né chặn. Owner chấp nhận rủi ro không đồng nghĩa nền tảng chấp thuận.

## Trạng thái và an toàn

Repo public: chỉ code/tài liệu/dữ liệu giả. Secrets/session/QR/transcript thật ở hạ tầng riêng có kiểm soát. `ZALO_PERSONAL_ENABLED=false` mặc định; chưa có login, live send hoặc provider test trong phiên sửa plan. Nhánh manual copilot dùng AI soạn nháp và người gửi bằng ứng dụng Zalo chính thức là phương án dự phòng khi không dùng bridge.
