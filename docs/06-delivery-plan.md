# 06 — Backlog hiện hành: 28 task cho Zalo cá nhân + WhatsApp

Cập nhật theo chủ dự án 2026-10-09: **không OA**. 27 task gốc giữ ID; SB-07 đổi thành Personal Bridge, thêm SB-27 kiểm chứng connector trước khi gắn account thật. Vai trò/size là thiết kế giao việc, không agent đã được assign/chạy. Source truth máy đọc: planning/backlog.json. Docs/10 ghi quyết định/caveats.

## Trình tự và dependency

G0: scope SB-01 + scaffold SB-02 → contracts SB-03; lúc này Channels làm **SB-27** sớm, Platform auth/DB, Console UI, QA dataset. G1: memory/tools/inbox-outbox với mock → luồng có draft/handoff. G2: Zalo personal controlled account tests và WhatsApp sandbox, **không gọi cả hai là official sandbox**. G3: copilot/operator UAT/security/restore. G4: auto low-risk có owner sign-off và đủ account/capability/privacy gates. G5: feedback-to-KB có duyệt.

SB-27 implementation assessment/fixtures có thể chạy với mock trước. Live QR cần owner chủ động cho phép và risk/terms review; nếu blocked không tự đổi scope về OA. Các module độc lập tiếp tục. SB-07 hoàn thành production capability chỉ khi có evidence, không nhầm mocks với live integration.

## Task chi tiết

