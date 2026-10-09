# 07 — Chất lượng, bảo mật và release gates hiện hành

Các chỉ số là mục tiêu cần đo, không kết quả application đã đạt. Phạm vi Zalo cá nhân theo docs/10; không yêu cầu OA token/cửa sổ OA/official Zalo sandbox. Hai clip chưa có nội dung vẫn giữ caveat.

## 1. Test pyramid và dataset

Unit: fake clock, policy, state/ownership/session transitions, redaction, cost/memory conflicts. Contract: event v2 channel/transport, decision v1, tools/OpenAPI, bridge command/service authentication; reject extra fields/secrets. Integration: DB thật/RLS/FKs, queue/outbox/spool, lease fencing, tombstones/objects. E2E: mocks trước, real-account controlled Zalo tests và official WhatsApp sandbox riêng sau. Model eval: correctness/grounding/clarify/tool/memory/tiếng Việt. Security/chaos: account privacy, signatures/service credentials, prompt injection/IDOR, worker crash, gap/unknown-send/takeover/restore. UAT: nhân viên và recipients đồng ý thử.

`evals/golden-cases.jsonl` chỉ seed kịch bản `fixture_status=to_implement`, chưa test runtime. SB-21 mở rộng ≥200 cases có nhãn: 60 FAQ/policy, 30 order/tool, 25 memory/identity, 25 handoff/approval, 20 channel/session, 20 injection/privacy, 20 failure/retry. Gồm Vietnamese dấu/không dấu/lỗi chính tả/emoji/mã hàng và English. Mỗi case cần concrete fixtures, tenant/customer, allowed source refs, expected/forbidden behavior và severity. Tách held-out set khỏi KB/prompts; 50 mẫu human review độc lập. Model judge không là oracle duy nhất.

## 2. Metrics và mẫu số

Grounded correctness = lượt in-scope trả đúng và đủ bằng chứng / toàn bộ lượt in-scope cần trả lời; abstain sai không tính đúng. Unsupported claims / tất cả factual claims, báo counts và denominator. Recall@5 có ít nhất một source đích trong 5 kết quả, tách stale/conflicts. Required-handoff recall theo case bắt buộc, riêng yêu cầu trực tiếp và manual takeover tests báo riêng.

Containment chỉ case resolve không reopen sau 24h, không xem user bỏ đi là success. Latency tách channel transport delay, durable ACK, queue, retrieval/model/tool/outbox/provider. Personal coverage gap không biến thành latency=0 hoặc uptime healthy. Mocks load target 10 inbound/s ×10 phút, 50 conversations: **không chạy traffic này vào Zalo account thật**. Cost gồm model/channel/infra, unknown khác 0.

## 3. Hard release gates

| Gate | Điều kiện |
|---|---|
| Q01 Scope/nguồn | Zalo personal đã xác nhận; business/KB/consent được owner duyệt; SB-00 đối chiếu hoặc owner ghi chấp nhận proposal độc lập |
| Q02 Channel readiness | SB-27/07 personal version/license/capability/account-risk/terms review và controlled-test evidence; WhatsApp policy/rates/template/terms/version riêng. Không coi owner approval là platform approval |
| Q03 Scope isolation | 100% deterministic cross-tenant/customer/binding tests pass; zero leak/unauthorized tool action; private personal threads không persisted/LLM/embeddings/logs |
| Q04 Answer quality | ≥200 cases, ≥90% grounded correctness, ≤2% unsupported claims, ≥90% Recall@5, 50 human-reviewed samples |
| Q05 Human control | ≥95% required handoff; direct request/takeover race 100%. Personal self visibility kiểm mobile/PC/Web theo cách dùng; chưa chắc thì chặn AUTO song song, không tự resume reconnect |
| Q06 Reliability/coverage | Duplicate 100 lần không thêm action; durable DB→queue/spool recovery; stale epochs denied; unknown-send không retry mù; disconnected gap hiển thị và auto pause, không hứa no-loss trước bridge persist |
| Q07 Latency/tải | Mocks backend ingest p95≤1s, text response p95≤10s khi dependencies khỏe; report bottlenecks, real-account kiểm có kiểm soát không stress/flood |
| Q08 Privacy/secrets | QR owner-only TTL/no-store, encrypted session/spool, private thread default deny, purge/replay/restore suppression tests; no secrets/PII public repo/log |
| Q09 Operations | Account-health/lease/spool/gap/restriction alerts, on-call/support, cost caps, per-binding kill switch, staging separation, restore evidence |
| Q10 Rollout | Owner explicit enable, approved cohort/intent, rollback rehearsal; session restricted/challenge/unresolved gap/self visibility unknown đều block auto |

Một P0 leak/wrong identity/unsafe action chặn go-live dù điểm trung bình cao. Không phép nào bảo đảm unofficial connector không bị khóa; không báo platform compliant hoặc no-ban từ test pass. Manual copilot fallback phải ghi chưa auto-integrated.

## 4. Threat model

