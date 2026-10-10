"""Build the E4 r12 common support map as a strict extension of E2 r11 plus its lineage.

Same integration semantics as e2_integrate_r11.py; additionally honours
excluded_outside_indices (ambiguous segments are not added to the reviewed universe).
Nothing from r11 is removed or rewritten; the strict-extension check is reused.
"""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
from runtime import ROOT, sha, save_json
from assemble import union_spans
from e2_integrate_r11 import strict_extension

E2=ROOT/'outputs/pearl-chunking-dev80-20261006-12'
OUT=ROOT/'outputs/pearl-chunking-dev80-20261006-13'

def load(p):return json.loads(Path(p).read_text('utf8'))

def main():
    base_path=E2/'common-support-map-e2-r11.json';base=load(base_path);new=copy.deepcopy(base)
    results=load(OUT/'review-results-e4-r12.json');assert results['base_mapping_sha256']==sha(base_path)
    export=load(OUT/'review-export-e4-r12.json');packets={p['packet_id']:p for p in export['packets']}
    recs={r['intent_id']:r for r in new['records']};accepted=[]
    for d in results['results']:
        pk=load(OUT/'review-packets-e4-r12'/f"{d['packet_id']}.json")
        assert pk['packet_sha256']==d['packet_sha256']==packets[d['packet_id']]['packet_sha256'] and not d['new_alternatives'] and not d['create_visible_universe_review']
        q=next(x for x in recs[d['intent_id']]['requirements'] if x['requirement_id']==d['requirement_id'])
        spans=[s['span'] for i,s in enumerate(pk['outside_segments']) if i not in set(d['excluded_outside_indices'])]
        ext=dict(revision='e4-r12',reviewer_id=d['reviewer_id'],packet_sha256=d['packet_sha256'],reviewed_text_sha256=d['reviewed_text_sha256'],
                 status='no_support_in_reviewed_segments',universe_expanded=bool(spans),rationale=d['outside_rationale'],kept_unknown=d['kept_unknown'],
                 excluded_ambiguous_segments=[pk['outside_segments'][i]['span'] for i in d['excluded_outside_indices']],human_verified=False)
        v=q['visible_universe_review']
        if spans:v['universe_spans']=union_spans(v['universe_spans']+spans)
        v.setdefault('review_extensions',[]).append(ext)
        for adj in d['uncertain_adjudications']:
            u=v['uncertain'][adj['index']]
            u.setdefault('adjudicated_variants',[]).append(dict(verdict=adj['verdict'],source_spans=adj['source_spans'],rationale=adj['rationale'],reviewer_id=d['reviewer_id'],packet_sha256=d['packet_sha256'],revision='e4-r12'))
        accepted.append(dict(packet_id=d['packet_id'],intent_id=d['intent_id'],requirement_id=d['requirement_id'],universe_segments_added=len(spans),excluded_ambiguous=len(d['excluded_outside_indices']),
            uncertain_adjudications=len(d['uncertain_adjudications']),new_alternatives=0,kept_unknown=bool(d['kept_unknown'])))
    strict_extension(base,new)
    records_sha=hashlib.sha256(json.dumps(new['records'],ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    new.update(e4_revision='r12',schema_version='source-support-map-e4-r12',previous_map_sha256=base['map_sha256'],map_sha256=records_sha,human_verified=False,
               e4_supplement_review=dict(results_sha256=sha(OUT/'review-results-e4-r12.json'),export_sha256=sha(OUT/'review-export-e4-r12.json'),reviewer_id=results['reviewer_id'],rule=results['rule']))
    target=OUT/'common-support-map-e4-r12.json';save_json(target,new)
    save_json(OUT/'map-lineage-e4-r12.json',dict(base_mapping_path=base_path.relative_to(ROOT).as_posix(),base_mapping_sha256=sha(base_path),new_mapping_sha256=sha(target),previous_map_sha256=base['map_sha256'],new_map_records_sha256=records_sha,
        review_results_sha256=sha(OUT/'review-results-e4-r12.json'),review_export_sha256=sha(OUT/'review-export-e4-r12.json'),packets_sha256={k:v['packet_file_sha256'] for k,v in packets.items()},
        integration_code_sha256=sha(__file__),strict_extension_of_r11=True,human_verified=False,accepted=accepted,
        scope='Only unknowns of the M1 arm that can change the r01 M0/M1 choice (4K Top100 final; 4K seed10 raw). r11 content retained literally; additions only. All four scored configurations (M0, M1, C3-M0, B0) are rescored uniformly with r12; revision effects are reported separately and are not prefix gains.'))
    print('r12 map',sha(target),'accepted',len(accepted),flush=True)

if __name__=='__main__':main()
