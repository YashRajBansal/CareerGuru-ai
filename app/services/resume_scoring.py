"""Deterministic, career-specific resume scoring with task-level text evidence.

This checks the support contained in a resume, not whether a claim is true.
No model, external service, or employment-success prediction is involved.
"""
import re
import math
from collections import Counter

VERSION = 2
RULES = {
 'sql': (('SQL','MySQL','PostgreSQL','Postgres','SQLite','T-SQL','SQL Server','window functions','CTEs'), r'quer(?:y|ies|ied)|join|tables?|database|records?|dataset|etl|cte|window function|schema'),
 'spreadsheets': (('spreadsheets','spreadsheet','Excel','Google Sheets','pivot tables','VLOOKUP','XLOOKUP'), r'pivot|formulas?|workbooks?|spreadsheets?|lookups?|vlookup|xlookup|reports?|inventory|budget|reconcil|data|dashboard'),
 'statistics': (('statistics','statistical','regression','hypothesis testing','A/B testing','probability','t-test'), r'regression|hypothes|statistic|a/b|t-test|probability|correlation|confidence interval|experiment'),
 'visualization': (('visualization','visualisation','Power BI','PowerBI','Tableau','matplotlib','seaborn','data charts'), r'dashboard|charts?|visuali[sz]|reports?|plots?|stakeholders?|trends?|metrics'),
 'cad': (('CAD','AutoCAD','Civil 3D','SolidWorks','CATIA','Revit'), r'drawings?|draft|plans?|models?|parts?|assembl|layouts?|blueprints?|dimensions?|design|floor'),
 'building design': (('building design','structural design','floor plans','floorplans','building plans','structural analysis','reinforced concrete beams'), r'building|structur|floor|plans?|beams?|columns?|loads?|blueprints?|residential|design'),
 'materials testing': (('materials testing','material testing','concrete testing','slump test','slump tests','compressive strength','compression tests','soil testing','tensile testing','aggregate testing'), r'concrete|slump|compress|soil|tensile|aggregate|specimen|samples?|laboratory|test'),
 'construction': (('construction','site supervision','site work','sitework','foundation work','building site','BOQ','quantity surveying'), r'site|foundation|concrete|reinforcement|contractors?|quantit|inspection|building|construction|schedule'),
 'python': (('Python','pandas','NumPy','Flask','Django'), r'scripts?|apps?|application|api|data|automat|pipeline|model|tests?|server|database|web'),
 'algorithms': (('algorithms','algorithm','data structures','binary search','sorting algorithm','dynamic programming'), r'algorithm|search|sort|complexity|structures?|graph|performance|runtime'),
 'git': (('Git','GitHub','GitLab','version control'), r'branches?|commits?|pull requests?|merge|repository|repositories|collaborat|version|code review'),
 'testing': (('testing','unit tests','unit testing','pytest','JUnit','test automation'), r'tests?|coverage|bugs?|defects?|api|cases?|regression|quality|validation'),
 'javascript': (('JavaScript','TypeScript','React','Node.js'), r'web|interface|apps?|application|components?|api|pages?|browser|forms?'),
 'html': (('HTML','HTML5'), r'web|pages?|forms?|semantic|accessib|interface'),
 'css': (('CSS','CSS3','Tailwind','Bootstrap'), r'layout|responsive|style|web|pages?|interface|mobile|design'),
 'java': (('Java','Spring Boot'), r'apps?|application|api|server|service|database|android|tests?'),
 'machine learning': (('machine learning','scikit-learn','TensorFlow','PyTorch'), r'model|train|classif|predict|dataset|validation|accuracy|precision|recall'),
 'communication': (('communication','presentations','presented findings','stakeholder communication'), r'present|stakeholder|client|report|findings|team|workshop|audience'),
 'teamwork': (('teamwork','collaborated','collaboration','team project'), r'team|collaborat|members?|project|review|coordinat'),
}
DISPLAY = {'sql':'SQL','cad':'CAD','python':'Python','git':'Git','html':'HTML','css':'CSS','javascript':'JavaScript','java':'Java','visualization':'Data visualization'}
ACTIONS = re.compile(r'\b(?:built|build|design(?:ed|ing)?|develop(?:ed|ing)?|implement(?:ed|ing)?|analy[sz](?:e|ed|ing)|queried|query|wrote|write|join(?:ed|ing)?|clean(?:ed|ing)?|creat(?:e|ed|ing)|automat(?:e|ed|ing)|test(?:ed|ing)?|perform(?:ed|ing)?|conduct(?:ed|ing)?|draft(?:ed|ing)?|model(?:ed|led|ing|ling)?|prepar(?:e|ed|ing)|supervis(?:e|ed|ing)|inspect(?:ed|ing)?|calculat(?:e|ed|ing)|estimat(?:e|ed|ing)|measur(?:e|ed|ing)|validat(?:e|ed|ing)|evaluat(?:e|ed|ing)|present(?:ed|ing)?|report(?:ed|ing)?|reconcil(?:e|ed|ing)|train(?:ed|ing)?|deploy(?:ed|ing)?|manag(?:e|ed|ing)|organi[sz](?:e|ed|ing)|led|reduc(?:e|ed|ing)|improv(?:e|ed|ing)|increas(?:e|ed|ing)|remov(?:e|ed|ing)|process(?:ed|ing)?|ran|us(?:e|ed|ing)|applied|apply|integrat(?:e|ed|ing)|collaborat(?:e|ed|ing)|coordinat(?:e|ed|ing)|document(?:ed|ing)?|compar(?:e|ed|ing)|assess(?:ed|ing)?)\b', re.I)
OBJECTS = re.compile(r'\b(?:data|dataset|database|tables?|records?|queries|reports?|dashboard|charts?|application|app|api|website|pipeline|scripts?|model|plans?|drawings?|building|site|concrete|samples?|test|inventory|budget|lesson|patients?|clients?|users?|process|campaign|project|product|design|equipment|experiment)\b', re.I)
CONCRETE_OBJECTS = re.compile(r'\b(?:data|datasets?|database|tables?|records?|queries|reports?|dashboards?|charts?|application|app|apis?|website|pipeline|scripts?|models?|plans?|drawings?|building|site|concrete|slump|soil|samples?|specimens?|inventory|budget|lessons?|patients?|clients?|users?|orders?|sales|surveys?|beams?|columns?|foundation|reinforcement|loads?|workbooks?|spreadsheets?|test cases?|coverage|bugs?|experiments?|campaigns?|equipment|repositories|branches|commits|pull requests|algorithms?|sorting|search)\b',re.I)
SCOPE = re.compile(r'\b\d+(?:[,.]\d+)*\s*(?:%|rows?|records?|tables?|users?|students?|clients?|hours?|minutes?|seconds?|days?|samples?|tests?|drawings?|requests?|datasets?|reports?|sites?|meters?|metres?|mpa|kn|mm|kg)\b|\d+(?:\.\d+)?\s*%', re.I)
OUTCOME = re.compile(r'\b(?:reduc|improv|increas|achiev|sav|cut|faster|accuracy|completion|performance|delivered|validated)', re.I)
FUTURE = re.compile(r'\b(?:plan(?:ning|ned)? to|intend to|will (?:build|learn|use|develop)|want to learn|aim to|not yet)\b',re.I)
SECTIONS = {
 'skills': ['technical skills','skills and tools','skills & tools','tools and technologies','key skills','core competencies','technologies','skills','tools'],
 'projects': ['academic projects','selected projects','personal projects','relevant projects','technical projects','capstone project','capstone','projects','project'],
 'experience': ['professional experience','work experience','employment history','internship experience','internships','internship','experience','employment'],
 'education': ['education','qualifications','academic background'],
 'summary': ['professional summary','career objective','summary','objective','profile'],
 'certifications': ['certifications','certificates','courses','training'],
 'other': ['interests','hobbies','references','awards','achievements'],
}
HEADER_NAMES = sorted([(label,section) for section,labels in SECTIONS.items() for label in labels], key=lambda item:-len(item[0]))
HEADER_PATTERN = '|'.join(re.escape(label) for label,_ in HEADER_NAMES)


