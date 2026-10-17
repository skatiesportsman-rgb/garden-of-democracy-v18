# DEVELOPMENT_PROGRESS — 2026-10-15

## Continuation — 2026-10-15
- Added historical publication-date replay controls. Time Machine now selects an actual survey release date rather than a misleading percentage of records, and the national map, counts and state detail use the same cutoff. A return-to-latest control restores the complete published dataset.
- Reconfirmed nine Python backend/integrity tests and JavaScript parsing. Existing desktop and mobile navigation, poll cards, source list, debate cards, audio toggle and theme controls passed browser smoke checks. The new replay interaction still needs an isolated automated end-to-end assertion before it can be called fully browser-verified.
- Re-checked VoteHub, PollResults and FEC documentation; external provider ingestion and production publication are **still unverified**.

## Verified today
- **Phase 0 — partially completed.** Current documentation verified for PollResults.org, VoteHub, GDELT, free GitHub Pages/Actions. Restricted development environment cannot execute external API requests; this is explicitly documented, not concealed.
- **Phase 1 — working local foundation.** FastAPI serves the actual website, source snapshot and API, initializes SQLite cache, implements REST + SSE; Pages/Actions production configuration included but not deployed to a live public URL.
- **Phase 2 — working national interactive garden.** All 50 state identifiers plus D.C. available; bundled accurate line boundaries and selectable centroids for offline use, upgraded full state polygons from US Atlas if reachable. Source-linked flower canvas and environment.
- **Phase 3 — working source-grounded polling garden with an important distinction.** Ten personally source-verified/datelabeled published 2026 poll measurements appear as flowers, including GA, MI and TX state-level examples. **Direct polling API worker network ingestion NOT yet runtime verified**; Phase 3's complete feed acceptance criterion remains pending.
- **Phase 4 — collector implemented and locally executed.** Self-contained independent Python job, retries through scheduler, validation, duplicate upsert, durable snapshot, SQLite; GitHub Actions workflow defined. **External successful ingestion after deployment not yet demonstrated.**
- **Phase 5 — partial.** Conservatory showing one sourced Michigan Senate debate record. No ongoing debate bot, transcript processor or complete national calendar.
- **Phase 6 — not complete.** Money Rain and legislation adapters not connected. Side-panel art layer is a legend/control, not actual finance data.
- **Phase 7 — partial.** GDELT public article metadata collector coded; cannot verify in this sandbox. No public discussion stream integration.
- **Phase 8 — partial.** Ambient particles, flowers, stems, 6 art palettes, exhibition mode; advanced botanical movement incomplete.
- **Phase 9 — partial.** User-activated Web Audio note generation, mute, volume; no comprehensive source-to-music orchestration.
- **Phase 10 — partial.** State comparison, issue explorer, timeline by publication dates, but not complete replay or analytical comparisons.
- **Phase 11 — not started.** Election-night result mode MUST stay disabled until authentic returns are available.
- **Phase 12 — partial.** Local HTTP, unit and desktop/mobile browser interaction tests; production site not deployed and external API verification blocked.

## Current release scope
- Poll observations: **10** published-source measurements, 5 national and 5 state-specific (Georgia 1, Michigan 3, Texas 1). Contains no forecast, no primary result and no fabricated candidate vote totals.
- Debates: **1** linked verified reported event.
- Map: all **51** jurisdictions navigable; offline accurate state-border linework and selectable points; online full polygons depend on a public atlas CDN.
- Scheduled data worker: coded, run in failure-safe mode locally, not yet scheduled in user's GitHub account.
- Live operations: **NOT deployed**; no external provider succeeded in this environment.

## Tests
- `pytest tests/test_pipeline.py`: 9 passing.
- Desktop/mobile Chromium in-memory interactive checks: nav, data, poll drilldowns, issue selection, themes, sound, source health passed; the browser environment blocked HTTP navigation, though local FastAPI HTTP routes returned 200.
- `node --check`: passed.

## Acceptance criteria outstanding
- Confirm a genuine network-based PollResults/VoteHub successful ingestion on GitHub Actions.
- Publish GitHub Pages URL from an authenticated repository.
- Verify whether hosted US Atlas downloads full polygons and visual quality in a real public browser.
- Add sources for all states, debates, state/federal finance, legislation, voting data, verified news and historical records.
- Integrate comprehensive campaign-finance/legislative roots, post-debate analysis and election-night system.
- Run fully navigated end-to-end public-site smoke tests and accessibility automation.

