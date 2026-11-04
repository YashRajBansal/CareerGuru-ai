import io
import json
import re
import pytest
from app import db, User, Professional, Conversation, ChatMessage, ReviewQuery, Career, Knowledge, Assessment, Resume, SavedCareer, AuditLog, limiter
from services import ai
from services.resume import extract

def token(client):
    return re.search(r'name="csrf-token" content="([^"]+)"', client.get('/login').get_data(as_text=True)).group(1)

def post(client, path, data=None, payload=None):
    csrf = token(client)
    return client.post(path, json=payload, headers={'X-CSRFToken': csrf}) if payload is not None else client.post(path, data={**(data or {}), 'csrf_token': csrf})

def login(client, username='student'):
    assert post(client, '/login', {'username':username, 'password':'test-password-123'}).status_code == 302

BOOKING = dict(name='Test Student', email='test@example.test', phone='1234567890', occupation='Diploma student', industry='Technology', company='', interest='Software', challenges='Choosing a path', outcome='A study plan', availability='Saturday 5 PM IST', comments='')

def test_signup_and_hashing(client):
    assert post(client,'/signup',dict(username='new',email='new@example.test',password='a-unique-password')).status_code == 302
    row = User.query.filter_by(username='new').one()
    assert row.password.startswith('$2') and not row.is_admin
    assert client.get('/home').status_code == 200
    assert post(client,'/logout').status_code == 302
    assert client.get('/home').status_code == 302
    post(client,'/signup',dict(username='NEW',email='different@example.test',password='a-unique-password'))
    assert User.query.count() == 4

def test_csrf(client):
    assert client.post('/login',data={'username':'student'}).status_code == 400
    login(client)
    for path, data in [('/api/careers/1/save',{}),('/api/quiz',{'answers':[5]*12})]:
        assert client.post(path,json=data).status_code == 400
    assert client.post('/professional',data=BOOKING).status_code == 400

def test_protected_legacy_and_admin_routes(client):
    paths=['/admin','/adlanding','/userdisplay','/calldisplay','/mail?id=1','/admin/careers','/admin/knowledge','/admin/queue','/admin/audit','/api/admin/analytics']
    for path in paths:
        assert client.get(path).status_code == 302, path
    login(client)
    for path in paths:
        assert client.get(path).status_code == 403, path
    assert post(client,'/admin/careers',{'title':'unauthorized'}).status_code == 403
    assert client.get('/delete/1').status_code == 405
    assert client.get('/deleteu/1').status_code == 405

@pytest.mark.parametrize('path',['/','/home','/careers','/careers/1','/quiz','/recommendations','/counselor','/chatbot1','/chatbot2','/interview','/resume','/professional','/profile','/logout'])
def test_student_pages(client,path):
    login(client)
    response=client.get(path)
    assert response.status_code == 200, path
    assert b'guru.css' in response.data

def test_admin_pages_analytics(client):
    login(client,'staff')
    for path in ['/admin','/adlanding','/admin/careers','/admin/knowledge','/admin/users','/admin/bookings','/admin/queue','/admin/audit']:
        assert client.get(path).status_code == 200, path
    data=client.get('/api/admin/analytics').json
    assert len(data['labels']) == len(data['signups']) == 14
    assert sum(data['signups']) == 3

def test_matching_and_saved_paths(client):
    ranked, mode=ai.rank('Python SQL algorithms software testing',Career.query.all())
    assert ranked[0][0]>0 and any(c.title=='Software Developer' for _,c in ranked)
    assert mode == 'Local text similarity'
    login(client)
    assert post(client,'/api/careers/1/save',payload={}).json['saved'] is True
    assert SavedCareer.query.count() == 1
    assert post(client,'/api/careers/1/save',payload={}).json['saved'] is False
    assert b'Software Developer' in post(client,'/recommendations',{'interests':'Python SQL software'}).data

def test_quiz(client):
    login(client)
    for answers in [[True]*12,[3]*11,[6]*12]:
        assert post(client,'/api/quiz',payload={'answers':answers}).status_code == 400
    response=post(client,'/api/quiz',payload={'answers':[5,4,3,2,1,5]*2})
    assert response.status_code == 200 and response.json['scores']['Realistic'] == 10
    assert Assessment.query.count() == 1
    assert client.get('/quiz').status_code == 200
    assert b'Your paths to explore' in client.get('/recommendations').data

