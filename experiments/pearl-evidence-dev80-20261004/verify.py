"""Independent Layer 2 scoring oracle; never imports the scoring implementation."""
import hashlib
import json
from pathlib import Path
from collections import Counter
from fractions import Fraction
from itertools import product
import math
import random
import sys

CONFIGURATIONS = ("C0-4096", "C0-8192", "C1-4096", "C1-8192")
PAIRS = (("C1-4096","C0-4096"),("C1-8192","C0-8192"),("C0-8192","C0-4096"),("C1-8192","C1-4096"))
PROMPT_SHA256 = "4554628c5f53fb465a33974e1dbef0606d741a031a2b42931f46b8786ec5e255"


def sha_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def audit_files(bindings, base=Path(".")):
    """Byte-only source preservation and artifact/code/configuration verification."""
    for entry in bindings:
        path = Path(entry["path"])
        if not path.is_absolute():
            path = Path(base) / path
        with path.open("rb") as stream:
            actual = hashlib.file_digest(stream, "sha256").hexdigest()
        if actual != entry["sha256"]:
            raise ValueError(f"SHA mismatch: {path}")
    return len(bindings)


def audit_contexts(rows, count_tokens, expected_intents=None, expected_types=None):
    keys = [(r["intent_id"], r["configuration"]) for r in rows]
    intents = set(expected_intents) if expected_intents is not None else {k[0] for k in keys}
    if len(keys) != len(set(keys)) or set(keys) != {(i, c) for i in intents for c in CONFIGURATIONS}:
        raise ValueError("incomplete or duplicate four-configuration matrix")
    type_by_intent = {}
    for row in rows:
        cfg = row["configuration"]
        if row["context_id"] != f'{row["intent_id"]}::{cfg}' or row["budget"] != int(cfg.split("-")[1]):
            raise ValueError("context/configuration/budget binding mismatch")
        text = row["serialized_context"]
        if sha_text(text) != row["text_sha256"]:
            raise ValueError("context text SHA mismatch")
        actual = count_tokens(text)
        if actual != row["token_count"] or actual > row["budget"]:
            raise ValueError("final serialized token count/budget mismatch")
        units = row["units"]
        if len({u["unit_id"] for u in units}) != len(units):
            raise ValueError("duplicate final unit")
        for unit in units:
            if unit["text_sha256"] != sha_text(unit["text"]):
                raise ValueError("unit text SHA mismatch")
        for step in row.get("steps", {}).values():
            if sha_text(step["serialized_context"]) != step["text_sha256"] or count_tokens(step["serialized_context"]) != step["token_count"]:
                raise ValueError("step text SHA/token mismatch")
        intent, typ = row["intent_id"], row["question_type"]
        if intent in type_by_intent and type_by_intent[intent] != typ:
            raise ValueError("question type drift between configurations")
        type_by_intent[intent] = typ
    counts = dict(Counter(type_by_intent.values()))
    if expected_types is not None and counts != expected_types:
        raise ValueError("question type/sample denominator mismatch")
    return {"contexts": len(rows), "intents": len(intents), "question_types": counts}


def oracle(groups, labels):
    if not groups or any(not group for group in groups):
        raise ValueError("empty evidence group")
    states = []
    for group in groups:
        values = [labels.get(requirement) for requirement in group]
        if any(value not in {"supported", "unsupported", "unknown"} for value in values):
            raise ValueError("missing or invalid requirement support")
        states.append("unsupported" if "unsupported" in values else "unknown" if "unknown" in values else "supported")
    return "supported" if "supported" in states else "unknown" if "unknown" in states else "unsupported"


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def unique_map(records, key):
    result = {key(r): r for r in records}
    if len(result) != len(records):
        raise ValueError("duplicate records")
    return result


