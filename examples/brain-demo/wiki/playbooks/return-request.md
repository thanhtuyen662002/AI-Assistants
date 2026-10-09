---
schema_version: '1.0'
id: kb-demo-playbooks-return-request
tenant_id: tenant-demo
kind: playbook
title: Tiếp nhận yêu cầu đổi trả
revision: 1
status: draft
audience: support
owner: synthetic-reviewer
source_refs:
- src-demo-returns-v1
links:
- wiki/sources/returns-policy
claims:
- id: claim-1
  statement: Agent không được tự hoàn tiền.
  source_id: src-demo-returns-v1
  quote: Agent không được tự hoàn tiền.
  locator: text:exact-quote
  nature: fact
---
# Tiếp nhận yêu cầu đổi trả

DỮ LIỆU TỔNG HỢP, CHƯA PUBLISHED.

Agent không được tự hoàn tiền.

[[wiki/sources/returns-policy]]
