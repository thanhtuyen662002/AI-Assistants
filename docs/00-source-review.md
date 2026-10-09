# 00 — Sổ nguồn

Baseline và sửa phạm vi ngày 2026-10-09. Nguồn yêu cầu mới: chủ dự án xác nhận **Zalo cá nhân, không phải OA**. Đọc [quyết định 10](10-zalo-personal-decision.md) trước khi chọn connector.

## Hai clip còn thiếu nội dung

V1: https://vt.tiktok.com/ZSbGmDL5w/ — baseline ghi nhận đích https://www.tiktok.com/@cham_station/video/7694150556495006994 .
V2: https://vt.tiktok.com/ZSbGudoxn/ — baseline ghi nhận đích https://www.tiktok.com/@cham_station/video/7694506762312912146 .

Không có hình/âm thanh/phụ đề/transcript để kiểm chứng trong baseline; lần sửa loại tài khoản này cũng không cung cấp nội dung mới. Không đoán phương pháp/tác giả nói gì từ URL. SB-00 vẫn BLOCKED; nhận nội dung có quyền sử dụng rồi ghi timestamp → ý diễn giải → bằng chứng → áp dụng/thay đổi/loại bỏ → task/ADR. Không public nguyên video/transcript dài. Owner có thể chấp nhận proposal độc lập, nhưng không gọi waiver là đã xem clip.

## Nguồn hiện hành theo phạm vi

Zalo cá nhân: P1–P6 trong docs/10 gồm upstream `RFS-ADRENO/zca-js`, tài liệu maintainer và Zalo Help. Đây là nguồn kiểm tra cho lần sửa. Connector unofficial; không có live verification. Tài liệu và endpoint OA trong baseline trước **không được dùng làm spec personal**.

Các nguồn dưới đây được giữ từ lần lập baseline; chưa khẳng định tất cả đã được mở lại ở lần sửa tài khoản:

| ID | Nguồn | Mức kiểm chứng và cách dùng |
|---|---|---|
| S1–S5 | https://oa.zalo.me/home/documents/guides/tin-tu-van và tài liệu OA OAuth/webhook | Chỉ là lịch sử nghiên cứu OA; OUT OF SCOPE cho personal, không áp 48h/7d/chữ ký/OA token |
| S6 | https://business.whatsapp.com/policy | Baseline đọc được chính sách 24h/template/opt-out/handoff, trang ghi cập nhật 23/09/2026; recheck khi implement/live |
| S7 | https://whatsappbusiness.com/products/platform-pricing/ | Baseline đọc được marketing page; không đủ để chốt rate card đang hiệu lực |
| S8 | https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing/non-template-messages | Baseline chưa đọc được; chốt actual rate/currency/market/effective date trước live, không mặc định free |
| S9 | https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/overview | Baseline gặp rate limit; phải kiểm live docs và fixtures |
| S10 | https://whatsapp.github.io/WhatsApp-Nodejs-SDK/api-reference/webhooks/start/ | Tham khảo handshake/signature; SDK archived, không chọn làm dependency |
| S11 | https://www.whatsapp.com/legal/meta-terms-whatsapp-business | Baseline gặp login; review terms/AI use case trước production, không mặc định đã được Meta chấp thuận |
| S12 | https://www.postgresql.org/docs/current/ddl-rowsecurity.html | Baseline đọc được RLS và owner/superuser/BYPASSRLS exceptions |
| S13 | https://github.com/pgvector/pgvector | Baseline đọc được exact/approximate search, filtering; benchmark theo phiên bản pin |
| S14 | https://docs.bullmq.io/patterns/idempotent-jobs | Baseline đọc được yêu cầu idempotent jobs khi retry |

Không lấy giá WhatsApp từ trí nhớ hoặc mốc 24 giờ. Personal không kế thừa OA rate card nhưng vẫn có chi phí model/hạ tầng; chi phí platform chưa biết phải ghi unknown, không tự ghi 0. Điều khoản/account risk, bảo vệ dữ liệu và version thư viện phải kiểm lại tại thời điểm thực hiện.

## Giả định thiết kế, không phải fact từ clip

Một doanh nghiệp pilot; TypeScript monorepo; relational + vector; bounded single-agent runtime; không fine-tune bằng chat khách; giá/đơn hàng qua tools. Các ngưỡng chất lượng/tải/retention là mục tiêu cần duyệt và đo. Chưa cấp credential, chưa có deployment, chưa biết ngành hàng/CRM/khối lượng. Loại tài khoản Zalo cá nhân là yêu cầu đã xác nhận, không còn là giả định.
