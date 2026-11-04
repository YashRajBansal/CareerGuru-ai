import pytest
from app import db, Career, User, Assessment
from seed import seed
from services.matching import split_interests, rank_careers, matching_interests, SUGGESTIONS
from test_application import login,post

@pytest.mark.parametrize('query,title',[
    ('cricket','Cricketer'),('Cricket','Cricketer'),('I enjoy playing cricket','Cricketer'),
    ('CAD, material testing','Civil Engineer'),('AutoCAD, materials testing','Civil Engineer'),
    ('building design','Civil Engineer'),('coding','Software Developer'),('cooking','Chef'),
])
def test_everyday_and_comma_separated_inputs_have_relevant_top_matches(query,title):
    results,_=rank_careers(query,Career.query.all())
    assert results and results[0][1].title==title

def test_each_interest_counts_and_unknowns_are_not_random_matches():
    assert split_interests(' Cricket, CAD; cricket\n material testing,  ')==['Cricket','CAD','material testing']
    results,_=rank_careers('cricket, CAD, material testing',Career.query.all())
    assert results[0][1].title=='Civil Engineer'
    assert any(c.title=='Cricketer' for _,c in results)
    assert rank_careers('zzzxxyy',Career.query.all())[0]==[]
    civil=Career.query.filter_by(title='Civil Engineer').one()
    assert matching_interests('CAD, material testing',civil)==['CAD','material testing']

def test_explicit_interests_take_precedence_over_a_past_quiz():
    careers=Career.query.all()
    assert rank_careers('cricket',careers,'Python SQL software programming computer')[0][0][1].title=='Cricketer'
    assert rank_careers('CAD, material testing',careers,'Realistic mechanical technician drawing measurement')[0][0][1].title=='Civil Engineer'

def test_results_are_before_the_editor_and_input_is_normalized(client):
    login(client)
    response=post(client,'/recommendations',{'interests':' CAD , material testing, cad '})
    html=response.get_data(as_text=True)
    assert response.status_code==200
    assert html.index('<h3>Civil Engineer</h3>') < html.index('id="interest-editor"')
    assert html.index('Top match') < html.index('<h3>Civil Engineer</h3>')
    assert User.query.filter_by(username='student').one().interests=='CAD, material testing'
    assert 'data-interest="cricket"' in html and 'cricket, drawing, computers' in html
    assert 'material testing' not in SUGGESTIONS

def test_old_quiz_does_not_override_cricket_in_the_actual_page(client):
    login(client)
    user=User.query.filter_by(username='student').one()
    db.session.add(Assessment(user_id=user.id,answers=[5]*12,scores={},profile='Python programming software testing'))
    db.session.commit()
    page=post(client,'/recommendations',{'interests':'cricket'}).get_data(as_text=True)
    assert '<h3>Cricketer</h3>' in page
    assert '<h3>Software Developer</h3>' not in page

def test_catalog_update_preserves_existing_edits_and_does_not_resurrect_deletes():
    career=Career.query.filter_by(title='Cricketer').one()
    db.session.delete(career)
    existing=Career.query.filter_by(title='Civil Engineering Technician').one()
    existing.description='An administrator edit'
    db.session.commit()
    assert seed()==0
    assert Career.query.filter_by(title='Cricketer').first() is None
    assert existing.description=='An administrator edit'
