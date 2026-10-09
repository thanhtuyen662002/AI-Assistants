# Kế hoạch hợp nhất v3 — Wiki có nguồn + ký ức khách + agent CSKH

Ngày: **2026-10-09**. Repo: `thanhtuyen662002/AI-Assistants`. Mục tiêu là tăng khả năng triển khai thành công bằng cách giảm phụ thuộc chưa biết, có luồng hoàn chỉnh sớm và chứng minh chất lượng từng bước; **không hứa tỷ lệ thành công 95–100% khi chưa đo**.

Đặc tả này thay các quyết định mâu thuẫn trong hai baseline trước. Lịch sử Git vẫn giữ nội dung cũ. Schema hiện hành được chỉ rõ trong `contracts/current.json`. Task IDs SB-00…SB-27 được giữ; SB-28…SB-33 bổ sung phần wiki và nghiệm thu hợp nhất.

<a id="scope"></a>
## 1. Phạm vi chốt và điều chưa biết

**Đã xác nhận:** Zalo cá nhân đang sử dụng; bộ não thứ hai cho CSKH; có WhatsApp; coding agents sẽ triển khai từ repo. Không cần OA, OA token, Zalo App hoặc ZBS cho nhánh personal.

**Giả định để bắt đầu:** một doanh nghiệp pilot, một tài khoản Zalo, text 1:1 và tiếng Việt; WhatsApp Business Platform/Cloud API; TypeScript monorepo. Ngành hàng, CRM, model, ngân sách, loại account WhatsApp và chính sách doanh nghiệp chưa biết. Ghi assumption, dùng synthetic fixtures; không bịa giá hay policy thật và không hỏi lại loại Zalo.

MVP giải quyết năm hành trình: FAQ có nguồn; nhớ preference đã cho phép của đúng khách; tra đơn read-only sau xác minh; tạo ticket idempotent sau xác nhận; chuyển nhân viên và dừng bot. Thêm vận hành wiki để chủ doanh nghiệp nạp/sửa/duyệt tri thức và xem nguồn của từng câu trả lời.

**Không làm ở MVP:** group/bulk marketing, auto-friend/quét số, voice/OCR/video, clone giọng, trợ lý mọi chủ đề, graph database riêng, fine-tune chat khách, đội agent runtime tự do, tự hoàn tiền, billing SaaS, sync Obsidian hai chiều. Những thứ xuất hiện trong demo nhưng không phục vụ năm hành trình không được kéo vào đường hoàn thành MVP.

<a id="synthesis"></a>
## 2. Kết hợp hai clip như thế nào?

Sổ bằng chứng: [docs/00-source-review.md](docs/00-source-review.md). Chỉ phần hình/màn hình đã kiểm chứng được dùng làm bằng chứng; âm thanh toàn bộ còn chưa đối chiếu.

| Đầu vào | Giữ lại | Bổ sung để dùng được trong CSKH |
|---|---|---|
| Clip 1: raw/Clippings, CLAUDE.md, wiki sources/entities/concepts/analysis, index/overview/log, liên kết và cập nhật | Tri thức có cấu trúc, bản gốc tách bản biên soạn, nhật ký và nguồn | Quyền thật bằng code, patch có base revision, kiểm lỗi, duyệt, published release và rollback |
| Clip 1: nạp tài liệu rồi cập nhật trang liên quan | Curator đọc và tổng hợp từng nguồn, không chỉ cất file | Dependency graph, invalidation, chống mâu thuẫn và không suy luận fact thiếu bằng chứng |
| Clip 2: ứng dụng tri thức vào trợ lý, giao diện chữ/giọng nói và các nút kênh | Một bộ tri thức phục vụ nhiều điểm giao tiếp | Text CSKH trước; connector được kiểm riêng, không suy backend từ giao diện |
| Clip 2: màn hình báo cáo việc/tin/usage và việc chưa giải quyết | Báo cáo tình trạng, lỗi và công việc còn mở | Số liệu lấy ledger/event thật, không để LLM tự kể số token/tin đã gửi; báo cáo là tính năng tùy chọn, không tự tạo lịch |
| Baseline hệ thống | Private memory, tools, scope, handoff, inbox/outbox, eval | Ghép với wiki đã biên soạn; không thay tất cả bằng một thư mục Markdown hoặc một vector DB |

