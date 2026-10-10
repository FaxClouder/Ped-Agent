"""Tests for the Stage 2 development annotation scope builder."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_dev_scope import (
    EVIDENCE_PATH,
    MANIFEST_PATH,
    OUTPUT_MANIFEST_PATH,
    QUESTIONS_PATH,
    build,
    build_rows,
    sha256,
    resolve_output_paths,
)


def _read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_build_rows_are_twenty_bilingual_pending_intents() -> None:
    rows = build_rows()

    assert len(rows) == 20
    assert sum(len(row["question_ids"]) for row in rows) == 40
    assert len({row["intent_id"] for row in rows}) == 20
    for row in rows:
        assert set(row["queries"]) == {"en", "zh"}
        assert len(row["question_ids"]) == 2
        assert row["reference_answer_en"] is None
        assert row["reference_answer_zh"] is None
        assert row["required_facts"] == []
        assert row["annotation_status"] == "pending_human_review"
        assert row["human_verified"] is False
        assert row["candidate_evidence"]["human_verified"] is False


def test_build_rows_match_candidate_dev_scope() -> None:
    source_questions = _read_jsonl(QUESTIONS_PATH)
    expected = {
        (question["intent_id"], question["question_id"])
        for question in source_questions
        if question.get("proposed_split") == "proposed_dev"
        and question.get("answerable") is True
    }
    actual = {
        (row["intent_id"], question_id)
        for row in build_rows()
        for question_id in row["question_ids"]
    }

    assert actual == expected
    assert len(actual) == 40


def test_build_writes_manifest_with_source_and_output_hashes(tmp_path: Path) -> None:
    output_path = tmp_path / "answer_annotations_dev_v1.jsonl"
    output_manifest_path = tmp_path / "answer_annotation_manifest_dev_v1.json"
    decisions_path = tmp_path / "annotation_decisions_dev_v1.md"
    build(output_path, output_manifest_path=output_manifest_path, decisions_path=decisions_path)

    rows = _read_jsonl(output_path)
    assert len(rows) == 20
    manifest = json.loads(output_manifest_path.read_text(encoding="utf-8"))
    assert manifest["intent_count"] == 20
    assert manifest["query_variant_count"] == 40
    assert manifest["source_sha256"][QUESTIONS_PATH.name] == sha256(QUESTIONS_PATH)
    assert manifest["source_sha256"][EVIDENCE_PATH.name] == sha256(EVIDENCE_PATH)
    assert manifest["source_sha256"][MANIFEST_PATH.name] == sha256(MANIFEST_PATH)
    assert manifest["output_sha256"][output_path.name] == sha256(output_path)
    assert manifest["output_sha256"][output_path.name] != hashlib.sha256(b"").hexdigest()
    assert manifest["status"] == "candidate_annotation_scope"
    assert manifest["human_verified"] is False
    assert decisions_path.exists()


def test_builder_rejects_existing_outputs(tmp_path: Path) -> None:
    output_path = tmp_path / "answer_annotations_dev_v1.jsonl"
    manifest_path = tmp_path / "answer_annotation_manifest_dev_v1.json"
    decisions_path = tmp_path / "annotation_decisions_dev_v1.md"
    output_path.write_text("do not replace", encoding="utf-8")
    with pytest.raises(FileExistsError):
        build(output_path, output_manifest_path=manifest_path, decisions_path=decisions_path)
    assert output_path.read_text(encoding="utf-8") == "do not replace"
    assert not manifest_path.exists()
    assert not decisions_path.exists()


def test_custom_output_paths_are_siblings(tmp_path: Path) -> None:
    output, manifest, decisions = resolve_output_paths(tmp_path / "answer_annotations_dev_v1.jsonl")
    assert output.parent == manifest.parent == decisions.parent == tmp_path
