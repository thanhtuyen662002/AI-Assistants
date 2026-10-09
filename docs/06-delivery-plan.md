# 06 — Kế hoạch triển khai và backlog giao coding agent

Ngày baseline: 2026-10-09. Không gán ngày hoàn thành cứng hoặc coi các task đã được agent chạy. Task DAG ở [`planning/backlog.json`](../planning/backlog.json); trạng thái ban đầu TODO, riêng SB-00 BLOCKED. Lead quyết định capacity và lịch sau khi có scope/credentials; số agent không thay thế dependency.

## 1. Cách tổ chức

Tám vai trò logic: Lead, Platform, Channels, Memory, Runtime, Console, QA, Operations. Một agent có thể làm nhiều vai trò nhưng không đồng thời sửa cùng hợp đồng/lockfile. Có hai coding agent Channels thì chia SB-07/SB-08, review chung SB-09. Giữ main ổn định; mỗi task một nhánh/PR; QA độc lập review acceptance.

P0 là bắt buộc trước pilot an toàn, P1 hoàn thiện workflow/quan sát, P2 mở rộng sau pilot. Estimate dùng S/M/L để chia task, không phải thời gian hứa: S một module nhỏ, M một module với integration, L phải tách PR con nhưng giữ cùng acceptance.

## 2. Các chặng và gate

| Chặng | Task chủ đạo | Đầu ra / gate |
|---|---|---|
| G0 — Scope và nền móng | 00–05, 21, 23 bắt đầu sớm | Repo build được, contracts có version, tenant isolation, mock fixtures; nguồn chưa xác minh được ghi rõ |
| G1 — Vertical slice bằng mock | 06, 10–17 | Message → memory/KB → draft → outbox → mock delivered; takeover dừng bot |
| G2 — Hai kênh sandbox | 07–09 + tích hợp 15 | Xác thực webhook/token, policy riêng, test duplicate/window/timeout; không dùng dữ liệu thật |
| G3 — Copilot vận hành | 18–20, 22–24 | Inbox/approval/KB review/metrics, eval/red-team/restore, nhân viên duyệt mọi tin |
| G4 — Auto low-risk có kiểm soát | 25 | Pilot một tenant/kênh trước, rollback và cap; mở kênh còn lại sau gate tương tự |
| G5 — Học có duyệt | 26 | Feedback → KB proposal → review → regression → publish |

G1 có thể demo runtime bằng mock sender/policy trước khi G2 xong; chỉ SB-15 hoàn tất khi contract tích hợp thật/policy/handoff đủ dependency. Mocks không được ghi như pass sandbox.

## 3. Backlog chi tiết

### SB-00 — Đối chiếu hai clip
- Owner: Lead; P1; S; dependency: không.
- Đầu ra: bảng timestamp/evidence/mapping trong docs/00, ADR thay đổi nếu cần; không đăng video/transcript khách hoặc nội dung bản quyền dài lên public repo.
- Acceptance: xem đủ hai nội dung và truy vết được từng claim, hoặc chủ dự án ghi waiver rõ rằng đang chọn proposal độc lập. Hiện BLOCKED vì không lấy được nội dung. Không chặn scaffold; phải báo tình trạng khi nghiệm thu scope.

### SB-01 — Chốt scope pilot và input registry
- Owner: Lead; P0; S; dependency: không.
- Đầu ra: tenant profile synthetic, ngành hàng/use cases được duyệt, nguồn KB, người trực, CRM target hoặc mock, danh sách quyết định còn mở và owner.
- Acceptance: không tự tạo giá/chính sách doanh nghiệp; có nguồn dữ liệu được quyền dùng; phân biệt readiness code/sandbox/production. Checklist tài liệu 09 được gán người xử lý.

### SB-02 — Scaffold monorepo và local development
- Owner: Operations; P0; M; dependency: không.
- Đầu ra: apps/packages theo tài liệu 02, pnpm workspace, pinned toolchain, lockfile, compose DB/Redis/object storage, .env.example, scripts lint/typecheck/test/build, CI smoke.
- Acceptance: clone sạch + config local chạy mock stack; health endpoint; không cần secret production; không commit binary/dependency folder; dependency/license/security scan ban đầu.

