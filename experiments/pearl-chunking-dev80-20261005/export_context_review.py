"""Export a fixed, score-blind actual final-context diagnostic review sample."""
import argparse
import json
from pathlib import Path
from runtime import save_json,sha,cache_identity
from review import export_visible_packets

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output
    contexts=[json.loads(l) for l in (out/'contexts.jsonl').read_text('utf8').splitlines()]
    maps={r['intent_id']:r for r in json.loads((out/'common-support-map-r03.json').read_text('utf8'))['records']}
    packets=[];bindings=[]
    # Fixed before opening any score file; one consistent final condition per intent.
    for c in contexts:
        if (c['strategy'],c['budget'],c['panel_id'])!=('P0',4096,'fixed_budget_main'):continue
        m=maps[c['intent_id']];packet=export_visible_packets(c,m['requirements'])
        packet={k:v for k,v in packet.items() if k not in ('packet_id','packet_sha256')}
        packet.update(query=m['query'],intent_id=m['intent_id']);packet['packet_id']=cache_identity(packet);packet['packet_sha256']=cache_identity(packet)
        packets.append(packet);bindings.append({'intent_id':m['intent_id'],'packet_id':packet['packet_id'],'context_id':c['context_id']})
    if len(packets)!=8:raise ValueError('actual final-context review sample incomplete')
    save_json(out/'visible-context-review-packets-r01.json',{'packets':packets})
    save_json(out/'visible-context-review-bindings-r01.json',{'contexts_sha256':sha(out/'contexts.jsonl'),'fixed_selection':'P0/4096/fixed_budget_main, every preselected intent; before scores','bindings':bindings,'review_role':'Diagnostic semantic inspection of actual final visible content; does not upgrade conservative certificate-based score or select strategies.'})
    print('exported actual visible packets',len(packets),flush=True)

if __name__=='__main__':main()
