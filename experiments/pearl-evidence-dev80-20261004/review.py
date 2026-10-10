"""Export text-bound blinded packets and validate actual semantic reviews."""
import argparse
import hashlib
import json
import random
from pathlib import Path

PROMPT = '''Independently read the FULL supplied serialized context. Do not access other files, PDF, old labels, answers, or methods. For each necessary requirement assign yes/no/unknown: yes requires the complete claim, conditions, units and source association to be supported in this exact text; no means this text does not provide the required evidence; unknown means an unresolved ambiguous support judgment. Combine fragments only when their anonymous source and experimental conditions permit it. Never copy labels across different texts. Preserve numerical table headers and units in your reasoning. For every yes cite exact verbatim substrings from this context and explain how they jointly support the full requirement. Explain absent conditions for no and ambiguity for unknown. Assign each provided unit relevant (contributes question-related evidence), irrelevant (unrelated content), mixed (contains both), or unknown. Units identify occurrence boundaries by character start/end in serialized_context; repeated text has separate occurrence labels. Mixed counts in both relevance and noise. Return one JSON object per packet: packet_id, packet_sha256, support mapping requirement_id to {label,rationale,quotes}, unit_labels mapping unit_id to label, full_read=true, reviewer_id, model_id (if not exposed say inherited Codex model, not exposed), prompt_sha256, elapsed_seconds (null if unmeasured). Do not infer support from titles alone. Missing or omitted evidence is no; genuinely undecidable support is unknown. These labels are semantic reference judgments, not system predictions.'''

def sha_text(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))

def build_packets(contexts, intents, include_steps=True, seed=20261004):
    intent_map={i['intent_id']:i for i in intents}
    packets={}
    bindings=[]
    all_sources={}
    for c in contexts:
        views=[c]+list(c.get('steps',{}).values())
        all_sources.setdefault(c['intent_id'],set()).update(u['source_id'] for v in views for u in v['units'])
    for c in contexts:
        intent=intent_map[c['intent_id']]
        if c.get('query')!=intent.get('query'):
            raise ValueError('context query differs from frozen Gold query: '+c['intent_id'])
        views=[('final',c)]
        if include_steps:
            views += list(c.get('steps',{}).items())
        for stage,view in views:
            original=view['serialized_context']
            if sha_text(original)!=view['text_sha256']:
                raise ValueError('serialized context hash mismatch')
            source_ids=sorted(all_sources[c['intent_id']])
            source_map={s:'S'+str(i+1) for i,s in enumerate(source_ids)}
            unit_map=[{'occurrence_index':i,'original_unit_id':u['unit_id'],'blind_unit_id':'U'+str(i+1)} for i,u in enumerate(view['units'])]
            reconstructed='\n\n'.join(f"[Source {u['source_id']} | {u['locator']}]\nTitle: {u['title']}\n{u['text']}" for u in view['units'])
            if reconstructed!=original:
                raise ValueError('saved text differs from frozen serialization')
            chunks=[f"[Source {source_map[u['source_id']]} | {u['locator']}]\nTitle: {u['title']}\n{u['text']}" for u in view['units']]
            blinded='\n\n'.join(chunks)
            units=[]
            offset=0
            for i,(u,chunk) in enumerate(zip(view['units'],chunks)):
                units.append({'unit_id':'U'+str(i+1),'source_id':source_map[u['source_id']],
                              'text_sha256':sha_text(u['text']),'character_start':offset,'character_end':offset+len(chunk)})
                offset+=len(chunk)+2
            requirements=[{k:r[k] for k in ('requirement_id','claim','scope') if k in r} for r in intent['requirements']]
            body={'query':intent['query'],'requirements':requirements,
                  'allowed_groups':[g['requirements'] for g in intent['evidence_groups']],
                  'serialized_context':blinded,'units':units}
            digest=sha_text(canonical(body))
            pid='packet-'+digest[:24]
            if pid not in packets:
                packets[pid]={'packet_id':pid,'packet_sha256':digest,**body}
            bindings.append({'context_id':c['context_id'],'intent_id':c['intent_id'],'stage':stage,
                             'packet_id':pid,'packet_sha256':digest,'original_text_sha256':view['text_sha256'],
                             'blinded_text_sha256':sha_text(blinded),'source_map':source_map,'unit_map':unit_map})
    values=list(packets.values())
    random.Random(seed).shuffle(values)
    return values,bindings

def validate_review(packet, review):
    if any(review.get(k)!=packet[k] for k in ('packet_id','packet_sha256')):
        raise ValueError('review input identity mismatch')
    required={r['requirement_id'] for r in packet['requirements']}
    if set(review.get('support',{}))!=required:
        raise ValueError('review must judge each requirement exactly once')
    for judgment in review['support'].values():
        if judgment.get('label') not in ('yes','no','unknown') or not judgment.get('rationale'):
            raise ValueError('invalid support judgment')
        quotes=judgment.get('quotes',[])
        if judgment['label']=='yes' and not quotes:
            raise ValueError('yes needs actual text quotes')
        if any(not quote or quote not in packet['serialized_context'] for quote in quotes):
            raise ValueError('quote absent from actual context')
    if set(review.get('unit_labels',{}))!={u['unit_id'] for u in packet['units']}:
        raise ValueError('unit labels missing or extra')
    if any(v not in ('relevant','irrelevant','mixed','unknown') for v in review['unit_labels'].values()):
        raise ValueError('invalid unit label')
    return True

