"""Version the independently reviewed u021 wording without changing v3 assets."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GOLD = ROOT / "memPed/knowledge/gold/2026-09-23-rebuild"
STEMS = (
    "questions_full_candidate", "evidence_planned_candidate", "unanswerable_questions_candidate",
    "reclassified_answerable_candidate", "reclassified_evidence_candidate",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_bundle(data: Path = GOLD) -> dict[str, list[dict]]:
    previous = json.loads((data / "full_candidate_manifest_v3.json").read_text(encoding="utf-8"))
    result = {}
    for stem in STEMS:
        name = f"{stem}_v3.jsonl"
        if sha(data / name) != previous["output_sha256"][name]:
            raise ValueError(f"v3 changed: {name}")
        records = [json.loads(line) for line in (data / name).read_text(encoding="utf-8").splitlines() if line]
        if stem in {"questions_full_candidate", "unanswerable_questions_candidate"}:
            for record in records:
                if record["intent_id"] == "rgq-u021":
                    record["query"] = {
                        "en": "How many deaths or injuries would the 2010 Love Parade disaster have avoided if both its eastern and western access tunnels had each been 20 percent wider, with other conditions unchanged?",
                        "zh": "若 2010 年 Love Parade 事故的东、西两条入口隧道均加宽 20%，其他条件不变，会避免多少人死亡或受伤？",
                    }[record["language"]]
                    record["absence_rationale"] = "冻结的 104 篇 PDF 未给出两条隧道均加宽 20% 的反事实伤亡预测或从通行能力到伤亡数量的模型。"
                    record["absence_review_status"] = "independent_AI_review_supported_frozen_PDF_corpus_only"
                    record["annotation_status"] = "agent_reviewed_candidate"
                    record["human_verified"] = False
        result[f"{stem}_v4.jsonl"] = records
    return result


def write_bundle(data: Path, bundle: dict[str, list[dict]]) -> Path:
    names = [*bundle, "full_candidate_manifest_v4.json"]
    if any((data / name).exists() for name in names):
        raise FileExistsError("Refusing to overwrite an existing v4 candidate asset")
    hashes = {}
    for name, rows in bundle.items():
        path = data / name
        path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
        hashes[name] = sha(path)
    manifest = {
        "gold_schema_version": "candidate-gold-v4-agent-reviewed", "status": "candidate_not_gold", "formal_gold_ready": False,
        "human_verified": False, "review_scope": "Frozen 104 source PDFs only",
        "selected_answerable_intents": 120, "proposed_dev_intents": 20, "proposed_test_intents": 100,
        "proposed_refusal_intents": 20, "selected_variants": 280, "reserve_reclassified_answerable_intents": 1,
        "u021_review": {
            "reviewer_kind": "independent_AI_assisted", "verdict": "absence_supported_in_frozen_PDF_corpus",
            "note": "Source PDF describes two access tunnels and theoretical flow capacity; it gives no 20-percent-wider counterfactual injury/death estimate. The question now specifies both tunnels. A theoretical throughput change cannot be converted into avoided casualties.",
            "source_resource_id": "lit-10-1140-epjds7", "source_pdf_sha256": "59f25c300daa2ba2973770715cf1cb21111f0ff76f280395f0cf4e1ed663fda6",
            "human_verified": False,
        },
        "pending_review": ["alternative relevant sources", "precise element locators", "corpus governance"],
        "input_sha256": {f"{stem}_v3.jsonl": sha(data / f"{stem}_v3.jsonl") for stem in STEMS},
        "source_manifest_sha256": sha(data / "full_candidate_manifest_v3.json"),
        "output_sha256": hashes,
    }
    path = data / "full_candidate_manifest_v4.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


if __name__ == "__main__":
    print(write_bundle(GOLD, build_bundle()))
