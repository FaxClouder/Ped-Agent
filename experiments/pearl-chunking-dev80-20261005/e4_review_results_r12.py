"""Record the E4 r12 supplement-review judgments (model reviewer, human_verified=false).

Each judgment was made by reading the blind packet (query, requirement, scope, existing
alternatives, visible uncertain passages and every outside segment) and, where joint
support with other visible text was conceivable, the actual visible serialized context.
Three-valued rule identical to E2 r11. Segments judged ambiguous are left outside the
reviewed universe (excluded_outside_indices) so the requirement stays unknown.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from runtime import ROOT, sha, save_json

OUT=ROOT/'outputs/pearl-chunking-dev80-20261006-13'
REVIEWER='e4_supplement_r12_claude_opus_5_5'
RULE=('Three-valued: complete visible support -> new alternative; exhaustively read without support -> extend reviewed universe; ambiguous -> keep unknown '
      '(ambiguous segments stay outside the universe). Uncertain passages are adjudicated does_not_support only when a required element is missing from the passage '
      'and from all other visible text; plausible paraphrases stay unknown.')

NO='Every outside segment was read in full; none states this requirement within its scope. No complete minimal supporting alternative.'
J={
 'E4P001':dict(r='Outside segments are page numbers and the introduction of the scope paper (synchronization literature: Cao, Wang, Lu, Yanagisawa, Pimentel, Tan); no characteristic density value is stated.'),
 'E4P002':dict(r='Outside segments are the social-force model components, wall repulsion and relaxation parameters of the scope paper; no communication or positional-adjustment rule is stated.',
   unc=[dict(index=4,verdict='does_not_support',rationale='Visible portion states only that patterns are described by a model based on social communication; neither positional adjustment nor verbal exchange appears in the passage or anywhere in the visible seed10 raw text (checked: no "verbal", no "position"). Required element missing.')]),
 'E4P003':dict(r='Same model-component segments as E4P002; the counterfactual no-communication simulation (inverse V, near-isolated speed) is not stated.'),
 'E4P004':dict(r='Outside segments are the introduction of a flood-water bottleneck study; reinjection or sustained supply in Nicolas et al. is not mentioned.'),
 'E4P005':dict(r='Outside segments describe YOLOv7 depth localization and Trackpy tracking cross-validated against optical flow in the Pouw et al. stairway paper, not visual correction or overlapping-camera cross-checks of the Lyon TopView data.'),
 'E4P006':dict(r='Outside segments state YOLOv7 localization on hand-annotated depth images and Trackpy tracking, but sensor fusion is absent here and from all other visible text (checked: no "fusion", no "sensor"); the three-part requirement is not completely supported.'),
 'E4P007':dict(r='Outside segments are a general modelling motivation paragraph and an unrelated fundamental-diagram fragment; no non-spatial counting or corridor statement.'),
 'E4P008':dict(r='Outside segments are a heading fragment about herding factors and a bullet glyph; selective, purposeful perception under limited information is not stated.'),
 'E4P009':dict(r='Outside segments discuss stress/urgency experiments and herding (Haghani review) and a speed-conflict fragment; the V-like formation trade-off of Moussaid et al. is not stated.'),
 'E4P010':dict(r='Segments 0, 1, 3-6 (mesh resolution, figure captions, the AR/PW comparison of another paper) do not support the requirement and extend the universe. Segment 2 (Twarogowska et al., confirmed by the corresponding-author segment in E4P021) states that obstacles reduce clogging significantly and that the total evacuation time with columns becomes smaller, but also that outflow is slower in the initial phase; "increases outflow" is a plausible inference, not an explicit statement. Kept unknown.',
   exclude=[2],kept='Segment 2 states reduced clogging and shorter total evacuation time but explicitly slower initial outflow; whether it states increased outflow is ambiguous. Left outside the reviewed universe; requirement kept unknown.'),
 'E4P011':dict(r='Outside segments are back matter and a headway sentence of Shi et al. (stairs); the Xie et al. ramp uphill/downhill speed relation is not stated.'),
 'E4P012':dict(r='Outside segments are back matter and free/minimum headways for preschool students; the free-speed descent/ascent comparison and its preschool exception are not stated.'),
 'E4P013':dict(r='Outside segments are the literature review of the water-bottleneck paper and a citation fragment; the 0.062 m water-versus-land exit spacing is not stated.'),
 'E4P014':dict(r='Outside segments are the Haghani review paragraph on disability experiments (Sharifi, Geoerg 2019 wheelchair study) and unrelated intros; the spacing behaviour toward neighbours with disabilities is not stated.'),
 'E4P015':dict(r='Outside segments define Li et al.\'s motion activation time; Tavana et al.\'s start-up delay between consecutive pedestrians is not stated.'),
 'E4P016':dict(r='Outside segments are a Haghani review section on bidirectional collision avoidance and a "Conclusion" heading; retrograder count versus evacuation time is not stated.'),
 'E4P017':dict(r='The only outside segment is the heading "5. Conclusion".'),
 'E4P018':dict(r='Outside segments are Haghani review body text (groups, obstacles, stress, VR) and section headings; the share and popularity of laboratory experiments is not stated.'),
 'E4P019':dict(r='Same Haghani review segments as E4P018; the Lyon field dataset scales are not stated.'),
 'E4P020':dict(r='Outside segments are from Li et al.\'s attention-based model (later SFM extensions by Kwak and Zhou); Helbing and Molnar\'s attractive potentials are not stated.'),
 'E4P021':dict(r='Outside segments are Twarogowska author metadata, a macroscopic-model review paragraph and another paper\'s stability discussion; the Chraibi et al. intrinsic-instability statement is not present.'),
 'E4P022':dict(r='No outside segments. The visible uncertain passage groups Helbing and Molnar with force models driven by internal motivation without equating the social force with the motivation to act (same passage and prior verdict as E2 r11); the reviewed universe is itself unresolved.',
   kept='Uncertain passage 2 remains a plausible paraphrase; universe_status unknown. Kept unknown (unchanged from E2 r11).'),
 'E4P023':dict(r='The outside segment is another paper\'s literature review mentioning that Pouw et al. analysed the stairs-to-landing transition; the higher landing velocity is not stated.'),
 'E4P024':dict(r='Outside segments are from Shi et al. (age-mixed stairway capacity, speed and headway); the Geoerg et al. speed-reduction distance finding is not stated.'),
 'E4P025':dict(r='Outside segments are Shi et al. headway text, Pouw et al. abstract/metadata and a review paragraph; the Shi study design with its Meishan/Sichuan setting is not stated, and the location is absent from all visible text (checked: no "Meishan", "Sichuan" or "single-file").'),
}

def main():
    export=json.loads((OUT/'review-export-e4-r12.json').read_text('utf8'));results=[]
    assert {p['packet_id'] for p in export['packets']}==set(J)
    for p in export['packets']:
        pk=json.loads((OUT/'review-packets-e4-r12'/f"{p['packet_id']}.json").read_text('utf8'));assert pk['packet_sha256']==p['packet_sha256']
        j=J[p['packet_id']];texts=[s['text'] for s in pk['outside_segments']]+[s['text'] for u in pk['uncertain_visible'] for s in u['visible_portion']]
        unc=[]
        for a in j.get('unc',[]):
            u=next(x for x in pk['uncertain_visible'] if x['index']==a['index'])
            spans=[s['span'] for s in u['visible_portion']]
            unc.append(dict(index=a['index'],verdict=a['verdict'],rationale=a['rationale'],source_spans=spans,visible_text_sha256=hashlib.sha256(json.dumps([s['text'] for s in u['visible_portion']],ensure_ascii=False).encode()).hexdigest()))
        excl=j.get('exclude',[])
        results.append(dict(packet_id=p['packet_id'],packet_sha256=pk['packet_sha256'],intent_id=pk['intent_id'],requirement_id=pk['requirement_id'],reviewer_id=REVIEWER,human_verified=False,
            reviewed_text_sha256=hashlib.sha256(json.dumps(texts,ensure_ascii=False).encode()).hexdigest(),reviewed_text_definition='sha256 of JSON list: outside segment texts then visible uncertain texts',
            outside_segments_decision='ambiguous_partial_keep_outside' if excl else 'no_support_extend_universe',outside_rationale=j['r'] if not excl else j['r'],excluded_outside_indices=excl,
            create_visible_universe_review=False,new_alternatives=[],uncertain_adjudications=unc,kept_unknown=j.get('kept'),generic_rationale=NO))
    save_json(OUT/'review-results-e4-r12.json',dict(review='e4-supplement-r12',reviewer_id=REVIEWER,human_verified=False,rule=RULE,base_mapping_sha256=export['base_mapping_sha256'],
        export_sha256=sha(OUT/'review-export-e4-r12.json'),recorder_sha256=sha(__file__),results=results))
    print(len(results),'judgments;',sum(bool(r['kept_unknown']) for r in results),'kept unknown;',sum(len(r['uncertain_adjudications']) for r in results),'uncertain adjudications',flush=True)

if __name__=='__main__':main()
