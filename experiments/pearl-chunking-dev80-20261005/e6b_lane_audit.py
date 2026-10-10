"""Session 6B read-only audit: label distributions per contiguous blind-ID range of one judged task directory.

Blind order is a seed-20261005 shuffle, so ranges handled by different judge contexts should show similar
label distributions; a large shift points to a judge-context effect, not an answer effect. Also reports the
share of merged (multi-tuple) Source blocks per configuration, read through the evaluation-side identity map.
Ranges are passed explicitly (taken from run-notes). Assigns no labels and changes no response.

--consistency (behavior, factuality; added in T5a after F7 was evaluated with the frozen file) runs the same permutation null on
segment x label tables as a flagged-not-gated diagnostic; f7() is unchanged.

--f7 adds the citation-redo acceptance statistics (6b-work-plan F7; standard e6b_workpackage.F7_STANDARD): Pearson X2
of segment x pair label (S1) and of segment x citation_extraction_unknown (S2), and S3 = the largest absolute gap between
a segment's unknown pair share and that of all other segments pooled (segments with >= 30 packets); each against the same
10,000 packet-level permutations (seed 20261005, segment packet counts kept).

Usage: python e6b_lane_audit.py <period>/<task> <name>=<first>-<last>[,<first>-<last>...] ... --out <json under RUN/research> [--f7] [--consistency]
"""
from __future__ import annotations
import argparse
import json
import random
import re
from collections import Counter
from runtime import ROOT, EXP, sha, save_json

WP=ROOT/'paper/pearl-6b-judge-workpackage'
RUN=ROOT/'outputs/pearl-chunking-dev80-20261007-16'
IDMAP=RUN/'research/research-identity-map-r01.json'
HEADER=re.compile(r'^\[Source (\[\[.*?\]\])\]',re.M)
PAIR_LABELS=('supported','partial','unsupported','contradicted','unknown','invalid','outside-context')
F7={'seed':20261005,'permutations':10000,'S1_p_min':0.01,'S2_p_min':0.01,'S3_p_min':0.01,'S3_min_packets':30,'pseudo_segments':4}


def packet(d,blind):return json.loads(json.loads((d/'packets'/f'{blind}.json').read_text(encoding='utf8'))['user_message'].split('\n',1)[1])


def dist(counter):
    n=sum(counter.values());return {'n':n,'share':{k:round(v/n,4) for k,v in sorted(counter.items(),key=lambda x:str(x[0]))} if n else {}}


def inside(n,spans):return any(a<=n<=b for a,b in spans)


def audit(task_dir,ranges):
    d=WP/task_dir;man=json.loads((d/'manifest.json').read_text(encoding='utf8'));task=man['task'];out={}
    for name,spans in ranges.items():
        claims,pairs,labels=Counter(),Counter(),Counter();files=0
        for i in man['index']:
            n=int(i['job_id'].rsplit('-',1)[1])
            if not inside(n,spans):continue
            r=json.loads((d/'responses'/f'{i["job_id"]}.json').read_text(encoding='utf8'));files+=1
            if task=='grounding':
                for c in r['claims']:claims[c.get('label')]+=1
                for p in r['citation_pairs']:pairs[p.get('label')]+=1
            elif task=='citation':
                for p in r['citation_pairs']:pairs[p.get('label')]+=1
                labels[bool(r.get('citation_extraction_unknown'))]+=1
            elif task=='behavior':
                labels[r['behavior']]+=1;claims[bool(r.get('unsupported_completion'))]+=1;pairs[bool(r.get('abstains_from_unsupported_completion'))]+=1
            elif task=='factuality':
                for c in r['claims']:claims[c.get('label')]+=1
            elif task=='answerability':labels[r['answerability']]+=1
            elif task=='layer3':
                for k in ('targets','conditions','claims'):
                    for v in r['decision'][k].values():labels[v]+=1
        extra={'claims':dist(claims),'citation_pairs':dist(pairs)} if task=='grounding' else \
              {'citation_pairs':dist(pairs),'citation_extraction_unknown':dist(labels)} if task=='citation' else               {'labels':dist(labels),'unsupported_completion':dist(claims),'abstains_from_unsupported_completion':dist(pairs)} if task=='behavior' else               {'claims':dist(claims)} if task=='factuality' else {'labels':dist(labels)}
        out[name]={'range':list(spans[0]) if len(spans)==1 else [list(x) for x in spans],'responses':files,**extra}
    return task,man,out


def x2(rows):
    """Pearson X2 of a segments x categories count table; empty rows and columns are dropped."""
    rows=[r for r in rows if sum(r)];cols=[sum(c) for c in zip(*rows)] if rows else [];n=sum(cols)
    if len(rows)<2 or not n:return 0.0
    keep=[j for j,c in enumerate(cols) if c];out=0.0
    for r in rows:
        t=sum(r)
        for j in keep:
            e=t*cols[j]/n;out+=(r[j]-e)**2/e
    return out


