"""Session 6B calibration gate record and offline research cost projection (no provider call).

The projection builds the blind research packets in memory only (nothing written), measures
their UTF-8 size and converts to tokens with ratios observed in this run's calibration usage and
the 6A English request usage. It is an estimate for the operator, not a measured cost.
"""
from __future__ import annotations
import argparse
import json
from collections import defaultdict
from pathlib import Path
from runtime import ROOT, sha, save_json
import e6b_judge as J
import e6b_prompts as P
import e6b_packets as K

OUT=ROOT/'outputs/pearl-chunking-dev80-20261006-15'
CAL=OUT/'calibration'


def load(p):return json.loads(Path(p).read_text(encoding='utf8'))


def projection():
    rows,order,packets,bindings,secondary,c2p=K.build()
    # English bytes per provider token from 6A generation usage (same contexts and answers).
    gen=[load(p) for p in sorted((K.S6A/'generation').glob('*.json'))]
    bpt=sum(g['request_utf8_bytes'] for g in gen)/sum(g['provider_response_metadata']['token_usage']['prompt_tokens'] for g in gen)
    # Output tokens per packet by task from calibration; grounding/factuality scaled by claim candidates.
    out_tokens=defaultdict(list);cands=defaultdict(list)
    for p in (CAL/'judge-r01').rglob('*.json'):
        rec=load(p);task=rec['meta'].get('task','layer3');out_tokens[task].append(rec['usage_total']['completion_tokens'])
        if task in ('grounding','factuality'):cands[task].append(max(1,len((rec['parsed'] or {}).get('claims',[]))))
    per_claim={t:sum(out_tokens[t])/sum(cands[t]) for t in cands}
    system_tokens={}
    for p in (CAL/'judge-r01').rglob('*.json'):
        rec=load(p);task=rec['meta'].get('task','layer3')
        system_tokens.setdefault(task,len(rec['request_body']['messages'][0]['content'].encode('utf8')))
    est={}
    for task,ps in packets.items():
        tin=tout=0
        for b,p in ps.items():
            msgs=P.layer3_messages(p) if task=='layer3' else P.layer4_messages(p,task)
            tin+=len(msgs[1]['content'].encode('utf8'))/bpt+len(msgs[0]['content'])  # system text is mostly CJK: ~1 token per char (upper bound)
            n=len(p.get('claims_candidates',[]))
            tout+=per_claim['grounding']*n if task=='grounding' else sum(out_tokens[task])/len(out_tokens[task])
        est[task]={'packets':len(ps),'input_tokens':round(tin),'output_tokens':round(tout)}
    g=est['grounding'];est['factuality']={'packets':g['packets'],'input_tokens':round(g['input_tokens']*0.8),
        'output_tokens':round(g['output_tokens']*sum(out_tokens['factuality'])/max(1,sum(out_tokens['grounding']))),
        'note':'exported after grounding; approximated from grounding size'}
    primary={k:dict(v) for k,v in est.items()}
    sec_factor=0.2  # fixed secondary sample is one fifth of cells per layer/task
    total_in=sum(v['input_tokens'] for v in est.values())*(1+sec_factor)
    total_out=sum(v['output_tokens'] for v in est.values())*(1+sec_factor)
    def usd(hit_share,tier):
        p=J.PRICE[tier];return round((total_in*hit_share*p['input_cache_hit']+total_in*(1-hit_share)*p['input_cache_miss']+total_out*p['output'])/1e6,2)
    cal_hit=sum(load(p)['usage_total']['prompt_cache_hit_tokens'] for p in (CAL/'judge-r01').rglob('*.json'))/sum(load(p)['usage_total']['prompt_tokens'] for p in (CAL/'judge-r01').rglob('*.json'))
    return {'primary_by_task':primary,'secondary_factor':sec_factor,'adjudication':'not included (up to 360 more packets)',
            'total_input_tokens':round(total_in),'total_output_tokens':round(total_out),'english_bytes_per_token_6A':round(bpt,3),
            'calibration_cache_hit_share':round(cal_hit,3),
            'estimated_usd':{'off_peak_no_cache':usd(0,'off_peak'),'off_peak_cal_cache_share':usd(cal_hit,'off_peak'),
                             'peak_no_cache':usd(0,'peak'),'peak_cal_cache_share':usd(cal_hit,'peak')},
            'unique_packets':{t:len(p) for t,p in packets.items()},'cells':len(rows),
            'limitation':'order-of-magnitude estimate; actual tokenization, caching and claim counts differ'}


def gate(revision):
    comp=load(CAL/f'calibration-comparison-{revision}.json')
    proj=projection()
    l3,l4=comp['layer3'],comp['layer4']
    record={'status':'failed','stage':'6B judge calibration','judge_model':J.JUDGE['model'],'judge_config':J.JUDGE,
            'comparison_path':(CAL/f'calibration-comparison-{revision}.json').relative_to(ROOT).as_posix(),
            'comparison_sha256':sha(CAL/f'calibration-comparison-{revision}.json'),
            'plan_sha256':sha(CAL/f'calibration-plan-{revision}.json'),
            'layer3':{'ac_exact_agreement':l3['ac_exact_agreement'],'ac_threshold':0.9,'claim_micro_agreement':l3['claim_micro_agreement'],
                      'claim_threshold':0.9,'sentinels':l3['sentinels'],'sentinels_passed':l3['sentinels_passed'],'passed':l3['passed'],
                      'disagreements':l3['disagreements']},
            'layer4':{'metrics':l4['metrics'],'threshold_each':0.95,'sentinels':l4['sentinels'],'failures':l4['failures'],'status':l4['status']},
            'failure_reasons':[r for r,bad in [('Layer 3 sentinels alternative_group_splicing (calibration-026) and missing_integration (calibration-040) failed',not l3['sentinels_passed']),
                                               (f'Layer 4 citation agreement {l4["metrics"]["citation"]["agreement"]:.3f} < 0.95',not l4['metrics']['citation']['passed']),
                                               (f'Layer 4 behavior agreement {l4["metrics"]["behavior"]["agreement"]:.3f} < 0.95',not l4['metrics']['behavior']['passed']),
                                               ('Layer 4 sentinels cal-31 relation splicing and cal-32 unqualified partial completion failed (citation schema)',any(not s['passed'] for s in l4['sentinels']))] if bad],
            'harness_check':'offset location problems: none; the disagreements are label disagreements on correctly located claims/citations, not parsing failures',
            'action':'blocked: no research packet judged; thresholds, rubrics and prompts unchanged; no second calibration pass (would be selection by result)',
            'calls':comp['calls'],'retries':comp['retries'],'usage':comp['usage'],'cost_usd':comp['cost_usd'],
            'research_cost_projection':proj,'human_verified':False}
    save_json(OUT/f'calibration-gate-{revision}.json',record)
    print(json.dumps({'status':record['status'],'reasons':record['failure_reasons'],'projection_usd':proj['estimated_usd'],'tokens':[proj['total_input_tokens'],proj['total_output_tokens']]},ensure_ascii=False))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--revision',default='r01');a=ap.parse_args();gate(a.revision)
