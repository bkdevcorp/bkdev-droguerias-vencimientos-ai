import sys
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from app.services.analysis import analyze
cases = json.loads((ROOT/'evals/golden.json').read_text())
results = []
for case in cases:
    actual = sorted(f['code'] for f in analyze(case['input'])['findings'])
    assert actual == sorted(case['expected_codes']), (case['name'], actual)
    results.append({'case':case['name'],'passed':True})
print(json.dumps({'dataset':'synthetic-v1','passed':len(results),'total':len(cases),'results':results},indent=2))