def f7(task_dir,ranges):
    """F7 statistics on one judged citation directory (also usable on primary grounding citation_pairs as a known-positive check)."""
    d=WP/task_dir;man=json.loads((d/'manifest.json').read_text(encoding='utf8'));order=[i['job_id'] for i in man['index']]
    owner={j:[name for name,spans in ranges.items() if inside(int(j.rsplit('-',1)[1]),spans)] for j in order}
    bad={j:v for j,v in owner.items() if len(v)!=1}
    if bad:return {'status':'not_evaluable','reason':'ranges do not cover every packet exactly once','examples':dict(list(bad.items())[:10])}
    names=list(ranges);pseudo=False
    if len(names)<2:
        q=len(order);cut=[round(q*k/F7['pseudo_segments']) for k in range(F7['pseudo_segments']+1)]
        names=[f'pseudo{k+1}' for k in range(F7['pseudo_segments'])];owner={j:[names[k]] for k in range(len(names)) for j in order[cut[k]:cut[k+1]]};pseudo=True
    vec={}
    for j in order:
        r=json.loads((d/'responses'/f'{j}.json').read_text(encoding='utf8'))
        c=Counter(p.get('label') for p in r['citation_pairs'])
        if any(k not in PAIR_LABELS for k in c):return {'status':'not_evaluable','reason':f'{j}: pair label outside the frozen set'}
        x=bool(r.get('citation_extraction_unknown'))
        vec[j]=([c[k] for k in PAIR_LABELS],[int(x),int(not x)])
    seg={n:[j for j in order if owner[j]==[n]] for n in names}
    def tables(assign):
        a={n:[[0]*len(PAIR_LABELS),[0,0]] for n in names}
        for n,js in assign.items():
            t=a[n]
            for j in js:
                p,x=vec[j]
                for k,v in enumerate(p):t[0][k]+=v
                t[1][0]+=x[0];t[1][1]+=x[1]
        return x2([a[n][0] for n in names]),x2([a[n][1] for n in names]),gaps(a),a
    ui=PAIR_LABELS.index('unknown');big=[n for n in names if len(seg[n])>=F7['S3_min_packets']]
    def gaps(a):
        tot=[sum(a[n][0][k] for n in names) for k in range(len(PAIR_LABELS))];out={}
        for n in big:
            own=a[n][0];rest=[t-o for t,o in zip(tot,own)]
            if sum(own) and sum(rest):out[n]=own[ui]/sum(own)-rest[ui]/sum(rest)
        return out
    s1,s2,u,obs=tables(seg);s3=max((abs(v) for v in u.values()),default=None)
    rng=random.Random(F7['seed']);pool=list(order);sizes=[len(seg[n]) for n in names];g1=g2=g3=0
    for _ in range(F7['permutations']):
        rng.shuffle(pool);assign={};k=0
        for n,m in zip(names,sizes):assign[n]=pool[k:k+m];k+=m
        a1,a2,a3,_=tables(assign);g1+=a1>=s1-1e-9;g2+=a2>=s2-1e-9
        if s3 is not None:g3+=max((abs(v) for v in a3.values()),default=0)>=s3-1e-9
    n_=F7['permutations'];p1=(1+g1)/(1+n_);p2=(1+g2)/(1+n_);p3=(1+g3)/(1+n_) if s3 is not None else None
    met=p1>=F7['S1_p_min'] and p2>=F7['S2_p_min'] and (p3 is None or p3>=F7['S3_p_min'])
    return {'status':'met' if met else 'not_met','standard':F7,'pseudo_segments':pseudo,
            'segments':{n:{'packets':len(seg[n]),'pairs':sum(obs[n][0]),'pair_labels':dict(zip(PAIR_LABELS,obs[n][0])),
                           'citation_extraction_unknown':obs[n][1][0]} for n in names},
            'S1':{'x2':round(s1,4),'p':round(p1,5)},'S2':{'x2':round(s2,4),'p':round(p2,5)},
            'S3':{'max_abs_unknown_gap':None if s3 is None else round(s3,4),'p':None if p3 is None else round(p3,5),
                  'segments_eligible':big,'gaps':{n:round(v,4) for n,v in u.items()}}}


CONSISTENCY={'behavior':{'behavior':('full_answer','bounded_partial','pure_abstain','ambiguous'),'unsupported_completion':(True,False),
                         'abstains_from_unsupported_completion':(True,False)},
             'factuality':{'claim_label':('true','false','unknown')}}


