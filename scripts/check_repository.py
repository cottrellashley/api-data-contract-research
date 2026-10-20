#!/usr/bin/env python3
"""Check local documentation links, JSON syntax, and illustrative artifact bindings.

External links are inventoried, not fetched. Historical broken vendor URLs are
intentionally preserved as provenance. This script is not a JSON Schema engine.
"""

import argparse
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\[[^\]]*\]\(([^\s)]+)(?:\s+\"[^\"]*\")?\)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-source-index", action="store_true")
    args = parser.parse_args()
    errors, links = [], {}
    markdown = sorted(ROOT.rglob("*.md"))
    local_count = 0
    for path in markdown:
        # Code fences contain illustrative links/paths, not repository navigation.
        body = re.sub(r"```.*?```", "", path.read_text(), flags=re.S)
        for match in LINK.finditer(body):
            target = match.group(1).strip("<>")
            if target.startswith(("https://", "http://")):
                links.setdefault(target, set()).add(str(path.relative_to(ROOT)))
                continue
            if target.startswith(("#", "mailto:")):
                continue
            local_count += 1
            file_part = unquote(urlsplit(target).path)
            destination = (path.parent / file_part).resolve()
            if not destination.is_relative_to(ROOT):
                errors.append(f"{path.relative_to(ROOT)}: link escapes repository: {target}")
            elif not destination.exists():
                errors.append(f"{path.relative_to(ROOT)}: missing link target: {target}")
    json_paths = sorted(ROOT.rglob("*.json"))
    for path in json_paths:
        try:
            json.loads(path.read_text())
        except (ValueError, UnicodeError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
    try:
        contract = json.loads((ROOT / "examples/orders-contract-v1.json").read_text())
        bundle = json.loads((ROOT / "examples/release-bundle.json").read_text())
        props = set(contract["schema"]["properties"])
        if not set(contract["schema"]["required"]) <= props:
            errors.append("contract requires an undefined field")
        if not set(contract["quality"]["unique_key"]) <= props:
            errors.append("contract unique key references an undefined field")
        if bundle["public_data_contract"] != contract["contract_id"]:
            errors.append("bundle and public contract identifiers differ")
        if not (ROOT / "examples" / bundle["contract_file"]).is_file():
            errors.append("bundle contract file is missing")
        sys.path.insert(0, str(ROOT / "examples"))
        from contract_lab import MAPPING_REVISION, PUBLIC_CONTRACT
        if bundle["mapping_revision"] != MAPPING_REVISION or PUBLIC_CONTRACT != contract["contract_id"]:
            errors.append("lab constants do not match artifact bindings")
    except (KeyError, ValueError, OSError, ImportError) as exc:
        errors.append(f"artifact consistency check failed: {exc}")
    index = {"research_date": "2026-10-20", "scope": "HTTP(S) citations; historical URLs retained; reachability not tested by this script", "sources": [{"url": url, "referenced_by": sorted(files)} for url, files in sorted(links.items())]}
    index_path = ROOT / "sources/external-links.json"
    if args.write_source_index:
        index_path.write_text(json.dumps(index, indent=2) + "\n")
    elif index_path.exists():
        if json.loads(index_path.read_text()) != index:
            errors.append("external-link index is stale; run --write-source-index")
    else:
        errors.append("external-link index missing; run --write-source-index")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"PASS: {len(markdown)} Markdown files, {local_count} local links, {len(json_paths)} JSON files, {len(links)} unique external citations; artifact bindings consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
