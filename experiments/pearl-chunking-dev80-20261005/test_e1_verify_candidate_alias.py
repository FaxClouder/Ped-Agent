import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from e1_verify import independent_candidate_contract, verify_candidate_equivalence


BASIS = (
    "identical canonical source partition, R1/R2/RRF-union/R3/R4 ranked "
    "source-text-score contracts, and actual P0 stage serialized text/spans at "
    "4096/8192; configuration-derived chunk/context IDs ignored"
)


def digest(value):
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def contract(config, source="source", ranking="ranking", context="context", latency=1.0):
    components = {
        "source_partition_signature": source,
        "ranking_contract_signature": ranking,
        "context_contract_signature": context,
    }
    return {
        "configuration_id": config,
        **components,
        "strict_equivalence_signature": digest(components),
        "retrieval_mean_seconds": latency,
    }


def metric(value):
    return {
        **value,
        "cgc4_lower": 0.8,
        "cgc4_upper": 0.8,
        "cegr10_lower": 0.7,
        "cegr10_upper": 0.7,
    }


def alias(config, representative, strict):
    return {
        "configuration_id": config,
        "equivalent_to": representative,
        "basis": BASIS,
        "strict_equivalence_signature": strict,
        "representative_rule": "minimum measured retrieval mean seconds, then configuration_id",
    }


def artifact_contract(order=("left", "right"), chunk_prefix="a"):
    children = {
        "left": {"core_spans": [{"doc_id": "d", "source_version": "v", "element_id": "e", "start": 0, "end": 4}], "overlap_spans": [], "prefix_spans": [], "text": "left", "score": 1.0},
        "right": {"core_spans": [{"doc_id": "d", "source_version": "v", "element_id": "e", "start": 5, "end": 10}], "overlap_spans": [], "prefix_spans": [], "text": "right", "score": 1.0},
    }
    library=[dict(children[name],chunk_id=f"{chunk_prefix}-{name}") for name in ("left","right")]
    ranked=[dict(children[name],chunk_id=f"{chunk_prefix}-{name}") for name in order]
    rankings=[{"intent_id":"q","status":"success","results":{m:ranked for m in ("R1","R2","R3","R4")},"rrf_union":ranked}]
    units=[{"seed_chunk_id":f"{chunk_prefix}-{name}","spans":children[name]["core_spans"],"text":children[name]["text"]} for name in ("left","right")]
    contexts=[]
    for budget in (4096,8192):
        stage={"units":units,"serialized_context":"left|right","token_count":2}
        contexts.append({"intent_id":"q","configuration_id":chunk_prefix,"context_id":f"ctx-{chunk_prefix}-{budget}","budget":budget,"panel_id":"fixed_budget_main","strategy":"P0","raw":stage,"expanded":stage,"deduplicated":stage,"final":stage,"truncation":[]})
    return independent_candidate_contract(library,rankings,contexts)


def test_same_partition_but_different_tie_ranking_cannot_be_aliased():
    a = {"configuration_id":"A","retrieval_mean_seconds":2.0,**artifact_contract(("left","right"),"a")}
    b = {"configuration_id":"B","retrieval_mean_seconds":1.0,**artifact_contract(("right","left"),"b")}
    assert a["source_partition_signature"]==b["source_partition_signature"]
    assert a["context_contract_signature"]==b["context_contract_signature"]
    assert a["ranking_contract_signature"]!=b["ranking_contract_signature"]
    decision = {
        "baseline_retained": "B0-regex320-overlap48-M0",
        "nonduplicate_metrics": [metric(a)],
        "equivalent_configs": [alias("B", "A", a["strict_equivalence_signature"])],
    }

    with pytest.raises(ValueError, match="candidate equivalence"):
        verify_candidate_equivalence(decision, {"A": a, "B": b})


def test_strict_group_must_keep_fastest_actual_representative():
    slow = contract("A", latency=2.0)
    fast = contract("B", latency=1.0)
    decision = {
        "baseline_retained": "B0-regex320-overlap48-M0",
        "nonduplicate_metrics": [metric(slow)],
        "equivalent_configs": [alias("B", "A", slow["strict_equivalence_signature"])],
    }

    with pytest.raises(ValueError, match="representative"):
        verify_candidate_equivalence(decision, {"A": slow, "B": fast})

    decision["nonduplicate_metrics"] = [metric(fast)]
    decision["equivalent_configs"] = [alias("A", "B", fast["strict_equivalence_signature"])]
    assert verify_candidate_equivalence(decision, {"A": slow, "B": fast})


def test_every_eligible_configuration_must_be_represented_once():
    a = contract("A")
    b = contract("B", source="different")
    decision = {
        "baseline_retained": "B0-regex320-overlap48-M0",
        "nonduplicate_metrics": [metric(a)],
        "equivalent_configs": [],
    }

    with pytest.raises(ValueError, match="coverage"):
        verify_candidate_equivalence(decision, {"A": a, "B": b})