### SB-03 — Chốt contracts và codegen
- Owner: Platform; P0; M; dependency: SB-02.
- Đầu ra: JSON Schema baseline → TS types/OpenAPI, normalized events, decision, tool registry và mock fixtures.
- Acceptance: validate valid/invalid samples, extra-property rejection, enum/version compatibility; Console/Channels/Runtime review và không duy trì schema trùng lệch.

### SB-04 — Operator auth, tenant binding và RBAC
- Owner: Platform; P0; M; dependency: SB-03.
- Đầu ra: login/session integration, membership roles, trusted context factory, channel binding registry, admin-only automation flags.
- Acceptance: tenant spoofing/role escalation/session CSRF bị chặn; auditor read-only; user không tự chọn tenant từ header; không tự viết password auth yếu khi có provider phù hợp.

### SB-05 — Database và RLS
- Owner: Platform; P0; L; dependency: SB-04.
- Đầu ra: migrations/indexes/composite FK theo tài liệu 05, runtime DB role ít quyền, encrypted fields và repos scoped.
- Acceptance: apply empty + upgrade data fixture; tenant A/B isolation qua API/worker; không owner/BYPASSRLS cho runtime; cascade/xóa không phá audit; EXPLAIN truy vấn hot path.

### SB-06 — Durable inbox, queue, outbox và replay
- Owner: Platform; P0; L; dependency: SB-05.
- Đầu ra: receipt transaction, dispatcher/sweeper, conversation serialization, leases, outbox state và mock sender.
- Acceptance: 100 lần duplicate sinh một processing intent; crash sau DB commit trước enqueue vẫn được phục hồi; worker retry không nhân action; unknown send không retry mù; không ACK trước durable write.

### SB-07 — Zalo adapter
- Owner: Channels; P0; L; dependency: SB-06.
- Đầu ra: OAuth/token manager, signature verifier, normalize, sender, capability matrix và fixtures đã ẩn secret.
- Acceptance: success + invalid signature + wrong OA + unsupported event + echo; refresh concurrent/revoked; xác minh byte canonicalization từ provider. Thiếu account ghi sandbox blocked, mock passed không thay thế account evidence.

### SB-08 — WhatsApp adapter
- Owner: Channels; P0; L; dependency: SB-06.
- Đầu ra: GET challenge, POST signature, WABA/phone binding, normalize batches, text/template sender và status mapping.
- Acceptance: đúng/sai challenge, tampered body, duplicate, nhiều messages, event out-of-order, revoked token và delivery failure; API version/capability evidence; không cài archived SDK.

### SB-09 — Channel policy, consent, throttling và budget gate
- Owner: Channels; P0; L; dependency: SB-07, SB-08.
- Đầu ra: send decision evaluator/versioned rules, template registry, consent/suppression, rate limits, budget reservations, policy UI state.
- Acceptance: WA 24h, Zalo 48h/7d boundary fixtures theo tài liệu 04; opt-out và template rejected bị chặn; recheck trước send; chưa rõ rate card không coi cost=0; human message cũng qua policy.

### SB-10 — Document ingestion và versioned KB
- Owner: Memory; P0; M; dependency: SB-05.
- Đầu ra: quarantine, text/PDF-text extraction, hash/dedup, chunk/embedding, version/review/publish/revoke.
- Acceptance: tài liệu malformed/scanned báo needs_review; nguồn/page/ACL được giữ; upload trùng không tăng version vô cớ; thu hồi loại khỏi retrieval ngay.

### SB-11 — Hybrid retrieval và source validation
- Owner: Memory; P0; L; dependency: SB-10.
- Đầu ra: lexical/vector fusion, rerank tùy chọn, Vietnamese tests, exact-search baseline, context builder và source validator.
- Acceptance: Recall@5 mục tiêu ≥90% trên tập có nhãn; ACL tenant/customer; stale/conflicting source không được auto-answer; đo index-filter recall/latency.

