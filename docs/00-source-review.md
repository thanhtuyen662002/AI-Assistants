# 00 — Sổ nguồn và đối chiếu hai clip

Ngày lập: **2026-10-09**, múi giờ nghiệp vụ Asia/Ho_Chi_Minh. Đây là provenance log, không phải transcript.

## 1. Hai nguồn người dùng cung cấp

| ID | Link gốc | Đích chuyển hướng quan sát được | Tình trạng |
|---|---|---|---|
| V1 | https://vt.tiktok.com/ZSbGmDL5w/ | https://www.tiktok.com/@cham_station/video/7694150556495006994 | BLOCKED — chưa lấy hình, âm thanh, phụ đề hoặc transcript |
| V2 | https://vt.tiktok.com/ZSbGudoxn/ | https://www.tiktok.com/@cham_station/video/7694506762312912146 | BLOCKED — chưa lấy hình, âm thanh, phụ đề hoặc transcript |

Đã thử mở short URL, URL đích, tra ID video; không thu được nội dung có thể kiểm chứng. Truy cập bằng HTTP trong môi trường làm việc cũng lỗi phân giải tên miền. Do đó không suy luận tiêu đề, phương pháp, stack, lời tác giả hay timestamp nội dung từ ID. Không tải lại hoặc đăng video/transcript có bản quyền vào repo công khai.

**Điều chưa hoàn thành:** phần “rút cách triển khai từ hai clip”. Toàn bộ đề xuất kiến trúc trong bộ tài liệu là thiết kế độc lập theo yêu cầu agent CSKH đa kênh, chưa được khẳng định tương đồng với hai clip.

### SB-00 — Quy trình đối chiếu khi có nội dung

Nhận video/transcript có quyền sử dụng từ chủ dự án hoặc truy cập công khai hợp lệ; xem toàn bộ. Tạo ghi chú có timestamp cho từng ý triển khai. Dùng bảng: `video_id | start/end | ý diễn giải | bằng chứng | áp dụng/thay đổi/loại bỏ | lý do | task/ADR`. Không dùng câu trích dài; tách rõ điều tác giả nói và điều nhóm suy luận.

Sau đối chiếu, sửa ADR và backlog bằng PR. Điểm không phù hợp policy Zalo/WhatsApp hoặc lộ dữ liệu không được làm theo chỉ vì có trong clip. SB-00 chỉ chuyển done khi có bằng chứng nội dung; chủ dự án có thể ghi `waived` nếu chấp nhận triển khai proposal độc lập. Không tự coi waived là đã xem clip.

## 2. Nguồn chính thức và mức xác minh

Các URL dưới đây là đầu vào kiểm chứng, không phải package cần cài. Kiểm tra lại tại thời điểm implement/go-live vì nền tảng có thể đổi.

