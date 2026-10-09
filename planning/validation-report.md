# Planning baseline validation — 2026-10-09

Đã kiểm tra các **tài sản đặc tả**, không phải ứng dụng hoặc tích hợp thật.

## Kết quả thực thi local

Dùng Python, `jsonschema.Draft202012Validator` và `FormatChecker` trong môi trường làm việc.

- 2 JSON Schema qua `check_schema` (Draft 2020-12).
- 14 smoke assertions qua: 5 event variants hợp lệ; từ chối inbound text thiếu text; từ chối top-level token field; 5 decision kinds hợp lệ; từ chối tool args chèn tenant_id; từ chối no_action có answer_text.
- 27 task ID duy nhất; mọi dependency tồn tại; DFS xác nhận DAG không có chu trình.
- 30 dòng JSONL parse được, ID duy nhất, có must/must_not; tất cả còn `fixture_status=to_implement`.

## Git blob SHA của file đã kiểm tra

```text
35ca1977ccedfbadaa028cbbe9f7d7dc55f18246  contracts/normalized-event.v1.schema.json
adc08200728d61ab617493642c763eab1d172fbd  contracts/agent-decision.v1.schema.json
ee933cf89c7b6d04f78c5dfd88ea3f5fb3cbe31d  planning/backlog.json
f3b46666ebe42ca37417bb551706549b03b791cd  evals/golden-cases.jsonl
```

## Chưa chạy / chưa hoàn thành

Không có application build/unit/integration/E2E/model evaluation, RLS trên DB thật, channel sandbox test, live message send hoặc deployment trong planning baseline. Không có nguồn video/transcript để hoàn thành SB-00. Smoke assertions không chứng minh toàn bộ schema semantic safety; server authorization/policy/retrieval validation vẫn bắt buộc.

SB-03/SB-21 phải đưa validation thành test runner/CI có fixtures đầy đủ trong repo. Các chỉ số chất lượng và vận hành trong tài liệu 07 là mục tiêu chưa đo, không phải kết quả đạt được.
