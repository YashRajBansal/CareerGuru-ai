"""Explainable interest matching: comma-separated choices, simple language, no model."""
import math
import re
from collections import Counter
from services import ai

SUGGESTIONS = ('cricket', 'coding', 'drawing', 'building design', 'helping people', 'business', 'cooking', 'numbers')
CANONICAL = {
    'cricketer':'cricket', 'cricketers':'cricket', 'materials':'material',
    'testing':'test', 'tests':'test', 'tested':'test', 'engineers':'engineer',
    'engineering':'engineer', 'buildings':'building', 'computers':'computer',
    'programmer':'programming', 'programmers':'programming', 'autocad':'cad',
    'sketching':'drawing', 'illustration':'drawing', 'illustrator':'drawing',
    'cooks':'cooking', 'cook':'cooking', 'teaching':'teach', 'teacher':'teach',
}
IGNORE = ai.STOP | {'i','my','me','a','an','in','of','to','enjoy','enjoys','playing','play','love','really','am','also','skills','interests','learning'}
# Everyday terms bridge to vocabulary used in actual career profiles.
EXPANSIONS = {
    'coding': {'programming','python','software'},
    'computers': {'computer','software','troubleshooting'},
    'computer': {'computer','software','troubleshooting'},
    'building design': {'building','cad','civil'},
    'helping people': {'teach','care','support','counseling'},
    'numbers': {'statistics','accounting','spreadsheets','financial'},
    'business': {'business','sales','budgeting','entrepreneur'},
}

def split_interests(text):
    values, seen = [], set()
    for part in re.split(r'[,;\n]+', text or ''):
        value = ' '.join(part.split()).strip()
        if value and value.casefold() not in seen:
            values.append(value)
            seen.add(value.casefold())
    return values

def terms(text):
    return Counter(CANONICAL.get(t,t) for t in re.findall(r'[a-z][a-z0-9+#]*',text.lower()) if t not in IGNORE)

def interest_group(value):
    base = set(terms(value))
    alternatives = EXPANSIONS.get(value.casefold().strip())
    if alternatives:
        return set(CANONICAL.get(t,t) for t in alternatives), True
    return base, False

def career_terms(career):
    weighted = Counter()
    for text, weight in [(career.title,4),(career.skills,2),(career.traits,1)]:
        for token,count in terms(text).items():
            weighted[token] += weight*count
    return weighted

def coverage(group, available):
    tokens, alternatives = group
    if not tokens:
        return 0.0
    hits = len(tokens & available)
    # An everyday synonym group represents alternatives, not required skills.
    return (1.0 if hits else 0.0) if alternatives else hits/len(tokens)

def matching_interests(text, career):
    available = set(career_terms(career))
    return [value for value in split_interests(text) if coverage(interest_group(value),available)>=.75]

def rank_careers(text, careers, quiz_profile='', limit=6):
    interests = split_interests(text)
    if not interests:
        ranked, _ = ai.rank(quiz_profile,careers,limit) if quiz_profile else ([], '')
        return [(s,c) for s,c in ranked if s>0], 'Local text similarity · quiz interests'
    groups = [interest_group(value) for value in interests]
    groups = [group for group in groups if group[0]]
    if not groups:
        return [], 'Local text similarity · individual interests'
    query = Counter(token for group,_ in groups for token in group)
    scored = []
    for career in careers:
        weighted = career_terms(career)
        covered = sum(coverage(group,set(weighted)) for group in groups)/len(groups)
        if not covered:
            continue
        norm = math.sqrt(sum(v*v for v in query.values())*sum(v*v for v in weighted.values()))
        similarity = sum(v*weighted.get(t,0) for t,v in query.items())/norm if norm else 0.0
        primary = .8*covered+.2*similarity
        # Quiz results can refine a match; they never introduce a career unrelated
        # to the interests explicitly entered for this search.
        quiz_similarity = ai.lexical(quiz_profile,career.document()) if quiz_profile else 0.0
        scored.append((round(primary,6),quiz_similarity,career))
    ordered = sorted(scored,key=lambda row:(-row[0],-row[1],row[2].title.casefold()))[:limit]
    return [(score,career) for score,_,career in ordered], 'Local text similarity · individual interests'