Trong hình clip 1 có chỗ ghi ba thao tác nhưng phần hiển thị chưa đủ thao tác thứ ba. **Rà soát/lint/publish dưới đây là phần thiết kế bổ sung**, không gán thành lời tác giả.

<a id="architecture"></a>
## 3. Kiến trúc: tách biên soạn và phục vụ khách

```text
CURATION PLANE (offline / asynchronous)
Upload được phép → quarantine → raw version + source registry
Clippings thủ công ───────────→ curator đề xuất wiki patch
        → lint/nguồn/ACL/mâu thuẫn → reviewer → build release
        → atomic publish pointer → derived lexical/vector/link indexes

SERVING PLANE (online / bounded)
Zalo Personal Bridge → lọc hội thoại CSKH → encrypted bounded spool
                      → authenticated internal ingest ┐
WhatsApp Cloud API → signature-verified webhook ───────┤
Manual copilot → operator nhập đoạn cần hỗ trợ ───────┘
             → durable inbox → dispatcher/queue → workflow
             → published wiki + private customer memory + live tools
             → grounded draft → policy/ownership/source validation
             → outbox → transport sender hoặc manual copy

CONTROL PLANE
Auth/RBAC + channel health + review + takeover + privacy + kill switch
```

**Chọn một nguồn chuẩn cho mỗi loại dữ liệu:** raw version là bằng chứng gốc; immutable published wiki revision là nội dung phục vụ; PostgreSQL giữ registry, release pointer, scope, hội thoại, fact, công việc và audit; pgvector/lexical/link indexes là dữ liệu dẫn xuất có thể dựng lại. Obsidian chỉ là workspace biên tập và xem mạng liên kết. Không phụ thuộc máy Obsidian đang mở để trả khách; không đọc trực tiếp workspace đang sửa vào production.

Stack đề xuất: TypeScript, Fastify API, Next.js console, Node worker và Node bridge chạy thường trực, PostgreSQL + pgvector, Redis + BullMQ, S3-compatible storage. Cần pin phiên bản được hỗ trợ và lockfile tại SB-02; không dùng version/model đoán. Chưa cần microservices ngoài bridge có vòng đời session riêng. Một codebase, các process có credential/role khác nhau.

Layout mục tiêu: `apps/api`, `apps/worker`, `apps/console`, `apps/zalo-bridge`; `packages/contracts`, `auth`, `db`, `channels`, `identity`, `knowledge`, `memory`, `agent-runtime`, `tools`, `observability`; `tests`, `evals`, `infra`. Curator có thể là worker riêng cùng codebase nhưng quyền khác runtime. Không cho một LLM vừa trả khách vừa có quyền sửa wiki published.

<a id="wiki"></a>
## 4. Wiki: nạp → hỏi → rà soát → phát hành

Hợp đồng chi tiết và vault mẫu: [docs/11-wiki-contract.md](docs/11-wiki-contract.md). Cấu trúc đích của workspace riêng:

```text
brain-workspace/
  CLAUDE.md                 # hướng dẫn curator, không phải security boundary
  raw/                      # tài liệu gốc theo version, curator read-only
  Clippings/                # tài liệu chờ kiểm quyền/duyệt, không auto-answer
  wiki/
    index.md                # mục lục được dựng từ registry
    overview.md             # tổng quan ngắn, cũng có nguồn khi có factual claims
    log.md                  # nhật ký thay đổi, không chứa PII
    sources/                # mỗi nguồn một trang dẫn xuất
    entities/               # sản phẩm/tổ chức thuộc doanh nghiệp, không CRM khách
    concepts/               # khái niệm/phương pháp
    analysis/               # tổng hợp có nguồn, phân biệt inference
    playbooks/              # quy trình CSKH bổ sung, có review
```

**Nạp:** validate quyền sử dụng/MIME/size → malware/quarantine → extract → hash/version → source registry. Raw import mới không tự trở thành tri thức được phép trả khách. MVP hỗ trợ text/Markdown và PDF có text layer; bảng/scan extraction không chắc → review, không chạy OCR tự động rồi coi đúng.

