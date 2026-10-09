# 04 — Hợp đồng kênh hiện hành

Đọc [MASTER_PLAN §7](../MASTER_PLAN.md#channels), [§8](../MASTER_PLAN.md#reliability) và [quyết định Zalo cá nhân](10-zalo-personal-decision.md). Không dùng bất kỳ OA OAuth/token/webhook/cửa sổ 48h–7d nào cho personal.

## Interface cần chốt SB-03

`ChannelAdapter` gồm capability snapshot, normalize verified transport, evaluate trusted send context, send authorized intent, reconcile unknown outcome và lifecycle health. Auth ingress riêng: WhatsApp kiểm provider signature; personal bridge kiểm service credential/binding/epoch. Không ép cả hai giả làm provider webhook.

`CapabilityRecord` lưu provider/implementation/version/integrity, account/binding, checked_at, observed environment, feature, supported/unsupported/unverified, evidence_ref và reviewer. Bằng chứng nhạy cảm ở kho riêng, không public Git. Connector implementation chọn sau spike, không import nguyên code demo chưa kiểm.

## Bộ nghiệm thu Zalo SB-27/SB-07

Owner consent trước login; QR TTL/no-store/owner-only; encrypted session/revoke; một listener/fencing; collision với phiên Web; inbound/outbound IDs và Unicode; self event mobile/PC/Web; correlate echo; duplicate/order; network gap; spool-full; restart; timeout sau send; có/không delivery evidence. Không suy khả năng replay/history khi chưa chứng minh. Self visibility hoặc gap không rõ thì không auto song song thiết bị ngoài console.

Chỉ 1:1 allowlisted CSKH; lọc trước persist. Group/friends/family ngoài allowlist không đi LLM/spool; chỉ counter tổng hợp nếu cần. Failover không active-active; reconnect không tự resume. Rate cap để bảo vệ vận hành, không hứa né khóa tài khoản. Manual fallback không dùng session và không báo đã đồng bộ tự động.

## Bộ nghiệm thu WhatsApp SB-08

Account type/business eligibility xác nhận; current API version/scopes, test recipients và secret riêng. GET challenge không thay POST signature; validate raw body/account binding; mọi entry/message/status trong batch. Tin khách mới cập nhật 24h watermark; delivery/outbound không mở lại cửa sổ. Templates phải đúng purpose/consent/language/status đang có hiệu lực.

Test boundary với fake clock, forged/tampered request, wrong account, revoked token, 429/Retry-After, status out-of-order, paused template khi queued, opt-out và unknown-send. Rate card/AI-use-case terms chưa rõ chặn gate live tương ứng, không cost=0. Không dùng WhatsApp Web session để thay Cloud API assumption.

## Policy SB-09

Pure evaluator có mock capability record từ contracts nên không chờ credentials SB-07/08. Decision gồm reason/version/expires_at và estimated_cost known-or-unknown. Sender kiểm lại policy, ownership, consent, channel health, source validity và budget ngay trước dispatch. Human console sends cũng không bypass. Live readiness chỉ theo [gate profile](../planning/release-gates.json), không theo một test mock.
