// Runs the kb's own causes.ts over the export. tenantOf is a plain lookup over the tenant files,
// because locales.ts uses Vite's import.meta.glob, which does not run outside a Vite build.
import { readFileSync, readdirSync, writeFileSync } from 'fs';
import { causeOf, dayFirst, groupByCause, readAs, sameCause, ticketCause, uniqueById, type Report, type Tenant } from '../raw/support-kb/src/lib/kb/causes';
import { DEDUPE_CASES } from '../raw/support-kb/src/lib/kb/dedupe-cases';
const [,, reportsPath, tenantsDir, notesPath, outPath] = process.argv;
const reports = JSON.parse(readFileSync(reportsPath, 'utf8')) as Report[];
const tenants = new Map(readdirSync(tenantsDir).filter(f => f.endsWith('.json')).map(f => { const t = JSON.parse(readFileSync(`${tenantsDir}/${f}`, 'utf8')) as Tenant; return [t.handle, t] as const; }));
const tenantOf = (r: Pick<Report,'tenant'>) => tenants.get(r.tenant);
const notes = JSON.parse(readFileSync(notesPath, 'utf8')) as { oneDayMove: string[] };
const uniq = uniqueById(reports).filter(r => r.mergedInto === 4471);
const groups = groupByCause(uniq, tenantOf);
const owner = ticketCause(groups, 4471);
console.log('records', reports.length, 'unique merged into 4471', uniq.length, 'owner cause', owner);
for (const t of [...tenants.values()].sort((a,b)=>a.handle.localeCompare(b.handle))) console.log(' tenant', t.handle, t.locale, t.form, 'dayFirst', dayFirst(t.locale));
for (const g of groups) console.log(' group', g.cause, g.reports.length, 'tagged', JSON.stringify(g.taggedAs), 'tenants', g.tenants, g.firstSeen, '->', g.lastSeen, 'oneDayMove readAs', readAs(g, notes.oneDayMove));
console.log('DEDUPE_CASES:');
for (const c of DEDUPE_CASES) console.log(' ', c.why, '| sameSubject', c.a.subject===c.b.subject, '| sameCause', sameCause(c.a, tenantOf(c.a), c.b, tenantOf(c.b)), '| a', causeOf(c.a, tenantOf(c.a)), 'b', causeOf(c.b, tenantOf(c.b)));
const rows = uniq.map(r => ({ id: r.id, tenant: r.tenant, channel: r.channel, intakeTag: r.meta.intakeTag, browserLocale: r.meta.browserLocale, baseline: causeOf(r, tenantOf(r)) ?? 'unplaced', oneDayMoveNote: notes.oneDayMove.includes(r.id) }));
writeFileSync(outPath, JSON.stringify(rows, null, 1));
console.log('wrote', outPath, rows.length);
