# 04 — Tích hợp Zalo OA và WhatsApp

Nguồn S1–S11 ở [sổ nguồn](00-source-review.md). Hướng dẫn dưới đây là quy trình implement; chưa có account/token thật hoặc kết quả test provider.

## 1. Interface chung, policy riêng

```ts
interface ChannelAdapter {
  verifyWebhook(rawBody: Uint8Array, headers: Headers, binding: TrustedBinding): Verification;
  normalize(verified: VerifiedWebhook): NormalizedEvent[];
  evaluateSend(ctx: TrustedSendContext): SendDecision;
  send(intent: AuthorizedOutboundIntent): Promise<ProviderSendResult>;
  refreshCredentials(bindingId: string): Promise<void>;
}
```

`TrustedBinding`, `VerifiedWebhook`, `AuthorizedOutboundIntent` là type chỉ server tạo được sau kiểm tra; schema từ client không thay thế authorization. Adapter normalize tất cả entry/message trong một callback, không chỉ phần tử `[0]`. Status và outbound echo không tạo lượt trả lời mới. Bản mock phải mô phỏng duplicate, delay, rate limit, expiration và unknown-send, không chỉ success.

### Bảng capability bắt buộc ghi trước tích hợp thật

`channel/account | api_version | scopes | inbound_types | webhook_signature_spec | retry_behavior | payload_limits | freeform_eligibility | templates | quotas | token_lifecycle | pricing_version | checked_at | evidence`.

Không điền bằng suy đoán. Chỗ chưa biết ghi `unverified`; adapter không tự gửi ở production khi thiếu thông tin bảo mật hoặc quyền gửi.

## 2. Zalo Official Account

### Chuẩn bị account

Chủ doanh nghiệp cung cấp OA thuộc quyền quản lý và có entitlement dùng OpenAPI; tạo Zalo App, liên kết/cấp quyền OA, callback HTTPS và cấu hình webhook theo tài liệu chính thức S3/S5. Xác nhận trạng thái OA, gói/quota và quyền app trong console thực tế. Zalo UID có phạm vi riêng theo OA/app; lưu kèm binding, không dùng UID trần làm khóa global.

Chỉ dùng OA OpenAPI; không hỗ trợ tài khoản Zalo cá nhân hoặc thư viện lấy cookie/session. Secret lưu mã hóa/secret manager. Phân biệt app secret và OA secret đúng loại, không lấy token thay chữ ký.

### Xác thực và token

Làm flow authorization theo tài liệu hiện hành, kiểm `state`, callback allowlist và PKCE nếu flow yêu cầu. Token manager lưu expiry do provider trả về, tự refresh trước hạn với jitter. Refresh single-flight theo OA/binding; cập nhật access + refresh token bằng compare-and-swap/transaction để không ghi đè refresh token mới bằng bản cũ. Retry hữu hạn, lỗi revoked/invalid chuyển `reauthorization_required`; không refresh vô hạn.

Chỉ mục S5 có mô tả tuổi access token nhưng trang không đọc đủ trong phiên. Không hard-code thời hạn từ chỉ mục. SB-07 phải thu được response fixture đã ẩn secret và test token rotation/revocation thực.

### Webhook

Nhận raw bytes, giới hạn body, validate binding/app/OA nhận. S4 mô tả `X-ZEvent-Signature` và công thức `sha256(appId + data + timeStamp + OAsecretKey)`. Đây không tự động là HMAC kiểu Meta; SB-07 phải xác minh chính xác field, encoding, prefix và canonicalization theo version đang dùng bằng callback thật. Không parse rồi JSON.stringify tùy ý để kiểm chữ ký. Không dùng bypass signature ở production.

Timestamp validation phải tách thời điểm sự kiện và thời điểm giao webhook. Cho phép retry hợp lệ theo provider, chống replay bằng dedup; không áp TTL 5 phút máy móc nếu provider có retry dài. Nhận message text, interaction hợp lệ, blocked/unfollow theo capability, outbound echo và delivery nếu account hỗ trợ. Event chưa hỗ trợ → acknowledge sau lưu + metric, không gọi LLM.

### Gửi và điều kiện

Theo S1: tin tư vấn qua OA OpenAPI có khung 7 ngày từ tương tác đủ điều kiện; mốc 48 giờ liên quan chi phí. Không dùng cửa sổ OA Manager làm quyền của OpenAPI. Không coi mọi follow/click là mở toàn bộ cửa sổ tư vấn; map đúng từng event được nền tảng công nhận. Lưu `last_eligible_interaction_at`, `interaction_kind`, evidence và `blocked_at`.

Endpoint tư vấn được tài liệu chính thức liệt kê: `POST https://openapi.zalo.me/v3.0/oa/message/cs`, header `access_token`, body có `recipient.user_id` và `message`. Agent đối chiếu riêng payload text/plain và trích dẫn, giới hạn text và version thực tế trước implement. Nguồn endpoint: https://stc-developers.zdn.vn/docs/v2/official-account/tin-nhan/tin-tu-van/gui-tin-tu-van-trich-dan . Không dùng trường bắt buộc của tin trích dẫn cho mọi loại tin.

Ngoài eligibility: không tự chuyển sang broadcast để né hạn. Tạo handoff hoặc thông báo chủ động bằng ZBS Template Message khi đúng use case, template approved và entitlement/consent; khả năng ZBS nằm ngoài đường gửi text MVP và phải có adapter/schema riêng nếu bật. Không coi template là chỗ nhét câu trả lời AI tùy ý. Mọi giá/quota gắn policy version theo account.

### Nghiệm thu Zalo thật

