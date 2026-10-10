"""Offline blind source packet export and explicit semantic review validation."""
from __future__ import annotations
from assemble import digest, union_spans, subtract_spans

def export_visible_packets(context,requirements,stage='final'):
    visible=context[stage]
    reqs=[{k:r.get(k) for k in ('requirement_id','description','scope')} for r in requirements]
    units=[dict(text=u['text'],spans=u['spans']) for u in visible['units']]
    packet=dict(schema_version='source-blind-packet-r01',requirements=reqs,visible_units=units)
    packet['packet_id']=digest(packet)
    packet['packet_sha256']=digest(packet)
    return packet

def validate_review(packet,review):
    if digest({k:v for k,v in packet.items() if k!='packet_sha256'})!=packet.get('packet_sha256'):
        raise ValueError('packet content SHA drift')
    if review.get('packet_id')!=packet['packet_id'] or review.get('packet_sha256')!=packet['packet_sha256']:
        raise ValueError('review packet binding drift')
    if not review.get('reviewer_id'): raise ValueError('explicit reviewer required')
    expected={r['requirement_id'] for r in packet['requirements']}
    if set(review.get('judgments',{}))!=expected: raise ValueError('complete judgment set required')
    available=union_spans([s for u in packet['visible_units'] for s in u['spans']])
    for judgment in review['judgments'].values():
        if judgment.get('status') not in ('yes','no','unknown') or not judgment.get('rationale'):
            raise ValueError('three-valued status and semantic rationale required')
        necessary=judgment.get('necessary_spans',[])
        if judgment['status']=='yes' and not necessary: raise ValueError('TRUE requires reviewed full necessary support spans')
        if subtract_spans(necessary,available): raise ValueError('review cites invisible source spans')
    return True
