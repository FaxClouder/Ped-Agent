"""Identity-normalized Unicode source view; separators have no evidence identity."""
import hashlib
import json


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf8")).hexdigest()


def text_hash(text):
    return hashlib.sha256(text.encode("utf8")).hexdigest()


def array(value):
    return json.loads(value) if isinstance(value, str) else list(value or [])


def make_span(element, start=0, end=None):
    return {k: element[k] for k in ("doc_id", "source_version", "element_id")} | {"start": start, "end": len(element["text"]) if end is None else end}


def build_source_view(doc, view_config=None):
    if hasattr(doc, "model_dump"):
        doc = doc.model_dump(mode="json")
    version = doc.get("source_version", doc.get("source_hash", doc.get("version_id")))
    doc_id = doc.get("doc_id", "pearl-src-" + str(version)[:16])
    elements, separators, runs, current, cursor = [], [], [], [], 0
    for raw in sorted(array(doc["elements"]), key=lambda e: e.get("order", 0)):
        e = dict(raw)
        if not e.get("text"):
            continue
        e.update(doc_id=doc_id, source_version=version, heading_path=array(e.get("heading_path")))
        if e.get("table_data") is not None:
            e["table_data"] = array(e["table_data"])
        if any(x["element_id"] == e["element_id"] for x in elements):
            raise ValueError("duplicate element identity")
        e["span"] = make_span(e)
        if elements:
            separators.append({"start": cursor, "end": cursor + 2, "text": "\n\n", "evidence": False})
            cursor += 2
        e["view_start"], e["view_end"] = cursor, cursor + len(e["text"])
        cursor = e["view_end"]
        elements.append(e)
        if e["element_type"] == "table":
            if current:
                runs.append(current)
                current = []
            runs.append([e["element_id"]])
        else:
            current.append(e["element_id"])
    if current:
        runs.append(current)
    result = dict(doc_id=doc_id, source_version=version, elements=elements,
                  paragraphs=[e for e in elements if e["element_type"] != "table"],
                  barrier_runs=runs, separator_map=separators,
                  source_text="\n\n".join(e["text"] for e in elements),
                  title=doc.get("title"),
                  config={"version": "identity-unicode-v1", "normalization": "none", "separator": "\n\n"} | (view_config or {}))
    if result["config"]["normalization"] != "none":
        raise ValueError("source normalization must remain identity")
    result["view_sha256"] = digest(result)
    return result


def text_for_spans(views, spans):
    if isinstance(views, dict):
        views = [views] if "elements" in views else list(views.values())
    lookup = {(e["doc_id"], e["source_version"], e["element_id"]): e for v in views for e in v["elements"]}
    parts, previous = [], None
    for s in spans:
        key = tuple(s[k] for k in ("doc_id", "source_version", "element_id"))
        e = lookup[key]
        if not 0 <= s["start"] <= s["end"] <= len(e["text"]):
            raise ValueError("source span outside raw Unicode text")
        if parts and (previous[0] != key or previous[1] != s["start"]):
            parts.append("\n\n")
        parts.append(e["text"][s["start"]:s["end"]])
        previous = (key, s["end"])
    return "".join(parts)


def resolve_legacy_span(child, parent, view):
    text = child.get("text", child.get("source_text", ""))
    candidates = []
    ids = array(child.get("element_ids")) if child.get("element_ids") else None
    for e in view["elements"]:
        if ids and e["element_id"] not in ids:
            continue
        start = 0
        while text and (found := e["text"].find(text, start)) >= 0:
            candidates.append(make_span(e, found, found + len(text)))
            start = found + 1
    return {"status": "unique" if len(candidates) == 1 else "ambiguous" if candidates else "unresolved", "candidates": candidates, "semantic_support": "unknown"}
