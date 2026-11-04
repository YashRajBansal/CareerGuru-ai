import io
import json
import pytest
from app import db, Career, Resume, User
from services.resume_scoring import evaluate
from services.resume import extract
from test_application import login,post

DATA_RESUME = '''
Asha Test
asha@example.test
Education
Diploma in Computer Science, Sample College, 2025.
Technical Skills
SQL, Excel, statistics, Power BI
Projects
Retail sales analysis
- Wrote SQL queries joining 4 tables and processed 12000 orders to reduce report preparation time by 30%.
- Built Excel pivot tables and lookup formulas to reconcile 12000 sales records and validated the final revenue totals.
- Performed statistical regression on sales data and compared hypothesis tests across 3 customer datasets to assess seasonal demand.
- Created Power BI dashboards with sales charts for stakeholders and reduced weekly reporting time by 25%.
Experience
- Presented findings to the retail project team and documented how the data cleaning process handled missing order records.
'''
CIVIL_RESUME = '''
Arun Test
arun@example.test
Education
Bachelor of Civil Engineering, Sample Institute, 2025.
Skills
AutoCAD, building design, materials testing, construction
Projects
Residential building project
- Drafted AutoCAD floor plans and detailed drawings for 3 residential buildings with dimensions and section layouts.
- Performed structural analysis for building design and calculated loads on reinforced concrete beams for 2 building plans.
- Conducted concrete slump tests and measured compressive strength for 20 samples in a materials testing laboratory.
Experience
- Supervised construction foundation work and inspected reinforcement at 2 sites while documenting contractor quality checks.
'''

def career(title):
    return Career.query.filter_by(title=title).one()

def test_same_polished_tech_resume_is_not_high_scoring_for_civil():
    data=evaluate(DATA_RESUME,career=career('Data Analyst'))
    civil=evaluate(DATA_RESUME,career=career('Civil Engineer'))
    assert data['score']>=80
    assert civil['score']<=25
    assert data['score']-civil['score']>=50
    assert data['quality_score']==civil['quality_score']
    assert all(item['status']=='missing' for item in civil['skill_evidence'])

def test_civil_project_evidence_is_high_for_civil_and_low_for_data():
    civil=evaluate(CIVIL_RESUME,career=career('Civil Engineer'))
    data=evaluate(CIVIL_RESUME,career=career('Data Analyst'))
    assert civil['score']>=80 and data['score']<=35
    assert all(item['status']=='supported' for item in civil['skill_evidence'])
    assert civil['penalty_total']==0

def test_sql_in_skills_without_a_supporting_task_is_penalized():
    without=DATA_RESUME.replace('- Wrote SQL queries joining 4 tables and processed 12000 orders to reduce report preparation time by 30%.','- Prepared a written project overview for the team.')
    weak=evaluate(without,career=career('Data Analyst'))
    strong=evaluate(DATA_RESUME,career=career('Data Analyst'))
    sql=next(item for item in weak['skill_evidence'] if item['canonical']=='sql')
    assert sql['status']=='listed_only' and sql['evidence']==[]
    assert weak['penalty_total']>=4 and 'SQL' in weak['unsupported_skills']
    assert strong['score']-weak['score']>=10

def test_keyword_lists_and_generic_projects_cannot_fake_evidence():
    resume='''test@example.test
Education: Diploma in Computing.
Skills: SQL, Excel, statistics, Power BI.
Projects
Implemented SQL, Excel, statistics and Power BI in a very important project.
Used SQL. Used Excel. Used statistics. Used Power BI.
'''
    result=evaluate(resume,career=career('Data Analyst'))
    assert result['score']<=45
    assert all(item['status']!='supported' for item in result['skill_evidence'])
    assert result['penalty_total']>=16

def test_real_aliases_and_present_tense_task_descriptions_are_supported():
    resume='''test@example.test
Education: Diploma in computing.
Skills: PostgreSQL, Google Sheets, statistical analysis, Tableau.
Projects
Write PostgreSQL queries joining customer and order tables to build a sales report.
Build Google Sheets pivot tables with formulas to reconcile inventory records.
Perform statistical regression on customer survey data to compare purchase patterns.
Create Tableau dashboards with sales charts for the project stakeholders.
'''
    result=evaluate(resume,career=career('Data Analyst'))
    assert all(item['status']=='supported' for item in result['skill_evidence'])

