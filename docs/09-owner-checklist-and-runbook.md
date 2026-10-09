# 09 — Checklist chủ dự án, vận hành và chi phí

## 1. Những gì đã và chưa làm ở baseline

Đã lập bộ đặc tả, task DAG, prompt coding agents, schema và eval seed. **Chưa** có code runtime, tài khoản Zalo/WhatsApp được kết nối, khóa model, CRM thật, hạ tầng provisioned, QA application hoặc tin nhắn khách đã gửi. Nội dung hai clip còn chưa đối chiếu. Không có task background/automation nào tự chạy từ repo này.

Repo public: không đưa input nhạy cảm vào Git. Checklist ghi trạng thái và owner; file/tài khoản/secret thật nhập qua kênh riêng được cấp quyền.

## 2. Input registry

| Input cần chủ dự án chốt | Dùng cho | Có thể làm gì khi chưa có | Gate bị chặn |
|---|---|---|---|
| Hai video hoặc transcript có quyền sử dụng | SB-00 đối chiếu thiết kế với clip | Tiếp tục proposal độc lập, giữ source caveat | Không tuyên bố bám sát clip; scope sign-off cần ghi giới hạn |
| Ngành hàng, sản phẩm, use cases ưu tiên | SB-01 dataset và tools | Cửa hàng sản phẩm thông thường synthetic | UAT nghiệp vụ và policy use-case |
| FAQ/chính sách/version/owner tài liệu | SB-10/11 | Synthetic KB có ghi giả | Trả lời khách thật |
| CRM/order backend/API và read scopes | SB-14 | Mock adapter, không bịa dữ liệu thật | Nghiệm thu tra cứu đơn thật |
| OA, Zalo App, quyền/entitlement, callback và secret | SB-07 | Mock verify/normalize/send fixtures | Sandbox/live Zalo |
| Meta app/WABA/số, webhook, token/scopes | SB-08 | Mock adapter + fake clock | Sandbox/live WhatsApp |
| Template và consent flow cho follow-up | SB-09 | Không gửi chủ động ngoài khung | Follow-up production |
| Rate card hiện hành và budget theo account/thị trường | SB-09/20/25 | Unknown-cost state, OFF/SHADOW | Tự gửi thật có chi phí |
| Provider/model, processing/retention/data region | SB-15 | Fake model/local fixtures | Dữ liệu khách đến model thật |
| Nhân viên nhận handoff, giờ làm, SLA, liên hệ ngoài giờ | SB-17/24 | Mock operator/synthetic SLA | Khách thật yêu cầu người |
| Privacy notice, mục đích xử lý, retention, xóa/export và legal review | SB-13/25 | Dữ liệu tổng hợp | Lưu trữ customer memory thật |
| Hosting/domain/TLS/budget/quyền deploy | SB-23 | Docker/CI/templates local | Deploy staging/production |

Không hỏi lại thông tin đã được ghi trong Decision Record. Lead dùng registry để chia phần độc lập, thay vì bắt toàn bộ đội chờ một credential.

## 3. Setup checklist theo thứ tự

### Local — Operations + Platform

Scaffold toolchain có pin versions, scripts và lockfile; dựng DB/Redis/object storage; migrate bằng admin job riêng; tạo synthetic tenant/users/KB/order fixtures. Runtime dùng DB role ít quyền. Model/channel/CRM mặc định mock. Lint/typecheck/unit/contracts/build chạy được từ checkout sạch. Không có `.env` thật trong commit.

### Staging — Channels + Operations

Tạo môi trường độc lập với production; owner cấp account test và budget. Cấu hình domain/TLS, webhook verification và binding mapping. Cấp secret least privilege qua secret manager; rotation thử. Test nhận/gửi/trạng thái thực trên cả hai kênh; giữ fixtures đã loại định danh. Không công khai test endpoint vô hạn hoặc dùng người nhận không đồng ý thử.

### Knowledge — Memory + business owner

Lập catalog tài liệu có owner/effective date; loại tài liệu nội bộ không cần cho CSKH; upload/quarantine/extract/review; chạy retrieval eval. Gắn nguồn giá/đơn hàng hiện tại vào tools, không KB snapshot. Review câu trả lời và giọng điệu tiếng Việt trên ít nhất 50 mẫu.

### Copilot — Console + support lead

Nhân viên login, nhận ca, xem source/draft, sửa và gửi bằng outbox. Diễn tập yêu cầu chuyển người, ca ngoài giờ, blocked recipient, expired template, lỗi tool và token revoke. Tất cả tin nhắn ở mode COPILOT phải được nhân viên duyệt; UI không tự gửi vì LLM tự đánh giá confidence cao.

## 4. Rollout có kiểm soát

Bước 1 OFF/SHADOW: ingest thật chỉ khi có quyền xử lý, chạy đánh giá không gửi tự động. Bước 2 COPILOT: người duyệt tất cả. Bước 3 AUTO_LOW_RISK cho allowlisted intent trên một tenant và một kênh, cohort nhỏ đã chốt. Bước 4 mở kênh thứ hai khi vượt cùng gate. Bước 5 tăng cohort từ 5% → 25% → 100% các hội thoại **đủ điều kiện**, không phải 100% mọi use case.

