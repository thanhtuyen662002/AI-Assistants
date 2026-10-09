#!/usr/bin/env python3
"""Validate planning assets, not the CSKH application or provider integration.

No network calls or credentials. Requires requirements-plan.txt.
Run: python scripts/validate_plan.py --self-test
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError


class ValidationError(Exception):
    """A deterministic planning-asset validation failure."""


class UniqueLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ValidationError(f"Duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValidationError(message)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_page(path: Path):
    raw = path.read_text(encoding="utf-8")
    require(len(raw.encode()) <= 1_000_000, f"Page too large: {path}")
    require(raw.startswith("---\n"), f"Missing YAML frontmatter: {path}")
    parts = raw.split("---\n", 2)
    require(len(parts) == 3, f"Unterminated YAML frontmatter: {path}")
    meta = yaml.load(parts[1], Loader=UniqueLoader)
    require(isinstance(meta, dict), f"Metadata must be object: {path}")
    return meta, parts[2]


def safe_path(base: Path, relative: str) -> Path:
    path = (base / relative).resolve()
    require(path.is_relative_to(base.resolve()), f"Path escapes workspace: {relative}")
    return path


def validate_assets(root: Path) -> dict[str, int]:
    backlog = load_json(root / "planning/backlog.json")
    rows = backlog["tasks"]
    tasks = {row["id"]: row for row in rows}
    require(len(tasks) == len(rows), "Duplicate task IDs")
    states = {"todo", "partial", "in_progress", "blocked", "ready_for_review", "done"}
    for tid, row in tasks.items():
        require(bool(re.fullmatch(r"SB-\d{2}", tid)), f"Invalid task ID: {tid}")
        require(row["status"] in states, f"Invalid state: {tid}")
        require(bool(row["deliverable"]) and bool(row["acceptance"]), f"Missing task evidence contract: {tid}")
        require(all(d in tasks for d in row["depends_on"]), f"Unknown dependency: {tid}")
    visiting, visited = set(), set()

    def visit(tid):
        require(tid not in visiting, f"Dependency cycle: {tid}")
        if tid in visited:
            return
        visiting.add(tid)
        for dep in tasks[tid]["depends_on"]:
            visit(dep)
        visiting.remove(tid)
        visited.add(tid)

    for tid in tasks:
        visit(tid)

    def closure(ids):
        seen = set()
        def add(tid):
            require(tid in tasks, f"Gate references unknown task: {tid}")
            if tid not in seen:
                seen.add(tid)
                for dep in tasks[tid]["depends_on"]:
                    add(dep)
        for tid in ids:
            add(tid)
        return seen

    profiles = load_json(root / "planning/release-gates.json")["profiles"]
    require(len({p["id"] for p in profiles}) == len(profiles), "Duplicate gate profile")
    optional = {tid for tid, task in tasks.items() if task["phase"] == "optional"}
    for p in profiles:
        needed = closure(p["required_tasks"])
        require(bool(p["checks"]) and len(set(p["checks"])) == len(p["checks"]), f"Missing/duplicate checks: {p['id']}")
        require(not needed & optional, f"Optional task blocks MVP: {p['id']}")
        if p["id"].startswith("whatsapp_"):
            require(not needed & {"SB-07", "SB-27"}, "WhatsApp gated on Zalo")
        if p["id"].startswith("zalo_"):
            require("SB-08" not in needed, "Zalo gated on WhatsApp")
        if p["id"] in {"mock_slice", "manual_copilot"}:
            require(not needed & {"SB-07", "SB-08", "SB-27"}, "Core gated on live accounts")

    schema = load_json(root / "contracts/wiki-page.v1.schema.json")
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    vault = root / "examples/brain-demo"
    source_rows = load_json(vault / "sources.json")["sources"]
    sources = {s["id"]: s for s in source_rows}
    require(len(sources) == len(source_rows), "Duplicate source IDs")
    source_text = {}
    for sid, source in sources.items():
        p = safe_path(vault, source["path"])
        require(p.is_file(), f"Missing raw source: {sid}")
        raw = p.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == source["sha256"], f"Raw digest mismatch: {sid}")
        source_text[sid] = raw.decode("utf-8")
    pages = {}
    page_ids = set()
    for p in sorted((vault / "wiki").rglob("*.md")):
        meta, body = read_page(p)
        errors = sorted(validator.iter_errors(meta), key=lambda e: str(list(e.path)))
        require(not errors, f"Schema error {p.name}: {errors[0].message if errors else ''}")
        require(meta["id"] not in page_ids, f"Duplicate page ID: {meta['id']}")
        page_ids.add(meta["id"])
        key = p.relative_to(vault).with_suffix("").as_posix()
        pages[key] = (meta, body)
    require(bool(pages), "No example wiki pages")
    rank = {"support": 0, "internal": 1}
    links_total = claims_total = 0
    for key, (meta, body) in pages.items():
        links = re.findall(r"\[\[([^\[\]]+)\]\]", body)
        require(set(links) == set(meta["links"]), f"Body/declaration link mismatch: {key}")
        for link in links:
            require(link in pages, f"Dangling or unsupported link: {link}")
            target = pages[link][0]
            require(meta["tenant_id"] == target["tenant_id"], f"Cross-tenant link: {key}")
            require(rank[meta["audience"]] >= rank[target["audience"]], f"Link exposes restricted target: {key}")
            links_total += 1
        for sid in meta["source_refs"]:
            require(sid in sources, f"Unknown source: {sid}")
            source = sources[sid]
            require(source["tenant_id"] == meta["tenant_id"], f"Cross-tenant source: {key}")
            require(rank[meta["audience"]] >= rank[source["audience"]], f"Broader source ACL: {key}")
        require(len({c['id'] for c in meta['claims']}) == len(meta['claims']), f"Duplicate claim IDs: {key}")
        for claim in meta["claims"]:
            sid = claim["source_id"]
            require(sid in meta["source_refs"], f"Claim source not declared: {key}")
            require(claim["quote"] in source_text[sid], f"Quote not found in raw: {key}")
            claims_total += 1
    cases = [json.loads(s) for s in (root / "evals/wiki-acceptance.jsonl").read_text(encoding="utf-8").splitlines() if s.strip()]
    require(len({c["id"] for c in cases}) == len(cases), "Duplicate acceptance IDs")
    require(all(c["setup"] and c["expected"] for c in cases), "Missing scenario assertion")
    return {"tasks": len(tasks), "gate_profiles": len(profiles), "wiki_schemas": 1,
            "raw_sources": len(sources), "wiki_pages": len(pages), "links": links_total,
            "claims_with_located_quotes": claims_total, "scenario_specs": len(cases)}


def self_test(root: Path) -> int:
    def edit_json(base, rel, fn):
        path = base / rel
        data = load_json(path)
        fn(data)
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    def edit_page(base, fn):
        path = base / "examples/brain-demo/wiki/concepts/returns.md"
        meta, body = read_page(path)
        fn(meta)
        path.write_text("---\n" + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False) + "---\n" + body, encoding="utf-8")
    changes = [
        ("cycle", lambda b: edit_json(b, "planning/backlog.json", lambda d: d["tasks"][2]["depends_on"].append("SB-03"))),
        ("unknown_dependency", lambda b: edit_json(b, "planning/backlog.json", lambda d: d["tasks"][2]["depends_on"].append("SB-99"))),
        ("cross_channel_gate", lambda b: edit_json(b, "planning/release-gates.json", lambda d: d["profiles"][4]["required_tasks"].append("SB-07"))),
        ("raw_tamper", lambda b: (b / "examples/brain-demo/raw/returns-policy.md").write_text("tampered", encoding="utf-8")),
        ("dangling_link", lambda b: (b / "examples/brain-demo/wiki/playbooks/return-request.md").unlink()),
        ("unknown_source", lambda b: edit_page(b, lambda m: m["source_refs"].append("unknown-source"))),
        ("cross_tenant", lambda b: edit_page(b, lambda m: m.update(tenant_id="another-tenant"))),
        ("restricted_source", lambda b: edit_json(b, "examples/brain-demo/sources.json", lambda d: d["sources"][0].update(audience="internal"))),
        ("forged_published", lambda b: edit_page(b, lambda m: m.update(status="published"))),
        ("invented_quote", lambda b: edit_page(b, lambda m: m["claims"][0].update(quote="This quote does not exist in the source."))),
    ]
    passed = 0
    for name, change in changes:
        with tempfile.TemporaryDirectory(prefix="plan-test-") as tmp:
            trial = Path(tmp) / "repo"
            trial.mkdir()
            for folder in ("planning", "contracts", "evals", "examples/brain-demo"):
                shutil.copytree(root / folder, trial / folder)
            change(trial)
            try:
                validate_assets(trial)
            except ValidationError:
                passed += 1
            else:
                raise ValidationError(f"Negative self-test failed to reject: {name}")
    return passed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        report = validate_assets(args.root)
        if args.self_test:
            report["negative_mutations_rejected"] = self_test(args.root)
        print(json.dumps({"status": "pass", "scope": "planning_assets_only", **report}, ensure_ascii=False, indent=2))
        print("NOT VERIFIED: semantic model quality, production publish/auth, DB RLS, live channels or deployment.")
        return 0
    except (ValidationError, SchemaError, OSError, KeyError, TypeError, ValueError, yaml.YAMLError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
