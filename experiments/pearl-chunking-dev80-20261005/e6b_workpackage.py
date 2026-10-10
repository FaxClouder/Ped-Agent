"""Session 6B via an external Agent judge (ChatGPT): export blind work packages and import responses.

The same frozen messages the API harness would send (e6b_calibrate.jobs / e6b_prompts) are exported
to paper/pearl-6b-judge-workpackage/<phase>/ as distinct system prompts plus per-packet user content.
The external judge writes one JSON object per packet to responses/. Import wraps each response in
the e6b judge-record schema (no usage, no provider), so the frozen comparison (e6b_calibrate.compare,
which imports the frozen score.py / compare_calibration.py) runs unchanged on a new revision.

Phases:
  calibration      revision cgpt-r01: messages identical to the API calibration plan r01
  calibration-r02  revision cgpt-r02: identical except that the Layer 4 behavior system prompt ends with
                   e6b-behavior-addendum-r02.md (definition clarification of unsupported_completion,
                   written after cgpt-r01 failed; protocol: revise prompt as r02, keep r01, recalibrate)

Research periods (6B T1; rules = the passed calibration cgpt-r02 system prompts, checked by SHA at export):
  research-primary-1  Layer 3, answerability, grounding/citation: no label dependency on any other task
  research-primary-2  behavior (protocol: judged only after answerability is fixed; the packet never carries the
                      answerability label) and factuality (packets carry the claims selected by primary grounding);
                      exported in T3b after primary-1 is imported: behavior = e6b_packets.build() packets, system prompt
                      with the r02 addendum (SHA-equal to cgpt-r02); factuality = one packet per primary grounding answer
                      with claims (claim_id, verbatim text, located occurrences; no labels, no context), numbered as that
                      grounding packet, facts from the user-approved facts-r03 (decision record), shaped as the historical
                      Layer 4 fact packets; answers without claims are NA and not exported. The factuality bindings are
                      frozen evaluation-side (factuality-bindings-primary-2-r01.json); the identity map and secondary
                      sample must reproduce unchanged
Research packets come from e6b_packets.build() (blind order seed 20261005, exact-duplicate bindings). The
evaluation-side identity map and the fixed secondary sample are frozen in RUN/research/ at the first research
export, before any research label exists. Each task is a separate directory judged in its own conversation;
workpackage manifests carry no cell, arm, intent or replicate identity.

Research import (T3a): checks the period and task manifests against the frozen export record, every packet file
against its manifest, and every packet against a fresh e6b_packets.build() (messages and canonical packet SHA, which
also re-verifies the frozen identity map and secondary sample); validates every response with the workpackage
validator plus a Layer 3 ID-set check; then keeps a read-only received copy and imports from that copy, binding each
blind ID to its cells. Grounding claim offsets come from the frozen e6b_prompts.locate_grounding; the grounding
citation_pairs (and citation_extraction_unknown) are retained verbatim, marked superseded (deviation D4), and never
located or scored. Judge identity is taken from the run-notes (sub-agent contexts; model and effort unknown).

Citation redo r03 (6b-work-plan F2-F7; deviation D8). The first-period citation labels diverged by judge context on
merged Source blocks (D4), so citations are judged again in one new format. F2: e6b_fragments derives every fragment's
Unicode [start,end) in the context from the block header intervals (context unchanged); fragments-audit checks all 240
E5 contexts against the frozen assembly records and source views and freezes the result. F3: a citation packet is the
grounding packet with claims_candidates replaced by the fixed primary claims (claim_id, verbatim text, located
occurrences; no labels), source_fragments added after context, and the r03 instruction; an answer whose primary grounding
has no claims is exported too (only an empty citation_pairs validates; as calibration anchor cal-33). F4: the system prompt is the cgpt-r02 grounding prompt with its
frozen rules byte-identical (checked by SHA) and only the output-format section replaced by the r03 input-format note
(e6b-citation-input-format-r03.md) plus the citation-only output format. F5: calibration-citation-r03 re-judges the 40
grounding anchors with claims fixed from the passed cgpt-r02 responses; compare_citation runs the frozen
compare_calibration.compare unchanged with every non-citation field taken from cgpt-r02, and the gate reads the citation
metrics only, at the original threshold. The research export (research-citation-r03) refuses to run until that gate
passed, and freezes the F7 standard (F7_STANDARD) in its export record.

Research import T5a: research-primary-2 reuses the T3a checks with factuality packets rebuilt from the imported primary grounding and
verified against the frozen factuality bindings; factuality labels are joined to the packet claims (verbatim text, located occurrences);
judge contexts and their blind-ID ranges are T5A_JUDGE_CONTEXTS, transcribed from the run-notes. research-citation-r03 import rebuilds the
redo packets, checks them against the frozen citation bindings, validates every response with the validator frozen at export, locates
citation offsets with the frozen locator, and marks the primary-1 citation_pairs as superseded by the redo (left unchanged). citation-f7
evaluates the F7 standard frozen in the redo export record with the e6b_lane_audit.py frozen with it.

Commands: export / validate / import / compare, each with --phase (compare: calibration phases only); citation-f7 (no --phase);
facts-check (no --phase) writes the facts-r03 provenance record for the user's decision;
fragments-audit (no --phase) writes the F2 audit; citation-dryrun (no --phase) builds the research citation packets in
memory only and writes the redo design record.
"""
from __future__ import annotations
import argparse
import importlib.util
import inspect
import json
import os
import re
import shutil
import stat
from datetime import datetime, timezone
from pathlib import Path
from runtime import ROOT, EXP, sha, save_json
import e6b_judge as J
import e6b_calibrate as C
import e6b_packets as K
import e6b_prompts as P
import e6b_fragments as F

WP=ROOT/'paper/pearl-6b-judge-workpackage'
RUN=ROOT/'outputs/pearl-chunking-dev80-20261007-16'
API_PLAN=ROOT/'outputs/pearl-chunking-dev80-20261006-15/calibration/calibration-plan-r01.json'
ADDENDUM=EXP/'e6b-behavior-addendum-r02.md'
PHASES={'calibration':{'rev':'cgpt-r01','addendum':None},'calibration-r02':{'rev':'cgpt-r02','addendum':ADDENDUM}}
RESEARCH=RUN/'research'
CAL_R02_MANIFEST=WP/'calibration-r02/manifest.json'
PERIODS={'research-primary-1':{'rev':'cgpt-research-r01','stage':'primary','tasks':('layer3','answerability','grounding'),'requires':None},
         'research-primary-2':{'rev':'cgpt-research-r01','stage':'primary','tasks':('behavior','factuality'),'requires':'research-primary-1'}}
CONVERSATION={'layer3':'A','answerability':'B','grounding':'C','behavior':'D','factuality':'E'}
DEPENDENCIES={'layer3':'none (frozen semantic reference only)','answerability':'none (query, context, requirements; no answer)',
              'grounding':'none (query, context, answer; no independent facts)',
              'behavior':'order only: answerability primary labels imported and hashed first (Layer 4 protocol); packet carries no answerability label',
              'factuality':'content: claims selected by primary grounding, plus independent facts-r03; no context'}
JUDGE={'kind':'external_agent','product':'Codex desktop app session (OpenAI; per judge run notes)','model_reported_by_user':'sol6.1','reasoning_effort_reported_by_user':'medium',
       'model_per_run_notes':'described as GPT-6-based Codex by its developer instructions; exact model ID and reasoning effort not exposed (null); sol6.1 not confirmed',
       'model_verified':False,'single_thread':True,'subagents':False,'operator':'user runs the judge in the same local repository; responses imported by file',
       'note':'identity as stated by the user and the judge run notes; this session cannot verify the executed model'}


def now():return datetime.now(timezone.utc).isoformat()


def system_name(meta):return 'layer3' if meta['layer']=='layer3' else 'layer4-'+meta['task']


def phase_jobs(phase):
    """Frozen jobs for the phase revision; r02 appends the behavior addendum to the behavior system prompt only."""
    cfg=PHASES[phase];rows=C.jobs(cfg['rev'])
    if not cfg['addendum']:return rows
    add=cfg['addendum'].read_text(encoding='utf8').strip();out=[]
    for job_id,messages,o,meta in rows:
        if meta['layer']=='layer4' and meta['task']=='behavior':
            messages=[dict(messages[0],content=messages[0]['content']+'\n\n'+add),messages[1]]
        out.append((job_id,messages,o,meta))
    return out


def export(phase):
    d=WP/phase;cfg=PHASES[phase]
    if d.exists():raise FileExistsError(d)
    (d/'system-prompts').mkdir(parents=True);(d/'packets').mkdir();(d/'responses').mkdir()
    rows=phase_jobs(phase);systems={};index=[]
    for job_id,messages,_,meta in rows:
        name=system_name(meta);sysmsg=messages[0]['content']
        if name in systems:assert systems[name]==sysmsg,'system prompt differs within one task'
        else:systems[name]=sysmsg;(d/'system-prompts'/f'{name}.md').write_text(sysmsg,encoding='utf8',newline='\n')
        packet={'job_id':job_id,'system_prompt':f'system-prompts/{name}.md','system_prompt_sha256':J.text_sha(sysmsg),
                'user_message':messages[1]['content'],'messages_sha256':J.text_sha(J.canon(messages)),
                'identity_field':('packet_id' if meta['layer']=='layer3' else 'anchor_id'),
                'identity_value':(meta['packet_id'] if meta['layer']=='layer3' else meta['anchor_id']),
                'response_file':f'responses/{job_id}.json'}
        p=d/'packets'/f'{job_id}.json'
        with p.open('x',encoding='utf8',newline='\n') as f:json.dump(packet,f,ensure_ascii=False,indent=1);f.write('\n')
        index.append({'job_id':job_id,'packet_file':f'packets/{job_id}.json','packet_file_sha256':sha(p),'messages_sha256':packet['messages_sha256'],
                      'system_prompt':name,'layer':meta['layer'],'task':meta.get('task','layer3')})
    plan=C.load(API_PLAN);api={p['job_id']:p['messages_sha256'] for p in plan['packets']}
    changed=[i['job_id'] for i in index if api[i['job_id']]!=i['messages_sha256']]
    save_json(d/'manifest.json',{'phase':phase,'revision':cfg['rev'],'created_utc':now(),'packets':len(index),'system_prompts':{k:J.text_sha(v) for k,v in systems.items()},
        'identical_messages_to_api_calibration_plan_r01':not changed,'messages_changed_vs_api_plan_r01':len(changed),
        'addendum':(cfg['addendum'].relative_to(ROOT).as_posix() if cfg['addendum'] else None),'addendum_sha256':(sha(cfg['addendum']) if cfg['addendum'] else None),
        'contains_expected_labels':False,'index':index,'exporter_sha256':sha(EXP/'e6b_workpackage.py')})
    print(json.dumps({'phase':phase,'packets':len(index),'system_prompts':sorted(systems),'messages_changed_vs_api_plan_r01':len(changed)}))


def validate(phase_dir):
    """Structural checks only; labels are not judged here."""
    man=json.loads((phase_dir/'manifest.json').read_text(encoding='utf8'));problems=[];ok=0
    need={'layer3':['packet_id','decision','rationale'],'answerability':['anchor_id','answerability','reason'],
          'grounding':['anchor_id','claims','citation_pairs'],'factuality':['anchor_id','claims'],'behavior':['anchor_id','behavior','refusal_reason']}
    for i in man['index']:
        r=phase_dir/'responses'/f'{i["job_id"]}.json'
        if not r.exists():problems.append((i['job_id'],'missing'));continue
        try:obj=json.loads(r.read_text(encoding='utf8'))
        except Exception as e:problems.append((i['job_id'],f'json:{e}'));continue
        if not isinstance(obj,dict):problems.append((i['job_id'],'not an object'));continue
        miss=[k for k in need[i['task']] if k not in obj]
        if miss:problems.append((i['job_id'],f'missing keys {miss}'));continue
        if i['layer']=='layer3' and not all(isinstance(obj['decision'].get(k),dict) for k in ('targets','conditions','claims')):problems.append((i['job_id'],'decision.targets/conditions/claims must be objects'));continue
        ok+=1
    return ok,problems,man


def write_plan(phase):
    """Plan record for the frozen compare(): thresholds/rules copied verbatim from the API plan r01."""
    cfg=PHASES[phase];base=C.load(API_PLAN);man=C.load(WP/phase/'manifest.json')
    save_json(RUN/'calibration'/f'calibration-plan-{cfg["rev"]}.json',{'status':'written_at_import','revision':cfg['rev'],'phase':phase,'judge':JUDGE,
        'note':'Packets were exported (manifest) before the external judge ran; this record is written at import time and copies thresholds and comparison rules unchanged from calibration-plan-r01.',
        'workpackage_manifest_sha256':sha(WP/phase/'manifest.json'),'messages_identical_to_plan_r01':man['identical_messages_to_api_calibration_plan_r01'],
        'addendum':man.get('addendum'),'addendum_sha256':man.get('addendum_sha256'),
        'base_plan':API_PLAN.relative_to(ROOT).as_posix(),'base_plan_sha256':sha(API_PLAN),
        'thresholds':base['thresholds'],'layer3_comparison_rules':base['layer3_comparison_rules'],'layer4_comparison':base['layer4_comparison'],
        'judge_reads_expected':False,'on_failure':base['on_failure']})


