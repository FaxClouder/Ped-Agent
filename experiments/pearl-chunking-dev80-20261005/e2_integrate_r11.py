"""Build the E2 r11 common support map as a strict extension of E3 r10 plus its lineage.

Applies review-results-e2-r11.json: reviewed outside segments are appended to the
requirement's reviewed universe (or a new exhaustive visible-universe review is created
where none existed); does_not_support variants are appended to uncertain passages.
Nothing from r10 is removed or rewritten; the strict-extension check is enforced.
"""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
from runtime import ROOT, sha, save_json
from assemble import union_spans
from e1_visible_review_verify import intervals, all_inside

E3=ROOT/'outputs/pearl-chunking-dev80-20261006-11'
OUT=ROOT/'outputs/pearl-chunking-dev80-20261006-12'

def load(p):return json.loads(Path(p).read_text('utf8'))

def strict_extension(old,new):
    assert [r['intent_id'] for r in old['records']]==[r['intent_id'] for r in new['records']]
    for a,b in zip(old['records'],new['records']):
        assert {k:v for k,v in a.items() if k!='requirements'}=={k:v for k,v in b.items() if k!='requirements'}
        for qa,qb in zip(a['requirements'],b['requirements']):
            assert {k:v for k,v in qa.items() if k!='visible_universe_review'}=={k:v for k,v in qb.items() if k!='visible_universe_review'}
            va,vb=qa.get('visible_universe_review'),qb.get('visible_universe_review')
            if va is None:continue
            assert vb['alternatives'][:len(va['alternatives'])]==va['alternatives']
            assert vb.get('review_extensions',[])[:len(va.get('review_extensions',[]))]==va.get('review_extensions',[])
            assert all_inside(va['universe_spans'],intervals(vb['universe_spans'])) if va['universe_spans'] else True
            assert len(vb['uncertain'])==len(va['uncertain'])
            for ua,ub in zip(va['uncertain'],vb['uncertain']):
                assert {k:v for k,v in ua.items() if k!='adjudicated_variants'}=={k:v for k,v in ub.items() if k!='adjudicated_variants'}
                assert ub.get('adjudicated_variants',[])[:len(ua.get('adjudicated_variants',[]))]==ua.get('adjudicated_variants',[])
            assert {k:v for k,v in va.items() if k not in ('alternatives','review_extensions','universe_spans','uncertain')}=={k:v for k,v in vb.items() if k not in ('alternatives','review_extensions','universe_spans','uncertain')}

def main():
    base_path=E3/'common-support-map-e3-r10.json';base=load(base_path);new=copy.deepcopy(base)
    results=load(OUT/'review-results-e2-r11.json');assert results['base_mapping_sha256']==sha(base_path)
    export=load(OUT/'review-export-e2-r11.json');packets={p['packet_id']:p for p in export['packets']}
    recs={r['intent_id']:r for r in new['records']};accepted=[]
    for d in results['results']:
        pk=load(OUT/'review-packets-e2-r11'/f"{d['packet_id']}.json")
        assert pk['packet_sha256']==d['packet_sha256']==packets[d['packet_id']]['packet_sha256']
        q=next(x for x in recs[d['intent_id']]['requirements'] if x['requirement_id']==d['requirement_id'])
        spans=[s['span'] for s in pk['outside_segments']]
        ext=dict(revision='e2-r11',reviewer_id=d['reviewer_id'],packet_sha256=d['packet_sha256'],reviewed_text_sha256=d['reviewed_text_sha256'],
                 status='no_support_in_reviewed_segments',universe_expanded=bool(spans),rationale=d['outside_rationale'],kept_unknown=d['kept_unknown'],human_verified=False)
        if d['create_visible_universe_review']:
            assert 'visible_universe_review' not in q
            q['visible_universe_review']=dict(alternatives=[],caveats=['Created by E2 r11 supplement review over the actual visible text of the affected cell only.'],exhaustive=True,
                packet_sha256=d['packet_sha256'],rationale=d['outside_rationale'],review_extensions=[ext],reviewer_id=d['reviewer_id'],uncertain=[],universe_spans=union_spans(spans),universe_status='no')
        else:
            v=q['visible_universe_review'];v['universe_spans']=union_spans(v['universe_spans']+spans);v.setdefault('review_extensions',[]).append(ext)
            for adj in d['uncertain_adjudications']:
                u=v['uncertain'][adj['index']]
                u.setdefault('adjudicated_variants',[]).append(dict(verdict=adj['verdict'],source_spans=adj['source_spans'],rationale=adj['rationale'],reviewer_id=d['reviewer_id'],packet_sha256=d['packet_sha256'],revision='e2-r11'))
        accepted.append(dict(packet_id=d['packet_id'],intent_id=d['intent_id'],requirement_id=d['requirement_id'],universe_segments_added=len(spans),uncertain_adjudications=len(d['uncertain_adjudications']),new_alternatives=len(d['new_alternatives']),created_review=d['create_visible_universe_review'],kept_unknown=bool(d['kept_unknown'])))
    strict_extension(base,new)
    records_sha=hashlib.sha256(json.dumps(new['records'],ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    new.update(e2_revision='r11',schema_version='source-support-map-e2-r11',previous_map_sha256=base['map_sha256'],map_sha256=records_sha,human_verified=False,
               e2_supplement_review=dict(results_sha256=sha(OUT/'review-results-e2-r11.json'),export_sha256=sha(OUT/'review-export-e2-r11.json'),reviewer_id=results['reviewer_id'],rule=results['rule']))
    target=OUT/'common-support-map-e2-r11.json';save_json(target,new)
    save_json(OUT/'map-lineage-e2-r11.json',dict(base_mapping_path=base_path.relative_to(ROOT).as_posix(),base_mapping_sha256=sha(base_path),new_mapping_sha256=sha(target),previous_map_sha256=base['map_sha256'],new_map_records_sha256=records_sha,
        review_results_sha256=sha(OUT/'review-results-e2-r11.json'),review_export_sha256=sha(OUT/'review-export-e2-r11.json'),packets_sha256={k:v['packet_file_sha256'] for k,v in packets.items()},
        integration_code_sha256=sha(__file__),strict_extension_of_r10=True,human_verified=False,accepted=accepted,
        scope='Only unknowns of O10/O20 arms that can change the r01 overlap choice (4K Top100 final; 4K seed10 raw). r10 requirements, groups, certificates, alternatives and adjudications retained literally; additions only. All six arms (incl. O0) are rescored uniformly with r11; revision effects are reported separately and are not overlap gains.'))
    print('r11 map',sha(target),'accepted',len(accepted),flush=True)

if __name__=='__main__':main()
