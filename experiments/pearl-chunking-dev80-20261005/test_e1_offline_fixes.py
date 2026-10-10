import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from e1_score import (
    candidate_decision,
    execution_row,
    integration_output_paths,
    select_equivalent_representatives,
    strict_equivalence_signatures,
)
from e1_statistics import load_verified_scoring, require_verified_artifact, select_panel


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf8")


def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_execution_row_requires_all_success_and_exact_coverage():
    query_ids = {"a", "b"}
    ranks = [
        {"intent_id": "a", "status": "failed"},
        {"intent_id": "b", "status": "success"},
    ]
    contexts = [
        {"intent_id": intent, "budget": budget}
        for intent in sorted(query_ids)
        for budget in (4096, 8192)
    ]

    row = execution_row("C", query_ids, ranks, contexts, scored_detail_cells=44)

    assert row["status"] == "failed_or_partial"
    assert row["retrieved"] == 1
    assert row["retrieval_failed"] == 1
    assert row["exact_ranking_coverage"] is True
    assert row["exact_context_coverage"] is True

    ranks[0]["status"] = "success"
    assert execution_row("C", query_ids, ranks, contexts, 44)["status"] == "scored"

    ranks[0]["intent_id"] = "extra"
    row = execution_row("C", query_ids, ranks, contexts, 44)
    assert row["status"] == "failed_or_partial"
    assert row["exact_ranking_coverage"] is False

    ranks[0]["intent_id"] = "a"
    contexts[-1] = dict(contexts[0])
    row = execution_row("C", query_ids, ranks, contexts, 44)
    assert row["status"] == "failed_or_partial"
    assert row["exact_context_coverage"] is False


def test_candidate_boundary_tie_is_resolved_by_next_criterion():
    metrics = [
        {
            "configuration_id": "A",
            "cgc4_lower": 0.8,
            "cgc4_upper": 0.9,
            "cegr10_lower": 0.7,
            "cegr10_upper": 0.8,
            "retrieval_mean_seconds": 2.0,
        },
        {
            "configuration_id": "B",
            "cgc4_lower": 0.7,
            "cgc4_upper": 0.8,
            "cegr10_lower": 0.4,
            "cegr10_upper": 0.6,
            "retrieval_mean_seconds": 1.0,
        },
    ]

    decision = candidate_decision(metrics)

    assert decision["status"] == "frozen"
    assert decision["selected"] == ["A", "B"]


def test_select_panel_rejects_duplicate_intent_rows():
    records = [
        {
            "kind": "layer1_raw",
            "method": "R4",
            "k": 10,
            "intent_id": "a",
            "failure": None,
        },
        {
            "kind": "layer1_raw",
            "method": "R4",
            "k": 10,
            "intent_id": "b",
            "failure": None,
        },
    ]
    chosen, lookup = select_panel(records, "R4_CEGR10", {"a", "b"})
    assert len(chosen) == len(lookup) == 2

    with pytest.raises(ValueError, match="duplicate or incomplete"):
        select_panel(records + [dict(records[0])], "R4_CEGR10", {"a", "b"})


def test_statistics_bind_to_passed_verification_and_scoring_mapping(tmp_path):
    output = tmp_path / "run"
    output.mkdir()
    actual_map = tmp_path / "actual-map.json"
    write_json(actual_map, {"records": [{"intent_id": "from-score"}]})
    write_json(output / "common-support-map-e1-r04.json", {"records": [{"intent_id": "wrong-hardcoded-map"}]})
    scores_path = output / "scores-e1-r01.json"
    write_json(
        scores_path,
        {
            "mapping_path": str(actual_map),
            "mapping_sha256": file_sha(actual_map),
        },
    )
    verification = tmp_path / "verification.json"
    write_json(
        verification,
        {
            "status": "passed",
            "score_file_sha256": file_sha(scores_path),
            "mapping_sha256": file_sha(actual_map),
        },
    )

    scores, records, resolved_map = load_verified_scoring(output, verification)

    assert scores["mapping_path"] == str(actual_map)
    assert [r["intent_id"] for r in records] == ["from-score"]
    assert resolved_map == actual_map.resolve()

    write_json(
        verification,
        {
            "status": "failed_matrix_explicit",
            "score_file_sha256": file_sha(scores_path),
            "mapping_sha256": file_sha(actual_map),
        },
    )
    with pytest.raises(ValueError, match="passed verification"):
        load_verified_scoring(output, verification)


def test_statistics_require_current_per_config_detail_binding(tmp_path):
    output = tmp_path / "run"
    detail = output / "index-C" / "score-details-e1-r01.jsonl"
    detail.parent.mkdir(parents=True)
    detail.write_text('{"intent_id":"q"}\n', encoding="utf8")
    verification = {
        "status": "passed",
        "checks": {
            "C": {
                "status": "passed",
                "artifact_sha256": {"score-details-e1-r01.jsonl": file_sha(detail)},
            }
        },
    }

    assert require_verified_artifact(output, verification, "C", "score-details-e1-r01.jsonl") == file_sha(detail)

    detail.write_text('{"intent_id":"drift"}\n', encoding="utf8")
    with pytest.raises(ValueError, match="artifact drift"):
        require_verified_artifact(output, verification, "C", "score-details-e1-r01.jsonl")

    with pytest.raises(ValueError, match="artifact binding"):
        require_verified_artifact(output, verification, "C", "contexts.jsonl")


