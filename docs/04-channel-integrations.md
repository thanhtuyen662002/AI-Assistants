# 04 — Zalo cá nhân và WhatsApp: tích hợp theo đúng transport

Phạm vi Zalo đã sửa theo chủ dự án, không OA. Nguồn P1–P6 ở docs/10; nguồn WhatsApp S6–S11 và giới hạn kiểm chứng ở docs/00. Chưa cài connector, chưa login, chưa có tin gửi thật.

## 1. Contract chung, hai ingress khác nhau

`normalize(verifiedTransportEvent)`, `evaluateSend(trustedContext)`, `send(authorizedIntent)`, `getHealth(binding)` là capability chung. Không ép mọi adapter có verifyWebhook/refreshCredentials: WhatsApp dùng webhook/token; Zalo cá nhân dùng owner QR/session/listener. `TrustedBinding` và scope chỉ server tạo từ registry.

Capability registry: channel/account, transport, implementation/version/integrity, supported inbound types, sender result/receipt semantics, reconnect/history/self-event capabilities, identity mapping, credential lifecycle, restrictions, rate policy/unknown, checked_at và evidence. Mỗi capability là verified/unsupported/unverified; không suy từ README thành account test passed.

## 2. Zalo Personal Bridge — SB-27 rồi SB-07

### A. Chuẩn bị và quyền sở hữu

Dùng tài khoản cá nhân do chủ dự án sở hữu/ủy quyền; không yêu cầu OA/App/OA token. Chọn máy/server do chủ dự án kiểm soát để chạy bridge thường trực. SB-27 đánh giá upstream `RFS-ADRENO/zca-js`, pin package/version/lockfile/integrity/license và review dependencies. Không cài fork chỉ vì có lời quảng cáo tránh khóa hoặc tính năng không có ở upstream.

Nguồn P1 xác định thư viện unofficial và có rủi ro khóa/ban. P4 là cảnh báo Zalo Help qua chỉ mục tìm kiếm, không toàn văn điều khoản. Trước dùng account thật phải owner xem rủi ro, điều khoản hiện hành, quyền xử lý dữ liệu và chủ động cho phép test. Không có cấu hình chống khóa được bảo đảm; human approval/low throughput không làm connector trở thành official.

### B. QR và session

Console chỉ owner/admin binding được tạo phiên login. Bridge khởi tạo QR theo API của phiên bản đã pin; owner tự quét và xác nhận trên điện thoại. QR hiển thị authenticated/no-store/TTL ngắn, không gửi email/chat/Git, không lưu screenshot telemetry. Session thành công lưu mã hóa bằng secret/key reference, không đưa cookie vào response frontend/LLM. Không yêu cầu gửi mật khẩu/OTP/cookie trong chat; không triển khai tự lấy credential từ thiết bị khác.

Lưu account UID, binding, secret reference, session generation, last heartbeat, listener epoch và state riêng. Revocation/logout/disconnect hủy listener và QR, thu hồi quyền bridge, purge session/derived secret. Expired/restricted/challenged → `REAUTH_REQUIRED` hoặc `PAUSED`, dừng send; owner đăng nhập lại hợp lệ. Không vòng QR/relogin, CAPTCHA bypass hoặc thay proxy/account để né chặn.

### C. Một listener/account

Nguồn P1 nói chỉ một web listener cùng lúc; mở Zalo Web có thể dừng listener. Worker deployment dùng active/passive và fenced lease, không scale nhiều listener cho cùng account. Lease mất thì bridge dừng cả ingest/send; backend từ chối stale epoch. Reconnect có backoff hữu hạn cho lỗi mạng; xung đột phiên với owner phải pause/alert thay vì tranh quyền liên tục.

Kịch bản phone/desktop/web coexistence phải test trên phiên bản/account thực. Không suy rằng đăng nhập thành công có nghĩa Zalo Web và bridge cùng hoạt động ổn định. Chưa có chính sách recovery/history được xác minh thì ghi unverified.

### D. Nhận tin và privacy filter

Dùng listener message theo API đã pin. P2 cung cấp `threadId`, `type` (User/Group), `isSelf`; ghi fixture sanitized để xác minh cấu trúc message ID/timestamp/text/sender/recipient. Chỉ accept text 1:1 trong allowlist CSKH. Thread chưa được chọn, nhóm, danh bạ, lịch sử riêng không persist/log/embed/gửi LLM. Owner có thể nhập/chọn ID hội thoại kinh doanh có quyền; không cần dump friends để onboarding.

`isSelf=false` ở thread hợp lệ → inbound.message. `isSelf=true` → outbound.echo để resolver kiểm human/bot, không tạo vòng chat. Message ID/thời gian cần được derive từ trường đã chứng minh, không bịa provider ID. Unsupported media không auto fetch arbitrary URL hoặc tuyên bố đã đọc nội dung.

Bridge có encrypted bounded local spool, retry gửi nội bộ đến API; server authenticated bằng mTLS hoặc HMAC bridge-specific + nonce/timestamp/body hash, bind credential/account/epoch. Backend derive tenant. Commit durable inbox trước trả ACK cho bridge. Đây **không phải webhook được Zalo ký**. HMAC nội bộ không chứng minh provider authenticity nếu bridge bị compromise.