**Never mark phases or sources complete because code exists alone.**

## Version 3 — visual and interactive continuation (2026-10-15)
- Preserved the running FastAPI/local website and collector, original polling snapshot, and state geography.
- Refined the site palette with rose quartz, mint, orchid, amethyst and warm gold. Added Rose Quartz, Enchanted Spring, and Orchid Twilight art-studio choices: nine total art presets.
- Added responsive Money Rain finance and Election Night exploration screens. Both deliberately remain in clearly labeled no-data status unless traceable sourced records are ingested; these are **interfaces, not functioning finance/results feed connections**.
- Added ambient, musical and minimal soundscape selection to the existing opt-in synthesis engine.
- Validation: 9 backend pytest tests passed; existing Chromium desktop/mobile interaction checks passed; newly added finance/results/theme/audio Chromium tests passed at 1440px and 390px; JavaScript syntax check passed.
- Pending: production live API validation, FEC ingestion, legislative ingestion, wider state survey coverage, hosted jobs, publicly deployed site, true live results and end-to-end audio hearing review. Project remains partial relative to the 13-phase specification.

## Version 4 milestone — finance adapter and public-news exploration
- New Fireflies tab for genuine GDELT news metadata (once retrieved); no fake national voter sentiment.
- New privacy-conscious OpenFEC 2026 candidate summary endpoint adapter in `worker/collect.py`, bounded pagination, per-source failure tracking, optional GitHub Actions secret.
- Financial aggregate amounts are displayed as candidate-cycle summary receipts and disbursements, not transaction rainfall. No personal political profiles.
- Expanded to 12 backend tests, all passing. New finance/news desktop and mobile Chromium tests passed at 1440px and 390px with isolated test fixtures. Existing v3 browser tests passed.
- Remaining: Verify external API retrieval in user-controlled network, deploy repository, increase FEC pagination/coverage carefully, build official legislative/ballot adapters, structured debate sourcing, accurate election returns feed, full accessibility and performance audit, and public Pages validation.

## Version 5 — Botanical layers on national map (2026-10-15)
- Added map overlays and sidebar toggles for finance droplets, news fireflies, debate butterflies, and legislative leaf symbols; symbols display only for stored source-linked, dated, state-associated records.
- Added issue-root vines between displayed polls sharing an actual issue taxonomy label (no fabricated relationships).
- The documented Michigan debate appears as a butterfly where geometry is available; no finance/news/legislative marks appear when imports are empty.
- Layer filtering respects selected state and historical replay date. Poll-layer toggling no longer suppresses other record layers.
- Added map-source detail inspection and status legend.
- Verified JavaScript syntax and automated Python tests. Browser automation attempt blocked by browser network administrator rule in this environment; live visual verification is outstanding.
- Autonomous public hosting and actual FEC/poll connectors still not externally verified.


## Version 6 — Government feeds and official debates
- Added Congress.gov 119th Congress legislation collector and federal-only Understory view, with national map integration via existing legislative layer.
- Added three sourced Georgia 2026 official debate/schedule records; displayed as butterflies with attendance limitations labeled.
- Existing PollResults.org/VoteHub/GDELT/FEC adapters retained; scheduled GitHub Pages workflow now accepts Congress.gov key.
- 20 unit/integration tests passed, JavaScript syntax checked.
- **Blocked:** External DNS in sandbox; live API end-to-end verification not possible. Public GitHub deployment not attempted without repository authorization.
- **Not complete:** All-state debates, official state-level legislative adapters, verified recurring hosted ingestion, real election returns.

## Version 7 continuation — 2026-10-15

- Implemented `worker/audit.py` to validate snapshot publication and added it before and after scheduled ingestion in GitHub Actions.
- Added atomic quality gate in `worker/collect.py` before replacing stored JSON.
- Tightened polling feed status: no fresh verification from an old `last_success` timestamp; client also checks snapshot age.
- Added `tests/test_v7_audit.py`. **26 Python tests passed**; JavaScript syntax validated.
- API reachability tested from this build environment; DNS resolution failed. Real external provider calls still **not verified**, therefore live integrations must not be labeled operational until a GitHub Actions run succeeds.
- GitHub Pages has not been published: project owner must authorize creation/upload to a public repository and run its Actions workflow.

