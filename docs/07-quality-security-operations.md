# 07 — Đo lường và nghiệm thu v3

Quyết định hiện hành: [MASTER_PLAN §11](../MASTER_PLAN.md#acceptance), [vận hành](../MASTER_PLAN.md#operations), [gate profiles](../planning/release-gates.json). Không dùng số đo trong video hoặc số test của planning kit làm kết quả chất lượng ứng dụng.

## 1. Phân biệt cấp bằng chứng

Planning lint/schema/DAG; unit deterministic; integration DB/queue/storage; E2E mock; model evaluation; controlled-account/provider evidence; human UAT; production observation là các cấp khác nhau. Chạy JSON parser không chứng minh test scenario đã chạy. `not_run`, `unknown`, `skipped` không passed. Gate phải được reviewer kiểm trên commit/config đang release, không dùng báo cáo cũ sau thay model/prompt/KB/connector.

SB-21 dựng harness và tối thiểu 20 smoke cases để unblock mock slice. Trước pilot theo gate profile cần ≥200 labeled cases và ≥50 câu review độc lập. Chia corpus: FAQ/policy 60; tools/order 30; memory/identity 25; handoff 25; channels 20; injection/privacy 20; retry/failure 20. Thêm WK scenarios vào các nhóm phù hợp; không đếm cùng test hai lần. Tách held-out và development, không đưa expected answer vào KB để gian điểm.

## 2. Định nghĩa metric

| Metric | Định nghĩa và điều không được làm |
|---|---|
| Grounded correctness | Số câu in-scope trả đúng nghiệp vụ và claim quan trọng có nguồn hợp lệ / tổng câu in-scope cần trả lời. Abstain sai không được tính đúng. |
| Unsupported claim rate | Số factual claim không được nguồn cho phép hỗ trợ / tổng factual claims. Báo counts và review method; zero denominator là N/A, không 0% thành công. |
| Recall@5 | Số câu có nguồn đích trong top5 / tổng câu retrieval có nguồn đích được gán nhãn. Không tính câu out-of-scope vào denominator để làm đẹp. |
| Required handoff recall | Case bắt buộc chuyển người đã chuyển đúng / tất cả case bắt buộc; trực tiếp yêu cầu người và race suite báo riêng. |
| False abstention | Câu có thể trả từ nguồn hợp lệ nhưng bot từ chối/handoff không cần thiết / tổng câu answerable. Theo dõi để không tăng correctness bằng né trả lời. |
| Containment | Case giải quyết không cần người và không reopen sau cửa sổ quan sát 24h / các case đủ thời gian quan sát. Khách im lặng không mặc định resolved. |
| Latency | ACK/durable write, queue wait, retrieval, LLM, tools, outbox, provider delivery báo riêng; p95 chỉ có ý nghĩa với số mẫu và tải được ghi. |
| Cost/case | Usage/model/embedding/channel + hạ tầng/storage/egress phân bổ / resolved cases đủ điều kiện. Unknown rates/outcomes tách estimate/actual, không số 0. |

Mục tiêu số lấy từ release-gates.json. Không model confidence tự khai thay semantic correctness. LLM judge chỉ hỗ trợ; ownership/scope/state kiểm bằng code, policy meaning/negation/numbers phải có labeled evidence và người review.

## 3. Checklist bằng chứng cho gate

| Check | Evidence tối thiểu |
|---|---|
| plan_assets_valid | Command validator + result, hashes của files được kiểm |
| synthetic_only | Fixtures không dữ liệu khách/secret; secret scan và review nguồn |
| golden_thread_pass | E2E executable source→publish→reply→takeover→update→delete/replay; không chỉ UI video |
| common_security | DB RLS/IDOR/tenant/customer/tool authorization/injection tests; zero unresolved P0 |
| source_grounding | Labeled eval theo corpus, source/ACL/release validity, WK semantic/lineage tests |
| privacy_purge_restore | Correction/TTL/deletion/spool/jobs/index/objects/backup suppression drill |
| human_review | ≥50 samples independent + support UAT; review owner/criteria/errors recorded |
| owner_data_processing_approval | Scope/purpose/retention/model-provider handling/support staffing approved, private evidence reference |
| manual_send_not_delivery | Copy/operator-marked-sent không provider accepted/delivered; không covert session connector |
| zalo_risk_terms_review | Current upstream/version/terms review, owner aware unofficial/account risk; not platform approval |
| zalo_controlled_account_evidence | Owner-authorized recipient tests, IDs/receive/send/revoke/status/unknown, thực tế đúng account/config |
| session_allowlist_fencing | Một active listener, stale epoch rejects, group/non-enrolled filtered trước persist |
| no_unresolved_gap | Coverage record reconciled có evidence, restart không tự xóa gap |
| manual_takeover_test | Two claims/late LLM/pending send/ambiguous echo; recorded in-flight limitations |
| cross_device_self_visibility | Mobile/PC/Web matrix theo cách owner dùng thực tế; missing visibility blocks auto coexistence |
| whatsapp_account_type_confirmed | Owner xác nhận account path/scopes/business permissions phù hợp; không giả assumption đã được duyệt |
| whatsapp_signature_sandbox | GET/POST khác nhau, raw signature, batch/forgery/IDs/status tests trên sandbox được phép |
| whatsapp_policy_terms_rates | Current API/terms/use case/rate card/account market/version, verified by owner/channel reviewer |
| consent_template_status | Purpose/opt-out/suppression/window/template approval checked lại khi queued→send |
| auto_allowlist_quality | Chất lượng đạt ngưỡng theo từng enabled intent/kênh, không gộp nhóm yếu; staged cohort configured |
| cost_cap | Atomic reservations, finite model/tool loops, cap/circuit breaker, actual/unknown reconciliation |
| kill_switch_rollback | Dừng pending send theo scope và restore/rollback được drill, không giả hủy in-flight |
| owner_auto_approval | Owner sign-off gắn release/channel/cohort/config, khác approval rollout preparation SB-25 |

Các check là yêu cầu cần thực hiện, **chưa có check nào được tự đánh pass cho runtime trong repo này**. Code task DONE không tự thay evidence gate. Gate resolver phải mở rộng transitive dependencies và xem đủ check, không chỉ đọc required_tasks cuối danh sách.

## 4. Tests và PR/CI

Unit: policy clocks/CAS/state/conflict/TTL. Contract: strict schema/batches/tool shapes. Integration: DB role/constraints/queue/crash/spool/publication. E2E: golden thread và controlled providers riêng. Security: tenant/customer/graph/SSRF/forged callback/secret leaks. Model: Vietnamese/no dấu/SKU/negation/multi-intent/unknown source. UAT: support operator thật với dữ liệu đã đồng ý dùng.

Không chạy load stress lên tài khoản Zalo cá nhân. Mục tiêu tải mock và cách báo p95 nằm trong master. Test optional SB-19 khi bật write action, không bỏ approval tests nhưng cũng không bắt feature-disabled MVP xây full write workflow.

CI ứng dụng do SB-02/23 tạo sau; planning kit có script local, không lịch CI hoặc automation nền được kích hoạt bởi lần bàn giao này. PR review phải đọc diff, báo command thật, failed/skipped và rollback. Một P0 leak/sai identity/unauthorized write chặn release dù average quality rất cao.
