# Validation report — unified planning kit v3

Date: 2026-10-09. Scope: **planning assets only**. No CSKH application, production database, model evaluation, live account, send or deployment is claimed to have run.

## Commands actually executed

```text
python /mnt/data/plan_v3/scripts/validate_plan.py --self-test
python -m py_compile /mnt/data/plan_v3/scripts/validate_plan.py
```

The local directory is a test copy of the planning kit, not a clone of the full repository. Dependencies present and checked: jsonschema 4.26.0, PyYAML 6.0.3. Equivalent clean-checkout usage after installing requirements-plan.txt:

```bash
python scripts/validate_plan.py --self-test
```

Actual validator output:

```json
{
  "status": "pass",
  "scope": "planning_assets_only",
  "tasks": 34,
  "gate_profiles": 6,
  "wiki_schemas": 1,
  "raw_sources": 2,
  "wiki_pages": 9,
  "links": 18,
  "claims_with_located_quotes": 6,
  "scenario_specs": 20,
  "negative_mutations_rejected": 10
}
```

The validator rejects ten deliberately corrupted copies: cyclic task dependencies, unknown dependency, cross-channel readiness dependency, raw-source tampering, dangling wiki link, unknown source, cross-tenant reference, support page exposing internal source, forged YAML published status, and a quote absent from its raw source.

This checks quoted text exists in the synthetic source; **it does not prove every claim's semantic meaning is correct**. Numeric/negation correctness and actual model grounding remain SB-31/evaluation/reviewer work. Twenty WK JSONL entries are scenario specifications, not twenty application tests that passed. Existing GC fixtures remain separate and were not executed by this command.

## Byte identity checked before publication

A separate local hash comparison computed Git blob SHA-1 from the exact bytes of 19 tested files and compared them with the blob SHAs returned by GitHub for prospective tree `330517eea7062b0e531260d2b6bc8f494e6b5f6d` and its subtrees. All 19 matched. This report is added afterward without changing those files.

```text
0708be5d2555c126cec4530399adf05293dbcd89  contracts/current.json
da0882666d5d200b9ade4dbc3af374a163f405f2  contracts/wiki-page.v1.schema.json
38acb734930dbe7e90fef671f4660b26cd703128  evals/wiki-acceptance.jsonl
68c6ee495b1597bbac6cd3acaae041752743c553  examples/brain-demo/raw/product-demo.md
52a317723ab70a3615dcd8cc8b71538f21582d4b  examples/brain-demo/raw/returns-policy.md
00d79f47533a56f57855b76905e7f01a545972cd  examples/brain-demo/sources.json
10ffdf7dcfddc738a735bba961d8cee14273badf  examples/brain-demo/wiki/analysis/support-map.md
218fe96f23a3e933f367b669be469d7127d7ae05  examples/brain-demo/wiki/concepts/returns.md
21fc745b9a327c2a97316ac241f2be1502b919f4  examples/brain-demo/wiki/entities/product-demo.md
d8ff578930d0061f6956620469b3d98c31f7c3f6  examples/brain-demo/wiki/index.md
f057690e00953c89f14b488028dc4853bd7126d1  examples/brain-demo/wiki/log.md
ca5d5152cb34eb5888bf1544c3606f38db741965  examples/brain-demo/wiki/overview.md
f3b1272556aadea100443f99ec2d7cf087c146c2  examples/brain-demo/wiki/playbooks/return-request.md
1220f61a739889dd6da13c79a96670b8ac69e871  examples/brain-demo/wiki/sources/product-demo.md
f9e46650dbf43c7b26f419d7d8aff765f605a323  examples/brain-demo/wiki/sources/returns-policy.md
cb2c3215aec56cf40d7fcda51b36bfa7b8749c16  planning/backlog.json
4e7f1c75a12315def5a5d402a5c1b77d2ee6ecfd  planning/release-gates.json
083ac9bf8d74939d8286549caaebf0626e7d51ec  requirements-plan.txt
c7bff181ff55f0920edeb1e289692b83bbdb2b4e  scripts/validate_plan.py
```

## Not verified / not activated

Full audio of the uploaded videos is not transcribed/verified; visual observations and uncertainty are logged in docs/00. The application has not been scaffolded, built or integration-tested. No actual database RLS/ACL/publish race, model answer quality, bridge account risk/capability, WhatsApp eligibility/rate card, customer handoff delivery or production recovery test is claimed passed.

No agents, background schedules, GitHub Actions scheduled workflows, account logins, customer sends, paid infrastructure or production deployment were started. All release profile statuses remain not_run. SB-00 is partial visual review; implementation tasks remain todo.

`planning/validation-report.md` and `planning/personal-revision-validation.md` are historical reports for earlier commits. They do not establish current application readiness or override v3 contracts.