## Version 8 — 2026-10-15, navigation and source-grounded Q&A

- Implemented five pairwise dropdown menus, two related destinations in each, and a prominent Ask the Garden section.
- Implemented free in-browser evidence retrieval over the current published poll, finance, legislative, debate and news snapshot. Three selectable answer-detail levels, original source links, state scope and historical cutoffs.
- Added local-only optional Ollama generative Q&A with server-side evidence retrieval, nonpartisan prompt safeguards and automatic fallback when the model is absent. Public hosting remains static: this must not be described as live hosted AI.
- Added safe import utility to carry the user's previously collected records from an existing V6 directory into V8 without modifying or deleting the old project.
- Verified browser interaction in local in-memory Chromium on desktop and mobile; added Python and JavaScript coverage. The original dataset has only 10 polls; the user's actual expanded dataset must be imported on their Mac to enable answers based on those new records.
- No new external political API connectors added in this release; existing FEC, Congress, PollResults and GDELT status remains as previously documented. Public deployment has not been verified.


## Version 9 — State legislation, pending live-key verification
- Added OpenStates v3 adapter using `OPENSTATES_API_KEY` in a request header, bounded pagination, genuine state/DC API-jurisdiction matching, original bill link/date/action preservation, deduplication and action-revision detection.
- Default GitHub Actions job queries four rotating state/DC jurisdictions per 2-hour cycle, to keep $0 research usage bounded. Explicit state and `all` options available.
- Updated Legislative Understory, Ask the Garden evidence attribution, state map leaves and state legislative coverage reporting.
- Added OpenStates GitHub Actions secret forwarding and automated tests for the adapter, no-key behavior, validation and non-duplicating updates.
- **Still required:** Real key-based OpenStates import must run successfully on user's Mac or GitHub; public repository must be deployed. All-state ingestion is rotating *limited slices*, not a comprehensive historical archive.

## Version 10 — October 16, 2026
- Added more engaging SVG motions to existing data-linked garden features.
- Built interactive Parallel Gardens issue-filtered evidence quest, five record counters, source inspection, random pair and reset.
- Validation: JS syntax valid, 35 focused Python tests passed, local HTTP 200. Browser visual validation remains pending because Chromium browser binary was not installed in this session.
- No new source integration or hosted deployment is claimed by this release.

## Version 11 — Cottage Garden and Parallel botanical exhibit (2026-10-16)
- Redesigned the working application as a floral field guide with natural, non-neon colors, warm editorial typography, original SVG hero wildflowers, cream paper panels and a calmer national garden map. Existing provider integration code, navigation and Q&A retained.
- Replaced Parallel Gardens counts-only cards with two complete interactive illustrated flower beds. Only source-linked records receive data symbols; decorative landscape cannot be confused with poll or finance activity.
- Added evidence ledger, record-specific detail views, field notebook, state selectors, random pair selection, issue filter, quest controls, keyboard access and reduced motion.
- Verification: 40 Python backend/integration tests, 9 JS Q&A tests, local HTTP 200 and 1440px/390px Chromium interaction checks passed using the real website code with a bundled offline snapshot. External API ingest and public Pages deployment **not retested** here.
- Update project ZIP and documentation; future phases still include comprehensive all-state feeds and publishing via GitHub.


## Version 12 — Map geography and motion containment

- [x] Separated fixed flower geographic anchors from CSS-driven motion.
- [x] Added 51 precise state-boundary clip paths in the SVG renderer when validated topology is available.
- [x] Created deterministic interior placements for state-linked polls, FEC raindrops, news, debates and state bills.
- [x] Constrained issue vines to share both documented issue and state.
- [x] National-only poll measurements no longer draw over an arbitrary individual state.
- [x] Balanced nationwide bloom sampling for map legibility; Pollarium continues to retain source records.
- [x] Added local TopoJSON cache tool, Mac startup integration, and GitHub Actions cache step.
- [x] Maintained labeled nonmoving centroid fallback for offline map conditions.
- [x] Regression-tested geographic clipping with 51 synthetic test-only polygons in Chromium, at desktop/mobile sizes.
- [ ] Confirm a live download and rendering of authentic us-atlas topology on the user's Mac and public GitHub site; sandbox network DNS prevents direct verification.
- [ ] Public GitHub Pages URL and scheduled collector deployment remain to be verified under the user's account.