def audit_gold_identity(contexts, packets, bindings, gold):
    """Compare only the query and sanitized requirement definitions to frozen Gold."""
    intents = unique_map(gold["intents"],lambda i:i["intent_id"])
    cmap = unique_map(contexts,lambda c:c["context_id"])
    pmap = unique_map(packets,lambda p:p["packet_id"])
    for context in contexts:
        intent = intents.get(context["intent_id"])
        if intent is None or context.get("query") != intent["query"]:
            raise ValueError("context query/intent differs from frozen Gold")
    for bound in bindings:
        if bound["context_id"] not in cmap or bound["packet_id"] not in pmap:
            raise ValueError("Gold binding references missing context/packet")
        intent = intents[cmap[bound["context_id"]]["intent_id"]]
        packet = pmap[bound["packet_id"]]
        requirements = [{k:r[k] for k in ("requirement_id","claim","scope") if k in r} for r in intent["requirements"]]
        groups = [g["requirements"] for g in intent["evidence_groups"]]
        if packet["query"] != intent["query"] or packet["requirements"] != requirements or packet["allowed_groups"] != groups:
            raise ValueError("packet query/requirements/groups differ from frozen Gold")
    return len(bindings)


def audit_provenance_coverage(bindings, cli_files, frozen, root):
    def absolute(path):
        path = Path(path)
        return (path if path.is_absolute() else Path(root)/path).resolve()
    def digest(path):
        with path.open("rb") as stream:
            return hashlib.file_digest(stream,"sha256").hexdigest()
    provided = unique_map(bindings,lambda b:absolute(b["path"]))
    gold = absolute(cli_files["gold"])
    if gold != absolute(frozen["gold_path"]) or digest(gold) != frozen["gold_sha256"]:
        raise ValueError("actual Gold path/SHA differs from frozen input manifest")
    required = {absolute(p):digest(absolute(p)) for p in cli_files.values()}
    for name in ("input_sha256","old_assets_sha256"):
        for path,sha in frozen.get(name,{}).items():
            resolved = absolute(path)
            if resolved in required and required[resolved] != sha:
                raise ValueError("actual CLI SHA differs from frozen input binding")
            required[resolved] = sha
    if gold not in {absolute(p) for p in frozen["input_sha256"]}:
        raise ValueError("Gold absent from frozen input bindings")
    if any(path not in provided or provided[path]["sha256"] != sha for path,sha in required.items()):
        raise ValueError("provenance coverage missing/wrong actual CLI or frozen file binding")
    audit_files(bindings,root)
    return len(required)


def audit_cross_manifests(files, assembly, exported, selected, scored, selection_count):
    """Require stage manifests to bind the actual artifacts, not current hashes alone."""
    paths = {name:Path(path).resolve() for name,path in files.items()}
    digest = lambda name: hashlib.sha256(paths[name].read_bytes()).hexdigest()
    def require_hash(expected, name, role):
        if expected != digest(name):
            raise ValueError(f"{role} manifest {name} SHA mismatch")
    def require_path(expected, name, role):
        if Path(expected).resolve() != paths[name]:
            raise ValueError(f"{role} manifest {name} path mismatch")
    require_hash(assembly["input_manifest_sha256"],"input_manifest","assembly")
    for name in ("contexts","input_manifest"):
        require_hash(assembly["output_sha256"].get(paths[name].name),name,"assembly")
    for name,prefix in (("contexts","source_contexts"),("gold","gold")):
        require_path(exported[prefix+"_path"],name,"export")
        require_hash(exported[prefix+"_sha256"],name,"export")
    for name,artifact in (("packets","packets.jsonl"),("bindings","bindings.jsonl"),("review_prompt","review-prompt.txt")):
        require_hash(exported["artifacts"].get(artifact),name,"export")
    require_hash(exported["prompt_sha256"],"review_prompt","export")
    require_hash(selected["prompt_sha256"],"review_prompt","selected")
    require_hash(selected["selected_reviews_sha256"],"reviews","selected")
    require_hash(selected["packets_sha256"],"packets","selected")
    if "source_reviews" in paths:
        require_hash(selected["source_reviews_sha256"],"source_reviews","selected")
    for name in ("contexts","packets","bindings","reviews"):
        entry = scored["input_artifacts"][name]
        require_path(entry["path"],name,"score")
        require_hash(entry["sha256"],name,"score")
    require_path(scored["output_path"],"scores","score")
    require_hash(scored["output_sha256"],"scores","score")
    if scored["expected_n"] != selection_count:
        raise ValueError("score manifest denominator differs from frozen selection")
    return True


