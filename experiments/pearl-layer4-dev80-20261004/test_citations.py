from citations import textual_pairs,expand_evidence

def test_bullet_without_period_stays_in_its_line():
    answer='- A [Source pearl-src-aa | p.1]\n- B [Source pearl-src-bb | p.2]'
    claims=[{'claim_id':x,'start':answer.index(x),'end':answer.index(x)+1,'grounding':{'label':'unsupported','evidence':[]}} for x in ['A','B']]
    pairs=textual_pairs(answer,claims,'[Source pearl-src-aa | p.1]\nA\n[Source pearl-src-bb | p.2]\nB')
    assert [(p['claim_id'],p['citation_source_id']) for p in pairs]==[('A','pearl-src-aa'),('B','pearl-src-bb')]

def test_inline_and_source_specific():
    context='[Source pearl-src-aa | p.1]\nA is 1.\n\n[Source pearl-src-bb | p.2]\nB is 2.'
    answer='A is 1. B is 2. [Source pearl-src-aa | p.1; Source pearl-src-bb | p.2]'
    pos=context.index('B is 2.')
    claim={'claim_id':'b','start':8,'end':15,'occurrences':[{'start':8,'end':15}], 'grounding':{'label':'supported','evidence':[{'source_label':'[Source pearl-src-bb | p.2]','start':pos,'end':pos+7,'quote':'B is 2.'}]}}
    pairs=textual_pairs(answer,[claim],context)
    assert len(pairs)==2
    assert [p['label'] for p in pairs]==['unknown','supported']
    assert expand_evidence(claim['grounding']['evidence'][0],context)['quote'].endswith('B is 2.')

def test_missing_source_and_repeated_occurrence():
    a='A is 1. [Source pearl-src-ff | p.1]\n\nA is 1. [Source pearl-src-aa | p.2]'
    c={'claim_id':'a','start':0,'end':7,'occurrences':[{'start':0,'end':7},{'start':a.rindex('A is'), 'end':a.rindex('A is')+7}], 'grounding':{'label':'unsupported','evidence':[]}}
    p=textual_pairs(a,[c],'[Source pearl-src-aa | p.1]\nA.')
    assert [x['label'] for x in p]==['invalid','outside-context']

def test_citation_inside_sentence_before_fact():
    answer='According to X [Source pearl-src-aa | p.1], A is 1.'
    start=answer.index('A is 1');ctx='[Source pearl-src-aa | p.1]\nA is 1.';pos=ctx.index('A is')
    c={'claim_id':'a','start':start,'end':len(answer),'grounding':{'label':'supported','evidence':[{'source_label':'[Source pearl-src-aa | p.1]','start':pos,'end':len(ctx),'quote':ctx[pos:]}]}}
    assert textual_pairs(answer,[c],ctx)[0]['label']=='supported'

def test_standalone_paragraph_scope():
    answer='A is 1. B is 2.\n[Source pearl-src-aa | p.1]'
    claims=[{'claim_id':str(i),'start':s,'end':s+7,'grounding':{'label':'unsupported','evidence':[]}} for i,s in enumerate([0,8])]
    assert len(textual_pairs(answer,claims,'[Source pearl-src-aa | p.1]\nX'))==2

def test_id_only_citation_preserves_original_text():
    answer='Fact [Source pearl-src-aa]';ctx='[Source pearl-src-aa | p.1]\nFact';pos=ctx.index('Fact')
    c={'claim_id':'c','start':0,'end':4,'grounding':{'label':'supported','evidence':[{'start':pos,'end':pos+4,'quote':'Fact','source_label':'[Source pearl-src-aa | p.1]'}]}}
    pair=textual_pairs(answer,[c],ctx)[0]
    assert pair['citation_quote']=='[Source pearl-src-aa]' and pair['label']=='supported'
