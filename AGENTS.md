# Hướng dẫn cho coding agents — Zalo cá nhân

## Yêu cầu có hiệu lực

Chủ dự án xác nhận dùng **Zalo cá nhân**, không phải OA. Đọc README → docs/10-zalo-personal-decision.md → docs/01..09 → planning/backlog.json. Không hỏi lại có phải OA không; không yêu cầu OA ID/App/OA token hoặc xây OA adapter làm MVP. WhatsApp giữ Cloud API như giả định thiết kế, không suy từ câu đính chính Zalo rằng WhatsApp cũng phải dùng cá nhân.

Bản sửa này thay giả định OA của commit baseline. Các hard gates dùng chung về tenant/customer, memory, tools, consent, chất lượng vẫn giữ. Hai clip chưa đọc được; SB-00 blocked, không tự tạo transcript. Có mâu thuẫn: yêu cầu chủ dự án đã ghi nhận → safety/platform constraints được kiểm chứng → docs/10 → contracts hiện hành → các module. Ghi ADR, không lặng lẽ đoán.

## Cách làm

Một task/một nhánh `agent/SB-XX-short-name`, một PR có dependency, scope, bằng chứng và rollback. Không force-push main hoặc tự merge PR mình. Claim task qua issue/PR; owner_role trong backlog không phải tài khoản đã assign. Kiểm tra PR/head mới trước sửa. Một agent quản lý root manifest/lockfile tại một thời điểm; pin supported versions sau compatibility check. Thiếu account không chặn mocks nhưng không được gọi mock là integration passed.

Vai trò: Lead quản lý scope/ADR; Platform contracts/auth/DB/identity/inbox/outbox/handoff; Channels bridge Zalo/WhatsApp/policy; Memory ingest/RAG/facts; Runtime workflow/tools/approval; Console inbox/settings/review; QA eval/security/E2E; Operations toolchain/deploy/secrets/observability/restore. Thay đổi chéo vùng cần review chủ module.

## Bất biến bắt buộc

1. Server derive tenant/customer scope từ auth và binding đã đăng ký; không tin field do client, bridge payload hoặc model tự chọn. Runtime DB không owner/superuser/BYPASSRLS. Filter tenant là chưa đủ với memory riêng từng khách.
2. Zalo Personal Bridge là **unofficial**, ứng viên `zca-js` sau SB-27. Review điều khoản/account risk và dependency trước live login. Không dùng tài khoản thật/scan QR khi chủ sở hữu chưa chủ động cho phép. Chấp nhận rủi ro không tạo quyền vượt giới hạn nền tảng.
3. Bridge riêng lâu dài, session mã hóa, một active listener/account bằng fencing lease. QR owner-only, TTL ngắn, không log/cache/public screenshot; cookie/session/IMEI/device context không vào LLM/Git. Không lấy credential từ người khác hoặc cài extension trích cookie làm yêu cầu mặc định.
4. Nhận Zalo từ listener qua authenticated internal ingest, không OA webhook hoặc giả chữ ký Zalo. Chữ ký bridge chứng minh bridge gửi, không chứng minh Zalo ký event. WhatsApp vẫn raw webhook signature và official Cloud API; không WhatsApp Web automation.
5. Lọc cuộc trò chuyện CSKH 1:1 được cho phép **tại bridge trước persist/LLM**. Không dump danh bạ, nhóm, lịch sử, tin riêng. Thread/user ID được bind tenant+account; không tự merge theo tên/số tự khai.
6. Durable inbox trước internal ACK; local encrypted bounded spool khi API lỗi; dedup và outbox. Không hứa replay đầy đủ từ Zalo hoặc exactly-once provider. Gap phải được báo; ambiguous send → unknown/reconcile, không retry mù.
7. Runtime và sender kiểm handoff/ownership version. `isSelf` không tự phân biệt người/bot: đối chiếu outbox/provider IDs; self event không khớp → human takeover bảo thủ. Chưa chứng minh quan sát được mobile/PC self messages thì AUTO bị chặn khi dùng song song ngoài console.
8. OA 48h/7d, OAuth refresh, OA quota/template không áp cho personal. Không suy ra personal không giới hạn hoặc hoàn toàn miễn phí. Unknown rate/capability không đổi thành 0/allowed. Không né CAPTCHA, challenge, block, giới hạn hoặc anti-bot; không tạo vòng login hay chuyển proxy/tài khoản để né chặn.
9. Chỉ published KB còn hiệu lực, ACL đúng. Memory candidate có nguồn và lifecycle; KB publish có duyệt. Giá/đơn hàng qua authorized live tool. Tool allowlist, approval gắn args hash, idempotency; không SQL/shell/arbitrary HTTP trong runtime CSKH.
10. Prompt injection không đổi quyền; thiếu nguồn → clarify/handoff. Xóa/sửa/TTL phủ summary/vector/cache/spool/jobs/restore suppression; session purge khi disconnect. Không auto resume bot chỉ vì listener reconnect.

## Definition of Done

Code + contract + tests + quan sát lỗi + docs + rollback; migration chạy trên empty/upgrade fixture; CI không cần secret production. Test local, controlled real-account và production tách riêng. Zalo cá nhân không gọi là official sandbox khi chỉ dùng account test. ACCOUNT_RISK_REVIEW_REQUIRED/MOCK_ONLY/REAL_ACCOUNT_BLOCKED phải ghi rõ.

Commands mục tiêu sau scaffold: pnpm lint, typecheck, test, test:contracts, test:security, test:e2e, eval, build. Chưa có app scripts ở planning baseline; không báo đã chạy khi chưa tồn tại.

Bàn giao: Task/Status; implementation và files; command thực chạy + result; acceptance evidence; connector/account capability chưa xác minh; migration/rollback; next dependency. Không tự báo production-ready trước QA và owner sign-off.
