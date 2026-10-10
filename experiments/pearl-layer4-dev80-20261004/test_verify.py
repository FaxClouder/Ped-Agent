import importlib.util,json
from pathlib import Path
import pytest

def module():
 s=importlib.util.spec_from_file_location('v4',Path(__file__).with_name('verify.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def test_quote_tampering():
 with pytest.raises(ValueError,match='quote'):module().check_span('Actual evidence',{'start':0,'end':6,'quote':'Forged'})
def test_label_tampering():
 with pytest.raises(ValueError,match='label'):module().recompute_claims([{'grounding':{'label':'correct'},'factuality':{'label':'true'}}],False)
def test_saved_score_tampering():
 with pytest.raises(ValueError,match='score'):module().assert_equal({'n':.5},{'n':.8},'score')
def test_independent_fixed_bounds():
 m=module(); claims=[{'grounding':{'label':x},'factuality':{'label':'unknown'}} for x in ['supported','supported','partial','unsupported','unknown']];r=m.recompute_claims(claims,False)
 assert r['faithfulness']==[.4,.6] and r['unsupported_rate']==[.4,.6]
 assert m.recompute_claims([],False)['faithfulness']==[None,None]
def test_forged_citation():
 m=module(); row={'claims':[{'claim_id':'c1','start':0,'end':4,'quote':'Fact','grounding':{'label':'unsupported','evidence':[]},'factuality':{'label':'unknown','source_evidence':[]}}],'citation_pairs':[{'claim_id':'c1','citation_start':5,'citation_end':9,'citation_quote':'[s2]','source_label':'[Source absent | p.9]','label':'supported','evidence':[]} ]};inp={'raw_answer':'Fact [s2]','context':'[Source s | p.1] Fact','source_map':[{'source_label':'[Source s | p.1]','start':0,'end':20}]}
 with pytest.raises(ValueError,match='citation identity'):m.validate_review(row,inp)
def test_invalid_abstain_unknown():
 with pytest.raises(ValueError,match='abstain'):module().recompute_reliability([{'answerability':'unknown','abstain':'yes'}])

def test_repeated_source_label_uses_matching_position():
 m=module();context='[Source s | p.1] Fact\n[Source s | p.1] Other'
 inp={'raw_answer':'Fact','context':context,'source_map':[{'source_label':'[Source s | p.1]','start':0,'end':21},{'source_label':'[Source s | p.1]','start':21,'end':len(context)}]}
 row={'claims':[{'claim_id':'c1','start':0,'end':4,'quote':'Fact','grounding':{'label':'supported','evidence':[{'start':17,'end':21,'quote':'Fact','source_label':'[Source s | p.1]'}]},'factuality':{'label':'unknown','source_evidence':[]}}],'citation_pairs':[]}
 assert m.validate_review(row,inp)

def test_pair_support_cannot_come_from_uncited_source():
 m=module();context='[Source s | p.1] Fact\n[Source t | p.2] Else'
 inp={'raw_answer':'Fact [Source t | p.2]','context':context,'source_map':[{'source_label':'[Source s | p.1]','start':0,'end':21},{'source_label':'[Source t | p.2]','start':21,'end':len(context)}]}
 row={'claims':[{'claim_id':'c1','start':0,'end':4,'quote':'Fact','grounding':{'label':'supported','evidence':[{'start':17,'end':21,'quote':'Fact','source_label':'[Source s | p.1]'}]},'factuality':{'label':'unknown','source_evidence':[]}}],'citation_pairs':[{'claim_id':'c1','citation_start':5,'citation_end':21,'citation_quote':'[Source t | p.2]','source_label':'[Source t | p.2]','label':'supported','evidence':[{'start':17,'end':21,'quote':'Fact','source_label':'[Source s | p.1]'}]}]}
 with pytest.raises(ValueError,match='citation support source'):m.validate_review(row,inp)

def test_valid_label_cannot_drift_from_selected_judgment():
 m=module();c={'claim_id':'c1','start':0,'end':4,'quote':'Fact','normalized_claim':'Fact','grounding':{'label':'supported','evidence':[]}}
 selected={'claims':[c],'citation_pairs':[]}
 row={'claims':[c|{'grounding':{'label':'unsupported','evidence':[]},'factuality':{'label':'unknown'}}],'citation_pairs':[]}
 with pytest.raises(ValueError,match='selected'):m.validate_selected_decision(row,'grounding',selected)

def test_exact_reuse_cannot_change_source_label(tmp_path):
 m=module();old_packet=tmp_path/'p.json';old_review=tmp_path/'r.json'
 packet={'blind_id':'old','claims':[{'claim_id':'c1','normalized_claim':'Fact'}]}
 decision={'claims':[{'claim_id':'c1','normalized_claim':'Fact','label':'true','source_evidence':[],'reason':'read'}]}
 old_packet.write_text(json.dumps(packet));old_review.write_text(json.dumps(decision))
 reuse={'original_packet_path':str(old_packet),'original_packet_sha256':m.sha_file(old_packet),'original_review_path':str(old_review),'original_review_sha256':m.sha_file(old_review),'exact_content_equal_except_blind_id':True}
 alias={'claims':[decision['claims'][0]|{'label':'unknown'}],'provenance':{'reuse':reuse}}
 with pytest.raises(ValueError,match='reuse'):m.validate_exact_reuse(alias,packet|{'blind_id':'new'},lambda p:None)

def test_atom_reuse_cannot_change_condition(tmp_path):
 m=module();p=tmp_path/'p.json';r=tmp_path/'r.json'
 claim={'claim_id':'old','quote':'Fact','normalized_claim':'Fact','conditions':['old condition']}
 p.write_text(json.dumps({'claims':[claim]}));r.write_text(json.dumps({'claims':[{'claim_id':'old','label':'true','source_evidence':[],'reason':'read'}]}))
 alias={'claim_id':'new','original_review_path':str(r),'original_review_sha256':m.sha_file(r),'original_packet_path':str(p),'original_packet_sha256':m.sha_file(p),'origin_claim_id':'old'}
 d={'claims':[{'claim_id':'new','label':'true','source_evidence':[],'reason':'read'}],'provenance':{'atom_reuse':[alias]}}
 with pytest.raises(ValueError,match='reuse'):m.validate_atom_reuse(d,{'claims':[claim|{'claim_id':'new','conditions':['changed']}]},lambda p:None)

def test_id_only_pair_matches_visible_source_pages():
 m=module();ctx='[Source pearl-src-aa | p.1]\nFact';pos=ctx.index('Fact');ev={'start':pos,'end':len(ctx),'quote':'Fact','source_label':'[Source pearl-src-aa | p.1]'}
 row={'claims':[{'claim_id':'c','start':0,'end':4,'quote':'Fact','grounding':{'label':'supported','evidence':[ev]},'factuality':{'label':'unknown'}}],'citation_pairs':[{'claim_id':'c','citation_start':5,'citation_end':26,'citation_quote':'[Source pearl-src-aa]','source_label':'[Source pearl-src-aa]','label':'supported','evidence':[ev]}]}
 answer='Fact [Source pearl-src-aa]';row['citation_pairs'][0]['citation_end']=len(answer)
 inp={'raw_answer':answer,'context':ctx,'source_map':[{'source_label':ev['source_label'],'source_id':'pearl-src-aa','page':'1','start':0,'end':len(ctx)}]}
 assert m.validate_review(row,inp)
 row['citation_pairs'][0]['source_label']='[Source pearl-src-bb]'
 with pytest.raises(ValueError,match='citation'):m.validate_review(row,inp)

def test_atom_reuse_rejects_new_condition_field(tmp_path):
 m=module();p=tmp_path/'p.json';r=tmp_path/'r.json';c={'claim_id':'old','quote':'Fact','normalized_claim':'Fact'}
 p.write_text(json.dumps({'claims':[c]}));r.write_text(json.dumps({'claims':[{'claim_id':'old','label':'true','source_evidence':[],'reason':'read'}]}))
 a={'claim_id':'new','origin_claim_id':'old','original_packet_path':str(p),'original_packet_sha256':m.sha_file(p),'original_review_path':str(r),'original_review_sha256':m.sha_file(r)}
 d={'claims':[{'claim_id':'new','label':'true','source_evidence':[],'reason':'read'}],'provenance':{'atom_reuse':[a]}}
 with pytest.raises(ValueError,match='reuse'):m.validate_atom_reuse(d,{'claims':[c|{'claim_id':'new','conditions':['added']}]},lambda p:None)
