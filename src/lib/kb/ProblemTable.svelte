<script lang="ts">
  // Every number on the #4471 split page comes from here, at render time, from the membership table.
  // Nothing in the page text is typed by hand. The membership table is the one place a report is placed.
  import reports from '#lib/data/reports-4471.json';
  import membership from '#lib/data/membership-4471.json';
  import problems from '#lib/data/problems-4471.json';
  import snapshot from '#lib/data/snapshot-4471.json';
  import { causeOf, uniqueById, type Report } from '#lib/kb/causes';
  import { tenantOf } from '#lib/kb/locales';

  type Row = { report_id: string; problem_id: string | null; bucket: string | null; reason: string; decided_by: string };
  type Problem = { id: string; slug: string; title: string; summary: string; issue?: string };

  let { ticket }: { ticket: number } = $props();

  const unique = $derived(uniqueById(reports as Report[]).filter((r) => r.mergedInto === ticket));
  const byId = $derived(new Map(unique.map((r) => [r.id, r] as const)));
  const rows = membership as Row[];
  const placed = $derived(rows.filter((m) => byId.has(m.report_id)));
  const unplacedIds = $derived(unique.filter((r) => !rows.some((m) => m.report_id === r.id)).map((r) => r.id));

  const of = (pid: string) => placed.filter((m) => m.problem_id === pid).map((m) => byId.get(m.report_id)!);
  const inBucket = (b: string) => placed.filter((m) => m.bucket === b).map((m) => byId.get(m.report_id)!);
  const buckets = $derived([...new Set(placed.flatMap((m) => (m.bucket ? [m.bucket] : [])))].sort());
  const days = (rs: Report[]) => rs.map((r) => r.receivedAt.slice(0, 10)).sort();
  const codeSays = (rs: Report[]) =>
    Object.entries(rs.reduce<Record<string, number>>((n, r) => { const c = causeOf(r, tenantOf(r)) ?? 'unplaced'; return { ...n, [c]: (n[c] ?? 0) + 1 }; }, {}))
      .sort((a, b) => b[1] - a[1]).map(([c, n]) => `${c} ×${n}`).join(' · ');
  const channels = (rs: Report[]) =>
    Object.entries(rs.reduce<Record<string, number>>((n, r) => ({ ...n, [r.channel]: (n[r.channel] ?? 0) + 1 }), {}))
      .sort((a, b) => b[1] - a[1]).map(([c, n]) => `${c} ×${n}`).join(' · ');
  const decidedBy = (rs: Report[]) =>
    Object.entries(placed.filter((m) => rs.some((r) => r.id === m.report_id)).reduce<Record<string, number>>((n, m) => ({ ...n, [m.decided_by]: (n[m.decided_by] ?? 0) + 1 }), {}))
      .sort((a, b) => b[1] - a[1]).map(([c, n]) => `${c} ×${n}`).join(' · ');
  const total = $derived((problems as Problem[]).reduce((n, p) => n + of(p.id).length, 0) + buckets.reduce((n, b) => n + inBucket(b).length, 0));
</script>

<p class="sum">
  <strong>{unique.length}</strong> unique reports merged into #{ticket}
  (<strong>{(reports as Report[]).filter((r) => r.mergedInto === ticket).length}</strong> records in the export, duplicates by id removed) ·
  <strong>{(problems as Problem[]).length}</strong> problems ·
  snapshot of <code>{snapshot.takenAt}</code>
</p>

<table>
  <thead>
    <tr><th>problem</th><th>reports</th><th>tenants</th><th>channels</th><th>seen</th><th>causes.ts says</th><th>decided by</th><th>ticket</th></tr>
  </thead>
  <tbody>
    {#each problems as p (p.id)}
      {@const rs = of(p.id)}
      <tr>
        <td><b>{p.title}</b><br /><span class="muted">{p.summary}</span></td>
        <td><strong>{rs.length}</strong></td>
        <td>{new Set(rs.map((r) => r.tenant)).size}</td>
        <td class="muted">{channels(rs)}</td>
        <td>{days(rs)[0]} → {days(rs).at(-1)}</td>
        <td class="muted">{codeSays(rs)}</td>
        <td class="muted">{decidedBy(rs)}</td>
        <td>{#if p.issue}<a href={p.issue}>{p.issue.replace(/^https:\/\/github\.com\//, '')}</a>{:else}not filed yet{/if}</td>
      </tr>
    {/each}
    {#each buckets as b (b)}
      {@const rs = inBucket(b)}
      <tr class="bucket">
        <td><b>{b}</b><br /><span class="muted">not a problem of its own; listed so the total adds up</span></td>
        <td><strong>{rs.length}</strong></td>
        <td>{new Set(rs.map((r) => r.tenant)).size}</td>
        <td class="muted">{channels(rs)}</td>
        <td>{days(rs)[0]} → {days(rs).at(-1)}</td>
        <td class="muted">{codeSays(rs)}</td>
        <td class="muted">{decidedBy(rs)}</td>
        <td>—</td>
      </tr>
    {/each}
  </tbody>
  <tfoot>
    <tr><td>total</td><td><strong>{total}</strong></td><td colspan="6" class:bad={total !== unique.length}>{total === unique.length ? 'every unique report has exactly one row' : `does not add up: ${unique.length - total} reports unaccounted for`}</td></tr>
  </tfoot>
</table>

{#if unplacedIds.length}
  <p class="bad">{unplacedIds.length} reports in the export have no row in the membership table: {unplacedIds.join(', ')}</p>
{/if}

<style>
  .sum { font-size: 1.1rem; }
  .muted { color: var(--muted); font-size: 0.85em; }
  .bucket td { background: var(--note-bg); }
  .bad { color: var(--warn); font-weight: 600; }
  tfoot td { font-weight: 600; }
</style>
