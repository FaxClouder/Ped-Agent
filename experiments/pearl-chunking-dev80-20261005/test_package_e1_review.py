import hashlib
import json
import sys
from pathlib import Path

import pytest


HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from package_e1 import (
    REUSED_FILES,
    STATISTICS_RECEIPT,
    TEST_CODE_SIDECAR,
    TEST_COMMAND_RECEIPT,
    validate_analysis_receipts,
    validate_baseline_conservation,
    validate_retrieval_and_zero_costs,
    validate_reuse,
    validate_supplemental_costs,
    validate_test_receipt,
    write_test_code_sidecar,
)
from e1_statistics import success_metadata


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True), encoding="utf8")


def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact_fixture(tmp_path):
    output = tmp_path / "run"
    configs = ["A", "B"]
    score = output / "scores-e1-r01.json"
    mapping = output / "common-support-map-e1-r05.json"
    verification = output / "verification-e1-r01.json"
    write_json(mapping, {"records": []})
    write_json(score, {"mapping_path": str(mapping), "mapping_sha256": file_sha(mapping)})
    checks = {}
    stat_bindings = {}
    case_bindings = {}
    for config in configs:
        directory = output / f"index-{config}"
        hashes = {}
        for name in ("score-details-e1-r01.jsonl", "rankings.jsonl", "contexts.jsonl"):
            path = directory / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(config + name, encoding="utf8")
            hashes[name] = file_sha(path)
        checks[config] = {"status": "passed", "artifact_sha256": hashes}
        stat_bindings[config] = hashes["score-details-e1-r01.jsonl"]
        case_bindings[config] = hashes
    write_json(
        verification,
        {
            "status": "passed",
            "score_file_sha256": file_sha(score),
            "mapping_sha256": file_sha(mapping),
            "checks": checks,
        },
    )
    costs = output / "costs-e1-r01.json"
    profiles = output / "chunk-profiles-e1-r01.json"
    write_json(costs, [])
    write_json(profiles, [])
    common = {
        "status": "completed",
        "verification_receipt_sha256": file_sha(verification),
        "score_file_sha256": file_sha(score),
        "mapping_sha256": file_sha(mapping),
        "generation_calls": 0,
    }
    statistics = dict(
        common,
        mapping_path=str(mapping),
        score_detail_bindings=stat_bindings,
        semantic_judgments_added=0,
        remote_model_calls=0,
        remote_judge_calls=0,
    )
    cases = dict(
        common,
        verified_direct_artifact_bindings=case_bindings,
        auxiliary_input_sha256={costs.name: file_sha(costs), profiles.name: file_sha(profiles)},
    )
    return output, configs, json.loads(verification.read_text("utf8")), json.loads(score.read_text("utf8")), statistics, cases


