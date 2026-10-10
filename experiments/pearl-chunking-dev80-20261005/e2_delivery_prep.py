"""E2 selection record, cost table and scoring-revision changes (r10 -> r11); no models."""
from __future__ import annotations
import json
from pathlib import Path
from runtime import ROOT, sha, save_json, save_rows

E1=ROOT/'outputs/pearl-chunking-dev80-20261005-05'
E3=ROOT/'outputs/pearl-chunking-dev80-20261006-11'
OUT=ROOT/'outputs/pearl-chunking-dev80-20261006-12'
BASES=('C2-L384-O0-M0','C3-L256-O0-M0')
def arms(b):return [b,b.replace('-O0-','-O10-'),b.replace('-O0-','-O20-')]
ALL=[c for b in BASES for c in arms(b)]

def load(p):return json.loads(Path(p).read_text('utf8'))
def rows(p):
    with Path(p).open(encoding='utf8') as f:return [json.loads(l) for l in f if l.strip()]
def idx(c):return (E1 if '-O0-' in c else OUT)/('index-'+c)
def rel(p):return Path(p).relative_to(ROOT).as_posix()

def revision_changes():
    a={(d['configuration_id'],d['budget'],d['panel_id'],d['intent_id'],d['stage']):d for d in rows(OUT/'score-details-e2-r10.jsonl')}
    out=[]
    for d in rows(OUT/'score-details-e2-r11.jsonl'):
        k=(d['configuration_id'],d['budget'],d['panel_id'],d['intent_id'],d['stage']);o=a[k]
        if o['sufficient']!=d['sufficient'] or o['support']!=d['support']:
            out.append(dict(configuration_id=k[0],budget=k[1],panel_id=k[2],intent_id=k[3],stage=k[4],before=o['sufficient'],after=d['sufficient'],before_support=o['support'],after_support=d['support'],visible_text_sha256=d['visible_text_sha256'],note='scoring revision r10->r11; not an overlap effect'))
    save_rows(OUT/'scoring-revision-changes-e2-r11.jsonl',out);return out

def costs():
    cells=[]
    e3cost={(c['configuration_id'],c['budget'],c['panel_id']):c for c in load(E3/'cost-e3-r01.json')['cells'] if c['strategy']=='P0'}
    for c in ALL:
        d=idx(c);b=load(d/'build-cost.json');r=load(d/'retrieval-cost.json')
        row=dict(configuration_id=c,source='E1 -05 original record (O0 strict reuse; not re-run)' if '-O0-' in c else 'E2 -12 r05 run',build_cost_file=rel(d/'build-cost.json'),dense_seconds=b['dense_seconds'],build_wall_seconds=b['wall_seconds'],passage_tokens=b['passage_tokens'],encoded_passages=b['encoded_passages'],index_bytes=b['index_bytes'],retrieval_wall_seconds=r['wall_seconds'],retrieval_cost_file=rel(d/'retrieval-cost.json'),assembly=[])
        for B in (4096,8192):
            for panel in ('fixed_budget_main','seed10_diagnostic'):
                if '-O0-' in c:
                    e=e3cost[c,B,panel];row['assembly'].append(dict(budget=B,panel_id=panel,mean_seconds=e['mean_seconds'],median_seconds=e['median_seconds'],mean_final_tokens=e['mean_final_tokens'],reused_contexts=e.get('reused_contexts'),source=rel(E3/'cost-e3-r01.json'),caveat=e.get('cost_caveat')))
                else:
                    e=load(OUT/f'contexts-{c}-P0-{B}-{panel}-receipt.json');row['assembly'].append(dict(budget=B,panel_id=panel,mean_seconds=e['mean_seconds'],median_seconds=e['median_seconds'],mean_final_tokens=e['mean_final_tokens'],wall_seconds=e['wall_seconds'],source=rel(OUT/f'contexts-{c}-P0-{B}-{panel}-receipt.json')))
        if '-O0-' not in c:
            p=load(d/'overlap-profile.json');row.update(attached_share=p['attached_share'],effective_ratio_mean=p['effective_ratio_mean'],overlap_content_tokens_mean_attached=p['overlap_content_tokens_mean_attached'],max_overlap_content_tokens=p['max_overlap_content_tokens'])
        cells.append(row)
    save_json(OUT/'cost-e2-r01.json',dict(cells=cells,caveat='O0 costs are the original E1/E3 records of the reused arm; they are not added to E2 run times and no end-to-end latency is claimed. E2 build wall includes the 1-in-40 original-function rechecks.',model_load=[load(p) for p in sorted(OUT.glob('model-load-cost-e2-C2*.json'))]))
    return cells

def config(c):
    m=load(idx(c)/'manifest.json')['configuration'];C,L,O=c.split('-')[:3]
    return dict(configuration_id=c,source_view_sha256=m['source'],table_snapshot_sha256=m['table'],parent_graph_sha256=m['parent'],tokenizer=m['tokenizer'],lexical=m['lexical'],calibration=m['calibration'],models=m['models'],
                C=C,L=int(L[1:]),O={'O0':0.0,'O10':0.1,'O20':0.2}[O],M='M0',retrieval=m['retrieval'],recovery='P0 (alias of the E3 frozen recovery arm)',budgets=[4096,8192],main_budget=4096,
                index_manifest=rel(idx(c)/'manifest.json'),index_manifest_sha256=sha(idx(c)/'manifest.json'),rankings_sha256=sha(idx(c)/'rankings.jsonl'),
                child_chunks_sha256=sha(idx(c)/'child_chunks.jsonl'),e2=m.get('E2'))

def selection():
    s10=load(OUT/'scores-e2-r10.json');s11=load(OUT/'scores-e2-r11.json');res={}
    for b in BASES:
        d=s11['decisions'][b]
        res[b]=dict(status=d['status'],selected=d['selected'],order=d['order'],threats=d['threats'],table_r11=d['table'],
                    decision_r10=dict((k,s10['decisions'][b][k]) for k in ('status','selected','order','threats')),
                    current_identity_for_5B=d['selected'] or b,
                    note=('frozen under rule r01 with map r11' if d['status']=='frozen' else 'pending_review under rule r01: a competitor still has yes+unknown >= leader yes; O0 is recorded as the current identity only, not claimed optimal'),
                    configs={c:config(c) for c in arms(b)})
    rule=OUT/'e2-overlap-selection-rule-r01.md'
    save_json(OUT/'e2-overlap-selection-r01.json',dict(stage='E2',rule=rel(rule),rule_sha256=sha(rule),mapping=rel(OUT/'common-support-map-e2-r11.json'),mapping_sha256=sha(OUT/'common-support-map-e2-r11.json'),map_lineage_sha256=sha(OUT/'map-lineage-e2-r11.json'),
        scores_r11_sha256=sha(OUT/'scores-e2-r11.json'),scores_r10_sha256=sha(OUT/'scores-e2-r10.json'),cores=res,first_choice_for_5B=res['C2-L384-O0-M0']['current_identity_for_5B'],
        statement='Development selection on dev80; not a significant win. 8K, Top10 diagnostics, duplication, effective overlap, tokens and latency were reported but not used as selection keys.',human_verified=False,generation_calls=0,E4_started=False))
    return res

if __name__=='__main__':
    ch=revision_changes();cs=costs();sel=selection()
    print('revision changes',len(ch),'| cost cells',len(cs),'|',{b:(v['status'],v['selected']) for b,v in sel.items()},flush=True)
