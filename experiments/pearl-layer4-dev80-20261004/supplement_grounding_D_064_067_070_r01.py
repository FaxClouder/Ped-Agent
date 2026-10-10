import json,hashlib
from grounding_inspect_D_r01 import ROOT,packet
from grounding_write_D_r01 import locate
from citations_D_r01 import textual_pairs
for i in(64,67,70):
 p=ROOT/'reviews/primary/grounding-D300-r02'/f'grounding-{i:04}.json';r=json.loads(p.read_text('utf-8'));x=packet(i)
 if i==64:
  c=r['claims'][3];c['grounding']={'label':'supported','evidence':locate(x['context'],[r'oscillations in position of pedestrians \(leads to nonphysical overlapping\)']),'reason':'实际补读p1-2明确position oscillations；原所引p6-7未支持该独立内容，不回填引用。'}
 if i==67:
  c=r['claims'][10];c['grounding']={'label':'supported','evidence':locate(x['context'],[r'objective of this study was to facilitate the coordination.{0,260}evacuating passengers']),'reason':'实际补读完整p1-2句明确协调两方并降低对向互动，原子完全支持。'}
 r['citation_pairs']=textual_pairs(x['raw_answer'],r['claims'],x['context'])
 for v in r['citation_pairs']:
  if (i==64 and v['claim_id']=='c004' and v['citation_page']=='6-7') or (i==70 and v['claim_id'] in('c004','c005','c006','c007') and v['citation_page']=='13'):
   v.update(label='unsupported',evidence=[],reason='实际完整阅读该引用页可见源块：该独立数值/关系不在此页；整体G来自另一actual页，禁止回填。')
 r['provenance'].update(origin_review_path=str(p),origin_review_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),supplement_reason='实际补读关联整句/所引源块完成page独立语义核对；七个科学字段不变。')
 q=ROOT/'reviews/primary/grounding-D300-supplement-r01'/p.name
 with q.open('x',encoding='utf-8') as f:json.dump(r,f,ensure_ascii=False,indent=2)