Spool chống mất từ thời điểm persist; không bảo đảm event lúc bridge offline. Mất kết nối, process crash, full disk hoặc gap phải ghi metric/đánh dấu coverage, pause auto cho phạm vi chưa đối soát. Nếu không có recovery evidence, yêu cầu đối soát thủ công; không tự xóa gap. Historical catch-up nếu có phải tag `historical`/no-reply và kiểm privacy/tombstone, không biến backlog cũ thành hàng loạt reply mới.

### E. Gửi và handoff

Outbox gửi command đã authorize đến bridge sở hữu đúng epoch. Recheck account/session/heartbeat, mode, conversation allowlist, consent/suppression, ownership version, budget và intent freshness. Text mapping dùng `sendMessage`/thread type theo upstream đã pin; không gọi OA endpoint. Result giữ provider IDs khi có; receipt unsupported thì không giả delivered/read.

`isSelf` chỉ xác định event từ account, **không phân biệt người/bot** [P2]. Đối chiếu provider/client IDs đã xác minh với outbox: matched → system echo, không kích LLM; unmatched/ambiguous → human takeover bảo thủ, cancel pending bot. Test self message từ mobile/PC/Web. Nếu một thiết bị không quan sát được đáng tin thì AUTO bị chặn trong chế độ sử dụng song song đó; người cần tắt bot/claim trước gửi ngoài console, hoặc dùng manual copilot. Không báo đạt handoff chỉ nhờ test nút trong console.

Tin đã dispatch trước takeover có thể không thu hồi; hiển thị in-flight. Sender và bridge cùng fencing/ownership check. Unknown send timeout không retry mù; reconcile bằng evidence nếu có, còn lại review thủ công.

### F. Policy personal, không OA

Không áp OA 48h/7d, OAuth refresh, gói OA, ZBS template hoặc chữ ký OA. Không suy ngược là personal gửi không giới hạn hoặc miễn phí mọi chi phí. Chỉ phản hồi CSKH được cho phép; disable proactive follow-up/bulk/group/friend requests. App quotas/token/cost budgets bảo vệ hệ thống nhưng không thay policy platform, không bảo đảm tài khoản không bị khóa. Unknown capability/policy/challenge → pause/draft-only.

### G. Nghiệm thu có kiểm soát

Owner QR/revoke; session secret redaction; one-listener failover/stale epoch; inbound/send text và IDs; self echo/manual activity; allowlist lọc tin riêng **trước persist**; duplicate/out-of-order; DB down/spool full; restart/session invalid; disconnect/gap; unknown-send; takeover khi LLM chạy; challenge/account restriction. Không gọi đây là official Zalo sandbox. Không load-test spam account thật. Mock throughput đo backend riêng.

## 3. WhatsApp Business Platform / Cloud API

Giữ giả định baseline, chưa được chủ dự án đổi sang personal WhatsApp. Account: business portfolio/WABA/phone/Meta app đúng quyền, official test recipient và credential phù hợp. Pin supported Graph API version khi implement. Không dùng SDK WhatsApp Node archived [S10] hoặc WhatsApp Web session automation.

GET webhook handshake kiểm mode/verify token, trả challenge; không dùng verify token thay App Secret. POST raw-body `X-Hub-Signature-256` verification theo live docs, constant-time compare/size limit; map phone/WABA → tenant registry. Process mọi entry/message/status; outbound/status không mở cửa sổ khách. Fixture thực sanitized và docs S9 phải kiểm lại vì baseline chưa đọc đầy đủ.

Theo nguồn S6 ở baseline: freeform response trong cửa sổ 24h từ tin khách; ngoài khung dùng approved template với điều kiện liên quan, opt-in/opt-out và lối chuyển người. Sender recheck trước dispatch, kể cả tin nhân viên. Template registry name/language/category/version/status/checked_at; paused/rejected/wrong purpose → deny; không nhét arbitrary AI answer vào template variable để lách policy.

24h eligibility không đồng nghĩa giá 0. Rate card/currency/market/category/effective date/tax/BSP nếu có phải xác minh hiện hành; S7/S8 ở baseline còn chưa giải quyết đủ. Không hard-code rate hoặc tự báo Meta chấp thuận AI use case khi chưa review S11.

Test challenge/signature/tamper/batch/binding mismatch/duplicate/late status; 24h boundary fake clock; opt-out while queued; template status changed; revoked token; 429; timeout accepted-but-unknown; actual delivery với recipient đồng ý thử. WhatsApp readiness không cần OA Zalo, personal readiness không thay điều kiện WhatsApp.

## 4. Retry, cost và policy engine

Shared trusted input: binding/customer/consent/purpose/mode/ownership, account health, policy version, budget. Personal bổ sung session generation/epoch, thread allowlist, gap/self-visibility/restriction state; WhatsApp bổ sung customer window/template registry/rate card. Output allow_freeform/allow_template/draft_only/handoff/deny + reason/version/expiry + cost estimate/unknown. allow_template không có implementation personal trong MVP.

Validation/auth/restriction không retry tự động. 429 dùng provider evidence/Retry-After khi có và circuit breaker; không lặp để né limit. Lỗi mạng an toàn mới retry hữu hạn. Side effect mơ hồ → unknown/reconcile. HTTP success có body error vẫn là lỗi. Split text theo provider cap đã kiểm tra, Unicode-safe và per-segment idempotency; không split thành flood. Replay vẫn qua mọi safety gate và expiry; historical event không auto-send.
