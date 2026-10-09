# 06 — Backlog v3 và điều phối

Nguồn task duy nhất: [planning/backlog.json](../planning/backlog.json). Có 34 task SB-00…SB-33; IDs cũ giữ nguyên nhưng dependency/scope đã hiệu chỉnh. [MASTER_PLAN §10](../MASTER_PLAN.md#delivery) giải thích lộ trình; [release gates](../planning/release-gates.json) quyết định readiness theo mode/channel, không một checkbox chung.

## Những sửa đổi quan trọng so với bản trước

SB-00 không còn mô tả chưa có video: `partial` vì visual evidence đã kiểm, full audio chưa đối chiếu. Đây không phải dependency runtime. SB-09 là pure policy engine kiểm được bằng mock từ contracts, không chờ SB-07/08. SB-15 và SB-33 vì vậy chạy end-to-end sớm khi chưa có tài khoản thật.

SB-07 vẫn bắt buộc qua SB-27 trước personal integration. SB-24 nghiệm thu phần chung/manual-copilot; production Zalo/WhatsApp có gate riêng. Không cần credential cả hai mới xây được core, nhưng không báo hoàn tất cả hai khi chỉ một kênh đạt. SB-19/26/32 là optional V1, không chặn MVP khi feature tắt.

## Workstreams và đầu ra

| Cụm | Task | Kết quả |
|---|---|---|
| Nền móng | 01–05, 21, 27 | Scope, chạy local, hợp đồng, auth/DB, dataset và personal capability decision |
| Tin nhắn/nhân viên | 06, 09, 16, 17 | Inbox/outbox mock, policy evaluator, UI tối thiểu, takeover |
| Wiki | 10, 28, 29, 30, 11, 31 | Source registry → workspace → patch → lint/review/release → retrieval → semantic/lineage tests |
| Ký ức/công cụ/runtime | 12, 13, 14, 15 | Customer scope, memory lifecycle, live-tool contract, bounded workflow |
| Luồng đầu tiên | 33 | Golden thread từ nguồn đến reply/handoff/update/delete với assertions |
| Tích hợp kênh | 07, 08 | Personal controlled test và WhatsApp sandbox/live-test evidence riêng |
| Pilot/operations | 18, 20, 22, 23, 24, 25 | Review UI, metrics/cost, security/restore/UAT, staged go-live theo gate |
| V1 tùy chọn | 19, 26, 32 | Risky-write approvals, feedback có review, owner brief; không tự bật lịch |

Task records có vai trò, phase, depends_on, status, deliverable và acceptance. Đây là owner-role logic, không GitHub accounts đã assign. Implementation mặc định TODO; SB-00 partial visual-review. Không tự tạo issues/lịch mới hoặc start agent từ file JSON.

## Phiên đầu tiên

Lead chốt SB-01 và owner inputs; Operations SB-02; QA chuẩn bị scenarios. Khi SB-03 có contract, Channels làm SB-27, Platform auth/DB, Console theo mock. Sau DB, Memory source/wiki, Platform inbox/identity, Runtime tools theo availability. Giữ tối đa ba luồng coding cùng lúc; không để mọi người sửa root lockfile/schema.

Mục tiêu kiểm chứng đầu tiên không phải giao diện đẹp hay login Zalo, mà là SB-33. Owner có thể xem nguồn, sửa policy, thấy bản chưa duyệt không ảnh hưởng bot, thấy takeover dừng bot và delete chặn replay.

## Task ready và DONE

Ready khi dependencies có evidence đã merge/review; có scope/fixtures/acceptance và không tranh ownership. Một task L tách nhiều PR nhỏ, không kéo nửa code production vào main chưa có guards. DONE cần reviewer+Lead nhận bằng chứng theo AGENTS. Các kiểm thử tài khoản thiếu credentials là blocked, không mock-pass.

Code readiness khác mock readiness khác actual-channel readiness. Gate resolver lấy transitive dependencies và toàn bộ check status=pass của đúng cấu hình/commit. Optional capability khi được bật phải có task/test mới tương ứng; không bỏ approval vì đang gọi nó tùy chọn.
