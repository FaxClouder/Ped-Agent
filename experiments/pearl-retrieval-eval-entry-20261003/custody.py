"""Explicit Gold/review custody, dynamically validated scoring; never imported by runtime."""
from pathlib import Path
import importlib.util
import math
import random
import sys

from runtime import OLD, METHODS, KS, STRATA, SPLITS, read, rows, sha, write


def legacy(name):
    sys.path.insert(0,str(OLD))
    spec=importlib.util.spec_from_file_location('entry_legacy_'+name,OLD/(name+'.py'))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return m


old_score=legacy('score')
old_blind=legacy('blind')
old_analysis=legacy('analyze')
old_verify=legacy('verify')


def gold_split(gold):
    return {'development':'development_80','sealed_independent_evaluation':'evaluation_200',
            'development_80':'development_80','evaluation_200':'evaluation_200'}.get(gold.get('split'))


def export_queries(gold_path,runtime_config_path,output,expected_count):
    """Custodian-side projection. Only the emitted contract/query view goes to the executor."""
    from collections import Counter
    from runtime import validate_contract,write_rows
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    gold=read(gold_path);config=read(runtime_config_path)
    split=gold_split(gold)
    if SPLITS.get(split)!=expected_count:raise ValueError('Gold export split/count')
    q_by=old_score.validate_gold_set(gold,expected_count)
    expected_intent_split='dev_candidate' if expected_count==80 else 'eval_candidate'
    if any(q.get('split',expected_intent_split)!=expected_intent_split for q in q_by.values()):raise ValueError('Gold per-intent cross-split export')
    if Counter(q['main_stratum'] for q in q_by.values())!={h:expected_count//4 for h in STRATA}:raise ValueError('Gold export quota')
    child_path=Path(config['index_dir'])/'child_chunks.jsonl'
    if ('child_path' in gold and Path(gold['child_path']).resolve()!=child_path.resolve()) or gold['frozen_child_library_sha256']!=sha(child_path):raise ValueError('Gold export actual child mismatch')
    queries=[dict(intent_id=i,query=q['query']) for i,q in q_by.items()]
    write_rows(output/'queries.jsonl',queries)
    config.update(identity_kind='raw-run',split=split,expected_count=expected_count,stratum_quotas={h:expected_count//4 for h in STRATA},
        queries_path=str((output/'queries.jsonl').resolve()),queries_sha256=sha(output/'queries.jsonl'),intent_ids=list(q_by),
        custody_binding={'gold_sha256':sha(gold_path),'child_sha256':sha(child_path)})
    config['runtime_files']=[p for p in config['runtime_files'] if p!=read(runtime_config_path).get('queries_path')]+[config['queries_path']]
    validate_contract(config);write(output/'contract.json',config)
    write(output/'custodian-export-receipt.json',dict(role='custodian',gold_sha256=sha(gold_path),contract_sha256=sha(output/'contract.json'),
        queries_sha256=sha(output/'queries.jsonl'),split=split,expected_count=expected_count,note='Executor receives no Gold path; register/pin the selected complete release before launch.'))
    return output/'contract.json'


def load_run(directory,gold_path,expected_count):
    directory=Path(directory);gold_path=Path(gold_path)
    run=read(directory/'run_manifest.json');seal=read(directory/'ranking-seal.json');gold=read(gold_path)
    if run.get('identity_kind')!='raw-run' or seal.get('identity_kind')!='raw-run':raise ValueError('revision-analysis cannot masquerade as raw-run')
    if run['status']!='retrieval_complete' or run['execution_failures'] or run['completed_queries_by_pass']!={str(p):expected_count for p in (1,2,3)}:raise ValueError('execution incomplete or failed; no quality score')
    old_score.verify_hash(directory/'run_manifest.json',seal['run_manifest_sha256'])
    old_score.verify_hash(directory/'rankings.jsonl',seal['rankings_sha256'])
    for name,digest in run['output_sha256'].items():old_score.verify_hash(directory/name,digest)
    old_score.verify_hash(run['contract_path'],run['contract_sha256']);contract=read(run['contract_path'])
    if sha(gold_path)!=contract['custody_binding']['gold_sha256']:raise ValueError('raw-run Gold identity mismatch; use separate revision-analysis')
    actual_child=Path(contract['index_dir'])/'child_chunks.jsonl'
    if ('child_path' in gold and Path(gold['child_path']).resolve()!=actual_child.resolve()) or sha(actual_child)!=contract['custody_binding']['child_sha256']:raise ValueError('raw-run frozen child binding mismatch')
    if expected_count!=run['expected_count'] or SPLITS.get(gold_split(gold))!=expected_count or gold_split(gold)!=run['split']:raise ValueError('Gold split/count mismatch')
    q_by=old_score.validate_gold_set(gold,expected_count)
    expected_intent_split='dev_candidate' if expected_count==80 else 'eval_candidate'
    if any(q.get('split',expected_intent_split)!=expected_intent_split for q in q_by.values()):raise ValueError('Gold per-intent cross-split')
    from collections import Counter
    if Counter(q['main_stratum'] for q in q_by.values())!={h:expected_count//4 for h in STRATA}:raise ValueError('Gold stratum quota mismatch')
    queries=rows(contract['queries_path'])
    if {q['intent_id']:q['query'] for q in queries}!={i:q['query'] for i,q in q_by.items()}:raise ValueError('Gold/query cross-split identity')
    old_score.verify_hash(contract['queries_path'],run['queries_sha256'])
    old_score.verify_hash(actual_child,gold['frozen_child_library_sha256'])
    children_list=rows(actual_child);children={c['chunk_id']:c for c in children_list}
    if len(children)!=len(children_list):raise ValueError('duplicate child')
    for c in children.values():old_score.validate_child(c)
    rankings=rows(directory/'rankings.jsonl');by={}
    for row in rankings:
        key=(row['intent_id'],row['method'])
        if key in by or key[0] not in q_by:raise ValueError('duplicate/unexpected ranking')
        old_score.validate_ranking(row,q_by[key[0]],children);by[key]=row
    if set(by)!={(i,m) for i in q_by for m in METHODS}:raise ValueError('missing matrix cell')
    for i in q_by:
        a={c['chunk_id']:(c['text'],c['text_sha256']) for c in by[i,'R3']['results']}
        b={c['chunk_id']:(c['text'],c['text_sha256']) for c in by[i,'R4']['results']}
        if a!=b:raise ValueError('R3/R4 body identity')
    for p in (2,3):
        repeated=rows(directory/f'pass-{p}/rankings.jsonl')
        signature=lambda rs:{(r['intent_id'],r['method']):(r['status'],r['query'],[(x['chunk_id'],x['score']) for x in r['results']]) for r in rs}
        if len(repeated)!=expected_count*4 or signature(repeated)!=signature(rankings):raise ValueError('repeat determinism')
        if read(directory/f'pass-{p}/query-vectors.json')!=read(directory/'pass-1/query-vectors.json'):raise ValueError('repeat vectors')
    return dict(directory=directory,gold_path=gold_path,gold=gold,q_by=q_by,children=children,ranks=by,run=run)


def packets(directory,gold_path,expected_count):
    inputs=load_run(directory,gold_path,expected_count);directory=Path(directory)
    for i,q in inputs['q_by'].items():
        core={c['chunk_id'] for m in METHODS for c in inputs['ranks'][i,m]['results'][:20]}
        pool={c['chunk_id'] for m in METHODS for c in inputs['ranks'][i,m]['results']}
        sources={a['source_id'] for a in q['atoms']}
        pool |= {c['chunk_id'] for c in inputs['children'].values() if c['source_id'] in sources}
        rng=random.Random(int.from_bytes(i.encode(),'little')+20260929)
        cs=[inputs['children'][c] for c in sorted(core)];ss=[inputs['children'][c] for c in sorted(pool-core)]
        rng.shuffle(cs);rng.shuffle(ss)
        packet=old_blind.packet(q,cs,ss)
        write(directory/'review/packets'/(i+'.json'),packet)
    return inputs


def combine(directory,gold_path,selection_path,output,expected_count):
    inputs=load_run(directory,gold_path,expected_count);directory=Path(directory)
    selection=read(selection_path)
    if selection.get('identity_kind')!='raw-run-review-selection' or selection.get('run_manifest_sha256')!=sha(directory/'run_manifest.json'):raise ValueError('review selection run binding')
    files=selection['files']
    if len(files)!=expected_count or len({f['intent_id'] for f in files})!=expected_count or {f['intent_id'] for f in files}!=set(inputs['q_by']):raise ValueError('unique selected review coverage')
    if len({str(Path(f['path']).resolve()) for f in files})!=len(files):raise ValueError('duplicate selected review path')
    validated=[];hashes={};packet_hashes={}
    for item in files:
        i=item['intent_id'];path=Path(item['path']);old_score.verify_hash(path,item['sha256'])
        decision=read(path)
        packet_path=directory/'review/packets'/(i+'.json');packet=read(packet_path);old_blind.assert_blind(packet)
        for child in packet['candidates']+packet.get('supplementary_candidates',[]):old_score.validate_child(child,inputs['children'])
        core={c['chunk_id'] for m in METHODS for c in inputs['ranks'][i,m]['results'][:20]}
        if {c['chunk_id'] for c in packet['candidates']}!=core:raise ValueError('neutral packet required union mismatch')
        decision=old_score.validate_decision(inputs['q_by'][i],packet,decision,sha(packet_path))
        for m in METHODS:old_score.require_reviewed([c['chunk_id'] for c in inputs['ranks'][i,m]['results']],decision['reviewed_ids'],20)
        validated.append(decision);hashes[str(path.resolve())]=sha(path);packet_hashes[packet_path.relative_to(directory).as_posix()]=sha(packet_path)
    mapping=dict(identity_kind='raw-run-support-map',status='synthetic_fixture' if inputs['gold'].get('synthetic') else 'agent_reviewed_preliminary',
                 run_manifest_sha256=sha(directory/'run_manifest.json'),ranking_seal_sha256=sha(directory/'ranking-seal.json'),
                 gold_sha256=sha(gold_path),rankings_sha256=sha(directory/'rankings.jsonl'),selection_path=str(Path(selection_path).resolve()),
                 selection_sha256=sha(selection_path),review_sha256=hashes,packets_sha256=packet_hashes,intents=validated)
    write(output,mapping);return mapping


def load_validated(directory,gold_path,mapping_path,expected_count):
    inputs=load_run(directory,gold_path,expected_count);directory=Path(directory);mapping=read(mapping_path)
    for path,key in [(gold_path,'gold_sha256'),(directory/'run_manifest.json','run_manifest_sha256'),(directory/'ranking-seal.json','ranking_seal_sha256'),(directory/'rankings.jsonl','rankings_sha256'),(mapping['selection_path'],'selection_sha256')]:old_score.verify_hash(path,mapping[key])
    selected=read(mapping['selection_path'])['files']
    if len(selected)!=expected_count or len({f['intent_id'] for f in selected})!=expected_count:raise ValueError('selected review coverage')
    original=[]
    for f in selected:
        old_score.verify_hash(f['path'],f['sha256']);original.append(read(f['path']))
    by={d['intent_id']:d for d in original};mapped={d['intent_id']:d for d in mapping['intents']}
    if by!=mapped or set(by)!=set(inputs['q_by']) or len(mapping['intents'])!=expected_count:raise ValueError('map differs from full selected review')
    if mapping['review_sha256']!={str(Path(f['path']).resolve()):f['sha256'] for f in selected}:raise ValueError('review SHA coverage')
    if set(mapping['packets_sha256'])!={'review/packets/'+i+'.json' for i in by}:raise ValueError('packet hash coverage')
    for i,q in inputs['q_by'].items():
        path=directory/'review/packets'/(i+'.json');old_score.verify_hash(path,mapping['packets_sha256'][path.relative_to(directory).as_posix()])
        packet=read(path);old_blind.assert_blind(packet)
        for child in packet['candidates']+packet.get('supplementary_candidates',[]):old_score.validate_child(child,inputs['children'])
        old_score.validate_decision(q,packet,by[i],sha(path))
        for m in METHODS:old_score.require_reviewed([c['chunk_id'] for c in inputs['ranks'][i,m]['results']],by[i]['reviewed_ids'],20)
    inputs.update(decisions=by,mapping=mapping);return inputs


def score_and_verify(directory,gold_path,mapping_path,expected_count):
    inputs=load_validated(directory,gold_path,mapping_path,expected_count);directory=Path(directory)
    details=old_score.build_details(inputs);summary=old_score.aggregate(details)
    scores=dict(identity_kind='raw-run-scoring',status='synthetic_fixture' if inputs['gold'].get('synthetic') else 'agent_reviewed_preliminary',
                intent_count=expected_count,split=inputs['run']['split'],native_gold_split=inputs['gold']['split'],human_verified=False,
                gold_sha256=sha(gold_path),mapping_sha256=sha(mapping_path),rankings_sha256=sha(directory/'rankings.jsonl'),
                summary=summary,details=details,strata={h:old_score.aggregate(details,{i for i,q in inputs['q_by'].items() if q['main_stratum']==h}) for h in STRATA})
    write(directory/'score-details.json',scores)
    stats=old_analysis.statistics(inputs,details)
    stats['interpretation']='Synthetic adapter verification only; no empirical PEARL evaluation or research conclusion.' if inputs['gold'].get('synthetic') else 'Frozen evaluation analysis; source dependence and review status limit inference.'
    for v in stats['comparisons'].values():v['interpretation']=stats['interpretation']
    write(directory/'statistics.json',stats)
    unknown={i:{m:old_analysis.depth_state(inputs['q_by'][i],inputs['decisions'][i],[c['chunk_id'] for c in inputs['ranks'][i,m]['results']],100) for m in METHODS} for i in inputs['q_by']}
    failures=[dict(intent_id=d['intent_id'],method=d['method'],CEGR_at_10=d['scores']['10']['CEGR'],missing_requirements=d['scores']['10']['missing_requirements_by_group']) for d in details if not d['scores']['10']['CEGR']]
    write(directory/'failures-and-unknown.json',dict(quality_failures=failures,unknown_depth=unknown,execution_failures=inputs['run']['execution_failures'],retry_attempts=inputs['run']['attempt_failures']))
    # Independent oracle imports no scorer and derives each prefix from Boolean membership.
    values={};prefixes=0
    by_details={(d['intent_id'],d['method']):d for d in details}
    for (i,m),rank in inputs['ranks'].items():
        values[i,m]={}
        for k in KS:
            actual=old_verify.oracle(inputs['q_by'][i],inputs['decisions'][i]['atom_paths'],[c['chunk_id'] for c in rank['results']],k)
            target=by_details[i,m]['scores'][str(k)]
            if any(actual[f]!=target[f] for f in actual):raise ValueError('independent oracle prefix mismatch')
            values[i,m][k]=actual;prefixes+=1
    total=0
    for m in METHODS:
        for k in KS:
            for field,label in [('CEGR','CEGR'),('BestGroupCov','BestGroupCov'),('CompleteRR','CompleteMRR')]:
                actual=sum(values[i,m][k][field] for i in inputs['q_by'])/expected_count
                if not math.isclose(actual,summary[m][str(k)][label],abs_tol=1e-12):raise ValueError('oracle overall metric')
                total+=1
    verification=dict(prefixes_verified=prefixes,overall_metrics_verified=total)
    write(directory/'independent-oracle.json',verification)
    write(directory/'analysis-binding.json',dict(identity_kind='raw-run-analysis',gold_sha256=sha(gold_path),mapping_sha256=sha(mapping_path),
        files_sha256={n:sha(directory/n) for n in ('score-details.json','statistics.json','failures-and-unknown.json','independent-oracle.json')},
        code_sha256={str(Path(p).resolve()):sha(p) for p in [Path(__file__),OLD/'score.py',OLD/'protocol.py',OLD/'analyze.py',OLD/'verify.py',OLD/'blind.py',OLD.parent/'pearl-index-106-adobe-20260929/score_pilot.py']}))
    return verify_saved(directory,gold_path,mapping_path,expected_count)


def verify_saved(directory,gold_path,mapping_path,expected_count):
    """Fresh reopen; Boolean oracle verifies persisted scalars without calling build_details/aggregate."""
    inputs=load_validated(directory,gold_path,mapping_path,expected_count);directory=Path(directory)
    binding=read(directory/'analysis-binding.json')
    if binding['identity_kind']!='raw-run-analysis' or binding['gold_sha256']!=sha(gold_path) or binding['mapping_sha256']!=sha(mapping_path):raise ValueError('analysis identity drift')
    for name,h in binding['files_sha256'].items():old_score.verify_hash(directory/name,h)
    for path,h in binding['code_sha256'].items():old_score.verify_hash(path,h)
    saved=read(directory/'score-details.json')
    if saved['intent_count']!=expected_count or saved['gold_sha256']!=sha(gold_path) or saved['mapping_sha256']!=sha(mapping_path) or saved['rankings_sha256']!=sha(directory/'rankings.jsonl'):raise ValueError('saved score binding')
    details={(d['intent_id'],d['method']):d for d in saved['details']}
    if len(details)!=expected_count*4 or len(saved['details'])!=len(details) or set(details)!=set(inputs['ranks']):raise ValueError('persisted score matrix')
    totals={};prefixes=0
    for (i,m),row in inputs['ranks'].items():
        for k in KS:
            actual=old_verify.oracle(inputs['q_by'][i],inputs['decisions'][i]['atom_paths'],[c['chunk_id'] for c in row['results']],k)
            if any(actual[f]!=details[i,m]['scores'][str(k)][f] for f in actual):raise ValueError('saved scalar oracle mismatch')
            for f in ('CEGR','BestGroupCov','CompleteRR'):totals[m,k,f]=totals.get((m,k,f),0)+actual[f]
            prefixes+=1
    checked=0
    for m in METHODS:
        for k in KS:
            cell=saved['summary'][m][str(k)]
            if cell['N']!=expected_count or cell['successes']!=totals[m,k,'CEGR']:raise ValueError('saved denominator')
            for f,label in [('CEGR','CEGR'),('BestGroupCov','BestGroupCov'),('CompleteRR','CompleteMRR')]:
                if not math.isclose(cell[label],totals[m,k,f]/expected_count,abs_tol=1e-12):raise ValueError('saved overall oracle')
                checked+=1
    expected=dict(prefixes_verified=prefixes,overall_metrics_verified=checked)
    if read(directory/'independent-oracle.json')!=expected:raise ValueError('saved oracle count')
    return expected


if __name__=='__main__':
    import argparse,json
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=('export','packets','combine','score','verify'))
    p.add_argument('--directory',type=Path,required=True);p.add_argument('--gold',type=Path,required=True);p.add_argument('--expected-count',type=int,required=True)
    p.add_argument('--selection',type=Path);p.add_argument('--mapping',type=Path);p.add_argument('--output',type=Path)
    p.add_argument('--runtime-config',type=Path)
    a=p.parse_args()
    if a.command=='export':
        if a.runtime_config is None or a.output is None:p.error('export requires --runtime-config and exclusive --output')
        result={'contract':str(export_queries(a.gold,a.runtime_config,a.output,a.expected_count))}
    elif a.command=='packets':result={'packets':len(packets(a.directory,a.gold,a.expected_count)['q_by'])}
    elif a.command=='combine':
        if a.selection is None or a.output is None:p.error('combine requires --selection and exclusive --output')
        result=combine(a.directory,a.gold,a.selection,a.output,a.expected_count)
    elif a.command=='score':
        if a.mapping is None:p.error('score requires --mapping')
        result=score_and_verify(a.directory,a.gold,a.mapping,a.expected_count)
    else:
        if a.mapping is None:p.error('verify requires --mapping')
        result=verify_saved(a.directory,a.gold,a.mapping,a.expected_count)
    print(json.dumps(result if a.command!='combine' else {'selected_intents':len(result['intents'])},sort_keys=True))
