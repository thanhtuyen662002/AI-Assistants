# AI-Assistants — Bộ não thứ hai cho Agent CSKH

Kế hoạch triển khai agent chăm sóc khách hàng trên **Zalo Official Account** và **WhatsApp Business Platform / Cloud API**, dùng chung bộ nhớ có kiểm soát, tri thức doanh nghiệp và công cụ nghiệp vụ.

> **Trạng thái: PLANNING BASELINE — chưa có ứng dụng chạy được.** Đây là bộ đặc tả để các coding agent triển khai; không phải thông báo đã tích hợp, kiểm thử hay đưa sản phẩm lên production.
>
> **Giới hạn nguồn:** hai clip TikTok do chủ dự án cung cấp chưa truy cập được nội dung hình/âm thanh/phụ đề trong phiên lập kế hoạch. Không có kết luận nào được gán là rút ra từ hai clip. Xem [sổ nguồn](docs/00-source-review.md). Kiến trúc bên dưới là đề xuất độc lập, dựa trên yêu cầu và tài liệu chính thức đã kiểm tra ngày **2026-10-09**.

## Bắt đầu ở đâu?

1. Agent điều phối đọc [AGENTS.md](AGENTS.md), [kế hoạch giao việc](docs/06-delivery-plan.md) và [prompt giao việc](docs/08-agent-prompts.md).
2. Các agent đọc [kiến trúc](docs/02-architecture.md), [thiết kế bộ nhớ](docs/03-second-brain.md), [hợp đồng dữ liệu/API](docs/05-data-and-api-contracts.md), sau đó nhận task theo dependency; không tự mở rộng phạm vi.
3. Chủ dự án xử lý các điều kiện bên ngoài trong [checklist vận hành](docs/09-owner-checklist-and-runbook.md). Thiếu credentials không chặn phát triển bằng mock nhưng chặn nghiệm thu tích hợp thật.

## Bản đồ tài liệu

| Tài liệu | Nội dung |
|---|---|
| [00 — Source review](docs/00-source-review.md) | Hai clip, tình trạng kiểm chứng, nguồn chính thức và các điểm chưa xác minh |
| [01 — Product & scope](docs/01-product-and-scope.md) | Use case, phạm vi MVP/V1, giả định, mục tiêu và giới hạn |
| [02 — Architecture](docs/02-architecture.md) | Stack đề xuất, luồng xử lý, queue/outbox, ranh giới module, quyết định kiến trúc |
| [03 — Second brain](docs/03-second-brain.md) | Các lớp bộ nhớ, ingest/RAG, nhớ–quên–sửa, danh tính đa kênh, học có duyệt |
| [04 — Channels](docs/04-channel-integrations.md) | Zalo OA, WhatsApp, webhook, xác thực, điều kiện gửi và ngân sách |
| [05 — Data & API](docs/05-data-and-api-contracts.md) | Mô hình bảng, sự kiện, interface, endpoint, state machine và tool safety |
| [06 — Delivery plan](docs/06-delivery-plan.md) | Backlog có ID, vai trò, phụ thuộc, đầu ra và tiêu chí nghiệm thu |
| [07 — Quality & security](docs/07-quality-security-operations.md) | Test, bảo mật, quan sát, đo chất lượng, release gate và rollback |
| [08 — Agent prompts](docs/08-agent-prompts.md) | Prompt điều phối, prompt theo vai trò và mẫu báo cáo bàn giao |
| [09 — Owner & runbook](docs/09-owner-checklist-and-runbook.md) | Checklist tài khoản/dữ liệu, cấu hình, rollout, chi phí và xử lý sự cố |
| [contracts/](contracts/) | JSON Schema nền cho sự kiện chuẩn hóa và quyết định của agent |
| [planning/backlog.json](planning/backlog.json) | Task DAG ở dạng máy đọc được; nội dung chi tiết nằm trong tài liệu 06 |
| [evals/golden-cases.jsonl](evals/golden-cases.jsonl) | Các tình huống kiểm thử tổng hợp ban đầu, không chứa dữ liệu khách thật |

## Đích sản phẩm

```text
Zalo OA / WhatsApp
        ↓
Webhook xác thực → durable inbox → queue
        ↓
Nhận diện khách + kiểm tra quyền + trạng thái human handoff
        ↓
Tri thức đã duyệt + bộ nhớ riêng của khách + dữ liệu nghiệp vụ sống
        ↓
Agent đề xuất → kiểm chứng nguồn / hành động / quy tắc kênh
        ↓
Transactional outbox → sender → trạng thái gửi / chuyển nhân viên
```

Bộ não gồm: ngữ cảnh phiên, tri thức doanh nghiệp, hồ sơ khách có nguồn, lịch sử xử lý và playbook có phiên bản. Agent **không** tự biến lời nói của khách thành chính sách công ty; **không** dùng ký ức thay cho dữ liệu đơn hàng hiện tại; **không** đọc bộ nhớ của khách khác.

## Lựa chọn mặc định để triển khai

- Một TypeScript monorepo: Next.js cho màn hình quản trị, Fastify cho API, Node.js worker; PostgreSQL + pgvector, Redis + BullMQ, object storage tương thích S3.
- Một agent CSKH có workflow xác định và tool allowlist; không xây “đội agent tự do” ở runtime MVP. Các coding agent được chia vai trò để xây sản phẩm song song.
- Chỉ API chính thức. Không tự động hóa tài khoản Zalo cá nhân, không điều khiển WhatsApp Web bằng session/QR.
- Một doanh nghiệp pilot trước; phân vùng tenant và khách hàng từ đầu. Chưa xây billing SaaS hoặc onboarding self-service.
- Giá, tồn kho, đơn hàng qua API nguồn. Tri thức ổn định mới đưa vào RAG. Hành động ghi có phê duyệt và idempotency.

Các lựa chọn trên là **quyết định thiết kế đề xuất**, không phải công nghệ đã tồn tại trong repo hay được xác nhận từ clip. Agent nền tảng phải pin phiên bản được hỗ trợ, ghi lockfile và kiểm thử tương thích khi scaffold.

## An toàn với repo công khai

Repo đang public tại thời điểm lập kế hoạch. Chỉ commit tài liệu, code, schema và dữ liệu giả. Không đưa token OA/Meta, khóa LLM, transcript khách, số điện thoại, đơn hàng thật hoặc tài liệu nội bộ vào Git. Credentials nhập qua secret manager của môi trường triển khai.

## Điều kiện hoàn thành

Đọc [release gates](docs/07-quality-security-operations.md) trước khi báo DONE. Gửi được một tin nhắn demo không đồng nghĩa sản phẩm hoàn thiện. Phải có kiểm thử tách tenant/khách, ngừng bot khi nhân viên tiếp quản, chống gửi trùng, chính sách kênh, trích nguồn, xóa bộ nhớ và rollback.

Bắt đầu với **SB-01, SB-02, SB-03**. **SB-00** đối chiếu hai clip chạy song song; chưa được đánh dấu hoàn thành khi chưa có nội dung thực tế hoặc quyết định miễn đối chiếu từ chủ dự án.
