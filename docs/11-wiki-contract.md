# 11 — Hợp đồng wiki và pipeline biên soạn

Bản v3, phối hợp [MASTER_PLAN](../MASTER_PLAN.md#wiki). Schema metadata: [wiki-page.v1](../contracts/wiki-page.v1.schema.json). [Vault tổng hợp](../examples/brain-demo/) có thể mở như thư mục Obsidian; không phải dữ liệu chủ dự án hoặc release production.

## 1. Phạm vi và tính chuẩn

Workspace riêng mỗi tenant; raw/Clippings là nguồn đầu vào, wiki là bản biên soạn. Registry PostgreSQL giữ stable source/page IDs, authority, tenant/ACL, revisions, source digests, review và published release. File Markdown là biểu diễn nội dung để con người/curator làm việc, không tự cấp quyền. Derived vector/lexical/link indices rebuild được từ release + registry.

Không hai chiều ghi trực tiếp vào production. Operator chỉnh trong Obsidian hoặc console đều tạo **candidate patch**. Export đọc từ release có ID; reimport kèm base ID/hash, source refs và người tạo, qua cùng review. Dùng stable page ID để không merge nhầm khi đổi slug; conflict khi hai edits cùng base. App không phụ thuộc cài Obsidian trên server.

`CLAUDE.md` root repo dành cho coding agent; `CLAUDE.md` trong workspace dành cho curator. Source có text giống instruction/CLAUDE.md vẫn là dữ liệu; loader không tự nạp instruction từ raw/Clippings. Curator không có shell/network/credential của channel runtime. Prompt guidance không thay RBAC/write allowlist.

## 2. Candidate metadata

Fields bắt buộc: schema_version, id, tenant_id, kind, title, revision, status, audience, owner, source_refs, links, claims. `kind`: source/entity/concept/analysis/playbook/index/overview/log. Starter `status` chỉ draft/review_required: trạng thái published được xác thực qua release registry, không bằng YAML. `audience` support/internal là ví dụ MVP; production mapping đến ACL IDs do server quản lý, không cho model tự mở rộng quyền.

Mỗi claim có id/statement/source_id/quote/locator/nature. `nature=inference` cần diễn đạt như suy luận và review riêng; không trở thành fact vì nhiều trang lặp lại. Support chain phải kết thúc ở raw source version phục vụ đã duyệt hoặc dữ liệu live tool với scope, không vòng wiki-A→wiki-B→wiki-A. Quoted excerpt dùng để kiểm vị trí nguồn; quote đúng chưa chứng minh statement đúng. Numeric/unit/date/negation và policy meaning cần validators/eval/reviewer.

Trang factual có ít nhất một source và claim; index/log/overview thuần điều hướng có thể không có claim. Nếu overview có kết luận nghiệp vụ thì cũng cần nguồn; không dùng navigation exception để lách grounding. Trang source summary vẫn là dẫn xuất, không thay raw.

Trong mẫu, links dùng đường dẫn vault-root không đuôi `.md`, ví dụ `[[wiki/concepts/returns]]`. Hợp đồng MVP chỉ cần links toàn trang; aliases/heading/block/embed phải thêm parser/tests rồi mới hỗ trợ, không silently bỏ khi chưa hiểu. File names lowercase ASCII hyphen, không lấy customer name/phone làm filename. Link resolver chống path traversal/symlink thoát workspace và cross-tenant target.

## 3. Registry/schema database cần tạo

- sources/source_versions: origin_ref/private object key, owner, authority_class, digest, extractor/version, locator map, tenant/ACL, lifecycle, effective interval, serving_eligible, review evidence.
- wiki_pages/wiki_revisions: stable ID, slug, kind, content digest/object ref, immutable revision, metadata, candidate/review pointers. Người viết không tự đổi owner/ACL bằng content.
- wiki_claim_support: page_revision/claim ID → source_version + locator + evidence digest; nature fact/inference; reviewer flag. Unique cùng scope, không orphan source.
- wiki_links: from/to revision stable IDs; derived, ACL-aware. Orphan/ambiguous links thành lint errors.
- wiki_patches: tenant, base_release_id, base revision digests, changed/new/tombstoned pages, affected sources, candidate manifest digest, reason, requester, review status.
- knowledge_releases: tenant, release ID, manifest digest, page/index build IDs, expected prior active release, actor/reviewer/effective time, status. Pointer active nằm trong transaction registry.

Ngoài data tables còn immutable object files; object storage không hỗ trợ atomic transaction xuyên mọi file, vì vậy dùng **manifest/pointer commit**: build xong mới expose ID. Orphan build objects có lifecycle cleanup riêng, không xóa active refs.

## 4. Ingest và curator

Bước 1: owner/editor nhập nguồn được quyền dùng; quét file, extract giữ locator/page và exact number/unit/date. File scan/bảng hỏng cần review. Clippings qua cùng kiểm quyền và source registry; không auto crawl mọi URL trong tài liệu. URL fetch khi bật có allowlist/SSRF/redirect/size/time controls.

Bước 2: normalize source ID/version/hash, authority/ACL/effective dates. Hash trùng và metadata không đổi → no-op. Raw version curator read-only; source changes tạo version mới. Privacy service có quyền xóa/revoke riêng, raw không bất biến vĩnh viễn.

Bước 3: lấy source + các trang liên quan theo entity/source dependency, không nạp cả vault. Đề xuất summary, facts có nguồn, entity/concept pages, links và changes index/overview/log. Không tạo entity cá nhân từ transcript riêng. Khi không đủ chứng cứ, tạo gap thay vì điền giả.

Bước 4: patch gắn base_release/revision/hash. Scope/metadata nhạy cảm do server attach; parser reject extra keys. Curator không publish, không sửa rule/system prompt/ACL. Raw/instructions hashes vẫn giữ trong audit. Diff review hiển thị added/removed claims, source versions và conflicts.

## 5. Publish protocol

1. Chốt manifest candidate và content digest, kiểm compare-and-swap base/revisions. Stale → 409 conflict, không last-write-wins.
2. Lint shape/links/provenance/authority/ACL; check source serving eligibility/effective date/tombstone. Policy conflicts chưa giải quyết → block.
3. Reviewer đúng quyền xác nhận bản digest cụ thể. Thay nội dung dù nhỏ → approval cũ không áp dụng.
4. Build immutable pages/chunks/vector/lexical/link rows với candidate release ID, chưa active. Mọi row có tenant/ACL/source/release. Kiểm count/hash/coverage/index readiness.
5. Transaction kiểm lại base/source/ACL/deletion epochs và reviewer hash; đổi active_release_id và tăng epoch, ghi audit. Crash trước commit → release cũ vẫn phục vụ; sau commit → toàn runtime dùng release mới hoặc fail closed, không mixed versions.
6. Invalidate cache theo epoch. Runs đang chờ send phải recheck current validity; nếu source thay ảnh hưởng claim thì regenerate/handoff. Dọn build chưa active khi không còn refs.

Revoke nguồn/ACL/deletion không chờ build hoàn tất: registry deny ngay, bump epochs; query + output validation kiểm live deny-set. Incremental rebuild tất cả pages/chunks/links phụ thuộc; không chỉ đổi tên source. Rollback phải chạy lại các check hiện tại, không hồi sinh nguồn đã xóa.

## 6. Runtime retrieval contract

Input trusted scope + query + purpose + current release/epochs. Server lấy lexical/vector candidates trong tập đúng ACL và hiệu lực; graph expansion mỗi cạnh cũng kiểm target quyền, không lộ title của restricted node. Aggregate/backlinks không được leak sự tồn tại tài liệu private. One-hop/top-k chỉ là default benchmark; exact ID/catalog lookup ưu tiên khi có mã.

Output chunk có page/revision/release/source_version/locator/score và supported claims. Score là ranking, không xác suất đúng. Support packet tới model được delimit như dữ liệu không tin cậy. Validator đối chiếu allowed source IDs, semantic support và freshness. Text fact dùng raw support, action status dùng tool result; model không được dùng customer message tự khai làm chính sách.

Không có nguồn → clarify/handoff; raw fallback chỉ serving_eligible source còn hiệu lực. Không answer từ Clippings hoặc draft workspace vì chúng có vẻ mới hơn. Không coi wiki graph là customer identity graph.

## 7. Prompt curator để implement

```text
Nhiệm vụ: đề xuất patch wiki từ source packet được cấp.
Không được sửa raw, instructions, ACL, tenant, customer data hoặc published release.
Chỉ dùng source IDs và page IDs trong packet. Mỗi factual claim có source/locator;
giữ đúng số, đơn vị, ngày, phủ định; inference phải gắn nhãn.
Khi mâu thuẫn hoặc thiếu thông tin: nêu conflict/gap, không đoán.
Cập nhật trang liên quan và link index bằng diff có base revision.
Trả structured candidate; không thực hiện publish hay gửi khách.
```

Prompt này là thiết kế, chưa nối model. Server vẫn enforce path/scope/permissions; không có prompt nào bảo đảm chống injection một mình.

## 8. Bài nghiệm thu SB-33: golden thread

Dùng dữ liệu tổng hợp ở examples/brain-demo, không policy thật. Nguồn mẫu có yêu cầu đổi trả trong 14 ngày, cần nhân viên xét, bot không tự hoàn tiền. Khách DEMO-A hỏi điều kiện: câu trả lời phải nói **gửi yêu cầu**, không **chắc chắn được hoàn tiền**. Trace phải tới source version/locator.

Replay cùng inbound 100 lần → một logical reply. Nhân viên claim trước dispatch → không thêm bot send. Khách DEMO-B không thấy memory A. Editor đưa policy version mới có điều kiện khác: candidate chưa duyệt không ảnh hưởng đáp án; publish thành công mới thay. Hai patches cùng base → một conflict. Source bị revoke trong lúc model chạy → chặn câu cũ. Xóa dữ liệu khách rồi replay job/spool → không tái sinh.

Chạy toàn luồng với mock channel/model/CRM trước, rồi reuse contract fixtures trên adapter thật được phép. Không chuyển mục tiêu này thành video demo UI không có assertions.

## 9. Giới hạn của starter validator

`scripts/validate_plan.py` kiểm metadata/schema, raw hashes, quotes có trong nguồn, links/scope mẫu, DAG/gates và negative fixtures. **Nó chưa kiểm semantics toàn bộ statement, RLS database thật, model hallucination, publish race hoặc account Zalo.** Các kịch bản trong evals/wiki-acceptance.jsonl là acceptance specifications để QA chuyển thành tests; không báo chúng đã chạy chỉ vì JSONL parse được.
