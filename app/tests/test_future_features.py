import pytest
from app import app, db, bcrypt, User, Professional, Conversation, ReviewQuery, Assessment, Resume
from services import ai
from test_application import login, post, BOOKING

def test_release_lock_blocks_even_configured_models(monkeypatch):
    monkeypatch.setenv('OLLAMA_MODEL','fixture-installed-model')
    monkeypatch.setattr(ai,'build_opener',lambda *args: pytest.fail('A locked feature must never open a model connection'))
    assert ai.GENERATION_LOCKED is True and ai.configured() is False
    with pytest.raises(ai.AIUnavailable,match='Future feature'):
        ai.complete('System','Question')
    with pytest.raises(ai.AIUnavailable,match='Future feature'):
        list(ai.stream([]))
    with pytest.raises(ai.AIUnavailable,match='Future feature'):
        ai._request([],False)

@pytest.mark.parametrize('path',['/counselor','/chatbot1','/chatbot2','/interview'])
def test_direct_ai_links_show_future_page(client,path):
    login(client)
    response=client.get(path)
    assert response.status_code==200
    assert b'future-page' in response.data and b'future feature' in response.data
    assert b'id="chat-form"' not in response.data

def test_locked_api_does_not_store_prompts_or_open_a_model(client,monkeypatch):
    login(client)
    monkeypatch.setenv('OLLAMA_MODEL','fixture-installed-model')
    monkeypatch.setattr(ai,'stream',lambda *args: pytest.fail('No generation expected'))
    response=post(client,'/api/chat',payload={'message':'Private question','kind':'interview'})
    assert response.status_code==501 and response.json['future_feature']
    assert Conversation.query.count()==ReviewQuery.query.count()==0

def test_working_tools_skip_model_calls_and_display_locked_controls(client,monkeypatch):
    login(client)
    monkeypatch.setenv('OLLAMA_MODEL','fixture-installed-model')
    monkeypatch.setattr(ai,'complete',lambda *args: pytest.fail('No generation expected'))
    assert post(client,'/api/quiz',payload={'answers':[4]*12}).status_code==200
    assert Assessment.query.one().interpretation==''
    assert post(client,'/recommendations',{'interests':'Python SQL testing'}).status_code==200
    text='test@example.test. Education: Diploma. Skills: Python. Projects: Built and tested an application. '*6
    assert post(client,'/resume',{'resume_text':text}).status_code==302
    assert Resume.query.one().result['ai_used'] is False
    assert post(client,'/professional',BOOKING).status_code==302
    assert Professional.query.one().summary is None
    for path in ['/quiz','/recommendations','/resume']:
        response=client.get(path)
        assert b'data-future-feature=' in response.data,path
        assert b'id="future-dialog"' in response.data

def test_admin_triage_is_locked_but_management_still_works(client,monkeypatch):
    login(client)
    post(client,'/professional',BOOKING)
    booking=Professional.query.one()
    post(client,'/logout');login(client,'staff')
    monkeypatch.setattr(ai,'complete',lambda *args: pytest.fail('No generation expected'))
    response=post(client,f'/admin/bookings/{booking.id}/summarize')
    assert response.status_code==302 and booking.summary is None
    page=client.get('/admin/bookings')
    assert b'Future feature:' in page.data and b'data-future-feature="AI consultation triage"' in page.data
    assert client.get('/admin').status_code==200

def test_admin_cli_and_canonical_signin(client):
    runner=app.test_cli_runner()
    result=runner.invoke(args=['create-admin','--username','newstaff','--email-address','newstaff@example.test','--password','test-only-admin-password'])
    assert result.exit_code==0,result.output
    row=User.query.filter_by(username='newstaff').one()
    assert row.is_admin and bcrypt.check_password_hash(row.password,'test-only-admin-password')
    response=post(client,'/login',{'username':'newstaff','password':'test-only-admin-password'})
    assert response.location=='/admin'
