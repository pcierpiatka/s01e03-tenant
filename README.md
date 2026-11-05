# s01e03-tenant — what ticket #4471 really holds

The support desk merged 412 reports about wrong dates into one ticket, #4471, and marked it known.
This repository splits that ticket into the problems it really contains, files one issue per problem
with the number of reports it covers, and adds a signed page about them to the desk's knowledge base (kb).

## What is here

```
src/                 the kb export (SvelteKit + mdsvex), plus the new page and its components
  routes/kb/incidents/4471-split/+page.svx   the page: words only, every number comes from a component
  lib/kb/ProblemTable.svelte                 counts per problem, computed from the membership table at render time
  lib/kb/CodeVsPage.svelte                   what causes.ts says next to what the incident page says
  lib/kb/IssueLinks.svelte                   one link per problem to its issue
  lib/data/membership-4471.json              report id -> problem or bucket, with reason and who decided
  lib/data/problems-4471.json                the problems: id, slug, title, summary, issue
  lib/data/reports-4471.json                 the export, bodies removed (see Privacy)
analysis/            the same membership and problems, plus counts.json and one id list per problem
tools/               the scripts: counts.py is the one source of numbers; make-issues.py builds the issues from it
rendered/            the page as the desk will see it: rendered/4471-split.html (self-contained) and rendered/site/ (full static build)
RUN-REPORT.md        how the run went: decisions, publications, source changes, errors, cost
```

## How the reports were placed

1. One id, one report: the export's overlapping pages are deduplicated with the kb's own `uniqueById`.
2. Cause by code: `causeOf` in `src/lib/kb/causes.ts` gives each report `parser` or `hint` from its tenant's locale, form and channel. The code is the source of truth for that split.
3. Blind read: readers saw each body without its cause or intake tag and recorded the symptom it describes.
4. Adjudication: where the body describes something a day/month swap cannot produce, or no defect at all, one adjudicator placed the report and wrote the reason into `analysis/membership.json`.
5. Second opinion: a fresh reader re-checked every disputed report and a fixed-seed sample of the rest (`analysis/second-opinion.json`).
6. One source of numbers: `tools/counts.py` checks that every unique report is placed exactly once, that the total equals the export's unique count, that each issue's count equals the length of its id list, and that every id exists in the export. The issues, the page and the report all read from `analysis/counts.json`.

## Build the kb

```
npm install
npm run build        # static site in build/, the page at build/kb/incidents/4471-split.html
```

## Check the numbers

```
python3 -I tools/counts.py analysis/snapshot.json analysis/membership.json analysis/problems.json /tmp/check
```

## Privacy

Report bodies are not in this repository. `src/lib/data/reports-4471.json` keeps every record and id
but replaces each body with a marker, so the page builds and the counts match the desk's export.
