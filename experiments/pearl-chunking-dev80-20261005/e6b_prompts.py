"""Frozen judge prompt assembly for Session 6B (shared by calibration and research packets).

The scientific instructions are the frozen Layer 3 / Layer 4 judge prompts, rubrics and the
Layer 4 r02 citation addendum, inserted verbatim. Only an output-format section is added for the
API runtime (harness r01). It changes no label definition, rubric or threshold. Character offsets
are located mechanically from the judge's exact quoted text (all occurrences, the rubric's
duplicate rule), because a stateless API model cannot run code to count offsets.
"""
from __future__ import annotations
import json
import re
from runtime import ROOT

L3_PROMPT=ROOT/'experiments/pearl-answer-dev80-20261004/judge-prompt-r01.md'
L3_RUBRIC=ROOT/'experiments/pearl-answer-dev80-20261004/rubrics.md'
L4_PROMPT=ROOT/'experiments/pearl-layer4-dev80-20261004/judge-prompt-r01.md'
L4_RUBRIC=ROOT/'experiments/pearl-layer4-dev80-20261004/rubrics.md'
L4_ADDENDUM=ROOT/'outputs/pearl-layer4-dev80-20261004-01/calibration/context-judge-prompt-addendum-r02.json'
HARNESS_VERSION='harness-r01'
UNIT_STRINGS=['m/s','cm/s','km/h','people','persons','pedestrians','%','fraction','proportion','percentage_points','people/m2','ped/m2',
              'people/m','ped/m','people/s','ped/s','people/min','ped/min','persons/(m*s)','m','cm','1/m','s','min','degrees','m/s2',
              'm2/person','cm2/person','dimensionless','integer','years']


def read(p):return p.read_text(encoding='utf8')


L3_FORMAT='''# Output format (API harness r01; does not change any rule above)
Return exactly one JSON object and nothing else:
{"packet_id": "<packet_id>",
 "decision": {"targets": {"<target id>": "correct|incorrect|missing|unknown"},
              "conditions": {"<condition id>": "correct|incorrect|missing|unknown"},
              "claims": {"<claim id>": "correct|incorrect|missing|unknown"},
              "contradiction": true | false | "unknown",
              "refusal": true | false,
              "integration": "yes|no|unknown|na",
              "numeric": {"<numeric target id>": {"status": "parsed|missing|unknown", "value": <number or null>, "unit": "<unit or null>"}}},
 "unknown_reasons": {"<id>": "<specific semantic ambiguity>"},
 "rationale": "<concise rationale>"}
Label every key target, required condition and claim ID listed in the reference, and every numeric target ID.
For a parsed numeric value give the value in the unit actually expressed by the answer, written with one of these
unit strings when the answer's unit is equivalent to one of them: ''' + ', '.join(UNIT_STRINGS) + '''.
If the answer's unit is none of these, copy the answer's unit verbatim. Do not convert an incorrect unit into the reference unit.'''