**Personal session/QR:** owner-only auth, CSRF, TTL/no-store, no screenshot capture/telemetry, secrets encryption/KMS rotation, restricted filesystem/service identity. QR/session là khả năng truy cập account, không đưa vào LLM/chat/Git. Disconnect/revocation invalidates session generation và listener epoch; credential cũ không replay send. Không restore revoked session từ backup.

**Private life contamination:** filter business allowlist trước local spool/backend/LLM; group/friends/private history default excluded. Consent xử lý chat CSKH không đồng nghĩa đọc mọi thứ trong account. Import lịch sử phải owner-selected range/purpose và historical no-reply pipeline riêng. Memory không tự chuyển private chat sang KB dùng chung.

**Bridge spoof/replay:** per-binding service auth mTLS/HMAC raw bytes/timestamp/nonce/body hash; trusted server registry derives tenant; stale lease/epoch rejected. Internal HMAC không chứng minh Zalo ký event, bridge compromise là trust boundary thật. WhatsApp dùng provider signature raw body/constant-time compare và đúng WABA/phone mapping. Binding URL token không auth.

**Prompt injection/IDOR:** typed allowlisted tools, strict schemas, untrusted content chỉ dữ liệu; scoped repositories/RLS/composite FKs và customer filters. Tách runtime DB khỏi migration admin. Cache key tenant/customer/ACL/KB version; object refs có quyền; không global cache private answer. Không shell/SQL/arbitrary browser/network tools cho bot.

**Actions và human race:** server policy/authorization/approval bound args hash/expiry, downstream idempotency/freshness/reconciliation. Outbox fence cả ownership và bridge epoch. isSelf matched system echo không reply; unknown self activity takeover bảo thủ; không ignore all self messages. In-flight có thể không hủy; UI phải phản ánh.

**Media/SSRF:** no arbitrary media fetch ở MVP; về sau allowlist, block private/loopback/link-local/metadata, kiểm redirect/DNS rebind/size/MIME/time, malware quarantine/sandbox extraction. Không execute file khách. Images chưa đọc không được LLM bịa đã thấy.

**Memory resurrection:** allowlist keys/provenance/sensitive denylist, KB publish human review, deletion generation/tombstones xuyên summary/vector/cache/jobs/**bridge spool**/exports/restore. Consent revoke hủy pending follow-up. Legal hold/retention cần quyết định owner có căn cứ, không mặc định vĩnh viễn.

**Account/financial abuse:** per-account bounded queue/LLM/tool budgets/circuit breaker, no spam/friend scraping/bulk/group, no anti-bot evasion/CAPTCHA bypass/proxy or account rotation to evade restrictions. Low send rate giảm tải nội bộ, không hứa account safety. Unknown fee không 0; model fallback phải được duyệt xử lý dữ liệu.

## 5. Chaos/race scenarios bắt buộc

Bridge chết trước event persist → coverage gap có thể mất tin, không báo recovered nếu không proof. Sau spool persist trước internal ACK → retry dedup. DB commit trước queue enqueue → sweeper recover. Spool full/offline dài → health degraded, auto pause và alert. Duplicate/stale lease làm hai bridge cùng chạy → chỉ epoch hợp lệ được server/sender chấp nhận, process lỗi dừng. Owner mở Zalo Web → session conflict, không reconnect war.

Manual mobile/PC message trong lúc LLM chạy → takeover khi observed; observation unsupported → production gate ngăn auto mode đó. Outbound accepted rồi timeout → unknown, no blind resend. Delivery status đến ngược thứ tự → không lùi. Account challenge/restriction → pause, owner official recovery, không tự vượt.

KB revoke khi đang draft → validator loại nguồn/regenerate/handoff. Delete request khi memory/spool job đang chạy → tombstone chặn resurrection. Consent/thread allowlist revoke khi queued → chặn dispatch và purge nội dung theo policy. Restore offline old inbox → historical no-send, suppression trước reconnect.

## 6. CI/release/observability

PR: lint/typecheck, unit/contracts/schema/migration/security scans/build sau scaffold thật. Release: integration/security/full eval/E2E/UAT/load mocks/restore drill. Mọi skipped integration ghi rõ không pass. Pin commit/image/model/prompt/policy/KB/connector versions; migration job riêng có lock, expand/contract; staging→QA→owner→inactive deploy→canary. Không tự paid provision hoặc production SQL.

Dashboards: failed service auth/signature, session heartbeat/epoch, listener conflict, account restriction, private-event drops (counts only), spool depth/age/full, ingestion gap duration, inbox lag/duplicates/queue age, retrieval/source rejections, model/tool latency/tokens, handoff age, outbox unknown, purge lag, costs. Alert không raw message/QR/session. Soft cap 80% là tuning proposal, hard cap owner-set.

Release evidence: real executed commands and reports, fixtures sanitized, version records, 50-case human review, owner account-risk/terms/privacy sign-off, per-client self visibility, known gaps, rate cards, kill switch, purge/restore/rollback, open blockers. Giữ nhạy cảm ngoài public repo. `planning/validation-report.md` là báo cáo **baseline cũ** cho assets khi đó, không chứng nhận revision personal hay runtime.