Các tỷ lệ là cách canary đề xuất, không phải lịch tự động. Mỗi lần tăng cần đủ số mẫu, không có P0, review quality/cost/reopen và support capacity; owner ghi quyết định. Action rủi ro, identity chưa xác minh, knowledge conflict hoặc ngoài policy luôn ở human flow.

Kill switch theo global/tenant/channel và loại action. OFF chặn sender lập tức cho intents chưa dispatch; tiếp tục lưu inbound và cảnh báo người vận hành nếu còn an toàn. Tin đã dispatch có thể không thu hồi được. Không tắt ingress chỉ để giảm lỗi và làm mất hội thoại.

## 5. Mô hình chi phí — không phải báo giá

```text
Monthly total = fixed infrastructure
              + LLM input/output usage * effective token rates
              + embeddings/re-embeddings + optional reranker
              + delivered channel messages by category/market/rate_version
              + BSP/service fees if used
              + storage/backup/egress/observability
              + taxes/FX where applicable
```

Input worksheet cần có: active customers, inbound turns/tháng, outbound segments/turn, token in/out/turn, tools/turn, KB size/change rate, % handoff, market distribution, provider minimum plans và approved spend cap. Không nhầm 1 inbound = 1 billable outbound; split message/retry/notification có thể tăng count.

Rate snapshot lưu nguồn, effective_at, currency, market/category, tier/allowance nếu có, checked_by; không suy ra mọi service message free từ cửa sổ 24h. Estimate lúc enqueue cần reservation atomic; actual khi có delivery/billing evidence thì đối soát và giải phóng/điều chỉnh reservation. Trạng thái unknown giữ dự phòng hợp lý đến khi đối soát, không xóa chi phí vì chưa thấy delivered event.

Đặt soft cap cảnh báo ở 80% và hard cap theo budget được duyệt. Quá cap: dừng auto/giảm công việc tùy chọn, tạo draft/handoff; không chuyển sang model rẻ chưa được duyệt xử lý dữ liệu. Đây là policy đề xuất để owner chốt, không phát sinh mua dịch vụ trong phiên lập plan.

## 6. Runbook sự cố

| Sự cố | Hành động đầu | Kiểm tra / phục hồi |
|---|---|---|
| Nghi lộ dữ liệu hoặc tool trái quyền | Tắt auto/action của phạm vi ảnh hưởng; giữ audit tối thiểu | Xác định tenant/customer/run, khóa credential cần thiết, incident owner và privacy response; không gửi transcript qua alert |
| Zalo/Meta token revoked | Dừng sender account đó, cảnh báo owner | Reauthorize đúng app/OA/WABA, test sandbox/controlled send; không spam refresh |
| Queue down / backlog tăng | Giữ durable receipt, báo delay, giảm optional jobs | Khôi phục queue, dispatcher sweeper/replay có dedup; không purge inbox chưa xử lý |
| Provider 429/5xx | Per-account backoff/circuit breaker | Theo Retry-After/status, không retry storm; kiểm quota/billing |
| Outbound unknown | Không retry mù | Đối soát ID/status nếu có, nhân viên kiểm khi không xác định; đánh dấu kết quả và audit |
| KB sai/thu hồi nguồn | Revoke version, dừng auto intent liên quan | Invalidate cache/context, publish bản sửa đã review + regression; chủ CSKH quyết định xử lý khách bị ảnh hưởng |
| Bot trả sau takeover | OFF bot channel/tenant theo impact | So ownership_version/leases/send timestamps, fix race và test trước bật lại |
| Model outage/cost spike | Circuit breaker, giữ draft/handoff | Kiểm budget/provider; fallback chỉ model đã được duyệt và vượt eval |
| Xóa dữ liệu chưa hoàn tất | Hạn chế đọc resource ngay bằng tombstone | Retry purge có audit; kiểm vector/cache/jobs/object/backup suppression |
| Deploy lỗi | OFF auto và rollback image/config | Chọn version tương thích schema, không reverse migration phá dữ liệu; restore chỉ theo runbook đã thử |

## 7. Backup/restore

Mục tiêu kỹ thuật pilot đề xuất RPO ≤24 giờ, RTO ≤4 giờ; phải đo trong restore drill và chỉnh theo yêu cầu thực tế, không coi đã đạt. Backup DB và objects có lịch/retention/mã hóa; key recovery được phân quyền. Restore vào môi trường cô lập; áp tombstones/suppression ledger và kiểm tenant isolation trước nối network/providers. Disable mọi sender trong quá trình restore để không replay gửi hàng loạt.

## 8. Danh sách ra quyết định trước production

Chủ dự án/support lead ký scope, dữ liệu, staffing và mode. Channels xác nhận policy/rate card/token/terms hiện hành cho account. QA ký báo cáo hard gates; Operations chứng minh kill switch/restore/cost cap; privacy reviewer duyệt retention và xử lý dữ liệu qua nhà cung cấp. Lead ghi phạm vi nào vẫn MOCK_ONLY/BLOCKED. Không báo sản phẩm hoàn thiện nếu tài khoản thật, nguồn nghiệp vụ hoặc tuyến chuyển người chưa hoạt động.
