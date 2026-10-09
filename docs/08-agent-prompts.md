# 08 — Prompt giao coding agents: Zalo cá nhân

Đây là prompt xây phần mềm, không system prompt gửi khách. Task ownership không tự assign/run agent. Đọc docs/10 trước mọi kết luận về Zalo.

## Lead kickoff

```text
Bạn là Lead repo thanhtuyen662002/AI-Assistants.
Chủ dự án đã xác nhận dùng tài khoản Zalo CÁ NHÂN, KHÔNG phải Zalo OA.
Đọc README.md, AGENTS.md, docs/10-zalo-personal-decision.md, docs/01..09,
planning/backlog.json và contracts hiện hành.

Không hỏi lại OA hay yêu cầu OA ID/App/OA token. WhatsApp giữ Cloud API giả định,
không tự đổi sang WhatsApp Web từ đính chính Zalo.
Kiểm tra head/code/PR hiện tại để không ghi đè agent khác.
Bắt đầu SB-01/SB-02, rồi SB-03. Cho Channels làm SB-27 kiểm chứng personal
connector sớm; các module memory/tools/console/QA tiếp tục mocks đúng contract.
SB-07 là Zalo Personal Bridge qua QR/session/listener, không OA webhook.

Ứng viên zca-js unofficial, có rủi ro khóa account. Chưa được owner cho phép
và review rủi ro/terms thì không login/gửi tin account thật. Không báo official
hoặc no-ban. Dùng manual copilot fallback nếu bridge chưa đáp ứng, ghi rõ
chưa tự động đồng bộ chứ không tự đổi scope sang OA.

Giữ hard gates: tenant/customer/binding isolation, chỉ thread CSKH allowlist,
private session/QR/spool, một fenced listener/account, no-loss caveat/gap,
human manual activity, source validation, deletion, tool approval, idempotency,
unknown send reconciliation, account restrictions/cost/kill switches.
Không vượt CAPTCHA/anti-bot, scrape friends/phones hoặc bulk/friend spam.

Một nhánh/PR mỗi task, không force-push main hoặc tự merge. Không commit secrets,
QR/cookies/PII. Task blocked credentials báo rõ nhưng phần mock độc lập tiếp tục.
Mỗi PR nêu commands thực chạy, tests/evidence/risks/migration/rollback.
Không production-ready trước QA+owner. SB-00 vẫn thiếu nội dung hai clip,
không tạo transcript hoặc nhận đã làm theo clip.
```

## Task template

```text
Repo: thanhtuyen662002/AI-Assistants
Role: <Lead|Platform|Channels|Memory|Runtime|Console|QA|Operations>
Task: <SB-XX>; branch agent/SB-XX-short-name
Đọc AGENTS.md, docs/10, task row docs/06 và spec module liên quan.
Check dependency đã review/merge. Dùng mock đúng contract cho phần độc lập;
không gọi MOCK_ONLY/REAL_ACCOUNT_BLOCKED thành integration passed.
Thay root schema/manifest/lockfile cần review owner. Không sửa expected behavior
để che thiếu capability. Không TODO ở auth/scope/ownership/session safety.
Bàn giao PR: files, command+result thật, acceptance evidence, blockers,
version/migration/rollback, next dependency unblocked.
```

## Channels: SB-27,07,08,09

```text
SB-27 đánh giá upstream/version/integrity/license/dependency của zca-js,
capability QR/login/revoke/listener/send/self messages/IDs/history/gaps và
rủi ro account/terms. Chỉ owner tự scan QR trong UI bảo vệ; không cần cookie
paste hoặc password/OTP qua chat. Test live chỉ sau owner cho phép.

Thiết kế bridge thường trực, một active lease với fencing/account, session
mã hóa, business-thread filter trước persist, bounded encrypted spool,
authenticated internal ingest. Không OA OAuth/webhook/window/pricing.
Mất phiên/challenge/restriction/session conflict → pause, không reconnect war.
Không tự hứa catch-up đủ lúc offline; unknown send không retry mù.

isSelf chỉ là cùng account, không phân biệt bot/người. Match outbox IDs;
unmatched/ambiguous self activity takeover bảo thủ. Test từng mobile/PC/Web,
không giả selfListen luôn quan sát hết. Nếu visibility thiếu thì không AUTO
trong chế độ dùng song song đó.

WhatsApp vẫn official Cloud API với raw signatures, template/consent/window,
current rates/terms. Chưa xác minh rate/capability thì fail closed, không 0/free.
```