def recompute_rows(contexts, packets, bindings, reviews, gold=None):
    """Check all stage bindings/reviews, then score final views independently."""
    cmap = unique_map(contexts, lambda x: x["context_id"])
    pmap = unique_map(packets, lambda x: x["packet_id"])
    rmap = unique_map(reviews, lambda x: x["packet_id"])
    bmap = unique_map(bindings, lambda x: (x["context_id"], x["stage"]))
    if gold is not None:
        audit_gold_identity(contexts,packets,bindings,gold)
    required_views = {(c["context_id"],stage) for c in contexts for stage in ["final",*c.get("steps",{})]}
    if set(bmap) != required_views:
        raise ValueError("missing/extra step binding")
    if set(pmap) != set(rmap) or {b["packet_id"] for b in bindings} != set(pmap):
        raise ValueError("incomplete/extraneous selected reviews or packets")
    for p in packets:
        body = {k: v for k, v in p.items() if k not in {"packet_id", "packet_sha256"}}
        digest = sha_text(canonical(body))
        if digest != p["packet_sha256"] or p["packet_id"] != "packet-" + digest[:24]:
            raise ValueError("packet content SHA mismatch")
        r = rmap[p["packet_id"]]
        if r["packet_sha256"] != digest:
            raise ValueError("selected review SHA mismatch")
        required = {x["requirement_id"] for x in p["requirements"]}
        if len(required) != len(p["requirements"]) or set(r["support"]) != required:
            raise ValueError("missing/extra requirement review")
        if set().union(*map(set, p["allowed_groups"])) != required:
            raise ValueError("requirement/group mismatch")
        for j in r["support"].values():
            if j["label"] not in {"yes", "no", "unknown"} or not j.get("rationale"):
                raise ValueError("invalid review judgment")
            quotes = j.get("quotes", [])
            if (j["label"] == "yes" and not quotes) or any(not q or q not in p["serialized_context"] for q in quotes):
                raise ValueError("review quotation not bound to final text")
        if set(r["unit_labels"]) != {u["unit_id"] for u in p["units"]} or any(x not in {"relevant", "irrelevant", "mixed", "unknown"} for x in r["unit_labels"].values()):
            raise ValueError("invalid/missing unit review")
    for b in bindings:
        if b["context_id"] not in cmap or b["packet_id"] not in pmap:
            raise ValueError("binding references missing context or packet")
        c = cmap[b["context_id"]]
        view = c if b["stage"] == "final" else c.get("steps", {}).get(b["stage"])
        if view is None or b["intent_id"] != c["intent_id"]:
            raise ValueError("binding stage/intent mismatch")
        original = view["serialized_context"]
        if sha_text(original) != view["text_sha256"] or b["original_text_sha256"] != view["text_sha256"]:
            raise ValueError("original text binding mismatch")
        p = pmap[b["packet_id"]]
        if b["packet_sha256"] != p["packet_sha256"]:
            raise ValueError("packet binding mismatch")
        chunks = [f"[Source {u['source_id']} | {u['locator']}]\nTitle: {u['title']}\n{u['text']}" for u in view["units"]]
        if "\n\n".join(chunks) != original:
            raise ValueError("original serialization mismatch")
        anonymous = [f"[Source {b['source_map'][u['source_id']]} | {u['locator']}]\nTitle: {u['title']}\n{u['text']}" for u in view["units"]]
        blinded = "\n\n".join(anonymous)
        if blinded != p["serialized_context"] or sha_text(blinded) != b["blinded_text_sha256"]:
            raise ValueError("blinded text binding mismatch")
        expected_map = [dict(occurrence_index=i, original_unit_id=u["unit_id"], blind_unit_id=f"U{i+1}") for i,u in enumerate(view["units"])]
        if b["unit_map"] != expected_map or not {u["source_id"] for u in view["units"]} <= set(b["source_map"]):
            raise ValueError("unit/source binding mismatch")
        expected_units = []
        offset = 0
        for i,(u,chunk) in enumerate(zip(view["units"], anonymous)):
            expected_units.append(dict(unit_id=f"U{i+1}",source_id=b["source_map"][u["source_id"]],text_sha256=sha_text(u["text"]),character_start=offset,character_end=offset+len(chunk)))
            offset += len(chunk)+2
        if p["units"] != expected_units:
            raise ValueError("packet unit text/order mismatch")
    rows = []
    for c in contexts:
        if (c["context_id"], "final") not in bmap:
            raise ValueError("missing final review binding")
        p = pmap[bmap[c["context_id"], "final"]["packet_id"]]
        r = rmap[p["packet_id"]]
        support = {k: j["label"] for k, j in r["support"].items()}
        translation = {"yes": "supported", "no": "unsupported", "unknown": "unknown"}
        state = oracle(p["allowed_groups"], {k: translation[x] for k, x in support.items()})
        limits = []
        for group in p["allowed_groups"]:
            if len(group) != len(set(group)):
                raise ValueError("duplicate group requirement")
            limits.append((Fraction(sum(support[x] == "yes" for x in group), len(group)), Fraction(sum(support[x] != "no" for x in group), len(group))))
        rows.append({k: c[k] for k in ("context_id", "intent_id", "configuration", "question_type", "text_sha256")} | {
            "packet_id": p["packet_id"], "support": support, "unit_labels": [r["unit_labels"][u["unit_id"]] for u in p["units"]],
            "sufficient": {"supported": "yes", "unsupported": "no", "unknown": "unknown"}[state],
            "coverage_lower": float(max(x[0] for x in limits)), "coverage_upper": float(max(x[1] for x in limits))})
    return rows


