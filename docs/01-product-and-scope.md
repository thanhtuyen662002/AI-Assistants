# 01 — Phạm vi sản phẩm hiện hành

## Mục tiêu và tài khoản

Agent CSKH có second brain cho **Zalo cá nhân của chủ dự án** và WhatsApp (giữ giả định Cloud API, chưa xác nhận riêng loại account). Không OA onboarding. Phần Zalo tích hợp qua personal bridge không chính thức chỉ sau kiểm chứng SB-27 và owner cho phép; không hứa tài khoản chính không bị hạn chế/khóa. Phương án manual copilot khi không dùng bridge phải được gắn nhãn chưa có tự động đồng bộ.

Một doanh nghiệp pilot, 1:1, tiếng Việt mặc định, tiếng Anh theo khách. Chưa có ngành hàng/CRM/ngân sách/traffic; dùng cửa hàng sản phẩm thông thường synthetic để code độc lập. Không bịa policy thật. Một tài khoản cá nhân có thể chứa cả công việc và đời tư: chỉ thread CSKH được allowlist/owner đánh dấu mới vào pipeline; không đọc toàn bộ history/danh bạ/nhóm. Lọc trước lưu/LLM, không chỉ trước hiển thị UI.

## Use cases và acceptance

| Use case | Hành vi đúng | Khi thiếu điều kiện |
|---|---|---|
| FAQ/chính sách | Retrieve published KB còn hiệu lực, giữ source refs | Clarify/handoff, không tự tạo policy |
| Khách quay lại | Đúng binding+customer, preference/case có nguồn | Không đọc chéo hoặc tự gộp hai kênh |
| Tra đơn hàng/giá/tồn kho | Xác minh quyền, gọi API nguồn, giữ as_of | Tool lỗi nói chưa kiểm tra được, không dùng memory cũ |
| Khiếu nại/đổi trả | Tra policy, lấy thông tin tối thiểu, tạo ticket idempotent | Ngoại lệ và monetary action qua người; không auto refund |
| Nhân viên tiếp quản | CAS ownership, hủy pending bot, nguồn/source summary | Không tự resume do timeout/reconnect; in-flight có thể không thu hồi |
| Sửa/xóa ký ức | Xác minh, sửa/tombstone, phủ summary/vector/cache/job/bridge spool | Hiển thị tiến độ/lỗi và retention/backup limits rõ |
| Duyệt tri thức | Upload → quarantine → extract → version → review → publish | Không biến lời khách thành chính sách chung |
| Kết nối personal | Owner QR, private session, một listener, account-health rõ | Revoked/conflict/gap → pause, báo người, không hứa no-loss |

## MVP

Text CSKH 1:1 hai kênh; mock trước real-account/sandbox phù hợp từng kênh. Unified inbox, KB Markdown/text/PDF có text layer, lexical+vector retrieval, facts/episodes riêng khách, order read-only adapter và ticket; takeover, source evidence, deletion, cost cap, kill switch. Unsupported image/audio/file chỉ ghi metadata được phép và chuyển người/yêu cầu mô tả; không bịa đã đọc ảnh.

Zalo cá nhân: allowlist thread, QR/session lifecycle, durable internal ingest, duplicate/self-loop guard, reconnect và data-gap report. Không yêu cầu hỗ trợ import toàn bộ lịch sử; nếu nghiên cứu import sau này phải owner chọn thread/range, quyền xử lý và label historical, tuyệt đối không tự trả lời backlog lịch sử.

WhatsApp: vẫn official Cloud API, template/consent ngoài cửa sổ phù hợp; chuẩn bị account theo checklist riêng. Không suy rằng yêu cầu personal Zalo là chấp thuận WhatsApp Web.

## Chế độ

OFF chỉ giữ phần được phép/nhân viên; SHADOW không gửi; COPILOT bridge có nhân viên duyệt nhưng vẫn unofficial; AUTO_LOW_RISK chỉ FAQ/order read đã xác minh và có đủ capability/safety gates. Manual copilot là biến thể **không kết nối bridge**, người đưa nội dung và gửi ở app chính thức.

Không bật auto Zalo nếu session không khỏe, có gap chưa đối soát, không quan sát chắc human self messages trong mô hình dùng nhiều client, account bị challenge/restrict hoặc policy/privacy chưa được review. Owner acceptance không là platform approval.

## Ngoài phạm vi

Zalo OA/ZBS, nhóm, tự kết bạn/broadcast, scrape danh bạ/số điện thoại, né CAPTCHA/anti-bot/block, đổi proxy/tài khoản để né chặn, voice calls, auto monetary actions, runtime multi-agent tự do, fine-tune chat khách, graph database, billing SaaS. Không tự provision trả phí hoặc tự đăng nhập account thật từ task planning.

## Mục tiêu pilot cần đo

≥200 eval cases, 50 mẫu human review; grounded correctness ≥90%, unsupported claims ≤2%, retrieval Recall@5 ≥90%; zero leak/unauthorized action trong suite là hard gate. Handoff bắt buộc ≥95%, riêng yêu cầu trực tiếp và takeover race 100%. Backend test target 10 inbound/s, 50 conversations, p95 durable ingest ≤1s và response ≤10s khi dependency khỏe. **Không phát tải này vào tài khoản Zalo thật** hoặc coi đây là quota được Zalo cho phép. Thời gian bridge offline/gap báo riêng, không tính uptime/coverage bằng giả định. Chi tiết tại docs/07.
