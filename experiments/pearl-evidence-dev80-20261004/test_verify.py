"""Independent evidence scoring oracle and saved-artifact audit fixtures."""
import importlib.util
from pathlib import Path

import pytest
import hashlib


def verifier():
    spec = importlib.util.spec_from_file_location("evidence_verifier", Path(__file__).with_name("verify.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("groups,labels,expected", [
    ([["a", "b"]], {"a": "supported", "b": "unsupported"}, "unsupported"),
    ([["a", "b"], ["c"]], {"a": "supported", "b": "unknown", "c": "supported"}, "supported"),
    ([["a", "b"]], {"a": "supported", "b": "unknown"}, "unknown"),
    ([["a", "b"]], {"a": "unsupported", "b": "unknown"}, "unsupported"),
    ([["a", "b"], ["c", "d"]], {"a": "supported", "b": "unsupported", "c": "unsupported", "d": "supported"}, "unsupported"),
])
def test_or_of_and_keeps_alternatives_and_unknown(groups, labels, expected):
    assert verifier().oracle(groups, labels) == expected


@pytest.mark.parametrize("groups,labels", [([], {}), ([[]], {}), ([["a"]], {}), ([["a"]], {"a": "not_applicable"})])
def test_oracle_rejects_invalid_or_missing_requirements(groups, labels):
    with pytest.raises(ValueError):
        verifier().oracle(groups, labels)


def context_fixture():
    text = "[u1] source\nbody"
    digest = hashlib.sha256(text.encode()).hexdigest()
    return dict(context_id="i::C0-4096", intent_id="i", configuration="C0-4096", budget=4096,
                token_count=len(text), serialized_context=text, text_sha256=digest, question_type="single",
                units=[dict(unit_id="u1", text="body", text_sha256=hashlib.sha256(b"body").hexdigest())])


def test_final_context_recounts_serialized_text_and_complete_matrix():
    v = verifier()
    rows = [dict(context_fixture(), context_id="i::"+c, configuration=c, budget=int(c.split("-")[1])) for c in v.CONFIGURATIONS]
    assert v.audit_contexts(rows, len, expected_intents=["i"], expected_types={"single": 1})["contexts"] == 4
    rows[0]["token_count"] += 1
    with pytest.raises(ValueError, match="token"):
        v.audit_contexts(rows, len, expected_intents=["i"])


@pytest.mark.parametrize("mutation", ["text", "budget", "duplicate", "missing", "unit"])
def test_context_audit_rejects_saved_mutations(mutation):
    v = verifier()
    rows = [dict(context_fixture(), context_id="i::"+c, configuration=c, budget=int(c.split("-")[1])) for c in v.CONFIGURATIONS]
    if mutation == "text": rows[0]["serialized_context"] += "!"
    if mutation == "budget": rows[0]["budget"] = 2
    if mutation == "duplicate": rows.append(rows[0])
    if mutation == "missing": rows.pop()
    if mutation == "unit": rows[0]["units"][0]["text"] += "!"
    with pytest.raises(ValueError):
        v.audit_contexts(rows, len, expected_intents=["i"])


def test_saved_file_sha_and_source_preservation_reject_mutation(tmp_path):
    v = verifier()
    source = tmp_path / "old.txt"
    source.write_bytes(b"frozen")
    binding = {"path": str(source), "sha256": hashlib.sha256(b"frozen").hexdigest()}
    assert v.audit_files([binding]) == 1
    source.write_bytes(b"changed")
    with pytest.raises(ValueError, match="SHA"):
        v.audit_files([binding])


def test_independent_bounds_macro_noise_and_paired_statistics():
    v = verifier()
    rows = []
    labels = {"C0-4096": ["no", "yes", "unknown"], "C0-8192": ["yes", "yes", "no"],
              "C1-4096": ["yes", "no", "unknown"], "C1-8192": ["yes", "yes", "yes"]}
    for config, values in labels.items():
        for i, value in enumerate(values):
            rows.append(dict(intent_id=str(i),configuration=config,question_type="T" if i < 2 else "U",
                             sufficient=value,coverage_lower=float(value=="yes"),coverage_upper=float(value!="no"),
                             unit_labels=["mixed", "unknown"] if i==0 else []))
    result = v.recompute_statistics(rows)
    first = result["overall"]["C0-4096"]
    assert first["n"] == 3 and first["yes"] == first["no"] == first["unknown"] == 1
    assert first["complete_group_upper"] == 2/3
    assert first["relevance_lower"] == first["noise_lower"] == .5
    assert first["noise_upper"] == 1 and first["relevance_applicable_n"] == 1
    assert result["by_type"]["T"]["C0-4096"]["n"] == 2
    pair = result["paired"][0]
    assert pair["gain"] == pair["loss"] == pair["unknown_pairs"] == 1
    assert pair["delta_lower"] == -1/3 and pair["delta_upper"] == 1/3
    assert pair["exact_mcnemar_p_resolved"] == 1