def do_import(phase):
    d=WP/phase;cfg=PHASES[phase];ok,problems,man=validate(d)
    if problems:raise SystemExit(f'{len(problems)} invalid/missing responses, e.g. {problems[:5]}')
    notes=d/'run-notes.md'
    if not notes.exists():raise SystemExit('run-notes.md (judge identity, times, files read) is required before import')
    if phase=='calibration':RUN.mkdir(exist_ok=False);(RUN/'calibration').mkdir()
    elif not RUN.is_dir():raise SystemExit('run dir missing')
    shutil.copytree(d,RUN/f'workpackage-{phase}-received')  # immutable evidence of what was imported
    C.CAL=RUN/'calibration'  # route the frozen comparison to the new run dir
    rows=phase_jobs(phase);idx={i['job_id']:i for i in man['index']}
    for job_id,messages,out,meta in rows:
        assert J.text_sha(J.canon(messages))==idx[job_id]['messages_sha256'],'prompt drift since export'
        resp=d/'responses'/f'{job_id}.json';content=resp.read_text(encoding='utf8');parsed=json.loads(content)
        out.parent.mkdir(parents=True,exist_ok=True)
        rec={'schema_version':'pearl-e6b-judge-record-v1','job_id':job_id,'status':'judged','meta':meta,'judge':JUDGE,
             'request_sha256':None,'messages_sha256':idx[job_id]['messages_sha256'],'request_body':{'messages':messages},
             'attempts':[{'number':1,'source':'external agent response file','response_file_sha256':sha(resp),'error':None}],
             'final_response_raw':content,'final_response_sha256':J.text_sha(content),'content':content,'parsed':parsed,
             'usage_total':{'prompt_tokens':0,'completion_tokens':0,'prompt_cache_hit_tokens':0,'prompt_cache_miss_tokens':0},
             'cost_usd_total':{'off_peak':0.0,'peak':0.0,'rule_tier':0.0},'human_verified':False,
             'identity_note':'external Agent judge (ChatGPT) response imported from file; model as reported by the user'}
        with out.open('x',encoding='utf8',newline='\n') as f:json.dump(rec,f,ensure_ascii=False,indent=1);f.write('\n')
    save_json(RUN/f'import-calibration-{cfg["rev"]}.json',{'time_utc':now(),'phase':phase,'judge':JUDGE,'responses':ok,'manifest_sha256':sha(d/'manifest.json'),
        'run_notes_sha256':sha(notes),'importer_sha256':sha(EXP/'e6b_workpackage.py'),'thresholds':'unchanged (same as calibration-plan-r01)',
        'comparison':'frozen e6b_calibrate.compare (imports frozen score.py and compare_calibration.py)'})
    write_plan(phase);C.compare(cfg['rev'],f'calibration-comparison-{cfg["rev"]}.json')


def compare_only(phase):
    C.CAL=RUN/'calibration';write_plan(phase);C.compare(PHASES[phase]['rev'],f'calibration-comparison-{PHASES[phase]["rev"]}.json')


def research_messages(task,packet):
    """Same assembly as calibration-r02: frozen prompts; behavior alone ends with the r02 addendum."""
    if task=='layer3':return P.layer3_messages(packet)
    m=P.layer4_messages(packet,task)
    if task=='behavior':m=[dict(m[0],content=m[0]['content']+'\n\n'+ADDENDUM.read_text(encoding='utf8').strip()),m[1]]
    return m


def freeze_or_check(path,value):
    """Exclusive write on first export; later exports must reproduce the frozen record exactly."""
    if path.exists():
        if C.load(path)!=json.loads(json.dumps(value,ensure_ascii=False)):raise ValueError(f'research freeze drift: {path}')
        return 'verified_unchanged'
    save_json(path,value);return 'written'


def research_freeze(built):
    rows,order,packets,bindings,secondary,c2p=built
    RESEARCH.mkdir(parents=True,exist_ok=True)
    idmap={'schema_version':'pearl-e6b-identity-map-v1','note':'evaluation-side only; never sent to the judge','seed':K.SEED,
           'builder':'experiments/pearl-chunking-dev80-20261005/e6b_packets.py','blind_cell_order':[c['cell_id'] for c in order],
           'cells':{c['cell_id']:{k:c[k] for k in ('arm','intent_id','replicate','response_sha256','context_sha256','record_path','record_sha256')} for c in rows},
           'bindings':{t:[{'blind_id':v['blind_id'],'cells':v['cells'],'packet_canonical_sha256':J.text_sha(J.canon(packets[t][v['blind_id']]))} for v in b.values()]
                       for t,b in bindings.items()},
           'cell_to_packet':c2p}
    sec={'schema_version':'pearl-e6b-secondary-sample-v1','status':'frozen_before_research_labels',
         'rule':'every fifth cell of the seed-20261005 shuffled 720-cell order, per layer/task','cells':secondary,
         'unique_packets':{t:sorted({c2p[t][x] for x in v}) for t,v in secondary.items() if t in c2p},
         'factuality_note':'factuality secondary packets are exported after primary grounding selection, for the same fixed cells',
         'units_cap':{'layer3_secondary':144,'layer4_secondary':576}}
    a=RESEARCH/'research-identity-map-r01.json';b=RESEARCH/'secondary-sample-r01.json'
    return {'identity_map':(a,freeze_or_check(a,idmap)),'secondary_sample':(b,freeze_or_check(b,sec))}


IMPORT_P1=RESEARCH/'import-research-primary-1.json'
FACTS_DECISION=RESEARCH/'facts-r03-decision-r01.json'
FACT_BINDINGS=RESEARCH/'factuality-bindings-primary-2-r01.json'
FACT_SCOPE=('Only source quotes actually frozen in facts-r03, unseen additions remain unknown. Source evidence starts relative to original full source text; '
            'selected quote char_start/char_end identify full-text positions.')  # verbatim from the historical outputs/pearl-layer4-dev80-20261004-01/export_fact_packets_r01.py
BEHAVIOR_KEYS={'anchor_id','query','raw_answer','response_sha256','context','context_sha256','requirements','instruction'}
FACTUALITY_KEYS={'anchor_id','claims','fact_packet','instruction'}


def primary2_inputs(packets):
    """research-primary-2 preconditions (T3b): primary-1 imported and unchanged since import; facts-r03 approved by the user."""
    imp=C.load(IMPORT_P1);problems=[]
    for task,v in imp['tasks'].items():
        if sha(ROOT/v['rows'])!=v['rows_sha256']:problems.append((task,'imported rows changed since import'))
    rc=imp['received_copy']
    if J.text_sha(J.canon(tree_sha(ROOT/rc['path'])))!=rc['tree_sha256']:problems.append(('received_copy','tree differs from import record'))
    if sha(RESEARCH/'export-research-primary-1.json')!=imp['export_record_sha256']:problems.append(('export record','changed since import'))
    dec=C.load(FACTS_DECISION);rel=K.FACTS.relative_to(ROOT).as_posix();h=sha(K.FACTS)
    if dec['decision']!='approved_with_sensitivity_analysis' or dec['facts']!={'path':rel,'sha256':h}:problems.append(('facts','not the user-approved facts-r03'))
    if C.load(RESEARCH/'export-research-primary-1.json')['inputs_sha256'].get(rel)!=h:problems.append(('facts','SHA differs from the primary-1 export record'))
    if problems:raise SystemExit(f'research-primary-2 preconditions failed: {problems}')
    rows=[json.loads(x) for x in (ROOT/imp['tasks']['grounding']['rows']).read_text(encoding='utf8').splitlines()]
    if [r['blind_id'] for r in rows]!=list(packets['grounding']):raise SystemExit('grounding rows differ from the rebuilt grounding packets')
    for r in rows:
        if r['packet_canonical_sha256']!=J.text_sha(J.canon(packets['grounding'][r['blind_id']])):raise SystemExit(f'{r["blind_id"]}: grounding packet SHA drift')
    return imp,dec,rows


def factuality_packets(rows,idmap):
    """One packet per primary grounding answer that has claims; same number as the grounding packet. Claims keep the primary
    claim_id and verbatim text plus the harness-located occurrences (grounding labels, evidence, reasons and the context are
    not carried). Facts: the intent's facts-r03 evidence and supplementary facts, shaped as the historical Layer 4 fact packets.
    Packets whose inputs (all but anchor_id) are byte-identical to an earlier one are not exported again; their cells bind to it."""
    facts={x['intent_id']:x for x in C.load(K.FACTS)['items']};h=sha(K.FACTS)
    instruction=C.load(K.L4CAL/'factuality'/'cal-01.json')['instruction'];packets={};bindings=[];na=[];seen={}
    for r in rows:
        intents={idmap['cells'][c['cell_id']]['intent_id'] for c in r['cells']}
        if len(intents)!=1 or intents!={c['intent_id'] for c in r['cells']}:raise ValueError(f'{r["blind_id"]}: intent binding')
        intent=intents.pop();claims=[{'claim_id':c['claim_id'],'text':c['text'],'occurrences':c['occurrences']} for c in r['response']['claims']]
        if not claims:na.append({'grounding_blind_id':r['blind_id'],'cells':[c['cell_id'] for c in r['cells']],'factuality':'NA (no claims; not exported)'});continue
        item=facts[intent];inputs={'claims':claims,'fact_packet':{'version':'facts-r03','facts_sha256':h,'sources':item['evidence'],
              'supplementary_facts':item.get('supplementary_facts',[]),'scope':FACT_SCOPE},'instruction':instruction};key=J.canon(inputs)
        if key in seen:  # 5B exact-duplicate rule: byte-identical inputs are judged once and bound to every cell using them
            b=seen[key];b['grounding_blind_ids'].append(r['blind_id']);b['cells']+=[c['cell_id'] for c in r['cells']]
            b['grounding_response_file_sha256'].append(r['response_file_sha256']);continue
        blind='factuality-'+r['blind_id'].rsplit('-',1)[1];packets[blind]={'anchor_id':blind,**inputs}
        seen[key]={'blind_id':blind,'grounding_blind_ids':[r['blind_id']],'cells':[c['cell_id'] for c in r['cells']],'intent_id':intent,'claims':len(claims),
                   'grounding_response_file_sha256':[r['response_file_sha256']],'packet_canonical_sha256':J.text_sha(J.canon(packets[blind]))}
        bindings.append(seen[key])
    return packets,bindings,na


def period_packets(period,built):
    """Blind packets per task. primary-1: e6b_packets.build(); primary-2: build() behavior plus factuality from imported primary grounding."""
    packets=built[2]
    if period=='research-primary-1':return {t:packets[t] for t in PERIODS[period]['tasks']},None
    imp,dec,rows=primary2_inputs(packets);idmap=C.load(RESEARCH/'research-identity-map-r01.json')
    fact,bindings,na=factuality_packets(rows,idmap)
    for b,p in packets['behavior'].items():
        if set(p)!=BEHAVIOR_KEYS or set(p['requirements'])!={'task','necessary_conclusions','necessary_groups'}:raise ValueError(f'{b}: behavior packet fields (no answerability label allowed)')
    for b,p in fact.items():
        if set(p)!=FACTUALITY_KEYS or any(set(c)!={'claim_id','text','occurrences'} for c in p['claims']):raise ValueError(f'{b}: factuality packet fields')
    if sum(len(x['cells']) for x in bindings)+sum(len(x['cells']) for x in na)!=720:raise ValueError('factuality cells do not cover 720')
    record={'schema_version':'pearl-e6b-factuality-bindings-v1','note':'evaluation-side only; never sent to the judge','period':period,
            'claims_source':{'path':imp['tasks']['grounding']['rows'],'sha256':imp['tasks']['grounding']['rows_sha256'],'import_record_sha256':sha(IMPORT_P1)},
            'facts':dec['facts'],'facts_decision_sha256':sha(FACTS_DECISION),
            'rule':'one factuality packet per primary grounding packet with at least one claim, numbered as that grounding packet; claim_id and verbatim text kept; no context; answers without claims are NA and not exported',
            'exact_duplicates':'5B frozen rule: a packet whose inputs (all but anchor_id) are byte-identical to an earlier one is judged once; its grounding packets and cells are listed under the first',
            'grounding_packets_with_claims':sum(len(x['grounding_blind_ids']) for x in bindings),
            'merged_duplicates':[{'blind_id':x['blind_id'],'grounding_blind_ids':x['grounding_blind_ids']} for x in bindings if len(x['grounding_blind_ids'])>1],
            'packets':len(fact),'cells':sum(len(x['cells']) for x in bindings),'bindings':bindings,'not_exported_na':na}
    return {'behavior':packets['behavior'],'factuality':fact},{'record':record,'answerability_import_rows_sha256':imp['tasks']['answerability']['rows_sha256'],'import':imp}


