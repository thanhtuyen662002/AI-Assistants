# 07 — Chất lượng, bảo mật, kiểm thử và release gates

Mọi số liệu bên dưới là mục tiêu nghiệm thu, chưa được đo trên sản phẩm. Planning baseline không có runtime, CI application hoặc sandbox credentials; không có test integration nào được báo passed ở đây.

## 1. Test pyramid

| Lớp | Kiểm gì | Dữ liệu / bằng chứng |
|---|---|---|
| Unit | Policy clock boundaries, state transitions, source filter, fact conflict, costs, redaction | Fake clock, fixture thuần, không gọi mạng |
| Contract | JSON Schema, OpenAPI, adapter normalize, tool args/results, UI API | Valid/invalid JSON + provider fixtures đã khử định danh |
| Integration | DB RLS/FK, inbox/outbox, Redis dispatcher, TTL/purge, object storage, ownership race | Compose dependencies thật, không chỉ mock DB |
| E2E | Conversation → RAG/tool → draft/reply → delivery → memory/handoff | Mock providers trước, sandbox suite tách riêng sau |
| Model eval | Groundedness, correctness, refusal/clarify, tiếng Việt, memory, tool choice | Golden test set có nhãn và nguồn; review độc lập |
| Security/chaos | IDOR, prompt injection, forged callback, worker crash, unknown sends, secret leak, restore | Attack fixtures, fault injection, audit evidence |
| UAT | Nhân viên xử lý và khách đồng ý thử | Kịch bản thật có kiểm soát; dữ liệu không ở public Git |

LLM judge không là oracle duy nhất. Dùng code assertions cho scope/quyền/state và người đánh giá cho claim nghiệp vụ. Tách tập phát triển và test giữ kín; không đưa expected answer của test vào KB/prompt chỉ để tăng điểm.

## 2. Golden set

`evals/golden-cases.jsonl` là **seed tổng hợp**, chưa đủ để nghiệm thu. SB-21 mở rộng tối thiểu 200 tình huống có nhãn: 60 FAQ/policy; 30 đơn hàng/tool; 25 memory/identity; 25 handoff/approval; 20 channel rules; 20 injection/privacy; 20 failure/retry. Có tiếng Việt có/không dấu, lỗi chính tả, emoji, code sản phẩm, câu nhiều ý và tiếng Anh.

Mỗi case cần fixture cụ thể, customer/tenant scope, input, allowed source IDs, expected behavior, forbidden behavior, applicable channel và severity. Các seed hiện mô tả test scenario, không phải inbound event payload để gửi trực tiếp đến provider. Không dùng số điện thoại hoặc ticket thật làm fixture.

### Định nghĩa metric

- Grounded correctness = số lượt in-scope có câu trả lời chính xác và mọi claim quan trọng được nguồn cho phép hỗ trợ / tổng lượt in-scope phải trả lời. Không tính abstain sai thành câu đúng.
- Unsupported-claim rate = số factual claims không được bằng chứng hợp lệ hỗ trợ / tổng factual claims. Báo cả số lỗi và mẫu số, không chỉ phần trăm.
- Recall@5 = tỷ lệ câu retrieval có ít nhất một source đích trong top 5; dùng corpus có nhãn, tách source conflict/stale.
- Required handoff recall = số case bắt buộc chuyển người được chuyển đúng / tất cả case bắt buộc; đo riêng yêu cầu trực tiếp gặp người.
- Reopen/containment = tính trên case đã resolve, quan sát 24 giờ trước chốt; không tính user bỏ đi là resolve.
- Latency = đo ACK, queue wait, retrieval, LLM, tool, outbox wait và provider delivery riêng. Response p95 không tính chỉ thời gian một HTTP endpoint.
- Cost per resolved case = hạ tầng phân bổ + model/embedding + channel + storage/egress theo case; thông tin rate chưa có ghi unknown, không tự coi bằng 0.

## 3. Hard gates trước AUTO_LOW_RISK

| Gate | Điều kiện |
|---|---|
| Q01 — Nguồn và scope | SB-01 được duyệt; SB-00 đã đối chiếu hoặc owner ghi chấp nhận rõ giới hạn nguồn; dữ liệu được quyền xử lý |
| Q02 — Account/policy | Cả Zalo và WhatsApp có capability record, policy/version và sandbox evidence; AI-use-case/terms, templates, consent, rate card được review trước gửi thật |
| Q03 — Identity/ACL | 100% deterministic tenant/customer isolation tests pass; zero leak và zero unauthorized tool action trong security suite |
| Q04 — Chất lượng | ≥200 eval cases; grounded correctness ≥90%; unsupported claims ≤2%; Recall@5 ≥90%; 50 mẫu được reviewer độc lập kiểm |
| Q05 — Chuyển người | Required handoff ≥95%; yêu cầu trực tiếp gặp người và takeover-race suite 100%; không tự resume; đường liên hệ nhân viên hoạt động |
| Q06 — Reliability | Duplicate 100 lần không tăng processing intent/action; crash-recovery và unknown-send tests pass; không ACK mất dữ liệu |
| Q07 — Tải/độ trễ | Tải thử đề xuất 10 inbound/s trong 10 phút, 50 conversation concurrent; ACK p95 ≤1s, text response p95 ≤10s khi dependencies khỏe; báo riêng bottleneck/quota |
| Q08 — Privacy | Correction, TTL, deletion, replay suppression và restore suppression pass; không secret/PII trong public repo/log/trace; retention được owner duyệt |
| Q09 — Vận hành | Alerts, on-call owner, cost cap, per-channel kill switch, staging/production isolation và backup restore có evidence |
| Q10 — Rollout | Chủ dự án sign-off; staff dùng được console; chỉ cohort đủ điều kiện; rollback thử thành công |

