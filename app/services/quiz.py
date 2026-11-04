"""Transparent, non-diagnostic RIASEC-style exploration rubric."""
QUESTIONS = [
    ('Realistic', 'I enjoy building, fixing or working with my hands.'),
    ('Investigative', 'I like figuring out why something works.'),
    ('Artistic', 'I enjoy creating designs, stories or new ideas.'),
    ('Social', 'Helping someone learn or solve a problem energizes me.'),
    ('Enterprising', 'I like leading a team or pitching an idea.'),
    ('Conventional', 'I enjoy organizing information and getting details right.'),
    ('Realistic', 'I would enjoy using equipment, tools or working outdoors.'),
    ('Investigative', 'I enjoy analyzing data and testing possible explanations.'),
    ('Artistic', 'I prefer projects where I can express my imagination.'),
    ('Social', 'I am patient when listening, teaching or caring for people.'),
    ('Enterprising', 'I am comfortable taking initiative and making decisions.'),
    ('Conventional', 'Clear processes, accurate records and planning appeal to me.'),
]

def score(answers):
    if not isinstance(answers, list) or len(answers) != len(QUESTIONS) or any(type(a) is not int or not 1 <= a <= 5 for a in answers):
        raise ValueError('Please answer all 12 questions using the 1–5 scale.')
    scores = {key:0 for key in ('Realistic','Investigative','Artistic','Social','Enterprising','Conventional')}
    for (key, _), value in zip(QUESTIONS, answers):
        scores[key] += value
    ordered = sorted(scores, key=scores.get, reverse=True)
    cutoff = scores[ordered[2]]
    top = [key for key in ordered if scores[key] >= cutoff]
    profile = 'Career exploration interests: ' + ', '.join(top) + '. '
    profile += ' '.join(question for (_, question), value in zip(QUESTIONS, answers) if value >= 4)
    return scores, profile