def export_research(period):
    cfg=PERIODS[period]
    if cfg['requires'] and not (RESEARCH/f'import-{cfg["requires"]}.json').exists():raise SystemExit(f'{period} needs {cfg["requires"]} imported first')
    d=WP/period
    if d.exists():raise FileExistsError(d)
    built=K.build();frozen=research_freeze(built);cal=C.load(CAL_R02_MANIFEST)['system_prompts'];tasks={}
    packets,extra=period_packets(period,built)
    if extra:
        if any(a!='verified_unchanged' for _,a in frozen.values()):raise SystemExit('frozen research record was rewritten')
        frozen['factuality_bindings']=(FACT_BINDINGS,freeze_or_check(FACT_BINDINGS,extra['record']))
    for task in cfg['tasks']:
        name='layer3' if task=='layer3' else 'layer4-'+task;t=d/task;sysmsg=None;index=[]
        (t/'system-prompts').mkdir(parents=True);(t/'packets').mkdir();(t/'responses').mkdir()
        for blind,packet in packets[task].items():
            messages=research_messages(task,packet)
            if sysmsg is None:
                sysmsg=messages[0]['content']
                if J.text_sha(sysmsg)!=cal[name]:raise ValueError(f'{name} system prompt differs from calibration-r02')
                (t/'system-prompts'/f'{name}.md').write_text(sysmsg,encoding='utf8',newline='\n')
            elif messages[0]['content']!=sysmsg:raise ValueError('system prompt differs within one task')
            rec={'job_id':blind,'system_prompt':f'system-prompts/{name}.md','system_prompt_sha256':J.text_sha(sysmsg),
                 'user_message':messages[1]['content'],'messages_sha256':J.text_sha(J.canon(messages)),
                 'identity_field':('packet_id' if task=='layer3' else 'anchor_id'),'identity_value':blind,'response_file':f'responses/{blind}.json'}
            p=t/'packets'/f'{blind}.json'
            with p.open('x',encoding='utf8',newline='\n') as f:json.dump(rec,f,ensure_ascii=False,indent=1);f.write('\n')
            index.append({'job_id':blind,'packet_file':f'packets/{blind}.json','packet_file_sha256':sha(p),'messages_sha256':rec['messages_sha256'],
                          'packet_canonical_sha256':J.text_sha(J.canon(packet)),'system_prompt':name,'layer':('layer3' if task=='layer3' else 'layer4'),'task':task})
        save_json(t/'manifest.json',{'period':period,'task':task,'conversation':CONVERSATION[task],'revision':cfg['rev'],'stage':cfg['stage'],'created_utc':now(),
            'packets':len(index),'system_prompts':{name:J.text_sha(sysmsg)},'system_prompt_identical_to_calibration_r02':True,
            'contains_expected_labels':False,'contains_cell_identity':False,'index':index})
        tasks[task]={'dir':task,'conversation':CONVERSATION[task],'packets':len(index),'manifest_sha256':sha(t/'manifest.json'),'dependency':DEPENDENCIES[task]}
    save_json(d/'manifest.json',{'period':period,'revision':cfg['rev'],'stage':cfg['stage'],'created_utc':now(),'tasks':tasks,
        'units':sum(v['packets'] for v in tasks.values()),'rule':'one task per conversation; tasks of this period may run in parallel',
        'contains_expected_labels':False,'contains_cell_identity':False})
    names=list(PERIODS);later={t:DEPENDENCIES[t] for p in names[names.index(period)+1:] for t in PERIODS[p]['tasks']}
    inputs=[K.REFS,K.FACTS,K.S6A/'e5-cells-r01.jsonl',CAL_R02_MANIFEST,ADDENDUM]
    if extra:inputs+=[IMPORT_P1,ROOT/extra['import']['tasks']['grounding']['rows'],ROOT/extra['import']['tasks']['answerability']['rows'],FACTS_DECISION,K.L4CAL/'factuality'/'cal-01.json']
    rec={'time_utc':now(),'period':period,'revision':cfg['rev'],'stage':cfg['stage'],
        'workpackage':d.relative_to(ROOT).as_posix(),'workpackage_manifest_sha256':sha(d/'manifest.json'),'tasks':tasks,'later_periods_tasks':later,
        'frozen':{k:{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'action':a} for k,(p,a) in frozen.items()},
        'rules':{'system_prompts':'identical (SHA) to calibration cgpt-r02, which passed','calibration_gate':'outputs/pearl-chunking-dev80-20261007-16/calibration-gate-cgpt-r02.json'},
        'code_sha256':{f:sha(EXP/f) for f in ('e6b_workpackage.py','e6b_packets.py','e6b_prompts.py','e6b_judge.py','runtime.py')},
        'inputs_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in inputs},
        'labels_assigned':False,'model_api_calls':0,'human_verified':False}
    if extra:
        r=extra['record']
        rec['primary_2']={'behavior':{'packets':len(packets['behavior']),'answerability_label_in_packets':False,
                              'order_dependency':'answerability primary labels imported and hashed before this export','answerability_rows_sha256':extra['answerability_import_rows_sha256']},
                          'factuality':{'packets':r['packets'],'cells':r['cells'],'grounding_packets_with_claims':r['grounding_packets_with_claims'],
                              'merged_duplicates':r['merged_duplicates'],'not_exported_na':r['not_exported_na'],'context_in_packets':False,
                              'claims':'claim_id, verbatim text and located occurrences from the imported primary grounding; no grounding labels, evidence or reasons',
                              'facts':r['facts'],'facts_decision':FACTS_DECISION.relative_to(ROOT).as_posix(),
                              'sensitivity_subset':'fixed in facts-r03-decision-r01.json before any factuality label (deviation D7)'},
                          'execution_rules':'F6 of 6b-work-plan.md, written into the workpackage README',
                          'validator_sha256':sha(WP/'validate_responses.py')}
    save_json(RESEARCH/f'export-{period}.json',rec)
    print(json.dumps({'period':period,'tasks':{k:v['packets'] for k,v in tasks.items()},'frozen':{k:a for k,(p,a) in frozen.items()}}))


RESEARCH_JUDGE={'kind':'external_agent','product':'Codex desktop session; each task executed by sub-agent contexts dispatched by one coordinator (per run-notes)',
    'model':'unknown','reasoning_effort':'unknown','model_requested_in_workpackage':'sol6.1, medium (user-specified; not runtime-verifiable)','model_verified':False,
    'single_thread':False,'subagents':True,'one_new_conversation_per_task_as_instructed':False,
    'operator':'user runs the judge in the same local repository; responses imported by file',
    'note':'identity as written in the run-notes of each task; this session cannot verify the executed model (deviation D3)'}
LANE_AUDIT={t:RESEARCH/f'lane-audit-primary-1-{t}-r01.json' for t in ('layer3','answerability','grounding')}
CITATION_SUPERSEDED={'status':'superseded','scored':False,'superseded_by':'citation redo research-citation-r03 (6b-work-plan F1-F7)',
    'reason':'deviation D4: citation labels diverge by judge context on merged Source blocks; first-period citation_pairs are not usable for the report'}
AGENT_ID=re.compile(r'/root/[A-Za-z0-9_]+')


def wp_validator():
    """The workpackage validator the judge ran (standard library only); reused so import checks exactly the same rules."""
    spec=importlib.util.spec_from_file_location('e6b_wp_validator',WP/'validate_responses.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def response_problem(V,task,obj,rec,packet):
    if not isinstance(obj,dict):return 'response is not a JSON object'
    miss=[k for k in V.NEED[task] if k not in obj]
    if miss:return f'missing keys {miss}'
    if obj.get(rec['identity_field'])!=rec['identity_value']:return f"{rec['identity_field']} must be {rec['identity_value']!r}"
    if task in V.ENUM and obj[V.NEED[task][1]] not in V.ENUM[task]:return f'{V.NEED[task][1]} not in enum'
    if task=='grounding':return V.verbatim(obj,rec)
    if task=='factuality':return V.factuality_claims(obj,rec)
    if task=='layer3':
        d=obj['decision'];ref=packet['reference']
        if not all(isinstance(d.get(k),dict) for k in ('targets','conditions','claims')):return 'decision.targets/conditions/claims must be objects'
        want={'targets':set(ref['key_targets']),'conditions':set(ref['required_conditions']),'claims':set(ref['claim_definitions']),
              'numeric':{t['id'] for t in ref['numeric_targets']}}
        for k,w in want.items():
            got=set(d.get(k) or {}) if isinstance(d.get(k,{}),dict) else None
            if got!=w:return f'decision.{k} IDs {sorted(got) if got is not None else "not an object"} differ from reference {sorted(w)}'
    return None


def judge_contexts(task,notes_text):
    """Context IDs and identity self-reports exactly as written in the run-notes; grounding ranges from the frozen lane audit."""
    ids=sorted(set(AGENT_ID.findall(notes_text)))
    reports={phrase:sorted({i for line in notes_text.splitlines() if phrase in line for i in AGENT_ID.findall(line)})
             for phrase in ('Codex API assistant','GPT-6 family')}
    lane=C.load(LANE_AUDIT[task])
    return {'context_ids_in_run_notes':ids,'contexts':len(ids),'self_reported_identity_lines':{k:v for k,v in reports.items() if v},
            'ranges':{k:v['range'] for k,v in lane['ranges'].items()},'ranges_source':LANE_AUDIT[task].relative_to(ROOT).as_posix(),
            'ranges_source_sha256':sha(LANE_AUDIT[task]),'model':'unknown','reasoning_effort':'unknown'}


def range_of(ranges,blind):
    n=int(blind.rsplit('-',1)[1]);hit=[k for k,(a,b) in ranges.items() if a<=n<=b]
    if len(hit)!=1:raise ValueError(f'{blind}: judge context range not unique {hit}')
    return hit[0]


def research_check(period,src=None):
    """All bindings and response checks for one period; writes nothing. src: directory to read (default the workpackage)."""
    cfg=PERIODS[period];d=src or WP/period;exp=C.load(RESEARCH/f'export-{period}.json');problems=[];V=wp_validator()
    if sha(d/'manifest.json')!=exp['workpackage_manifest_sha256']:problems.append(('period','manifest differs from export record'))
    for k,v in exp['frozen'].items():
        p=ROOT/v['path']
        if not p.exists() or sha(p)!=v['sha256']:problems.append((k,'frozen record missing or changed since export'))
    if 'primary_2' in exp and sha(WP/'validate_responses.py')!=exp['primary_2']['validator_sha256']:problems.append(('validator','changed since export'))
    if problems:raise SystemExit(f'binding check failed: {problems}')
    built=K.build();packets=built[2];frozen=research_freeze(built)  # both records exist: verify-only, raises on drift
    if any(a!='verified_unchanged' for _,a in frozen.values()):raise SystemExit('frozen research record was rewritten')
    idmap=C.load(RESEARCH/'research-identity-map-r01.json');cal=C.load(CAL_R02_MANIFEST)['system_prompts'];tasks={}
    binds={t:{b['blind_id']:b for b in idmap['bindings'][t]} for t in cfg['tasks'] if t in idmap['bindings']};na_cells={}
    if period=='research-primary-2':  # factuality packets and bindings are rebuilt from the imported primary grounding (T5a)
        packets,extra=period_packets(period,built)
        if freeze_or_check(FACT_BINDINGS,extra['record'])!='verified_unchanged':raise SystemExit('factuality bindings were rewritten')
        binds['factuality']={b['blind_id']:b for b in extra['record']['bindings']}
        na_cells['factuality']=sum(len(x['cells']) for x in extra['record']['not_exported_na'])
    for task in cfg['tasks']:
        t=d/task;man=C.load(t/'manifest.json');name='layer3' if task=='layer3' else 'layer4-'+task;tp=[]
        if sha(t/'manifest.json')!=exp['tasks'][task]['manifest_sha256']:tp.append(('manifest','differs from export record'))
        sp=(t/'system-prompts'/f'{name}.md').read_text(encoding='utf8')
        if not J.text_sha(sp)==man['system_prompts'][name]==cal[name]:tp.append(('system_prompt','differs from manifest or calibration-r02'))
        bind=binds[task]
        if [i['job_id'] for i in man['index']]!=list(packets[task]) or set(bind)!=set(packets[task]):tp.append(('index','blind IDs differ from rebuild or identity map'))
        responses={}
        for i in man['index']:
            blind=i['job_id'];pf=t/i['packet_file']
            if sha(pf)!=i['packet_file_sha256']:tp.append((blind,'packet file changed'));continue
            rec=C.load(pf);packet=packets[task][blind];messages=research_messages(task,packet);canon_sha=J.text_sha(J.canon(packet))
            if not J.text_sha(J.canon(messages))==i['messages_sha256']==rec['messages_sha256'] or rec['user_message']!=messages[1]['content']:tp.append((blind,'messages drift'));continue
            if not canon_sha==i['packet_canonical_sha256']==bind[blind]['packet_canonical_sha256']:tp.append((blind,'packet SHA differs from identity map'));continue
            r=t/'responses'/f'{blind}.json'
            if not r.exists():tp.append((blind,'missing response'));continue
            try:obj=json.loads(r.read_text(encoding='utf8'))
            except Exception as e:tp.append((blind,f'invalid JSON: {e}'));continue
            bad=response_problem(V,task,obj,rec,packet)
            if bad:tp.append((blind,bad));continue
            responses[blind]=(obj,r,packet,i)
        if not (t/'run-notes.md').exists():tp.append(('run-notes','missing'))
        cells=sum(len(b['cells']) for b in bind.values())+na_cells.get(task,0)
        if cells!=720:tp.append(('cells',f'{cells} bound (plus NA) cells, expected 720'))
        problems+=[(task,)+p for p in tp];tasks[task]={'responses':responses,'bindings':bind,'manifest':man,'dir':t}
    if problems:raise SystemExit(f'{len(problems)} check problems, e.g. {problems[:10]}')
    return exp,idmap,tasks


def tree_sha(root):
    return {p.relative_to(root).as_posix():sha(p) for p in sorted(root.rglob('*')) if p.is_file()}


T5A_JUDGE_CONTEXTS={  # judge contexts and the blind-ID ranges whose current response files each wrote, as stated in the run-notes (T5a)
    'behavior':{'/root/behavior_review':[(1,211)],'/root/behavior_front_continued':[(212,224)],'/root/behavior_front_0225':[(225,352)],
                '/root/behavior_review/behavior_tail':[(353,704)]},
    'factuality':{'/root/factuality_review':[(1,600)],'/root/factuality_tail':[(601,704)]},
    'citation':{'/root':[(1,176)],'/root/review_0177_0352':[(177,352)],'/root/review_0353_0528':[(353,528)],'/root/review_0529_0704':[(529,704)]}}
T5A_COORDINATOR='/root (coordinator: dispatch, progress and run-notes only; judged no packet)'
T5A_NOTES={'behavior':('behavior-0209..0211 were first written by /root/behavior_front_continued (files created 07:12:04Z) and overwritten without backup by '
                       '/root/behavior_review (08:07:03-08:07:48Z) after an overlapping re-dispatch; the current files are that second write, so the three IDs '
                       'belong to /root/behavior_review here; whether the labels changed is unknown (behavior run-notes, coordinator section)'),
           'factuality':'manifest IDs only (698 packets; 0406 NA, 0494/0578/0592/0595/0649 merged duplicates); /root/factuality_review wrote 595, /root/factuality_tail 103',
           'citation':'four contexts x 176 packets, contiguous and non-overlapping (run-notes table and final mechanical verification)'}
T5A_OVERWRITTEN={'behavior':{'behavior-0209','behavior-0210','behavior-0211'}}
T5A_SELF_REPORTED='Codex desktop; model family GPT-6 as stated by the coordinator and several contexts; exact model ID and reasoning effort unknown'


def t5a_judge(task,notes_text):
    """Judge contexts for one T5a task: the run-notes ranges (T5A_JUDGE_CONTEXTS), each context ID checked to occur in the run-notes."""
    ctx=T5A_JUDGE_CONTEXTS[task];missing=[c for c in ctx if c not in notes_text]
    if missing:raise SystemExit(f'{task}: context IDs not in run-notes: {missing}')
    return {'contexts':len(ctx),'coordinator':T5A_COORDINATOR,'ranges':{c:[list(s) for s in v] for c,v in ctx.items()},
            'ranges_source':'run-notes.md of the task (sha256 recorded with the task)','note':T5A_NOTES[task],
            'self_reported':T5A_SELF_REPORTED,'model':'unknown','reasoning_effort':'unknown'}


def context_of(ctx,blind):
    n=int(blind.rsplit('-',1)[1]);hit=[c for c,v in ctx.items() if any(a<=n<=b for a,b in v)]
    if len(hit)!=1:raise ValueError(f'{blind}: judge context not unique {hit}')
    return hit[0]


def fact_row(obj,packet):
    """Factuality labels joined to the packet claims (verbatim text and harness-located occurrences); evidence quotes checked mechanically only."""
    occ={c['claim_id']:c for c in packet['claims']};quotes=[s.get('quote') or '' for s in packet['fact_packet']['sources']]
    quotes+=[json.dumps(x,ensure_ascii=False) for x in packet['fact_packet'].get('supplementary_facts') or []];claims=[];off=0
    for c in obj['claims']:
        ev=c.get('fact_evidence') or [];bad=sum(1 for e in ev if isinstance(e,dict) and e.get('quote') and not any(e['quote'] in q for q in quotes))
        off+=bad;claims.append({**c,'text':occ[c['claim_id']]['text'],'occurrences':occ[c['claim_id']]['occurrences'],'evidence_quotes_not_verbatim':bad})
    return {**obj,'claims':claims},off


def import_research(period):
    cfg=PERIODS[period];src=WP/period;dst=RESEARCH/f'workpackage-{period}-received';out=RESEARCH/f'import-{period}'
    if dst.exists() or out.exists() or (RESEARCH/f'import-{period}.json').exists():raise FileExistsError(f'{period} already imported')
    research_check(period)  # check the live workpackage first, before copying anything
    shutil.copytree(src,dst);files=tree_sha(dst)
    if files!=tree_sha(src):raise SystemExit('received copy differs from the workpackage')
    for p in dst.rglob('*'):
        if p.is_file():os.chmod(p,stat.S_IREAD)  # read-only evidence of exactly what was imported
    exp,idmap,tasks=research_check(period,dst)  # import reads the read-only copy only
    out.mkdir();summary={};judge={};p2=period=='research-primary-2'
    for task,T in tasks.items():
        notes=(T['dir']/'run-notes.md').read_text(encoding='utf8');ctx=t5a_judge(task,notes) if p2 else judge_contexts(task,notes);judge[task]=ctx
        rows=[];located=0;loc_problems={};sup=0;quote_off={}
        for blind,(obj,r,packet,i) in T['responses'].items():
            cells=T['bindings'][blind]['cells']
            row={'schema_version':'pearl-e6b-research-import-row-v1','period':period,'revision':cfg['rev'],'stage':cfg['stage'],'task':task,'blind_id':blind,
                 'cells':[{'cell_id':c,**{k:idmap['cells'][c][k] for k in ('arm','intent_id','replicate')}} for c in cells],
                 'packet_canonical_sha256':i['packet_canonical_sha256'],'messages_sha256':i['messages_sha256'],
                 'response_file':r.relative_to(ROOT).as_posix(),'response_file_sha256':sha(r),'human_verified':False}
            if p2:
                row['judge_context']=context_of(T5A_JUDGE_CONTEXTS[task],blind)
                if blind in T5A_OVERWRITTEN.get(task,()):row['execution_event']='overwritten without backup after an overlapping re-dispatch; earlier labels unknown (see run-notes)'
            else:row['lane_audit_range']=range_of(ctx['ranges'],blind)
            if task=='factuality':
                row['grounding_blind_ids']=T['bindings'][blind]['grounding_blind_ids'];row['response'],bad=fact_row(obj,packet)
                if bad:quote_off[blind]=bad
            elif task=='grounding':
                cite={k:obj[k] for k in ('citation_pairs','citation_extraction_unknown')}
                g=P.locate_grounding({k:v for k,v in obj.items() if k not in cite},packet['raw_answer'])  # frozen locator; claims only
                g.pop('citation_pairs')
                if g['location_problems']:loc_problems[blind]=g['location_problems']
                located+=sum(len(c['occurrences']) for c in g['claims']);sup+=len(cite['citation_pairs'])
                row.update(response=g,citation_superseded={**cite,**CITATION_SUPERSEDED})
            else:row['response']=obj
            rows.append(row)
        path=out/f'{task}.jsonl'
        with path.open('x',encoding='utf8',newline='\n') as f:
            for row in rows:f.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+'\n')
        summary[task]={'responses':len(rows),'cells_bound':sum(len(r['cells']) for r in rows),'rows':path.relative_to(ROOT).as_posix(),'rows_sha256':sha(path),
                       'run_notes_sha256':sha(T['dir']/'run-notes.md'),'manifest_sha256':sha(T['dir']/'manifest.json'),
                       **({'claims':sum(len(r['response']['claims']) for r in rows),'claim_occurrences_located':located,'location_problems':loc_problems,
                           'citation_pairs_superseded':sup} if task=='grounding' else {})}
        if task=='factuality':
            summary[task].update(claims=sum(len(r['response']['claims']) for r in rows),offsets='claim occurrences carried from the packet (located by the frozen locator at export)',
                                 evidence_quotes_not_verbatim_in_fact_packet=quote_off,not_exported_na=exp['primary_2']['factuality']['not_exported_na'],
                                 bindings={'path':FACT_BINDINGS.relative_to(ROOT).as_posix(),'sha256':sha(FACT_BINDINGS)})
        if task in T5A_OVERWRITTEN:summary[task]['overwritten_without_backup']=sorted(T5A_OVERWRITTEN[task])
    if p2:
        rec={'time_utc':now(),'period':period,'revision':cfg['rev'],'stage':cfg['stage'],
             'judge':{**RESEARCH_JUDGE,'note':'identity as written in the run-notes; contexts dispatched with fork_turns=none per the coordinator record; '
                      'this session cannot verify the executed model','per_task':judge},'tasks':summary,
             'received_copy':{'path':dst.relative_to(ROOT).as_posix(),'files':len(files),'tree_sha256':J.text_sha(J.canon(files)),'read_only':True,
                              'identical_to_workpackage_at_import':True},
             'checks':{'period_and_task_manifests':'equal to export record','packet_files':'equal to manifest SHA',
                       'packets':'behavior rebuilt by e6b_packets.build(); factuality rebuilt from the imported primary grounding rows and facts-r03; messages and canonical packet SHA equal to manifest, identity map and factuality bindings',
                       'frozen_records':'identity map, secondary sample and factuality bindings verified unchanged','system_prompts':'equal to calibration cgpt-r02',
                       'responses':'workpackage validate_responses.py rules (keys, identity, enums, factuality claim coverage)',
                       'cells':'720 per task: behavior through the identity map; factuality 719 bound plus 1 NA (no claims)'},
             'export_record_sha256':sha(RESEARCH/f'export-{period}.json'),'identity_map_sha256':sha(RESEARCH/'research-identity-map-r01.json'),
             'deviation_record':'paper/pearl-6b-judge-workpackage/incidents-and-deviations.md (T5a entries)',
             'code_sha256':{f:sha(EXP/f) for f in ('e6b_workpackage.py','e6b_packets.py','e6b_prompts.py','e6b_judge.py','runtime.py')},
             'validator_sha256':sha(WP/'validate_responses.py'),'validator_sha256_at_export':exp['primary_2']['validator_sha256'],
             'labels_assigned':False,'labels_changed':False,'scored':False,'model_api_calls':0,'human_verified':False}
        save_json(RESEARCH/f'import-{period}.json',rec)
        print(json.dumps({'period':period,'tasks':{k:{x:y for x,y in v.items() if x in ('responses','cells_bound','claims')} for k,v in summary.items()},
                          'evidence_quotes_not_verbatim':{k:sum(v.get('evidence_quotes_not_verbatim_in_fact_packet',{}).values()) for k,v in summary.items()}}))
        return
    save_json(RESEARCH/f'import-{period}.json',{'time_utc':now(),'period':period,'revision':cfg['rev'],'stage':cfg['stage'],
        'judge':{**RESEARCH_JUDGE,'per_task':judge},'tasks':summary,
        'received_copy':{'path':dst.relative_to(ROOT).as_posix(),'files':len(files),'tree_sha256':J.text_sha(J.canon(files)),'read_only':True,
                         'identical_to_workpackage_at_import':True},
        'checks':{'period_and_task_manifests':'equal to export record','packet_files':'equal to manifest SHA',
                  'packets':'rebuilt by e6b_packets.build(); messages and canonical packet SHA equal to manifest and identity map',
                  'frozen_records':'identity map and secondary sample verified unchanged','system_prompts':'equal to calibration cgpt-r02',
                  'responses':'workpackage validate_responses.py rules (keys, identity, enums, grounding verbatim) plus Layer 3 ID sets equal to the packet reference',
                  'cells':'720 cells bound per task through the identity map'},
        'grounding':{'offsets':'frozen e6b_prompts.locate_grounding on claims; the harness, not the judge, binds identity',
                     'citation_pairs':CITATION_SUPERSEDED,'claim_labels':'retained for scoring (user decision after D4)'},
        'export_record_sha256':sha(RESEARCH/f'export-{period}.json'),'identity_map_sha256':sha(RESEARCH/'research-identity-map-r01.json'),
        'deviations':{'D3':'sub-agent execution instead of one new conversation per task','D4':'citation labels diverge by context; citation_pairs superseded',
                      'D5':'responses edited after writing (mechanical corrections; see run-notes); imported files are the final state',
                      'D6':'judges saw re-formatted displays of some packets'},
        'deviation_record':'paper/pearl-6b-judge-workpackage/incidents-and-deviations.md',
        'code_sha256':{f:sha(EXP/f) for f in ('e6b_workpackage.py','e6b_packets.py','e6b_prompts.py','e6b_judge.py','runtime.py')},
        'validator_sha256':sha(WP/'validate_responses.py'),
        'labels_assigned':False,'labels_changed':False,'scored':False,'model_api_calls':0,'human_verified':False})
    print(json.dumps({'period':period,'tasks':{k:{x:y for x,y in v.items() if x in ('responses','cells_bound','claims','citation_pairs_superseded')} for k,v in summary.items()},
                      'location_problems':{k:len(v.get('location_problems',{})) for k,v in summary.items()}}))


