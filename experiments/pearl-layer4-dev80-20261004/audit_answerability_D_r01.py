"""Mechanical provenance/span checks only; never changes semantic decisions."""
import collections,re
from context_write_D_r01 import ROOT
from assemble_c100_r01 import read,sha,write
if __name__=='__main__':
 directory=ROOT/'reviews/primary/answerability-D300-r02';counts=collections.Counter();errors=[];empty=[]
 for p in sorted(directory.glob('*.json')):
  d=read(p);packet=read(d['provenance']['packet_path']);c=packet['context'];counts[d['answerability']]+=1
  if d['provenance']['packet_sha256']!=sha(d['provenance']['packet_path']):errors.append([p.name,'SHA'])
  if len(d['requirements'])!=len(packet['requirements']):errors.append([p.name,'requirement count'])
  for req in d['requirements']:
   if req['label'] in ('supported','partial') and not req['evidence']:empty.append([p.name,req['requirement_id'],req['label']])
   for e in req['evidence']:
    if c[e['start']:e['end']]!=e['quote']:errors.append([p.name,'quote'])
    labels=list(re.finditer(r'\[Source[^\]]+\]',c[:e['start']+1]));actual=labels[-1].group() if labels else None
    if actual!=e['source_label']:errors.append([p.name,'source'])
    if re.search(r'\[Source[^\]]+\]',e['quote']):errors.append([p.name,'cross source boundary'])
 result={'status':'mechanical_audit_only_not_D_acceptance','packet_n':sum(counts.values()),'answerability_counts':dict(counts),'errors':errors,'supported_or_partial_without_evidence':empty,'no_grounding_behavior_factuality_review_started':True}
 write(ROOT/'reviews/primary/answerability-D300-mechanical-audit-r01.json',result);print(result)
