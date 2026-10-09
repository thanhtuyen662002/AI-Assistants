# AI-Assistants — Bộ não thứ hai cho CSKH

**Kế hoạch hợp nhất v3 — 2026-10-09.** Zalo là **tài khoản cá nhân của chủ dự án, không phải OA**. WhatsApp Cloud API là phương án thiết kế chưa được xác nhận loại tài khoản. Không đổi kênh của người dùng để né khó khăn kỹ thuật.

## Bắt đầu tại đây

1. Đọc [MASTER_PLAN.md](MASTER_PLAN.md): phạm vi, kiến trúc hợp nhất, thứ tự làm, điều kiện nghiệm thu và đường dự phòng.
2. Coding agent đọc [AGENTS.md](AGENTS.md), nhận đúng task trong [backlog](planning/backlog.json), rồi đọc tài liệu chuyên môn của task. Không nạp mọi tài liệu vào mỗi phiên.
3. Agent tri thức đọc [hợp đồng wiki](docs/11-wiki-contract.md) và mở [vault mẫu](examples/brain-demo/) bằng Obsidian hoặc trình soạn thảo Markdown.
4. Chạy kiểm tra tài sản kế hoạch theo [hướng dẫn giao việc](docs/08-agent-prompts.md). Đây không phải kiểm thử ứng dụng production.

## Thiết kế hợp nhất

```text
Tài liệu gốc / Clippings được phép
       ↓ nạp và chuẩn hóa, nguồn gốc giữ nguyên
Wiki liên kết: sources / entities / concepts / analysis / playbooks
       ↓ bản đề xuất → kiểm tra → người duyệt → published release
Chỉ mục tìm kiếm có thể dựng lại + nguồn kiểm chứng
       ↓
Agent CSKH đọc wiki đã duyệt + bộ nhớ riêng khách + dữ liệu CRM mới
       ↓
Kiểm quyền / kiểm nguồn / chuyển nhân viên / giới hạn chi phí
       ↓
Zalo Personal Bridge hoặc WhatsApp Cloud API
```

**Wiki giúp tổ chức tri thức; vector chỉ là chỉ mục; database giữ trạng thái và ký ức riêng; agent không có quyền tự sửa chính sách hoặc tự hoàn tiền.** Obsidian là công cụ biên tập/xem liên kết, không là database production hoặc điều kiện để bot hoạt động.

## Những gì có trong repo

- Kế hoạch v3, 34 task giữ ID SB-00…SB-33, quan hệ phụ thuộc và gate riêng cho từng chế độ/kênh.
- Hợp đồng sự kiện hiện hành v2, quyết định agent v1, schema trang wiki và bộ mẫu tổng hợp.
- Prompt cho coding agent và curator; checklist scope, bảo mật, vận hành, đánh giá và rollback.
- Bộ kiểm tra kế hoạch chạy local và các tình huống nghiệm thu bổ sung cho wiki. Kịch bản không đồng nghĩa application tests đã passed.

Các tài liệu cũ ở đường dẫn docs/01…10 trở thành mục dẫn đến đặc tả v3 để không có hai kiến trúc cạnh tranh. Bản trước còn trong lịch sử Git ở commit `5184b25e3efab6ce9594db1c7ce4b7efb9c13655`.

## Trạng thái trung thực

Hai video MP4 đã được kiểm tra các khung hình và nội dung hiển thị; chưa đối chiếu toàn bộ âm thanh. [Sổ nguồn](docs/00-source-review.md) phân biệt điều quan sát được, điều chưa biết và phần thiết kế bổ sung. Không suy ra thư viện Zalo từ nút Zalo trên demo.

Đây là **planning + synthetic starter kit**, chưa có ứng dụng CSKH chạy thật, login QR, tin khách đã gửi, đánh giá model, deployment hoặc agent được khởi chạy. Không tự tạo/bật lại lịch chạy, không mua dịch vụ.

Connector Zalo cá nhân ứng viên `zca-js` là unofficial, có rủi ro hạn chế/khóa tài khoản; kiểm thử tốt không biến nó thành API được nền tảng chấp thuận. Phải kiểm chứng sớm SB-27; không bật ngay trên tài khoản chính. Manual copilot là dự phòng không dùng session, không được báo thành đồng bộ tự động.

Repo public chỉ chứa nội dung tổng hợp, code và mẫu. Không commit tài liệu nội bộ, video, dữ liệu khách, cookie, QR, khóa API hoặc vault thật.