def test_statistics_and_cases_must_bind_current_verification_score_map_and_artifacts(tmp_path):
    output, configs, verified, scores, statistics, cases = artifact_fixture(tmp_path)
    validate_analysis_receipts(output, configs, verified, scores, statistics, cases)

    stale = json.loads(json.dumps(statistics))
    stale["verification_receipt_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="verification"):
        validate_analysis_receipts(output, configs, verified, scores, stale, cases)

    stale = json.loads(json.dumps(cases))
    stale["verified_direct_artifact_bindings"]["A"]["rankings.jsonl"] = "0" * 64
    with pytest.raises(ValueError, match="direct artifact"):
        validate_analysis_receipts(output, configs, verified, scores, statistics, stale)


def test_statistics_r02_success_metadata_explicitly_records_no_model_or_judge_calls():
    assert STATISTICS_RECEIPT == "statistics-e1-r02.json"
    assert success_metadata() == {
        "generation_calls": 0,
        "semantic_judgments_added": 0,
        "remote_model_calls": 0,
        "remote_judge_calls": 0,
    }


def reuse_fixture(tmp_path):
    root = tmp_path
    attempt = root / "outputs" / "pearl-chunking-dev80-20261005-04"
    output = root / "outputs" / "pearl-chunking-dev80-20261005-05"
    source = attempt / "index-C1-L256-O0-M0"
    target = output / "index-C1-L256-O0-M0"
    copied = {}
    artifacts = {}
    for name in REUSED_FILES:
        for directory in (source, target):
            directory.mkdir(parents=True, exist_ok=True)
            (directory / name).write_text(name, encoding="utf8")
        copied[name] = file_sha(source / name)
        key = (source / name).relative_to(root).as_posix()
        artifacts[key] = copied[name]
    manifest = {
        "status": "aborted_performance_restart",
        "accepted_run": output.relative_to(root).as_posix(),
        "completed_real_configuration": "C1-L256-O0-M0",
        "generation_calls": 0,
        "historical_scores_loaded": False,
        "logical_rerank_pairs_completed": 8000,
        "stored_contexts": 160,
        "retained_partial_configuration": "C1-L384-O0-M0",
        "artifact_count": len(artifacts),
        "artifacts_sha256": artifacts,
    }
    write_json(attempt / "attempt-delivery-manifest.json", manifest)
    receipt = {
        "configuration_id": "C1-L256-O0-M0",
        "origin": str(source.resolve()),
        "real_recorded_intents": 80,
        "new_build_model_calls": 0,
        "new_retrieval_model_calls": 0,
        "copied_sha256": copied,
    }
    write_json(output / "e1-current-run-cache-reuse.json", receipt)
    write_json(
        output / "input-copy-manifest.json",
        {"copied_sha256": {"e1-current-run-cache-reuse.json": file_sha(output / "e1-current-run-cache-reuse.json")}},
    )
    return root, attempt, output


def test_reuse_receipt_binds_origin_manifest_and_every_accepted_file(tmp_path):
    root, attempt, output = reuse_fixture(tmp_path)
    result = validate_reuse(output, attempt, root=root)
    assert result["files"] == len(REUSED_FILES)
    assert result["retrieval_intents"] == 80

    (output / "index-C1-L256-O0-M0" / REUSED_FILES[0]).write_text("drift", encoding="utf8")
    with pytest.raises(ValueError, match="reuse file hash"):
        validate_reuse(output, attempt, root=root)


def zero_cost_fixture(configs):
    matrix = {"status": "passed", "configuration_count": len(configs), "failed_configurations": [], "generation_calls": 0}
    scores = {"generation_calls": 0}
    verified = {"generation_calls": 0, "remote_judge_calls": 0}
    decision = {"generation_calls": 0}
    statistics = {
        "generation_calls": 0,
        "semantic_judgments_added": 0,
        "remote_model_calls": 0,
        "remote_judge_calls": 0,
    }
    cases = {"generation_calls": 0, "semantic_judgments_added": 0}
    rerun = {
        "status": "passed",
        "provenance": {"historical_scores_loaded": False, "gold_loaded": False, "dense_model_loaded": False},
        "cost": {"generation_calls": 0, "remote_calls": 0, "dense_model_loads": 0},
        "totals": {"configurations": len(configs), "query_intents_per_configuration": 80, "R4_pairs_recomputed": len(configs) * 8000},
        "configurations": [
            {"configuration_id": config, "R4": {"status": "passed", "queries": 80, "pairs_compared": 8000}}
            for config in configs
        ],
    }
    costs = [
        {
            "configuration_id": config,
            "generation_calls": 0,
            "remote_judge_calls": 0,
            "remote_model_calls": 0,
            "stages": {
                "build": {"generation_calls": 0, "remote_calls": 0},
                "retrieval": {"generation_calls": 0, "remote_calls": 0},
                "context": {"generation_calls": 0},
            },
        }
        for config in configs
    ]
    return matrix, scores, verified, decision, statistics, cases, rerun, costs


def test_retrieval_pair_total_and_zero_generation_api_costs_are_gated():
    configs = [f"C{i}" for i in range(13)]
    args = zero_cost_fixture(configs)
    validate_retrieval_and_zero_costs(configs, *args)

    bad = list(args)
    bad[6] = json.loads(json.dumps(args[6]))
    bad[6]["totals"]["R4_pairs_recomputed"] = 103999
    with pytest.raises(ValueError, match="104000"):
        validate_retrieval_and_zero_costs(configs, *bad)

    bad = list(args)
    bad[7] = json.loads(json.dumps(args[7]))
    bad[7][0]["remote_model_calls"] = 1
    with pytest.raises(ValueError, match="zero-call"):
        validate_retrieval_and_zero_costs(configs, *bad)


def test_b0_legacy_core_gaps_are_required_and_returned_for_disclosure(tmp_path):
    output = tmp_path / "run"
    path = output / "index-B0-regex320-overlap48-M0" / "source-conservation.json"
    write_json(
        path,
        {
            "status": "baseline_legacy_gaps_recorded",
            "source_characters": 100,
            "missing_characters": 7,
            "duplicate_core_characters": 0,
            "gaps": [{"reason": "legacy_regex_boundary", "start": 0, "end": 7}],
        },
    )
    disclosure = validate_baseline_conservation(output)
    assert disclosure["missing_core_characters"] == 7
    assert disclosure["evaluated_visible_evidence"] == "authenticated core_spans + overlap_spans"

    write_json(path, {"status": "passed", "missing_characters": 0, "duplicate_core_characters": 0, "gaps": []})
    with pytest.raises(ValueError, match="legacy core-gap"):
        validate_baseline_conservation(output)


def test_final_test_receipt_is_bound_to_current_code_and_logs(tmp_path):
    output = tmp_path / "run"
    output.mkdir()
    assert TEST_COMMAND_RECEIPT == "command-tests-r04.json"
    assert TEST_CODE_SIDECAR == "command-tests-r04-code-sha256.json"
    stdout = output / "command-tests-r04.stdout.log"
    stderr = output / "command-tests-r04.stderr.log"
    stdout.write_text("16 passed in 0.22s\n", encoding="utf8")
    stderr.write_text("", encoding="utf8")
    tests = {"argv": ["python", "-m", "pytest"], "exit_code": 0, "stdout": stdout.name, "stderr": stderr.name}
    receipt = output / TEST_COMMAND_RECEIPT
    write_json(receipt, tests)
    current_code = {"experiments/example.py": "a" * 64}
    write_test_code_sidecar(output, current_code=current_code)
    assert validate_test_receipt(output, tests, current_code) == 16

    sidecar = json.loads((output / TEST_CODE_SIDECAR).read_text("utf8"))
    sidecar["experiment_code_sha256"]["experiments/example.py"] = "b" * 64
    write_json(output / TEST_CODE_SIDECAR, sidecar)
    with pytest.raises(ValueError, match="code hash"):
        validate_test_receipt(output, tests, current_code)


def test_supplemental_cost_and_scheduling_receipts_bind_saved_verification(tmp_path):
    root = tmp_path
    output = root / "outputs" / "run"
    output.mkdir(parents=True)
    rerun_path = output / "independent-retrieval-verification-e1-r01.json"
    rerun = {
        "totals": {
            "R4_pairs_recomputed": 104000,
            "R4_actual_forward_tokens_including_probe_repetitions": 200000,
            "R4_adaptive_probe_repeat_forward_calls": 4160,
            "R4_adaptive_probe_repeat_tokens": 10000,
        },
        "configurations": [{"R4": {"actual_forward_call_count": 8320}} for _ in range(13)],
    }
    write_json(rerun_path, rerun)
    probe = root / "outputs" / "attempt" / "probe.json"
    write_json(probe, {"status": "passed"})
    supplemental = {
        "status": "recorded",
        "verification": {
            "receipt": rerun_path.name,
            "receipt_sha256": file_sha(rerun_path),
            "logical_pairs": 104000,
            "captured_forward_input_sequences_including_probes": 108160,
            "additional_probe_input_sequences": 4160,
            "actual_forward_input_tokens_including_probes": 200000,
            "additional_probe_input_tokens": 10000,
        },
        "context_assembly": {
            "accepted": 2080,
            "retained_original_attempt": 160,
            "additional_equivalence_probe_batch_assemblies": 12,
            "known_executed_total": 2252,
            "probes": [
                {"receipt": probe.relative_to(root).as_posix(), "sha256": file_sha(probe), "additional_batch_assemblies": 6},
                {"receipt": probe.relative_to(root).as_posix(), "sha256": file_sha(probe), "additional_batch_assemblies": 6},
            ],
        },
        "primary_model_accounting": {"unique_query_encodings": 1040, "logical_reranker_pairs": 104000},
        "generation_calls": 0,
        "external_model_api_calls": 0,
        "external_judge_api_calls": 0,
    }
    configs = [f"C{i}" for i in range(13)]
    scheduling = {
        "status": "recorded",
        "primary_retrieval_completed_configurations": 13,
        "primary_retrieval_completion_events": [
            {"configuration_id": config, "stage": "retrieve", "status": "completed"}
            for config in configs
        ],
        "independent_verification_command": "command-independent-retrieval-r01.json",
        "concurrent_primary_stage": "B0 P0 context assembly on CPU",
        "GPU_concurrency": "Independent R4 verification starts only after all primary GPU retrieval has completed.",
    }
    write_json(output / "supplemental-cost-accounting-e1-r01.json", supplemental)
    write_json(output / "verification-scheduling-e1.json", scheduling)
    result = validate_supplemental_costs(output, configs, rerun, supplemental, scheduling, root=root)
    assert result["known_context_assemblies"] == 2252
    assert result["captured_forward_input_sequences_including_probes"] == 108160

    supplemental["verification"]["additional_probe_input_sequences"] = 0
    write_json(output / "supplemental-cost-accounting-e1-r01.json", supplemental)
    with pytest.raises(ValueError, match="supplemental verification accounting"):
        validate_supplemental_costs(output, configs, rerun, supplemental, scheduling, root=root)


def test_analysis_accepts_named_e0_check_but_rejects_other_extra_checks(tmp_path):
    output, configs, verified, scores, statistics, cases = artifact_fixture(tmp_path)
    verified["checks"]["E0_frozen_release"] = {"status": "passed", "artifact_count": 160}
    path = output / "verification-e1-r01.json"
    path.write_text(json.dumps(verified), encoding="utf8")
    for receipt in (statistics, cases):
        receipt["verification_receipt_sha256"] = file_sha(path)
    validate_analysis_receipts(output, configs, verified, scores, statistics, cases)
    verified["checks"]["unexpected_config"] = {"status": "passed"}
    with pytest.raises(ValueError, match="configuration coverage"):
        validate_analysis_receipts(output, configs, verified, scores, statistics, cases)
    del verified["checks"]["unexpected_config"]
    verified["checks"]["E0_frozen_release"]["status"] = "failed"
    with pytest.raises(ValueError, match="E0 frozen"):
        validate_analysis_receipts(output, configs, verified, scores, statistics, cases)
