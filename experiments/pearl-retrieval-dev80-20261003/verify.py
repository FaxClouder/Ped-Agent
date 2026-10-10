"""Independent boolean-formula recomputation and sealed-file byte-only verification."""
from pathlib import Path
import argparse
import hashlib
import json
import math
from collections import Counter
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[2]
KS=(1,5,10,20)
METHODS=('R1','R2','R3','R4')

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def rows(p):return [json.loads(x) for x in Path(p).read_text(encoding='utf8').splitlines() if x.strip()]

def verify_review_bindings(mapping):
    """Independently bind mapped judgments to the selected immutable review files."""
    bindings=mapping.get('review_sha256',{})
    if not bindings:raise ValueError('selected review binding empty')
    source=[]
    for path,digest in bindings.items():
        if sha(path)!=digest:raise ValueError('selected review file hash mismatch')
        value=read(path)
        if 'intents' in value:
            if not value['intents']:raise ValueError('selected review empty batch')
            source.extend({'review_type':value.get('review_type'),**d} for d in value['intents'])
        else:source.append(value)
    original={d['intent_id']:d for d in source}
    selected={d['intent_id']:d for d in mapping['intents']}
    if len(original)!=len(source) or len(selected)!=len(mapping['intents']) or original!=selected:
        raise ValueError('selected review content disagrees with mapping')
    return len(original)

def verify_repeated_outputs(directory,first):
    """Reopen every repeated ranking and saved query-vector artifact."""
    def signature(row):
        return (row['status'],row['query'],[(c['chunk_id'],c['score']) for c in row['results']])
    original={(r['intent_id'],r['method']):signature(r) for r in first}
    if len(original)!=len(first):raise ValueError('repeated ranking duplicate first cell')
    for n in (2,3):
        repeated=rows(directory/f'pass-{n}/rankings.jsonl')
        actual={(r['intent_id'],r['method']):signature(r) for r in repeated}
        if len(actual)!=len(repeated) or actual!=original:raise ValueError('repeated ranking mismatch')
        for artifact in ('query_vectors.npy','query_vector_ids.json'):
            if sha(directory/f'pass-{n}'/artifact)!=sha(directory/'pass-1'/artifact):
                raise ValueError('repeated query vector mismatch')
    return dict(ranking_ids_equal=True,ranking_scores_exact=True,query_vectors_bytes_exact=True,max_score_abs_delta=0)

def oracle(q,paths,ranking,k):
    """Evaluate all prefixes directly, without importing or invoking the scoring code."""
    reqs={r['requirement_id']:r['support_bundles'] for r in q['requirements']}
    groups=[g['requirements'] for g in q['evidence_groups']]
    if not reqs or not groups or any(not g for g in groups) or any(not bs or any(not b for b in bs) for bs in reqs.values()):
        raise ValueError('invalid empty Gold')
    seen=set();first=None;cov=0
    for pos,cid in enumerate(ranking[:k],1):
        seen.add(cid)
        supplied={a for a,ps in paths.items() if any(all(c in seen for c in p) for p in ps)}
        satisfied={r for r,bs in reqs.items() if any(all(a in supplied for a in b) for b in bs)}
        cov=max(sum(r in satisfied for r in g)/len(g) for g in groups)
        if cov==1 and first is None:first=pos
    return {'CEGR':int(first is not None),'BestGroupCov':cov,'CompleteRR':1/first if first else 0,
            'first_complete_rank':first}