Curator lấy chỉ những trang cần cập nhật, tạo patch với `base_release_id`, revision/hashes, source refs và reason; không sửa raw, không tự publish, không tự đổi CLAUDE.md/ACL. Nguồn trùng hash không tạo work vô ích. Nguồn mới mâu thuẫn phải nêu conflict; không ghi đè âm thầm. Người review kiểm source, meaning và mức thẩm quyền; ngày mới hơn không tự làm một tài liệu đáng tin hơn policy đã duyệt.

**Rà soát:** schema/frontmatter, wikilinks/backlinks, source hash/locator, missing evidence, numeric/date/negation fidelity, orphan notes, duplicate entities, unresolved conflicts, ACL và injection. Link graph chỉ giúp tìm liên hệ, không chứng minh quan hệ có thật. Tách relation đã có nguồn và inference. Khách thật không thành entity trong shared wiki.

**Phát hành:** frozen candidate → kiểm patch base không stale → lint/eval/reviewer → build immutable manifest/pages/chunks/index entries với release ID → kiểm đầy đủ → transaction đổi active pointer bằng CAS và tăng epoch. Job build lỗi giữ bản đang phục vụ; không để nửa trang bản mới/nửa index bản cũ. Review DB là nguồn phê duyệt, không tin người sửa frontmatter tự ghi `published`.

Nguồn bị revoke/xóa hoặc ACL thay đổi phải chặn tức thì bằng registry/epoch ngay cả khi vector/cache chưa purge. Dependency graph đánh dấu các trang/chunk dẫn xuất không hợp lệ. Rollback là tạo release an toàn từ nội dung cũ sau kiểm quyền/nguồn/tombstone hiện tại, **không** phục hồi dữ liệu đã xóa hoặc quyền cũ bằng việc đổi pointer mù.

**Hỏi:** runtime chỉ đọc release hiện hành và source phục vụ đã được duyệt. Retrieval lexical + vector + tối đa một bước mở rộng liên kết có ACL; raw fallback chỉ với source `serving_eligible` còn hiệu lực, không với Clippings/draft. Truy bằng mã SKU/đơn hàng không được biến đổi. Exact-search baseline để so với approximate index. Tính Recall@5 trên câu có nguồn đích, không dùng similarity làm độ chắc đúng.

Mọi claim nghiệp vụ trong câu trả lời phải truy được từ wiki tới source version/locator, hoặc live tool result/as_of. Source ID tồn tại chưa đủ: kiểm nội dung hỗ trợ claim, negation, ngày/tiền/đơn vị. Link công khai hợp lệ mới gửi khách; ref private chỉ hiển thị cho nhân viên có quyền. Không có bằng chứng → hỏi lại/handoff.

<a id="memory"></a>
## 5. Bộ nhớ riêng và thông tin sống

Năm lớp: working context theo conversation; wiki doanh nghiệp; customer facts có nguồn; episodic case history; playbooks. Wiki không chứa hồ sơ khách hàng thật. Ký ức riêng chỉ truy vấn theo tenant + customer; summaries vẫn có source refs và scope.

Fact workflow: candidate → policy/consent/allowlist → confirmed hoặc rejected → superseded/expired/deleted. Preference đơn giản được chính khách nói rõ có thể auto-confirm nếu policy cho phép; quyền admin, tài khoản, địa chỉ, thông tin nhạy cảm không được LLM tự xác nhận. Confidence tự chấm không thay bằng chứng. Never store password, bank OTP, card secret hoặc dữ liệu không phục vụ CSKH.

Identity là `(tenant, binding, external_user)`. Zalo và WhatsApp mặc định tách hồ sơ. Không merge theo tên/ảnh/số tự khai; verified linking là V1 có proof/TTL/revoke/audit. Order API còn cần xác minh sở hữu tại nguồn, không chỉ thấy mã đơn trong chat.

