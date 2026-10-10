"""Export neutral actual-text review packets for unresolved E3 4K main cells."""
import argparse
import json
from pathlib import Path
from e3 import SOURCE,REVIEW,CONFIGS,rows,load
from assemble import union_spans,key
from score import score_context
from runtime import ROOT,sha,save_json

def export(out,source_dirs=None):
    directory=out/'review-packets-e3-r08';directory.mkdir(exist_ok=True)
    maps={m['intent_id']:m for m in load(REVIEW/'common-support-map-e1-r07.json')['records']}
    views=load(SOURCE/'source-views-prepared.json');elements={key(dict(doc_id=v['doc_id'],source_version=v['source_version'],element_id=e['element_id'])):e for v in views for e in v['elements']};titles={(v['doc_id'],v['source_version']):v['title'] for v in views}
    needs={};contexts={}
    for path in [p for d in (source_dirs or [out]) for p in d.glob('contexts-*-4096-fixed_budget_main.jsonl')]:
        # Live workers flush complete JSON lines; omit an active partial last line.
        def completed_lines(path):
            with path.open(encoding='utf8') as f:
                for line in f:
                    if line.endswith('\n'):yield json.loads(line)
        for ctx in completed_lines(path):
            m=maps[ctx['intent_id']];result=score_context(ctx,m)
            contexts.setdefault(ctx['intent_id'],[]).append(ctx)
            if result['sufficient']=='unknown':
                for rid,s in result['support'].items():
                    if s=='unknown':needs.setdefault(ctx['intent_id'],set()).add(rid)
    index=[]
    for i,rids in sorted(needs.items()):
        # Each review intent has all three primary 4K restoration cells.
        if {c['strategy'] for c in contexts[i] if c['configuration_id']==CONFIGS[1]}!={'P0','P1','P2'}:continue
        path=directory/(i+'.json')
        if path.exists():continue
        visible=union_spans([s for ctx in contexts[i] for u in ctx['final']['units'] for s in u['spans']])
        requirements=[dict(requirement_id=r['requirement_id'],description=r['description'],scope=r.get('scope'),reference_evidence=[[dict(text=elements[key(s)]['text'][s['start']:s['end']],source_span=s) for s in g['necessary_spans']] for g in r['evidence_groups'] if g['status']=='yes']) for r in maps[i]['requirements'] if r['requirement_id'] in rids]
        segments=[dict(segment_id=f'S{j}',source_span=s,document_title=titles[s['doc_id'],s['source_version']],element_type=elements[key(s)].get('element_type'),heading_path=elements[key(s)].get('heading_path'),text=elements[key(s)]['text'][s['start']:s['end']]) for j,s in enumerate(visible,1)]
        packet=dict(intent_id=i,query=maps[i]['query'],requirements=requirements,segments=segments,instructions='Judge each requirement against actual visible text. For yes, return minimal source spans sufficient for all conditions and rationale. No means entire supplied text union has no sufficient alternative. Use unknown for ambiguity; no keyword or same-document inference. Preserve relation/scope. Each returned source span must be within a supplied segment. Hidden method/rank/old scores. Agent review, not human.')
        save_json(path,packet);index.append(dict(intent_id=i,path=path.relative_to(ROOT).as_posix(),sha256=sha(path),characters=sum(len(s['text']) for s in segments),requirements=len(requirements)))
        save_json(directory/(i+'-binding.json'),dict(packet_sha256=sha(path),mapping_sha256=sha(REVIEW/'common-support-map-e1-r07.json'),visible_spans=visible,contexts=[dict(context_id=c['context_id'],configuration_id=c['configuration_id'],strategy=c['strategy'],budget=c['budget'],panel_id=c['panel_id'],text_sha256=c['final']['text_sha256']) for c in contexts[i]]))
    print(json.dumps(index,ensure_ascii=False),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--sources',nargs='*',type=Path);args=p.parse_args();export(args.output.resolve(),args.sources)
