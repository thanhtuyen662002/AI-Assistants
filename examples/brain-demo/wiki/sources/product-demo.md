---
schema_version: '1.0'
id: kb-demo-sources-product-demo
tenant_id: tenant-demo
kind: source
title: Nguồn sản phẩm mẫu
revision: 1
status: draft
audience: support
owner: synthetic-reviewer
source_refs:
- src-demo-product-v1
links:
- wiki/entities/product-demo
claims:
- id: claim-1
  statement: DEMO-01 là mã sản phẩm dùng để kiểm thử, không phải hàng đang bán.
  source_id: src-demo-product-v1
  quote: DEMO-01 là mã sản phẩm dùng để kiểm thử, không phải hàng đang bán.
  locator: text:exact-quote
  nature: fact
---
# Nguồn sản phẩm mẫu

DỮ LIỆU TỔNG HỢP, CHƯA PUBLISHED.

DEMO-01 là mã sản phẩm dùng để kiểm thử, không phải hàng đang bán.

[[wiki/entities/product-demo]]
