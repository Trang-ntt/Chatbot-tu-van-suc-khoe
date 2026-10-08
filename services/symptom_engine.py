import json
from pathlib import Path

DATA = json.loads(Path(__file__).with_name('diseases.json').read_text(encoding='utf-8'))


def analyze(symptoms):
    selected = [s.strip().lower() for s in symptoms if s.strip()]
    results = []
    for disease in DATA:
        count = sum(1 for s in selected if s in [x.lower() for x in disease['symptoms']])
        percent = round(count / len(disease['symptoms']) * 100) if disease['symptoms'] else 0
        results.append({'name': disease['name'], 'percent': percent, 'advice': disease['advice']})
    results.sort(key=lambda x: x['percent'], reverse=True)
    return results[:5]