def review_fixture():
    v = verifier()
    text = "[Source source | p1]\nTitle: title\nbody"
    context = context_fixture()
    context.update(serialized_context=text,text_sha256=v.sha_text(text),token_count=len(text))
    context["units"][0].update(source_id="source",locator="p1",title="title")
    blinded = "[Source S1 | p1]\nTitle: title\nbody"
    body = dict(query="Q", requirements=[dict(requirement_id="a",claim="body")],allowed_groups=[["a"]],
                serialized_context=blinded, units=[dict(unit_id="U1",source_id="S1",text_sha256=v.sha_text("body"),character_start=0,character_end=len(blinded))])
    digest = v.sha_text(v.canonical(body))
    packet = dict(body,packet_id="packet-"+digest[:24],packet_sha256=digest)
    binding = dict(context_id=context["context_id"],intent_id="i",stage="final",packet_id=packet["packet_id"],
                   packet_sha256=digest,original_text_sha256=v.sha_text(text),blinded_text_sha256=v.sha_text(body["serialized_context"]),
                   source_map={"source":"S1"},unit_map=[dict(occurrence_index=0,original_unit_id="u1",blind_unit_id="U1")])
    review = dict(packet_id=packet["packet_id"],packet_sha256=digest,support={"a":dict(label="yes",rationale="body",quotes=["body"])},unit_labels={"U1":"relevant"})
    review.update(full_read=True,reviewer_id="fixture-reviewer",model_id="fixture-model",prompt_sha256="4554628c5f53fb465a33974e1dbef0606d741a031a2b42931f46b8786ec5e255",elapsed_seconds=None)
    return context,packet,binding,review


def test_independent_review_binding_and_oracle():
    v = verifier()
    c,p,b,r = review_fixture()
    rows = v.recompute_rows([c],[p],[b],[r])
    assert rows[0]["sufficient"] == "yes" and rows[0]["coverage_lower"] == 1


@pytest.mark.parametrize("mutation", ["packet", "context", "quote", "missing", "unit", "binding", "extra"])
def test_independent_review_audit_rejects_mutations(mutation):
    v = verifier()
    c,p,b,r = review_fixture()
    if mutation == "packet": p["query"] = "wrong"
    if mutation == "context": c["serialized_context"] += "wrong"
    if mutation == "quote": r["support"]["a"]["quotes"] = ["absent"]
    if mutation == "missing": r["support"] = {}
    if mutation == "unit": r["unit_labels"] = {}
    if mutation == "binding": b["blinded_text_sha256"] = "wrong"
    reviews = [r,r] if mutation == "extra" else [r]
    with pytest.raises(ValueError):
        v.recompute_rows([c],[p],[b],reviews)


def test_saved_score_reread_detects_changed_denominator(tmp_path):
    v = verifier()
    c,p,b,r = review_fixture()
    contexts, bindings = [], []
    for cfg in v.CONFIGURATIONS:
        cid = "i::"+cfg
        contexts.append(dict(c,context_id=cid,configuration=cfg,budget=int(cfg.split("-")[1])))
        bindings.append(dict(b,context_id=cid))
    paths = {}
    for name, records in (("contexts",contexts),("packets",[p]),("bindings",bindings),("reviews",[r])):
        paths[name] = tmp_path / (name+".jsonl")
        paths[name].write_text("".join(__import__("json").dumps(x)+"\n" for x in records),encoding="utf-8")
    scores = dict(rows=v.recompute_rows(contexts,[p],bindings,[r]))
    scores.update(v.recompute_statistics(scores["rows"]))
    scores["bootstrap_ci"] = v.independent_bootstrap(scores["rows"])
    paths["scores"] = tmp_path / "scores.json"
    paths["scores"].write_text(__import__("json").dumps(scores),encoding="utf-8")
    out = v.audit_saved(paths, len, ["i"], {"single":1})
    assert out["score_rows"] == 4
    scores["overall"]["C0-4096"]["n"] = 2
    paths["scores"].write_text(__import__("json").dumps(scores),encoding="utf-8")
    with pytest.raises(ValueError,match="score"):
        v.audit_saved(paths,len,["i"],{"single":1})


def test_selected_review_content_manifest_detects_mutation():
    v = verifier()
    c,p,b,r = review_fixture()
    manifest = {"prompt_sha256":r["prompt_sha256"], "selected":[dict(packet_id=r["packet_id"],packet_sha256=r["packet_sha256"],review_content_sha256=v.sha_text(v.canonical(r)))]}
    assert v.audit_selected([r],manifest) == 1
    r["support"]["a"]["rationale"] += "changed"
    with pytest.raises(ValueError,match="selected"):
        v.audit_selected([r],manifest)