FACTS_EVIDENCE={'evaluation_versions':ROOT/'outputs/pearl-chunking-dev80-20261006-13/evaluation-versions-r01.json',
    'layer4_pre_C_freeze':ROOT/'outputs/pearl-layer4-dev80-20261004-01/pre-C-freeze-r01.json',
    'layer4_score_bindings_r03':ROOT/'outputs/pearl-layer4-dev80-20261004-01/score-bindings-r03.json',
    'independent_basis_review':ROOT/'outputs/pearl-layer4-dev80-20261004-01/facts/independent-basis-review-r01.json',
    'review_revision_r03':ROOT/'outputs/pearl-layer4-dev80-20261004-01/facts/review-revision-r03.json',
    'validation_r02':ROOT/'outputs/pearl-layer4-dev80-20261004-01/facts/validation-r02.json'}


def facts_check():
    """Evidence on facts-r03 for the user's decision (T3a); reads only, decides nothing."""
    f=K.FACTS;h=sha(f);x=C.load(f);ev={k:C.load(p) for k,p in FACTS_EVIDENCE.items()};txt={k:p.read_text(encoding='utf8') for k,p in FACTS_EVIDENCE.items()}
    exp=C.load(RESEARCH/'export-research-primary-1.json');basis=ev['independent_basis_review']
    rec={'schema_version':'pearl-e6b-facts-provenance-v1','time_utc':now(),'status':'evidence_for_user_decision','decision':'pending_user',
        'facts':{'path':f.relative_to(ROOT).as_posix(),'sha256':h,**{k:x[k] for k in ('schema_version','status','revision','supersedes','independence','source_scope','revision_reason')},
                 'items':len(x['items']),'isolation_exceptions':{i['intent_id']:i['isolation_exception'] for i in x['items'] if i.get('isolation_exception')}},
        'five_b_freeze':{'path':FACTS_EVIDENCE['evaluation_versions'].relative_to(ROOT).as_posix(),'sha256':sha(FACTS_EVIDENCE['evaluation_versions']),
                         'layer4_keys':sorted(ev['evaluation_versions']['layer4']),'mentions_facts':'facts' in txt['evaluation_versions'],'mentions_facts_sha256':h in txt['evaluation_versions']},
        'historical_layer4':{'pre_C_freeze_status':ev['layer4_pre_C_freeze']['status'],'pre_C_freeze_binds_facts_r03':ev['layer4_pre_C_freeze']['facts_sha256']==h,
                             'score_bindings_r03_binds_facts_r03':h in txt['layer4_score_bindings_r03'],
                             'fact_packet_exporter_reads':'outputs/pearl-layer4-dev80-20261004-01/export_fact_packets_r01.py reads facts/facts-r03.json'},
        'independent_review':{'status':basis['status'],'facts_sha256_matches':basis['facts_sha256']==h,
                              **{k:basis[k] for k in ('reviewer','model','actual_read','prior_exposure','unresolved')},
                              'decisions':sorted({i['decision'] for i in basis['items']}),'items':len(basis['items']),
                              'item_009':[i for i in basis['items'] if i['intent_id']=='pearl-dev-009'],
                              'review_revision_r03_isolation':ev['review_revision_r03']['isolation'],
                              'validation_r02':{k:ev['validation_r02'][k] for k in ('status','items','verified_source_quotes','source_review_limitations')}},
        'six_b_use':{'e6b_packets_FACTS':K.FACTS.relative_to(ROOT).as_posix(),'export_research_primary_1_input_sha256':exp['inputs_sha256'].get(f.relative_to(ROOT).as_posix()),
                     'already_in_judged_packets':'answerability (and behavior) packets carry requirements.necessary_conclusions / necessary_groups taken from facts-r03 (e6b_packets.build)'},
        'file_mtime_utc':{p.relative_to(ROOT).as_posix():datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat()
                          for p in (f,FACTS_EVIDENCE['layer4_pre_C_freeze'],FACTS_EVIDENCE['independent_basis_review'],FACTS_EVIDENCE['evaluation_versions'],K.S6A/'e5-cells-r01.jsonl')},
        'mtime_note':'filesystem times are weak evidence, recorded only for ordering','evidence_sha256':{k:sha(p) for k,p in FACTS_EVIDENCE.items()},
        'checker_sha256':sha(EXP/'e6b_workpackage.py'),'model_api_calls':0}
    save_json(RESEARCH/'facts-r03-provenance-r01.json',rec);print(json.dumps({k:rec[k] for k in ('five_b_freeze','historical_layer4')},ensure_ascii=False))


