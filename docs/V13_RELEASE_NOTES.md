# Version 13 — Harvest Journal and public-launch reliability

**Built on V12.** The soft cottage-garden visuals, state-clipped animations, interactive Parallel Gardens, Ask the Garden, source registry, and all current adapters remain.

## Shipped

1. **Harvest Journal:** A source-linked, filterable list of new or revised records that actually reached the collector. Records distinguish `collected_at` from the original `published_at`; a record revision does not add a second poll. The bounded journal contains at most 250 changes, not all observations. No events are generated to make the artwork appear busier.
2. **Healthier Observatory:** Full successful/attempted source-check times, status, and errors. Polling measurements, legislation and finance remain separate types of evidence. Public refresh doesn't reset the age of the source evidence.
3. **Safer federal API access:** FEC and Congress.gov now receive credentials in the supported `X-Api-Key` HTTP header rather than in the request URL. The website never ships these credentials to the browser.
4. **Pages deployment preflight:** `python tools/deployment_doctor.py` audits records, 51 state/DC identities, public paths, and tests the website under a nested `/garden-of-democracy/` URL using a local HTTP server. It does **not** fake a GitHub deployment.
5. **Gentler news cadence:** Scheduled GitHub Actions checks GDELT only on six-hour UTC boundaries to reduce 429 rate-limit responses. All other integrated sources retain their source-aware behavior. A collector may still report a provider as unavailable.
6. **Mac startup convenience:** `start.command` chooses the first free local port from 8000–8003, without stopping any prior servers, and opens the correct URL.
7. **Security:** Local `.venv/` directories are now ignored by Git when preparing a public repository.

## Evidence and technical limits

- The bundled project includes 10 editorially checked dated polling records, four linked debate records, and no newly imported OpenStates/FEC data. **Your live collected political data remains in your Mac's previous project folder** and must be imported using `tools/import_existing_snapshot.py`. Do not mistake a fresh ZIP for your most recent personal snapshot.
- Any user-provided API keys are **not included** in this ZIP. Restore them privately in Terminal or GitHub Actions secrets after deploying.
- Local browser and static-host smoke tests do **not** establish provider connectivity, GitHub Actions execution or a publicly accessible URL. A project owner needs to publish and inspect live GitHub Actions output.
- GitHub Pages serves static HTML/CSS/JS and snapshots. It does not run an always-on server or an internet-accessible local Ollama model. The deterministic source-grounded Ask the Garden works on Pages.
- The Harvest Journal is a *collection change log*, not a continuous stream of citizens' activities. It is not a substitute for a state election result feed.

## Test commands

```bash
python -m pytest tests/test_pipeline.py tests/test_v5_layers.py tests/test_v6_integrations.py tests/test_v7_audit.py tests/test_v8_assistant.py tests/test_v9_openstates.py tests/test_v12_state_motion.py tests/test_v13_harvest.py tests/test_v13_browser.py -q
node --test tests/test_ask_garden.mjs
python tools/deployment_doctor.py
node --check site/app.js
```

See [the publishing guide](GITHUB_PUBLISHING.md) for free GitHub Pages setup and honest live-feed verification.
