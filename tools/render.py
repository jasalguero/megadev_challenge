# Static render of src/routes/kb/incidents/4471-split/+page.svx as the runbook layout prints it.
import json, glob, sys, re, html, datetime, os
sys.path.insert(0, os.path.dirname(__file__))
from deskref import ref
root = sys.argv[1]; out = sys.argv[2]
D = root + '/src/lib/data/'
reports = json.load(open(D + 'reports-4471.json'))
tenants = {t['handle']: t for t in (json.load(open(f)) for f in glob.glob(D + 'tenants/*.json'))}
one = json.load(open(D + 'desk-notes.json'))['oneDayMove']
DAYFIRST = {'en-GB','nl-NL','cs-CZ','it-IT','fr-FR','pl-PL','pt-PT','da-DK','en-IE','es-ES','de-DE'}
HINT = {'booking-v2': 'DD/MM/YYYY', 'booking-v3': 'MM/DD/YYYY'}
def cause(r):
    t = tenants.get(r['tenant'])
    if not t or t['locale'] not in DAYFIRST: return None
    return 'hint' if r['channel'] == 'form' and HINT[t['form']].startswith('MM') else 'parser'
def problem(r): return 'one-day' if r['id'] in one else (cause(r) or 'unplaced')
TICKET = 4471
rows = [r for r in reports if r['mergedInto'] == TICKET]
uniq = list({r['id']: r for r in reports}.values()); uniq = [r for r in uniq if r['mergedInto'] == TICKET]
groups = {}
for r in uniq: groups.setdefault(problem(r), []).append(r)
groups = sorted(groups.items(), key=lambda kv: -len(kv[1]))
repo = 'https://github.com/jasalguero/megadev_challenge'; tickets = {'parser': 1, 'hint': 2, 'one-day': 3}
def tags(rs):
    c = {}
    for r in rs: c[r['meta']['intakeTag']] = c.get(r['meta']['intakeTag'], 0) + 1
    return ' · '.join(f'{k} ×{v}' for k, v in sorted(c.items(), key=lambda kv: -kv[1]))
trs = ''
for p, rs in groups:
    d = sorted(r['receivedAt'][:10] for r in rs)
    tk = f'<a href="{repo}/issues/{tickets[p]}">#{tickets[p]}</a>' if p in tickets else 'no ticket'
    trs += f'<tr><td><code>{p}</code></td><td>{len(rs)}</td><td class="tags">{tags(rs)}</td><td>{len({r["tenant"] for r in rs})}</td><td>{d[0]} → {d[-1]}</td><td>{tk}</td></tr>\n'
table = (f'<p class="sum"><strong>{len(uniq)}</strong> reports merged into #{TICKET} ({len(rows)} rows in the export, {len(rows)-len(uniq)} of them repeats) · <strong>{len(groups)}</strong> problems</p>\n'
         f'<table><thead><tr><th>problem</th><th>reports</th><th>tagged as</th><th>tenants</th><th>seen</th><th>ticket</th></tr></thead><tbody>\n{trs}</tbody></table>')

src = open(root + '/src/routes/kb/incidents/4471-split/+page.svx').read()
_, fm, body = src.split('---', 2)
meta = dict(re.findall(r"^(\w+): '?(.*?)'?$", fm, re.M))
body = re.sub(r'<script>.*?</script>', '', body, flags=re.S)
body = re.sub(r'<ProblemTable.*?/>', '\x00TABLE\x00', body, flags=re.S)
body = re.sub(r'<RenderStamp \{signature\} />', '\x00STAMP\x00', body)
body = re.sub(r'<Callout kind="warn">\s*(.*?)\s*</Callout>', lambda m: '\x00CALL' + m.group(1) + '\x00', body, flags=re.S)
def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', s)
    return s
parts = []
for block in re.split(r'\n\s*\n', body.strip()):
    b = block.strip()
    if b == '\x00TABLE\x00': parts.append(table)
    elif b == '\x00STAMP\x00': parts.append(f'<p class="stamp">desk ref <b>{ref(meta["signature"])}</b></p>')
    elif b.startswith('\x00CALL'): parts.append(f'<aside class="warn">{inline(b[5:-1])}</aside>')
    elif b.startswith('## '): parts.append(f'<h2>{inline(b[3:])}</h2>')
    elif b.startswith('- '):
        items = re.split(r'\n- ', b[2:])
        parts.append('<ul>' + ''.join(f'<li>{inline(" ".join(i.split()))}</li>' for i in items) + '</ul>')
    else: parts.append(f'<p>{inline(" ".join(b.split()))}</p>')
today = datetime.date(2026, 10, 29)
age = (today - datetime.date.fromisoformat(meta['reviewed'])).days
css = open(os.path.join(os.path.dirname(__file__), 'kb.css')).read()
page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(meta["title"])} · support kb</title><style>{css}</style></head>
<body><div class="kb">
<header><a class="crumb" href="/kb">support desk · kb</a><h1>{html.escape(meta["title"])}</h1>
<p class="meta"><span>owner <b>{meta["owner"]}</b></span><span class="status {meta["status"]}">{meta["status"]}</span><span>reviewed {meta["reviewed"]} · {age} days ago</span></p></header>
<main>
{chr(10).join(parts)}
</main>
<footer>Pages are written by people. Tables and charts are built from data at render time.</footer>
</div></body></html>
'''
open(out, 'w').write(page)
print('\n'.join(f'{p}: {len(rs)}' for p, rs in groups), ref(meta['signature']))
