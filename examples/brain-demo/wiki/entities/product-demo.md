---
schema_version: '1.0'
id: kb-demo-entities-product-demo
tenant_id: tenant-demo
kind: entity
title: Sản phẩm DEMO-01
revision: 1
status: draft
audience: support
owner: synthetic-reviewer
source_refs:
- src-demo-product-v1
links:
- wiki/sources/product-demo
claims:
- id: claim-1
  statement: Giá và tồn kho hiện tại phải lấy từ công cụ nghiệp vụ, không từ wiki.
  source_id: src-demo-product-v1
  quote: Giá và tồn kho hiện tại phải lấy từ công cụ nghiệp vụ, không từ wiki.
  locator: text:exact-quote
  nature: fact
---
# Sản phẩm DEMO-01

DỮ LIỆU TỔNG HỢP, CHƯA PUBLISHED.

Giá và tồn kho hiện tại phải lấy từ công cụ nghiệp vụ, không từ wiki.

[[wiki/sources/product-demo]]