def test_booking_and_ownership(client):
    login(client)
    assert post(client,'/professional',BOOKING).status_code == 302
    row=Professional.query.one()
    assert row.user_id == User.query.filter_by(username='student').one().id
    post(client,'/logout'); login(client,'other')
    assert post(client,f'/professional/{row.id}/cancel').status_code == 404
    post(client,'/logout'); login(client,'staff')
    assert client.get(f'/mail?id={row.id}').status_code == 200
    assert post(client,'/admin/bulk/bookings',{'ids':str(row.id),'action':'confirmed'}).status_code == 302
    assert row.status == 'confirmed' and AuditLog.query.count() == 1

def test_conversation_ownership_and_delete(client):
    conversation=Conversation(user_id=User.query.filter_by(username='student').one().id,title='Private')
    db.session.add(conversation); db.session.flush()
    db.session.add(ChatMessage(conversation_id=conversation.id,role='user',content='Private message')); db.session.commit()
    identifier=conversation.id
    login(client,'other')
    assert client.get(f'/api/conversations/{identifier}').status_code == 404
    assert post(client,f'/api/conversations/{identifier}/delete').status_code == 404
    post(client,'/logout'); login(client)
    assert client.get(f'/api/conversations/{identifier}').json['messages'][0]['content'] == 'Private message'
    assert post(client,f'/api/conversations/{identifier}/delete').status_code == 200
    assert ChatMessage.query.count() == 0

def test_missing_provider(client):
    login(client)
    response=post(client,'/api/chat',payload={'message':'What can I do after a diploma?'})
    assert response.status_code == 501 and response.json['future_feature'] is True
    assert ReviewQuery.query.count() == 0 and Conversation.query.count() == 0

def test_streaming_grounding_memory_feedback(client,monkeypatch):
    monkeypatch.setattr(ai,'GENERATION_LOCKED',False)
    monkeypatch.setenv('OLLAMA_MODEL','fixture-local-model')
    captured=[]
    def stream(messages):
        captured.append(messages)
        yield 'Explore **Software Developer**. '
        yield 'Try a Python project.'
    monkeypatch.setattr(ai,'stream',stream)
    login(client)
    response=post(client,'/api/chat',payload={'message':'Python software development'})
    events=[json.loads(line[6:]) for line in response.get_data(as_text=True).split('\n') if line.startswith('data: ')]
    identifier=events[0]['conversation_id']
    assert events[-1]['done'] and ChatMessage.query.count() == 2
    assert 'Retrieved reference' in captured[0][0]['content'] and 'Software Developer' in captured[0][0]['content']
    second = post(client,'/api/chat',payload={'message':'What next?','conversation_id':identifier})
    assert second.status_code == 200
    second.get_data()
    assert len(captured[1]) == 4
    assert post(client,'/api/chat/flag',payload={'conversation_id':identifier}).status_code == 200
    assert ReviewQuery.query.filter_by(reason='User requested review').count() == 1
    post(client,'/api/chat',payload={'kind':'interview','message':'Practice for Python developer'}).get_data()
    assert 'Communication /5' in captured[-1][0]['content']

def test_stream_failure(client,monkeypatch):
    monkeypatch.setattr(ai,'GENERATION_LOCKED',False)
    monkeypatch.setenv('OLLAMA_MODEL','fixture-local-model')
    def broken(messages):
        yield 'Partial'
        raise ai.AIUnavailable('Test interruption')
    monkeypatch.setattr(ai,'stream',broken)
    login(client)
    response=post(client,'/api/chat',payload={'message':'Python software'})
    assert 'Test interruption' in response.get_data(as_text=True)
    assert ChatMessage.query.filter_by(role='assistant').count() == 0
    assert ReviewQuery.query.filter_by(reason='Provider unavailable or interrupted').count() == 1

