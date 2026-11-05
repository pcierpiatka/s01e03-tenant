#!/usr/bin/env python3 -I
"""Public copy of the export: same records and ids, bodies removed. usage: redact.py <in.json> <out.json>"""
import json, sys
d = json.load(open(sys.argv[1]))
for r in d: r['body'] = '[removed from the public copy; the desk holds the text]'
json.dump(d, open(sys.argv[2], 'w'), indent=2, ensure_ascii=False)
print('redacted', len(d), 'records ->', sys.argv[2])
