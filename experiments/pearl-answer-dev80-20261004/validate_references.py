"""Structural reference/oracle validation; independent human/agent semantics are external."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

BUDGET=8192

def sha_text(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def sha_file(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()

def require(condition, message):
    if not condition: raise ValueError(message)

def validate_identity_set(actual, expected):
    actual=list(actual); expected=list(expected)
    require(len(actual)==len(set(actual)) and len(expected)==len(set(expected)) and set(actual)==set(expected),'missing, duplicate or unexpected reference identity')

def id_list(value, definitions, name):
    require(isinstance(value,list) and len(value)==len(set(value)),name+' IDs must be unique list')
    require(isinstance(definitions,dict) and set(value)<=set(definitions),name+' dangling definition')
    require(all(isinstance(k,str) and bool(k) for k in value),name+' malformed ID')
    for key in value: require(bool(definitions[key]),name+' empty definition')

def finite_number(value, name, nonnegative=False):
    require(isinstance(value,(float,int)) and not isinstance(value,bool) and math.isfinite(value),name+' must be finite number')
    if nonnegative: require(value>=0,name+' must be nonnegative')

def validate_candidate(candidate, packet, count_tokens):
    require(candidate.get('intent_id')==packet.get('intent_id'),'intent identity mismatch')
    require(candidate.get('stratum')==packet.get('stratum'),'stratum mismatch')
    require(isinstance(candidate.get('resolved'),bool),'resolved must be boolean')
    if not candidate['resolved']:
        require(bool(candidate.get('unresolved_reason') or candidate.get('reason')),'unresolved reference needs concrete reason')
    else:
        require(isinstance(candidate.get('reference_answer'),str) and bool(candidate['reference_answer'].strip()),'resolved reference answer missing')
    id_list(candidate.get('key_targets',[]),candidate.get('target_definitions',{}),'target')
    id_list(candidate.get('required_conditions',[]),candidate.get('condition_definitions',{}),'condition')
    if candidate['resolved']: require(bool(candidate.get('key_targets')),'resolved key targets missing')
    groups=candidate.get('allowed_claim_groups',[]); definitions=candidate.get('claim_definitions',{})
    require(isinstance(groups,list),'allowed groups malformed')
    for group in groups:
        require(bool(group),'empty allowed claim group')
        id_list(group,definitions,'claim')
    if candidate['resolved']: require(bool(groups),'resolved allowed groups missing')
    require(isinstance(candidate.get('integration_applicable'),bool),'integration applicability missing')
    if candidate['integration_applicable']: require(bool(candidate.get('integration_rule')),'applicable integration rule missing')
    numeric=candidate.get('numeric_targets',[])
    require(isinstance(numeric,list),'numeric targets malformed')
    ids=[]
    for target in numeric:
        require(isinstance(target,dict) and isinstance(target.get('id'),str) and bool(target['id']),'numeric ID missing')
        if 'allowed_values' in target:
            values=target['allowed_values']
            require(isinstance(values,list) and bool(values) and target.get('tolerance')==0,'exact numeric alternatives require nonempty list and zero tolerance')
            for value in values: finite_number(value,'allowed numeric value')
            require(len(values)==len(set(values)),'duplicate allowed numeric alternative')
        ids.append(target['id'])
        finite_number(target.get('value'),'numeric value')
        finite_number(target.get('tolerance'),'numeric tolerance',True)
        require(all(isinstance(target.get(k),str) and bool(target[k].strip()) for k in ['unit','dimension','tolerance_basis']),'numeric unit, dimension or tolerance basis missing')
    require(len(ids)==len(set(ids)),'duplicate numeric target ID')
    sources={}
    allowed={a['source_id'] for a in packet.get('atoms',[])}
    for source in packet['sources']:
        key=(source['source_id'],source['chunk_id'])
        require(key not in sources,'duplicate frozen chunk')
        require(source['source_id'] in allowed,'source outside allowed atoms')
        require(sha_text(source['text'])==source['text_sha256'],'frozen source text hash mismatch')
        sources[key]=source
    citations=candidate.get('citations',[])
    if candidate['resolved']: require(bool(citations),'resolved reference citations missing')
    for citation in citations:
        key=(citation.get('source_id'),citation.get('chunk_id'))
        require(key in sources,'citation source not allowed')
        source=sources[key]
        require(citation.get('text_sha256')==source['text_sha256'],'citation chunk text hash mismatch')
        quote=citation.get('quote')
        require(isinstance(quote,str) and bool(quote) and quote in source['text'],'citation quote is not exact source substring')
        if 'text_start_byte' in citation or 'text_end_byte' in citation:
            start,end=citation.get('text_start_byte'),citation.get('text_end_byte')
            require(type(start) is int and type(end) is int and 0<=start<end<=len(source['text'].encode('utf-8')),'citation byte interval invalid')
            require(source['text'].encode('utf-8')[start:end]==quote.encode('utf-8'),'citation byte interval mismatch')
    oracle=candidate.get('oracle')
    if not oracle:
        require(bool(candidate.get('oracle_unresolved_reason') or candidate.get('unresolved_reason') or candidate.get('reason')),'absent oracle needs unresolved reason')
        return {'intent_id':candidate['intent_id'],'reference_structurally_valid':True,'oracle_structurally_valid':False,'semantic_validation':False}
    require(oracle.get('budget')==BUDGET,'oracle budget must be 8192')
    segments=oracle.get('segments',[])
    require(bool(segments),'oracle segments empty')
    rendered=[]
    for segment in segments:
        key=(segment.get('source_id'),segment.get('chunk_id'))
        require(key in sources,'oracle source not allowed')
        source=sources[key]; raw=source['text'].encode('utf-8')
        start,end=segment.get('text_start_byte'),segment.get('text_end_byte')
        require(type(start) is int and type(end) is int and 0<=start<end<=len(raw),'oracle byte interval invalid')
        exact=segment.get('exact_text')
        require(isinstance(exact,str) and raw[start:end]==exact.encode('utf-8'),'oracle UTF8 bytes mismatch')
        if 'text_sha256' in segment: require(segment['text_sha256'] in {sha_text(exact),source['text_sha256']},'oracle segment text hash mismatch')
        rendered.append(f"[Source {source['source_id']} | {source['locator']}]\nTitle: {source['title']}\n{exact}")
    serialized='\n\n'.join(rendered)
    require(oracle.get('serialized_context')==serialized,'oracle serialized context mismatch')
    measured=count_tokens(serialized)
    require(type(measured) is int and measured>=0 and measured<=BUDGET,'oracle pinned-token budget exceeded')
    require(oracle.get('token_count')==measured,'oracle token count mismatch')
    return {'intent_id':candidate['intent_id'],'reference_structurally_valid':True,'oracle_structurally_valid':True,'oracle_context_sha256':sha_text(serialized),'oracle_tokens':measured,'semantic_validation':False}

def validate_review(review,candidate,candidate_sha):
    require(review.get('intent_id')==candidate['intent_id'] and review.get('candidate_sha256')==candidate_sha,'review candidate binding mismatch')
    provenance=review.get('provenance',{})
    require(review.get('actual_read') is True,'independent reviewer actual reading missing')
    require(provenance.get('role')=='reviewer' and provenance.get('fork_turns')=='none' and provenance.get('independent') is True,'independent reviewer provenance missing')
    original_author=candidate.get('provenance',{}).get('agent_id',candidate.get('provenance',{}).get('task'))
    numeric_author=candidate.get('review_revision_provenance',{}).get('agent_id')
    effective_author=candidate.get('semantic_revision',{}).get('reviewer',numeric_author or original_author)
    if numeric_author:
        require(candidate['review_revision_provenance'].get('source_actual_read') is True and bool(candidate['review_revision_provenance'].get('basis')),'numeric revision source reading/basis missing')
        require(bool(review.get('base_original_candidate_sha256')) and bool(review.get('original_review_sha256')),'numeric revision baseline bindings missing')
    require(bool(effective_author) and bool(provenance.get('agent_id')) and provenance['agent_id']!=effective_author,'latest reference author cannot be independent reviewer')
    require(review.get('reference_verdict') in {'yes','unresolved'},'reference rejected or unreviewed')
    require(review.get('oracle_verdict') in {'yes','no','unresolved'},'oracle verdict missing')
    require(bool(review.get('rationale')) and bool(review.get('citation_checks')),'review rationale and citation checks missing')
    if candidate.get('numeric_targets'): require(bool(review.get('numeric_review')),'numeric review missing')
    if candidate.get('integration_applicable'): require(bool(review.get('integration_review')),'integration review missing')
    if candidate.get('oracle'): require(review.get('actual_read_oracle') is True,'oracle actual reading missing')
    if review['reference_verdict']=='unresolved': require(bool(review.get('unresolved_reason') or review.get('rationale')),'unresolved reference reason missing')
    if review['oracle_verdict']!='yes': require(bool(review.get('oracle_reason')),'oracle no/unresolved needs reason')
    if review['oracle_verdict']=='yes': require(bool(candidate.get('oracle')),'eligible oracle missing')
    return {'resolved':candidate['resolved'] and review['reference_verdict']=='yes','oracle_eligible':candidate['resolved'] and review['reference_verdict']=='yes' and review['oracle_verdict']=='yes'}

def load_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def pinned_counter(root, manifest):
    sys.path.insert(0,str(root/'Knowledge-Base/src'))
    from ped_knowledge.tokenization import HuggingFaceTokenCounter
    entries=manifest['frozen_input_sha256']
    matches=[k for k in entries if k.replace('\\','/').endswith('bge-m3/tokenizer.json')]
    require(len(matches)==1,'pinned tokenizer binding missing')
    path=root/matches[0]
    require(sha_file(path)==entries[matches[0]],'pinned tokenizer hash mismatch')
    counter=HuggingFaceTokenCounter.from_local_path(path,expected_sha256=entries[matches[0]])
    return counter.count

def validate_all(root, output, freeze_output=None, candidate_dir=None, reviews_dir=None):
    root=Path(root).resolve(); output=Path(output).resolve()
    manifest=load_json(output/'input-manifest.json'); expected=manifest['intent_ids']
    require(len(expected)==80,'freeze requires exactly 80 expected intents')
    candidates=sorted(Path(candidate_dir or output/'evaluation/reference-candidates').glob('*.json'))
    validate_identity_set([load_json(p).get('intent_id') for p in candidates],expected)
    count=pinned_counter(root,manifest)
    # Compare packet source bytes with frozen original JSONL records, not just packet self hashes.
    verified_libraries={}
    frozen=manifest['frozen_input_sha256']
    rows=[]; checks=[]
    for path in candidates:
        candidate=load_json(path); ident=candidate['intent_id']
        packet_path=output/'evaluation/reference-build'/f'{ident}.json'
        require(sha_file(packet_path)==manifest['reference_packets_sha256'][packet_path.name],'reference build packet hash mismatch')
        packet=load_json(packet_path)
        for source in packet['sources']:
            library=source['source_library_path']; library_path=root/library
            expected_sha=next((v for k,v in frozen.items() if k.replace('\\','/')==library),None)
            require(expected_sha is not None and source['source_library_sha256']==expected_sha,'source library binding missing')
            if library not in verified_libraries:
                require(sha_file(library_path)==expected_sha,'frozen source library hash mismatch')
                verified_libraries[library]=True
            with library_path.open('rb') as f:
                start,end=source['jsonl_byte_start'],source['jsonl_byte_end']; f.seek(start); record=json.loads(f.read(end-start))
            require(all(record[k]==source[k] for k in ['source_id','chunk_id','text','text_sha256','source_sha256']),'packet differs from original source bytes')
        check=validate_candidate(candidate,packet,count)
        review_path=Path(reviews_dir or output/'evaluation/reference-reviews')/f'{ident}.json'
        require(review_path.is_file(),'independent semantic review missing: '+ident)
        candidate_sha=sha_file(path); review=load_json(review_path)
        revision=candidate.get('semantic_revision')
        if not revision and candidate.get('review_revision_provenance'):
            numeric_revision=candidate['review_revision_provenance']
            revision={'reason':numeric_revision.get('basis'),'reviewer':numeric_revision.get('agent_id'),'original_candidate_sha256':review.get('base_original_candidate_sha256'),'original_review_sha256':review.get('original_review_sha256')}
        revision_bindings=None
        if revision:
            require(bool(revision.get('reason')) and bool(revision.get('reviewer')),'semantic revision reason/author missing')
            original_path=Path(revision.get('original_candidate_path',output/'evaluation/reference-selected-candidates-r01'/f'{ident}.json'))
            baseline_review_path=Path(revision.get('original_review_path',output/'evaluation/reference-reviews'/f'{ident}.json'))
            original_sha=sha_file(original_path)
            require(original_sha==revision.get('original_candidate_sha256'),'semantic revision original candidate hash mismatch')
            baseline_review=load_json(baseline_review_path)
            if revision.get('original_review_sha256'): require(sha_file(baseline_review_path)==revision['original_review_sha256'],'semantic revision original review hash mismatch')
            validate_review(baseline_review,load_json(original_path),original_sha)
            revision_bindings={'original_candidate_path':str(original_path),'original_candidate_sha256':original_sha,'original_review_path':str(baseline_review_path),'original_review_sha256':sha_file(baseline_review_path),'latest_author':revision['reviewer']}
        selection=validate_review(review,candidate,candidate_sha)
        require(not selection['oracle_eligible'] or check['oracle_structurally_valid'],'eligible oracle lacks valid structure')
        selected=dict(candidate,**selection,selected_candidate_sha256=candidate_sha,selected_review_sha256=sha_file(review_path),reference_packet_sha256=sha_file(packet_path))
        if revision_bindings: selected['validated_revision_bindings']=revision_bindings
        rows.append(selected); checks.append(dict(check,**selection))
    result={'schema_version':'pearl-answer-reference-freeze-v1','structural_checks_complete':True,'semantic_verdicts_imported':True,'semantic_verdicts_generated_by_validator':False,'intent_n':80,'resolved_n':sum(r['resolved'] for r in rows),'oracle_eligible_n':sum(r['oracle_eligible'] for r in rows),'rows':rows,'checks':checks}
    if freeze_output:
        dest=Path(freeze_output); dest.parent.mkdir(parents=True,exist_ok=True)
        with dest.open('x',encoding='utf-8') as f: json.dump(result,f,ensure_ascii=False,indent=2)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--root',default='.'); p.add_argument('--output',default='outputs/pearl-answer-dev80-20261004-01'); p.add_argument('--freeze-output'); p.add_argument('--candidate-dir'); p.add_argument('--reviews-dir'); a=p.parse_args()
    r=validate_all(a.root,a.output,a.freeze_output,a.candidate_dir,a.reviews_dir); print(json.dumps({k:v for k,v in r.items() if k not in {'rows','checks'}}))
