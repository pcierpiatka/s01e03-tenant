<script lang="ts">
  // What the kb's own code says about #4471, next to what its incident page says. The code wins.
  import reports from '#lib/data/reports-4471.json';
  import membership from '#lib/data/membership-4471.json';
  import { groupByCause, ticketCause, uniqueById, type Report } from '#lib/kb/causes';
  import { tenantOf } from '#lib/kb/locales';

  let { ticket }: { ticket: number } = $props();
  const merged = $derived(uniqueById(reports as Report[]).filter((r) => r.mergedInto === ticket));
  const groups = $derived(groupByCause(merged, tenantOf));
  const owner = $derived(ticketCause(groups, ticket));
  // Reports the membership table moves out of the cause causes.ts gave them.
  const moved = $derived(
    groups.map((g) => ({
      cause: g.cause,
      kept: g.reports.filter((r) => (membership as { report_id: string; problem_id: string | null }[]).find((m) => m.report_id === r.id)?.problem_id === `P-${g.cause}`).length,
      total: g.reports.length,
    })),
  );
</script>

<table>
  <thead><tr><th>causes.ts group</th><th>reports</th><th>kept under that problem</th><th>moved by a human reading the body</th><th>the incident page says</th></tr></thead>
  <tbody>
    {#each moved as m (m.cause)}
      <tr>
        <td><code>{m.cause}</code>{m.cause === owner ? ' (the ticket’s own cause)' : ''}</td>
        <td>{m.total}</td>
        <td>{m.kept}</td>
        <td>{m.total - m.kept}</td>
        <td>{m.cause === owner ? 'one issue, fix queued' : 'nothing: merged into #' + ticket + ' as if it were the same bug'}</td>
      </tr>
    {/each}
  </tbody>
</table>