def consistency(task_dir,ranges):
    """Diagnostic for behavior and factuality (no frozen gate exists for these tasks; F7 is the citation standard): Pearson X2 of
    segment x label for each table in CONSISTENCY and, for factuality, the largest unknown-share gap (segments >= 30 packets),
    each against the F7 null (10,000 whole-packet reassignments, segment sizes kept, seed 20261005). p < 0.01 is flagged, not gated."""
    d=WP/task_dir;man=json.loads((d/'manifest.json').read_text(encoding='utf8'));task=man['task'];order=[i['job_id'] for i in man['index']]
    owner={j:[name for name,spans in ranges.items() if inside(int(j.rsplit('-',1)[1]),spans)] for j in order}
    bad={j:v for j,v in owner.items() if len(v)!=1}
    if bad:return {'status':'not_evaluable','reason':'ranges do not cover every packet exactly once','examples':dict(list(bad.items())[:10])}
    tabs=CONSISTENCY[task];names=list(ranges);vec={}
    for j in order:
        r=json.loads((d/'responses'/f'{j}.json').read_text(encoding='utf8'))
        if task=='behavior':vec[j]={'behavior':[int(r['behavior']==k) for k in tabs['behavior']],
                                    **{t:[int(bool(r.get(t))==k) for k in tabs[t]] for t in ('unsupported_completion','abstains_from_unsupported_completion')}}
        else:
            c=Counter(x.get('label') for x in r['claims']);vec[j]={'claim_label':[c[k] for k in tabs['claim_label']]}
    seg={n:[j for j in order if owner[j]==[n]] for n in names};big=[n for n in names if len(seg[n])>=F7['S3_min_packets']]
    def stats(assign):
        a={t:{n:[sum(vec[j][t][k] for j in assign[n]) for k in range(len(cats))] for n in names} for t,cats in tabs.items()}
        out={t:x2([a[t][n] for n in names]) for t in tabs}
        if task=='factuality':
            ui=tabs['claim_label'].index('unknown');tot=[sum(a['claim_label'][n][k] for n in names) for k in range(3)];g={}
            for n in big:
                own=a['claim_label'][n];rest=[t-o for t,o in zip(tot,own)]
                if sum(own) and sum(rest):g[n]=own[ui]/sum(own)-rest[ui]/sum(rest)
            out['unknown_gap']=max((abs(v) for v in g.values()),default=None);out['_gaps']=g
        return out,a
    obs,tab=stats(seg);keys=[k for k in obs if not k.startswith('_') and obs[k] is not None];ge=dict.fromkeys(keys,0)
    rng=random.Random(F7['seed']);pool=list(order);sizes=[len(seg[n]) for n in names]
    for _ in range(F7['permutations']):
        rng.shuffle(pool);assign={};k=0
        for n,m in zip(names,sizes):assign[n]=pool[k:k+m];k+=m
        s,_=stats(assign)
        for t in keys:ge[t]+=(s[t] if s[t] is not None else 0)>=obs[t]-1e-9
    p={t:round((1+ge[t])/(1+F7['permutations']),5) for t in keys}
    return {'status':'flagged' if any(v<0.01 for v in p.values()) else 'not_flagged','gate':False,'null':'F7 permutation null (seed 20261005, 10,000)',
            'statistics':{t:{'value':round(obs[t],4),'p':p[t]} for t in keys},'gaps':{n:round(v,4) for n,v in obs.get('_gaps',{}).items()},
            'segments':{n:{'packets':len(seg[n]),**{t:dict(zip(map(str,cats),tab[t][n])) for t,cats in tabs.items()}} for n in names}}


def merged_share(task_dir):
    d=WP/task_dir;m=json.loads(IDMAP.read_text(encoding='utf8'));task=json.loads((d/'manifest.json').read_text(encoding='utf8'))['task'];st={}
    for b in m['bindings'][task]:
        arm=m['cells'][b['cells'][0]]['arm'];hs=[json.loads(h) for h in HEADER.findall(packet(d,b['blind_id'])['context'])]
        s=st.setdefault(arm,[0,0]);s[0]+=len(hs);s[1]+=sum(len(h)>1 for h in hs)
    return {arm:{'source_blocks':t,'merged_blocks':mu,'share':round(mu/t,4)} for arm,(t,mu) in sorted(st.items())}


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('task_dir');ap.add_argument('ranges',nargs='+');ap.add_argument('--out',required=True);ap.add_argument('--f7',action='store_true');ap.add_argument('--consistency',action='store_true');a=ap.parse_args()
    ranges={}
    for r in a.ranges:
        name,spans=r.split('=');ranges[name]=[tuple(int(v) for v in s.split('-')) for s in spans.split(',')]
    task,man,res=audit(a.task_dir,ranges)
    rec={'schema_version':'pearl-e6b-lane-audit-v1','task_dir':a.task_dir,'task':task,'manifest_sha256':sha(WP/a.task_dir/'manifest.json'),
         'ranges_source':'judge run-notes (contexts per blind-ID range)','ranges':res,'auditor_sha256':sha(EXP/'e6b_lane_audit.py'),
         'note':'read-only distribution audit; no label assigned or changed'}
    if 'context' in packet(WP/a.task_dir,man['index'][0]['job_id']):rec['merged_source_blocks_by_configuration']=merged_share(a.task_dir)
    if a.f7:rec['f7']=f7(a.task_dir,ranges)
    if a.consistency:rec['consistency_diagnostic']=consistency(a.task_dir,ranges)
    save_json(RUN/'research'/a.out,rec);print(json.dumps(res,ensure_ascii=False)[:1500])
