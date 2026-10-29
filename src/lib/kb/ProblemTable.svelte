<script lang="ts">
  import reports from '#lib/data/reports-4471.json';
  import notes from '#lib/data/desk-notes.json';
  import { uniqueById, type Report } from '#lib/kb/causes';
  import { tenantOf } from '#lib/kb/locales';
  import { splitTicket, type Problem } from '#lib/kb/problems';

  // tickets: problem → issue number in `repo`.
  let { ticket, repo, tickets }: { ticket: number; repo: string; tickets: Partial<Record<Problem, number>> } = $props();

  const rows = $derived((reports as Report[]).filter((r) => r.mergedInto === ticket).length);
  const unique = $derived(uniqueById(reports as Report[]).filter((r) => r.mergedInto === ticket).length);
  const groups = $derived(splitTicket(reports as Report[], ticket, tenantOf, notes.oneDayMove));
  const tags = (g: { taggedAs: Record<string, number> }) =>
    Object.entries(g.taggedAs)
      .sort((a, b) => b[1] - a[1])
      .map(([tag, n]) => `${tag} ×${n}`)
      .join(' · ');
  const issue = (p: string) => tickets[p as Problem];
</script>

<p class="sum">
  <strong>{unique}</strong> reports merged into #{ticket} ({rows} rows in the export, {rows - unique} of them repeats) ·
  <strong>{groups.length}</strong>
  {groups.length === 1 ? 'problem' : 'problems'}
</p>

<table>
  <thead>
    <tr><th>problem</th><th>reports</th><th>tagged as</th><th>tenants</th><th>seen</th><th>ticket</th></tr>
  </thead>
  <tbody>
    {#each groups as g (g.problem)}
      <tr class:open={!issue(g.problem)}>
        <td><code>{g.problem}</code></td>
        <td>{g.reports.length}</td>
        <td class="tags">{tags(g)}</td>
        <td>{g.tenants.length}</td>
        <td>{g.firstSeen} → {g.lastSeen}</td>
        <td>
          {#if issue(g.problem)}<a href="{repo}/issues/{issue(g.problem)}">#{issue(g.problem)}</a>{:else}no ticket{/if}
        </td>
      </tr>
    {/each}
  </tbody>
</table>

<style>
  .sum { font-size: 1.1rem; }
  .tags { color: var(--muted); font-size: 0.85em; }
  .open td { background: var(--warn-bg); }
</style>