def test_independent_step_attribution_requires_two_text_judgments():
    v = verifier()
    rows = [dict(context_id="i",stage=stage,sufficient=status,support={"a":label,"b":"unknown"})
            for stage,status,label in [("raw","no","no"),("expanded","unknown","yes"),("deduplicated","no","no")]]
    out = v.recompute_attribution(rows)
    assert out[0]["requirement_gains"] == ["a"]
    assert out[1]["requirement_losses"] == ["a"]
    assert all(r["unknown_requirements"] == ["b"] for r in out)
    assert len(out) == 2


def bootstrap_rows(statuses=None):
    configs = ("C0-4096","C0-8192","C1-4096","C1-8192")
    statuses = statuses or ["no","yes","unknown","yes"]
    return [dict(intent_id=f"i{i}",question_type="T" if i < 2 else "U",configuration=c,sufficient=statuses[j])
            for i in range(4) for j,c in enumerate(configs)]


def test_independent_bootstrap_constant_unknown_and_shared_pairs():
    v = verifier()
    result = v.independent_bootstrap(bootstrap_rows())
    assert result["replicates"] == 10000 and result["seed"] == 20261004
    assert result["stratum_sizes"] == {"T":2,"U":2}
    assert result["overall"]["C1-4096"]["lower_bound_ci"] == [0,0]
    assert result["overall"]["C1-4096"]["upper_bound_ci"] == [1,1]
    assert result["paired"][0]["envelope"] == [0,1]
    assert result["paired"][1]["envelope"] == [0,0]
    assert result["paired"][2]["lower_bound_point"] == 1
    varied = bootstrap_rows(["yes","yes","no","no"])
    varied[0]["sufficient"] = varied[1]["sufficient"] = "no"
    expected = v.independent_bootstrap(varied)
    assert expected["paired"][2]["envelope"] == [0,0]
    assert v.independent_bootstrap(list(reversed(varied))) == expected


def test_saved_ci_tampering_rejected():
    v = verifier()
    rows = bootstrap_rows()
    saved = v.independent_bootstrap(rows)
    saved["paired"][0]["envelope"][0] = .1
    with pytest.raises(ValueError,match="bootstrap"):
        v.audit_bootstrap(rows,saved)


@pytest.mark.parametrize("field", ["statistics_version","statistics_supplement_sha256","score_code_sha256"])
def test_bootstrap_version_and_code_document_binding(field):
    v = verifier()
    rows = bootstrap_rows()
    saved = v.independent_bootstrap(rows)
    saved[field] = "wrong"
    with pytest.raises(ValueError,match="bootstrap"):
        v.audit_bootstrap(rows,saved)


def test_bootstrap_invalid_cluster_matrix():
    v = verifier()
    with pytest.raises(ValueError):
        v.independent_bootstrap(bootstrap_rows()[:-1])
    rows = bootstrap_rows()
    rows[0]["question_type"] = "drift"
    with pytest.raises(ValueError):
        v.independent_bootstrap(rows)


def test_missing_step_binding_rejected_even_with_final_review():
    v = verifier()
    c,p,b,r = review_fixture()
    c["steps"] = {"raw":dict(serialized_context=c["serialized_context"],text_sha256=c["text_sha256"],units=c["units"])}
    with pytest.raises(ValueError,match="step"):
        v.recompute_rows([c],[p],[b],[r])


@pytest.mark.parametrize("field,value", [("full_read",False),("model_id",""),("reviewer_id",""),("prompt_sha256","wrong"),("elapsed_seconds",-1)])
def test_selected_per_review_provenance_required(field,value):
    v = verifier()
    c,p,b,r = review_fixture()
    r[field] = value
    manifest = {"prompt_sha256":"4554628c5f53fb465a33974e1dbef0606d741a031a2b42931f46b8786ec5e255","selected":[dict(packet_id=r["packet_id"],packet_sha256=r["packet_sha256"],review_content_sha256=v.sha_text(v.canonical(r)))]}
    with pytest.raises(ValueError,match="provenance"):
        v.audit_selected([r],manifest)


def test_synchronized_wrong_prompt_review_and_manifest_rejected():
    v = verifier()
    c,p,b,r = review_fixture()
    r["prompt_sha256"] = "wrong-synchronized-prompt"
    manifest = {"prompt_sha256":r["prompt_sha256"],"selected":[dict(packet_id=r["packet_id"],packet_sha256=r["packet_sha256"],review_content_sha256=v.sha_text(v.canonical(r)))]}
    with pytest.raises(ValueError,match="prompt"):
        v.audit_selected([r],manifest)


