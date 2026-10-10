"""Fixed stratified actual-text audit, independent of observed quality changes."""
import argparse
import random
from pathlib import Path
from e3 import REVIEW,SOURCE,CONFIGS,load,rows
from assemble import union_spans,key
from runtime import ROOT,save_json,sha

def run(out):
    maps={m['intent_id']:m for m in load(REVIEW/'common-support-map-e1-r07.json')['records']};strata={}
    for i,m in maps.items():strata.setdefault(m['main_stratum'],[]).append(i)
    rng=random.Random(20261005);chosen={s:sorted(rng.sample(sorted(ids),min(2,len(ids)))) for s,ids in sorted(strata.items())}
    selection=out/'semantic-audit-sample-e3-r01.json'
    if not selection.exists():save_json(selection,dict(seed=20261005,strata=chosen,intents=sorted(i for group in chosen.values() for i in group),scope='2 intents per stratum uniformly selected, quality-independent; actual 4K Top100 text union for semantic audit; other budgets/panel inherit explicit reviewed-scope limits.'))
    else:assert load(selection)['strata']==chosen
    elements={key(dict(doc_id=v['doc_id'],source_version=v['source_version'],element_id=e['element_id'])):e for v in load(SOURCE/'source-views-prepared.json') for e in v['elements']}
    titles={(v['doc_id'],v['source_version']):v['title'] for v in load(SOURCE/'source-views-prepared.json')}
    directory=out/'review-packets-e3-r08';directory.mkdir(exist_ok=True)
    wanted=set(load(selection)['intents']);by_intent={i:[] for i in wanted}
    for p in out.glob('contexts-*-4096-fixed_budget_main.jsonl'):
        for c in rows(p):
            if c['intent_id'] in wanted:by_intent[c['intent_id']].append(c)
    for i in load(selection)['intents']:
        path=directory/(i+'.json')
        if path.exists():
            if {r['requirement_id'] for r in load(path)['requirements']}=={r['requirement_id'] for r in maps[i]['requirements']}:continue
            path=directory/(i+'-fixed-sample.json')
            if path.exists():continue
        contexts=by_intent[i]
        assert len(contexts)==9
        visible=union_spans([s for c in contexts for u in c['final']['units'] for s in u['spans']])
        requirements=[dict(requirement_id=r['requirement_id'],description=r['description'],scope=r.get('scope'),reference_evidence=[[dict(text=elements[key(s)]['text'][s['start']:s['end']],source_span=s) for s in g['necessary_spans']] for g in r['evidence_groups'] if g['status']=='yes']) for r in maps[i]['requirements']]
        segments=[dict(segment_id=f'S{j}',source_span=s,document_title=titles[s['doc_id'],s['source_version']],element_type=elements[key(s)].get('element_type'),heading_path=elements[key(s)].get('heading_path'),text=elements[key(s)]['text'][s['start']:s['end']]) for j,s in enumerate(visible,1)]
        save_json(path,dict(intent_id=i,query=maps[i]['query'],requirements=requirements,segments=segments,instructions='Judge every requirement only against actual supplied segments. Enumerate distinct minimal complete alternatives; preserve conditions and relations. Ambiguity unknown. Reference text only explains requirements; hidden method/rank/old scores. Agent review, not human.'))
        save_json(directory/(path.stem+'-binding.json'),dict(packet_sha256=sha(path),mapping_sha256=sha(REVIEW/'common-support-map-e1-r07.json'),visible_spans=visible,contexts=[dict(context_id=c['context_id'],configuration_id=c['configuration_id'],strategy=c['strategy'],budget=c['budget'],panel_id=c['panel_id'],text_sha256=c['final']['text_sha256']) for c in contexts],fixed_sample=True))
    print('Fixed semantic sample',load(selection)['intents'],flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();run(a.output.resolve())
