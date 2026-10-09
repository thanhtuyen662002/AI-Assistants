# 10 — Zalo cá nhân là yêu cầu, không phải OA

Quyết định chủ dự án giữ nguyên: dùng account Zalo cá nhân đang sử dụng. Sai lệch baseline đầu là loại tài khoản, không phải account thật so với account test. Không có OA token/App/OAuth/ZBS hoặc cửa sổ 48h–7d trong đường personal.

Thiết kế hiện hành: [MASTER_PLAN §7](../MASTER_PLAN.md#channels), [adapter checks](04-channel-integrations.md), [nguồn E3/E3b](00-source-review.md). `zca-js` là **ứng viên unofficial**, chưa cài hoặc kiểm chứng trên tài khoản người dùng. Login QR/nhân viên duyệt tin/rate cap không làm nó thành API được Zalo chấp thuận hoặc bảo đảm không bị khóa.

SB-27 phải kiểm upstream/version/integrity/license/dependency, owner authorization, one-listener/collision, session revoke/restart, self visibility trên mobile/PC/Web, IDs/unknown-send, gaps và privacy filter. Supported/unsupported/unverified cần evidence, không suy từ một README hoặc UI demo. Khi thiếu capability cần cho auto, giữ manual/bridge-copilot phù hợp và báo giới hạn; không tự đổi sang OA.

Một fenced bridge thường trực/account, session được mã hóa và không tới LLM/browser logs; allowlist CSKH 1:1 trước spool/persist, không gom group/family/history. Listener offline không có guarantee replay đầy đủ; gap unresolved dừng auto. Người dùng trả tay ngoài console phải có evidence self-visibility hoặc tắt bot trước; không tự coi isSelf phân biệt bot/người.

Manual copilot không dùng connector/session: operator đưa đoạn cần hỗ trợ, nhận draft có nguồn, tự gửi trên ứng dụng chính thức. Đây không là hoàn thành đồng bộ tự động. Bridge-copilot vẫn có account risk unofficial.

Hai clip đã có visual evidence; chúng **không chứng minh** thư viện hoặc loại tài khoản phía sau demo. Full audio chưa đối chiếu, SB-00 partial. Không có login, live send hoặc deployment được thực hiện khi cập nhật plan.
