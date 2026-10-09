# 02 — Kiến trúc hợp nhất v3

Đặc tả kiến trúc hiện hành nằm tại [MASTER_PLAN §3](../MASTER_PLAN.md#architecture); tin nhắn/handoff/bảo mật tại [§8](../MASTER_PLAN.md#reliability); wiki pipeline tại [docs/11](11-wiki-contract.md).

Ba ranh giới: curation đề xuất tri thức; serving trả lời từ bản đã duyệt và tools; control plane quản quyền/review/handoff/privacy. Không dùng một agent có quyền sửa published wiki rồi đồng thời trả khách.

Raw/source registry và immutable wiki release là nguồn chuẩn nội dung; PostgreSQL giữ trạng thái/scope; lexical/vector/link indexes là dẫn xuất rebuildable. Obsidian là workspace tùy chọn, không database production và không sync hai chiều trực tiếp.

Stack và cây module đề xuất nằm trong master; SB-02 phải pin supported versions trước scaffold. Bridge Zalo chạy thường trực, một active fenced listener/account; không short-lived function. Chưa có code hoặc deployment chạy trong planning kit.

Quyết định ADR v3: source-first wiki; publication bằng manifest/CAS; customer memory riêng; một bounded workflow; transport-specific reliability; independent channel gates; optional features không chặn MVP. Thay đổi ADR cần evidence/owner review và cập nhật hợp đồng/backlog cùng PR.
