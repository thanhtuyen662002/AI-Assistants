# 05 — Mô hình dữ liệu và hợp đồng module

Đây là thiết kế logic, **không phải migration đã chạy**. SB-03/SB-05 sinh migration, OpenAPI và contract tests; review schema trước khi các agent tích hợp.

## 1. Quy tắc schema

ID nội bộ dùng UUID; thời gian dùng UTC `timestamptz`, tiền dùng decimal hoặc minor units + currency (không float). Mọi bảng chứa dữ liệu tenant có `tenant_id NOT NULL`, timestamp tạo/cập nhật, optimistic version khi mutable. Composite foreign keys `(tenant_id, id)` chống tham chiếu chéo tenant; customer-scoped record còn ràng buộc customer của conversation.

JSONB không thay các field cần index/constraint. Không lưu token raw; chỉ secret reference/ciphertext + key version. Hash/encrypt định danh; lookup hash có key riêng theo tenant khi cần, raw values chỉ decrypt cho mục đích được phép. Index và constraint phải được kiểm bằng EXPLAIN/test ở tải thử.

## 2. Bảng cốt lõi

| Nhóm / bảng | Field quan trọng ngoài tenant/id | Constraint / ghi chú |
|---|---|---|
| tenants | name, status, mode, retention_policy_id, budget_config | Không cho client tùy ý đổi tenant |
| operators, memberships | auth_subject, role, scopes, active | Membership theo tenant; role owner/admin/agent/reviewer/auditor |
| channel_bindings | channel, external_account_id, app_id, credential_ref, policy_version, status | Unique channel + external_account_id theo mô hình provider; không bind cùng account cho hai tenant trái phép |
| customers | display_name_encrypted, status, deletion_generation | Identity nội bộ, không lấy phone làm PK |
| channel_identities | customer_id, channel_binding_id, external_user_id_encrypted/hash, verification_level | Unique tenant + binding + external user; evidence linking riêng |
| identity_links | source_identity_id, target_identity_id, verifier, evidence_ref, consent_ref, expires_at, revoked_at | Không tự merge bằng tên/LLM |
| consents | customer_id, channel_binding_id, purpose, status, source_ref, recorded_at, revoked_at | Purpose-specific; append audit cho thay đổi |
| conversations | customer_id, binding_id, mode, ownership_state, assigned_operator_id, ownership_version, last_customer_message_at, last_eligible_interaction_at | State transition atomically; timestamps dùng max với event đến muộn |
| messages | conversation_id, provider_message_id, direction, kind, text_ciphertext, provider_at, received_at, delivery_state | Unique tenant + binding + provider_message_id + direction khi provider semantics yêu cầu |
| inbox_receipts | binding_id, provider_event_key, body_ref/hash, verified_at, received_at, dispatch_state, lease_until | Unique tenant + binding + event_key; tách event message và status |
| normalized_events | receipt_id, event_id, event_type, payload, occurred_at, causal_ref | Event envelope v1; immutable, retention-aware |
| agent_runs | conversation_id, causal_event_id, state, model/prompt/config_version, context_refs, usage, validated_decision, ownership_version | Retry có attempt riêng; không dùng opaque chain-of-thought làm audit |
| outbox_intents | causal_event_id, conversation_id, kind, idempotency_key, content_ref, state, provider_message_id, lease, expected_ownership_version, policy_version | Unique tenant + idempotency_key; unknown không tự reset pending |
| tool_executions | run_id, tool_name/version, argument_hash, scope, idempotency_key, result_ref, state, as_of | Scoped auth và sanitized result; write attempt lưu intent trước side effect |
| approvals | action_id, requester, approver, argument_hash, expires_at, state, approved_at | Approver role hợp lệ; request đổi args phải tạo approval mới |
| tickets | customer_id, conversation_id, external_ticket_id, reason, priority, state, due_at | Case reference, SLA và reopen tracking |
| documents | owner_id, source_ref, source_hash, sensitivity, acl, active_version_id | Nguồn riêng tư không lộ qua URL công khai |
| document_versions | document_id, version, status, effective_from/to, reviewer, content_ref | Published immutable; active pointer đổi atomic |
| knowledge_chunks | document_version_id, content_ref/text, ordinal, source_locator, language, acl | Index tenant/version/status; invalidation kiểm ở query |
| embeddings | chunk_id, model_id, model_version, dimension, vector | Không trộn embedding dimension/model; migration dual index khi đổi |
| memory_facts | customer_id, key, encrypted_value, type, status, source_event_id, verification_level, valid_until, supersedes_id, purpose, generation | Type/key allowlist; fact private không vào KB global |
| episodic_memories | customer_id, case_id, summary_ref, source_refs, as_of, generation | Có provenance và delete propagation |
| conversation_summaries | conversation_id, source_watermark, source_refs, summary_ref, generation | Invalidated khi source bị xóa/sửa |
| memory_candidates | customer_id, proposal, source_ref, status, reviewed_by, reason | Không có quyền publish KB trực tiếp |
| knowledge_gaps, feedback | run_id, reason, corrected_source_ref, reviewer, triage_state | Không copy transcript sang tenant/global |
| audit_events | actor_ref, operation, resource_ref, before_after_hash, reason, timestamp | Append-only qua runtime permissions; tránh PII/raw secret |
| deletion_requests, tombstones | customer/resource, verified_by, generation, state, purged_at, suppression_ref | Chống tái sinh từ replay/backup |
| cost_ledger | run/intent_id, provider, category, market, quantity, rate_version, currency, estimated/actual | Unknown cost không ghi 0; đối soát hóa đơn |