def independent_aggregate(rows):
    n = len(rows)
    labels = Counter(r["sufficient"] for r in rows)
    active = [r for r in rows if r["unit_labels"]]
    out = {"n": n, **{x: labels[x] for x in ("yes", "no", "unknown")},
           "complete_group_lower": labels["yes"] / n if n else None,
           "complete_group_upper": (n-labels["no"]) / n if n else None,
           "coverage_lower": math.fsum(r["coverage_lower"] for r in rows) / n if n else None,
           "coverage_upper": math.fsum(r["coverage_upper"] for r in rows) / n if n else None,
           "relevance_applicable_n": len(active), "unit_n": sum(len(r["unit_labels"]) for r in active),
           "unknown_unit_n": sum(r["unit_labels"].count("unknown") for r in active)}
    for name, positive in (("relevance", {"relevant", "mixed"}), ("noise", {"irrelevant", "mixed"})):
        ratios = [(Fraction(sum(x in positive for x in r["unit_labels"]), len(r["unit_labels"])),
                   Fraction(sum(x in positive or x == "unknown" for x in r["unit_labels"]), len(r["unit_labels"]))) for r in active]
        for j, suffix in enumerate(("lower", "upper")):
            out[name+"_"+suffix] = float(sum(pair[j] for pair in ratios)/len(ratios)) if ratios else None
    return out


def recompute_statistics(rows):
    lookup = unique_map(rows, lambda r: (r["intent_id"], r["configuration"]))
    ids = sorted({r["intent_id"] for r in rows})
    if set(lookup) != set(product(ids, CONFIGURATIONS)):
        raise ValueError("incomplete scoring matrix")
    paired = []
    for a,b in (("C1-4096", "C0-4096"), ("C1-8192", "C0-8192"), ("C0-8192", "C0-4096"), ("C1-8192", "C1-4096")):
        transitions = Counter((lookup[i,a]["sufficient"], lookup[i,b]["sufficient"]) for i in ids)
        gain, loss = transitions["yes", "no"], transitions["no", "yes"]
        unknown = sum(v for pair,v in transitions.items() if "unknown" in pair)
        differences = []
        for av,bv in ((lookup[i,a]["sufficient"], lookup[i,b]["sufficient"]) for i in ids):
            outcomes = [{"yes": [1], "no": [0], "unknown": [0,1]}[v] for v in (av,bv)]
            values = [x-y for x,y in product(*outcomes)]
            differences.append((min(values), max(values)))
        discordant = gain+loss
        probability = min(1., float(Fraction(2 * sum(math.comb(discordant, k) for k in range(min(gain,loss)+1)), 2**discordant))) if discordant else 1.
        paired.append(dict(a=a,b=b,n=len(ids),unknown_pairs=unknown,resolved_pairs=len(ids)-unknown,gain=gain,loss=loss,
                           delta_lower=sum(d[0] for d in differences)/len(ids),delta_upper=sum(d[1] for d in differences)/len(ids),exact_mcnemar_p_resolved=probability))
    ordered = sorted(paired, key=lambda p: p["exact_mcnemar_p_resolved"])
    ceiling = 0.
    for rank, pair in enumerate(ordered):
        ceiling = max(ceiling, min(1., (len(ordered)-rank)*pair["exact_mcnemar_p_resolved"]))
        pair["holm_p_resolved"] = ceiling
    return {"overall": {c: independent_aggregate([r for r in rows if r["configuration"] == c]) for c in CONFIGURATIONS},
            "by_type": {t: {c: independent_aggregate([r for r in rows if r["configuration"] == c and r["question_type"] == t]) for c in CONFIGURATIONS} for t in sorted({r["question_type"] for r in rows})}, "paired": paired}