Giá/tồn kho/trạng thái đơn hàng lấy live API, kèm as_of và thời hạn dùng kết quả theo nghiệp vụ. API lỗi phải nói chưa kiểm được; không lấy episodic memory thay hiện trạng. Summary chỉ là context nén, không được làm nguồn chính sách hoặc cấp quyền.

Retention là quyết định owner/privacy review, không là thời hạn pháp lý do plan đặt. Default đề xuất trước review: context làm việc 24h sau đóng phiên; raw transport 7 ngày; transcript 90 ngày; preference review lại sau 180 ngày; audit ít PII 180 ngày. TTL job không thay xử lý yêu cầu xóa sớm.

Xóa/sửa có verification, tombstone và generation; propagate source→wiki/summary/fact/vector/cache/object/spool/jobs/export. Job cũ không tái tạo dữ liệu. Raw read-only chỉ ràng buộc curator, không cấm privacy service xóa. Backup có expiry và suppression khi restore; không hứa xóa tức thì mọi backup bất biến.

<a id="runtime"></a>
## 6. Workflow trả lời và hành động

`RECEIVE → AUTH_SCOPE → CHECK_MODE/HANDOFF → CLASSIFY → RETRIEVE → OPTIONAL_TOOL → DRAFT → VALIDATE → OUTBOX → MEMORY_CANDIDATE`.

MVP dùng một workflow có trạng thái persisted, không runtime multi-agent tự do. Classifier/risk của model chỉ là tín hiệu. Gateway code cưỡng chế scope, policy, tool registry, approval và ngân sách. Model không nhận session/token/SQL/shell/arbitrary URL.

Structured decision dùng contract v1, nhưng `request_order_change` dù có tên trong schema vẫn disabled ở runtime MVP. Tool allowlist MVP: search_knowledge, get_order_status, get_product_availability, create_support_ticket. Ticket write cần xác nhận thích hợp và idempotency; không có refund executor. Hành động rủi ro V1: preview + customer confirm + staff approval gắn argument hash/expiry + reauthorize/freshness + execute/reconcile. Args đổi phải xin lại.

Context builder bắt đầu budget thử: system/playbook tối giản 1.000 token, history/summary 1.500, wiki 3.500, customer memory 800, tools 1.000, phần còn lại cho request/answer trong model limit. Đây là tuning proposal, phải đếm bằng tokenizer của model; không coi mọi lượt đều dùng đúng budget. Top-k khởi đầu 5, link expansion 1 hop và tối đa 3 trang, tối đa 3 tool calls/2 draft attempts/1 approved fallback. Vượt budget → clarify/handoff, không vòng retry tự tăng.

Không nạp toàn bộ vault hoặc toàn lịch sử vào mọi lượt. Cache source chunks theo tenant/ACL/release; private cache thêm customer/deletion generation. Exact FAQ/template không gọi model chỉ khi scope/intent/biến đã được code xác minh; không tái dùng câu trả lời cá nhân cho khách khác. Lưu usage thật, cache hit, latency và cost estimates/actual, không để model tự báo thành tích.

Prompt/runtime/model/KB/policy version đều ghi trong run. Quan sát reason codes, bằng chứng và action results, không cần chain-of-thought. Model lựa chọn bằng bakeoff trên cùng tập tiếng Việt/structured output/grounding/latency/cost và điều kiện xử lý dữ liệu; chỉ chọn provider được owner cho phép nhận dữ liệu.

<a id="channels"></a>
## 7. Kênh: kiểm rủi ro Zalo trước, không bỏ WhatsApp

### Zalo cá nhân — spike trước adapter

Ứng viên `zca-js` mô tả API unofficial, login QR/listener/send và cảnh báo nguy cơ khóa; README cũng nêu giới hạn một web listener/account [E3]. Đó là bằng chứng về thư viện, không phải kết quả test account người dùng, không phải backend đã được xác định từ clip.

SB-27 chạy sớm sau contracts; trước live test cần owner cấp tài khoản/quyền và hiểu rủi ro. Không tự đăng nhập account chính. Chốt capability matrix: source/version/integrity, login/revoke/restart, IDs/duplicate/order, `isSelf`, nhận tin từ mobile/PC/Web, session collision, gap/recovery, send acceptance/status và unknown outcomes. Mỗi capability là supported/unsupported/unverified có evidence. Không suy `isSelf` phân biệt được bot và người; cần correlate outbox IDs.

