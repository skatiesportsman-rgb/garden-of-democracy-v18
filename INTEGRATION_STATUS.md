# INTEGRATION_STATUS — initial development release

| Source | Role | Current status | Reason / next check |
|---|---|---|---|
| Fox News published polling reports, dated June–October 2026 | Initial published observations | **VERIFIED PUBLICATION; 10 measurement records entered** | Linked original article with methodology. This is curated content, not live API. |
| PollResults.org public API (`api.pollresults.org/v1.0`) | 2026 election polling | **DOCUMENTED; RUNTIME UNAVAILABLE** | API pages and endpoint are real. Container DNS blocked; run on GitHub Actions, verify schema and license. |
| VoteHub public polling API (`api.votehub.com/polls`) | Surveys / generic ballot | **DOCUMENTED; RUNTIME UNAVAILABLE** | Beta; verify production host/schema after deployment, never silently reuse newer credentialed endpoint. |
| GDELT DOC API | News article metadata | **DOCUMENTED; RUNTIME UNAVAILABLE** | Authorized article metadata, not opinion. Verify response and rate limits online. |
| FEC OpenFEC | Campaign finance | **CREDENTIALS REQUIRED / NOT IMPLEMENTED** | Obtain free developer key from FEC API site before implementing source-specific adapter. |
| Congress.gov API | Federal legislation | **CREDENTIALS REQUIRED / NOT IMPLEMENTED** | Request free key from Congress.gov. |
| OpenStates v3 | State legislation | **CREDENTIALS REQUIRED / NOT IMPLEMENTED** | Check enrollment and coverage. |
| 50 states + D.C. | Geospatial identity | **LOCALLY VERIFIED** | 51 unique codes, bundled state boundary lines. Full SVG polygons via US Atlas CDN unverified online. |
| MIT Election Data and Science Lab | Historical comparison | **RESEARCH ONLY** | Reuse permissions/data availability must be reviewed before import. |
| State election authorities | Early vote and official results | **NOT IMPLEMENTED** | State-specific feed licensing/access; no votes before official result reporting. |
| Supabase Postgres | Optional DB mirror | **SCHEMA/ADAPTER READY; CREDENTIALS MISSING** | Requires free Supabase project and `DATABASE_URL` GitHub secret. |
| GitHub Actions + Pages | $0 publishing/schedule | **WORKFLOW IMPLEMENTED; NOT DEPLOYED** | User must create public GitHub repository; real-run testing pending. |

Source health displayed in the site snapshot is updated after each run. Missing source data does not become zero public opinion.

## Continuation source check (2026-10-15)
- VoteHub documents a free, CC BY 4.0 polling beta endpoint at `https://api.votehub.com/polls`. A separate `polling.votehub.com` service documents API-key authorization; the two must not be conflated. Public beta remains the current worker target.
- PollResults.org documents 2026 Senate, House, and governor feeds and cursor pagination. Direct network run from the isolated environment remains blocked; no claim of successful ingestion.
- OpenFEC officially provides `DEMO_KEY` for exploration and free developer API-key registration for higher use limits. Production FEC adaptation is not yet implemented.

## Version 3 safeguards
Money Rain and Election Night now have navigable UI screens; both remain unpopulated and are **not integrated live providers**. Neither interface fabricates a transaction or election result. PollResults/VoteHub remain unverified for automated remote collection in this environment. The local dated snapshot is not labeled real-time streaming.

## Version 4 — 2026-10-15
- **OpenFEC candidate totals (2026):** API documented and bounded adapter implemented. `FEC_API_KEY` required; API response **not reached** due sandbox DNS restriction; not operational as shipped. Does not collect individuals' donations or infer state from candidate names. On missing key the collector records `credentials-required` and retains existing snapshot.
- **GDELT Fireflies:** The existing article-metadata adapter is now exposed through a dedicated interactive Fireflies section. The API remains runtime-unverified. News is not labeled as survey opinion.
- **GitHub Actions:** Workflow now passes optional FEC key from a GitHub Actions secret. Cannot verify deployment without a repository the user controls.
- **Polling:** Existing real published survey snapshot preserved; external polling API integration still unverified from this environment. Missing evidence remains missing.


## Version 6 integration status (2026-10-15)
- Congress.gov **implemented, locally unit-tested, not live-verified**. Set `CONGRESS_API_KEY`. Its federal bill actions appear in Legislation and national map leaves. No state inference.
- FEC **implemented previously, locally unit-tested, not live-verified**. Set `FEC_API_KEY`. Only cycle-to-date candidate aggregates appear.
- PollResults/VoteHub **implemented previously, external runtime connectivity unverified**. PollResults documents a free public API; do not call the adapter operational before it returns parsed polls.
- GDELT **implemented previously, remote connectivity unverified**. Debates remain source-linked curated records; automatic debate discovery is not yet validated.
- GitHub Pages **workflow configured, no public deployment verified**. An authorized GitHub repository is necessary to activate it.

