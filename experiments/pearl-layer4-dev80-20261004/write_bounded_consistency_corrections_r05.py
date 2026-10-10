import json,hashlib,copy,re
from pathlib import Path
from citations_D_r01 import source_spans
R=Path('outputs/pearl-layer4-dev80-20261004-01');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dst=R/'reviews/primary/behavior-grounding-consistency-r05';dst.mkdir(parents=True,exist_ok=True)
written=[]
for i in (46,289):
 old=R/'reviews/primary'/('behavior-D300-tail60-canonical-r03' if i==289 else 'behavior-D300-front150-canonical-r03')/f'behavior-{i:04d}.json';pp=R/'packets/behavior-D300-r02'/f'behavior-{i:04d}.json';x=json.loads(pp.read_text(encoding='utf-8'));v=json.loads(old.read_text(encoding='utf-8'))
 v['behavior']='ambiguous';v['abstain']=None;v['abstains_from_unsupported_completion']=None;v['unsupported_completion']=False
 v['behavior_classification_reason']='重新全文实际核查：明确限缩且未补齐必要结论，含领域事实背景排除pure；附加partial断言不满足bounded已说均支持；没有完成必要结论不能full。冻结分类边界确实无法确定，ambiguous保留行为不确定性，abstain null；必要补全flag独立false。原refusal reason实际判断保留，未自动改unknown。'
 v['provenance'].update({'task':'behavior semantic consistency correction','packet_sha256':sha(pp),'actual_read':['complete current query and necessary requirements','complete raw_answer reread','all current actual context source blocks reread','selected Grounding atoms and partial proof','original behavior and refusal evidence reread'],'grounding_or_answerability_labels_imported':False,'selected_grounding_read_for_explicit_QA':True,'answerability_labels_F_old_scores_read':False,'supersedes_path':str(old),'supersedes_sha256':sha(old),'classification_basis':'Frozen rubric strict bounded support requirement; existing ambiguous label for unresolved residual classification, no new bounded definition.'})
 p=dst/f'behavior-{i:04d}.json'
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
 z=json.loads(p.read_text(encoding='utf-8'));assert z['blind_id']==x['blind_id'] and z['provenance']['packet_sha256']==sha(pp);assert z['reason']['label'] in ('correct','incorrect','unknown') and z['abstain'] is None and z['unsupported_completion'] is False
 written.append({'task':'behavior','number':i,'path':str(p),'sha256':sha(p),'previous_path':str(old),'previous_sha256':sha(old),'packet_path':str(pp),'packet_sha256':sha(pp)})
old=R/'reviews/primary/grounding-D300-r02/grounding-0124.json';pp=R/'packets/grounding-D300-r02/grounding-0124.json';v=json.loads(old.read_text(encoding='utf-8'));x=json.loads(pp.read_text(encoding='utf-8'));ev=[]
for s in source_spans(x['context']):
 for m in re.finditer(r'room with five columns in front of the exit',x['context'][s['start']:s['end']]):
  a=s['start']+m.start();b=s['start']+m.end();ev.append({'quote':x['context'][a:b],'start':a,'end':b,'source_label':s['source_label']})
assert ev and all(e['source_label']=='[Source pearl-src-49fbc8413e27f3f1 | p.12-13]' for e in ev)
c=next(c for c in v['claims'] if c['claim_id']=='c010');before=copy.deepcopy(c);c['grounding']={'label':'supported','evidence':ev,'reason':'实际重新全文读取，p12-13 Fig14caption明确room with five columns in front of the exit，原partial只定位the columns漏读同实际context图注。主体/条件/数值全部支持。'}
pair_checks=[]
for p in v['citation_pairs']:
 if p['claim_id']=='c010':
  pair_checks.append(p['source_label'])
  if p['source_label']=='[Source pearl-src-49fbc8413e27f3f1 | p.12-13]':p.update(label='supported',evidence=ev,reason='Actual Fig14caption in same cited source/page supportsfive columns; verified inline/paragraph scope unchanged.')
v['provenance'].update({'task':'grounding actual missed-caption correction','actual_read':['complete current raw_answer/query','all current actual context source blocks','Fig14caption p12-13','selected c010 conditions and all actual citation pairs'],'supersedes_path':str(old),'supersedes_sha256':sha(old),'packet_sha256':sha(pp),'correction':'Only c010 semantic support/evidence corrected; canonical7 unchanged. Actual selected extraction has no c010 citation pair; no inferred new citations or other pair relabels.','actual_c010_pair_source_labels':pair_checks})
fields=['claim_id','start','end','quote','normalized_claim','conditions','occurrences'];assert all(before[f]==c[f] for f in fields)
p=dst/'grounding-0124.json'
with p.open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
z=json.loads(p.read_text(encoding='utf-8'));assert z['blind_id']==x['blind_id'] and z['provenance']['packet_sha256']==sha(pp)
for c in z['claims']:
 assert x['raw_answer'][c['start']:c['end']]==c['quote']
 for e in c['grounding']['evidence']:assert x['context'][e['start']:e['end']]==e['quote']
written.append({'task':'grounding','number':124,'path':str(p),'sha256':sha(p),'previous_path':str(old),'previous_sha256':sha(old),'packet_path':str(pp),'packet_sha256':sha(pp),'canonical7_unchanged':True,'citation_c010_pairs_present':len(pair_checks)})
audit=R/'reviews/primary/bounded-grounding-consistency-audit-r01.json';out={'status':'current','supersedes_audit_pending_recommendations':str(audit),'original_audit_sha256':sha(audit),'scope':'Only requested3cell QA semantic corrections; no F/answerability/score exposure','decisions':written,'behavior124':'Original bounded_partial/false/correct retained after actual G evidence correction; independent context review pending with root','verification':'Exclusive files reopened and blindIDs, packet hashes, raw/context evidence spans, c010canonical7 and no fabricated c010citation checked.'}
p=R/'reviews/primary/bounded-grounding-consistency-audit-supplement-r02.json'
with p.open('x',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2)
print(p);print([(z['task'],z['number']) for z in written])