### SB-12 — Customer identity và liên kết có xác minh
- Owner: Platform; P0; M; dependency: SB-05.
- Đầu ra: identity per binding, ownership verification contract, linking disabled mặc định; challenge/link/unlink khi bật.
- Acceptance: trùng tên/phone tự khai không merge; cross-channel chỉ đọc chung sau evidence hợp lệ; challenge hết hạn/dùng lại bị chặn; order ownership kiểm độc lập.

### SB-13 — Customer memory lifecycle
- Owner: Memory; P0; L; dependency: SB-12.
- Đầu ra: candidate extraction/allowlist, facts/episodes/summary, conflict/supersede/TTL, correction/deletion/tombstones.
- Acceptance: preference mới thay active fact; sensitive fields bị chặn; nguồn không có không confirmed; delete + replay/job cũ/restore không tái sinh dữ liệu; customer A/B isolation.

### SB-14 — Tools và CRM/order/ticket adapter
- Owner: Runtime; P0; M; dependency: SB-05, SB-12.
- Đầu ra: allowlisted tools theo tài liệu 05, mock CRM, ít nhất một connector nguồn được chọn khi có input, idempotency/authorization/sanitization.
- Acceptance: biết order ID không đủ đọc; tenant mismatch bị chặn; API lỗi không báo success; duplicate create_ticket không tạo nhiều ticket; refund execution không tồn tại ở MVP.

### SB-15 — Workflow agent runtime
- Owner: Runtime; P0; L; dependency: SB-09, SB-11, SB-13, SB-14, SB-17.
- Đầu ra: classify/retrieve/plan/tool/draft/validate, prompt/model/config version, budget, finite retries, fallbacks và structured decision.
- Acceptance: end-to-end grounded reply, clarification và handoff; source giả bị reject; prompt injection không thêm quyền; context limit; không trả khi handoff; text/ảnh unsupported không bị mô hình bịa đã xem.

### SB-16 — Unified inbox console
- Owner: Console; P0; M; dependency: SB-03, SB-04.
- Đầu ra: list/filter conversations, thread, customer panel, draft/source evidence, status/provider errors; mock data trước backend thật.
- Acceptance: role/tenant isolation; loading/empty/error/accessibility; không expose token; hiển thị rõ draft, accepted, delivered, unknown; không hứa realtime khi mất connection.

### SB-17 — Human handoff và ownership arbitration
- Owner: Platform; P0; L; dependency: SB-06, SB-16.
- Đầu ra: claim/assign/resume, state CAS, queue/SLA timer, handoff summary, cancel pending bot intents và echo handling contract.
- Acceptance: takeover trong lúc LLM chạy chặn outbound chưa dispatch; hai nhân viên claim chỉ một thắng; bot không tự resume do hết giờ; in-flight không thể thu hồi được hiển thị minh bạch; human replies vẫn đúng policy.

### SB-18 — Knowledge và memory governance UI
- Owner: Console; P1; M; dependency: SB-10, SB-13, SB-16.
- Đầu ra: upload/version preview, approve/revoke, nguồn/ACL, customer facts + sửa/xóa, knowledge-gap inbox.
- Acceptance: editor không tự publish khi thiếu reviewer scope; xem source được phân quyền; delete progress/error rõ; version history và audit; không lộ PII ở client log.

### SB-19 — Approval workflow cho action ghi
- Owner: Runtime; P1; M; dependency: SB-14, SB-17.
- Đầu ra: proposal preview, customer confirmation khi cần, staff approval/hash/expiry, execution/reconcile trạng thái.
- Acceptance: args đổi/approval hết hạn không execute; self-approval risky action bị chặn; revalidate order/version trước write; production MVP vẫn disabled mọi monetary action.

### SB-20 — Observability và cost accounting
- Owner: Operations; P1; M; dependency: SB-06, SB-15.
- Đầu ra: redacted traces, latency/error/queue dashboards, usage ledger, cost estimates/actual reconciliation, alert routes.
- Acceptance: trace một case không raw PII; cost unknown hiển thị unknown; per-tenant budget cap/circuit breaker; không log secrets khi provider trả lỗi.

