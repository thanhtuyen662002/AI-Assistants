# Validation assets — Zalo personal revision — 2026-10-09

Đây là kiểm tra **đặc tả và dữ liệu kế hoạch**, không ứng dụng/connector đang chạy. `planning/validation-report.md` giữ báo cáo lịch sử của baseline OA trước đó; nó không chứng nhận personal revision.

## Kiểm tra thực sự đã chạy local

Python với jsonschema.Draft202012Validator và FormatChecker:

- Event v2 qua meta-schema check.
- 25 shape assertions PASS: 15 valid (5 event types × 3 channel/transport combinations) và 10 invalid (legacy zalo/v1, transport mismatch/missing, extra cookie/token, thiếu text, invalid UUID/time).
- 28 task ID duy nhất, dependencies tồn tại, DFS xác nhận không chu trình; SB-07 và SB-25 phụ thuộc SB-27.
- 38 scenario seed JSONL parse được, IDs duy nhất, must/must_not, channel hợp lệ và tất cả `fixture_status=to_implement`.

Git blob SHA của assets đã kiểm tra:

```text
257b66023a89e763ab81373896ad0d6d2eae651c  contracts/normalized-event.v2.schema.json
cc6dedaf68d0211b9d120a83d161ef65f2af8010  planning/backlog.json
ba42b15eb8b7369a163f086cfbc18af882978dde  evals/golden-cases.jsonl
```

Không có app build/test, LLM evaluation, bridge executable, QR login, real account send, delivery verification, one-listener/gap/handoff integration test hoặc deployment đã chạy trong revision. Scenario seed là yêu cầu kiểm thử, không kết quả vượt kiểm thử. JSON Schema không kiểm chữ ký/quyền/nguồn/thực tế receipt; các kiểm tra đó vẫn cần code/test runtime.

SB-03/SB-21 đưa checks vào CI repo và mở rộng fixtures thực; SB-27 làm compatibility/account capability sau owner authorization/risk review. Không coi passing shape assertions là bảo đảm không khóa tài khoản hoặc đã tích hợp Zalo.
