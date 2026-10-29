# Rendered pages

`kb/incidents/4471-split.html` is `src/routes/kb/incidents/4471-split/+page.svx` as the desk sees it:
the runbook frame, the problem table computed from `src/lib/data/`, and the desk ref from the
page's signature. Rebuild it with:

```
python3 tools/render.py . rendered/kb/incidents/4471-split.html
```