def recompute_attribution(rows):
    views = unique_map(rows, lambda r: (r["context_id"], r["stage"]))
    result = []
    for cid in sorted({r["context_id"] for r in rows}):
        for before, after in zip(("raw", "expanded", "deduplicated"), ("expanded", "deduplicated", "final")):
            if (cid,before) not in views or (cid,after) not in views:
                continue
            left, right = views[cid,before], views[cid,after]
            if set(left["support"]) != set(right["support"]):
                raise ValueError("attribution requirement drift")
            changes = {r:(left["support"][r],right["support"][r]) for r in left["support"]}
            result.append(dict(context_id=cid,before_stage=before,after_stage=after,
                before_status=left["sufficient"],after_status=right["sufficient"],
                requirement_gains=sorted(k for k,pair in changes.items() if pair == ("no","yes")),
                requirement_losses=sorted(k for k,pair in changes.items() if pair == ("yes","no")),
                unknown_requirements=sorted(k for k,pair in changes.items() if "unknown" in pair)))
    return result


def audit_selected(reviews, manifest):
    if manifest.get("prompt_sha256") != PROMPT_SHA256:
        raise ValueError("selected review prompt SHA differs from frozen prompt")
    selected = unique_map(manifest["selected"], lambda r: r["packet_id"])
    actual = unique_map(reviews, lambda r: r["packet_id"])
    if set(selected) != set(actual):
        raise ValueError("selected manifest incomplete")
    for pid,r in actual.items():
        elapsed = r.get("elapsed_seconds")
        if r.get("full_read") is not True or not r.get("reviewer_id") or not r.get("model_id") or r.get("prompt_sha256") != manifest.get("prompt_sha256") or "elapsed_seconds" not in r or (elapsed is not None and (not isinstance(elapsed,(int,float)) or isinstance(elapsed,bool) or not math.isfinite(elapsed) or elapsed < 0)):
            raise ValueError("selected per-review provenance invalid")
        entry = selected[pid]
        if entry["packet_sha256"] != r["packet_sha256"] or entry["review_content_sha256"] != sha_text(canonical(r)):
            raise ValueError("selected review content SHA mismatch")
    return len(actual)


