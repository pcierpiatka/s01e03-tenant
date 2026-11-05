#!/usr/bin/env python3 -I
"""Generate one issue (title + body markdown) per problem from counts.json and the id lists.
usage: make-issues.py <counts-dir> <membership.json> <out-dir> <repo-slug owner/name> <page-path-in-repo>
Numbers are read from counts.json, never typed."""
import json, sys, os
cdir, mem_p, out, repo, page_path = sys.argv[1:6]
counts = json.load(open(os.path.join(cdir, 'counts.json')))
members = json.load(open(mem_p))
os.makedirs(out, exist_ok=True)
for p in counts['problems']:
    ids = open(os.path.join(cdir, 'ids', f"{p['id']}.txt")).read().split()
    assert len(ids) == p['count'], (p['id'], len(ids), p['count'])
    by = {}
    for m in members:
        if m['problem_id'] == p['id']: by[m['decided_by']] = by.get(m['decided_by'], 0) + 1
    title = f"{p['title']} ({p['count']} {'report' if p['count']==1 else 'reports'})"
    body = f"""**Reports covered: {p['count']}** of {counts['unique']} unique reports merged into #4471 (export snapshot {counts['snapshotTakenAt']}, {counts['records']} records, duplicates by id removed).

{p['summary']}

**Placement.** {', '.join(f'{n} by {k}' for k, n in sorted(by.items(), key=lambda x: -x[1]))}. `causes.ts` in the kb settles `parser` vs `hint` by tenant locale, form and channel; a blind read of every body found the reports whose symptom is not a day/month swap, and one adjudicator placed those with a written reason. Every reason is in [`analysis/membership.json`](https://github.com/{repo}/blob/main/analysis/membership.json).

**Report ids ({p['count']}):** [`analysis/ids/{p['id']}.txt`](https://github.com/{repo}/blob/main/analysis/ids/{p['id']}.txt)

<details><summary>ids</summary>

```
{chr(10).join(ids)}
```

</details>

**kb page:** [`{page_path}`](https://github.com/{repo}/blob/main/{page_path}) · rendered: [`rendered/4471-split.html`](https://github.com/{repo}/blob/main/rendered/4471-split.html)

Problem id `{p['id']}` · slug `{p['slug']}` · counts from `analysis/counts.json`, checked by `tools/counts.py`.
"""
    json.dump({'id': p['id'], 'title': title, 'body': body, 'count': p['count']}, open(os.path.join(out, f"{p['id']}.json"), 'w'), indent=1)
    print(p['id'], '|', title)