def test_integrate_revision_paths_preserve_r04_by_default(tmp_path):
    default_map, default_receipt = integration_output_paths(tmp_path, "r04")
    revised_map, revised_receipt = integration_output_paths(tmp_path, "r05")

    assert default_map.name == "common-support-map-e1-r04.json"
    assert default_receipt.name == "source-review-integration.json"
    assert revised_map.name == "common-support-map-e1-r05.json"
    assert revised_receipt.name == "source-review-integration-r05.json"
    assert default_map != revised_map

    with pytest.raises(ValueError, match="integration revision"):
        integration_output_paths(tmp_path, "r06")


def equivalence_fixture(order=("left", "right"), chunk_prefix="a"):
    source = {
        "left": {
            "core_spans": [{"doc_id": "d", "source_version": "v", "element_id": "e", "start": 0, "end": 4}],
            "overlap_spans": [],
            "prefix_spans": [],
            "text": "left",
            "score": 1.0,
        },
        "right": {
            "core_spans": [{"doc_id": "d", "source_version": "v", "element_id": "e", "start": 5, "end": 10}],
            "overlap_spans": [],
            "prefix_spans": [],
            "text": "right",
            "score": 1.0,
        },
    }
    children = []
    for name in ("left", "right"):
        children.append(dict(source[name], chunk_id=f"{chunk_prefix}-{name}"))
    ranked = [dict(source[name], chunk_id=f"{chunk_prefix}-{name}") for name in order]
    ranking = {
        "intent_id": "q",
        "status": "success",
        "results": {method: ranked for method in ("R1", "R2", "R3", "R4")},
        "rrf_union": ranked,
    }
    units = [
        {
            "seed_chunk_id": f"{chunk_prefix}-{name}",
            "spans": source[name]["core_spans"],
            "text": source[name]["text"],
        }
        for name in order
    ]
    contexts = []
    for budget in (4096, 8192):
        stage = {
            "serialized_context": "|".join(order),
            "token_count": 2,
            "units": units,
        }
        contexts.append(
            {
                "intent_id": "q",
                "configuration_id": chunk_prefix,
                "context_id": f"context-{chunk_prefix}-{budget}",
                "budget": budget,
                "panel_id": "fixed_budget_main",
                "strategy": "P0",
                "raw": stage,
                "expanded": stage,
                "deduplicated": stage,
                "final": stage,
                "truncation": [],
            }
        )
    return children, [ranking], contexts


def test_same_partition_with_different_tie_ranking_is_not_collapsed():
    library_a, ranks_a, contexts_a = equivalence_fixture(("left", "right"), "a")
    library_b, ranks_b, _ = equivalence_fixture(("right", "left"), "b")
    _, _, contexts_b = equivalence_fixture(("left", "right"), "b")

    signatures_a = strict_equivalence_signatures(library_a, ranks_a, contexts_a)
    signatures_b = strict_equivalence_signatures(library_b, ranks_b, contexts_b)

    assert signatures_a["source_partition_signature"] == signatures_b["source_partition_signature"]
    assert signatures_a["ranking_contract_signature"] != signatures_b["ranking_contract_signature"]
    assert signatures_a["context_contract_signature"] == signatures_b["context_contract_signature"]
    assert signatures_a["strict_equivalence_signature"] != signatures_b["strict_equivalence_signature"]

    representatives, aliases = select_equivalent_representatives(
        [
            dict(configuration_id="A", retrieval_mean_seconds=2.0, signatures=signatures_a),
            dict(configuration_id="B", retrieval_mean_seconds=1.0, signatures=signatures_b),
        ]
    )
    assert {r["configuration_id"] for r in representatives} == {"A", "B"}
    assert aliases == []


def test_strict_equivalence_keeps_fastest_actual_representative():
    library_a, ranks_a, contexts_a = equivalence_fixture(chunk_prefix="a")
    library_b, ranks_b, contexts_b = equivalence_fixture(chunk_prefix="b")
    signatures_a = strict_equivalence_signatures(library_a, ranks_a, contexts_a)
    signatures_b = strict_equivalence_signatures(library_b, ranks_b, contexts_b)
    assert signatures_a["strict_equivalence_signature"] == signatures_b["strict_equivalence_signature"]

    representatives, aliases = select_equivalent_representatives(
        [
            dict(configuration_id="slow", retrieval_mean_seconds=2.0, signatures=signatures_a),
            dict(configuration_id="fast", retrieval_mean_seconds=1.0, signatures=signatures_b),
        ]
    )

    assert [r["configuration_id"] for r in representatives] == ["fast"]
    assert aliases == [
        {
            "configuration_id": "slow",
            "equivalent_to": "fast",
            "basis": "identical canonical source partition, R1/R2/RRF-union/R3/R4 ranked source-text-score contracts, and actual P0 stage serialized text/spans at 4096/8192; configuration-derived chunk/context IDs ignored",
            "strict_equivalence_signature": signatures_a["strict_equivalence_signature"],
            "representative_rule": "minimum measured retrieval mean seconds, then configuration_id",
        }
    ]
