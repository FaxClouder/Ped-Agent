"""Reopen blind actual-context review and bind every quote to saved final/source text."""
import argparse
import json
from pathlib import Path
from runtime import sha,cache_identity,save_json

def load(p):return json.loads(p.read_text('utf8'))
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output
    packet_path=out/'visible-context-review-packets-r01.json';review_path=out/'independent-visible-context-reviews-r01.json'
    packets={r['packet_id']:r for r in load(packet_path)['packets']};review=load(review_path);bindings=load(out/'visible-context-review-bindings-r01.json')
    if review['input_file_sha256']!=sha(packet_path) or bindings['contexts_sha256']!=sha(out/'contexts.jsonl'):raise ValueError('review input binding drift')
    contexts={r['context_id']:r for r in map(json.loads,(out/'contexts.jsonl').read_text('utf8').splitlines())}
    actual={}
    for b in bindings['bindings']:
        packet=packets[b['packet_id']];context=contexts[b['context_id']]
        if cache_identity({k:v for k,v in packet.items() if k!='packet_sha256'})!=packet['packet_sha256']:raise ValueError('packet internal hash')
        if packet['intent_id']!=context['intent_id'] or packet['visible_units']!=[{'text':u['text'],'spans':u['spans']} for u in context['final']['units']]:raise ValueError('packet actual-final visibility mismatch')
        actual[b['packet_id']]=context
    sources={(v['doc_id'],v['source_version'],e['element_id']):e['text'] for v in load(out/'source-views-prepared.json') for e in v['elements']}
    expected={(pid,r['requirement_id']) for pid,packet in packets.items() for r in packet['requirements']};seen=set();quotes=0;counts={'yes':0,'no':0,'unknown':0}
    for r in review['reviews']:
        pid=r['packet_id'];rid=r['requirement_id'];identity=(pid,rid)
        if identity in seen or identity not in expected:raise ValueError('review requirement matrix')
        seen.add(identity);packet=packets[pid]
        req=next(x for x in packet['requirements'] if x['requirement_id']==rid)
        if r['intent_id']!=packet['intent_id'] or r['requirement_description']!=req['description']:raise ValueError('review target binding')
        status=r['judgment']
        if status not in counts or not r['semantic_reason'] or status=='yes' and not r['quotes']:raise ValueError('review semantic judgment shape')
        counts[status]+=1
        for q in r['quotes']:
            u=actual[pid]['final']['units'][q['visible_unit_index']];start,end=q['visible_unicode_start'],q['visible_unicode_end']
            if not 0<=start<end<=len(u['text']) or u['text'][start:end]!=q['quote']:raise ValueError('review quote not actual visible text')
            segments=[]
            for part in u['parts']:
                left,right=max(start,part['text_start']),min(end,part['text_end'])
                if left>=right:continue
                s=part['span'];s=dict(s,start=s['start']+left-part['text_start'],end=s['start']+right-part['text_start'])
                raw=sources[(s['doc_id'],s['source_version'],s['element_id'])][s['start']:s['end']]
                segments.append(dict(s,quote=raw))
            if q['source_segments']!=segments:raise ValueError('review source quote/offset mismatch')
            quotes+=1
    if seen!=expected or len(packets)!=8:raise ValueError('incomplete visible review')
    save_json(out/'visible-review-verification-r01.json',{'status':'passed','actual_context_packets':len(packets),'requirements':len(seen),'quotes':quotes,'diagnostic_judgments':counts,'review_sha256':sha(review_path),'packet_file_sha256':sha(packet_path),'contexts_sha256':sha(out/'contexts.jsonl'),'score_change':'none; source certificate scores remain conservative and unchanged'})
    print('actual final/source review verification passed',len(packets),len(seen),quotes,flush=True)

if __name__=='__main__':main()
