# 02 — Kiến trúc: personal bridge + shared second brain

## Stack và ranh giới

Modular monolith + background workers bằng TypeScript; Next.js console, Fastify API, PostgreSQL + pgvector, Redis + BullMQ, S3-compatible storage. Thêm **apps/zalo-bridge** là process Node.js/container thường trực cho session/listener cá nhân. Không đặt listener trong request handler, browser console người vận hành hoặc short-lived serverless function. Chưa cài stack; SB-02 pin supported versions, lockfile và compatibility tests.

Ứng viên transport `zca-js` được đánh giá ở SB-27 (nguồn P1–P3 trong docs/10). Một account/một active bridge listener bằng DB lease + fencing epoch; standby không tự login khi không sở hữu lease. Runtime/console/LLM không cầm personal session. Không dùng cookie extraction extension làm quy trình onboarding mặc định.

```text
Zalo cá nhân → bridge listener → allowlisted CSKH filter
                                 ↓ encrypted bounded local spool
                                 ↓ authenticated internal ingest
WhatsApp → raw signature verified webhook
                                 ↓
                         durable DB inbox
                                 ↓ dispatcher/sweeper
                         queue by conversation
                                 ↓
                 auth/identity/handoff → agent workflow
                    KB + private memory + live tools
                                 ↓ validated decision
                       transactional outbox
                         ↙                ↘
                bridge command        WhatsApp sender
                session/fence         policy/template
                         ↘                ↙
                      accepted / delivered / unknown
```

## Code layout cần tạo

`apps/api`, `apps/worker`, `apps/console`, `apps/zalo-bridge`; `packages/contracts`, `db`, `auth`, `channels/zalo-personal`, `channels/whatsapp`, `channels/mock`, `identity`, `knowledge`, `memory`, `agent-runtime`, `tools`, `observability`; `infra`, `prompts`, `evals`, `tests`. Root contracts là design source, SB-03 chốt codegen một nguồn sự thật. Event hiện hành v2; không map lại enum zalo v1 thành personal.

## Ingress: hai cơ chế khác nhau

**WhatsApp:** đọc raw body/limit → validate signature/account binding → normalized v2 → commit receipt/events/dispatch cursor → ACK provider. DB lỗi không ACK thành công; không gọi LLM trong webhook. Normalize mọi message/status, không chỉ entry đầu.

**Zalo personal:** bridge nhận event từ authenticated account session, lọc 1:1/thread allowlist trước persist. Chuẩn hóa tối thiểu, bỏ raw credentials/private fields; ghi encrypted local spool có cap/retention. Gửi event đến private ingest bằng mTLS hoặc service HMAC có raw bytes, timestamp, nonce, body hash, credential/binding allowlist và fencing epoch. Server derive tenant từ credential registry, không tin payload tenant. Durable DB commit trước internal ACK; bridge chỉ xóa spool entry đã ACK. Internal signature là của bridge, **không phải chữ ký provider Zalo**.

Không có provider ACK/retry giống OA để mặc định dựa vào. Spool chỉ bảo vệ từ khi event đã tới bridge và được lưu bền; crash trước persist hoặc listener offline có thể mất sự kiện. Nếu chưa chứng minh replay/history API, ghi khoảng gap, pause auto affected binding và yêu cầu đối soát; không báo đã nhận đủ. Spool đầy/DB unavailable dài → DEGRADED/auto stop, alert không PII; không âm thầm drop rồi báo healthy. Historical replay đánh dấu riêng, cập nhật ngữ cảnh có kiểm soát, không kích hoạt tin trả lời cũ.

**Chung:** unique event key theo binding + provider message/type/status discriminator; dispatcher lease/sweeper phục hồi gap DB→queue. Worker idempotent và serialize conversation bằng persisted version; Redis lock chỉ bổ sung. Lưu provider_at/received_at riêng, timestamp watermark chỉ tăng. Unsupported/status/self echo không tạo user turn.

## Session/control plane