Bridge chạy thường trực. Một lease/fencing epoch/account; stale instance không ingest/send, standby không tự login. Owner tự quét QR trong trang admin có auth, TTL/no-store; session secret không về browser/LLM/log/Git. Không dùng CAPTCHA bypass hay cố reconnect tranh phiên với người.

Lọc thread 1:1 allowlist trước persist/spool/LLM; nhóm, gia đình/bạn bè chưa enroll bị loại, chỉ aggregate counter không nội dung. Encrypted bounded spool bảo vệ từ khi đã ghi bền; offline/crash trước ghi vẫn có thể mất tin. Internal ingest xác thực mTLS hoặc HMAC raw bytes + timestamp/nonce/binding/generation/epoch. Đây là chữ ký bridge, không giả chữ ký provider Zalo.

Internal ACK chỉ sau DB commit; retry nonce mới cùng causal key; spool xóa sau ACK. Gap hoặc spool-full → degraded, pause auto, yêu cầu đối soát; reconnect không tự xóa gap hoặc bật bot. Import lịch sử là đường no-reply riêng. Không áp cửa sổ/biểu phí OA 48h/7d hoặc hứa personal gửi không giới hạn.

Self echo match chắc outbox → status only. Self event khác hoặc ambiguous → human takeover/pause bảo thủ. Chưa chứng minh mobile/PC/Web self visibility thì không bật auto khi người dùng trả lời ngoài console. Không hứa thu hồi tin đã dispatch. Khi connector không đạt, giữ **manual copilot** để dùng được bộ não; ghi rõ không đồng bộ tự động. Bridge-copilot vẫn có rủi ro unofficial như auto bridge.

### WhatsApp — track độc lập

Giữ Cloud API như assumption chờ xác nhận; không tự chuyển WhatsApp cá nhân thành business hoặc dùng WhatsApp Web session. Cần account/WABA/number/app/scopes/version thật khi tích hợp. GET challenge và POST signature là hai việc riêng; kiểm POST trên raw body và bind account server-side, xử lý toàn bộ batch/status, không chỉ phần tử đầu.

Tài liệu policy chính thức mô tả phản hồi tự do trong 24h sau tin người dùng, approved template ngoài khung và tuyến chuyển người; kiểm consent/opt-out/mục đích theo quy định đang áp dụng [E4]. Không suy cửa sổ gửi đồng nghĩa miễn phí. Rate card, template status, eligibility AI use case và điều khoản account phải được kiểm lại trước production, phần chưa đọc đủ ghi unverified.

Policy evaluator trả allow/draft/handoff/deny + reason/version/expiry/cost known-or-unknown. Sender kiểm lại ngay trước gửi, kể cả tin nhân viên. Provider 429 theo Retry-After/backoff/circuit breaker; validation/auth/policy errors không retry mù; unknown timeout sau send phải reconcile thay vì gửi lại.

<a id="reliability"></a>
## 8. Reliability, takeover và bảo mật

WhatsApp durable receipt trước ACK provider; personal durable local spool/internal DB ACK theo giới hạn trên. Inbox dedup theo binding+message/event discriminator; status key khác message key để không mất delivered/read. Dispatcher/sweeper sửa khoảng DB→queue; worker idempotent, conversation version/lease, không dựa riêng Redis lock.

Transaction ghi decision + outbox intent + ownership/KB/ACL/deletion epochs. Sender và bridge recheck version, mode, consent, binding health, budget, freshness và source revocation ngay trước dispatch. Takeover dùng cùng arbitration protocol, tăng ownership_version, cancel intents chưa dispatch. Không giữ DB transaction suốt lúc gọi LLM. Một command đã tới provider trước takeover có thể không hủy được.

Outbox: pending → dispatching → accepted → delivered/read khi có provider evidence; hoặc blocked/failed/unknown. Timeout sau có thể accepted → unknown, không reset pending; downstream idempotency có thì dùng đúng contract, không có thì reconcile/human review. Không hứa exactly-once end-to-end. Delivery/status đến trễ không lùi trạng thái, callback echo không tạo vòng bot.