def independent_bootstrap(rows):
    """Independent integer cluster resampling from the frozen statistical supplement."""
    lookup = unique_map(rows,lambda r:(r["intent_id"],r["configuration"]))
    ids = sorted({r["intent_id"] for r in rows})
    if not ids or set(lookup) != set(product(ids,CONFIGURATIONS)):
        raise ValueError("bootstrap requires complete nonempty cluster matrix")
    strata = {}
    encoded = {}
    for intent in ids:
        types = {lookup[intent,c]["question_type"] for c in CONFIGURATIONS}
        if len(types) != 1:
            raise ValueError("bootstrap question type drift")
        strata.setdefault(types.pop(),[]).append(intent)
        values = []
        for cfg in CONFIGURATIONS:
            state = lookup[intent,cfg]["sufficient"]
            if state not in {"yes","no","unknown"}:
                raise ValueError("bootstrap invalid judgment")
            values.extend((int(state=="yes"),int(state!="no")))
        for a,b in PAIRS:
            ai,bi = CONFIGURATIONS.index(a)*2,CONFIGURATIONS.index(b)*2
            values.extend((values[ai]-values[bi+1],values[ai+1]-values[bi]))
        encoded[intent] = values
    groups = [strata[t] for t in sorted(strata)]
    generator = random.Random(20261004)
    distributions = [[] for _ in range(16)]
    for _ in range(10000):
        multiplicities = Counter(generator.choice(group) for group in groups for _ in range(len(group)))
        for j in range(16):
            distributions[j].append(sum(encoded[i][j]*k for i,k in multiplicities.items())/len(ids))
    points = [sum(encoded[i][j] for i in ids)/len(ids) for j in range(16)]
    def interval(j):
        limits = []
        for distribution in distributions[j:j+2]:
            ordered = sorted(distribution)
            pair = []
            for q in (.025,.975):
                position = 9999*q
                lo = int(position)
                weight = position-lo
                pair.append(ordered[lo]*(1-weight)+ordered[lo+1]*weight)
            limits.append(pair)
        return dict(lower_bound_point=points[j],upper_bound_point=points[j+1],lower_bound_ci=limits[0],upper_bound_ci=limits[1],envelope=[limits[0][0],limits[1][1]])
    folder = Path(__file__).parent
    return dict(statistics_version="layer2-stratified-paired-bootstrap-r01",confidence_level=.95,
        replicates=10000,seed=20261004,n=len(ids),stratum_sizes={t:len(strata[t]) for t in sorted(strata)},
        resampling_unit="underlying_intent_cluster",quantile_method="linear_interpolation_(B-1)*q",
        purpose="pre-summary descriptive uncertainty envelopes; not additional hypothesis tests",
        python_version=sys.version.split()[0],score_code_sha256=hashlib.sha256((folder/"score.py").read_bytes()).hexdigest(),
        statistics_supplement_sha256=hashlib.sha256((folder/"statistics-supplement.md").read_bytes()).hexdigest(),
        overall={c:interval(j*2) for j,c in enumerate(CONFIGURATIONS)},
        paired=[dict(a=a,b=b,**interval(8+j*2)) for j,(a,b) in enumerate(PAIRS)])


def audit_bootstrap(rows,saved):
    assert_same(independent_bootstrap(rows),saved,"bootstrap_ci")
    return True