def verify(directory,mapping_path,score_path,output):
    if output.exists():raise FileExistsError(output)
    run=read(directory/'run_manifest.json');pre=read(directory/'preflight.json')
    if run['status']!='retrieval_complete_support_review_pending' or run['completed_queries_by_pass']!={'1':80,'2':80,'3':80} or run['execution_failures']:
        raise ValueError('incomplete execution')
    for name,h in run['output_sha256'].items():
        if sha(directory/name)!=h:raise ValueError('runtime artifact '+name)
    gold_path=Path(pre['gold_path']);gold=read(gold_path);mapping=read(mapping_path);scores=read(score_path)
    bound_decisions=verify_review_bindings(mapping)
    if sha(gold_path)!=pre['gold_sha256'] or sha(gold_path)!=mapping['gold_sha256'] or sha(mapping_path)!=scores['mapping_sha256']:
        raise ValueError('frozen scoring binding')
    if sha(directory/'rankings.jsonl')!=mapping['rankings_sha256'] or sha(directory/'run_manifest.json')!=mapping['run_manifest_sha256']:
        raise ValueError('frozen runtime binding')
    qs={q['intent_id']:q for q in gold['intents']};decisions={q['intent_id']:q for q in mapping['intents']}
    ranks=rows(directory/'rankings.jsonl');details={(d['intent_id'],d['method']):d for d in scores['details']}
    keys={(q,m) for q in qs for m in METHODS}
    if len(qs)!=80 or set(decisions)!=set(qs) or len(ranks)!=320 or {(r['intent_id'],r['method']) for r in ranks}!=keys or set(details)!=keys:
        raise ValueError('matrix coverage')
    raw={};independent=[];prefixes=0
    for row in ranks:
        key=(row['intent_id'],row['method']);q=qs[key[0]];d=decisions[key[0]]
        if row['status']!='success' or row['query']!=q['query'] or row['returned']!=len(row['results']):raise ValueError('execution identity')
        if [c['rank'] for c in row['results']]!=list(range(1,row['returned']+1)):raise ValueError('original ranks')
        for c in row['results']:
            if hashlib.sha256(c['text'].encode('utf8')).hexdigest()!=c['text_sha256']:raise ValueError('raw child hash')
        ids=[c['chunk_id'] for c in row['results']]
        if not set(ids[:20])<=set(d['reviewed_ids']) or set(ids[:20])&set(d['unresolved_ids']):raise ValueError('unresolved scoring prefix')
        raw[key]=row
        out={}
        for k in KS:
            actual=oracle(q,d['atom_paths'],ids,k);expected=details[key]['scores'][str(k)]
            for field,value in actual.items():
                target=expected[field]
                if value is None or target is None:
                    if value!=target:raise ValueError('completion-rank recomputation')
                elif not math.isclose(value,target,rel_tol=0,abs_tol=1e-12):raise ValueError('independent metric '+str(key)+' '+str(k)+' '+field)
            out[str(k)]=actual;prefixes+=1
        independent.append({'intent_id':key[0],'method':key[1],'scores':out})
    for q in qs:
        a={c['chunk_id']:(c['text'],c['text_sha256']) for c in raw[q,'R3']['results']}
        b={c['chunk_id']:(c['text'],c['text_sha256']) for c in raw[q,'R4']['results']}
        if a!=b:raise ValueError('R3 R4 identity')
    for method in METHODS:
        for k in KS:
            for label,field in [('CEGR','CEGR'),('BestGroupCov','BestGroupCov'),('CompleteMRR','CompleteRR')]:
                mean=sum(x['scores'][str(k)][field] for x in independent if x['method']==method)/80
                if not math.isclose(mean,scores['summary'][method][str(k)][label],rel_tol=0,abs_tol=1e-12):raise ValueError('aggregate '+method+label)
    sealed=pre['sealed_files_sha256']
    for p,h in sealed.items():
        path=ROOT/p
        if sha(path)!=h or not path.stat().st_file_attributes&1:raise ValueError('sealed file changed '+p)
    vectors=[];pairs=[]
    for n in (1,2,3):
        vectors+=rows(directory/f'pass-{n}/query_inputs.jsonl')
        pairs+=rows(directory/('model-inputs-r4.jsonl' if n==1 else f'pass-{n}/model-input-identities-r4.jsonl'))
    if len(vectors)!=240 or len(pairs)!=24000 or any(x['truncated'] for x in vectors) or any(any(x[t] for t in ('query_truncated','child_truncated_initial','child_truncated_pair')) for x in pairs):
        raise ValueError('actual input audits')
    if not all(x['actual_forward_inputs_verified'] for x in vectors+pairs):raise ValueError('forward input mismatch')
    det=verify_repeated_outputs(directory,ranks)
    if det!=run['determinism']:raise ValueError('determinism manifest mismatch')
    if not all(det[k] for k in ('ranking_ids_equal','ranking_scores_exact','query_vectors_bytes_exact')) or det['max_score_abs_delta']!=0:raise ValueError('determinism')
    result={'status':'passed','created_at_utc':datetime.now(timezone.utc).isoformat(),'run_id':run['run_id'],
            'matrix_cells':320,'independent_formula_prefixes':prefixes,'independent_aggregates':48,
            'selected_review_content_bindings':bound_decisions,
            'oracle':'independent boolean formula; no scorer functions imported; raw frozen rankings and mapping only',
            'all_K_le20_adjudicated':True,'runtime_artifact_hashes':len(run['output_sha256']),
            'R3_R4_identity_intents':80,'query_inputs':240,'reranker_pairs':24000,'truncation_count':0,
            'determinism':det,'sealed_file_hash_and_readonly_checks':len(sealed),
            'evaluation_content_access':'byte hashing only; not parsed or used for development',
            'Gold_sha256':sha(gold_path),'mapping_sha256':sha(mapping_path),'scores_sha256':sha(score_path),
            'verification_code_sha256':sha(Path(__file__)),'quality':'80-intent development; independent Agent preliminary review; no human Gold'}
    with output.open('x',encoding='utf8',newline='\n') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps(result))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,required=True);p.add_argument('--mapping',type=Path,required=True)
    p.add_argument('--scores',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    verify(a.directory.resolve(),a.mapping.resolve(),a.scores.resolve(),a.output.resolve())