Conversation: bot_active → handoff_pending → human_active → resolved; explicit operator resume mới bot_active. Handoff_pending cũng dừng trả nghiệp vụ, chỉ một thông báo chuyển khi được phép. Nhân viên và AI dùng cùng policy send. Ngoài giờ giữ ticket/thông tin liên hệ phù hợp, không giả đang có người trực.

Mọi runtime table tenant_id NOT NULL, composite FK cùng tenant, customer ownership cho message/fact/tool. Runtime role không owner/superuser/BYPASSRLS; RLS là lớp bổ sung [E6]. Migration credential tách process. Auth membership/RBAC và request scoping là bắt buộc kể cả service role. Không xuất cả vault hoặc graph có tài liệu không được phép để rồi mong filter ở UI.

Untrusted documents/messages không thành instructions; network allowlist/SSRF protection, sandbox extractor, file size/MIME/malware limits. Encrypted secrets/PII, log redaction, private object URLs ngắn hạn. Prompt/trace không raw transcript/token. Delete/request privacy phải phủ vector, graph titles, cache, exports, queue và bridge spool. Không auto fine-tune từ chat.

<a id="contracts"></a>
## 9. Hợp đồng và ranh giới triển khai

Giữ normalized-event v2 với `zalo_personal`/`personal_bridge`, `whatsapp`/`provider_webhook`, `mock`/`mock`; agent-decision v1 là proposal, không authorization. Event v1 lịch sử không nhận personal. Channel health/gap ở control plane riêng, không giả customer event. SB-03 sinh TS/OpenAPI từ một nguồn schema, không duy trì hai bộ lệch nhau.

DB core: tenant/membership/binding; session/lease/allowlist/gap; customer/identity/consent; conversation/message/inbox/outbox; run/tool/ticket/audit; source registry/raw versions; wiki page/revision/link/claim support/patch/release/chunks; facts/candidates/summary; deletion/tombstone; cost ledger. Chỉ tạo bảng theo vertical slice trước, không dựng toàn SaaS schema rồi mới demo. Các bảng còn lại thêm migration từng task, có empty/upgrade/rollback tests.

Operator API auth+RBAC+tenant, cursor pagination, ETag/If-Match cho cập nhật, Idempotency-Key cho side effect (same key different args = 409). Nhóm API: conversations/messages/takeover/resume/replies; knowledge/imports/patches/reviews/releases/search-preview/revoke; customers/memory-corrections/deletion; channels/login-sessions/health/allowlist/disconnect; tickets; metrics. Private bridge events/heartbeat/commands dùng service auth và fencing; không public send endpoint tùy ý. API trả 404-not-visible cho tài nguyên tenant khác, không lộ tồn tại.

`/v1/knowledge/releases` nhận base_release_id và candidate digest, reviewer decision trong DB; `/publish` không tin `status` trong YAML. Store run/source/claim evidence theo release. Historical imports và operator paste không giả webhook provider. Một thao tác copy thủ công chỉ là `copied`/`operator_marked_sent`, không provider-delivered.

<a id="delivery"></a>
## 10. Lộ trình tối ưu cho xác suất hoàn thành

**M0 — Đóng những rủi ro lớn:** SB-01 scope/business inputs; SB-02 scaffold tối thiểu; SB-03 contracts; SB-27 personal feasibility; SB-21 fixtures/bakeoff model. Mock trước khi có credentials. Kết quả M0 là quyết định rõ có thể/không thể/chưa biết, không chứng nhận production.

**M1 — Một luồng hoàn chỉnh dùng dữ liệu giả:** một source policy → wiki patch → lint/review/publish → câu hỏi → câu trả lời có nguồn → outbox mock → nhân viên takeover → bot dừng. Có UI tối thiểu để kiểm nguồn, không xây dashboard cầu kỳ trước luồng này. SB-33 là bài nghiệm thu xuyên suốt, không chỉ demo một hàm RAG.

