# 01 — Sản phẩm, phạm vi và tiêu chí thành công

## Mục tiêu

Xây bộ não thứ hai giúp agent CSKH hiểu doanh nghiệp, nhớ đúng khách, nối tiếp công việc và dùng công cụ được phép trên Zalo OA/WhatsApp. Người vận hành thấy agent dựa vào nguồn nào, đã làm gì, cần người hỗ trợ ở đâu và có thể sửa/xóa tri thức hoặc dừng tự động ngay.

## Giả định để triển khai không bị chờ

Một doanh nghiệp pilot, giao tiếp 1:1, tiếng Việt mặc định, tiếng Anh khi khách sử dụng. Chưa biết ngành hàng, CRM, ngân sách, số hội thoại và hạ tầng mong muốn. Dùng dữ liệu giả của cửa hàng bán sản phẩm thông thường; không suy ra lĩnh vực nhạy cảm hoặc trường hợp bị nền tảng hạn chế. Chỉ sandbox/mocks cho đến khi checklist chủ dự án hoàn tất.

Thiết kế chịu tải thử ban đầu 10 tin inbound/giây trong 10 phút và 50 hội thoại đang xử lý; đây là **test target**, không phải dự báo traffic hay quota provider. Tăng tải theo đo thực tế. Không đưa con số hạ tầng hoặc lịch ra mắt thành cam kết khi chưa có dữ liệu.

## Hành trình cần chạy được

| Use case | Luồng đúng | Kết quả / phương án thiếu dữ liệu |
|---|---|---|
| FAQ và chính sách | Tra tài liệu published còn hiệu lực → soạn câu trả lời → lưu source refs | Trả lời có căn cứ; không thấy nguồn thì hỏi rõ hoặc chuyển người |
| Khách quay lại | Xác định đúng channel identity → lấy preference/lịch sử được phép → nối tiếp case | Không yêu cầu kể lại toàn bộ; không lộ lịch sử khách khác |
| Tình trạng đơn hàng | Xác minh quyền sở hữu → gọi order API → trả trạng thái mới nhất | API lỗi thì nói chưa kiểm tra được; không lấy status cũ từ vector |
| Đổi trả/khiếu nại | Tra chính sách → thu thông tin tối thiểu → tạo ticket có xác nhận | Nhân viên duyệt ngoại lệ; bot không tự hoàn tiền |
| Tiếp quản bởi người | Khách yêu cầu người hoặc rủi ro cao → ticket/queue → tóm tắt có nguồn | Bot dừng, không tranh trả lời; SLA theo giờ làm việc cấu hình |
| Liên kết Zalo–WhatsApp | Chứng minh sở hữu qua tài khoản đăng nhập/challenge riêng cho linking | Mới dùng chung bộ nhớ sau link hợp lệ; tên/số tự khai không đủ |
| Cập nhật tri thức | Upload → kiểm tra → chuẩn hóa → version → review → publish | Bản cũ bị loại khỏi retrieval ngay khi hết hiệu lực/thu hồi |
| Sửa/xóa dữ liệu | Yêu cầu của khách → xác minh → sửa/tombstone → purge các bản dẫn xuất | Không phục hồi ký ức đã xóa từ bản tóm tắt hoặc job cũ |

## Phạm vi

### MVP nghiệm thu

Text inbound/outbound cho cả hai kênh chính thức; sandbox/mock trước tài khoản thật. Inbox hợp nhất với quyền nhân viên; một kho tài liệu Markdown/text và PDF có text layer; tìm kiếm theo từ khóa + vector; source refs nội bộ. Bộ nhớ phiên, preference có nguồn, lịch sử case; user identity không tự merge đa kênh. Tra cứu order read-only qua adapter mock và một hệ thống thật khi được chỉ định. Ticket idempotent. Human handoff, kill switch, quota/cost cap, audit và đánh giá chất lượng.

Ảnh/file khách gửi trong MVP: nhận metadata, kiểm tra an toàn và báo chuyển người hoặc yêu cầu mô tả bằng text; không bịa rằng đã đọc ảnh. Chưa cho tải media tùy ý vào LLM.

### V1 sau pilot

UI sửa/link/unlink identity có xác minh; workflow phê duyệt hành động ghi; extraction tài liệu phức tạp có kiểm chứng; vòng học có review; follow-up theo template được duyệt và đồng ý nhận tin. Thêm CRM thật còn thiếu. Kiểm tra chi phí và quyền sử dụng riêng trước khi thêm voice/OCR.

### Ngoài phạm vi

Zalo cá nhân, nhóm chat hoặc broadcast marketing hàng loạt; WhatsApp Web automation; cuộc gọi/voice agent; thanh toán/hoàn tiền tự động; bot AI tổng quát trả lời mọi chủ đề; fine-tune bằng dữ liệu khách; graph database; multi-agent tự quyết ở runtime; billing SaaS; tích hợp tất cả CRM; triển khai hạ tầng trả phí không được duyệt.

## Cấp độ tự động hóa

`OFF`: chỉ tiếp nhận và chuyển người. `SHADOW`: chạy suy luận/đánh giá nhưng không gửi. `COPILOT`: nhân viên xem và duyệt bản nháp. `AUTO_LOW_RISK`: tự trả FAQ có nguồn, preference hợp lệ, order read-only đã xác minh. Không có chế độ tự thực hiện mọi action. Mỗi tenant/channel có flag; sender là nơi cưỡng chế cuối cùng.

## Ưu tiên nghiệp vụ

P0: trả lời đúng phạm vi, không lộ dữ liệu, không bỏ sót tin, không gửi khi người đang xử lý, không thực hiện hành động trái quyền. P1: nhớ preference, giảm lặp hỏi, trích nguồn, tool read-only, UI quản trị. P2: tự đề xuất cải thiện KB, báo cáo giá trị, kênh/media bổ sung.

## Mục tiêu đo lường đề xuất

Tối thiểu 200 câu đánh giá có nhãn trước auto mode; 50 mẫu được người độc lập review. Grounded correctness ≥90% trên câu trả lời trong phạm vi; unsupported-claim ≤2%; không chấp nhận lỗi lộ dữ liệu hoặc action trái quyền dù điểm tổng cao. Recall@5 ≥90% trên tập retrieval có nguồn đích. Handoff bắt buộc ở tình huống rủi ro ≥95%, riêng yêu cầu trực tiếp gặp người và kiểm thử takeover phải đạt 100%.

ACK webhook nội bộ p95 ≤1 giây sau khi nhận, text response p95 ≤10 giây ở tải thử với provider khỏe; tách thời gian phía hệ thống và phía provider, không báo đáp ứng SLA production nếu chưa load test. Đếm containment chỉ khi case giải quyết không cần người và không reopen trong 24 giờ; không tối ưu bằng cách ngăn khách gặp nhân viên.

Ngưỡng là điều kiện mục tiêu cho pilot, chủ dự án có thể điều chỉnh bằng Decision Record có lý do. Chi tiết cách tính và bộ test ở tài liệu 07.