def _pattern(phrase):
    escaped = re.escape(phrase).replace(r'\ ', r'[\s-]+')
    return re.compile(r'(?<![\w])'+escaped+r'(?![\w])',re.I)


def _mentions(text, aliases):
    if FUTURE.search(text):
        return []
    hits=[]
    for alias in aliases:
        for match in _pattern(alias).finditer(text):
            prefix=re.split(r'[;.!?]|\bbut\b',text[max(0,match.start()-70):match.start()],flags=re.I)[-1]
            if re.search(r'\b(?:no|not|never|without|lack(?:ing)?)\b(?:\W+\w+){0,7}\W*$',prefix,re.I):
                continue
            hits.append(match)
    return hits


def _units(text):
    # Handle both line-based uploads and inline headings in pasted resumes.
    text=re.sub(r'(^|[\n.;])\s*('+HEADER_PATTERN+r')\s*:',lambda m:m.group(1)+'\n'+m.group(2)+':\n',text,flags=re.I)
    result=[];section='unsectioned';seen=Counter();present=set()
    for raw in text.splitlines():
        line=' '.join(raw.strip(' \t#*•●▪-–').split())
        if not line:
            continue
        heading=None
        for label,name in HEADER_NAMES:
            if re.fullmatch(re.escape(label)+r'\s*:?',line,re.I):
                heading=name;break
        if heading:
            if not (heading=='skills' and section in ('projects','experience') and line.lower().rstrip(':') in ('technologies','tools','tools and technologies')):
                section=heading
            present.add(section);continue
        for sentence in re.split(r'(?<=[.!?])\s+|[•●▪]\s*',line):
            sentence=sentence.strip()
            if not sentence:
                continue
            fingerprint=re.sub(r'\W+',' ',sentence.casefold()).strip()
            seen[fingerprint]+=1
            if seen[fingerprint]==1:
                result.append({'text':sentence,'section':section})
    duplicate_count=sum(count-1 for value,count in seen.items() if len(value.split())>=6)
    content_count=sum(count for value,count in seen.items() if len(value.split())>=6)
    return result,present,duplicate_count/max(1,content_count)


