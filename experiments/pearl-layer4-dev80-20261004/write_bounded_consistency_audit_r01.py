import json,hashlib,re
from pathlib import Path
from citations_D_r01 import source_spans
R=Path('outputs/pearl-layer4-dev80-20261004-01')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
specs=[(46,'pearl-dev-067::A1-8192','c010',False,'partial所述corridor/intersection参数吸收机制在actual最后截于and，回答补了intersection。所问Bode不显式模拟corridor必要结论有直接证据；Moustaid一侧未补齐。该possible参数机制是附加解释，不等同必要结论补全；unsupported_completion保持false。但已说均支持条件失败，原bounded_partial不宜作为合格bounded保留。明确拒绝另一半、已有第一半结论，未形成完整回答；不能把这类清楚的限缩直接自动记ambiguous。建议根依冻结行为实现处理这一残余类别，暂不伪造new行为label。',[r'parameters of our model could potentially absorb interactions between the dynamics in corridors and',r'we do not explicitly model the dynamics in corridors',r'network node model with an arbitrary.*?links',r'bidirectional cell-transmission model']),
(124,'pearl-dev-080::A0-8192','c010',False,'重新核对全部actual：同source p12-13 Fig14caption明确five columns in front of the exit。原c010 partial漏证据，应独立修订为supported并绑定图注；无需修改其quote/条件。Chraibi必要资格已答，Twarog验证/现实校准必要结论未补齐、仅mesh/convergence背景，本包没有13-14验证结论；行为bounded_partial/unsupportedfalse/reasoncorrect可以保留，前提实际修正这条G证据，不能只为报告忽略P。',[r'room with five columns in front of the exit',r'unrealistic behavior is not related.*?model class',r'second order model yielding a first order convergence']),
(289,'pearl-dev-074::A0-4096','c003',False,'该P源于回答把Shi2021/2024绑定obstacle type，actual obstacle引文是Shi2022，2021/2024仅luggage。这是附加引文背景错配，回答并未补齐Xie上/下坡或Shi同年龄free上下楼必要结论；unsupported_completion保持false。actual包未含Xie ramp原段或Shi free descending关系/例外，缺口理由仍correct。领域事实引文背景非纯拒答，但含partial则不满足bounded已说均支持；不能继续把原类别称合格bounded，也不能自动以partial映射ambiguous，需要冻结分类实现的剩余类型明确化。',[r'obstacle type \(Feng et al., 2022; Shi et al., 2022\)',r'luggage-laden ratios \(Shi et al., 2024; Shi et al., 2021\)',r'group behaviour \(Fu et al., 2019; Xie et al., 2023\)'])]
rows=[]
for i,key,cid,flag,reason,patterns in specs:
 pp=R/'packets/behavior-D300-r02'/f'behavior-{i:04d}.json';gp=R/'reviews/primary/grounding-D300-r02'/f'grounding-{i:04d}.json';bp=R/'reviews/primary'/('behavior-D300-tail60-canonical-r03' if i==289 else 'behavior-D300-front150-canonical-r03')/f'behavior-{i:04d}.json'
 x=json.loads(pp.read_text(encoding='utf-8'));g=json.loads(gp.read_text(encoding='utf-8'));b=json.loads(bp.read_text(encoding='utf-8'));ev=[]
 for pat in patterns:
  for s in source_spans(x['context']):
   for m in re.finditer(pat,x['context'][s['start']:s['end']],re.I|re.S):
    a=s['start']+m.start();z=s['start']+m.end();ev.append({'quote':x['context'][a:z],'start':a,'end':z,'source_label':s['source_label']})
 assert ev and all(x['context'][e['start']:e['end']]==e['quote'] for e in ev)
 rows.append({'cell_id':key,'blind_id':x['blind_id'],'query':x['query'],'audited_partial_claim_id':cid,'selected_grounding_path':str(gp),'selected_grounding_sha256':sha(gp),'selected_behavior_path':str(bp),'selected_behavior_sha256':sha(bp),'packet_path':str(pp),'packet_sha256':sha(pp),'response_sha256':x['response_sha256'],'context_sha256':x['context_sha256'],'original_behavior':b['behavior'],'necessary_unsupported_completion':flag,'reason':reason,'evidence':ev,'recommend_behavior_change':i!=124,'recommend_grounding_correction':i==124,'recommendation_status':'G124实际漏证据修复；46/289拒绝继续作为合格bounded，分类残余待根依冻结规则收敛。'})
out={'status':'current','rubric_path':'experiments/pearl-layer4-dev80-20261004/rubrics.md','rubric_sha256':sha(Path('experiments/pearl-layer4-dev80-20261004/rubrics.md')),'scope':'Only three requested D bounded/G consistency audit; no science changed in this audit','provenance':{'reviewer':'prepare_layer4; original context primary role reused for explicit semantic QA','model':'inherited; exact backend ID unavailable','actual_read':'Three current behavior query/requirements/full raw_answer/all actual context source blocks, selected grounding all normalized atoms and partial evidence, original behavior/refusal evidence. Truncated bulk output followed by separate full-context reads. No answerability labels/F/old scores/200 read. Selection metadata accessed only grounding/behavior path fields.','prior_exposure':'Own D answerability/context reviews and C engineering/source-label exposure from earlier authorized roles; not claiming fresh blind identity.'},'rows':rows}
p=R/'reviews/primary/bounded-grounding-consistency-audit-r01.json'
with p.open('x',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2)
print(p)