@pytest.mark.parametrize("field",["query","requirements","allowed_groups"])
def test_packets_bind_query_requirements_groups_to_frozen_gold(field):
    v = verifier()
    c,p,b,r = review_fixture()
    c["query"] = "Q"
    gold = {"intents":[dict(intent_id="i",query="Q",requirements=[dict(requirement_id="a",claim="body")],evidence_groups=[dict(requirements=["a"])])]}
    v.audit_gold_identity([c],[p],[b],gold)
    p[field] = "changed" if field=="query" else []
    with pytest.raises(ValueError,match="Gold"):
        v.audit_gold_identity([c],[p],[b],gold)


def test_provenance_requires_actual_cli_files_and_all_frozen_bindings(tmp_path):
    v = verifier()
    gold = tmp_path/"gold.json"
    gold.write_bytes(b"frozen gold")
    contexts = tmp_path/"contexts.jsonl"
    contexts.write_bytes(b"context")
    source = tmp_path/"frozen-source"
    source.write_bytes(b"source")
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    frozen = dict(gold_path=str(gold),gold_sha256=digest(gold),input_sha256={str(gold):digest(gold),str(source):digest(source)},old_assets_sha256={})
    bindings = [dict(path=str(gold),sha256=digest(gold))]
    with pytest.raises(ValueError,match="coverage"):
        v.audit_provenance_coverage(bindings,{"contexts":contexts,"gold":gold},frozen,tmp_path)
    bindings += [dict(path=str(contexts),sha256=digest(contexts)),dict(path=str(source),sha256=digest(source))]
    assert v.audit_provenance_coverage(bindings,{"contexts":contexts,"gold":gold},frozen,tmp_path) == 3
    frozen["gold_sha256"] = "wrong"
    with pytest.raises(ValueError,match="Gold"):
        v.audit_provenance_coverage(bindings,{"contexts":contexts,"gold":gold},frozen,tmp_path)


def cross_manifest_fixture(tmp_path):
    files = {}
    for name in ("contexts","packets","bindings","reviews","scores","gold","input_manifest","review_prompt","source_reviews"):
        files[name] = tmp_path / (name+".txt")
        files[name].write_bytes(name.encode())
    digest = lambda name: hashlib.sha256(files[name].read_bytes()).hexdigest()
    assembly = dict(input_manifest_sha256=digest("input_manifest"),output_sha256={files["input_manifest"].name:digest("input_manifest"),files["contexts"].name:digest("contexts")})
    export = dict(source_contexts_path=str(files["contexts"]),source_contexts_sha256=digest("contexts"),gold_path=str(files["gold"]),gold_sha256=digest("gold"),
                  artifacts={"packets.jsonl":digest("packets"),"bindings.jsonl":digest("bindings"),"review-prompt.txt":digest("review_prompt")},prompt_sha256=digest("review_prompt"))
    selected = dict(selected_reviews_sha256=digest("reviews"),packets_sha256=digest("packets"),source_reviews_sha256=digest("source_reviews"),prompt_sha256=digest("review_prompt"))
    score = dict(expected_n=20,output_path=str(files["scores"]),output_sha256=digest("scores"),input_artifacts={name:dict(path=str(files[name]),sha256=digest(name)) for name in ("contexts","packets","bindings","reviews")})
    return files,assembly,export,selected,score


def test_cross_manifest_actual_artifacts_and_denominator(tmp_path):
    v = verifier()
    files,*manifests = cross_manifest_fixture(tmp_path)
    assert v.audit_cross_manifests(files,*manifests,20) is True


@pytest.mark.parametrize("artifact",["contexts","input_manifest","gold","packets","bindings","reviews","scores","review_prompt","source_reviews"])
def test_synchronized_current_digest_cannot_replace_frozen_stage_identity(tmp_path,artifact):
    v = verifier()
    files,*manifests = cross_manifest_fixture(tmp_path)
    files[artifact].write_bytes(b"synchronized replacement")
    with pytest.raises(ValueError,match="manifest"):
        v.audit_cross_manifests(files,*manifests,20)


def test_score_manifest_bound_paths_and_selection_count(tmp_path):
    v = verifier()
    files,assembly,export,selected,score = cross_manifest_fixture(tmp_path)
    score["input_artifacts"]["reviews"]["path"] = str(files["source_reviews"])
    with pytest.raises(ValueError,match="manifest"):
        v.audit_cross_manifests(files,assembly,export,selected,score,20)
    score["input_artifacts"]["reviews"]["path"] = str(files["reviews"])
    with pytest.raises(ValueError,match="denominator"):
        v.audit_cross_manifests(files,assembly,export,selected,score,80)