# ---------------------------------------------------------------- citation redo r03 (F2-F7)
CITE_CAL='calibration-citation-r03';CITE_RES='research-citation-r03';CITE_REV='cgpt-citation-r03'
CITE_NOTE=EXP/'e6b-citation-input-format-r03.md'
CITE_SYSTEM_NAME='layer4-citation-r03'
FRAGMENT_AUDIT=RESEARCH/'fragment-boundaries-r03.json'
CITE_DESIGN=RESEARCH/'citation-redo-design-r03.json'
CITE_BINDINGS=RESEARCH/'citation-bindings-r03.json'
CITE_PLAN=RUN/'calibration'/'calibration-plan-citation-r03.json'
CITE_GATE=RUN/'calibration-gate-citation-r03.json'
CITE_VALIDATOR=WP/'validate_citation_responses.py'
CAL_R02_GROUNDING=RUN/'calibration'/'judge-cgpt-r02'/'layer4'
SOURCE_VIEWS=ROOT/'outputs/pearl-chunking-dev80-20261005-05/source-views-prepared.json'
E3_CONTEXTS=ROOT/'outputs/pearl-chunking-dev80-20261006-11'
CITE_FORMAT_R03='''# Output format (citation redo r03)
Return exactly one JSON object:
{"anchor_id": "<id from packet>",
 "citation_pairs": [{"claim_id": "<claim_id from the packet claims>",
                     "citation_text": "<exact verbatim citation string from raw_answer>",
                     "citation_occurrence": <1-based index of this citation string among identical citation strings in raw_answer>,
                     "source_id": "<fragment_id of the cited source in source_fragments; if the citation names a source that matches no fragment, the source identifier as written in the citation>",
                     "label": "supported|partial|unsupported|contradicted|unknown|invalid|outside-context",
                     "reason": "<reason>"}],
 "citation_extraction_unknown": false, "reason": "<overall note>"}
Every citation_text must be copied character-for-character from raw_answer; the program locates its character offsets.
Do not output offsets, claims or claim labels.'''
CITE_INSTRUCTION='引用重做r03：claims已固定。按系统提示中的“输入格式说明 r03”读取claims与source_fragments，只输出citation_pairs与citation_extraction_unknown。不得接触事实包或expected。'
CITE_LABELS=('supported','partial','unsupported','contradicted','unknown','invalid','outside-context')
# F7 acceptance standard (draft written in T3c; frozen verbatim into the research-citation-r03 export record in T3e, before
# any redo label exists; not to be changed afterwards).
F7_STANDARD={'version':'f7-citation-consistency-r01',
    'data':'imported research-citation-r03 responses; pair labels (7 categories) and packet-level citation_extraction_unknown',
    'segments':'one segment per judge context (coordinator or sub-agent) with the blind-ID ranges written in run-notes; a context with several ranges is one segment. '
               'If run-notes name only one context, its packets are cut into four consecutive pseudo-segments in blind-ID order (drift check). '
               'Ranges must cover every exported packet exactly once; otherwise F7 cannot be evaluated and is not met.',
    'statistics':{'S1':'Pearson X2 of the segment x pair-label table (7 labels; labels absent everywhere dropped)',
                  'S2':'Pearson X2 of the segment x citation_extraction_unknown (true/false) table over packets',
                  'S3':'largest absolute gap, over segments with at least 30 packets, between the segment unknown pair share and the unknown pair share of all other segments pooled (the D4 failure mode)',
                  'null':'the same 10,000 random reassignments of whole packets (with all their pairs) to segments, segment packet counts kept, for S1-S3; '
                         'random.Random(20261005); p=(1+#{S*>=S})/(1+10000). Packets, not pairs, are permuted because pairs within a packet are not independent'},
    'thresholds':{'S1_p_min':0.01,'S2_p_min':0.01,'S3_p_min':0.01},
    'pass':'met only if p(S1)>=0.01 and p(S2)>=0.01 and p(S3)>=0.01 (S3 vacuous when no segment has >=30 packets)',
    'draft_history':'a first draft used a fixed bound U<=0.10 on the unknown gap; on superseded primary-1 citation labels with interleaved (context-mixed) segments it '
                    'flagged 0.12-0.14 gaps that the permutation tests did not, because unknown pairs cluster within packets; it was replaced by the permutation-calibrated S3 '
                    'in T3c, before any redo label exists (controls in citation-redo-design-r03.json)',
    'descriptive_only':['per-segment label shares','per-segment shares split by whether the cited block is merged (source_id -> block via source_fragments; '
                        'unidentifiable source_id counted as unclassified)','per-configuration label shares (configuration is the research effect, not a gate)'],
    'not_met':['write the F7 record as not_met; change no label, drop no segment, keep thresholds',
               'investigate segment by segment: the segments that drive S1/S2/U, their run-notes (coordinator messages, clarifications, truncation, resumes), '
               'merged vs single-fragment blocks, and packets judged before/after any recorded event',
               'citation metrics stay blocked in the report (scoring-pipeline-spec G7, section 6.4); every other metric proceeds',
               'report to the user with the findings and options (e.g. re-judging the affected range in a new context under the same README as a new revision); the user decides'],
    'tool':'experiments/pearl-chunking-dev80-20261005/e6b_lane_audit.py --f7'}


def citation_system():
    """r03 system prompt: frozen rules byte-identical to cgpt-r02 grounding; only the output-format section is replaced."""
    base=P.layer4_messages({},'grounding')[0]['content'];cal=C.load(CAL_R02_MANIFEST)['system_prompts']['layer4-grounding']
    fmt=P.L4_FORMAT['grounding']
    if J.text_sha(base)!=cal or not base.endswith(fmt):raise ValueError('grounding system prompt differs from calibration cgpt-r02')
    prefix=base[:-len(fmt)];text=prefix+CITE_NOTE.read_text(encoding='utf8').strip()+'\n\n'+CITE_FORMAT_R03
    return text,{'cgpt_r02_grounding_system_sha256':cal,'frozen_rules_prefix_sha256':J.text_sha(prefix),'frozen_rules_prefix_chars':len(prefix),
                 'frozen_rules_prefix_identical_to_cgpt_r02':True,'replaced':'only the trailing harness output-format section (API harness r01 grounding format)',
                 'appended':[CITE_NOTE.relative_to(ROOT).as_posix(),'CITE_FORMAT_R03 (e6b_workpackage.py)'],'input_format_note_sha256':sha(CITE_NOTE)}


def citation_messages(packet):
    return [{'role':'system','content':citation_system()[0]},{'role':'user','content':'Packet (JSON):\n'+json.dumps(packet,ensure_ascii=False,indent=1)}]


def citation_packet(base,claims,anchor):
    """Grounding packet -> citation packet: claims_candidates -> fixed claims, source_fragments after context, r03 instruction."""
    out={'anchor_id':anchor}
    for k,v in base.items():
        if k in ('anchor_id','claims_candidates','instruction'):continue
        out[k]=v
        if k=='context':out['source_fragments']=F.packet_field(F.derive(v))
    out['claims']=[{'claim_id':c['claim_id'],'text':c['text'],'occurrences':c['occurrences']} for c in claims];out['instruction']=CITE_INSTRUCTION
    return out


def fixed_claims(parsed,raw_answer):
    g=P.locate_grounding({k:v for k,v in parsed.items() if k not in ('citation_pairs','citation_extraction_unknown')},raw_answer)
    if g['location_problems']:raise ValueError(f'claims not located: {g["location_problems"][:3]}')
    return [{'claim_id':c['claim_id'],'text':c['text'],'occurrences':c['occurrences']} for c in g['claims']]


def fragments_audit():
    """F2: derive and verify fragment boundaries of every E5 context (240) and every calibration grounding anchor (40)."""
    rows=[json.loads(x) for x in (K.S6A/'e5-cells-r01.jsonl').read_text(encoding='utf8').splitlines()]
    views={(v['doc_id'],v['source_version'],e['element_id']):e['text'] for v in C.load(SOURCE_VIEWS) for e in v['elements']}
    want={(r['arm'],r['intent_id']):r for r in rows};records={}
    for arm in sorted({r['arm'] for r in rows}):
        with (E3_CONTEXTS/f'contexts-{arm}-P0-4096-fixed_budget_main.jsonl').open(encoding='utf8') as f:
            for line in f:
                rec=json.loads(line)
                if (arm,rec['intent_id']) in want:records[(arm,rec['intent_id'])]=rec['final']
    per=[];arms={};unaligned=[];checks={'assembly_record':0,'source_text':0}
    for r in rows:
        ctx=r['context'];blocks=F.derive(ctx);field=F.packet_field(blocks)
        if J.text_sha(ctx)!=r['context_sha256']:raise ValueError('context SHA')
        bad_rec=F.verify(ctx,blocks,record=records.get((r['arm'],r['intent_id'])));bad_src=F.verify(ctx,blocks,views=views)
        checks['assembly_record']+=int(not bad_rec);checks['source_text']+=int(not bad_src)
        un=[b['block_id'] for b in blocks if b['alignment']!='exact']
        for b in blocks:
            if b['alignment']!='exact':unaligned.append({'arm':r['arm'],'intent_id':r['intent_id'],'block_id':b['block_id'],'problems':b.get('problems')})
        if bad_rec or bad_src:unaligned.append({'arm':r['arm'],'intent_id':r['intent_id'],'verification_problems':{'assembly_record':bad_rec,'source_text':bad_src}})
        a=arms.setdefault(r['arm'],{'contexts':0,'blocks':0,'merged_blocks':0,'fragments':0,'unaligned_blocks':0})
        a['contexts']+=1;a['blocks']+=len(blocks);a['merged_blocks']+=sum(len(b['fragments'])>1 for b in blocks);a['fragments']+=sum(len(b['fragments']) for b in blocks);a['unaligned_blocks']+=len(un)
        per.append({'arm':r['arm'],'intent_id':r['intent_id'],'context_sha256':r['context_sha256'],'blocks':len(blocks),
                    'merged_blocks':sum(len(b['fragments'])>1 for b in blocks),'fragments':sum(len(b['fragments']) for b in blocks),'unaligned_blocks':un,
                    'supplementary_plane_chars':sum(ord(ch)>0xFFFF for ch in ctx),'source_fragments_sha256':J.text_sha(J.canon(field))})
    for a in arms.values():a['merged_share']=round(a['merged_blocks']/a['blocks'],4)
    cal=[]
    for p in sorted((C.L4CAL/'judge-packets'/'grounding').glob('cal-*.json')):
        b=F.derive(C.load(p)['context']);cal.append({'anchor_id':p.stem,'blocks':len(b),'alignment':[x['alignment'] for x in b],'derivation':[x['derivation'] for x in b],
                                                     'fragments':sum(len(x['fragments']) for x in b)})
    idmap=C.load(RESEARCH/'research-identity-map-r01.json');ctx_shas={x['context_sha256'] for x in per}
    used={idmap['cells'][b['cells'][0]]['context_sha256'] for b in idmap['bindings']['grounding']}
    total={k:sum(a[k] for a in arms.values()) for k in ('contexts','blocks','merged_blocks','fragments','unaligned_blocks')}
    rec={'schema_version':'pearl-e6b-fragment-boundaries-v1','version':F.VERSION,'time_utc':now(),'status':'frozen_before_citation_redo_labels',
         'rule':'fragment spans derived from the header intervals only (source-assembly-r01 serialization); a block is exact only if the derived body ends at the next block '
                'boundary and every separator is a blank line; unaligned blocks keep their header and get no spans (nothing guessed); context never changed',
         'offsets':'Unicode code points, half-open (Python str indices); not UTF-16 units, not bytes',
         'independent_checks':{'assembly_record':'derived header tuples, fragment spans and block text equal the frozen source-assembly-r01 final units (spans, parts, text) of the same context',
                               'source_text':'every fragment text equals element_text[start:end] of the frozen source views'},
         'totals':total,'by_configuration':dict(sorted(arms.items())),'unaligned':unaligned,
         'checks_passed':{'contexts':len(per),'header_derivation_all_exact':total['unaligned_blocks']==0,**{k:f'{v}/{len(per)}' for k,v in checks.items()}},
         'contexts_with_supplementary_plane_chars':sum(x['supplementary_plane_chars']>0 for x in per),
         'research_grounding_contexts_covered':used<=ctx_shas,'research_grounding_unique_contexts':len(used),
         'calibration_grounding_anchors':{'anchors':len(cal),'all_single_block_single_source_label':all(x['blocks']==1 and x['alignment']==['exact'] and x['derivation']==['single_source_label'] and x['fragments']==1 for x in cal),
                                          'merged_blocks':0,'note':'calibration anchors are single-source; F5 cannot test merged blocks'},
         'contexts':per,
         'inputs_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in [K.S6A/'e5-cells-r01.jsonl',SOURCE_VIEWS]+[E3_CONTEXTS/f'contexts-{a}-P0-4096-fixed_budget_main.jsonl' for a in sorted(arms)]},
         'code_sha256':{f:sha(EXP/f) for f in ('e6b_fragments.py','e6b_workpackage.py','assemble.py')},'labels_assigned':False,'model_api_calls':0}
    save_json(FRAGMENT_AUDIT,rec);print(json.dumps({k:rec[k] for k in ('totals','checks_passed','contexts_with_supplementary_plane_chars','research_grounding_contexts_covered')},ensure_ascii=False))


def calibration_citation_packets():
    """40 calibration citation packets: frozen grounding anchors; claims fixed from the passed cgpt-r02 grounding responses."""
    out={}
    for p in sorted((C.L4CAL/'judge-packets'/'grounding').glob('cal-*.json')):
        base=C.load(p);rec=C.load(CAL_R02_GROUNDING/'grounding'/f'{p.stem}.json')
        if rec['meta']['packet_sha256']!=sha(p) or rec['parsed']['anchor_id']!=p.stem:raise ValueError(f'{p.stem}: cgpt-r02 record does not bind this anchor')
        out[p.stem]=citation_packet(base,fixed_claims(rec['parsed'],base['raw_answer']),p.stem)
    return out


