from pathlib import Path
from app import db, Career, Knowledge, CatalogRevision

def interest_catalog_update(rows):
    revision = 'everyday-interests-v1'
    if db.session.get(CatalogRevision,revision):
        return 0
    additions = {'Cricketer','Civil Engineer'}
    count = 0
    for line in rows:
        if not line or line.startswith('#'):
            continue
        title,cluster,skills,traits,education,description = line.split('|')
        if title in additions and not Career.query.filter_by(title=title).first():
            db.session.add(Career(title=title,cluster=cluster,skills=skills,traits=traits,education=education,description=description,outlook='Opportunities depend on region, training, experience and selection requirements. Research current local pathways before making a decision.',position=Career.query.count()+count))
            count += 1
    db.session.add(CatalogRevision(name=revision))
    db.session.commit()
    return count

def seed():
    rows = Path(__file__).with_name('data').joinpath('careers.txt').read_text(encoding='utf-8-sig').splitlines()
    if Career.query.first():
        return interest_catalog_update(rows)
    count = 0
    for line in rows:
        if not line or line.startswith('#'):
            continue
        title, cluster, skills, traits, education, description = line.split('|')
        db.session.add(Career(title=title, cluster=cluster, skills=skills, traits=traits, education=education, description=description, outlook='Opportunities depend on region, sector and experience. Check current local vacancies and qualification requirements before choosing a path.', position=count))
        count += 1
    if not Knowledge.query.first():
        db.session.add(Knowledge(title='Diploma pathways', content='A diploma can lead to entry-level work, apprenticeships or further study. Eligibility for lateral entry and professional registration varies by institution and location. Verify requirements with the institution.'))
        db.session.add(Knowledge(title='Exploring a career', content='Try a small project, speak to a practitioner, compare required skills and review current vacancies. Career Guru assessments are exploration aids, not psychological diagnoses or guarantees of employment.'))
    db.session.commit()
    interest_catalog_update(rows)
    return count