def _rule(skill):
    key=skill.strip().lower()
    for canonical,(aliases,task) in RULES.items():
        if key==canonical or any(key==alias.lower() for alias in aliases):
            return canonical,aliases,task
    return key,(skill.strip(),),OBJECTS.pattern


def _excerpt(text,match):
    start=max(0,match.start()-75)
    end=min(len(text),start+260)
    return ('…' if start else '')+text[start:end]+('…' if end<len(text) else '')


def _check_skill(skill,units):
    canonical,aliases,task=_rule(skill)
    mentions=[];evidence=[]
    for unit in units:
        text=unit['text'];hits=_mentions(text,aliases)
        if unit['section']=='other':
            continue
        if not hits:
            continue
        mentions.extend(hits)
        eligible=unit['section'] in ('projects','experience','unsectioned') or (unit['section']=='education' and re.search(r'\b(?:project|capstone)\b',text,re.I))
        if not eligible or not ACTIONS.search(text) or not CONCRETE_OBJECTS.search(text):
            continue
        task_hits=list(re.finditer(task,text,re.I))
        close=next((hit for hit in hits if any(abs(hit.start()-candidate.start())<=140 for candidate in task_hits)),None)
        if close is None or len(re.findall(r'\b\w+\b',text))<7:
            continue
        strength=.8 if unit['section'] in ('projects','experience','education') else .65
        signals=['Concrete task in '+('project/experience text' if unit['section']=='unsectioned' else unit['section'])]
        if SCOPE.search(text):
            strength+=.1;signals.append('Specific scale or measurement')
            if OUTCOME.search(text):
                strength+=.1;signals.append('Stated result with a measurement')
        evidence.append({'excerpt':_excerpt(text,close),'section':unit['section'],'strength':round(min(strength,1),2),'signals':signals,'unit':text})
    evidence.sort(key=lambda item:-item['strength'])
    return {'skill':skill,'canonical':canonical,'status':'supported' if evidence else 'listed_only' if mentions else 'missing','strength':evidence[0]['strength'] if evidence else 0,'evidence':evidence[:2]}