def test_resume_rubric_upload_privacy_delete(client):
    from werkzeug.datastructures import FileStorage
    for raw,name in [(b'fake pdf','resume.pdf'),(b'bad','resume.exe'),(b'short','resume.txt')]:
        with pytest.raises(ValueError): extract(FileStorage(stream=io.BytesIO(raw),filename=name))
    login(client)
    text='student@example.test. Education: Diploma. Skills: Python, SQL. Projects: Built and tested an application for 20 users. '*8
    response=post(client,'/resume',{'resume_text':text,'career_id':'1'})
    assert response.status_code == 302
    assert client.get(response.location).status_code == 200
    row=Resume.query.one()
    assert 0 <= row.result['score'] <= 100 and row.result['score_kind']=='career_fit'
    assert row.result['ai_used'] is False and 'resume_text' not in row.result
    assert post(client,f'/resume/{row.id}/delete').status_code == 302
    assert Resume.query.count() == 0
    assert post(client,'/resume',{'resume':(io.BytesIO(text.encode()),'resume.txt')}).status_code == 302
    assert Resume.query.count() == 1

def test_profile_validation(client):
    login(client)
    data=dict(username='student',email='student@example.test',first_name='Asha',last_name='',age='19',location='Pune',phone_number='',birthday='',interests='Python')
    assert post(client,'/update-profile',data).status_code == 302
    assert User.query.filter_by(username='student').one().first_name == 'Asha'
    data['email']='other@example.test'
    assert post(client,'/update-profile',data).status_code == 302
    assert User.query.filter_by(username='student').one().email == 'student@example.test'

def test_admin_crud_and_audit(client):
    login(client,'staff')
    career=Career.query.first(); data=career.public(); data.update(title='Edited Career',id=career.id)
    career.embedding=[1,2]; career.embedding_model='test'; db.session.commit()
    assert post(client,'/admin/careers',data).status_code == 302
    assert career.title == 'Edited Career' and career.embedding is None
    assert post(client,'/admin/knowledge',{'title':'Guide','content':'Verified editorial guidance.'}).status_code == 302
    assert Knowledge.query.filter_by(title='Guide').count() == 1
    response=client.get('/admin/users?export=csv')
    assert response.status_code == 200 and 'password' not in response.get_data(as_text=True)
    row=ReviewQuery(question='Question',reason='No reference'); db.session.add(row); db.session.commit()
    assert post(client,'/admin/queue',{'id':row.id,'resolution':'Updated guidance'}).status_code == 302
    assert row.resolved and AuditLog.query.count() >= 4

def test_reorder_and_admin_deletion_guard(client):
    login(client,'staff'); ids=[r.id for r in Career.query.all()]
    assert post(client,'/api/admin/careers/reorder',payload={'ids':ids[::-1]}).status_code == 200
    assert Career.query.order_by(Career.position).first().id == ids[-1]
    assert post(client,'/api/admin/careers/reorder',payload={'ids':[1,1]}).status_code == 400
    staff=User.query.filter_by(username='staff').one()
    assert post(client,'/admin/bulk/users',{'ids':str(staff.id),'action':'delete'}).status_code == 302
    assert User.query.count() == 3

def test_user_deletion_retains_booking(client):
    login(client); post(client,'/professional',BOOKING)
    student=User.query.filter_by(username='student').one(); identifier=student.id
    db.session.add(Resume(user_id=identifier,result={'score':20})); db.session.commit()
    post(client,'/logout'); login(client,'staff')
    assert post(client,'/admin/bulk/users',{'ids':str(identifier),'action':'delete'}).status_code == 302
    assert db.session.get(User,identifier) is None and Resume.query.count() == 0
    assert Professional.query.one().user_id is None

def test_rate_limit(client):
    limiter.enabled=True; limiter.reset()
    try:
        csrf=token(client)
        responses=[client.post('/login',data={'csrf_token':csrf,'username':'unknown','password':'wrong'}) for _ in range(11)]
        assert responses[-1].status_code == 429
    finally:
        limiter.reset(); limiter.enabled=False

def test_seed_preserves_admin_edits(client):
    from seed import seed
    assert 75 <= Career.query.count() <= 150
    first=Career.query.first(); first.title='Admin edit'; db.session.commit()
    assert seed() == 0 and Career.query.first().title == 'Admin edit'
    assert all(c.skills and c.education and c.description and c.outlook for c in Career.query.all())
