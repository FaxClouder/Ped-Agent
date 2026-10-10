"""Offline source support maps; anchor matching proposes locations, never labels."""
from __future__ import annotations
from assemble import digest, union_spans, subtract_spans, views_by_id
VERSION='source-support-r01'

def visible_support(visible_spans,mapping):
    visible=union_spans(visible_spans)
    result={}
    for req in mapping['requirements']:
        statuses=[]
        for group in req.get('evidence_groups',[]):
            complete=bool(group.get('necessary_spans')) and not subtract_spans(group['necessary_spans'],visible)
            reviewed=bool(group.get('reviewer_id')) and bool(group.get('rationale')) and group.get('status') in ('yes','no')
            statuses.append(group['status'] if complete and reviewed else 'unknown')
        result[req['requirement_id']]='yes' if 'yes' in statuses else 'no' if statuses and all(s=='no' for s in statuses) else 'unknown'
    return result

def export_source_support(gold,registry,legacy_review=None,views=None):
    """No inherited old chunk label: retain Gold requirements and mechanical candidates.

    legacy_review is deliberately not a semantic license. New reviewed source spans
    must be explicitly supplied with actual offline source review provenance.
    """
    vs=views_by_id(views) if views is not None else {}
    records=[]
    for intent in gold['intents']:
        atoms={a['atom_id']:a for a in intent['atoms']}
        requirements=[]
        for req in intent['requirements']:
            bundles=[]
            for bundle in req.get('support_bundles',[]):
                candidates=[]; unresolved=[]
                for aid in bundle:
                    atom=atoms[aid]; anchor=atom.get('anchor_text',''); hits=[]
                    for (doc,version),v in vs.items():
                        if doc!=atom['source_id'] or not anchor: continue
                        for e in v['elements']:
                            begin=e['text'].find(anchor)
                            while begin>=0:
                                hits.append(dict(doc_id=doc,source_version=version,element_id=e['element_id'],start=begin,end=begin+len(anchor)))
                                begin=e['text'].find(anchor,begin+1)
                    candidates.append(dict(atom_id=aid,anchor=anchor,locations=hits,unique=len(hits)==1))
                    if len(hits)!=1: unresolved.append(aid)
                bundles.append(dict(atom_ids=bundle,anchor_candidates=candidates,necessary_spans=[],status='unknown',reviewer_id=None,rationale=None,unresolved_atoms=unresolved))
            requirements.append(dict(requirement_id=req['requirement_id'],description=req['claim'],scope=req.get('scope'),evidence_groups=bundles))
        records.append(dict(intent_id=intent['intent_id'],query=intent['query'],main_stratum=intent['main_stratum'],requirements=requirements,groups=[g['requirements'] for g in intent['evidence_groups']],review_status='pending'))
    result=dict(schema_version=VERSION,gold_sha256=digest(gold),source_registry_sha256=digest(registry),legacy_chunk_labels_inherited=False,records=records)
    result['map_sha256']=digest(result)
    return result
