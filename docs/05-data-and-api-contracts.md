# 05 — Data/API hiện hành v3

Nguồn authority: [MASTER_PLAN §9](../MASTER_PLAN.md#contracts), [manifest schemas](../contracts/current.json), [wiki registry/publish](11-wiki-contract.md). Dưới đây là checklist implementation, không migration hay endpoint đã chạy.

## Khóa và constraints

UUID nội bộ; UTC timestamptz; money decimal/minor-unit + currency, không float. Tenant tables có tenant_id NOT NULL và composite FK `(tenant_id, id)`; message/fact/tool còn kiểm customer/conversation đúng scope. Runtime role không owner/BYPASSRLS. Secret chỉ reference/encrypted ciphertext; browser không nhận credential channel.

Unique constraints bắt buộc: identity `(tenant,binding,external_user_hash)`; inbox `(tenant,binding,provider_event_key)`; outbox `(tenant,idempotency_key)`; source/version/digest theo registry; page/revision; active pointer một release/tenant. Status event key có discriminator để không làm mất delivered/read vì dedup chung message ID. Tool write cùng key khác args hash trả conflict.

Core tables theo vertical slice: tenant/membership/binding → customer/identity/conversation/messages → inbox/outbox/run/tool/ticket → source registry/raw version/wiki page/patch/release → fact/candidate/summary/tombstone/audit. Session/lease/spool/gap/capability thêm ở personal task. Không dựng mọi bảng SaaS trước luồng đầu tiên.

## Event và decision

Normalized event **v2** dùng `zalo_personal`↔`personal_bridge`, `whatsapp`↔`provider_webhook`, `mock`↔`mock`. V1 giữ lịch sử không dùng cho personal. Tenant/customer quyền do server derive sau transport verification; schema shape không cấp authorization. Health/gap không giả customer message. Historical import ở no-reply job riêng.

Decision v1 là proposal reply/clarify/handoff/request_tool/no_action. Model không chọn scope/credential. Source refs phải thật, đúng ACL/effectivity và hỗ trợ statement. Request_order_change có trong design schema nhưng runtime MVP deny; monetary executor không tồn tại. Một tool name trong schema không đồng nghĩa đã enable.

## Endpoint families cần sinh OpenAPI

| Family | Quyền và invariants |
|---|---|
| GET/POST /webhooks/whatsapp/:bindingToken | Verify challenge hoặc raw provider signature; binding token chỉ định tuyến |
| POST /internal/bridges/:bindingId/events, /heartbeat | Service auth/binding/nonce/timestamp/generation/epoch; durable ACK |
| POST /v1/channels/zalo-personal/:id/login-sessions; GET /:sessionId; POST /disconnect | Owner-only, CSRF, TTL/no-store, secret không browser, revoke+fence |
| GET /v1/channels/:id/health; PUT /allowed-conversations/:threadRef | Tenant/purpose/consent, default-deny enroll, explicit resume |
| GET /v1/conversations, /:id/messages | Cursor pagination, membership/assignment scope, PII masking |
| POST /v1/conversations/:id/takeover, /resume, /replies | CAS ownership, Idempotency-Key, common outbox/policy |
| POST /v1/knowledge/imports, /patches, /reviews, /releases | Base release/revision/digest; server reviewer quyền; no direct YAML publish |
| POST /v1/knowledge/releases/:id/publish, /revoke; /search-preview | Candidate approval hash + CAS + source/ACL/tombstone epochs; no raw SQL |
| POST /v1/customers/:id/memory-corrections, /deletion-requests | Verified subject, reason/evidence, async progress, purge derivatives |
| GET /v1/runs/:id, /metrics; PATCH /v1/settings/automation | Redacted evidence; admin CAS/audit; OFF enforced sender |

Path parameters, error schemas và pagination shapes phải được Platform/Console review ở SB-03. Errors safe code/message/request_id/retryable; 404-not-visible không tiết lộ tenant khác. Mutation sử dụng If-Match/ETag khi cần và idempotency; same key different body=409. Không cung cấp arbitrary internal send endpoint cho browser/model.

## Evidence packet

Run lưu commit/config/model/prompt/KB release/policy/ownership epochs, causal event, retrieved refs/claim support, tool result_ref/as_of, validation reason và outbox status. Không lưu private chain-of-thought, raw secret hoặc cả transcript trong log. Unknown delivery khác failed; operator-marked-sent khác provider-delivered.

Approval/release/action records gắn immutable argument/content hash, actor, reviewer, expiry và scope. Artifact thay đổi phải review lại; restore hoặc rollback không được bỏ qua tombstones/ACL hiện tại.
