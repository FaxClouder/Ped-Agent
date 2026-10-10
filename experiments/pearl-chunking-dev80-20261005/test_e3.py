from e3 import transition, choose_recovery

def test_transition_retains_unknown():
    assert transition('no','yes') == 'confirmed_gain'
    assert transition('yes','no') == 'confirmed_loss'
    assert transition('yes','unknown') == 'possible_loss'
    assert transition('unknown','yes') == 'unresolved_to_yes'

def test_selection_refuses_unknown_that_can_change_order():
    rows=[dict(strategy='P0',yes=57,unknown=0,mean_seconds=1),
          dict(strategy='P1',yes=54,unknown=5,mean_seconds=2),
          dict(strategy='P2',yes=50,unknown=0,mean_seconds=3)]
    assert choose_recovery(rows)['status']=='pending_review'
    rows[1]['unknown']=0
    assert choose_recovery(rows)['selected']=='P0'

def test_leader_unknown_is_allowed_only_with_robust_bounds():
    from e3_analysis import robust_choice
    rows=[dict(strategy='P0',yes=50,unknown=1,mean_seconds=1),dict(strategy='P1',yes=60,unknown=3,mean_seconds=2),dict(strategy='P2',yes=55,unknown=4,mean_seconds=3)]
    assert robust_choice(rows)['selected']=='P1'
    rows[2]['unknown']=6
    assert robust_choice(rows)['status']=='pending_review'
    rows[2].update(yes=60,unknown=0,mean_seconds=3)
    assert robust_choice(rows)['selected']=='P1'
    rows[2].update(yes=59,unknown=1,mean_seconds=1)
    assert robust_choice(rows)['status']=='pending_review'