def assert_same(actual, expected, path="score"):
    if isinstance(actual, dict) and isinstance(expected, dict):
        if set(actual) != set(expected):
            raise ValueError(f"{path} keys mismatch")
        for key in actual:
            assert_same(actual[key],expected[key],path+"."+str(key))
    elif isinstance(actual, list) and isinstance(expected, list):
        if len(actual) != len(expected):
            raise ValueError(f"{path} length mismatch")
        for i,(a,b) in enumerate(zip(actual,expected)):
            assert_same(a,b,path+"."+str(i))
    elif isinstance(actual, float) and isinstance(expected, (int,float)):
        if not math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12):
            raise ValueError(f"{path} numerical mismatch")
    elif actual != expected:
        raise ValueError(f"{path} value mismatch")


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def audit_saved(paths, count_tokens, expected_intents, expected_types, tokenizer_fingerprint=None, gold=None):
    data = {name: read_jsonl(paths[name]) for name in ("contexts", "packets", "bindings", "reviews")}
    report = audit_contexts(data["contexts"],count_tokens,expected_intents,expected_types)
    if tokenizer_fingerprint is not None and any(c.get("tokenizer_fingerprint") != tokenizer_fingerprint for c in data["contexts"]):
        raise ValueError("tokenizer fingerprint mismatch")
    rows = recompute_rows(**data,gold=gold)
    saved = json.loads(Path(paths["scores"]).read_text(encoding="utf-8"))
    assert_same(rows,saved["rows"])
    stats = recompute_statistics(rows)
    for name,value in stats.items():
        assert_same(value,saved[name])
    if "bootstrap_ci" not in saved:
        raise ValueError("bootstrap_ci missing")
    audit_bootstrap(rows,saved["bootstrap_ci"])
    if "step_rows" in saved or "attribution" in saved:
        steps = []
        for c in data["contexts"]:
            for stage,view in [*c.get("steps",{}).items(), ("final",c)]:
                cid = c["context_id"]
                bound = [b for b in data["bindings"] if b["context_id"] == cid and b["stage"] == stage]
                if not bound:
                    raise ValueError("missing step binding")
                fake = dict(c,serialized_context=view["serialized_context"],text_sha256=view["text_sha256"],units=view["units"],steps={})
                subset = dict(bound[0],stage="final")
                packet = next(p for p in data["packets"] if p["packet_id"] == subset["packet_id"])
                review = next(r for r in data["reviews"] if r["packet_id"] == subset["packet_id"])
                scored = recompute_rows([fake],[packet],[subset],[review])[0]
                steps.append({k:scored[k] for k in ("context_id","packet_id","text_sha256","support","sufficient","coverage_lower","coverage_upper")} | {"stage":stage})
        assert_same(steps,saved["step_rows"])
        assert_same(recompute_attribution(steps),saved["attribution"])
    elif any(c.get("steps") for c in data["contexts"]):
        raise ValueError("missing saved step scores/attribution")
    report.update(score_rows=len(rows),packets=len(data["packets"]),reviews=len(data["reviews"]),
                  independent_scores_match=True,independent_statistics_match=True,independent_bootstrap_match=True)
    return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("contexts","packets","bindings","reviews","scores","tokenizer","tokenizer-sha256","provenance","selected-review-manifest","expected-intents","expected-types","gold","input-manifest","assembly-manifest","export-manifest","score-manifest","output"):
        parser.add_argument("--"+name,required=True)
    parser.add_argument("--review-prompt")
    parser.add_argument("--source-reviews")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    import sys
    sys.path.insert(0,str(repo/"Knowledge-Base/src"))
    from ped_knowledge.tokenization import HuggingFaceTokenCounter
    counter = HuggingFaceTokenCounter.from_local_path(Path(args.tokenizer),expected_sha256=args.tokenizer_sha256)
    selection = json.loads(Path(args.expected_intents).read_text(encoding="utf-8"))
    ids = selection["intent_ids"] if isinstance(selection,dict) else selection
    types = json.loads(Path(args.expected_types).read_text(encoding="utf-8"))
    provenance = json.loads(Path(args.provenance).read_text(encoding="utf-8"))
    bindings = provenance["file_bindings"]
    if not bindings:
        raise ValueError("nonempty provenance file bindings required")
    frozen = json.loads(Path(args.input_manifest).read_text(encoding="utf-8"))
    cli_files = {name:getattr(args,name) for name in ("contexts","packets","bindings","reviews","scores","tokenizer","selected_review_manifest","expected_intents","expected_types","gold","input_manifest","assembly_manifest","export_manifest","score_manifest")}
    cli_files["review_prompt"] = args.review_prompt or str(Path(args.export_manifest).parent/"review-prompt.txt")
    if hashlib.sha256(Path(cli_files["review_prompt"]).read_bytes()).hexdigest() != PROMPT_SHA256:
        raise ValueError("actual review prompt differs from frozen SHA")
    if args.source_reviews:
        cli_files["source_reviews"] = args.source_reviews
    files_checked = audit_provenance_coverage(bindings,cli_files,frozen,repo)
    manifests = [json.loads(Path(path).read_text(encoding="utf-8")) for path in (args.assembly_manifest,args.export_manifest,args.selected_review_manifest,args.score_manifest)]
    audit_cross_manifests(cli_files,*manifests,len(ids))
    paths = {name:getattr(args,name) for name in ("contexts","packets","bindings","reviews","scores")}
    gold = json.loads(Path(args.gold).read_text(encoding="utf-8"))
    report = audit_saved(paths,counter.count,ids,types,counter.fingerprint,gold)
    selected = json.loads(Path(args.selected_review_manifest).read_text(encoding="utf-8"))
    report["selected_reviews_checked"] = audit_selected(read_jsonl(args.reviews),selected)
    report.update(file_sha_bindings_checked=files_checked,tokenizer_sha256=args.tokenizer_sha256,
                  cross_manifest_bindings_verified=True,
                  verification_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  status="verified",scope="Layer 2 development; structural/statistical audit, no semantic rejudgment")
    with Path(args.output).open("x",encoding="utf-8") as stream:
        json.dump(report,stream,ensure_ascii=False,indent=2)
    # Reopen the newly saved audit result before reporting completion.
    assert_same(report,json.loads(Path(args.output).read_text(encoding="utf-8")),"verification output")
    print(json.dumps(report,ensure_ascii=False))


if __name__ == "__main__":
    main()
