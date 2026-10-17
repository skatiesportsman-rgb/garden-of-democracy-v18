# Validation report — 2026-10-15

## Executed successfully

- Local FastAPI served `/` with HTTP **200**, `/health` HTTP **200**, `/api/snapshot` HTTP **200**, and state-boundary JSON HTTP **200**.
- `node --check site/app.js` — syntax valid.
- `python -m py_compile worker/collect.py worker/postgres_sync.py server.py` — passed.
- `pytest tests/test_pipeline.py -q` — **9 tests passed**. Covers state non-inference, invalid percentages, one-category polls, duplicate revision handling, missing schema rejection, failure-safe offline refresh, 51-jurisdiction roster, and API routes.
- Desktop in-memory Chromium at **1440×900** — loaded 10 poll observations; three recent cards; Pollarium shows 10; poll drilldown works; the source registry; 8 issues; audio toggle and theme controls work; no uncaught JS errors.
- Mobile in-memory Chromium at **390×844** — same checks passed; screenshot inspected visually.

## Important limits

- The sandbox explicitly blocks Chromium navigation to localhost/file URLs. The interactive checks used the real HTML, CSS, and JS in Chromium with a mocked fetch transport reading **the actual dated/verified local JSON source file**, not fabricated election data. This validates UI behavior but **not production HTTP browser navigation**.
- The sandbox blocks outbound DNS; polling/news API requests failed. Therefore **no live API was verified as actually ingesting records** and no publicly reachable site has been deployed.
- The hosted repository, GitHub Pages deployment, scheduled jobs, and optional Postgres credentials are not connected. This is an implementation artifact ready for user-controlled deployment, not an already operating cloud service.
- The complete 13-phase feature brief remains unfinished. See `DEVELOPMENT_PROGRESS.md`.


## Version 4 regression — 2026-10-15
- 12 Python pipeline/API tests: PASS.
- `node --check site/app.js`: PASS.
- Chromium UI test at desktop 1440 and mobile 390 with isolated test-only metadata/finance fixtures: PASS.
- Prior version-3 Chromium theme/audio/finance/results regression: PASS.
- Online API ingestion and public deployment: BLOCKED by environment/network/repository access; neither is called operational.
