# 00 — Sổ bằng chứng v3: hai video + kiểm chứng bên ngoài

Ngày kiểm tra: 2026-10-09. Bản cũ ghi chưa truy cập được clip đã lỗi thời sau khi người dùng tải MP4. Trạng thái đúng hiện tại là **đã kiểm tra các khung hình/nội dung hiển thị, chưa đối chiếu toàn bộ lời thoại**. Không tuyên bố đã xem/nghe toàn bộ hoặc đã reverse-engineer ứng dụng demo.

## 1. File gốc và mức phủ

| ID | File người dùng cung cấp | Thời lượng ffprobe | SHA-256 |
|---|---|---|---|
| V1 | snaptik.vn_7694150556495006994.mp4 | 483.133333 giây | 21799f230fbe7106ac3d6024cfb276ef8a39451be4bc5776b7857a73333164ca |
| V2 | snaptik.vn_7694506762312912146.mp4 | 195.633333 giây | 7073c9629a97a248cefa073662f1b553ba147c7dc4497374cbb26e676ac62c29 |

Hai file có video H.264 và audio AAC. Lần hợp nhất đọc lại contact sheets: V1 mốc 00:00–08:00 khoảng 20 giây/frame và frame chi tiết 02:00; V2 00:00–03:10 khoảng 10 giây/frame. Đây là sampling hình, không phải bản ghi toàn bộ lời nói. Không upload video, screenshot, nội dung chat/số điện thoại/đơn hàng trong demo hoặc transcript dài lên repo public.

## 2. Evidence → quyết định → task

| Mã | Video/mốc gần đúng | Quan sát trực tiếp trên màn hình | Áp dụng / giới hạn | Task |
|---|---|---|---|---|
| C1 | V1 01:40–02:20 | CLAUDE.md; raw read-only; wiki/index, log, overview; sources/entities/concepts/analysis | Tách source/workspace/derived wiki; quyền enforced bằng code, không chỉ prompt | SB-28/29 |
| C2 | V1 02:00–02:40 | Quy ước metadata/tên trang, liên kết, số liệu và mâu thuẫn nguồn | Schema + provenance/number/negation/conflict tests; không tự giữ số sai vì model confidence cao | SB-28/31 |
| C3 | V1 03:20 và 05:00 | Phản hồi dựng thư mục nêu phần hướng dẫn ba thao tác chưa đủ nội dung thứ ba; overview cần bổ sung | Không sao chép thiếu sót thành spec. Lint/review/publish là bổ sung của kế hoạch, không gán tác giả | SB-30 |
| C4 | V1 04:40–07:20 | raw và Clippings; nạp nguồn, tạo trang sources/entities/concepts, cập nhật index/overview/log và mạng liên kết | Curator patch theo nguồn, link graph có ACL, index có thể rebuild | SB-10/29/30/11 |
| C5 | V2 00:20–01:10 | Trình bày một ứng dụng đầu ra dạng sách | Minh họa sử dụng tri thức, không phải yêu cầu xây công cụ viết sách trong dự án CSKH | Scope |
| C6 | V2 01:20–01:50 và 02:30 | UI trợ lý có chữ/giọng nói, nút Zalo/Telegram | Multi-channel interface là ý tưởng dùng; voice/Telegram không thành MVP bắt buộc; không chứng minh library/backend/account type | SB-16, SB-07/08 kiểm riêng |
| C7 | V2 02:00–02:10 | Màn hình báo cáo tin/usage/việc chưa xong và thông tin cấu hình trợ lý | Owner brief từ ledger, structured business profile; không sao chép PII hoặc đơn giá trong demo | SB-01/20/32 |
| C8 | V2 02:20 | Graph các trang tri thức | Liên kết hỗ trợ điều hướng, không bằng chứng cần graph database hoặc RAG đã đúng | SB-28/31 |

Không dùng số liệu doanh thu/token/giá/định danh trong demo làm dữ kiện của chủ dự án. Không định danh người trong hình. Chỉ paraphrase kỹ thuật cần thiết.

## 3. Nguồn ngoài được đọc lại

| ID | Nguồn gốc | Điều đã kiểm / điều chưa đủ |
|---|---|---|
| E1 | https://obsidian.md/help/links | Obsidian hỗ trợ wikilinks/Markdown links; liên kết và alias không tự là bằng chứng đúng |
| E2 | https://code.claude.com/docs/en/memory | CLAUDE.md/AGENTS.md là context hướng dẫn, không enforced configuration; vì vậy plan không dựa riêng prompt để giữ quyền |
| E3 | https://github.com/RFS-ADRENO/zca-js | README mô tả personal unofficial API, loginQR/listener/send, risk account và một web listener/account; chưa cài/test account người dùng |
| E3b | https://zca-js.tdung.com/en/listeners/message | Event message/thread/isSelf của thư viện; không chứng minh self-visibility trên mọi thiết bị hoặc mọi phiên bản |
| E4 | https://business.whatsapp.com/policy | Policy có khung phản hồi 24h/template và tuyến chuyển người; cần kiểm lại với account trước go-live |
| E5 | https://github.com/pgvector/pgvector | Chỉ mục/vector retrieval PostgreSQL; chọn exact/approximate và filter phải benchmark theo corpus |
| E6 | https://www.postgresql.org/docs/current/ddl-rowsecurity.html | RLS và quyền bypass của owner/superuser; runtime role không dùng các quyền này |

Nguồn kỹ thuật có thể đổi. SB-27 pin zca version và thu fixtures được phép; SB-08 pin API version hiện hành; SB-25 xác minh terms/AI use case/rate card/template/capability thực tế. Chưa có rate card WhatsApp đã được xác nhận trong phiên hợp nhất: ghi unknown, không số 0. Không dùng điều khoản OA cho tài khoản cá nhân.

## 4. Phân biệt evidence và proposal

Các lựa chọn PostgreSQL/pgvector/BullMQ, atomic release, ACL, private memory, tool safety, bảng task và chỉ số chất lượng là **thiết kế bổ sung**, không nói là tác giả clip đã triển khai chúng. Demo không chứng minh uptime, account approval, chống rò dữ liệu hay hiệu quả tại quy mô doanh nghiệp.

SB-00 giữ `partial`: có visual evidence đủ để truy vết các ý đã dùng; full-audio verification chưa làm. Không chặn code độc lập chỉ vì phần này chưa đủ; không tự đổi thành fully verified. Khi có lời thoại được đối chiếu, cập nhật đúng ý khác biệt qua PR thay vì âm thầm gán lại nguồn.