| ID | Nguồn | Điều dùng trong plan | Mức xác minh |
|---|---|---|---|
| S1 | https://oa.zalo.me/home/documents/guides/tin-tu-van | OA OpenAPI có khung 7 ngày từ tương tác hợp lệ; 48 giờ liên quan tính phí; khác OA Manager | Đọc được nội dung chính thức |
| S2 | https://oa.zalo.me/home/documents/vie/guides/tong-quan-cac-loai-tin-nhan-tren-zalo-official-account-_3651713298729094511 | Phân biệt tin tư vấn, broadcast, ZBS Template Message; trang nêu hiệu lực 01/01/2026 | Nội dung chính thức qua chỉ mục tìm kiếm |
| S3 | https://oa.zalo.me/home/documents/guides/Khoi-tao-ung-dung-va-cap-quyen_117071366476220195 | OA liên kết/cấp quyền cho Zalo App để tích hợp | Nội dung chính thức qua chỉ mục tìm kiếm |
| S4 | https://stc-developers.zdn.vn/docs/v2/official-account/webhook/tin-nhan/su-kien-nguoi-dung-gui-tin-nhan | Có chữ ký X-ZEvent-Signature; công thức trong chỉ mục dùng appId, data, timestamp, OA secret | Chỉ mục có nội dung; trang mở trực tiếp chỉ có shell. Bắt buộc xác nhận canonicalization bằng fixture thật |
| S5 | https://stc-developers.zdn.vn/docs/v2/official-account/bat-dau/xac-thuc-va-uy-quyen-cho-ung-dung-new | OAuth/PKCE, access và refresh token | Chỉ mục có nội dung; không coi tuổi token hiển thị trong chỉ mục là hằng số implementation |
| S6 | https://business.whatsapp.com/policy (chuyển hướng https://whatsappbusiness.com/policy/) | 24 giờ cho phản hồi tự do, template ngoài khung, opt-in/opt-out, lối chuyển người | Đọc được; trang ghi cập nhật 23/09/2026 |
| S7 | https://whatsappbusiness.com/products/platform-pricing/ | Giá phụ thuộc loại tin/thị trường; có nội dung miễn phí trên trang marketing | Đọc được nhưng chưa giải quyết khác biệt với thông tin cập nhật tháng 10/2026; không dùng để chốt giá |
| S8 | https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing/non-template-messages | Nguồn cần kiểm tra cho giá service message đang hiệu lực | Chưa đọc được trang trong phiên; BLOCKED cho chốt rate card, không khẳng định mức giá |
| S9 | https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/overview | Tài liệu webhook hiện hành cần dùng khi implement | Bị rate limit khi mở; phải kiểm tra lại |
| S10 | https://whatsapp.github.io/WhatsApp-Nodejs-SDK/api-reference/webhooks/start/ | Tham khảo chính thức GET verify challenge và POST signature | Đọc được, nhưng **SDK đã archived**; không chọn SDK này làm dependency |
| S11 | https://www.whatsapp.com/legal/meta-terms-whatsapp-business | Điều khoản hiện hành và phân loại use case AI | Chuyển đến trang login; phải đọc bản áp dụng cho account trước production. Không mặc định assistant AI tổng quát được phép |
| S12 | https://www.postgresql.org/docs/current/ddl-rowsecurity.html | RLS; owner/superuser/BYPASSRLS có thể vượt policy | Đọc được tài liệu PostgreSQL |
| S13 | https://github.com/pgvector/pgvector | Vector search, exact/approximate index, filter và hybrid retrieval | Đọc được tài liệu dự án gốc |
| S14 | https://docs.bullmq.io/patterns/idempotent-jobs | Worker retry phải idempotent, chia job nhỏ | Đọc được tài liệu dự án gốc |

## 3. Kết luận được dùng, không được suy rộng

S1 hỗ trợ phân biệt quyền gửi và chi phí Zalo; không suy ra mọi tài khoản OA có cùng entitlement/quota. S6 hỗ trợ giới hạn 24 giờ và lối chuyển người; không chứng minh account đã được duyệt hoặc model/provider nào được phép nhận dữ liệu.

**Giá WhatsApp là quyết định còn mở:** trang marketing đọc được có mô tả miễn phí cho service; nguồn kỹ thuật cập nhật chưa truy cập được, trong khi chỉ mục tìm kiếm có thông tin thay đổi. Không hard-code 0 đồng, không điền đơn giá ước đoán. SB-09/SB-25 phải lấy rate card hiệu lực từ Meta/account, ghi effective_at/market/currency/loại tin; chưa chốt thì chỉ sandbox hoặc draft-only với giới hạn chi tiêu.

S4/S5/S9 chưa đủ để khẳng định mọi byte payload/thuật toán/token lifecycle. Contract adapter phải có test từ sandbox, không sao chép ví dụ không kiểm chứng vào production. S10 chỉ dùng hiểu phân tách GET handshake và POST authentication; không dùng dependency đã archived.

## 4. Sổ quyết định

- D01: một doanh nghiệp pilot, nhiều kênh; đây là giả định thiết kế, chưa biết ngành hàng/CRM/khối lượng thực tế.
- D02: TypeScript monorepo và PostgreSQL làm nguồn trạng thái; không phải yêu cầu từ clip.
- D03: API chính thức, RAG + bộ nhớ có nguồn + tool kiểm soát; không fine-tune hoặc graph database ở MVP.
- D04: chưa có credentials hoặc dữ liệu thật trong repo; không có deployment được tạo trong phiên này.
- D05: các ngưỡng chất lượng, retention, tải thử, token budget là mục tiêu ban đầu cần đo/duyệt, không phải SLA đã đạt hay thời hạn pháp lý.