def validate_provenance(review):
    if review.get('full_read') is not True:
        raise ValueError('actual full-context reading declaration required')
    if not review.get('reviewer_id') or not review.get('model_id'):
        raise ValueError('actual reviewer/model provenance required')
    if review.get('prompt_sha256')!=sha_text(PROMPT):
        raise ValueError('review prompt hash mismatch')
    if 'elapsed_seconds' not in review or (review['elapsed_seconds'] is not None and
            (not isinstance(review['elapsed_seconds'],(int,float)) or review['elapsed_seconds']<0)):
        raise ValueError('elapsed time must be measured nonnegative number or explicit null')
    return True

def file_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def validate_export_inputs(contexts_path, gold_path, input_manifest_path=None, assembly_manifest_path=None):
    """Bind the selected Gold and saved contexts to the assembly's frozen metadata."""
    contexts=Path(contexts_path).resolve()
    gold=Path(gold_path).resolve()
    inputs=Path(input_manifest_path).resolve() if input_manifest_path else contexts.parent/'input-manifest.json'
    assembly=Path(assembly_manifest_path).resolve() if assembly_manifest_path else contexts.parent/'assembly-manifest.json'
    input_record=json.loads(inputs.read_text(encoding='utf-8'))
    assembly_record=json.loads(assembly.read_text(encoding='utf-8'))
    input_digest=file_sha(inputs)
    outputs=assembly_record.get('output_sha256',{})
    if assembly_record.get('input_manifest_sha256')!=input_digest or outputs.get(inputs.name)!=input_digest:
        raise ValueError('assembly input manifest hash mismatch')
    if outputs.get(contexts.name)!=file_sha(contexts):
        raise ValueError('saved contexts differ from frozen assembly output')
    root=Path(__file__).resolve().parents[2]
    def resolve_recorded(path):
        recorded=Path(path)
        return recorded.resolve() if recorded.is_absolute() else (root/recorded).resolve()
    recorded_gold=input_record.get('gold_path')
    if not recorded_gold or resolve_recorded(recorded_gold)!=gold:
        raise ValueError('selected Gold path differs from frozen input manifest')
    gold_digest=file_sha(gold)
    if input_record.get('gold_sha256')!=gold_digest:
        raise ValueError('selected Gold SHA differs from frozen input manifest')
    matches=[digest for path,digest in input_record.get('input_sha256',{}).items() if resolve_recorded(path)==gold]
    if matches!=[gold_digest]:
        raise ValueError('Gold missing or inconsistent in frozen input SHA bindings')
    return {'input_manifest_path':str(inputs),'input_manifest_sha256':input_digest,
            'assembly_manifest_path':str(assembly),'assembly_manifest_sha256':file_sha(assembly)}

def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding='utf-8').splitlines() if line.strip()]

def write_jsonl(path, rows):
    with Path(path).open('x',encoding='utf-8') as out:
        for row in rows:
            out.write(json.dumps(row,ensure_ascii=False)+'\n')

def main():
    p=argparse.ArgumentParser()
    commands=p.add_subparsers(dest='command',required=True)
    export=commands.add_parser('export')
    for name in ('contexts','gold','output'):
        export.add_argument('--'+name,required=True)
    export.add_argument('--input-manifest')
    export.add_argument('--assembly-manifest')
    select=commands.add_parser('select')
    for name in ('packets','reviews','output','model-id','reviewer-id','input-path'):
        select.add_argument('--'+name,required=True)
    args=p.parse_args()
    out=Path(args.output)
    if args.command=='export':
        proof=validate_export_inputs(args.contexts,args.gold,args.input_manifest,args.assembly_manifest)
        gold=json.loads(Path(args.gold).read_text(encoding='utf-8'))
        packets,bindings=build_packets(read_jsonl(args.contexts),gold['intents'])
        out.mkdir(parents=True,exist_ok=False)
        write_jsonl(out/'packets.jsonl',packets)
        write_jsonl(out/'bindings.jsonl',bindings)
        (out/'review-prompt.txt').write_text(PROMPT,encoding='utf-8')
        manifest={'packet_n':len(packets),'binding_n':len(bindings),'prompt_sha256':sha_text(PROMPT),'seed':20261004,
                  'source_contexts_path':str(Path(args.contexts).resolve()),'source_contexts_sha256':file_sha(args.contexts),
                  'gold_path':str(Path(args.gold).resolve()),'gold_sha256':file_sha(args.gold),
                  'code_sha256':file_sha(__file__),**proof,
                  'artifacts':{name:file_sha(out/name) for name in ('packets.jsonl','bindings.jsonl','review-prompt.txt')}}
        (out/'export-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    else:
        out.mkdir(parents=True,exist_ok=False)
        packets={r['packet_id']:r for r in read_jsonl(args.packets)}
        reviews=read_jsonl(args.reviews)
        if len({r['packet_id'] for r in reviews})!=len(reviews):
            raise ValueError('duplicate reviews require explicit external adjudication')
        for review in reviews:
            validate_review(packets[review['packet_id']],review)
            validate_provenance(review)
        if set(packets)!={r['packet_id'] for r in reviews}:
            raise ValueError('missing packet reviews; explicit unknown judgments required')
        write_jsonl(out/'selected-reviews.jsonl',reviews)
        manifest={'model_id':args.model_id,'reviewer_id':args.reviewer_id,'review_input_path':args.input_path,
                  'review_input_sha256':file_sha(args.input_path),'source_reviews_sha256':file_sha(args.reviews),
                  'packets_sha256':file_sha(args.packets),'selected_reviews_sha256':file_sha(out/'selected-reviews.jsonl'),
                  'code_sha256':file_sha(__file__),
                  'prompt_sha256':sha_text(PROMPT),'human_verified':False,
                  'selected':[{'packet_id':r['packet_id'],'packet_sha256':r['packet_sha256'],'review_content_sha256':sha_text(canonical(r))} for r in reviews]}
        (out/'selected-review-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')

if __name__=='__main__':
    main()