def export_calibration_citation():
    d=WP/CITE_CAL
    if d.exists() or CITE_PLAN.exists():raise FileExistsError(d)
    gate=C.load(RUN/'calibration-gate-cgpt-r02.json')
    if gate.get('status')!='passed':raise SystemExit('cgpt-r02 calibration gate is not passed')
    if not FRAGMENT_AUDIT.exists():raise SystemExit('run fragments-audit first (F2)')
    system,sysinfo=citation_system();packets=calibration_citation_packets()
    (d/'system-prompts').mkdir(parents=True);(d/'packets').mkdir();(d/'responses').mkdir()
    (d/'system-prompts'/f'{CITE_SYSTEM_NAME}.md').write_text(system,encoding='utf8',newline='\n');index=[]
    for anchor,packet in packets.items():
        job=f'L4-citation-{anchor}';messages=citation_messages(packet)
        rec={'job_id':job,'system_prompt':f'system-prompts/{CITE_SYSTEM_NAME}.md','system_prompt_sha256':J.text_sha(system),'user_message':messages[1]['content'],
             'messages_sha256':J.text_sha(J.canon(messages)),'identity_field':'anchor_id','identity_value':anchor,'response_file':f'responses/{job}.json'}
        p=d/'packets'/f'{job}.json'
        with p.open('x',encoding='utf8',newline='\n') as f:json.dump(rec,f,ensure_ascii=False,indent=1);f.write('\n')
        index.append({'job_id':job,'anchor_id':anchor,'packet_file':f'packets/{job}.json','packet_file_sha256':sha(p),'messages_sha256':rec['messages_sha256'],
                      'packet_canonical_sha256':J.text_sha(J.canon(packet)),'system_prompt':CITE_SYSTEM_NAME,'layer':'layer4','task':'citation','claims':len(packet['claims'])})
    save_json(d/'manifest.json',{'phase':CITE_CAL,'revision':CITE_REV,'task':'citation','created_utc':now(),'packets':len(index),
        'system_prompts':{CITE_SYSTEM_NAME:J.text_sha(system)},'frozen_rules_prefix_identical_to_cgpt_r02':True,
        'input_format_note':CITE_NOTE.relative_to(ROOT).as_posix(),'input_format_note_sha256':sha(CITE_NOTE),
        'claims_source':'passed calibration cgpt-r02 grounding responses (claim_id, verbatim text, located occurrences; no labels)',
        'contains_expected_labels':False,'contains_claim_labels':False,'index':index})
    base=C.load(RUN/'calibration'/'calibration-plan-cgpt-r02.json')
    save_json(CITE_PLAN,{'status':'frozen_before_judge','revision':CITE_REV,'phase':CITE_CAL,'time_utc':now(),
        'workpackage_manifest_sha256':sha(d/'manifest.json'),'system_prompt':sysinfo,'system_prompt_sha256':J.text_sha(system),
        'packets':[{k:i[k] for k in ('job_id','anchor_id','messages_sha256','packet_canonical_sha256','claims')} for i in index],
        'claims_source':{'records':(CAL_R02_GROUNDING/'grounding').relative_to(ROOT).as_posix(),'located_by':'frozen e6b_prompts.locate_grounding',
                         'cgpt_r02_extraction_agreement':C.load(RUN/'calibration'/'calibration-comparison-cgpt-r02.json')['layer4']['metrics']['extraction']},
        'fragment_audit':{'path':FRAGMENT_AUDIT.relative_to(ROOT).as_posix(),'sha256':sha(FRAGMENT_AUDIT)},
        'comparison':{'method':'frozen experiments/pearl-layer4-dev80-20261004/compare_calibration.compare, unchanged, on the 40 frozen expected anchors (expected-r01.json). '
                               'Inputs per anchor: grounding = cgpt-r02 claims and extraction_unknown (located as in the cgpt-r02 comparison) with citation_pairs replaced by the r03 '
                               'citation_pairs located by the frozen e6b_prompts.locate_grounding; answerability, factuality and behavior = the cgpt-r02 responses (normalized as in the cgpt-r02 comparison). '
                               'Only citation results are read; the other metrics are reported as an input check (they must equal cgpt-r02).',
                      'metric':'metrics.citation.agreement (expected pairs with label unknown excluded, as frozen)',
                      'gate':['metrics.citation.agreement >= 0.95 (original Layer 4 threshold each_metric_min)',
                              'no failure with metric citation_schema (pair count and (claim_id, citation_text, citation_span) set equal to expected)',
                              'every one of the 8 sentinel anchors has no citation or citation_schema failure',
                              '40/40 responses valid (validate_citation_responses.py) with every citation located'],
                      'not_gated':'citation_extraction_unknown and source_id are recorded but not compared (the frozen comparer does not compare them)',
                      'threshold_source':{'path':(RUN/'calibration'/'calibration-plan-cgpt-r02.json').relative_to(ROOT).as_posix(),'layer4':base['thresholds']['layer4']},
                      'code':'e6b_workpackage.compare_citation'},
        'limitation':'the 40 anchors are single-source with one block each (no merged blocks); a pass shows only that the r03 format leaves the calibrated citation behavior unchanged, '
                     'not that merged blocks are handled correctly (6b-work-plan F5; to be stated in the report)',
        'on_failure':'write blocked; no threshold, rule, note or format change; no research citation packets',
        'judge_reads_expected':False,'code_sha256':{f:sha(EXP/f) for f in ('e6b_workpackage.py','e6b_fragments.py','e6b_prompts.py','e6b_judge.py','runtime.py')},
        'frozen_comparer_sha256':sha(ROOT/'experiments/pearl-layer4-dev80-20261004/compare_calibration.py'),
        'expected_sha256':sha(C.L4CAL/'expected-r01.json'),'validator_sha256':sha(CITE_VALIDATOR),'labels_assigned':False,'model_api_calls':0,'human_verified':False})
    print(json.dumps({'phase':CITE_CAL,'packets':len(index),'claims':sum(i['claims'] for i in index),'system_prompt_sha256':J.text_sha(system)}))


def compare_citation(responses):
    """F5 comparison. responses: {anchor_id: parsed r03 response}. Returns the frozen comparer report plus the citation-only gate."""
    comp=C.module('l4compare',ROOT/'experiments/pearl-layer4-dev80-20261004/compare_calibration.py')
    l4exp=C.load(C.L4CAL/'expected-r01.json')['expected'];results={};located={}
    for e in l4exp:
        ident=e['anchor_id'];results[ident]={}
        for task in C.TASKS:
            parsed=C.load(CAL_R02_GROUNDING/task/f'{ident}.json')['parsed'];packet=C.load(C.L4CAL/'judge-packets'/task/f'{ident}.json')
            if task=='grounding':
                g=P.locate_grounding(parsed,packet['raw_answer']);r=responses.get(ident) or {}
                cite=P.locate_grounding({'citation_pairs':r.get('citation_pairs') or []},packet['raw_answer'])
                parsed={**g,'citation_pairs':cite['citation_pairs'],'citation_extraction_unknown':r.get('citation_extraction_unknown')}
                located[ident]=cite['location_problems']
            if task=='behavior':parsed=P.normalize_behavior(parsed)
            parsed['anchor_id']=ident;results[ident][task]=parsed
    rep=comp.compare(l4exp,results);cfail=[f for f in rep['failures'] if f['metric'] in ('citation','citation_schema')]
    sent={s['anchor_id'] for s in rep['sentinels']}
    gate={'citation':rep['metrics']['citation'],'citation_schema_failures':[f for f in cfail if f['metric']=='citation_schema'],
          'sentinels':[{'anchor_id':s['anchor_id'],'kind':s['kind'],'citation_passed':not any(f['anchor_id']==s['anchor_id'] for f in cfail)} for s in rep['sentinels']],
          'location_problems':{k:v for k,v in located.items() if v},'responses':len(responses)}
    gate['passed']=(rep['metrics']['citation']['agreement'] is not None and rep['metrics']['citation']['agreement']>=0.95 and not gate['citation_schema_failures']
                    and len(sent)==8 and all(s['citation_passed'] for s in gate['sentinels']) and not gate['location_problems'] and len(responses)==40)
    gate['non_citation_metrics_input_check']={k:v['agreement'] for k,v in rep['metrics'].items() if k!='citation'}
    return rep,gate


def citation_validator():
    spec=importlib.util.spec_from_file_location('e6b_cite_validator',CITE_VALIDATOR);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def import_calibration_citation():
    """T3e: validate, keep a read-only received copy, compare with the method frozen in CITE_PLAN, write the gate."""
    d=WP/CITE_CAL;dst=RUN/f'workpackage-{CITE_CAL}-received';plan=C.load(CITE_PLAN)
    if dst.exists() or CITE_GATE.exists():raise FileExistsError(dst)
    if sha(d/'manifest.json')!=plan['workpackage_manifest_sha256']:raise SystemExit('manifest differs from the frozen plan')
    if sha(CITE_VALIDATOR)!=plan['validator_sha256']:raise SystemExit('validator changed since the plan')
    if not (d/'run-notes.md').exists():raise SystemExit('run-notes.md is required before import')
    if citation_validator().main(CITE_CAL)!=0:raise SystemExit('responses do not validate')
    fresh=calibration_citation_packets();man=C.load(d/'manifest.json')
    for i in man['index']:
        rec=C.load(d/i['packet_file']);packet=fresh[i['anchor_id']];messages=citation_messages(packet)
        if (sha(d/i['packet_file'])!=i['packet_file_sha256'] or J.text_sha(J.canon(packet))!=i['packet_canonical_sha256']
                or not J.text_sha(J.canon(messages))==i['messages_sha256']==rec['messages_sha256'] or rec['user_message']!=messages[1]['content']):
            raise SystemExit(f'{i["job_id"]}: packet drift since export')
    shutil.copytree(d,dst);files=tree_sha(dst)
    if files!=tree_sha(d):raise SystemExit('received copy differs')
    for p in dst.rglob('*'):
        if p.is_file():os.chmod(p,stat.S_IREAD)
    responses={i['anchor_id']:C.load(dst/'responses'/f'{i["job_id"]}.json') for i in man['index']}
    rep,gate=compare_citation(responses)
    save_json(RUN/'calibration'/'calibration-comparison-citation-r03.json',{**rep,'citation_gate':gate,'plan_sha256':sha(CITE_PLAN)})
    save_json(CITE_GATE,{'status':'passed' if gate['passed'] else 'blocked','revision':CITE_REV,'time_utc':now(),'gate':gate,'plan_sha256':sha(CITE_PLAN),
        'received_copy':{'path':dst.relative_to(ROOT).as_posix(),'files':len(files),'tree_sha256':J.text_sha(J.canon(files)),'read_only':True},
        'run_notes_sha256':sha(d/'run-notes.md'),'thresholds':'unchanged (plan)','limitation':plan['limitation'],
        'importer_sha256':sha(EXP/'e6b_workpackage.py'),'labels_assigned':False,'model_api_calls':0,'human_verified':False})
    print(json.dumps({'status':'passed' if gate['passed'] else 'blocked','citation':gate['citation'],'sentinels':[s['citation_passed'] for s in gate['sentinels']]}))


def research_citation_packets(built):
    """F3 research citation packets (T3e export; T3c builds them in memory only): one per primary grounding packet (704),
    numbered as that grounding packet; claims fixed from the imported primary grounding rows."""
    packets=built[2];imp,_,rows=primary2_inputs(packets);out={};bindings=[];na=[];seen={}
    audit={x['context_sha256']:x['source_fragments_sha256'] for x in C.load(FRAGMENT_AUDIT)['contexts']}
    for r in rows:
        base=packets['grounding'][r['blind_id']];claims=r['response']['claims']
        blind='citation-'+r['blind_id'].rsplit('-',1)[1];p=citation_packet(base,claims,blind)
        if J.text_sha(J.canon(p['source_fragments']))!=audit.get(base['context_sha256']):raise ValueError(f'{blind}: fragments differ from the frozen F2 audit')
        key=J.canon({k:v for k,v in p.items() if k!='anchor_id'})
        if key in seen:seen[key]['grounding_blind_ids'].append(r['blind_id']);seen[key]['cells']+=[c['cell_id'] for c in r['cells']];continue
        out[blind]=p;seen[key]={'blind_id':blind,'grounding_blind_ids':[r['blind_id']],'cells':[c['cell_id'] for c in r['cells']],'claims':len(claims),
                                'blocks':len(p['source_fragments']),'merged_blocks':sum(len(b['fragments'])>1 for b in p['source_fragments']),
                                'unaligned_blocks':sum(b['alignment']!='exact' for b in p['source_fragments']),
                                'grounding_response_file_sha256':r['response_file_sha256'],'packet_canonical_sha256':J.text_sha(J.canon(p))}
        bindings.append(seen[key])
    if sum(len(x['cells']) for x in bindings)+sum(len(x['cells']) for x in na)!=720:raise ValueError('citation cells do not cover 720')
    return out,bindings,na,imp


def f7_controls():
    """F7 behaviour on the superseded primary-1 citation_pairs (no redo label exists): the D4 lanes must fail; interleaved segments,
    which mix judge contexts evenly, must pass; one segment falls back to four pseudo-segments."""
    L=C.module('e6b_lane_audit_f7',EXP/'e6b_lane_audit.py');lane=C.load(LANE_AUDIT['grounding']);task='research-primary-1/grounding'
    keep=lambda r:{k:r[k] for k in ('status','S1','S2','S3','pseudo_segments')}
    out={'data':'research-primary-1/grounding citation_pairs (superseded; read-only)','known_positive_D4_lanes':keep(L.f7(task,{k:[tuple(v['range'])] for k,v in lane['ranges'].items()})),
         'single_segment_pseudo_quartiles':keep(L.f7(task,{'all':[(1,704)]}))}
    for k in (4,7,14):out[f'negative_control_interleaved_mod{k}']=keep(L.f7(task,{f'mod{j}':[(n,n) for n in range(1,705) if n%k==j] for j in range(k)}))
    out['expected']='known positive not_met; interleaved controls met';out['as_expected']=(out['known_positive_D4_lanes']['status']=='not_met'
        and all(out[f'negative_control_interleaved_mod{k}']['status']=='met' for k in (4,7,14)))
    return out