### SB-21 — Eval harness và golden dataset
- Owner: QA; P0; M; dependency: SB-03.
- Đầu ra: chuyển JSONL seed thành test runner, mở rộng ≥200 cases có nhãn bằng dữ liệu synthetic/được phép; score theo từng intent/channel/risk.
- Acceptance: tách deterministic tests và model evaluation; reference answers + allowed source IDs; 50 mẫu review độc lập; reproducible seed/config; test set không chảy vào prompt/KB để gian điểm.

### SB-22 — Security, concurrency và chaos verification
- Owner: QA; P0; L; dependency: SB-09, SB-13, SB-15, SB-17, SB-19, SB-21.
- Đầu ra: prompt-injection/ACL/IDOR/webhook/media/SSRF tests, replay/crash/timeout tests, takeover-send race, privacy purge report.
- Acceptance: zero cross-tenant/customer leakage, zero unauthorized action trong suite; lỗi nghiêm trọng chặn release; phân biệt lỗi model và code; khắc phục có regression test.

### SB-23 — CI/CD và staging + backup/restore
- Owner: Operations; P0; L; dependency: SB-02, SB-05.
- Đầu ra: CI scripts/gates, image build, migration job riêng, staging template, secrets wiring, backup policy, restore runbook.
- Acceptance: build từ clean checkout; deploy staging chỉ khi chủ dự án cấp scope/chi phí; restore DB + object + tombstones; rollback app không corrupt schema; không gọi provisioning trả phí tự ý.

### SB-24 — E2E, UAT và copilot pilot
- Owner: QA; P0; L; dependency: SB-15, SB-17, SB-18, SB-19, SB-20, SB-21, SB-22, SB-23.
- Đầu ra: báo cáo eval/load/UAT, evidence hai kênh sandbox và copilot với người vận hành, fix list và release recommendation.
- Acceptance: release gates tài liệu 07; 5 workflow thật đã đồng ý thử trên mỗi kênh; backup restore + kill switch test; code/mocks không thay provider delivery evidence; blocked credentials ghi rõ.

### SB-25 — Go-live có kiểm soát
- Owner: Lead; P0; M; dependency: SB-01, SB-07, SB-08, SB-09, SB-24.
- Đầu ra: owner sign-off, live policy/rate card/AI-use-case review, staffing/retention/alerts, rollout staged và rollback owner.
- Acceptance: tất cả hard gates; SB-00 phải được đối chiếu hoặc owner chấp nhận giới hạn/waiver; tỷ lệ auto tăng chỉ sau quan sát và review; không mở toàn bộ khách ngay; production secrets không ở Git.

### SB-26 — Feedback-to-knowledge có review
- Owner: Memory; P2; M; dependency: SB-11, SB-18, SB-24.
- Đầu ra: gap clustering khử PII → KB change proposal → owner approval → regression → canary publish.
- Acceptance: không tự publish từ lời khách; không dùng chat train model; lỗi tăng có rollback; thay KB phải giữ source/provenance và eval comparison.

## 4. Điều phối song song

Nhánh đầu: Lead SB-00/01, Operations SB-02, QA chuẩn bị seed. Sau SB-03/04, Console SB-16 và QA SB-21 chạy song song Platform SB-05. Sau DB, Memory SB-10, Platform SB-06/12, Runtime SB-14, Operations SB-23 có thể chia việc. Sau event pipeline, hai adapter kênh chạy riêng; Memory tiếp SB-11/13; Platform+Console làm SB-17. Tích hợp SB-15 sau contracts/guards sẵn; hardening/approval/observability trước UAT.

Critical path dự kiến: 02 → 03 → 04 → 05 → 06 → (07 & 08) → 09 → 15 → 22/24 → 25, nhưng memory/handoff/approval cũng có thể thành đường chậm. Lead cập nhật theo thực tế, không để task phụ thuộc chưa xong thành `done` chỉ vì mock hoạt động.

## 5. Tiêu chí hoàn thành sản phẩm

Không chỉ là “agent trả được”. Cần source-backed answer, memory correction/deletion, verified identity, policy kênh, staff takeover, idempotency/reconciliation, security suite, observability/cost cap, approved data/terms và rollback được thử. Chủ dự án quyết định production, coding agent chỉ báo bằng chứng và phần chưa đạt.
