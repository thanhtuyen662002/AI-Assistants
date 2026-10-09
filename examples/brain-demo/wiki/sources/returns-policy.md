---
schema_version: '1.0'
id: kb-demo-sources-returns-policy
tenant_id: tenant-demo
kind: source
title: Nguồn chính sách đổi trả mẫu
revision: 1
status: draft
audience: support
owner: synthetic-reviewer
source_refs:
- src-demo-returns-v1
links:
- wiki/concepts/returns
claims:
- id: claim-1
  statement: Khách có thể gửi yêu cầu đổi trả trong 14 ngày từ khi nhận hàng.
  source_id: src-demo-returns-v1
  quote: Khách có thể gửi yêu cầu đổi trả trong 14 ngày từ khi nhận hàng.
  locator: text:exact-quote
  nature: fact
---
# Nguồn chính sách đổi trả mẫu

DỮ LIỆU TỔNG HỢP, CHƯA PUBLISHED.

Khách có thể gửi yêu cầu đổi trả trong 14 ngày từ khi nhận hàng.

[[wiki/concepts/returns]]
