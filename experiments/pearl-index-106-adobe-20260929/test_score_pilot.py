"""PEARL metric examples independent of the retrieval implementation."""

import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("pearl_score_pilot", HERE / "score_pilot.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_evidence_bundle_needs_joint_children_and_first_complete_rank():
    gold = {
        "atoms": [{"atom_id": "a"}, {"atom_id": "b"}],
        "requirements": [{"requirement_id": "r1", "support_bundles": [["a", "b"]]}],
        "evidence_groups": [{"group_id": "g", "requirements": ["r1"]}],
    }
    paths = {"a": [["c1", "c2"]], "b": [["c3"]]}
    ranking = ["c1", "c3", "c2"]
    assert MODULE.score_prefix(gold, paths, ranking, 2)["CEGR"] == 0
    scored = MODULE.score_prefix(gold, paths, ranking, 3)
    assert scored["CEGR"] == 1
    assert scored["BestGroupCov"] == 1
    assert scored["CompleteRR"] == 1 / 3
    assert scored["first_complete_rank"] == 3


def test_group_coverage_uses_requirements_not_atoms():
    gold = {
        "atoms": [{"atom_id": "a"}, {"atom_id": "b"}, {"atom_id": "c"}],
        "requirements": [
            {"requirement_id": "r1", "support_bundles": [["a", "b"]]},
            {"requirement_id": "r2", "support_bundles": [["c"]]},
        ],
        "evidence_groups": [{"group_id": "g", "requirements": ["r1", "r2"]}],
    }
    scored = MODULE.score_prefix(gold, {"a": [["c1"]], "b": [["c2"]], "c": []}, ["c1", "c2"], 2)
    assert scored["CEGR"] == 0
    assert scored["BestGroupCov"] == 0.5
    assert scored["CompleteRR"] == 0


def test_combine_accepts_eight_distinct_reviewed_intents(tmp_path):
    directory = HERE.parents[1] / "outputs/pearl-retrieval-dev-pilot-8-adobe106-20260929-01"
    output = tmp_path / "mapping.json"
    MODULE.combine(directory, output, MODULE.GOLD)
    mapping = json.loads(output.read_text(encoding="utf-8"))
    assert len(mapping["intents"]) == 8