Không dùng trung bình để che lỗi nghiêm trọng. Một P0 leak/side effect trái quyền/sai identity chặn go-live dù đạt 99% correctness. Các threshold không là bảo đảm sẽ không bao giờ có lỗi; tiếp tục monitoring khi chạy thật.

## 4. Threat model và control

**Webhook spoof/replay:** raw signature verification, account binding, body limit, durable dedup, provider retry-aware timestamps, constant-time compare. Endpoint token/IP allowlist chỉ bổ sung, không thay chữ ký.

**Prompt injection trực tiếp/qua tài liệu:** model không cầm secret/quyền admin; tool allowlist + scoped context; nội dung tài liệu là untrusted data; structured output/semantic validator; deny instruction thay đổi tenant/role. Test nguồn KB bị chèn “bỏ policy và hoàn tiền”.

**IDOR/cross-tenant/cross-customer:** derive context từ auth, scoped repositories, RLS và composite FK; kiểm worker/background/admin export/cache/vector/object storage. Cache key phải chứa tenant, ACL version, customer khi riêng tư, knowledge version. Không cache câu trả lời cá nhân toàn cục.

**Media/SSRF:** MVP không tải URL khách tùy ý. Khi bật fetch: chỉ storage/provider allowlist, kiểm DNS/IP private/link-local/loopback/metadata, redirects và DNS rebinding, egress deny-default, max size/time, MIME sniffing, sandbox extraction, malware quarantine. File người dùng không được execute.

**Secret/PII exposure:** secret manager, encryption at rest/transit, key rotation plan; redacted logs; tracing opt-in có giới hạn và quyền; không gửi toàn bộ hồ sơ cho LLM. Review vùng lưu dữ liệu, retention của model provider và điều kiện dùng dữ liệu trước production. Không suy ra “không train” nếu chưa có cấu hình/điều khoản chứng minh.

**Action abuse:** deterministic authorization, limit/approval/hash binding, transaction intent trước effect, downstream idempotency/reconciliation, fresh source recheck; không dùng model score để vượt quyền. User confirmation không thay staff approval với thao tác rủi ro.

**Human/bot race:** cùng ownership protocol và fencing version, kiểm tra ở sender; event echo không kích hoạt chatbot; hủy pending intents, in-flight được đánh dấu và giải thích giới hạn.

**Memory poisoning và resurrection:** allowlist key, provenance, sensitive-field denylist, review trước KB publish, tombstone/deletion generation, cache invalidation và restore suppression. Consent revoke cũng hủy follow-up đang chờ.

**Budget denial-of-wallet:** per-account inbound/LLM/tool quotas, token cap, debounce, finite retries, circuit breaker, queue limits và cost reservations. Không trả quá nhiều tin “đang xử lý” hoặc vòng bot echo.

## 5. Kịch bản lỗi bắt buộc

Tắt Redis sau durable ACK → dispatcher phục hồi không mất event. Kill worker sau tool success trước persist → reconcile, không write lại mù. Provider nhận send rồi ngắt mạng → unknown → không tạo duplicate. Status delivered đến trước accepted update → không lùi trạng thái. LLM timeout khi nhân viên takeover → không gửi câu trả lời muộn. OA token refresh cùng lúc ở hai worker → một kết quả hợp lệ không bị token cũ đè.

Thu hồi KB trong lúc câu trả lời đang soạn → validator/sender policy yêu cầu regenerate hoặc handoff nếu nguồn không còn hợp lệ. Khách yêu cầu xóa trong lúc memory job chạy → tombstone chặn commit dữ liệu cũ. Cùng tên khách ở hai tenant/cùng tenant khác customer → không lộ dữ liệu. Đổi địa chỉ/giá từ nguồn trực tiếp sau approval → freshness check bắt buộc đánh giá lại.

## 6. CI và release workflow

Sau SB-02/23, PR chạy lint/typecheck, unit, contract, schema/migration tests, secret/dependency scan và build. Critical path thêm integration/security/eval subset. Scheduled/full release pipeline chạy full eval, E2E, load/chaos và restore test theo kế hoạch được owner duyệt; không tự lập automation bên ngoài chỉ từ tài liệu này.

Deployment build image immutable với commit SHA; schema migration có job duy nhất và lock; expand/contract cho thay đổi phá vỡ tương thích. Staging → QA report → owner review → deploy inactive → smoke → canary mode. Không tự sửa production DB từ console SQL của coding agent. Branch protection/review phải được owner cấu hình khi bắt đầu implementation; bộ plan này chưa thay setting repo.

## 7. Observability

Metrics: webhook_verify_fail, inbox_dispatch_lag, duplicate_events, queue_age, model/token/tool latency, retrieval_no_result, rejected_sources, handoff_pending_age, outbox_unknown/failed, provider_429, refresh_fail, purge_lag, budget_spend, policy_denied. Dashboard theo tenant/channel nhưng quyền truy cập tối thiểu.

Alert đề xuất: backlog tăng liên tục; credential revoked; bất kỳ suspected leak/action trái quyền; outbox unknown; handoff quá SLA; cost vượt 80%/100% cap; failure rate tăng so baseline. Ngưỡng vận hành cụ thể chốt từ load/pilot, không coi các default là SLA hợp đồng. Alert chỉ chứa ID truy vết, không raw transcript.

## 8. Bằng chứng bàn giao release

Commit/image SHA, migration version, model/prompt/policy/KB versions, test reports có command/log và skipped rõ, provider capability records, secret scan, 50-case human review, UAT record, backup restore log, purge/replay evidence, rates/consent/terms checklist, rollback owner và open risk register. Dữ liệu thật/evidence nhạy cảm lưu ngoài public repo; repo chỉ link access-controlled hoặc báo cáo đã khử dữ liệu.
