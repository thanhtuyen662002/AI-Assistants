# 05 — Data/API contracts hiện hành

Đặc tả logic, chưa migration/runtime. Zalo hiện là **zalo_personal**, WhatsApp giữ Cloud API. Event v2 trong `contracts/normalized-event.v2.schema.json` là contract hiện hành; v1 giữ nguyên như lịch sử baseline OA, không đổi meaning và không gửi v1 personal. Decision schema v1 giữ nguyên, server vẫn authorize từng trường/action.

## 1. Bất biến dữ liệu

UUID nội bộ, UTC timestamptz, money decimal/minor-unit+currency không float. Bảng tenant-scoped có tenant_id NOT NULL; composite FKs (tenant_id,id), customer/conversation ràng buộc cùng scope. Runtime DB role không owner/superuser/BYPASSRLS. Optimistic versions cho resources mutable, secrets chỉ encrypted references. PII encrypted; indexed lookup hash keyed theo tenant khi cần. JSONB không thay constraint/query fields cần index.

## 2. Mô hình bảng

| Bảng | Fields/constraints chính |
|---|---|
| tenants / operators / memberships | mode, policy/budget refs; auth subject/role/scopes; server derives tenant từ membership |
| channel_bindings | channel enum hiện hành, external account ID encrypted/hash, implementation/version, credential_ref, status, policy_version; không gán cùng external account hai tenant trái phép |
| personal_sessions | binding_id, encrypted_secret_ref, generation, state, last_auth_at, revoked_at; không token raw/QR lâu dài |
| bridge_instances / listener_leases | binding, service credential ref, instance, epoch, lease_until, heartbeat, state; một active lease/account; stale epoch bị từ chối |
| conversation_allowlists | binding, external_thread_id_hash, permitted purpose, owner/reason, status, consent_ref; default deny personal thread |
| ingestion_gaps | binding, observed_from/to, reason, recovery_status/evidence, reconciled_by; gap không tự resolved do reconnect |
| bridge_spool (local encrypted store) | stable event ID, binding, generation, epoch, payload ciphertext, created/expiry, ACK cursor, deletion generation; bounded/quota và purge |
| customers / channel_identities | customer_id, binding_id, external_user_id encrypted/hash, verification_level; unique tenant+binding+external ID; không phone/name matching tự động |
| identity_links / consents | verifier/evidence/TTL/revocation; purpose-specific consent/suppression, audit mọi thay đổi |
| conversations | customer/binding, mode, ownership_state/version, assigned_operator, timestamps, ingestion coverage, external-thread key; timestamps tăng bằng max |
| messages | conversation, provider/client message IDs khi có, direction/kind, content ciphertext, provider/received_at, delivery_state, origin_evidence; unique key theo capability provider |
| inbox_receipts / normalized_events | authenticated transport metadata, external dedup key, receipt/dispatch state/lease; immutable event v2; bridge nonce replay và causal message dedup khác nhau |
| agent_runs | causal event, state, model/prompt/config versions, context/source refs, usage, validated decision, ownership version; không chain-of-thought |
| outbox_intents | stable idempotency key, content ref, expected ownership/session generation/epoch, send state/provider IDs; unknown không tự pending |
| tool_executions | name/version, action ID, argument hash, trusted scope, idempotency, sanitized result_ref/as_of/state |
| approvals / tickets | action hash/expiry/approver/state; case ref/reason/priority/due_at/reopen; không báo success khi chưa thực hiện |
| documents / versions / chunks / embeddings | owner, ACL, active version, review/effective dates; published immutable; source locator/hash; model/version/dimension; reject revoked source trong query/validator |
| memory_facts / candidates | customer/key/value encrypted, provenance/verification, purpose/status/TTL/supersedes/generation; candidates không tự publish KB |
| episodic_memories / summaries | case/conversation, source refs/watermark/as_of, generation; invalidate khi source xóa/sửa |
| knowledge_gaps / feedback | reason, corrected source, reviewer/triage; không copy personal chat sang global KB |
| audit_events | actor/operation/resource/time/reason/hash; append-only runtime permissions; no raw PII/secret |
| deletion_requests / tombstones | verified subject, generation, suppression ref, purge status; phủ bridge spool và restore |
| cost_ledger | run/intent/provider/category/market/quantity/rate_version/currency/estimate/actual; unknown khác 0 |

Index hot path theo tenant+binding+conversation/event, migration/recovery test và EXPLAIN bắt buộc SB-05. Session fields của personal không đưa vào global model context hoặc API listing của operator thường.

## 3. Event v2 và trust

Envelope: schema_version=2.0; event_id, event_type, tenant_id, channel, channel_binding_id, external_user_id, provider_event_key, occurred_at, received_at, source_transport, payload. Channels `zalo_personal`, `whatsapp`, `mock`; source_transport lần lượt `personal_bridge`, `provider_webhook`, `mock`. JSON Schema kiểm matching channel/transport, nhưng không chứng minh authorization.

Event types: inbound.message, outbound.echo, delivery.status, customer.opt_out, channel.interaction. Payload text cần message_id/message_kind/text; unsupported media chỉ media_ref private đã kiểm. Echo là self activity cần resolver; không mặc định human hay bot. Status chỉ phát nếu capability có evidence; personal không bịa delivered/read. Channel/session health không nhét vào event hội thoại thiếu customer; dùng control plane riêng.

Bridge gửi transport envelope raw/minimal không được tự cấp tenant. Server verify mTLS/HMAC credential, nonce/timestamp/body hash, binding allowlist/session generation/listener epoch; sau đó dựng normalized event. HMAC bridge không phải chữ ký Zalo. WhatsApp verify raw provider signature trước dựng envelope. Event private/historical chưa được cho phép không được đưa vào runtime; historical imports vào ingestion job riêng no-reply, không endpoint inbound live.