| ID / Vai trò / ưu tiên / size | Phụ thuộc | Đầu ra và acceptance bắt buộc |
|---|---|---|
| SB-00 Lead P1 S — Đối chiếu hai clip | — | Timestamp/evidence→ADR/task; hiện blocked, không tự bịa transcript. Owner có thể chấp nhận proposal độc lập nhưng không coi là đã xem clip. |
| SB-01 Lead P0 S — Scope và input registry | — | Ghi Zalo personal đã xác nhận; ngành hàng/KB/CRM/support/consent còn cần owner. Không hỏi lại OA; không bịa policy. Tách code/mock/controlled-account/production readiness. |
| SB-02 Operations P0 M — Scaffold | — | Monorepo, pinned toolchain/lockfile, apps/api/worker/console/**zalo-bridge**, DB/Redis/storage compose, env và lint/typecheck/test/build/CI smoke. Clean checkout chạy mocks không secrets. |
| SB-03 Platform P0 M — Contracts/codegen | 02 | Event v2 zalo_personal+transport, decision v1, OpenAPI/internal bridge protocol, fixtures. Invalid/extra fields/mismatched transport rejected; review Channels/Runtime/Console; không hai nguồn schema lệch nhau. |
| SB-04 Platform P0 M — Auth/binding/RBAC | 03 | Operator sessions/memberships, service auth per binding, owner QR permissions, trusted context. Tenant spoof/CSRF/role escalation/QR access của người khác bị chặn. |
| SB-05 Platform P0 L — DB/RLS | 04 | Bảng/indexes/FKs theo docs/05, runtime least privilege; session refs/leases/allowlists/gaps; empty+upgrade migrations, cross-tenant/customer tests, EXPLAIN. |
| SB-06 Platform P0 L — Inbox/outbox/replay | 05 | Durable receipts, dispatcher/sweeper/leases, bounded encrypted bridge spool contract, idempotent jobs. Duplicate 100 lần một logical action; recover DB→queue; unknown không retry mù; gap không tự hết. |
| SB-07 Channels P0 L — Zalo Personal Bridge | 06,27 | QR owner/session encryption, one listener/fencing, allowlisted 1:1 receive/send, self-event correlation, health/gap/revoke. Không OA endpoints/token. Reject stale epoch, revoke/collision an toàn, evidence real-account riêng; chưa kiểm thì blocked. |
| SB-08 Channels P0 L — WhatsApp adapter | 06 | GET challenge/POST raw signature, WABA/phone mapping, batch normalize/send/status; API version/fixtures. Test tampered body, wrong binding, token revoked, delivery failure, duplicate/out-of-order. |
| SB-09 Channels P0 L — Channel policy/consent/budget | 07,08 | Personal gates session/epoch/allowlist/gap/self visibility/account pause; WhatsApp 24h/template/rates. Opt-out queued bị chặn; no OA 48h/7d; no unlimited/free assumption; human sends cũng qua gates. |
| SB-10 Memory P0 M — Ingest/versioned KB | 05 | Quarantine, text/PDF-text extraction, hash/chunk/embed, review/publish/revoke. Source/page/ACL giữ đủ; malformed/scanned needs_review; revoke loại ngay. |
| SB-11 Memory P0 L — Hybrid retrieval | 10 | Vietnamese lexical+vector+rerank tùy chọn, exact baseline, context/source validator. Recall@5 target ≥90%; customer/tenant ACL, stale/conflicting sources không auto-answer. |
| SB-12 Platform P0 M — Identity/link | 05 | Identity theo binding, ownership verification, link disabled mặc định. Không merge qua tên/phone tự khai; link có proof/TTL/revoke; order authorization độc lập. |
| SB-13 Memory P0 L — Memory lifecycle | 12 | Candidates/allowlists/facts/episodes/summaries/conflicts/TTL/correction/purge. Provenance; sensitive data denied; delete+replay/job/**bridge spool**+restore không tái sinh; lọc personal thread trước memory. |
| SB-14 Runtime P0 M — Tools/CRM | 05,12 | Allowlisted typed tools, mock order/CRM và adapter nguồn khi owner chọn; idempotency, sanitization. Biết order ID không đủ; timeout không success; duplicate ticket một logical record; no refund execution. |
| SB-15 Runtime P0 L — Agent workflow | 09,11,13,14,17 | Bounded classify/retrieve/tool/draft/validate, model/prompt versions/budgets/fallbacks. Fake sources/injection bị reject; missing evidence clarify/handoff; no late bot send/no historical reply/unsupported-media hallucination. |
| SB-16 Console P0 M — Unified inbox | 03,04 | Threads/customer/source/drafts/status, mock-first; thêm personal health/QR owner-only/thread enrollment/gap. Role isolation, loading/error/accessibility; phân biệt accepted/delivered/unknown, không token browser. |
| SB-17 Platform P0 L — Human handoff | 06,16 | Claim/assign/resume CAS, cancel pending intents, SLA/summary, self-echo resolver. Unmatched self events takeover; test mobile/PC/Web visibility; chưa chắc không auto song song. Two claims one winner; reconnect không resume; in-flight limits hiển thị. |
| SB-18 Console P1 M — KB/memory governance | 10,13,16 | Upload/version/review/revoke, ACL/source preview, facts correction/deletion/gaps. Editor thiếu reviewer không publish; progress/audit và PII masking. |
| SB-19 Runtime P1 M — Approval workflow | 14,17 | Preview/customer confirmation/staff approval hash/expiry, execute/reconcile. Args changed/expired/self-approval risky bị chặn, fresh source reread; monetary execution disabled. |
| SB-20 Operations P1 M — Observability/cost | 06,15 | Redacted traces/dashboards/usage ledger; bridge heartbeat/gap/restriction/stale epoch/spool depth, cost unknown/estimate/actual. Secrets không log; account/tenant caps/circuit breakers. |
| SB-21 QA P0 M — Eval harness | 03 | Seed→≥200 labeled synthetic/authorized cases, source targets; separate deterministic/model eval, 50 independent human reviews. Không làm lộ expected answers vào KB; không gọi seed thành application tests passed. |
| SB-22 QA P0 L — Security/chaos | 09,13,15,17,19,21 | ACL/IDOR/injection/SSRF, WhatsApp forgery, bridge auth/epoch/nonce, crash/spool/gap, QR/session leak, privacy allowlist, deletion, takeover/send race. Zero leak/unauthorized action; regression cho mọi blocker. |
| SB-23 Operations P0 L — CI/staging/restore | 02,05 | CI/build/migrations, long-running bridge template/one-listener failover, secret and encrypted spool volumes, restore with senders OFF. No self-provision paid services; restore tombstones before reconnect. |
| SB-24 QA P0 L — E2E/UAT/copilot | 15,17,18,19,20,21,22,23 | Full reports/load mocks/UAT; ≥5 agreed workflows mỗi kênh. Zalo personal controlled account not official sandbox; verify manual mobile reply interference. Kill switch/restore/deletion evidence; thiếu account ghi blocked. |
| SB-25 Lead P0 M — Controlled go-live | 01,07,08,09,24,27 | Owner sign-off source caveat/scope/privacy/support; personal account-risk/terms/capability review; WhatsApp rates/terms. No OA dependency. Open auto only eligible cohort after hard gates; unknown gap/self visibility blocks; no promise no-ban. |
| SB-26 Memory P2 M — Feedback→KB | 11,18,24 | PII-reduced gaps→proposal→review→regression→canary→rollback; no autonomous policy learning from private chat or model training with customer data. |
| SB-27 Channels P0 M — Personal feasibility spike | 03 | Upstream version/license/dependency audit, capability matrix, login/listen/send/revoke/fencing/self-visibility/gap fixtures, risk/terms record. Owner authorization trước live QR; unsupported/unverified rõ, không gọi unofficial thành approved. Kết luận go/no-go cho bridge; manual fallback không báo fully integrated. |

## Triển khai song song

Lead SB-01/00 và Operations SB-02; sau contracts, Channels SB-27, Console SB-16 và QA SB-21 trong khi Platform SB-04/05. Sau DB, Memory SB-10 và Platform SB-06/12, Runtime SB-14, Operations SB-23 có thể phân nhánh. Channels chia personal/WhatsApp; Platform+Console làm handoff; Runtime tích hợp SB-15 khi gates sẵn. Mock vertical slice có thể demo sớm nhưng không đánh SB-07/09/24 done trước evidence.

Không dùng số ngày cứng làm cam kết. Một task/một PR; L tách PR con nhưng giữ acceptance. Root lockfile/contracts có một owner review; không sửa test expectation để che thiếu capability. Mẫu report: task/status/files/commands thật/evidence/blocked inputs/rollback/dependency opened. Mọi P0 leak/wrong identity/unsafe action chặn release dù điểm trung bình tốt.