**M2 — Copilot dùng được:** sửa nguồn, kiểm version mới, nhớ/sửa/xóa preference, order mock đã xác minh, ticket, inbox/handoff, giới hạn token/cost và audit. Nhân viên duyệt câu trả lời. Manual-copilot không cần session Zalo và được báo đúng hạn chế.

**M3 — Mỗi kênh một gate:** Zalo controlled account integration sau SB-27; WhatsApp sandbox/live-test track riêng. Credentials một kênh thiếu không chặn xây hoặc nghiệm thu kênh còn lại, nhưng không được báo hoàn tất cả hai. Không official Zalo sandbox giả định cho account cá nhân.

**M4 — Auto low-risk có điều kiện:** có quality/security/UAT/rollback/owner approvals rồi mới canary một kênh, allowlisted intents và cohort nhỏ. Tăng 5% →25%→100% các lượt đủ điều kiện chỉ sau review dữ liệu đủ mẫu, không theo đồng hồ hay vì hết sprint. Theo dõi complaints/reopen/false confidence và support capacity, không chỉ containment.

**M5 — V1 tùy chọn:** write approvals, verified cross-channel linking, feedback→KB proposals, owner brief; voice/OCR/graph UI/fine-tune chỉ có case riêng chứng minh cần. Không bắt các mục này thành dependency MVP.

Tám vai trò, ban đầu tối đa ba luồng coder: Platform/integration; Memory; Channels/Console tùy dependency. Lead quản backlog và reviewer/QA độc lập. Không tự mở thêm agent/lịch. WIP nhỏ, PR tập trung; interface/fixture trước code phụ thuộc. Sau M1 mới ước lượng lại số ngày theo throughput thực; các task size S/M/L là độ lớn tương đối, không cam kết lịch giả.

<a id="acceptance"></a>
## 11. Nghiệm thu: kết quả thật, không checkmark cảm tính

`planning/release-gates.json` tách gate common, manual-copilot, zalo-copilot, zalo-auto, whatsapp-copilot, whatsapp-auto. Mỗi evidence ghi commit/config/model/prompt/KB/policy version, command, môi trường, số mẫu, người review, pass/fail/skipped. `not_run` hoặc unknown không là passed. Plan validator chỉ chứng minh tài sản kế hoạch nhất quán.

Hard gates: zero leak/cross-tenant/customer/unauthorized tool action trong security suite; zero unsafe publish, deletion resurrection hoặc send-after-takeover trong deterministic tests. Bất kỳ P0 thật nào chặn release, dù điểm trung bình tốt. Source refs tồn tại/còn hiệu lực và wiki link correctness 100% trên published candidate; semantic grounding cần eval/người review, không suy từ lint.

Mục tiêu pilot đề xuất: ≥200 labeled cases (core corpus tách held-out test), ≥50 câu review độc lập, grounded correctness ≥90%, unsupported factual claim ≤2%, Recall@5 ≥90%. Required handoff ≥95%, riêng trực tiếp xin gặp người và takeover deterministic 100%. Đo false abstention và sai trên từng intent/channel/risk, không gộp để che nhóm yếu. Không coi LLM judge là oracle duy nhất.

Reliability tests: duplicate 100 lần không thêm logical reply/ticket; crash sau DB commit trước enqueue; worker restart sau effect; provider accept rồi timeout; delivered đến trước status cũ; source revoke khi đang soạn; opt-out khi queued; delete rồi replay/spool/restore; hai curator sửa cùng base; publish index lỗi; self-event ambiguous; two bridge epochs; private graph neighbor. Không test flood tài khoản Zalo thật; load test chỉ mock/staging được phép.

Load target ban đầu với mock: 10 inbound/s trong 10 phút, 50 conversations đang xử lý; ACK p95 ≤1s sau durable write, response p95 ≤10s với dependencies khỏe. Với personal phải đo riêng listener→spool→ingest; không có provider ACK tương đương. Provider latency/quota báo riêng, không claim SLA chưa đo. Định nghĩa cost/groundedness/recall/sample counts trong báo cáo, không chỉ screenshot.