## Version 13 — October 16, 2026 · Harvest and public-launch reliability

- [x] New **Harvest Journal** with source-linked record changes, provider name, ingestion timestamp separate from original publication date, per-type filtering, and clickable evidence. The journal appears on the homepage but empty states remain honest.
- [x] Collection worker writes a bounded 250-entry changelog **only** when a source record is first added or materially revised. Repeated unchanged fetches cannot create phantom bloom events. Source provenance and timestamps are audited.
- [x] Observatory source statuses show full checked/succeeded timestamps and errors rather than an ambiguous "just updated" label.
- [x] Federal FEC and Congress.gov credentials moved to authenticated headers, not URL query parameters. Existing API integration tests adapted and passed.
- [x] Scheduled GDELT runs reduced to six-hour UTC boundary cadence to moderate known HTTP 429 responses.
- [x] Offline deployment doctor checks 51-state identity, source audit, GitHub workflow structure and a realistic nested-path local HTTP Pages simulation.
- [x] Mac start script chooses first free port among 8000–8003 to eliminate common local binding conflicts.
- [x] `.venv/` explicitly ignored by Git before committing to public repository.
- [x] Desktop and mobile Chromium test of Harvest filters, source-inspection interaction, Observatory health and no frontend errors with a test-only ingestion event.
- [ ] **Not yet verified:** Actual public GitHub Pages deployment, scheduled remote ingestion and continued free hosting under a user-controlled repository.
- [ ] **Not yet finished:** State election returns, all-state official debates and additional online conversation feeds; these will require source-specific permitted integrations and, where appropriate, credentials/licensing.

## Version 14 · Civic Garden Quest

- Seven interactive learning chapters in the real website; includes polls, debates, FEC finances, lawmaking, voting and certification.
- Paired Learn & Play navigation; progress blooms, local completion stamps, state/issue-scoped original evidence.
- No new ingestion sources or credentials required.
- Local backend collection remains unchanged; public GitHub deployment remains unverified.
- Browser and game-logic tests added; see docs/V14_RELEASE_NOTES.md.

## Version 15 — The Stories We Grow (2026-10-17)

- [x] Replaced quiz-based Civic Garden Quest with a three-character choice-driven storybook.
- [x] Added Maya (housing and rent), Jordan (debate reporting), Elena (school transportation and policy) as fictional characters in fictional towns.
- [x] Each narrative offers multiple scenes, character dialogue, meaningful choice effects and three reachable endings. Undo, restart, separate saves per character and simple/detailed story modes supported.
- [x] Natural cottage illustrations, characters and botanical stage art on desktop/mobile; reduced-motion controls preserved.
- [x] Real independently imported evidence appears only in a clearly separated, source-linked panel; state geography and historical cutoffs preserved.
- [x] Removed previous quiz code and updated GitHub Actions regression checks.
- [x] New graph/branching/evidence tests and browser interaction checks at 1440px and 390px with offline published snapshot.
- [ ] Actual public GitHub deployment remains unverified; API imports remain the same as Version 14.
- [ ] The ZIP’s bundled source snapshot is the small baseline; the user's latest collected records must be imported locally.


## V17 map rollback
Reverted only the national/state SVG artwork and animation to the pre-state-lock Version 11 implementation. See docs/V17_RELEASE_NOTES.md. Modern game and non-map functionality preserved.

### Version 17 verification
- 49 Python tests passed, 2 obsolete V12 state-clipping checks skipped after intentional rollback.
- 14 Node tests passed.
- Chromium desktop/mobile tests passed for restored map controls and current branching story.
- Local HTTP checks passed. External API collection not rechecked.

## Version 18 — Public launch readiness (2026-10-17)
- [x] Preserved original pre-state-lock map and branching narrative.
- [x] Added public deployment status manifest and Source Observatory status.
- [x] Updated GitHub workflow to publish audited datasets even if optional APIs fail; persist snapshots non-blockingly afterward.
- [x] Added static nested-URL and build manifest tests, explicit $0 publishing and security walkthrough.
- [ ] User account: create/publish repository and confirm actual public GitHub Pages URL.
- [ ] User account: add rotated secrets and confirm remote provider access, data changes and automatic scheduled runs.
- [ ] Verify the published URL on actual user devices. Do not claim hosted success from offline tests.