L4_FORMAT={
 'answerability':'''# Output format (API harness r01)
Return exactly one JSON object: {"anchor_id": "<id from packet, or blind_id>", "answerability": "complete|partial|none|unknown",
 "reason": "<position-bound reason quoting the supporting or missing context>"}''',
 'grounding':'''# Output format (API harness r01)
Return exactly one JSON object:
{"anchor_id": "<id from packet, or blind_id>",
 "claims": [{"claim_id": "<keep the candidate claim_id when a candidate is kept unchanged; new or split claims get the next ids c<n> in answer order>",
             "text": "<exact verbatim substring of raw_answer for this claim>",
             "other_occurrence_texts": ["<exact verbatim substring of raw_answer for each further, differently worded duplicate occurrence of the same fact>"],
             "normalized_claim": "<normalized claim>", "conditions": "<conditions retained>",
             "label": "supported|partial|unsupported|contradicted|unknown",
             "context_evidence": [{"quote": "<exact verbatim context quote>", "source_label": "<source label as in the context>"}],
             "reason": "<reason>"}],
 "citation_pairs": [{"claim_id": "<claim id>", "citation_text": "<exact verbatim citation string from raw_answer>",
                     "citation_occurrence": <1-based index of this citation string among identical citation strings in raw_answer>,
                     "source_id": "<cited source id>", "label": "supported|partial|unsupported|contradicted|unknown|invalid|outside-context",
                     "reason": "<reason>"}],
 "extraction_unknown": false, "citation_extraction_unknown": false, "reason": "<overall note>"}
Every text and citation_text must be copied character-for-character from raw_answer; the program locates character offsets
from them (all identical occurrences are recorded). Do not output offsets.''',
 'factuality':'''# Output format (API harness r01)
Return exactly one JSON object: {"anchor_id": "<id from packet, or blind_id>",
 "claims": [{"claim_id": "<claim id from packet>", "label": "true|false|unknown",
             "fact_evidence": [{"quote": "<exact verbatim quote from the independent fact source>", "source_id": "<source id>"}],
             "reason": "<reason>"}]}
Label every claim in the packet.''',
 'behavior':'''# Output format (API harness r01)
Return exactly one JSON object: {"anchor_id": "<id from packet, or blind_id>",
 "behavior": "full_answer|bounded_partial|pure_abstain|ambiguous",
 "abstains_from_unsupported_completion": true | false, "unsupported_completion": true | false,
 "refusal_reason": "correct" | "incorrect" | "unknown" | null, "reason": "<reason>"}'''}


def layer3_messages(packet):
    system=read(L3_PROMPT)+'\n\n'+read(L3_RUBRIC)+'\n\n'+L3_FORMAT
    return [{'role':'system','content':system},{'role':'user','content':'Packet (JSON):\n'+json.dumps(packet,ensure_ascii=False,indent=1)}]


def layer4_messages(packet,task):
    addendum=json.loads(read(L4_ADDENDUM))
    system=(read(L4_PROMPT)+'\n\n'+read(L4_RUBRIC)+'\n\n# 引用归属补充 r02\n'+addendum['rule']+'\n\n# 本次任务\n'+task+'\n\n'+L4_FORMAT[task])
    return [{'role':'system','content':system},{'role':'user','content':'Packet (JSON):\n'+json.dumps(packet,ensure_ascii=False,indent=1)}]


def all_occurrences(haystack,needle):
    if not needle:return []
    spans=[];start=0
    while True:
        i=haystack.find(needle,start)
        if i<0:return spans
        spans.append([i,i+len(needle)]);start=i+len(needle)


def locate_grounding(parsed,raw_answer):
    """Mechanical offset location from the judge's verbatim quotes; no semantic change."""
    out=dict(parsed);claims=[];problems=[]
    for c in parsed.get('claims',[]) or []:
        texts=[c.get('text') or '']+[t for t in (c.get('other_occurrence_texts') or []) if t]
        occ=[]
        for t in texts:
            found=all_occurrences(raw_answer,t)
            if not found:problems.append({'claim_id':c.get('claim_id'),'text_not_found':t[:120]})
            occ+=found
        claims.append({**c,'occurrences':sorted({tuple(o) for o in occ})})
    for c in claims:c['occurrences']=[list(o) for o in c['occurrences']]
    pairs=[]
    for p in parsed.get('citation_pairs',[]) or []:
        found=all_occurrences(raw_answer,p.get('citation_text') or '')
        k=p.get('citation_occurrence') or 1
        span=found[k-1] if isinstance(k,int) and 1<=k<=len(found) else None
        if span is None:problems.append({'claim_id':p.get('claim_id'),'citation_not_located':(p.get('citation_text') or '')[:120]})
        pairs.append({**p,'citation_span':span or []})
    out['claims']=claims;out['citation_pairs']=pairs;out['location_problems']=problems
    return out


def normalize_behavior(parsed):
    out=dict(parsed)
    if out.get('refusal_reason') in ('null','None','na','NA',''):out['refusal_reason']=None
    return out
