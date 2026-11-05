#!/usr/bin/env python3 -I
"""Compare blind verifier observations with the kb-code baseline.

usage: compare.py <baseline.json> <verify-output-dir> <out.json>
Writes a list of rows {id, tenant, channel, baseline, symptom, secondSymptom, confidence, status}
status: agree | disagree | unverified
A row agrees when the body's symptom is `swap` with no second symptom: both parser and hint produce a
month/day swap, and which of the two it is comes from the tenant's form and channel (causes.ts), not from
the body. Any other symptom, any second symptom, or unclear/low confidence is a disagreement to adjudicate.
"""
import json, sys, os, collections
base_path, vdir, out = sys.argv[1:4]
baseline = {r['id']: r for r in json.load(open(base_path))}
obs = {}
for f in sorted(os.listdir(vdir)):
    if not f.endswith('.json'): continue
    for o in json.load(open(os.path.join(vdir, f))):
        obs[o['id']] = o
rows = []
for rid, b in sorted(baseline.items()):
    o = obs.get(rid)
    if o is None:
        rows.append({**b, 'symptom': None, 'secondSymptom': None, 'confidence': None, 'status': 'unverified', 'obs': None}); continue
    sym, sec, conf = o.get('symptom'), o.get('secondSymptom'), o.get('confidence')
    agree = sym == 'swap' and not sec and conf in ('high', 'medium') and b['baseline'] != 'unplaced'
    rows.append({**b, 'symptom': sym, 'secondSymptom': sec, 'confidence': conf, 'status': 'agree' if agree else 'disagree', 'obs': o})
json.dump(rows, open(out, 'w'), indent=1, ensure_ascii=False)
c = collections.Counter(r['status'] for r in rows)
print('rows', len(rows), dict(c))
print('by symptom', dict(collections.Counter(r['symptom'] for r in rows)))
print('disagree by baseline', dict(collections.Counter((r['baseline'], r['symptom'], r['secondSymptom']) for r in rows if r['status'] == 'disagree')))
extra = set(obs) - set(baseline)
if extra: print('WARN observed ids not in baseline:', sorted(extra))