def citation_dryrun():
    """T3c: build the research citation packets in memory only (no workpackage written) and record the design and the F7 draft."""
    built=K.build();frozen=research_freeze(built)
    if any(a!='verified_unchanged' for _,a in frozen.values()):raise SystemExit('frozen research record was rewritten')
    packets,bindings,na,imp=research_citation_packets(built);system,sysinfo=citation_system()
    for b,p in packets.items():
        if set(p)!={'anchor_id','query','context','source_fragments','context_sha256','raw_answer','response_sha256','claims','instruction'}:raise ValueError(f'{b}: fields')
    sizes=sorted(len(J.canon(citation_messages(p)).encode('utf8')) for p in packets.values())
    rec={'schema_version':'pearl-e6b-citation-redo-design-v1','status':'design_and_dry_run (no research citation packet exported)','time_utc':now(),
         'packet':{'fields':['anchor_id','query','context','source_fragments','context_sha256','raw_answer','response_sha256','claims','instruction'],
                   'from':'the frozen research grounding packet (e6b_packets.build), unchanged except: claims_candidates -> claims, source_fragments added, instruction -> r03',
                   'claims':'claim_id, verbatim text and located occurrences from the imported primary grounding rows; no label, evidence, reason, normalized_claim or conditions',
                   'instruction':CITE_INSTRUCTION,'numbering':'citation-NNNN = grounding-NNNN',
                   'no_claims':'exported with claims [] (only an empty citation_pairs validates), as calibration sentinel cal-33 (pure abstention, no claims); not NA'},
         'system_prompt':{**sysinfo,'sha256':J.text_sha(system),'output_format':CITE_FORMAT_R03},
         'dry_run':{'packets':len(packets),'cells':sum(len(x['cells']) for x in bindings),'not_exported_na':na,
                    'merged_duplicates':[x for x in bindings if len(x['grounding_blind_ids'])>1],
                    'claims':sum(x['claims'] for x in bindings),'blocks':sum(x['blocks'] for x in bindings),'merged_blocks':sum(x['merged_blocks'] for x in bindings),
                    'unaligned_blocks':sum(x['unaligned_blocks'] for x in bindings),'message_utf8_bytes':{'min':sizes[0],'median':sizes[len(sizes)//2],'max':sizes[-1]},
                    'packets_canonical_sha256':J.text_sha(J.canon({b:J.text_sha(J.canon(p)) for b,p in packets.items()}))},
         'claims_source':{'path':imp['tasks']['grounding']['rows'],'sha256':imp['tasks']['grounding']['rows_sha256'],'import_record_sha256':sha(IMPORT_P1)},
         'fragment_audit':{'path':FRAGMENT_AUDIT.relative_to(ROOT).as_posix(),'sha256':sha(FRAGMENT_AUDIT)},
         'f7_standard_draft':{**F7_STANDARD,'status':'draft (T3c); frozen verbatim into the research-citation-r03 export record in T3e'},
         'f7_controls':f7_controls(),
         'export_guard':'export --phase research-citation-r03 refuses unless calibration-gate-citation-r03.json is passed',
         'code_sha256':{f:sha(EXP/f) for f in ('e6b_workpackage.py','e6b_fragments.py','e6b_packets.py','e6b_prompts.py','e6b_lane_audit.py')},
         'labels_assigned':False,'model_api_calls':0}
    save_json(CITE_DESIGN,rec);print(json.dumps({k:v for k,v in rec['dry_run'].items() if k not in ('not_exported_na',)},ensure_ascii=False))


def citation_bindings_record(packets,bindings,na,imp):
    return {'schema_version':'pearl-e6b-citation-bindings-v1','note':'evaluation-side only; never sent to the judge','rule':CITE_DESIGN.name,
            'claims_source':{'path':imp['tasks']['grounding']['rows'],'sha256':imp['tasks']['grounding']['rows_sha256']},'packets':len(packets),
            'cells':sum(len(x['cells']) for x in bindings),'bindings':bindings,'not_exported_na':na}


def export_research_citation():
    """T3e only: after the F5 gate passed. Writes the workpackage (README by hand), the frozen bindings, and the export record with F7 frozen."""
    if not CITE_GATE.exists() or C.load(CITE_GATE).get('status')!='passed':raise SystemExit('F5 calibration citation gate has not passed; research citation packets are not exported')
    d=WP/CITE_RES
    if d.exists():raise FileExistsError(d)
    built=K.build();frozen=research_freeze(built)
    if any(a!='verified_unchanged' for _,a in frozen.values()):raise SystemExit('frozen research record was rewritten')
    packets,bindings,na,imp=research_citation_packets(built);system,sysinfo=citation_system()
    if J.text_sha(system)!=C.load(CITE_PLAN)['system_prompt_sha256']:raise SystemExit('r03 system prompt differs from the calibrated one')
    record=citation_bindings_record(packets,bindings,na,imp)
    frozen['citation_bindings']=(CITE_BINDINGS,freeze_or_check(CITE_BINDINGS,record))
    (d/'system-prompts').mkdir(parents=True);(d/'packets').mkdir();(d/'responses').mkdir()
    (d/'system-prompts'/f'{CITE_SYSTEM_NAME}.md').write_text(system,encoding='utf8',newline='\n');index=[]
    for blind,packet in packets.items():
        messages=citation_messages(packet)
        rec={'job_id':blind,'system_prompt':f'system-prompts/{CITE_SYSTEM_NAME}.md','system_prompt_sha256':J.text_sha(system),'user_message':messages[1]['content'],
             'messages_sha256':J.text_sha(J.canon(messages)),'identity_field':'anchor_id','identity_value':blind,'response_file':f'responses/{blind}.json'}
        p=d/'packets'/f'{blind}.json'
        with p.open('x',encoding='utf8',newline='\n') as f:json.dump(rec,f,ensure_ascii=False,indent=1);f.write('\n')
        index.append({'job_id':blind,'packet_file':f'packets/{blind}.json','packet_file_sha256':sha(p),'messages_sha256':rec['messages_sha256'],
                      'packet_canonical_sha256':J.text_sha(J.canon(packet)),'system_prompt':CITE_SYSTEM_NAME,'layer':'layer4','task':'citation'})
    save_json(d/'manifest.json',{'period':CITE_RES,'task':'citation','revision':CITE_REV,'stage':'primary','created_utc':now(),'packets':len(index),
        'system_prompts':{CITE_SYSTEM_NAME:J.text_sha(system)},'frozen_rules_prefix_identical_to_cgpt_r02':True,'contains_expected_labels':False,
        'contains_claim_labels':False,'contains_cell_identity':False,'index':index})
    save_json(RESEARCH/f'export-{CITE_RES}.json',{'time_utc':now(),'period':CITE_RES,'revision':CITE_REV,'workpackage':d.relative_to(ROOT).as_posix(),
        'workpackage_manifest_sha256':sha(d/'manifest.json'),'packets':len(index),'cells':record['cells'],'not_exported_na':na,
        'frozen':{k:{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'action':a} for k,(p,a) in frozen.items()},
        'f7_standard':{**F7_STANDARD,'status':'frozen at this export, before any citation redo label; not to be changed'},
        'system_prompt':sysinfo,'calibration_gate':{'path':CITE_GATE.relative_to(ROOT).as_posix(),'sha256':sha(CITE_GATE)},
        'design_record_sha256':sha(CITE_DESIGN),'fragment_audit_sha256':sha(FRAGMENT_AUDIT),
        'code_sha256':{f:sha(EXP/f) for f in ('e6b_workpackage.py','e6b_fragments.py','e6b_packets.py','e6b_prompts.py','e6b_judge.py','e6b_lane_audit.py','runtime.py')},
        'validator_sha256':sha(CITE_VALIDATOR),'labels_assigned':False,'model_api_calls':0,'human_verified':False})
    print(json.dumps({'period':CITE_RES,'packets':len(index),'na':len(na)}))


CITE_IMPORT=RESEARCH/f'import-{CITE_RES}.json'
CITE_F7=RESEARCH/'lane-audit-citation-r03-r01.json'


def citation_check(src):
    """T5a: every binding and response check for research-citation-r03; writes nothing. src: workpackage or received copy."""
    exp=C.load(RESEARCH/f'export-{CITE_RES}.json');problems=[]
    if sha(src/'manifest.json')!=exp['workpackage_manifest_sha256']:problems.append(('manifest','differs from export record'))
    for k,v in exp['frozen'].items():
        p=ROOT/v['path']
        if not p.exists() or sha(p)!=v['sha256']:problems.append((k,'frozen record missing or changed since export'))
    if sha(CITE_VALIDATOR)!=exp['validator_sha256']:problems.append(('validator','changed since export'))
    if sha(CITE_GATE)!=exp['calibration_gate']['sha256'] or C.load(CITE_GATE)['status']!='passed':problems.append(('F5 gate','changed or not passed'))
    if problems:raise SystemExit(f'citation binding check failed: {problems}')
    built=K.build();frozen=research_freeze(built)
    if any(a!='verified_unchanged' for _,a in frozen.values()):raise SystemExit('frozen research record was rewritten')
    packets,bindings,na,imp=research_citation_packets(built);system,_=citation_system()
    if freeze_or_check(CITE_BINDINGS,citation_bindings_record(packets,bindings,na,imp))!='verified_unchanged':raise SystemExit('citation bindings were rewritten')
    man=C.load(src/'manifest.json');sp=(src/'system-prompts'/f'{CITE_SYSTEM_NAME}.md').read_text(encoding='utf8');tp=[]
    if not J.text_sha(sp)==J.text_sha(system)==man['system_prompts'][CITE_SYSTEM_NAME]==C.load(CITE_PLAN)['system_prompt_sha256']:tp.append(('system_prompt','differs from the calibrated r03 prompt'))
    bind={b['blind_id']:b for b in bindings};V=citation_validator();responses={}
    if [i['job_id'] for i in man['index']]!=list(packets) or set(bind)!=set(packets):tp.append(('index','blind IDs differ from rebuild or bindings'))
    rows1={json.loads(x)['blind_id']:json.loads(x) for x in (ROOT/imp['tasks']['grounding']['rows']).read_text(encoding='utf8').splitlines()}
    for i in man['index']:
        blind=i['job_id'];pf=src/i['packet_file']
        if sha(pf)!=i['packet_file_sha256']:tp.append((blind,'packet file changed'));continue
        rec=C.load(pf);packet=packets[blind];messages=citation_messages(packet)
        if not J.text_sha(J.canon(messages))==i['messages_sha256']==rec['messages_sha256'] or rec['user_message']!=messages[1]['content']:tp.append((blind,'messages drift'));continue
        if not J.text_sha(J.canon(packet))==i['packet_canonical_sha256']==bind[blind]['packet_canonical_sha256']:tp.append((blind,'packet SHA differs from bindings'));continue
        if any(rows1[g]['response_file_sha256']!=bind[blind]['grounding_response_file_sha256'] for g in bind[blind]['grounding_blind_ids']):tp.append((blind,'superseded grounding row differs'));continue
        r=src/'responses'/f'{blind}.json'
        if not r.exists():tp.append((blind,'missing response'));continue
        try:obj=json.loads(r.read_text(encoding='utf8'))
        except Exception as e:tp.append((blind,f'invalid JSON: {e}'));continue
        bad=V.check(obj,rec)
        if bad:tp.append((blind,bad));continue
        responses[blind]=(obj,r,packet,i)
    if not (src/'run-notes.md').exists():tp.append(('run-notes','missing'))
    cells=sum(len(b['cells']) for b in bind.values())+sum(len(x['cells']) for x in na)
    if cells!=720:tp.append(('cells',f'{cells} bound cells, expected 720'))
    if tp:raise SystemExit(f'{len(tp)} check problems, e.g. {tp[:10]}')
    return exp,bind,responses,imp,rows1


def import_research_citation():
    """T5a: validate, hash-check and bind the 704 redo responses to their cells; locate citation offsets with the frozen locator; the redo
    supersedes the primary-1 citation_pairs, which stay unchanged in the primary-1 import rows (never scored)."""
    src=WP/CITE_RES;dst=RESEARCH/f'workpackage-{CITE_RES}-received';out=RESEARCH/f'import-{CITE_RES}'
    if dst.exists() or out.exists() or CITE_IMPORT.exists():raise FileExistsError(f'{CITE_RES} already imported')
    citation_check(src)  # live workpackage first, before copying anything
    shutil.copytree(src,dst);files=tree_sha(dst)
    if files!=tree_sha(src):raise SystemExit('received copy differs from the workpackage')
    for p in dst.rglob('*'):
        if p.is_file():os.chmod(p,stat.S_IREAD)
    exp,bind,responses,imp,rows1=citation_check(dst);idmap=C.load(RESEARCH/'research-identity-map-r01.json')
    notes=(dst/'run-notes.md').read_text(encoding='utf8');ctx=t5a_judge('citation',notes);out.mkdir();rows=[];loc_problems={};pairs_n=0;unclassified=0
    for blind,(obj,r,packet,i) in responses.items():
        b=bind[blind];loc=P.locate_grounding({'citation_pairs':obj['citation_pairs']},packet['raw_answer'])
        frag={f['fragment_id']:(blk['block_id'],len(blk['fragments'])>1) for blk in packet['source_fragments'] for f in blk['fragments']}
        pairs=[{**p,'source_block':frag.get(p['source_id'],(None,None))[0],'source_block_merged':frag.get(p['source_id'],(None,None))[1]} for p in loc['citation_pairs']]
        unclassified+=sum(p['source_block'] is None for p in pairs);pairs_n+=len(pairs)
        if loc['location_problems']:loc_problems[blind]=loc['location_problems']
        rows.append({'schema_version':'pearl-e6b-research-import-row-v1','period':CITE_RES,'revision':CITE_REV,'stage':'primary','task':'citation','blind_id':blind,
                     'cells':[{'cell_id':c,**{k:idmap['cells'][c][k] for k in ('arm','intent_id','replicate')}} for c in b['cells']],
                     'grounding_blind_ids':b['grounding_blind_ids'],'packet_canonical_sha256':i['packet_canonical_sha256'],'messages_sha256':i['messages_sha256'],
                     'response_file':r.relative_to(ROOT).as_posix(),'response_file_sha256':sha(r),'judge_context':context_of(T5A_JUDGE_CONTEXTS['citation'],blind),
                     'response':{'anchor_id':obj['anchor_id'],'citation_pairs':pairs,'citation_extraction_unknown':obj['citation_extraction_unknown'],'reason':obj['reason']},
                     'location_problems':loc['location_problems'],
                     'supersedes':{'period':'research-primary-1','task':'grounding','blind_ids':b['grounding_blind_ids'],'field':'citation_superseded',
                                   'action':'primary-1 citation_pairs retained unchanged in the primary-1 import rows; not scored'},
                     'human_verified':False})
    path=out/'citation.jsonl'
    with path.open('x',encoding='utf8',newline='\n') as f:
        for row in rows:f.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+'\n')
    p1=imp['tasks']['grounding']
    save_json(CITE_IMPORT,{'time_utc':now(),'period':CITE_RES,'revision':CITE_REV,'stage':'primary',
        'judge':{**RESEARCH_JUDGE,'note':'identity as written in the run-notes; four contexts dispatched with the README F6 template and fork_turns=none per the coordinator record; '
                 'this session cannot verify the executed model','per_task':{'citation':ctx}},
        'tasks':{'citation':{'responses':len(rows),'cells_bound':sum(len(r['cells']) for r in rows),'pairs':pairs_n,'rows':path.relative_to(ROOT).as_posix(),'rows_sha256':sha(path),
                             'run_notes_sha256':sha(dst/'run-notes.md'),'manifest_sha256':sha(dst/'manifest.json'),'location_problems':loc_problems,
                             'pairs_source_id_not_a_fragment':unclassified,
                             'offsets':'frozen e6b_prompts.locate_grounding on citation_text and citation_occurrence; the harness, not the judge, binds offsets'}},
        'supersedes':{'what':'research-primary-1 grounding citation_pairs and citation_extraction_unknown (deviation D4)','rows':p1['rows'],'rows_sha256':p1['rows_sha256'],
                      'rows_unchanged':sha(ROOT/p1['rows'])==p1['rows_sha256'],'pairs_superseded':p1['citation_pairs_superseded'],
                      'action':'retained verbatim and unchanged; citation metrics read only the redo rows','claim_labels':'primary-1 claim-level grounding retained (F3)'},
        'received_copy':{'path':dst.relative_to(ROOT).as_posix(),'files':len(files),'tree_sha256':J.text_sha(J.canon(files)),'read_only':True,'identical_to_workpackage_at_import':True},
        'checks':{'manifest':'equal to export record','packet_files':'equal to manifest SHA',
                  'packets':'rebuilt from e6b_packets.build() and the imported primary grounding rows; messages and canonical packet SHA equal to manifest and citation bindings',
                  'frozen_records':'identity map, secondary sample and citation bindings verified unchanged; F5 gate passed and unchanged',
                  'system_prompt':'equal to the calibrated r03 prompt (calibration-plan-citation-r03)','responses':'validate_citation_responses.check, the validator SHA frozen at export',
                  'superseded_rows':'each bound primary grounding response file SHA equal to the one recorded in the citation bindings','cells':'720 cells bound'},
        'f7':{'standard':'frozen in the export record (f7_standard); evaluated separately by citation-f7','record':CITE_F7.relative_to(ROOT).as_posix()},
        'export_record_sha256':sha(RESEARCH/f'export-{CITE_RES}.json'),'identity_map_sha256':sha(RESEARCH/'research-identity-map-r01.json'),
        'deviation_record':'paper/pearl-6b-judge-workpackage/incidents-and-deviations.md (T5a entries)',
        'code_sha256':{f:sha(EXP/f) for f in ('e6b_workpackage.py','e6b_fragments.py','e6b_packets.py','e6b_prompts.py','e6b_judge.py','runtime.py')},
        'validator_sha256':sha(CITE_VALIDATOR),'labels_assigned':False,'labels_changed':False,'scored':False,'model_api_calls':0,'human_verified':False})
    print(json.dumps({'period':CITE_RES,'responses':len(rows),'cells':sum(len(r['cells']) for r in rows),'pairs':pairs_n,'location_problems':len(loc_problems),
                      'source_id_not_a_fragment':unclassified}))


def citation_f7():
    """T5a: F7 on the imported redo with the standard frozen in the export record and the e6b_lane_audit.py frozen with it (SHA checked).
    Segments are the four judge contexts of the run-notes. Writes met / not_met; changes no label, segment or threshold."""
    if CITE_F7.exists():raise FileExistsError(CITE_F7)
    exp=C.load(RESEARCH/f'export-{CITE_RES}.json');imp=C.load(CITE_IMPORT);tool=EXP/'e6b_lane_audit.py'
    if sha(tool)!=exp['code_sha256']['e6b_lane_audit.py']:raise SystemExit('e6b_lane_audit.py differs from the tool frozen with F7')
    if {k:v for k,v in exp['f7_standard'].items() if k!='status'}!=F7_STANDARD:raise SystemExit('F7 standard in code differs from the frozen export record')
    rc=imp['received_copy'];dst=ROOT/rc['path']
    if J.text_sha(J.canon(tree_sha(dst)))!=rc['tree_sha256'] or tree_sha(dst)!=tree_sha(WP/CITE_RES):raise SystemExit('workpackage or received copy differs from the import')
    L=C.module('e6b_lane_audit_f7',tool);th=exp['f7_standard']['thresholds']
    if (L.F7['seed'],L.F7['permutations'],L.F7['S1_p_min'],L.F7['S2_p_min'],L.F7['S3_p_min'])!=(20261005,10000,th['S1_p_min'],th['S2_p_min'],th['S3_p_min']):raise SystemExit('tool constants differ from the standard')
    ranges={c:[tuple(s) for s in v] for c,v in T5A_JUDGE_CONTEXTS['citation'].items()}
    _,_,res=L.audit(CITE_RES,ranges);f=L.f7(CITE_RES,ranges)
    rows=[json.loads(x) for x in (ROOT/imp['tasks']['citation']['rows']).read_text(encoding='utf8').splitlines()]
    if sha(ROOT/imp['tasks']['citation']['rows'])!=imp['tasks']['citation']['rows_sha256']:raise SystemExit('import rows changed')
    split={};conf={}
    for r in rows:
        s=split.setdefault(r['judge_context'],{'merged':{},'single':{},'unclassified':{}})
        arms=sorted({c['arm'] for c in r['cells']});a=conf.setdefault(arms[0] if len(arms)==1 else 'mixed',{})
        for p in r['response']['citation_pairs']:
            k='unclassified' if p['source_block_merged'] is None else 'merged' if p['source_block_merged'] else 'single'
            s[k][p['label']]=s[k].get(p['label'],0)+1;a[p['label']]=a.get(p['label'],0)+1
    rec={'schema_version':'pearl-e6b-lane-audit-v1','task_dir':CITE_RES,'task':'citation','manifest_sha256':sha(WP/CITE_RES/'manifest.json'),
         'ranges_source':'research-citation-r03/run-notes.md (four contexts x 176, contiguous, non-overlapping)','ranges':res,
         'f7':f,'f7_status':f['status'],'f7_standard':{'path':f'outputs/pearl-chunking-dev80-20261007-16/research/export-{CITE_RES}.json#f7_standard','version':exp['f7_standard']['version'],
                                                      'export_record_sha256':sha(RESEARCH/f'export-{CITE_RES}.json')},
         'auditor_sha256':sha(tool),'auditor_sha256_frozen_at_export':exp['code_sha256']['e6b_lane_audit.py'],
         'auditor_function_source_sha256':{n:J.text_sha(inspect.getsource(getattr(L,n))) for n in ('f7','x2','inside','audit')},
         'invocation':'e6b_workpackage.citation_f7 calls e6b_lane_audit.audit and .f7 directly (the CLI merged_share reads identity-map bindings, which have no citation task; algorithm unchanged)',
         'descriptive_only':{'per_segment_pair_labels_by_cited_block':split,'per_configuration_pair_labels':dict(sorted(conf.items())),
                             'merged_block_share_by_configuration':{k:v['merged_share'] for k,v in C.load(FRAGMENT_AUDIT)['by_configuration'].items()}},
         'import_record_sha256':sha(CITE_IMPORT),'labels_assigned':False,'labels_changed':False,'model_api_calls':0,
         'on_not_met':exp['f7_standard']['not_met'] if f['status']!='met' else None}
    save_json(CITE_F7,rec)
    print(json.dumps({k:f.get(k) for k in ('status','S1','S2','S3','segments')},ensure_ascii=False))


CITE_F7_INVESTIGATION=RESEARCH/'f7-investigation-citation-r03-r01.json'
CLAIM_HAS_CITATION_REASON=re.compile(r'(claim|主张).{0,12}(含|包含|包括).{0,6}(完整)?引用|固定.{0,8}(含|包含).{0,4}引')
F7_EVENTS_ROOT={'compressions_after':[16,37,60,83,106,128,148,169],'first_claim_contains_citation_unknown_in_run_notes':98,
                'source':'research-citation-r03/run-notes.md, coordinator entries (compression 1-8; citation-0098 is the first entry naming a fixed claim that contains the citation)'}


def citation_f7_investigation():
    """F7 not_met step 2 (frozen standard): segment-by-segment investigation. Read-only on labels; descriptive counts only, no verdict change."""
    if CITE_F7_INVESTIGATION.exists():raise FileExistsError(CITE_F7_INVESTIGATION)
    f7=C.load(CITE_F7);imp=C.load(CITE_IMPORT)
    if f7['f7_status']=='met':raise SystemExit('F7 met; nothing to investigate')
    rows=[json.loads(x) for x in (ROOT/imp['tasks']['citation']['rows']).read_text(encoding='utf8').splitlines()];num=lambda r:int(r['blind_id'].rsplit('-',1)[1])
    claims={r['blind_id']:C.load(WP/CITE_RES/'packets'/f'{r["blind_id"]}.json') for r in rows}
    claims={b:json.loads(p['user_message'].split('\n',1)[1])['claims'] for b,p in claims.items()}
    has_cite=lambda b:any('[Source' in c['text'] or 'Source:' in c['text'] for c in claims[b])  # packet property (primary-1 claim spans), not a label
    def tally(sel):
        lab={};x=0;on_frag=0;cc=0
        for r in sel:
            x+=r['response']['citation_extraction_unknown']
            for p in r['response']['citation_pairs']:
                lab[p['label']]=lab.get(p['label'],0)+1
                if p['label']=='unknown' and p['source_block'] is not None:on_frag+=1
                if p['label']=='unknown' and CLAIM_HAS_CITATION_REASON.search(p['reason']):cc+=1
        n=sum(lab.values())
        return {'packets':len(sel),'pairs':n,'unknown_share':round(lab.get('unknown',0)/n,4) if n else None,'extraction_unknown_share':round(x/len(sel),4) if sel else None,
                'unknown_pairs_on_identified_fragment':on_frag,'unknown_pairs_reason_claim_contains_citation':cc,'labels':dict(sorted(lab.items()))}
    seg={c:tally([r for r in rows if r['judge_context']==c]) for c in T5A_JUDGE_CONTEXTS['citation']}
    sub={f'{a}-{b}':tally([r for r in rows if a<=num(r)<=b]) for a,b in ((1,40),(41,80),(81,97),(98,147),(148,176))}
    exposure={c:{'packets_with_claim_containing_citation':sum(has_cite(r['blind_id']) for r in rows if r['judge_context']==c),
                 **{k:v for k,v in tally([r for r in rows if r['judge_context']==c and has_cite(r['blind_id'])]).items() if k in ('pairs','unknown_share')}} for c in T5A_JUDGE_CONTEXTS['citation']}
    rec={'schema_version':'pearl-e6b-f7-investigation-v1','time_utc':now(),'f7_record':{'path':CITE_F7.relative_to(ROOT).as_posix(),'sha256':sha(CITE_F7),'status':f7['f7_status']},
         'verdict':'F7 not_met stands; no label changed, no segment dropped, thresholds unchanged (frozen not_met rule)',
         'drivers':{'S1':f7['f7']['S1'],'S2':f7['f7']['S2'],'S3':f7['f7']['S3']},'per_segment':seg,'coordinator_subranges':sub,'coordinator_events':F7_EVENTS_ROOT,
         'claims_containing_citation_exposure':exposure,
         'merged_vs_single':f7['descriptive_only']['per_segment_pair_labels_by_cited_block'],
         'findings':['the coordinator segment /root (citation-0001..0176) drives S2 and S3; the three sub-agent segments have unknown shares 0.106-0.126',
                     'in the sub-agent segments unknown pairs are almost only pairs whose source_id is not a fragment (document-level or author-year citations); '
                     '/root also labels unknown many pairs whose cited fragment is identified (merged and single blocks)',
                     '/root alone treats a fixed claim whose text contains the citation string as not covered by the rules (unknown, F6 rule 3), first at citation-0098 '
                     '(after its fourth context compression) and in 47 packets up to 0174; the other contexts meet such packets too and judge them',
                     '/root also records corrupted source units or symbols (e.g. mŁ 1, Ł 0.38 s) as uncovered, unknown',
                     'extraction-unknown share rises within /root across its range; among the sub-agents review_0177_0352 is higher (0.31) than the other two (0.14-0.15)',
                     'the fixed claims come from primary-1 grounding: claim spans that include the citation string are a primary-1 extraction property present in all segments'],
         'reason_pattern':CLAIM_HAS_CITATION_REASON.pattern,'labels_assigned':False,'labels_changed':False,'model_api_calls':0,
         'code_sha256':{'e6b_workpackage.py':sha(EXP/'e6b_workpackage.py')}}
    save_json(CITE_F7_INVESTIGATION,rec);print(json.dumps({'per_segment':seg,'coordinator_subranges':sub,'exposure':exposure},ensure_ascii=False)[:3000])


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('cmd',choices=['export','validate','import','compare','facts-check','fragments-audit','citation-dryrun','citation-f7','citation-f7-investigate'])
    ap.add_argument('--phase',choices=list(PHASES)+list(PERIODS)+[CITE_CAL,CITE_RES]);a=ap.parse_args()
    if a.cmd=='facts-check':facts_check();raise SystemExit
    if a.cmd=='fragments-audit':fragments_audit();raise SystemExit
    if a.cmd=='citation-dryrun':citation_dryrun();raise SystemExit
    if a.cmd=='citation-f7':citation_f7();raise SystemExit
    if a.cmd=='citation-f7-investigate':citation_f7_investigation();raise SystemExit
    if not a.phase:ap.error('--phase is required')
    if a.phase==CITE_CAL:
        if a.cmd=='export':export_calibration_citation()
        elif a.cmd=='import':import_calibration_citation()
        else:raise SystemExit(f'{a.cmd} is not defined for {CITE_CAL}; use validate_citation_responses.py')
        raise SystemExit
    if a.phase==CITE_RES:
        if a.cmd=='export':export_research_citation()
        elif a.cmd=='import':import_research_citation()
        else:raise SystemExit(f'{a.cmd} is not defined for {CITE_RES}; use validate_citation_responses.py')
        raise SystemExit
    if a.phase in PERIODS:
        if a.cmd=='export':export_research(a.phase)
        elif a.cmd=='validate':
            for task in PERIODS[a.phase]['tasks']:
                ok,p,_=validate(WP/a.phase/task);print(json.dumps({'task':task,'valid':ok,'problems':len(p),'examples':p[:10]},ensure_ascii=False))
        elif a.cmd=='import':import_research(a.phase)
        else:raise SystemExit('research compare is not part of T3a')
    elif a.cmd=='export':export(a.phase)
    elif a.cmd=='validate':
        ok,p,_=validate(WP/a.phase);print(json.dumps({'valid':ok,'problems':len(p),'examples':p[:10]},ensure_ascii=False))
    elif a.cmd=='compare':compare_only(a.phase)
    else:do_import(a.phase)
