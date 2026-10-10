"""Explicit reviewed scope exclusions; historical map definitions stay literal."""
import copy
from e1_visible_review import support_r06, contained
from e1_visible_review_verify import req_status, all_inside, intervals

def active_requirement(q):
    q=copy.deepcopy(q);r=q.get('visible_universe_review',{});v=r.get('scope_revision',{})
    for i in v.get('excluded_certificate_indices',[]):q['evidence_groups'][i]['status']='unknown'
    r['alternatives']=[a for i,a in enumerate(r.get('alternatives',[])) if i not in v.get('excluded_alternative_indices',[])]
    return q

def support_revision(spans,mapping):
    m=dict(mapping,requirements=[active_requirement(q) for q in mapping['requirements']])
    support,basis,base=support_r06(spans,m)
    for q in m['requirements']:
        rid=q['requirement_id'];v=q.get('visible_universe_review',{}).get('scope_revision',{})
        if support[rid]=='unknown' and any(contained(spans,u) for u in v.get('negative_scopes',[])):
            support[rid]='no';basis[rid]='exhaustive_actual_scope_adjudication'
    return support,basis,base

def independent_status(req,spans,iv):
    # Independently project indices rather than reuse production projection.
    q=copy.deepcopy(req);r=q.get('visible_universe_review',{});v=r.get('scope_revision',{})
    excluded=set(v.get('excluded_certificate_indices',[]))
    q['evidence_groups']=[dict(g,status='unknown') if i in excluded else g for i,g in enumerate(q['evidence_groups'])]
    excluded=set(v.get('excluded_alternative_indices',[]))
    r['alternatives']=[a for i,a in enumerate(r.get('alternatives',[])) if i not in excluded]
    result=req_status(q,spans,iv)
    if result=='unknown' and spans and any(all_inside(spans,intervals(u)) for u in v.get('negative_scopes',[])):return 'no'
    return result

def scoring_run(out,mapping,revision):
    import score as core
    import e3
    import e3_score_verify as gate
    from runtime import sha,save_json
    core.reviewed_support=lambda spans,m: support_revision(spans,m)[:2]
    e3.req_status=independent_status
    gate.req_status=independent_status
    gate.support_r06=support_revision
    save_json(out/f'scope-scoring-driver-{revision}.json',dict(driver_sha256=sha(__file__),mapping_sha256=sha(mapping),scope='Explicit reviewed exclusions projected in memory; original certificate definitions retained. Production and independently projected reopen scorer both apply exclusions and exhaustive actual negative scopes.'))
    gate.run(out,mapping,revision)

if __name__=='__main__':
    import argparse
    from pathlib import Path
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--mapping',type=Path,required=True);p.add_argument('--revision',required=True);a=p.parse_args()
    scoring_run(a.output.resolve(),a.mapping.resolve(),a.revision)
