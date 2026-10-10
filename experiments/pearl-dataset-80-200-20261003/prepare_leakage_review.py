"""Prepare all-question semantics and similarity flags for an independent family review."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from dataset_audit import all_leakage_candidates, read_rows, sha

PILOT = ROOT / 'paper/pearl-framework/datasets/retrieval-pilot/pearl-retrieval-dev-pilot-8-adobe106-gold.json'

def prepare(config_path: Path, output: Path) -> None:
    if output.exists():
        raise FileExistsError(f'refusing to overwrite {output}')
    config = json.loads(config_path.read_text(encoding='utf-8'))
    parts = {role: read_rows(ROOT / item['candidates']) for role, item in config['parts'].items()}
    dev = read_rows(PILOT) + parts['dev']
    evaluation = parts['eval_a'] + parts['eval_b']
    summaries = []
    for split, rows in (('dev', dev), ('eval', evaluation)):
        for q in rows:
            summaries.append({key: q[key] for key in ('intent_id', 'family_id', 'main_stratum', 'query', 'reference_answer')} |
                             {'split': split, 'necessary_claims': [{'claim': req['claim'], 'scope': req['scope']} for req in q['requirements']],
                              'source_pages': sorted({(a['source_id'], a['page']) for a in q['atoms']})})
    result = {'created_at_utc': datetime.now(timezone.utc).isoformat(),
              'candidate_sha256': {role: sha(ROOT / config['parts'][role]['candidates']) for role in parts},
              'candidate_paths': {role: config['parts'][role]['candidates'] for role in parts},
              'pilot_gold_sha256': sha(PILOT), 'code_sha256': sha(Path(__file__)),
              'question_count': len(dev) + len(evaluation), 'questions': summaries,
              'flags': all_leakage_candidates(dev, evaluation),
              'review_instruction': 'Scan all questions, answers, necessary claims and study scope for within-set and cross-set semantic families, near-duplicates and number/source-only template substitutions. Adjudicate every flag; exact-family, exact-query and numeric-template collisions require repair before sealing.'}
    with output.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + '\n')
    print(json.dumps({'questions': result['question_count'], 'flags': len(result['flags']), 'output': str(output)}))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    prepare(args.config.resolve(), args.output.resolve())
