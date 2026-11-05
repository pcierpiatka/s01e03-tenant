#!/usr/bin/env python3 -I
"""The one source of numbers.

usage: counts.py <snapshot.json> <membership.json> <problems.json> <out-dir> [baseline.json]
membership.json: list of {report_id, problem_id | null, bucket | null, reason, decided_by, alsoCountedUnder: [problem_id]}
  alsoCountedUnder: problems that count this report too, the way the desk's CauseTable does (filed by cause, footnoted).
problems.json:   list of {id, slug, title, summary}
Checks the invariants, then writes <out-dir>/counts.json and <out-dir>/ids/<problem-id>.txt.
Exit 1 on any failed invariant. Nothing downstream may type a number by hand: read counts.json.
"""
import json, sys, os, collections
snap_p, mem_p, prob_p, out = sys.argv[1:5]
base_p = sys.argv[5] if len(sys.argv) > 5 else None
snap = json.load(open(snap_p)); members = json.load(open(mem_p)); problems = json.load(open(prob_p))
ids = set(snap['ids']); pids = {p['id'] for p in problems}
errors = []
seen = collections.Counter(m['report_id'] for m in members)
dup = [i for i, n in seen.items() if n > 1]
if dup: errors.append(f'report ids with more than one row: {dup}')
missing = sorted(ids - set(seen))
if missing: errors.append(f'unique reports with no row: {len(missing)} e.g. {missing[:5]}')
unknown = sorted(set(seen) - ids)
if unknown: errors.append(f'rows whose id is not in the snapshot: {unknown}')
for m in members:
    if (m.get('problem_id') is None) == (m.get('bucket') is None):
        errors.append(f"{m['report_id']}: needs exactly one of problem_id or bucket")
    if m.get('problem_id') is not None and m['problem_id'] not in pids:
        errors.append(f"{m['report_id']}: unknown problem {m['problem_id']}")
    if not m.get('reason') or not m.get('decided_by'):
        errors.append(f"{m['report_id']}: reason and decided_by are required")
if len(members) != snap['unique']:
    errors.append(f"rows {len(members)} != snapshot unique {snap['unique']}")
by_problem = collections.defaultdict(list); by_bucket = collections.defaultdict(list); also = collections.defaultdict(list)
for m in members:
    (by_problem[m['problem_id']] if m.get('problem_id') is not None else by_bucket[m['bucket']]).append(m['report_id'])
    for extra in m.get('alsoCountedUnder', []):
        if extra not in pids: errors.append(f"{m['report_id']}: alsoCountedUnder unknown problem {extra}")
        if extra == m.get('problem_id'): errors.append(f"{m['report_id']}: alsoCountedUnder repeats its own problem")
        also[extra].append(m['report_id'])
total = sum(len(v) for v in by_problem.values()) + sum(len(v) for v in by_bucket.values())
if total != snap['unique']: errors.append(f'primary rows {total} != unique {snap["unique"]}')
# The desk's view: a problem that carries a causes.ts cause covers exactly the reports the code gives that cause.
if base_p:
    base = {r['id']: r['baseline'] for r in json.load(open(base_p))}
    for p in problems:
        if p.get('cause'):
            code = sorted(i for i, c in base.items() if c == p['cause'])
            ours = sorted(by_problem[p['id']] + also[p['id']])
            if code != ours: errors.append(f"{p['id']}: covers {len(ours)} but causes.ts gives {p['cause']} to {len(code)}; diff {sorted(set(code) ^ set(ours))[:6]}")
if errors:
    print('INVARIANTS FAILED'); [print(' -', e) for e in errors]; sys.exit(1)
os.makedirs(os.path.join(out, 'ids'), exist_ok=True)
counts = {
    'snapshotTakenAt': snap['takenAt'], 'snapshotSha256': snap['sha256'], 'records': snap['records'], 'unique': snap['unique'],
    'problems': [{**p, 'count': len(by_problem[p['id']]) + len(also[p['id']]), 'primary': len(by_problem[p['id']]), 'alsoCounted': len(also[p['id']]),
                  'alsoCountedUnder': sorted({x for m in members if m.get('problem_id') == p['id'] for x in m.get('alsoCountedUnder', [])})} for p in problems],
    'buckets': [{'bucket': b, 'count': len(v)} for b, v in sorted(by_bucket.items())],
    'total': total,
    'overlap': sum(len(v) for v in also.values()),
    'sumOfTicketCounts': total + sum(len(v) for v in also.values()),
    'note': 'Each unique report has one primary row. A ticket also counts the reports the desk files under its cause (causes.ts) even when their body describes another problem; those are counted in both tickets and footnoted, as readAs does on the incident page.',
}
json.dump(counts, open(os.path.join(out, 'counts.json'), 'w'), indent=1)
for p in problems:
    open(os.path.join(out, 'ids', f"{p['id']}.txt"), 'w').write('\n'.join(sorted(by_problem[p['id']] + also[p['id']])) + '\n')
for b, v in by_bucket.items():
    open(os.path.join(out, 'ids', f'bucket-{b}.txt'), 'w').write('\n'.join(sorted(v)) + '\n')
print('INVARIANTS OK', json.dumps({p['id']: p['count'] for p in counts['problems']}), 'buckets', {b['bucket']: b['count'] for b in counts['buckets']}, 'primary total', total, 'overlap', counts['overlap'], 'snapshot', snap['takenAt'])
