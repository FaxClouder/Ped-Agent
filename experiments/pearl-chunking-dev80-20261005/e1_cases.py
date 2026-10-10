"""Expose certificate gaps and measured budget transitions; no new semantic labels."""
import argparse
import json
from pathlib import Path
from assemble import subtract_spans
from runtime import sha,cache_identity,save_json,save_rows
from e1 import configurations
from e1_score import rows,write_csv
from e1_statistics import load_verified_scoring,require_verified_artifact
from support import visible_support

def certificate_gaps(mapping,visible,expected_support=None):
    support=visible_support(visible,mapping)
    if expected_support is not None and support!=expected_support:raise ValueError('saved support/source-visible support drift')
    result=[]
    for requirement in mapping['requirements']:
        if support[requirement['requirement_id']]!='unknown':continue
        alternatives=[]
        for index,bundle in enumerate(requirement['evidence_groups']):
            missing=subtract_spans(bundle['necessary_spans'],visible)
            alternatives.append(dict(bundle_index=index,source_certificate_status=bundle['status'],missing_spans=missing))
        result.append(dict(requirement_id=requirement['requirement_id'],description=requirement['description'],semantic_status='unknown',alternatives=alternatives))
    return result

def validate_detail_bindings(details,rankings,contexts):
    rank_hashes={i:cache_identity(r) for i,r in rankings.items()};context_hashes={i:cache_identity(r) for i,r in contexts.items()}
    for detail in details:
        if detail['kind']=='layer1_raw':
            actual=rankings.get(detail['intent_id'])
            if actual is None or detail.get('ranking_sha256')!=rank_hashes[detail['intent_id']]:raise ValueError('case detail/ranking binding drift')
        elif detail['kind']=='context':
            actual=contexts.get((detail['intent_id'],detail['budget']))
            if actual is None or detail.get('context_id')!=actual.get('context_id') or detail.get('context_sha256')!=context_hashes[detail['intent_id'],detail['budget']]:raise ValueError('case detail/context binding drift')
        else:raise ValueError('unknown score detail kind')
    return True

def run(output,verification_receipt):
    score_path=output/'scores-e1-r01.json';scores,map_records,_=load_verified_scoring(output,verification_receipt);verification=json.loads(Path(verification_receipt).read_text('utf8'))
    maps={r['intent_id']:r for r in map_records};unknown=[];transitions=[];comparison=[];direct_bindings={}
    summaries={(r['configuration_id'],r['cell']):r for r in scores['summaries']}
    costs_path=output/'costs-e1-r01.json';profiles_path=output/'chunk-profiles-e1-r01.json'
    costs={r['configuration_id']:r for r in json.loads(costs_path.read_text('utf8'))}
    profiles={r['configuration_id']:r for r in json.loads(profiles_path.read_text('utf8'))}
    for config in configurations():
        directory=output/('index-'+config);direct_bindings[config]={name:require_verified_artifact(output,verification,config,name) for name in ('score-details-e1-r01.jsonl','rankings.jsonl','contexts.jsonl')};details=rows(directory/'score-details-e1-r01.jsonl')
        ranking_rows=rows(directory/'rankings.jsonl');context_rows=rows(directory/'contexts.jsonl');rankings={r['intent_id']:r for r in ranking_rows};contexts={(r['intent_id'],r['budget']):r for r in context_rows}
        if len(rankings)!=len(ranking_rows) or len(contexts)!=len(context_rows):raise ValueError('duplicate case ranking/context identity')
        validate_detail_bindings(details,rankings,contexts)
        selected=[r for r in details if (r['kind']=='layer1_raw' and r['method']=='R4' and r['k']==10) or (r['kind']=='context' and r['stage']=='final')]
        detail_lookup={(r['intent_id'],r.get('budget'),r.get('stage')):r for r in details if r['kind']=='context'}
        for detail in selected:
            if detail['sufficient']!='unknown':continue
            if detail['kind']=='context':
                actual=contexts[detail['intent_id'],detail['budget']];visible=[s for u in actual['final']['units'] for s in u['spans']]
                identity=dict(context_id=actual['context_id'],context_sha256=detail['context_sha256'],serialized_context_sha256=actual['final']['text_sha256'])
            else:
                actual=rankings[detail['intent_id']];visible=[s for c in actual['results']['R4'][:10] for s in c['core_spans']+c['overlap_spans']]
                identity=dict(ranking_sha256=detail['ranking_sha256'])
            unknown.append(dict(configuration_id=config,intent_id=detail['intent_id'],query=maps[detail['intent_id']]['query'],cell=detail['cell'],failure=detail['failure'],visible_spans=visible,certificate_gaps=certificate_gaps(maps[detail['intent_id']],visible,detail['support']),mapping_sha256=scores['mapping_sha256'],interpretation='Incomplete conservative certificate is unknown, never proof of absent semantic support.',**identity))
        for (intent,budget),context in contexts.items():
            before=detail_lookup[intent,budget,'expanded'];after=detail_lookup[intent,budget,'final']
            transitions.append(dict(configuration_id=config,intent_id=intent,budget=budget,expanded_status=before['sufficient'],final_status=after['sufficient'],full_certificate_lost=before['sufficient']=='yes' and after['sufficient']!='yes',confirmed_semantic_loss=before['sufficient']=='yes' and after['sufficient']=='no',possibly_semantic_loss=before['sufficient']=='yes' and after['sufficient']=='unknown',expanded_tokens=context['expanded']['token_count'],final_tokens=context['final']['token_count'],context_id=context['context_id']))
        a=summaries[config,'fixed_budget_main/P0/4096/final'];b=summaries[config,'fixed_budget_main/P0/8192/final'];r=summaries[config,'layer1_raw/R4/10'];p=profiles[config];cost=costs[config]
        comparison.append(dict(configuration_id=config,n=80,children=p['children'],table_children=p['table_children'],token_max=p['token_max'],CGC4K_lower=a['complete_group_lower'],CGC4K_possible_upper=a['complete_group_upper'],CGC4K_unknown=a['unknown'],CGC8K_lower=b['complete_group_lower'],CGC8K_possible_upper=b['complete_group_upper'],CGC8K_unknown=b['unknown'],CEGR10_lower=r['complete_group_lower'],CEGR10_possible_upper=r['complete_group_upper'],CEGR10_unknown=r['unknown'],CompleteMRR10_lower=r['complete_mrr_lower'],CompleteMRR10_possible_upper=r['complete_mrr_upper'],mean_R4_seconds=cost['mean_r4_total_seconds'],build_seconds=cost['stages']['build']['wall_seconds'],context_seconds=cost['stages']['context']['wall_seconds']))
    save_rows(output/'unknown-evidence-e1-r01.jsonl',unknown);write_csv(output/'budget-transitions-e1-r01.csv',transitions);write_csv(output/'comparison-e1-r01.csv',comparison)
    save_json(output/'case-inventory-e1-r01.json',dict(status='completed',verification_receipt_sha256=sha(verification_receipt),score_file_sha256=sha(score_path),mapping_sha256=scores['mapping_sha256'],verified_direct_artifact_bindings=direct_bindings,auxiliary_input_sha256={costs_path.name:sha(costs_path),profiles_path.name:sha(profiles_path)},primary_unknown_records=len(unknown),budget_transition_records=len(transitions),comparison_rows=len(comparison),semantic_judgments_added=0,generation_calls=0))
    print('saved',len(unknown),'primary unknown evidence records;',len(transitions),'budget transitions')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--verification-receipt',type=Path,required=True);args=parser.parse_args();run(args.output.resolve(),args.verification_receipt.resolve())