## Version 7 deployment verification notice

Static deployment is configured but **not remotely verified**. Current environment cannot resolve the external polling or FEC hosts. Do not infer operational provider status from connector code alone. Inspect a successful hosted Actions run and the generated `site/data/snapshot.json` source health records to establish true availability.

## V8 optional question assistant integration

- **Browser evidence Q&A:** operational with the bundled records; entirely client-side on GitHub Pages. Generates constrained source-derived summaries without a language model.
- **On-device Ollama AI narration:** integrated, but **requires optional user installation and local model download**, and is not verified active on the user's Mac. No credentials or paid subscriptions required. Backend `POST /api/ask` returns unavailable rather than inventing a model response when Ollama isn't enabled or there's insufficient evidence.
- **Public AI inference:** not integrated, not advertised as operational. GitHub Pages cannot run Python/Ollama in production on its static web host.


## Version 9 — Plural Open / OpenStates
- API v3 `/bills` implementation **coded and unit-tested; awaiting a successful key-authenticated external runtime request**. Uses `X-API-KEY` header and `OPENSTATES_API_KEY` environment variable, never a query string key.
- 50 states plus Washington, D.C. supported with explicit source jurisdiction validation; no geolocation guesses.
- Default 4-state rotation per 2-hour scheduled run; data availability is dependent on API quotas, returned bill metadata and run completion.
- Secret forwarded by GitHub Actions on deployment; public GitHub Pages site not yet deployed or verified.


## Version 12 geometry delivery

- `us-atlas@3` state Albers TopoJSON: documented URL, strict 51-jurisdiction identity validation, local cache and CDN fallback implemented; remote fetching **unverified** in this offline build environment. It is not a political observation API.
- GitHub Actions now runs the optional geometry cacher before packaging. This deployment remains **unverified** until the owner publishes and runs the workflow.
- Polling/FEC/Congress/OpenStates API integrations remain as previously recorded; do not treat local test success as fresh live API evidence.

## Version 13 — verified local engineering, not remote API status
- FEC + Congress.gov: Existing source adapters now transmit keys using `X-Api-Key` headers, aligned with the api.data.gov documented approach. Local mocks/tests pass. The user's prior local Mac import succeeded, but **this container has not successfully made the external key-bearing API calls**.
- OpenStates: State bill adapter and four-state scheduled rotation preserved; the user's particular key is not included in the distribution. Live connection from the current environment remains unverified.
- GDELT: Included on 6-hour UTC boundaries instead of every 2-hour GitHub Actions run; prior 429 was reported by user's Mac, not misclassified as a successful import.
- PollResults + VoteHub: Existing public-feed collectors and dated original records preserved. Remote collection on GitHub Pages infrastructure not yet verified.
- GitHub Pages + Actions: Workflow, local preflight and nested-path HTTP test **verified locally**; an actual GitHub repository and live deployment run are still required to establish a shareable URL and operational scheduled updates.
- Harvest Journal: Deterministic ingestion changelog implemented; records saved only when new/revised data arrives. Does not claim that the sample 10-poll snapshot has undergone any new ingestion events.

## Version 14 educational game

Civic Garden Quest: **IMPLEMENTED, client-side.** Uses the existing stored political snapshot only; no extra external API. Classroom activities are separated from verified political records. Local Browser progress only. Public-hosting verification remains pending.

## Version 15 storytelling engine — local interactive module

**IMPLEMENTED AND LOCALLY TESTED.** The Stories We Grow is a no-key, client-side branching fictional narrative. Three characters, multiple real-feeling scenes, three attainable endings each, history rewind, browser-only progress, original SVG portraits, desktop/mobile browser tests, and optional source-linked records from the existing published snapshot. Fictional story events are not promoted into real-data layers. No new provider connection, external language model, public deployment or hosted automation is claimed by this module. The earlier quiz module was removed.

## Version 18 hosting integration
- **GitHub Pages deployment:** implemented; locally validated (static nested path); NOT publicly deployed/verified.
- **GitHub Actions scheduled polling/FEC/Congress/OpenStates:** configured, local collector code tested; remote scheduled runs/credentials NOT verified in this session.
- **Public Source Observatory build manifest:** implemented; offline browser tested; no source freshness is inferred from website load time.
- **Optional PostgreSQL mirror:** implemented interface only. No free remote database has been provisioned under the $0 budget.
