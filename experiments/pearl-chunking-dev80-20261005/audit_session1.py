"""Read-only Session 1 asset/location audit. No models, indexing, or scoring.

Writes only a new output directory; Gold is used solely for offline location audit.
"""
import argparse
import collections
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / 'outputs/pearl-index-106-adobe-20260929-01'
R02 = ROOT / 'outputs/pearl-retrieval-dev80-gold-r02-20261003-01'

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()

def read(path):
    return json.loads(Path(path).read_text('utf-8'))

def rows(path):
    return [json.loads(s) for s in Path(path).read_text('utf-8').splitlines() if s.strip()]

def rel(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()

def write(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')

def run(output):
    output.mkdir(parents=True, exist_ok=False)
    assets = {}
    def record(path, expected=None, role='input'):
        path = Path(path)
        actual = sha(path) if path.is_file() else None
        row = dict(path=rel(path), sha256=actual, expected_sha256=expected,
                   exists=path.is_file(), matches_expected=None if expected is None else actual == expected,
                   role=role)
        assets[row['path']] = row
        return row
    build = read(INDEX/'build_manifest.json')
    sources, documents, registry = rows(INDEX/'sources.jsonl'), {}, []
    for s in sources:
        pdf = record(ROOT/s['source_path'], s['sha256'], 'corpus_pdf')
        doc = record(ROOT/s['document_path'], s['document_sha256'], 'canonical_adobe')
        d = read(ROOT/s['document_path'])
        documents[s['source_id']] = d
        derived = (ROOT/s['document_path']).parent
        raw = record(derived/'adobe/extract.zip', role='raw_adobe_response')
        extras = [record(p, role='derived_text_table') for p in sorted(derived.rglob('*'))
                  if p.is_file() and (p.suffix in {'.json','.jsonl','.html'}) and p.name != 'document.json']
        registry.append(dict(doc_id=s['source_id'], resource_id=d['resource_id'],
            source_version=d['version_id'], source_sha256=s['sha256'], title=s['catalog_version']['title'],
            pdf=pdf, canonical=doc, adobe_zip=raw, derived_assets=extras,
            parser_version=d['parser_version'], element_count=len(d['elements']),
            element_types=dict(collections.Counter(e['element_type'] for e in d['elements'])),
            coordinate_type='canonical_element_python_unicode_half_open; bbox retained at element level only',
            pdf_character_mapping_available=False))
    for name, expected in build['output_sha256'].items():
        record(INDEX/name, expected, 'historical_index')
    record(INDEX/'build_manifest.json', role='historical_build')
    for name, expected in build['dense']['actual_asset_sha256'].items():
        record(ROOT/'memPed/knowledge/models/bge-m3'/name, expected, 'dense_model')
    rerank_path = ROOT/'experiments/pearl-index-106-adobe-20260929/reranker-config.json'
    rerank = read(rerank_path)
    record(rerank_path, role='reranker_config')
    for name, expected in rerank['verified_files_sha256'].items():
        record(ROOT/rerank['local_model_dir']/name, expected, 'reranker_model')
    corpus_dir = ROOT/'paper/pearl-framework/datasets/retrieval-corpus'
    for name in ('corpus-manifest-v02.jsonl','adobe-membership-verification-v02.json'):
        record(corpus_dir/name, role='corpus_manifest')
    gold = read(R02/'gold-r02.json')
    revision = read(R02/'revision-manifest.json')
    record(R02/'gold-r02.json', revision['revised_gold_sha256'], 'development_gold')
    support_path = R02/'analysis-r02-01/support-map.json'
    support = read(support_path)
    record(support_path, role='legacy_support_map')
    query_path = ROOT/'outputs/pearl-retrieval-dev80-20261003-01/queries.jsonl'
    queries = rows(query_path)
    record(query_path, role='query_only_dev80')
    assert len(queries)==80 and {q['intent_id']:q['query'] for q in queries} == {i['intent_id']:i['query'] for i in gold['intents']}
    # Exact location only. A match does not establish support, completeness, or semantic transfer.
    atom_audit=[]
    for intent in gold['intents']:
        for a in intent['atoms']:
            d=documents.get(a['source_id']); anchor=a.get('anchor_text','')
            matches=[]
            if d and anchor:
                for e in d['elements']:
                    text=e['text']; start=0
                    while True:
                        at=text.find(anchor,start)
                        if at<0:break
                        matches.append(dict(element_id=e['element_id'],start=at,end=at+len(anchor),page=e['page_number'],element_type=e['element_type']))
                        start=at+1
            on_page=[m for m in matches if m['page']==a.get('page')]
            selected=on_page if on_page else matches
            status='deterministic_location_candidate' if len(selected)==1 else 'semantic_review_required' if d else 'source_unrecoverable'
            atom_audit.append(dict(intent_id=intent['intent_id'],atom_id=a['atom_id'],source_id=a['source_id'],
                declared_page=a.get('page'),anchor_sha256=hashlib.sha256(anchor.encode()).hexdigest(),
                matches=matches,selected_matches=selected,status=status,
                page_consistent=bool(on_page),support_transfer='not_adjudicated'))
    children,parents=rows(INDEX/'child_chunks.jsonl'),rows(INDEX/'parent_chunks.jsonl')
    byparent={p['chunk_id']:p for p in parents}
    child_audit=[]
    for c in children:
        p=byparent[c['parent_chunk_id']];d=documents[c['source_id']]
        byelement={e['element_id']:e for e in d['elements']}
        element_ids=json.loads(p['element_ids']) if isinstance(p['element_ids'],str) else p['element_ids']
        es=[byelement[eid] for eid in element_ids]
        heading=' > '.join(es[0]['heading_path'])
        body='\n\n'.join(e['text'].strip() for e in es if e['text'].strip())
        render=(heading+'\n\n'+body).strip() if heading else body
        st,en=c.get('character_start'),c.get('character_end')
        direct=st is not None and en is not None and p['text'][st:en]==c['text']
        child_audit.append(dict(chunk_id=c['chunk_id'],parent_reconstructed=render==p['text'],
            offset_present=st is not None and en is not None,offset_text_equal=direct,
            parent_contains_child=c['text'] in p['text'],parent_occurrence_count=p['text'].count(c['text'])))
    reference=ROOT/'outputs/pearl-answer-dev80-20261004-01/reference-freeze-r01.json'
    record(reference,role='independent_answer_reference')
    reference_rows=read(reference)['rows']
    assert {x['intent_id'] for x in reference_rows}=={i['intent_id'] for i in gold['intents']}
    for name in ('input-manifest.json','prompt-r01.json','generator-config-r01.json','reference-selection-r01.json','research-run-manifest-r01.json'):
        record(reference.parent/name,role='answer_frozen_configuration')
    # Preserve all historical experiment files by byte hashing, never deserialize eval200 questions.
    protected={}
    for directory in ('pearl-index-106-adobe-20260929-01','pearl-retrieval-dev80-20261003-01',
        'pearl-retrieval-dev80-gold-r02-20261003-01','pearl-evidence-dev80-20261004-01',
        'pearl-answer-dev80-20261004-01','pearl-layer4-dev80-20261004-01','pearl-retrieval-eval200-20261003-01'):
        for p in sorted((ROOT/'outputs'/directory).rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts and 'chroma' not in p.parts:
                protected[rel(p)]=sha(p)
    code={}
    for folder in ('Knowledge-Base/src','Contracts/src','Agent/src',
        'experiments/pearl-index-106-adobe-20260929','experiments/pearl-retrieval-dev80-20261003',
        'experiments/pearl-retrieval-eval-entry-20261003','experiments/pearl-evidence-dev80-20261004',
        'experiments/pearl-answer-dev80-20261004','experiments/pearl-layer4-dev80-20261004'):
        for p in sorted((ROOT/folder).rglob('*.py')):code[rel(p)]=sha(p)
    git=lambda *args: subprocess.check_output(['git',*args],cwd=ROOT,text=True,encoding='utf-8')
    baseline=dict(commit=git('rev-parse','HEAD').strip(),branch=git('branch','--show-current').strip(),
        git_status=git('status','--short'),code_sha256=code,
        dependencies={n:importlib.metadata.version(n) for n in ('numpy','torch','FlagEmbedding','transformers','tokenizers','PyYAML')})
    record(ROOT/'DUMMY_DO_NOT_USE',role='audit_sentinel') if False else None
    draft=Path('D:/GoogleDownload/PedRAGent_Chunking_Experiments_Agent_Plan_v1.0.md')
    baseline['user_draft']=dict(path=str(draft),exists=draft.is_file(),sha256=sha(draft) if draft.is_file() else None,
        expected_sha256='8e9bc10f981f0c485f96a45809c2aeda0dd7526fed7e5c7483a4cb6164244470')
    summary=dict(source_count=len(sources),child_count=len(children),parent_count=len(parents),
        query_count=len(queries),reference_count=len(reference_rows),
        strata=dict(collections.Counter(i['main_stratum'] for i in gold['intents'])),
        asset_count=len(assets),missing=[a for a in assets.values() if not a['exists']],
        hash_mismatches=[a for a in assets.values() if a['matches_expected'] is False],
        atoms=dict(collections.Counter(a['status'] for a in atom_audit)),atom_count=len(atom_audit),
        anchors_without_exact_match=sum(not a['matches'] for a in atom_audit),
        child_checks={k:sum(bool(a[k]) for a in child_audit) for k in ('parent_reconstructed','offset_present','offset_text_equal','parent_contains_child')},
        protected_file_count=len(protected),e0_status='audit_ready_smoke_pending',models_executed=False,
        support_map_new=None,semantic_transfer_complete=False)
    write(output/'asset-audit.json',dict(summary=summary,assets=assets,legacy_retrieval=read(ROOT/'outputs/pearl-retrieval-dev80-20261003-01/run_manifest.json')['method_config']))
    write(output/'source-registry-corpus.json',dict(schema_version='source-registry-audit-v1',sources=registry))
    write(output/'gold-location-audit.json',dict(note='Location candidates only; no new support labels.',atoms=atom_audit))
    write(output/'legacy-child-location-audit.json',child_audit)
    write(output/'workspace-baseline.json',baseline)
    write(output/'protected-assets-sha256.json',protected)
    print(json.dumps(summary,ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    run(p.parse_args().output.resolve())