## Platform: SB-03,04,05,06,12,17

```text
Chốt event v2 zalo_personal/transport, internal bridge auth/fencing schemas,
OpenAPI và typed tools trước downstream. Không diễn giải lại event v1 zalo
baseline OA thành personal. Trusted context server-generated, DB least privilege,
RLS/composite FKs và customer ownership checks.
Durable inbox/outbox/spool ACK semantics và boundaries no-loss rõ ràng.
Lease/session generation/epoch chống stale sends, tenant spoof và split-brain.
Personal control plane không đưa cookie vào browser/LLM.
Handoff có CAS/version, self-event resolver, no automatic resume on reconnect.
Identity tách kênh đến khi verified link; biết order ID không đủ đọc đơn.
```

## Memory: SB-10,11,13,26

```text
Giữ docs/03: published/effective/ACL KB, provenance chunk/version,
Vietnamese hybrid retrieval và exact baseline. Customer memory scoped;
preference có nguồn, candidates không publish policy; xóa/sửa/TTL phủ
summary/vector/cache/jobs/bridge spool và restore suppression.
Chỉ dữ liệu CSKH được owner/khách cho phép, không ingest personal history,
nhóm/bạn bè chỉ vì account được login. Historical import cần quyền riêng
và no-reply semantics. Không train model bằng chat, không học policy từ lời khách.
```

## Runtime: SB-14,15,19

```text
Bounded workflow và typed JSON proposals; auth/source/approval/send gates ở code.
Live order/price từ authorized tools, failure không success, private context tối thiểu.
No SQL/shell/arbitrary HTTP. Writes có preview/approval/hash/expiry/freshness/
idempotency/reconcile; monetary execution disabled.
No bot reply sau handoff, session gap/restriction hoặc source revoked;
không auto-reply historical events. Tôn trọng epoch/ownership trong sender.
```

## Console: SB-16,18

```text
Unified inbox/drafts/source/memory review; contract mocks trước backend.
Thêm owner-only QR/session status/disconnect, thread allowlist, gap/coverage và
account-risk warning. QR no-store/TTL, không screenshot public hoặc telemetry.
Không show cookies/token, không direct send ngoài outbox/policy.
Phân biệt accepted/delivered/unknown/manual external send; không hứa mobile
handoff được phát hiện nếu capability chưa verified. Manual copilot phải ghi rõ
không auto-sync; role controls ở UI không thay server auth.
```

## QA: SB-21,22,24

```text
Seed→≥200 labeled cases +50 human review; deterministic scope/state tests và model
eval tách nhau. Test bridge credential/binding/nonce/epoch, QR/session leak,
private-thread filter trước persist, stale listeners, disconnect/spool full,
gap/history no-reply, self echo vs human, manual mobile reply while LLM runs,
unknown-send, purge/restore. Zero leak/unauthorized action là hard gate.
Zalo personal dùng controlled real-account tests, không official sandbox.
Không chạy backend load target vào Zalo thật. Missing capability hoặc skipped
integration phải báo blocked, không sửa expectation cho pass.
```

## Operations: SB-02,20,23

```text
Pin toolchain/containers/lockfile; local defaults mock and personal disabled.
Bridge là service thường trực, session volume mã hóa, secrets references,
one-active-listener fencing, controlled failover; không short-lived function.
CI không personal login/session/QR, không provision dịch vụ trả phí tự ý.
Observability gồm account health/gap/spool/epoch/restriction, no PII/secrets.
Restore với sender/listener OFF, apply deletion suppression; không phục hồi
session revoked rồi replay tin. Cost unknown khác 0, fallback model approved only.
```

## Reviewer

```text
Review diff và evidence thật theo task/AGENTS/docs10, không chỉ mô tả PR.
Tìm bypass tenant/customer/thread allowlist, session QR/credential boundaries,
lease fencing, human handoff, source validation/deletion/approval/budget.
Chặn nhánh OA cũ lọt vào personal, fake provider signature/delivery/no-loss,
no-ban promises, anti-bot evasion hoặc tự bật account thật.
Skipped mandatory gate không passed. Nêu file/line, impact và acceptance cần chứng minh.
```