## 3. NormalizedEvent v1

Schema: [`../contracts/normalized-event.v1.schema.json`](../contracts/normalized-event.v1.schema.json). Một callback có thể thành nhiều event. Envelope được tạo **sau** signature verification; external payload không gọi trực tiếp endpoint nội bộ để dựng trusted event.

Field bắt buộc: `schema_version`, `event_id`, `event_type`, `tenant_id`, `channel`, `channel_binding_id`, `external_user_id`, `provider_event_key`, `occurred_at`, `received_at`, `payload`. Các event v1: `inbound.message`, `delivery.status`, `outbound.echo`, `customer.opt_out`, `channel.interaction`. Payload inbound gồm message_id, message_kind và text khi kind=text; status gồm message_id và delivery status; interaction có kind và eligibility evidence do adapter map; opt-out có purpose. MVP schema không chứa raw media URL hoặc auth token.

Dedup message key dùng ID message của provider + binding; status key dùng message ID + status + event discriminator/timestamp theo provider. Không dedup chỉ bằng message ID cho tất cả event vì sẽ mất status update. Nếu provider không có event ID, derive stable hash từ semantic fields đã được chốt và fixture test; lưu collision handling và raw hash để điều tra.

Customer mapping thực hiện trong server workflow, không nhận `customer_id` tự khai từ kênh làm chủ thể được tin cậy. Unknown type lưu quarantine/metric, không tạo reply.

## 4. AgentDecision v1

Schema: [`../contracts/agent-decision.v1.schema.json`](../contracts/agent-decision.v1.schema.json). Model output gồm `kind`, `intent`, `answer_text`, `source_refs`, `proposed_tool_calls`, `memory_candidates`, `handoff_reason`, `risk`. Giá trị `kind`: `reply`, `clarify`, `handoff`, `request_tool`, `no_action`.

Schema validation chỉ kiểm hình dạng; runtime còn cưỡng chế semantic rules: reply không rỗng; factual claims cần source/tool proof; clarify chỉ hỏi thông tin tối thiểu; handoff có reason; request_tool chỉ thuộc registry đã allowlist; no_action không tạo tin nhắn. `memory_candidates` không bao gồm subject/tenant/role được model chọn, server gắn scope đúng. Nguồn và fact keys phải thực sự tồn tại/được cho phép. Model risk chỉ là tín hiệu, policy code quyết định quyền.

Không yêu cầu model xuất private chain-of-thought. Audit lưu reason code ngắn, nguồn, tool inputs đã redact và kết quả validation.

## 5. API nội bộ v1 cần tạo

Tất cả `/v1/*` trừ webhook/health có operator auth, tenant membership, RBAC, request ID và rate limit. Tenant scope được derive từ session + membership, không tin header trần. Paginate bằng cursor, sort ổn định, optimistic ETag/If-Match cho resource mutable. POST side-effect có Idempotency-Key; cùng key khác body hash → 409.