def test_negation_plans_and_substrings_do_not_prove_sql():
    resume='''test@example.test
Skills
NoSQL, Excel
Summary
No experience with SQL. Plan to learn SQL and build SQL queries next year.
Projects
Built a NoSQL application to manage customer documents and inventory records.
'''
    result=evaluate(resume,skills='SQL')
    assert result['skill_evidence'][0]['status']=='missing'
    assert result['fit_score']<=25

def test_qualifications_and_project_titles_are_not_task_evidence():
    resume='''test@example.test
Education
Completed a course in SQL and database systems.
Skills
SQL
Projects
SQL database project
Certifications
SQL database certificate
'''
    result=evaluate(resume,skills='SQL')
    assert result['skill_evidence'][0]['status']=='listed_only'
    assert result['penalty_total']>=4

def test_repeated_text_does_not_raise_the_score():
    original=evaluate(DATA_RESUME,career=career('Data Analyst'))
    repeated=evaluate(DATA_RESUME*4,career=career('Data Analyst'))
    assert repeated['score']<=original['score']
    assert repeated['penalty_total']>=10

def test_repeating_keywords_in_a_skills_list_is_penalized():
    result=evaluate('test@example.test\nSkills\n'+('SQL '*30)+'\nProjects\nSQL Project',skills='SQL')
    assert any('keyword repetition' in item['reason'] for item in result['penalties'])
    assert result['score']<=45

def test_saved_report_contains_selected_excerpts_not_full_resume():
    result=evaluate(DATA_RESUME,career=career('Data Analyst'))
    serialized=json.dumps(result)
    assert DATA_RESUME.strip() not in serialized
    assert 'asha@example.test' not in serialized
    assert all('unit' not in item for check in result['skill_evidence'] for item in check['evidence'])
    assert any(item['evidence'] for item in result['skill_evidence'])

def test_role_scoring_is_used_by_the_actual_resume_route(client):
    login(client)
    scores=[]
    for title in ['Data Analyst','Civil Engineer']:
        response=post(client,'/resume',{'resume_text':DATA_RESUME,'career_id':str(career(title).id)})
        assert response.status_code==302
        page=client.get(response.location)
        assert page.status_code==200
        assert b'Presentation quality' in page.data and b'Target skills' in page.data
        row=Resume.query.order_by(Resume.id.desc()).first()
        assert row.result['career']==title and row.result['score_kind']=='career_fit'
        scores.append(row.result['score'])
    assert scores[0]>=80 and scores[1]<=25

def test_invalid_career_cannot_silently_become_a_general_review(client):
    login(client)
    response=post(client,'/resume',{'resume_text':DATA_RESUME,'career_id':'999999'})
    assert response.status_code==200 and b'no longer available' in response.data
    assert Resume.query.count()==0

def test_legacy_scores_are_labeled_and_not_rewritten(client):
    login(client)
    user=User.query.filter_by(username='student').one()
    old={'score':87,'career':'Civil Engineer','rubric':{},'report':''}
    row=Resume(user_id=user.id,filename='old.txt',result=old)
    db.session.add(row);db.session.commit()
    response=client.get(f'/resume?review={row.id}')
    assert response.status_code==200
    assert b'Legacy review' in response.data and b'not career fit' in response.data
    assert row.result==old

def test_general_review_is_explicitly_not_a_career_match():
    result=evaluate(DATA_RESUME)
    assert result['score_kind']=='resume_quality' and result['fit_score'] is None
    assert any('Select a target career' in item for item in result['suggestions'])

def test_half_points_round_up_in_the_displayed_score():
    result=evaluate(DATA_RESUME,career=career('Data Analyst'))
    assert result['base_score']==94.5 and result['penalty_total']==0
    assert result['score']==95

def test_docx_paragraphs_and_tables_do_not_merge_skill_names():
    from docx import Document
    from werkzeug.datastructures import FileStorage
    doc=Document();doc.add_paragraph('Education: Diploma. Skills: Python')
    table=doc.add_table(rows=1,cols=1)
    table.cell(0,0).text='SQL projects: Wrote SQL queries joining order tables and generated reports for the team.'
    stream=io.BytesIO();doc.save(stream);stream.seek(0)
    text=extract(FileStorage(stream=stream,filename='resume.docx'))
    assert 'Python\nSQL' in text
