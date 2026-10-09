# 08 — Giao việc và bằng chứng

Đọc [AGENTS](../AGENTS.md) và [MASTER_PLAN](../MASTER_PLAN.md#first-run). Không dùng prompt phiên bản OA/personal-baseline cũ để thay v3.

## Lệnh có thật cho planning kit

```bash
python -m pip install -r requirements-plan.txt
python scripts/validate_plan.py --self-test
```

Python packages được pin theo môi trường chạy kiểm tra kế hoạch (jsonschema 4.26.0, PyYAML 6.0.3); không phải lựa chọn dependency ứng dụng. Agent SB-02 tạo scripts pnpm thực, supported Node/toolchain/lockfile và CI ứng dụng sau. Chưa có lệnh build/runtime/E2E/model eval được báo đã chạy ở kit này.

## Prompt Lead

```text
Bạn phụ trách repo thanhtuyen662002/AI-Assistants, kế hoạch hợp nhất v3.
Đọc README, AGENTS, MASTER_PLAN, planning/backlog.json và release-gates.json.
Kiểm HEAD/PR hiện có trước sửa. Chạy plan validator. Không tự bật lịch,
đăng nhập tài khoản, gửi khách, tăng quota, mua dịch vụ hoặc deploy.

Zalo cá nhân, không OA. WhatsApp Cloud API còn là assumption.
Wiki-curation và runtime-CSKH tách quyền; customer memory không vào wiki chung.
Hai video có visual evidence, chưa fully transcribed; không bịa backend từ demo.

Bắt đầu SB-01/SB-02, sau SB-03 mở spike SB-27 sớm.
Tối đa ba luồng coder, QA/reviewer độc lập, một task/một PR.
Mục tiêu tích hợp đầu tiên là SB-33 golden thread bằng mock.
Không buộc SB-15 chờ cả hai tài khoản; policy mock có contract và gates thật tách kênh.
Không kéo SB-19/26/32 vào dependency MVP khi feature chưa bật.

Mỗi task có acceptance trước code. Chỉ báo DONE với evidence có command,
commit/config version và review. Unknown/skipped không passed.
Báo theo ba mục: đã chứng minh; chưa chứng minh; owner decision cần thiết.
```

## Prompt nhận một task

```text
Task: SB-XX (đọc toàn bộ record trong planning/backlog.json).
Branch: agent/SB-XX-short-name.
Đọc AGENTS và phần MASTER_PLAN/task-specific docs; không nạp cả repo mọi lượt.
Kiểm dependencies, owner claim và module ownership. Dùng fixtures/contract mock
khi upstream chưa sẵn nhưng ghi rõ phần implementation không thay live evidence.
Implement nhỏ nhất đủ acceptance. Test happy path + failure + authorization.
Không tự đổi schema/expected behavior để vượt test; đưa thay đổi hợp đồng ra review.
Bàn giao PR có command/result thật, evidence, rollback, blocked inputs.
Không tự merge hoặc force-push main.
```

## Phần đọc theo vai trò

Platform: MASTER_PLAN 3/8/9, schema manifests; kiểm tenant/customer/cas/ownership/lease. Memory: docs/11-wiki-contract, vault mẫu và cases WK; raw read-only, proposal/review/publish, ACL/lineage/deletion. Channels: MASTER_PLAN 7/8, docs/10; account risk, no-loss limits, signatures/session/fencing, self events, capability records. Runtime: MASTER_PLAN 5/6/9; bounded context, source support, live tool authorization. Console: MASTER_PLAN 4/8/12; drafts/sources/takeover/review/status thật. QA: MASTER_PLAN 11 + gates + cả bộ GC/WK; independent semantic review và negative tests. Operations: MASTER_PLAN 3/12; portable runtime/bridge, secrets, cost caps, restore senders OFF.

## Review PR

Reviewer đọc diff thật, không chỉ báo cáo agent. Kiểm acceptance và bypass paths: scope/ACL, stale source/patch, instruction injection, human takeover, session fencing, unknown send, tombstone, costs. Phân biệt structural tests với semantic/model/provider evidence. P0 chưa sửa chặn merge; skipped mandatory test không được coi pass. Root contract/lockfile/migrations cần owner review; một agent không vừa viết vừa tự duyệt.

## Mẫu report

```text
Task / branch / commit:
Status: ready_for_review | blocked | partial (không tự production-ready)
Implemented / files / contract versions:
Requirement & source refs:
Commands actually run + results:
Acceptance evidence + environment:
Skipped / unknown / external blockers:
Security / privacy impact:
Migration / rollback:
Next dependency unblocked:
```
