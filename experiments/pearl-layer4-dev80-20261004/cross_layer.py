"""Read-only linkage; never substitutes old L2/L3 labels for new judgments."""
from collections import Counter

def diagnostics(rows,old,l2):
    strict={(r['intent_id'],r['arm']):r['strict'] for r in old['rows']}
    evidence={(r['intent_id'],r['arm']):r['l2_sufficient'] for r in l2['cells']}
    arms={};details=[];actual=0
    for arm in sorted({r['arm'] for r in rows}):
        answer=Counter();truth=Counter();joint=Counter();complete=Counter();unsupported=0
        for r in [r for r in rows if r['arm']==arm]:
            key=(r['intent_id'],arm);previous=evidence[key];correct=strict[key]
            if previous in ('yes','no','unknown'):answer[previous+'|'+r['answerability']]+=1;actual+=1
            all_supported=bool(r['claims']) and not r.get('extraction_unknown',False) and all(c['grounding']['label']=='supported' for c in r['claims'])
            support='fully_supported' if all_supported else 'no_claims' if not r['claims'] else 'not_fully_supported'
            joint['|'.join((r['answerability'],r['behavior'],correct,support))]+=1
            if r['answerability']=='complete':complete[correct]+=1
            unsupported+=int(r['unsupported_completion'])
            for c in r['claims']:truth[c['factuality']['label']+'|'+c['grounding']['label']]+=1
            details.append({'cell_id':r['cell_id'],'l2_sufficient':previous,'answerability':r['answerability'],'old_strict':correct,'behavior':r['behavior'],'unsupported_completion':r['unsupported_completion'],'support_of_asserted_claims':support})
        arms[arm]={'cell_N':sum(joint.values()),'l2_answerability':dict(answer),'claim_truth_grounding':dict(truth),'joint_answer_states':dict(joint),'complete_strict':dict(complete),'unsupported_completion_N':unsupported}
    return {'schema_version':'pearl-layer4-cross-layer-v1','l2_actual_cell_N':actual,'arms':arms,'rows':details,'interpretation':'Old Strict=no means task-level acceptance failed; it is not a claim-level false label. Claim truth-grounding cross-tab uses independent factuality only. L2/new answerability disagreement is diagnostic, not automatically an old label error or evidence of parameter knowledge.'}