`DISCONNECTED → QR_PENDING → CONNECTED → DEGRADED | REAUTH_REQUIRED | PAUSED → DISCONNECTED`. QR owner-only có TTL, no-store, không telemetry/screenshot public. Success lưu secret reference/key version, increment session generation; backend không trả cookie. Heartbeat/lease epoch làm fence cả ingest lẫn send. Disconnect dừng listener, thu hồi credential bridge, purge session/QR/spool theo policy, block queued sends. Explicit operator resume mới cho auto; reconnect không tự cấp lại quyền gửi.

Upstream nêu một web listener/account và việc mở Zalo Web có thể dừng listener [P1]. Vì vậy không thiết kế active-active cùng account; không vòng reconnect để tranh phiên với chủ tài khoản. Test cụ thể mobile/PC/Web ở SB-27; không suy từ library option rằng mọi self message luôn được quan sát.

## Agent runtime

`RECEIVE → SCOPE/HANDOFF → CLASSIFY → RETRIEVE → PLAN → OPTIONAL TOOL → DRAFT → VALIDATE → OUTBOX → MEMORY CANDIDATES`. Mỗi bước có status/timeout/version, tool calls và attempts hữu hạn; default đề xuất 3 tools, 2 draft attempts, 1 approved model fallback. Model là adapter chưa chọn bằng tên cụ thể. Tool failures/source missing → clarify/handoff; không model fallback chưa duyệt xử lý dữ liệu.

LLM không chọn tenant/customer credentials/role. KB published+ACL+effective version; customer facts riêng; order/price từ live tools. Candidate không auto publish KB. Context budgets và metrics là tuning targets, không chứng minh correctness.

## Outbox và human arbitration

Persist decision+outbox+expected ownership version trong transaction. Sender recheck OFF/scope/consent/channel eligibility/session health/lease/epoch/account pause/budget/handoff ngay trước dispatch. Bridge cũng kiểm fenced authorized command, không cung cấp send endpoint arbitrary. Approved human reply qua cùng outbox/gates.

States `pending → dispatching → accepted → delivered/read` hoặc `failed/blocked/unknown`. Provider acceptance không delivery. Zalo không có verified receipt capability thì chỉ accepted/unknown; không tự tạo delivered. Timeout sau write → unknown, reconcile nếu có ID/evidence; không retry mù. Không hứa exactly-once end-to-end.

`isSelf` event: đối chiếu outbox/provider IDs để nhận echo của hệ thống; self event không map chắc là manual human activity → tăng ownership version/takeover bảo thủ. Không discard toàn bộ self events vì sẽ bỏ lỡ người can thiệp. Nếu ID correlation mơ hồ hoặc self visibility thiếu → pause auto, không đoán. Tin đã in-flight trước takeover có thể không thu hồi được; console ghi rõ.

## Security/operations

Môi trường local mock, controlled account tests và production tách secret/data. Runtime DB role không owner/BYPASSRLS; composite tenant FK/RLS; cached private data có tenant/customer/ACL version. Bridge credential map account/binding, local spool mã hóa và áp deletion tombstone; không gửi personal history về telemetry.

Logs chỉ IDs, versions, reason codes; trace receipt→run→tool→outbox. Circuit breakers theo channel/account; bridge liveness/gap/unknown/account restriction metrics. Kill switch vẫn giữ inbound được phép nếu an toàn. Restore môi trường cô lập với sender tắt, suppression/tombstones trước reconnect. Account banned/challenged không cố vượt; owner dùng quy trình chính thức hoặc manual copilot.

ADR-001 relational+vector; ADR-002 bounded single runtime agent; ADR-003 transport-specific ingress/policy; ADR-004 durable inbox/outbox nhưng no-loss/exactly-once có giới hạn; ADR-005 private customer memory + reviewed KB; ADR-006 container portable; ADR-007 Zalo personal thay OA theo yêu cầu; ADR-008 một fenced listener/account và explicit manual fallback.