def evaluate(text, skills='', career=None):
    units,sections,duplicate_ratio=_units(text)
    wanted=[value.strip() for value in (career.skills if career is not None else skills).split(',') if value.strip()]
    # Canonical aliases represent one skill, not additional points for synonyms.
    wanted=list({ _rule(value)[0]:value for value in wanted }.values())
    if career is not None and not wanted:
        raise ValueError('The selected career has no usable skill requirements. Choose another career or ask an administrator to update it.')
    checks=[_check_skill(skill,units) for skill in wanted]
    claimed={check['canonical']:check for check in checks if check['status']!='missing'}
    for canonical,(aliases,_) in RULES.items():
        if any(_mentions(unit['text'],aliases) for unit in units if unit['section']=='skills'):
            claimed.setdefault(canonical,_check_skill(DISPLAY.get(canonical,canonical.title()),units))
    unsupported=[check for check in claimed.values() if check['status']=='listed_only']
    supported=[check for check in claimed.values() if check['status']=='supported']
    task_units=[unit for unit in units if unit['section'] in ('projects','experience','unsectioned') and ACTIONS.search(unit['text']) and OBJECTS.search(unit['text']) and not FUTURE.search(unit['text']) and len(unit['text'].split())>=7]
    measured=[unit for unit in task_units if SCOPE.search(unit['text'])]
    word_count=len(text.split())
    quality={
        'Contact details': (10 if re.search(r'[\w.+-]+@[\w.-]+\.[a-z]{2,}',text,re.I) else 0,10),
        'Education described': (10 if any(u['section']=='education' for u in units) else 0,10),
        'Clear skills section': (10 if any(u['section']=='skills' for u in units) else 0,10),
        'Substantive projects or experience': (min(20,len(task_units)*10),20),
        'Action-led task descriptions': (min(15,len(task_units)*5),15),
        'Specific scale or outcomes': (min(15,len(measured)*5),15),
        'Readable resume length': (10 if 150<=word_count<=1200 else 5 if 80<=word_count<150 else 0,10),
        'Distinct, non-repeated content': (10 if duplicate_ratio<.2 else 0,10),
    }
    quality_score=sum(item[0] for item in quality.values())
    penalties=[]
    if unsupported:
        penalties.append({'reason':'Skills listed without a concrete supporting task in projects or experience: '+', '.join(check['skill'] for check in unsupported),'points':min(20,4*len(unsupported))})
    if duplicate_ratio>=.2:
        penalties.append({'reason':'Repeated descriptions do not provide additional evidence.','points':10})
    # Repeated skill lists do not earn coverage or evidence repeatedly.
    repeated_keywords=0
    for unit in units:
        if unit['section']!='skills':
            continue
        for aliases,_ in RULES.values():
            spans={(hit.start(),hit.end()) for hit in _mentions(unit['text'],aliases)}
            repeated_keywords+=max(0,len(spans)-2)
    if repeated_keywords>=10 and repeated_keywords/max(1,word_count)>.12:
        penalties.append({'reason':'Heavy keyword repetition without enough task detail.','points':8})
    caps=[]
    if wanted:
        present_count=sum(check['status']!='missing' for check in checks)
        supported_count=sum(check['status']=='supported' for check in checks)
        strength=sum(check['strength'] for check in checks)/len(checks)
        relevant_units={e['unit'] for check in checks for e in check['evidence']}
        relevance=(supported_count/len(checks))*(.75+.25*min(1,len(relevant_units)/2)) if supported_count else 0
        rubric={
            'Target skills mentioned': (round(25*present_count/len(checks),1),25),
            'Evidence behind target skills': (round(40*strength,1),40),
            'Relevant project or experience tasks': (round(20*relevance,1),20),
            'Resume presentation': (round(15*quality_score/100,1),15),
        }
        if not present_count:
            caps.append({'limit':25,'reason':'No target-career skills were found in the resume.'})
        elif not supported_count:
            caps.append({'limit':45,'reason':'No target-career skill has a concrete supporting task in the text.'})
        elif supported_count/len(checks)<.5:
            caps.append({'limit':60,'reason':'Fewer than half the target-career skills have task evidence.'})
        kind='career_fit';label='Career fit'
    else:
        evidence_balance=sum(c['strength'] for c in claimed.values())/max(1,len(claimed))
        rubric={'Resume presentation':(round(.7*quality_score,1),70),'Evidence behind claimed skills':(round(30*evidence_balance,1),30)}
        kind='resume_quality';label='General resume quality'
        if claimed and not supported:
            caps.append({'limit':60,'reason':'Claimed skills are not supported by concrete task descriptions.'})
    base=round(sum(item[0] for item in rubric.values()),1)
    deduction=sum(item['points'] for item in penalties)
    score=max(0,math.floor(base-deduction+.5))
    if caps:
        score=min(score,min(item['limit'] for item in caps))
    suggestions=[]
    for check in checks:
        if check['status']=='missing':
            suggestions.append(f"If you have experience with {check['skill']}, describe a real task or project that used it. Do not add it just to raise the score.")
        elif check['status']=='listed_only':
            suggestions.append(f"Support {check['skill']} with what you did, the tool or method you used, and a concrete output or result. Only include facts you can substantiate.")
    if not suggestions and supported:
        suggestions.append('Keep the strongest task examples and add actual scope or outcomes where you can substantiate them.')
    if not wanted:
        suggestions.insert(0,'Select a target career to get a career-fit score. This general review does not measure suitability for a specific field.')
    if not task_units:
        suggestions.append('Add a Projects or Experience section with concrete tasks, rather than only a list of tools.')
    # Persist only short, selected evidence excerpts, never full parsed units.
    for check in checks+list(claimed.values()):
        for evidence in check['evidence']:
            evidence.pop('unit',None)
    return {
        'schema_version':VERSION,'score':min(100,score),'score_kind':kind,'score_label':label,
        'career':career.title if career is not None else None,'quality_score':quality_score,
        'fit_score':min(100,score) if wanted else None,'base_score':base,'penalty_total':deduction,
        'rubric':{key:{'earned':value[0],'possible':value[1]} for key,value in rubric.items()},
        'quality_rubric':{key:{'earned':value[0],'possible':value[1]} for key,value in quality.items()},
        'matched_skills':[c['skill'] for c in checks if c['status']!='missing'],
        'missing_skills':[c['skill'] for c in checks if c['status']=='missing'],
        'supported_skills':[c['skill'] for c in supported], 'unsupported_skills':[c['skill'] for c in unsupported],
        'skill_evidence':checks if wanted else list(claimed.values()),
        'penalties':penalties,'caps':caps,'suggestions':suggestions[:8],
        'word_count':word_count,'report':'','ai_used':False,
        'limitations':'This rubric assesses text evidence, not the truth of claims, professional eligibility or an employer ATS. A missing example does not prove that you lack a skill. Parsing and terminology can miss valid experience.',
    }
