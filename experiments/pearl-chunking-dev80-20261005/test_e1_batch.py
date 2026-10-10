import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from e1_batch import truncate_batch
from assemble import unit,views_by_id,truncate_with_offsets,serialize

class Nonmonotonic:
    def count(self,text):return 100 if text.endswith('ab') else len(text)
    def offsets(self,text):return [(i,i+1) for i in range(len(text))]

def test_batch_preserves_unicode_and_nonmonotonic_maximal_prefix():
    v={'doc_id':'d','source_version':'v','elements':[{'element_id':'e','text':'ab😀tail'}]}
    views=views_by_id([v]);span=dict(doc_id='d',source_version='v',element_id='e',start=0,end=7)
    u=unit([span],views,'c',1);counter=Nonmonotonic()
    budget=len(serialize([unit([dict(span,end=3)],views,'c',1)]))
    old,trace=truncate_with_offsets(u,[],views,budget,counter)
    new,newtrace=truncate_batch(u,[],views,budget,counter)
    assert old==new and trace['retained_characters']==newtrace['retained_characters']==3
