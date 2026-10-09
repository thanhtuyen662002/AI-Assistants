# 03 — Tri thức và ký ức: đường dẫn hiện hành

[MASTER_PLAN §4](../MASTER_PLAN.md#wiki) và [hợp đồng wiki](11-wiki-contract.md) quy định tri thức doanh nghiệp; [§5](../MASTER_PLAN.md#memory) quy định customer memory; [§6](../MASTER_PLAN.md#runtime) quy định context budget.

Năm lớp: context phiên, wiki doanh nghiệp, facts riêng khách, lịch sử case, playbooks. Phải có scope/provenance/version/retention tương ứng; không một vector namespace chung cho tất cả khách.

Fact cần `tenant_id`, `customer_id`, `key`, `value_ciphertext`, `source_event_id`, `purpose`, `verification_level`, `status`, `valid_from/until`, `supersedes_id`, `deletion_generation`. Summary cần source_refs/watermark/as_of và generation; khi nguồn xóa/sửa phải invalidate/rebuild. Candidate extraction không tự tạo verified identity hoặc quyền admin.

Knowledge link không là customer identity link. Giá/tồn kho/order status dùng live tools, không từ ký ức cũ. Preference có thể auto-confirm theo policy đã duyệt khi khách nói rõ; dữ kiện nhạy cảm hoặc policy doanh nghiệp không đi đường này.

Raw read-only đối với curator không cấm privacy service xóa. Tombstone và generation phải chặn replay/job/spool/restore làm dữ liệu xuất hiện lại. Phương pháp publish/revoke/rollback nguồn dẫn xuất theo docs/11, không rollback mù về phiên bản chứa nguồn đã xóa.
