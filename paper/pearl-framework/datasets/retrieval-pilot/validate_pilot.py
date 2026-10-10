"""Check pilot annotation structure and its source-PDF locators.

This validates traceability, not the semantic sufficiency of an answer.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

import pymupdf


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
CORPUS_MANIFEST = HERE.parent / "retrieval-corpus" / "corpus-manifest.jsonl"
PILOT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "pilot-intents.json"


def normalized(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).replace("\u00ad", "")
    return re.sub(r"\s+", " ", value).casefold().strip()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> None:
    pilot = json.loads(PILOT.read_text(encoding="utf-8"))
    corpus = [json.loads(line) for line in CORPUS_MANIFEST.read_text(encoding="utf-8").splitlines()]
    by_source = {row["source_id"]: row for row in corpus}
    require(len(by_source) == len(corpus), "duplicate source ID in corpus manifest")
    require(pilot["corpus_manifest_sha256"] == digest(CORPUS_MANIFEST), "pilot corpus hash mismatch")
    require(all(row["corpus_version"] == pilot["corpus_version"] for row in corpus), "corpus version mismatch")
    expected_frozen = pilot["status"] == "agent_reviewed_preliminary"
    require(pilot["status"] in {"agent_draft_unreviewed", "agent_revision_pending_recheck", "agent_reviewed_preliminary"}
            and pilot["gold_frozen"] is expected_frozen, "pilot status mismatch")
    require(len(pilot["intents"]) == 8, "expected eight pilot intents")
    require(len({item["intent_id"] for item in pilot["intents"]}) == 8, "duplicate intent ID")
    require(len({item["family_id"] for item in pilot["intents"]}) == 8, "duplicate family ID")
    expected_strata = {"single_source", "numeric_table", "within_paper_multi", "cross_paper"}
    require(Counter(item["main_stratum"] for item in pilot["intents"]) == Counter({kind: 2 for kind in expected_strata}),
            "pilot stratum balance mismatch")

    opened = {}
    checked_atoms = 0
    try:
        for item in pilot["intents"]:
            prefix = item["intent_id"]
            require(item["split"] == "dev_candidate", f"{prefix}: wrong split")
            require(item["query"] and item["reference_answer"], f"{prefix}: empty query or answer")
            atoms = {atom["atom_id"]: atom for atom in item["atoms"]}
            requirements = {req["requirement_id"]: req for req in item["requirements"]}
            require(len(atoms) == len(item["atoms"]) and bool(atoms), f"{prefix}: atom identity")
            require(len(requirements) == len(item["requirements"]) and bool(requirements), f"{prefix}: requirement identity")
            require(bool(item["evidence_groups"]), f"{prefix}: no complete group")
            for atom in item["atoms"]:
                source = by_source.get(atom["source_id"])
                require(source is not None, f"{prefix}: unknown source {atom['source_id']}")
                if atom["source_id"] not in opened:
                    path = REPO / source["source_path"]
                    require(path.is_file() and digest(path) == source["sha256"], f"{prefix}: source file/hash mismatch")
                    opened[atom["source_id"]] = pymupdf.open(path)
                document = opened[atom["source_id"]]
                require(1 <= atom["page"] <= len(document), f"{prefix}: invalid page")
                page_text = normalized(document[atom["page"] - 1].get_text("text"))
                if atom["locator_type"] == "text_anchor":
                    require(normalized(atom["anchor_text"]) in page_text,
                            f"{prefix}: anchor missing on PDF page {atom['page']}: {atom['anchor_text']}")
                elif atom["locator_type"] == "table_cell":
                    for field in ("table", "row", "column", "value"):
                        require(normalized(atom[field]) in page_text,
                                f"{prefix}: table {field} missing on PDF page {atom['page']}")
                else:
                    raise ValueError(f"{prefix}: unknown locator type")
                require(atom["supports"], f"{prefix}: atom has no interpretation")
                checked_atoms += 1
            for req in item["requirements"]:
                require(req["claim"] and req["scope"], f"{prefix}: missing claim/scope")
                bundles = req["support_bundles"]
                require(bool(bundles) and all(bundle for bundle in bundles), f"{prefix}: empty support bundle")
                require(all(len(bundle) == len(set(bundle)) and set(bundle) <= atoms.keys() for bundle in bundles),
                        f"{prefix}: invalid support bundle atom")
            for group in item["evidence_groups"]:
                ids = group["requirements"]
                require(bool(ids) and len(ids) == len(set(ids)) and set(ids) <= requirements.keys(),
                        f"{prefix}: invalid complete group")
                if item["main_stratum"] == "cross_paper":
                    for chosen_bundles in itertools.product(*(requirements[req_id]["support_bundles"] for req_id in ids)):
                        sources = {atoms[atom_id]["source_id"] for bundle in chosen_bundles for atom_id in bundle}
                        require(len(sources) >= 2, f"{prefix}: one complete cross-paper path has fewer than two sources")
            require(set().union(*(set(g["requirements"]) for g in item["evidence_groups"])) == requirements.keys(),
                    f"{prefix}: unused requirement")
            require({atom_id for req in item["requirements"] for bundle in req["support_bundles"]
                     for atom_id in bundle} == atoms.keys(), f"{prefix}: unused source atom")
    finally:
        for document in opened.values():
            document.close()

    print(json.dumps({"intents": len(pilot["intents"]), "source_pdfs": len(opened),
                      "source_atoms_verified": checked_atoms, "status": pilot["status"]}, sort_keys=True))


if __name__ == "__main__":
    main()