Ablation nhỏ trên cùng corpus: raw retrieval vs wiki retrieval vs wiki+hybrid+one-hop. Chỉ giữ reranker/link expansion nếu tăng chất lượng có ý nghĩa với chi phí/latency chấp nhận; không mặc định graph đẹp là tốt hơn. Test chất lượng trên cả policy version mới/cũ và câu ngoài scope.

<a id="operations"></a>
## 12. Vận hành, chi phí và fallback

Local: no secrets, mocks, synthetic vault. Staging: DB/bucket/keys riêng, người nhận đồng ý. Production: secrets manager, separate migrations, TLS, least privilege, on-call/support owner. Không tự provision dịch vụ trả phí từ plan. Bridge listener không chạy trong short-lived function; một replica active/account và explicit failover.

Chi phí = hạ tầng + model input/output + embeddings/rebuild/rerank + channel messages theo rate card + storage/egress/logs + phí/tax áp dụng. Chưa có đơn giá thì unknown, không 0. Budget reservation atomic trước call/send; reconcile actual và unknown outcomes. Soft cap 80%/hard cap theo owner; vượt cap dừng auto, giữ draft/handoff; không dùng model rẻ chưa được duyệt nhận dữ liệu.

Dashboard lấy số thật: inbound/outbound by status, resolved/reopened, handoff age, rejected source, retrieval miss, model tokens/cost, queue lag, bridge heartbeat/gap, unknown sends, failed purge và KB releases. Owner brief SB-32 tóm tắt ledger + open tasks + incidents với refs, không tự tạo việc thành công. Ban đầu nút Generate report; lịch chỉ tạo khi chủ dự án yêu cầu riêng.

Kill switch global/tenant/channel/action ở sender, tiếp tục durable ingress hợp lệ nếu an toàn. Session revoked/restricted/gap/self-visibility thiếu → personal auto OFF, không loop né hạn chế. KB lỗi → revoke source/release, invalidate câu đang soạn, dùng bản còn hợp lệ hoặc handoff. Provider unknown → reconcile, không retry mù. Leak/sai action → OFF phạm vi ảnh hưởng, giữ audit tối thiểu, incident owner xử lý.

Restore: DB + objects + key recovery + deletion suppression trong môi trường cô lập, senders OFF. Mục tiêu pilot đề xuất RPO24h/RTO4h cần drill đo thật. App rollback phải tương thích schema (expand/contract migrations), không reverse phá dữ liệu. KB rollback vẫn kiểm ACL/consent/tombstones hiện hành. Chỉ reconnect sau kiểm tra và explicit owner action.

<a id="inputs"></a>
## 13. Đầu vào owner và quyết định không chặn code

Cần owner chốt trước live: ngành hàng + top use cases; 10–20 tài liệu/FAQ có owner/ngày hiệu lực; CRM/order source và quyền read; nhân viên/hours/SLA; privacy/retention/data processing; model/provider+budget; account test/production và consent recipients; loại account WhatsApp; Zalo risk/terms/capability acceptance. Credentials nhập qua secret manager, không chat/Git.

Không có input thì dùng fixture và ghi blocked tại đúng gate. Code/plan completion khác account integration completion khác production acceptance. Full audio review của clip còn chưa hoàn tất; không làm dependency runtime vì tất cả quyết định triển khai đã được ghi là proposal hoặc visual evidence. Không tự đánh SB-00 fully verified.

<a id="first-run"></a>
## 14. Phiên làm việc đầu tiên cho Lead

Đọc README/AGENTS và plan này; chạy plan validator; mở backlog, giữ tất cả implementation tasks TODO khi chưa có code. Claim SB-01, giao SB-02; QA chuẩn bị fixtures. Sau contracts SB-03, chạy spike SB-27 độc lập và mở auth/DB/wiki-format theo DAG. Mục tiêu kế tiếp là **SB-33 mock end-to-end**, không phải login account thật cho kịp demo.

Mỗi PR ghi acceptance trước code, command/result thật, source/requirement refs, blocked input và rollback. Không báo phần trăm hoàn thiện thiếu mẫu số. Tổng kết theo ba cột: đã chứng minh, chưa chứng minh, quyết định cần owner. Không tự merge, tạo lịch hay deploy.
