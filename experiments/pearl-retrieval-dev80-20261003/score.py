"""Merge arbitrary blinded review batches and score frozen dev80 ranks, fail closed."""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from protocol import require_reviewed, score_prefix, validate_gold

ROOT = Path(__file__).resolve().parents[2]
GOLD = ROOT / 'outputs/pearl-retrieval-dev80-eval200-adobe106-20261003-01/pearl-retrieval-dev-80-adobe106-gold-20261003-r01.json'
METHODS = ('R1', 'R2', 'R3', 'R4')
KS = (1, 5, 10, 20)
IDENTITY_FIELDS = ('text', 'text_sha256', 'source_id', 'source_sha256', 'title', 'page_start', 'page_end', 'locator')


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def rows(path):
    return [json.loads(line) for line in Path(path).read_text(encoding='utf-8').splitlines() if line.strip()]


def write(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write('\n')


def verify_hash(path, expected):
    if sha(path) != expected:
        raise ValueError('hash mismatch: ' + str(path))


def unique(values, label):
    if not isinstance(values, list) or any(not isinstance(v, str) or not v for v in values):
        raise ValueError('invalid ' + label)
    if len(values) != len(set(values)):
        raise ValueError('duplicate ' + label)
    return set(values)


def validate_child(child, frozen=None):
    for field in ('chunk_id',) + IDENTITY_FIELDS:
        if field not in child:
            raise ValueError('missing child identity field: ' + field)
    if not isinstance(child['text'], str) or hashlib.sha256(child['text'].encode('utf-8')).hexdigest() != child['text_sha256']:
        raise ValueError('child text hash mismatch')
    if child.get('chunk_level', 'child') != 'child':
        raise ValueError('parent not eligible')
    if frozen is not None:
        if child['chunk_id'] not in frozen:
            raise ValueError('unknown frozen child identity')
        actual = frozen[child['chunk_id']]
        if any(child[field] != actual[field] for field in IDENTITY_FIELDS):
            raise ValueError('frozen child identity mismatch: ' + child['chunk_id'])


def validate_decision(gold, packet, decision, packet_sha256):
    """Validate actual review identities and every sufficient path's literal evidence."""
    validate_gold(gold)
    semantic_fields = ('intent_id', 'query', 'reference_answer', 'requirements', 'atoms', 'evidence_groups')
    if {k:packet.get('intent',{}).get(k) for k in semantic_fields} != {k:gold.get(k) for k in semantic_fields}:
        raise ValueError('packet Gold identity mismatch')
    if decision.get('intent_id') != gold['intent_id']:
        raise ValueError('review intent identity mismatch')
    if decision.get('review_type') != 'subagent_blind_content' or not decision.get('reviewer_id'):
        raise ValueError('review type or reviewer identity missing')
    if decision.get('packet_sha256') != packet_sha256:
        raise ValueError('review packet hash mismatch')
    if any(key not in decision for key in ('rejection_summary', 'notes')):
        raise ValueError('review lacks rejection_summary/notes')
    candidates = packet['candidates']
    supplementary = packet.get('supplementary_candidates', [])
    pool = candidates + supplementary
    for child in pool:
        validate_child(child)
        if set(child) & {'method', 'rank', 'score', 'r1_rank', 'r2_rank', 'in_top100'}:
            raise ValueError('packet contains ranking context')
    required = unique([c['chunk_id'] for c in candidates], 'required IDs')
    pool_ids = unique([c['chunk_id'] for c in pool], 'packet IDs')
    by_id = {c['chunk_id']: c for c in pool}
    reviewed = unique(decision.get('reviewed_ids'), 'reviewed identity')
    unresolved = unique(decision.get('unresolved_ids'), 'unresolved identity')
    if not reviewed <= pool_ids or not unresolved <= pool_ids:
        raise ValueError('review uses unknown identity')
    if not required <= reviewed:
        raise ValueError('required candidates not fully reviewed')
    if unresolved & (required | reviewed):
        raise ValueError('unresolved core or reviewed identity')
    if reviewed | unresolved != pool_ids:
        raise ValueError('reviewed/unresolved partition does not cover packet')
    paths = decision.get('atom_paths', {})
    if set(paths) != {a['atom_id'] for a in gold['atoms']}:
        raise ValueError('atom path identity mismatch')
    expected = set()
    for atom, alternatives in paths.items():
        if not isinstance(alternatives, list):
            raise ValueError('invalid atom paths')
        for path in alternatives:
            ids = unique(path, 'path')
            if not ids or not ids <= reviewed:
                raise ValueError('empty, absent or unreviewed path')
            key = (atom, tuple(sorted(ids)))
            if key in expected:
                raise ValueError('duplicate atom path')
            expected.add(key)
    observed = set()
    for evidence in decision.get('path_evidence', []):
        atom = evidence.get('atom_id')
        ids = unique(evidence.get('chunk_ids'), 'path evidence IDs')
        key = (atom, tuple(sorted(ids)))
        if key not in expected or key in observed:
            raise ValueError('unmatched or duplicate path evidence')
        if not isinstance(evidence.get('reason'), str) or not evidence['reason'].strip():
            raise ValueError('empty path evidence reason')
        excerpt_ids = set()
        for excerpt in evidence.get('excerpts', []):
            cid, text = excerpt.get('chunk_id'), excerpt.get('text')
            if cid not in ids or not isinstance(text, str) or not text.strip() or text not in by_id[cid]['text']:
                raise ValueError('invalid literal path excerpt')
            if 'text_sha256' in excerpt and excerpt['text_sha256'] != by_id[cid]['text_sha256']:
                raise ValueError('excerpt child hash mismatch')
            excerpt_ids.add(cid)
        if excerpt_ids != ids:
            raise ValueError('path evidence lacks excerpt for every child')
        observed.add(key)
    if observed != expected:
        raise ValueError('accepted path lacks evidence')
    return copy.deepcopy(decision)


def validate_ranking(row, gold, children):
    if row.get('intent_id') != gold['intent_id'] or row.get('query') != gold['query'] or row.get('method') not in METHODS:
        raise ValueError('ranking identity mismatch')
    if row.get('status') != 'success':
        raise ValueError('execution failure or unrun method; quality score unavailable')
    if row.get('pass_number', 1) != 1:
        raise ValueError('scoring only permits first-pass rankings')
    results = row['results']
    if row.get('returned') != len(results) or len(results) > 100:
        raise ValueError('returned count mismatch')
    if [r['rank'] for r in results] != list(range(1, len(results) + 1)):
        raise ValueError('noncontiguous original ranks')
    if len(results) < 100 and not any(row.get(f) for f in ('return_reason', 'empty_result_reason', 'short_result_reason')):
        raise ValueError('short/empty result lacks valid completion reason')
    for child in results:
        validate_child(child, children)
    return [r['chunk_id'] for r in results]


def validate_gold_set(gold, expected_count):
    intents = gold['intents']
    ids = [q['intent_id'] for q in intents]
    if len(ids) != expected_count or len(set(ids)) != expected_count:
        raise ValueError('dev intent coverage mismatch')
    strata = Counter(q['main_stratum'] for q in intents)
    if expected_count == 80 and (len(strata) != 4 or sorted(strata.values()) != [20] * 4):
        raise ValueError('dev strata quota mismatch')
    for q in intents:
        validate_gold(q)
    return {q['intent_id']: q for q in intents}


def load_run(directory, gold_path, expected_count=80):
    directory, gold_path = Path(directory), Path(gold_path)
    preflight = read(directory / 'preflight.json')
    run = read(directory / 'run_manifest.json')
    gold = read(gold_path)
    q_by = validate_gold_set(gold, expected_count)
    verify_hash(gold_path, preflight['gold_sha256'])
    binding = run.get('input_binding', run)
    verify_hash(gold_path, binding['gold_sha256'])
    if 'preflight_sha256' in run:
        verify_hash(directory / 'preflight.json',run['preflight_sha256'])
    if run.get('status') not in ('retrieval_complete_support_review_pending', 'complete', 'retrieval_complete'):
        raise ValueError('execution matrix incomplete')
    if set(run['methods_executed']) != set(METHODS) or run.get('execution_failures'):
        raise ValueError('execution matrix incomplete or failed')
    for name, expected in run['output_sha256'].items():
        verify_hash(directory / name, expected)
    index = Path(preflight['index_dir'])
    if not index.is_absolute():
        index = ROOT / index
    child_path = index / 'child_chunks.jsonl'
    verify_hash(child_path, preflight['frozen_child_sha256'])
    verify_hash(index / 'build_manifest.json', preflight['index_build_manifest_sha256'])
    if gold['frozen_child_library_sha256'] != preflight['frozen_child_sha256']:
        raise ValueError('Gold frozen child binding mismatch')
    children_rows = rows(child_path)
    children = {c['chunk_id']: c for c in children_rows}
    if len(children) != len(children_rows):
        raise ValueError('duplicate frozen child ID')
    for c in children_rows:
        validate_child(c)
    ranks = rows(directory / 'rankings.jsonl')
    by_key = {}
    for row in ranks:
        key = (row['intent_id'], row['method'])
        if row['intent_id'] not in q_by or key in by_key:
            raise ValueError('unexpected/duplicate ranking matrix cell')
        validate_ranking(row, q_by[row['intent_id']], children)
        by_key[key] = row
    if set(by_key) != {(q, m) for q in q_by for m in METHODS}:
        raise ValueError('missing ranking matrix cell')
    for ident in q_by:
        a, b = by_key[ident, 'R3']['results'], by_key[ident, 'R4']['results']
        if Counter(r['chunk_id'] for r in a) != Counter(r['chunk_id'] for r in b):
            raise ValueError('R3/R4 candidate identity mismatch')
    return dict(directory=directory, gold_path=gold_path, gold=gold, q_by=q_by, run=run,
                preflight=preflight, children=children, ranks=by_key)


def review_files(decision_paths):
    """A decision file may contain one intent or an arbitrary nonempty intents batch."""
    combined = []
    hashes = {}
    for path in decision_paths:
        value = read(path)
        if 'intents' in value:
            items = value['intents']
            if not items:
                raise ValueError('empty review batch')
            for item in items:
                if item.get('review_type',value.get('review_type')) != value.get('review_type'):
                    raise ValueError('review batch/item type mismatch')
                combined.append({'review_type':value.get('review_type'), **item})
        else:
            combined.append(value)
        hashes[str(Path(path).resolve())] = sha(path)
    return combined, hashes


def combine(directory, output, gold_path=GOLD, decision_paths=None, expected_count=80):
    inputs = load_run(directory, gold_path, expected_count)
    directory = inputs['directory']
    decision_paths = list(decision_paths or sorted((directory / 'review/decisions').glob('*.json')))
    decisions, decision_hashes = review_files(decision_paths)
    by_id = {d['intent_id']: d for d in decisions}
    if len(decisions) != len(by_id) or set(by_id) != set(inputs['q_by']):
        raise ValueError('review intent coverage must exactly equal development Gold')
    packet_hashes = {}
    validated = []
    for ident, q in inputs['q_by'].items():
        packet_path = directory / 'review/packets' / (ident + '.json')
        packet = read(packet_path)
        digest = sha(packet_path)
        packet_hashes[packet_path.relative_to(directory).as_posix()] = digest
        for c in packet['candidates'] + packet.get('supplementary_candidates', []):
            validate_child(c, inputs['children'])
        decision = validate_decision(q, packet, by_id[ident], digest)
        for method in METHODS:
            ids = [r['chunk_id'] for r in inputs['ranks'][ident, method]['results']]
            require_reviewed(ids, decision['reviewed_ids'], 20)
        validated.append(decision)
    mapping = dict(status='agent_reviewed_preliminary_development_80',
        review_type='subagent_blind_content', run_id=inputs['run']['run_id'],
        created_at_utc=datetime.now(timezone.utc).isoformat(),
        gold_sha256=sha(gold_path), rankings_sha256=sha(directory/'rankings.jsonl'),
        run_manifest_sha256=sha(directory/'run_manifest.json'),
        preflight_sha256=sha(directory/'preflight.json'),
        frozen_child_sha256=inputs['preflight']['frozen_child_sha256'],
        packets_sha256=packet_hashes, review_sha256=decision_hashes,
        scoring_range=list(KS), intents=validated,
        interpretation='80 development intents; independent Agent child-content review, not human Gold or sealed evaluation.')
    write(output, mapping)
    return mapping


def load_validated_inputs(directory, mapping_path, gold_path=GOLD, expected_count=80):
    inputs = load_run(directory, gold_path, expected_count)
    directory = inputs['directory']
    mapping = read(mapping_path)
    for path, field in ((gold_path,'gold_sha256'), (directory/'rankings.jsonl','rankings_sha256'),
                        (directory/'run_manifest.json','run_manifest_sha256'), (directory/'preflight.json','preflight_sha256')):
        verify_hash(path, mapping[field])
    if mapping['run_id'] != inputs['run']['run_id'] or mapping['frozen_child_sha256'] != inputs['preflight']['frozen_child_sha256']:
        raise ValueError('mapping run or frozen child mismatch')
    if not mapping['review_sha256']:
        raise ValueError('selected review binding is empty')
    for path, digest in mapping['review_sha256'].items():
        verify_hash(path, digest)
    decisions = mapping['intents']
    by_id = {d['intent_id']:d for d in decisions}
    if len(by_id) != len(decisions) or set(by_id) != set(inputs['q_by']):
        raise ValueError('mapping intent coverage mismatch')
    originals, original_hashes = review_files(list(mapping['review_sha256']))
    selected = {d['intent_id']:d for d in originals}
    if len(selected)!=len(originals) or selected!=by_id or original_hashes!=mapping['review_sha256']:
        raise ValueError('mapping disagrees with selected review decisions')
    expected_packets = {'review/packets/' + ident + '.json' for ident in by_id}
    if set(mapping['packets_sha256']) != expected_packets:
        raise ValueError('mapping packet coverage mismatch')
    for ident, q in inputs['q_by'].items():
        path = directory/'review/packets'/ (ident+'.json')
        digest = mapping['packets_sha256'][path.relative_to(directory).as_posix()]
        verify_hash(path, digest)
        packet = read(path)
        for c in packet['candidates'] + packet.get('supplementary_candidates', []):
            validate_child(c, inputs['children'])
        validate_decision(q, packet, by_id[ident], digest)
        for method in METHODS:
            require_reviewed([r['chunk_id'] for r in inputs['ranks'][ident,method]['results']], by_id[ident]['reviewed_ids'],20)
    inputs.update(mapping=mapping, mapping_path=Path(mapping_path), decisions=by_id)
    return inputs


def build_details(inputs):
    details=[]
    for ident, q in inputs['q_by'].items():
        paths=inputs['decisions'][ident]['atom_paths']
        for method in METHODS:
            row=inputs['ranks'][ident,method]
            ids=[r['chunk_id'] for r in row['results']]
            scores={}
            for k in KS:
                result=score_prefix(q,paths,ids,k)
                seen=set(ids[:k])
                result['atoms_hit']={a['atom_id']:any(set(path)<=seen for path in paths[a['atom_id']]) for a in q['atoms']}
                result['missing_requirements_by_group']={g['group_id']:[r for r in g['requirements'] if not result['requirements_hit'][r]] for g in q['evidence_groups']}
                result['satisfied_paths']={a['atom_id']:[p for p in paths[a['atom_id']] if set(p)<=seen] for a in q['atoms']}
                sources={a['source_id'] for a in q['atoms']}
                result['AnySourceHit']=int(any(c['source_id'] in sources for c in row['results'][:k]))
                page_applicable=all(isinstance(a.get('page'),int) for a in q['atoms'])
                result['AnyPageHit']=(int(any(c['source_id']==a['source_id'] and c['page_start']<=a['page']<=c['page_end']
                                         for c in row['results'][:k] for a in q['atoms'])) if page_applicable else None)
                scores[str(k)]=result
            details.append(dict(intent_id=ident,method=method,main_stratum=q['main_stratum'],
                                status=row['status'],returned=row['returned'],scores=scores))
    return details


def aggregate(details, selected=None):
    subset=[d for d in details if selected is None or d['intent_id'] in selected]
    result={}
    for method in METHODS:
        cells=[r for r in subset if r['method']==method]
        result[method]={str(k):dict(N=len(cells),successes=sum(r['scores'][str(k)]['CEGR'] for r in cells),
            **{label:sum(r['scores'][str(k)][field] for r in cells)/len(cells)
               for label,field in [('CEGR','CEGR'),('BestGroupCov','BestGroupCov'),('CompleteMRR','CompleteRR')]}) for k in KS}
    return result


def score(directory, mapping_path, output=None, gold_path=GOLD, expected_count=80, csv_output=None):
    inputs=load_validated_inputs(directory,mapping_path,gold_path,expected_count)
    details=build_details(inputs)
    result=dict(status='agent_reviewed_preliminary_80_intent_development_comparison',
                run_id=inputs['run']['run_id'], intent_count=len(inputs['q_by']), methods=list(METHODS),k=list(KS),
                gold_sha256=sha(gold_path),mapping_sha256=sha(mapping_path),rankings_sha256=sha(Path(directory)/'rankings.jsonl'),
                summary=aggregate(details),
                strata={h:aggregate(details,{q['intent_id'] for q in inputs['gold']['intents'] if q['main_stratum']==h})
                        for h in sorted({q['main_stratum'] for q in inputs['gold']['intents']})},
                details=details,scoring_code_sha256={p.name:sha(p) for p in (Path(__file__),Path(__file__).with_name('protocol.py'),
                   ROOT/'experiments/pearl-index-106-adobe-20260929/score_pilot.py')},
                interpretation='80 development intents only; Agent-reviewed actual child support. Not the 200 sealed evaluation or human Gold.')
    output=Path(output or Path(directory)/'score-details.json')
    write(output,result)
    if csv_output is not None:
        flat=[]
        for d in details:
            row={key:d[key] for key in ('intent_id','method','main_stratum','status','returned')}
            for k in KS:
                for field in ('CEGR','BestGroupCov','CompleteRR','first_complete_rank'):
                    row[field+'@'+str(k)]=d['scores'][str(k)][field]
            flat.append(row)
        with Path(csv_output).open('x',encoding='utf-8',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(flat[0]));writer.writeheader();writer.writerows(flat)
    return result


def recompute(directory,mapping_path,reference,output,gold_path=GOLD):
    """Fresh load of original ranks+map; never inherit scores from the reference."""
    # Compute first without output, then compare immutable scientific result fields.
    result=score(directory,mapping_path,output,gold_path)
    old=read(reference)
    keys=('gold_sha256','mapping_sha256','rankings_sha256','summary','strata','details')
    if any(result[k]!=old[k] for k in keys):
        raise ValueError('independent recomputation disagrees; new output retained')
    return dict(status='passed',comparison_fields=list(keys),reference_sha256=sha(reference),recomputed_sha256=sha(output))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('combine','score','recompute'))
    parser.add_argument('--directory',type=Path,required=True)
    parser.add_argument('--gold',type=Path,default=GOLD)
    parser.add_argument('--mapping',type=Path)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--decisions',type=Path,nargs='+')
    parser.add_argument('--reference',type=Path)
    parser.add_argument('--csv-output',type=Path)
    args=parser.parse_args()
    if args.command=='combine':
        destination=args.output or args.directory/('pearl-retrieval-dev-80-adobe106-support-map-'+args.directory.name+'.json')
        combine(args.directory,destination,args.gold,args.decisions)
    elif args.command=='score':
        if args.mapping is None:parser.error('--mapping required')
        score(args.directory,args.mapping,args.output,args.gold,csv_output=args.csv_output or args.directory/'scores.csv')
    else:
        if args.mapping is None or args.reference is None or args.output is None:
            parser.error('recompute requires --mapping --reference --output (new file)')
        print(json.dumps(recompute(args.directory,args.mapping,args.reference,args.output,args.gold)))