| Endpoint đề xuất | Actor / chức năng | Bất biến |
|---|---|---|
| GET/POST /webhooks/whatsapp/:bindingToken | Provider handshake/callback | Token định tuyến không phải authorization; POST cần signature |
| POST /webhooks/zalo/:bindingToken | Provider callback | Map binding + signature trước ingest |
| GET /health/live, /health/ready | Infra | Không lộ config/secret; ready phản ánh dependency thiết yếu |
| GET /v1/conversations, /:id/messages | Operator | Tenant + assignment/role scope; không quét mọi transcript |
| POST /v1/conversations/:id/takeover | Agent/admin | CAS ownership_version; cancel intents chưa dispatch |
| POST /v1/conversations/:id/resume | Agent/admin | Explicit reason, cập nhật ownership_version, không auto resume do timeout |
| POST /v1/conversations/:id/replies | Assigned operator | Cùng outbox và policy như bot; Idempotency-Key |
| GET /v1/customers/:id/memories | Operator được cấp scope | Che PII, source refs, status/expiry |
| POST /v1/customers/:id/memory-corrections | Authorized operator | Evidence/reason, không sửa audit gốc |
| POST /v1/customers/:id/deletion-requests | Authorized privacy role | Verification + asynchronous purge; trả request_id |
| POST /v1/identity-links/challenges, /verify, /revoke | Verified account/operator | Single-use TTL, anti-enumeration, rate limit |
| POST /v1/knowledge/uploads, /:id/versions | Knowledge editor | Quarantine, size/MIME, source metadata |
| POST /v1/knowledge/versions/:id/publish, /revoke | Reviewer/admin | Audit + active pointer + cache invalidation |
| POST /v1/knowledge/search-preview | Reviewer | Cùng retrieval ACL; không direct SQL/vector access |
| GET /v1/approvals; POST /:id/approve, /reject | Approver scope | Bound to argument hash; approver khác requester cho risky action |
| GET /v1/runs/:id, /v1/metrics | Operator/auditor theo scope | Redacted trace, không raw prompt/PII |
| PATCH /v1/settings/automation | Admin | ETag, audit; OFF ngay ở sender; không chờ deploy |

Errors chuẩn: `code`, safe `message`, `request_id`, `retryable`; 400 validation, 401 auth, 403 scope, 404 resource-not-visible, 409 version/idempotency conflict, 422 policy/unsupported, 429 limit, 503 dependency. Response không phân biệt tồn tại resource thuộc tenant khác. Webhook response tuân provider riêng, không máy móc trả internal errors.

## 6. Tool gateway

| Tool | Mức rủi ro | Input / quyền / điều kiện | Output |
|---|---|---|---|
| search_knowledge | Read | Query + server ACL; chỉ published | Chunks + source refs |
| get_order_status | Read private | Order ref + server customer authorization; không chỉ biết mã đơn | Minimal status, as_of, result_ref |
| get_product_availability | Read | Product ref, tenant catalog scope | Giá/tồn kho theo nguồn + as_of |
| create_support_ticket | Write thấp | Khách xác nhận nhu cầu + idempotency; tenant-scoped | Ticket ref, state, due_at |
| request_order_change | Write cao, V1 | Intent preview + khách xác nhận + approval nhân viên hợp lệ + freshness check | Request ref, không hứa đã đổi trước success |
| request_refund | Ngoài MVP | Chỉ mở quy trình phê duyệt; không gọi hoàn tiền tự động | Pending request, không monetary side effect |

`TrustedToolContext` do server gắn tenant/customer/actor/purpose/action_id. Model không truyền token/URL arbitrary/SQL. Tool schema `additionalProperties: false`, server kiểm object ownership; network allowlist, response size limit, timeout, sanitized error. Mỗi tool có argument schema, side-effect class, retry policy, required approval, result schema và fixture success/failure.

Write flow: persist proposal → validate → xác nhận khách khi cần → request approval gắn arg hash → reauthorize và reread nguồn → execute once theo idempotency → persist result → audit → trả trạng thái thật. Approval expired hoặc args đổi phải xin lại. Nếu provider timeout sau có thể đã ghi, giữ unknown/reconcile; không thử ghi lần nữa theo model yêu cầu.

## 7. State machines

Conversation: `bot_active → handoff_pending → human_active → resolved`; explicit resume mới trở lại `bot_active`. Inbound mới khi resolved tạo episode/reopen theo policy; không tự tắt suppression/opt-out. Claim human và resume đều tăng ownership_version. Handoff pending cũng dừng bot trả nghiệp vụ, chỉ cho thông báo chuyển người một lần khi kênh cho phép.

Document: `draft → processing → review_required → published → superseded/revoked`. Memory: `candidate → confirmed/rejected → superseded/expired/deleted`. Approval: `pending → approved/rejected/expired → executed/failed/unknown`. Outbox theo tài liệu 02. Database constraints và tests phải ngăn transition sai, không chỉ vẽ diagram.

## 8. Test contract tối thiểu

JSON Schema kiểm valid/invalid event cho từng event_type; text cần field text, status không giả thành inbound; reject extra secret field. Golden fixture của hai adapter normalize thành cùng shape. Backward compatibility: thêm optional field có version review, đổi meaning/bắt buộc → major event schema mới. Roundtrip encoding tiếng Việt/emoji, timestamp UTC, nullable fields và empty body. OpenAPI validation của console không được đi vòng server authorization.
