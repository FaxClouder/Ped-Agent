"""Independent synthetic identity-gate counterexamples; no model execution."""
import json
from pathlib import Path
from types import SimpleNamespace
import sys

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import smoke
from runtime import cache_identity, sha


def write(path, value):
    path.write_text(json.dumps(value), encoding="utf8")


@pytest.fixture
def gated_run(tmp_path, monkeypatch):
    # Synthetic provenance records exercise the actual gate and actual file SHA.
    # Replacing model construction with a failing sentinel proves no inference.
    monkeypatch.setattr(smoke, "models", lambda: pytest.fail("gate reached model execution"))
    monkeypatch.setattr(smoke, "model_assets", lambda: {"synthetic-model": "frozen"})
    monkeypatch.setattr(smoke, "counter", lambda: SimpleNamespace(fingerprint="synthetic-tokenizer"))
    def read_rows(path):
        return [json.loads(line) for line in Path(path).read_text("utf8").splitlines() if line]
    monkeypatch.setattr(smoke, "legacy_runtime", lambda: SimpleNamespace(compare=SimpleNamespace(read_jsonl=read_rows)))
    write(tmp_path / "source-views-prepared.json", [])
    write(tmp_path / "table-snapshot.json", {"tables": []})
    write(tmp_path / "public-parent-graph.json", {"parents": []})
    queries = [{"intent_id": str(i), "query": "frozen question " + str(i)} for i in range(8)]
    (tmp_path / "queries.jsonl").write_text("\n".join(json.dumps(q) for q in queries), encoding="utf8")
    index = tmp_path / "index-C1-L384-O0-M0"
    index.mkdir()
    (index / "synthetic-index.bin").write_bytes(b"frozen index asset")
    configuration = {
        "models": {"synthetic-model": "frozen"},
        "source": sha(tmp_path / "source-views-prepared.json"),
        "table": sha(tmp_path / "table-snapshot.json"),
        "parent": sha(tmp_path / "public-parent-graph.json"),
        "tokenizer": "synthetic-tokenizer",
        "code": {str((smoke.EXP / "runtime.py").relative_to(smoke.ROOT)): sha(smoke.EXP / "runtime.py")},
    }
    manifest = {"configuration": configuration, "output_sha256": {"synthetic-index.bin": sha(index / "synthetic-index.bin")}}
    write(index / "manifest.json", manifest)
    ranking = {
        "intent_id": "0", "status": "success", "results": {"R4": []},
        "index_sha256": sha(index / "manifest.json"),
        "query_sha256": cache_identity(queries[0]),
        "source_sha256": configuration["source"], "parent_sha256": configuration["parent"],
    }
    (tmp_path / "rankings.jsonl").write_text(json.dumps(ranking) + "\n", encoding="utf8")
    return tmp_path, index, manifest, queries


@pytest.mark.parametrize("identity", ["source", "table", "parent", "tokenizer", "code", "models"])
def test_retrieval_rejects_frozen_identity_drift_before_models(gated_run, identity):
    output, index, manifest, _ = gated_run
    if identity in {"source", "table", "parent"}:
        path = {"source": "source-views-prepared.json", "table": "table-snapshot.json", "parent": "public-parent-graph.json"}[identity]
        # Alter current source, leaving the frozen index manifest/assets intact.
        (output / path).write_text("[\"changed current asset\"]", encoding="utf8")
    elif identity == "code":
        manifest["configuration"]["code"] = {name: "incorrect-frozen-code-sha" for name in manifest["configuration"]["code"]}
        write(index / "manifest.json", manifest)
    else:
        manifest["configuration"][identity] = "different-frozen-identity"
        write(index / "manifest.json", manifest)
    with pytest.raises(ValueError, match="drift"):
        smoke.retrieve(output)
    assert not (output / "retrieval-audits.jsonl").exists()


@pytest.mark.parametrize("drift", ["query", "source", "parent", "index_manifest", "index_asset"])
def test_context_rejects_rankings_binding_or_index_asset_drift(gated_run, monkeypatch, drift):
    output, index, manifest, queries = gated_run
    import assemble
    monkeypatch.setattr(assemble, "assemble", lambda *args: pytest.fail("drift reached assembly"))
    if drift == "query":
        queries[0]["query"] = "changed query"
        (output / "queries.jsonl").write_text("\n".join(json.dumps(q) for q in queries), encoding="utf8")
    elif drift in {"source", "parent"}:
        path = "source-views-prepared.json" if drift == "source" else "public-parent-graph.json"
        write(output / path, [])
        # Preserve valid JSON while making an actual byte-identity change.
        with (output / path).open("a", encoding="utf8") as handle:
            handle.write("\n")
    elif drift == "index_manifest":
        manifest["unexpected_field"] = "changed"
        write(index / "manifest.json", manifest)
    else:
        (index / "synthetic-index.bin").write_bytes(b"changed index asset")
    with pytest.raises(ValueError, match="drift"):
        smoke.contexts(output)
    assert not (output / "contexts.jsonl").exists()
