# Version 10 — Living Garden and Parallel Evidence Quests

## Added
- Continuously breathing petals and swaying whole flowers on the map.
- Animated flowing dash texture on issue vines; hover/focus glow and keyboard interaction preserved.
- Gentle drifting finance glyphs, moving fireflies, butterflies, and leaves. These animate *existing published records*; movement does **not** represent new money, new government activity, or new public opinion.
- Motion intensity slider changes speed of the garden artwork. Operating-system reduced-motion preference disables these animations.
- Parallel Gardens: choose or randomize two states, filter by issue, inspect five independent categories of source records, open original sources, and play four research challenges with progress.
- Comparative counts remain distinct from voter support and do not create predictive scores.

## Validation performed
- `node --check site/app.js`: passed.
- 35 focused Python tests (`tests/test_pipeline.py`, `test_v9_openstates.py`, `test_v8_assistant.py`, `test_v7_audit.py`, `test_v6_integrations.py`): passed.
- Local HTTP endpoint on port 8765: HTTP 200.
- Browser-level visual regression: **not verified**; Playwright Chromium executable is unavailable in this environment. Check on desktop and phone before production publication.
- External source connections and public deployment: not reverified; continue using your Mac's authenticated collector and public GitHub deployment workflow.

## Upgrade on Mac
1. Keep the older folder; do not copy API keys into source code.
2. Open the new extracted folder and create/activate `.venv` as described in README.
3. Import saved data using `python tools/import_existing_snapshot.py "$HOME/Downloads/garden-of-democracy 6/site/data/snapshot.json"` or the path of your latest collected `snapshot.json`.
4. Run `python -m uvicorn server:app --host 127.0.0.1 --port 8000`.
5. In Safari open `http://127.0.0.1:8000`, select **Compare**, try **Surprise me**, then click category counts and research challenges.
