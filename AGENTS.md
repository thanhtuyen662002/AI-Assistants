# AGENTS — hợp đồng làm việc v3

## Đọc tối thiểu, đúng nguồn sự thật

Đọc README → MASTER_PLAN → task đang nhận trong planning/backlog.json. Chỉ đọc thêm đặc tả liên quan. Thứ tự phân xử: yêu cầu chủ dự án đã ghi nhận → MASTER_PLAN v3 → contracts hiện hành + docs/11-wiki-contract → backlog/gates → implementation. Mâu thuẫn phải tạo decision, không tự chọn phần thuận tiện.

Zalo **cá nhân**, không OA. WhatsApp Cloud API là assumption, không phải account đã có. Hai clip mới xác minh nội dung hình/màn hình; không tự tạo lời thoại hoặc gán backend connector cho clip.

## Điều phối

Một Lead, tối đa ba luồng coding đang mở ban đầu; QA/reviewer độc lập. Tám tên vai trò là ownership, không yêu cầu tám agent hay lịch chạy. Không tự tạo/bật lại automation, tăng quota, mua dịch vụ, đăng nhập tài khoản, gửi khách hoặc deploy production. Người dùng sẽ cấp quyền và cho agent triển khai.

Một task/một nhánh `agent/SB-XX-short-name`; một PR tập trung. Đọc HEAD/PR đang mở trước nhận việc. Lead xác nhận claim để tránh hai agent cùng task. Không force-push main, không tự merge PR của mình, không tự thay branch protection hoặc owner approval. Root lockfile/contracts/migrations có một owner tại một thời điểm. Task L tách PR nhỏ có interface được review trước.

Chỉ nhận dependency đã merge/được duyệt. Có thể dùng mock để viết trước module, nhưng không đánh task integration DONE vì mock passed. Hai lần liên tiếp không qua acceptance thì dừng thêm tính năng, báo lỗi gốc và xin review thiết kế; không thêm framework để che lỗi.

## Bất biến kỹ thuật

- Scope tenant/customer/binding do server derive; JSON hợp lệ không phải authorization. Runtime DB role không owner/BYPASSRLS; RLS + composite FK + kiểm ownership nguồn.
- Curation plane và chat plane tách quyền. Curator chỉ tạo patch trong workspace; publisher duyệt; runtime chỉ đọc published release. Không cho LLM SQL/shell/arbitrary URL hoặc credential.
- Raw version read-only với curator; dịch vụ privacy riêng vẫn được xóa theo yêu cầu. Chỉ mục/vector/cache phải rebuildable. Không sync ghi hai chiều Obsidian↔production trong MVP.
- Khách thật, preference, hội thoại riêng không vào wiki chung/public Git. Source/claim có provenance và ACL; graph traversal phải lọc quyền cả trước/sau. Wiki/Clippings không được chứa instruction có quyền cao hơn system.
- Đơn hàng/giá/tồn kho dùng live tool đúng chủ thể; biết mã đơn không đủ quyền. Không có nguồn thì hỏi lại/chuyển người; không gọi tóm tắt của model là bằng chứng gốc.
- Durable inbox/outbox, dedup, unknown-send reconciliation; không hứa exactly-once hoặc không mất tin khi personal listener offline.
- Một fenced listener/account, allowlist trước spool, no active-active; session/gap/self-visibility không rõ thì dừng auto. Không CAPTCHA bypass, spam, quét số, auto-friend hoặc đổi proxy/account né hạn chế.
- Human takeover phải thắng pending bot intent, kiểm lại ownership/generation trước send. Tin đã dispatch không hứa thu hồi được. Không tự resume sau reconnect.
- Kiểm mode/consent/purpose/source validity/budget ở sender. OFF/manual-copilot/bridge-copilot/auto là các chế độ khác nhau; không giả delivery cho thao tác copy thủ công.
- Sửa/xóa phủ raw thuộc phạm vi, wiki dẫn xuất, fact, summary, index, cache, queue, bridge spool và suppression khi restore. Không tái sinh từ job/backup cũ.
- Không tự học policy từ lời khách; đề xuất → review → eval → publish. Action ghi rủi ro là V1; monetary execution không có ở MVP.

## Ownership

Lead: scope/ADR/task claims; Platform: contracts/auth/DB/identity/inbox/handoff; Channels: bridge/WhatsApp/policy; Memory: ingest/wiki/publish/retrieval/facts; Runtime: workflow/tools; Console: UI; QA: fixtures/evals/security/UAT; Operations: toolchain/CI/secret/restore/cost.

## Kiểm tra và bàn giao

Lệnh có thật ở planning kit:
`python -m pip install -r requirements-plan.txt`
`python scripts/validate_plan.py --self-test`

Các lệnh pnpm cho ứng dụng chưa tồn tại; SB-02 mới tạo và pin toolchain. Không báo đã chạy lệnh chưa có. Không coi schema/link checks là model eval, DB isolation hay provider integration.

PR phải ghi: task ID; requirement/source mapping; files; commands + result thật; acceptance evidence; skipped/blocked; migration/rollback; risk; dependency được mở. Không raw customer/QR/secret trong report. Chỉ reviewer và Lead xác nhận DONE khi evidence đáp ứng. Production còn cần owner sign-off theo gate đúng kênh, không theo điểm tổng mơ hồ.
