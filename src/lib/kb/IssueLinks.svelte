<script lang="ts">
  // One link per problem, to the ticket filed for it. Counts come from the membership table, not from here.
  import problems from '#lib/data/problems-4471.json';
  import membership from '#lib/data/membership-4471.json';
  type Problem = { id: string; slug: string; title: string; summary: string; issue?: string };
  const count = (pid: string) => (membership as { problem_id: string | null; alsoCountedUnder?: string[] }[]).filter((m) => m.problem_id === pid || (m.alsoCountedUnder ?? []).includes(pid)).length;
</script>

<ul>
  {#each problems as p (p.id)}
    <li>
      {#if p.issue}<a href={p.issue}>{p.title}</a>{:else}{p.title} (not filed yet){/if}
      · {count(p.id)} {count(p.id) === 1 ? 'report' : 'reports'}
    </li>
  {/each}
</ul>