Dedup: message key = binding + provider ID (hoặc stable semantic hash đã kiểm chứng khi ID thiếu); status = message ID + status + event discriminator, tránh làm mất trạng thái sau. Nonce hết hạn chống replay transport không thay causal dedup; retry hợp lệ dùng nonce mới nhưng cùng event key. Unknown type → quarantine tối thiểu/no LLM. Channel health/gap không giả thành customer message.

## 4. AgentDecision v1

`kind` reply/clarify/handoff/request_tool/no_action; intent, answer_text, source_refs, proposed_tool_calls, memory_candidates, handoff_reason, risk. Schema bắt hình dạng; server kiểm actual source existence/ACL/effective time, grounded claims, tool registry/scope, memory allowlist/provenance và current modes. Model risk score không cấp quyền. Model không chọn tenant/customer/credential; không private reasoning traces. Monetary execution vẫn không có trong MVP.

## 5. REST / control plane

Mọi operator API auth+membership+RBAC, rate limit, request ID; mutable resource dùng ETag/If-Match/CAS. POST side effect Idempotency-Key; same key+different body hash=409. Cursor pagination và redaction. Error 400/401/403/404-not-visible/409/422/429/503 không lộ resource tenant khác.

| Endpoint đề xuất | Điều kiện |
|---|---|
| GET/POST /webhooks/whatsapp/:bindingToken | GET challenge; POST raw provider verification, binding token chỉ định tuyến |
| POST /internal/bridges/:bindingId/events | Private service auth, body limits, timestamp/nonce/epoch/binding, durable commit trước internal ACK |
| POST /internal/bridges/:bindingId/heartbeat | Service auth+epoch; không tự resume mode, gap vẫn mở |
| POST /v1/channels/zalo-personal/:id/login-sessions | Owner/admin, CSRF/idempotency/rate limit; QR ephemeral session, không cookie trả browser |
| GET /v1/channels/zalo-personal/:id/login-sessions/:sessionId | Owner scope; no-store QR/status, TTL; không logs/screenshots |
| POST /v1/channels/zalo-personal/:id/disconnect | Owner/admin, revoke/fence/purge/block queued send |
| GET /v1/channels/:id/health | Authorized operator; state/gaps/capabilities, không secret |
| PUT /v1/channels/:id/allowed-conversations/:threadRef | Owner/purpose/consent; server validate scope, deny by default |
| GET /v1/conversations, /:id/messages | Tenant+assignment/customer privacy; không full-account export |
| POST /v1/conversations/:id/takeover, /resume | Ownership CAS; explicit resume, không auto do reconnect |
| POST /v1/conversations/:id/replies | Assigned operator, outbox/policy; manual external send được đánh dấu riêng, không giả delivery |
| GET /v1/customers/:id/memories | Masked PII/source/status/expiry; đúng customer |
| POST /v1/customers/:id/memory-corrections, /deletion-requests | Evidence/verification/reason, async purge status |
| POST /v1/identity-links/challenges, /verify, /revoke | Single-use TTL/rate limit/anti-enumeration; not enabled mặc định |
| POST /v1/knowledge/uploads, /:id/versions, /versions/:id/publish, /revoke | Quarantine/editor/reviewer, ACL/active version/cache invalidation |
| POST /v1/knowledge/search-preview | Cùng retrieval ACL, không arbitrary SQL |
| GET /v1/approvals; POST /:id/approve, /reject | Args hash/expiry/role/separation cho risky action |
| GET /v1/runs/:id, /v1/metrics; PATCH /v1/settings/automation | Redacted traces; admin CAS/audit OFF at sender |

Không tạo POST /webhooks/zalo như OA ingress. Internal control/sender commands không public; credential không cho browser gọi send trực tiếp. Authenticate service does not bypass customer consent, deletion hoặc ownership.

## 6. Tools và actions

search_knowledge đọc published ACL; get_order_status cần order ownership qua trusted context; get_product_availability đọc live catalog/as_of; create_support_ticket là low-risk write có khách xác nhận và idempotency. request_order_change ở V1 cần preview/customer confirm/staff approval bound to argument hash, expiry/freshness/source version. request_refund chỉ tạo yêu cầu/handoff, không monetary side effect.

Tool schema strict, allowlisted network/arguments/results, max response size/timeout, sanitized error. Model không gửi secret/arbitrary URL/SQL. Write: persisted proposal → validation → customer confirmation khi cần → approval → reauthorization/live freshness → idempotent execute → sanitized result/audit. Ambiguous downstream write = unknown/reconcile; không để LLM quyết retry side effect.

## 7. States và tests

Conversation bot_active→handoff_pending→human_active→resolved; explicit resume mới bot_active. Personal session như docs/02, gap/restricted chặn auto. Outbox pending/dispatching/accepted/delivered/read/failed/blocked/unknown theo evidence. KB draft/processing/review_required/published/superseded/revoked; memory candidate/confirmed/rejected/superseded/expired/deleted; approval pending/approved/rejected/expired/executed/failed/unknown.

Test JSON valid/invalid từng event, channel-transport mismatch, extra secrets, text thiếu text, Unicode/timestamp; event v1 personal rejected. Integration phải kiểm stale epoch/cross-binding credential forgery, nonce replay/cross-customer, deletion in spool, self echo vs human, gap/resume, idempotency/arg hash, private RLS, schema migration. Chưa có test application chạy ở lần sửa tài liệu.