Text inbound → một receipt → một reply accepted và kiểm tra nhận thực tế. Duplicate không trả thêm. Sai chữ ký/app/OA bị chặn. Refresh song song không mất token. Test ở mốc 48 giờ và 7 ngày bằng clock fixtures; đối chiếu sandbox/account theo quyền thực tế. Human reply từ OA Manager nếu có echo phải được nhận diện/tiếp quản; nếu account không cho quan sát đáng tin, auto mode chỉ dùng khi agent người thao tác qua console của dự án và có SOP rõ ràng.

## 3. WhatsApp Business Platform / Cloud API

### Chuẩn bị account

Chủ doanh nghiệp cung cấp business portfolio/WABA/số điện thoại phù hợp; Meta app, quyền truy cập, cấu hình webhook, test recipient và payment/quota khi cần. Kiểm tra quyền sở hữu, review/verification và phương thức token đang dùng; không coi token phát triển ngắn hạn là credential production. Không đoán có/không coexistence với WhatsApp Business App; xác minh account capability trước thiết kế human echo.

Pin Graph API version còn được hỗ trợ trong config sau SB-08. Không dùng SDK WhatsApp Node đã archived (S10). Có thể dùng HTTP client được bảo trì với contract tests.

### GET handshake và POST callback

GET kiểm `hub.mode`, `hub.verify_token` đúng cấu hình, trả `hub.challenge` khi hợp lệ. Verify token không thay thế App Secret và không chứng minh các POST tiếp theo hợp lệ. POST xác minh `X-Hub-Signature-256` trên raw body với App Secret theo tài liệu hiện hành; constant-time compare, reject header sai định dạng, không log signature/secret. S10 xác nhận sự tách biệt hai bước; S9 cần kiểm lại live docs trước production.

Map phone_number_id/WABA từ payload đã xác thực sang tenant binding do server quản lý. Xử lý mọi entry/change/messages/statuses; text và unsupported media tách rõ. Store provider message ID và recipient scope. Delivery status không cập nhật `last_customer_message_at`; outbound của bot/người không mở cửa sổ phản hồi mới. User message đến muộn chỉ tăng watermark bằng max, không lùi timestamp.

### Policy gửi tin

S6 quy định phản hồi không template trong cửa sổ 24 giờ mở lại bởi tin người dùng; ngoài khung dùng approved template. Có opt-in phù hợp cho tin chủ động và tôn trọng opt-out. Automation cần lối chuyển người rõ ràng. Những điều này được kiểm ở sender, kể cả tin nhân viên gửi từ console: con người cũng không bỏ qua policy kênh.

Template registry lưu ID/name/language/category/version/status/checked_at. Template bị pause/reject hoặc không khớp mục đích → chặn. Chỉ whitelist biến được phép; không đưa nguyên câu trả lời bất kỳ vào placeholder để lách policy. Bật follow-up sau pilot, kiểm purpose-specific consent và suppression list ngay trước gửi.

### Pricing / AI use case — chưa chốt

Quyền gửi trong 24 giờ **không đồng nghĩa mặc định miễn phí**. Tình trạng chưa xác minh rate card tháng 10/2026 đã ghi ở tài liệu 00. Tách `send_eligibility` khỏi `cost_estimate`; unknown price không chuyển thành 0. Production phải có rate card hiệu lực, currency, market, taxes/BSP fee nếu có, budget và đối soát delivered message.

Sản phẩm giới hạn trong CSKH của doanh nghiệp, không biến thành trợ lý AI tổng quát trên WhatsApp. SB-25 cần review điều khoản AI áp dụng cho account, nhà cung cấp model và dữ liệu; chưa đọc được S11 trong phiên nên không tuyên bố use case tự động đã được Meta chấp thuận.

### Nghiệm thu WhatsApp thật

GET challenge đúng/sai; POST chữ ký hợp lệ/sai body; payload nhiều messages; inbound/outbound/status khác nhau; send text đúng khung; template approved/rejected; delivery failure; opt-out; account/scope sai; token revoked; 429; timeout sau acceptance; duplicate callback. Mock clock test 23:59:59, 24:00:00 và 24:00:01 theo quy tắc biên đã ghi nhận; dùng khoảng nửa mở bảo thủ nếu chưa có xác nhận khác.

Nguồn bổ sung để lấy payload fixture gốc: workspace Meta trên Postman, https://www.postman.com/meta/whatsapp-business-platform/folder/tduohwq/webhook-payload-reference . Phiên bản fixture phải được ghi và kiểm lại với live account; không dùng dữ liệu người thật trong repo.

## 4. Policy engine chung

Input trusted: tenant/channel/account, timestamp nguồn, loại tin, consent/purpose, block state, handoff/ownership version, mode, template approval, quota, budget. Output: `allow_freeform | allow_template | draft_only | handoff | deny` + reason codes + policy version + estimated cost/unknown + expiry.

Fail-closed cho policy chưa xác minh, thiếu consent, template không duyệt, channel revoked, unknown recipient, human takeover hoặc kill switch. Đánh giá lại khi job delayed/retry, không tái dùng quyết định allow đã hết hạn. Chuẩn hóa UTC trong storage, hiển thị Asia/Ho_Chi_Minh cho operator; không so sánh cửa sổ bằng ngày lịch địa phương.

## 5. Retry và lỗi

Lỗi validation/auth/policy không retry tự động. 429 theo Retry-After, exponential backoff có jitter, per-account throttling. 5xx retry chỉ khi biết chưa có side effect hoặc provider có idempotency phù hợp. Network timeout sau write chuyển unknown và đối soát. Không nuốt HTTP 200 có body error code. Truncate/split tin phải theo codepoint/UTF-8 và giới hạn provider, giữ ý nghĩa, nguồn và chuỗi idempotency của từng segment.
