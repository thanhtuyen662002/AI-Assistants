# 10 — Quyết định sửa phạm vi: Zalo cá nhân, không phải OA

Ngày: 2026-10-09. Trạng thái: **yêu cầu loại tài khoản đã được chủ dự án xác nhận; connector mới là ứng viên thiết kế, chưa kiểm thử live**.

## Yêu cầu và tác động

Chủ dự án: “Mình dùng account Zalo thật không phải Zalo OA nha”. Trong plan hiện hành, Zalo là tài khoản người dùng cá nhân đang sử dụng. Không chuyển người dùng sang OA, không coi OA là tài khoản thử và cá nhân mới là tài khoản thật. Sai lệch của baseline trước là **loại tài khoản**, không phải môi trường test/production.

Giữ nguyên mục tiêu second brain và WhatsApp Cloud API giả định. Thay riêng transport Zalo: OA OAuth/webhook → personal login/session/listener bridge. Không có OA ID/App secret/access token/ZBS hoặc mốc 48h/7d trong đường personal. WhatsApp chưa có yêu cầu đổi loại tài khoản.

## Nguồn kiểm tra trong lần sửa

| ID | Nguồn gốc | Bằng chứng / giới hạn |
|---|---|---|
| P1 | https://github.com/RFS-ADRENO/zca-js | README upstream mô tả unofficial personal API qua Zalo Web; loginQR, message listener, sendMessage; cảnh báo khóa/ban; chỉ một web listener/account, mở Zalo Web có thể dừng listener |
| P2 | https://zca-js.tdung.com/en/listeners/message | Tài liệu maintainer: threadId, ThreadType.User/Group, isSelf; isSelf chỉ nói event từ tài khoản đang dùng, không tự phân biệt bot và người |
| P3 | https://zca-js.tdung.com/vi/get-started/upgrade-to-v2 | Tài liệu maintainer có cấu hình selfListen; cấu trúc API khác giữa các phiên bản. Phải pin version và contract-test; chưa cài thư viện |
| P4 | https://help.zalo.me/doc-tag/loi/ | Chỉ mục tìm kiếm trang Zalo Help liệt kê dùng công cụ/phần mềm bên thứ ba trong nhóm tài khoản tự động có thể bị yêu cầu xác thực/hạn chế. Mở trực tiếp bị 403 trong phiên; không trình bày đây là toàn văn điều khoản đã đọc |
| P5 | https://developers.zalo.me/ và https://oa.zalo.me/home/documents/guides/Khoi-tao-ung-dung-va-cap-quyen_117071366476220195 | Tài liệu official được tìm thấy mô tả OA OpenAPI cho OA. Không có bằng chứng trong các nguồn đã đọc rằng OA API có thể điều khiển inbox của tài khoản cá nhân |
| P6 | https://tdung.gitbook.io/zca-js | Tài liệu maintainer cũ cảnh báo rủi ro vi phạm policy/vô hiệu hóa. Không dùng ví dụ API cũ thay tài liệu phiên bản đã pin |

Không chứng minh “không có bất kỳ API chính thức nào trên toàn nền tảng”; kết luận hẹp là phương án đã kiểm tra cho **inbox cá nhân hiện tại** là connector unofficial, không phải OA. Không gán capability của fork bất kỳ cho upstream. Không coi thư viện có code mẫu là đã chạy được trên tài khoản của chủ dự án.

## Lựa chọn đề xuất

**Ứng viên A — self-hosted Zalo Personal Bridge dùng zca-js.** Owner đăng nhập QR; bridge duy trì session/listener và giao tiếp backend riêng. Test một account do owner cho phép với người nhận đồng ý; không auto bật trên tài khoản chính chỉ vì cấu hình hợp lệ. Chỉ 1:1 CSKH allowlist; không nhóm, thu thập bạn bè, tìm số điện thoại hoặc bulk send. Adapter độc lập để đổi implementation nếu upstream hỏng.

**Dự phòng B — manual copilot.** Người dùng chủ động đưa nội dung CSKH tối thiểu vào console, AI soạn nháp có nguồn, người tự gửi qua app Zalo chính thức. Không cần bridge/session; không có đồng bộ inbox tự động, phải ghi nhận thủ công. Đây không được báo là hoàn thành tích hợp tự động.

Copilot **qua bridge** vẫn sử dụng công cụ bên thứ ba và vẫn có rủi ro account. Chỉ nhánh manual không kết nối session mới tránh được phụ thuộc connector. Không hứa rate-limit, delay, QR hay human approval loại bỏ nguy cơ khóa.

## Những điều SB-27 phải chứng minh

Pin upstream/package/version/integrity/license; review dependency và dữ liệu gửi ra ngoài. Tài khoản tự login QR qua màn quản trị hạn chế quyền; session revoke/relogin/rotation an toàn; chỉ một listener với fencing; listener chết khi phiên Web khác hoạt động được nhận biết; reconnect hữu hạn, không vượt challenge.

Test text inbound/outbound IDs, unicode, self echo, out-of-order/duplicate, mất kết nối và việc có/không bù lịch sử. Test riêng tin gửi tay từ mobile/PC/Web; không suy từ `selfListen` rằng mọi thiết bị luôn sync được. Chưa quan sát chắc self messages → manual/copilot hoặc tắt bot thủ công trước trả ngoài console; không mở auto khi owner dùng nhiều client mà hệ thống không kiểm soát được.

Release báo rõ `supported`, `unsupported`, `unverified` cho từng capability. Quá trình này không bảo đảm platform approval. Owner review rủi ro/terms hiện hành là điều kiện trước test/live; một checkbox chấp nhận rủi ro không được dùng để vượt kiểm soát của Zalo.

## Thay đổi yêu cầu triển khai

SB-07 thành personal adapter. SB-09 dùng personal account-health/allowlist/session/kill-switch gates, bỏ OA window/pricing. SB-17 bổ sung handoff qua self events và giới hạn quan sát. SB-23 bổ sung long-running bridge, encrypted spool/session, listener fencing. SB-24 kiểm thử account có kiểm soát, không official Zalo sandbox. SB-25 không yêu cầu OA; phải có account risk/capability/privacy acceptance. SB-27 mới để kiểm chứng sớm. Normalized event v2 dùng `zalo_personal`, tránh diễn giải lại `zalo` v1 vốn gắn baseline OA.

Lần sửa này chỉ thay đặc tả: chưa đăng nhập tài khoản, chưa gửi tin, chưa triển khai bridge. Hai clip vẫn cần nội dung thực tế để đóng SB-00.
