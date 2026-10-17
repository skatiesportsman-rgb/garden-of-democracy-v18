> **Version 18 public launch:** Start with [docs/V18_PUBLIC_LAUNCH.md](docs/V18_PUBLIC_LAUNCH.md). The launch workflow is locally tested, but no actual GitHub Pages URL is claimed until you publish it.

# The Garden of Democracy — Version 15: The Stories We Grow

**NEW: A branching interactive storybook replaces the quiz-based Civic Garden Quest.** Three original fictional characters and their situations illustrate real kinds of civic decisions. The local garden, nationwide geographic map, source-backed flowers, state legislation, Parallel Gardens, source observatory, collector and Ask the Garden remain in the same project.

### Play the new stories

Choose **Learn & Play → The Stories We Grow** in the top navigation or click **Step into a story** beneath the national map. Choose:

- **Maya Patel** — a student in fictional Willow Creek, Georgia whose rent rises unexpectedly. Her choices follow housing conversations, polling, a possible city hearing and campaign claims.
- **Jordan Ellis** — a student journalist in fictional Harbor Point, Michigan covering a clipped debate video; the plot changes depending on how Jordan gathers and communicates evidence.
- **Elena Rivera** — a parent and shopkeeper in fictional Pine Hollow, North Carolina facing a changed school bus stop, learning the separate roles of school boards, state legislatures and election administrators.

Click an action to change the next scene. Dialogues, subsequent paths and attainable endings respond to decisions. **No quizzes, correct political answers, winning-party rankings or simulated election totals.** Each character has at least three reachable, differently written endings. Use **Undo last choice**, **Start over**, or choose another character. Choose **Story only** or **Story + civics notes** for different reading depth. Individual story progress is saved only in the visitor's browser when local storage is available.

Illustrations and places are original fictional story elements. All named characters and specific described events are fictional, not 2026 claims. The optional **Show real records** panel opens independently sourced polls, debates or legislation from the garden's currently imported dataset; it never claims a fictional character attended a documented debate or influenced a real bill. State-only sources remain in their original state, historical cutoffs are respected and missing records are labeled. The story can be completed without an API key or AI model.

### Start it on your Mac

1. Download and unzip Version 15 into its own folder, leaving earlier versions untouched.
2. Open Terminal inside the extracted `garden-of-democracy-v15` folder.
3. If you have already collected political records, import the **newest verified** snapshot from the old folder *before* starting Version 15:

   ```bash
   python3 tools/import_existing_snapshot.py "$HOME/Downloads/garden-of-democracy 6/site/data/snapshot.json"
   ```

   Replace that path with your newest version's `site/data/snapshot.json` if your later version has more complete data. Keep the old folder as a backup.
4. Run `bash start.command` and follow the automatically printed URL (typically `http://127.0.0.1:8000`; ports 8001–8003 are automatically attempted if busy). Leave Terminal open.
5. Open **Learn & Play → The Stories We Grow**. Your old quiz progress is not used by this new independent storybook.

### Tests

- `node --test tests/test_ask_garden.mjs tests/test_v15_stories.mjs` checks existing source-grounded question answering and new narrative graphs, three reachable endings per character, proper branching and rewind, unsafe links, state specificity and date cutoffs.
- `python3 -m pytest tests/test_v15_browser.py -q` verifies real website code and native browser interactions in Chromium at desktop (1440px) and mobile (390px) with bundled source-linked records, with no external political-feed requests.
- CI `.github/workflows/deploy.yml` now checks `site/civic-story.js` and the new story tests instead of deleted quiz code.

**Not yet done:** Public GitHub Pages publication and hosted scheduled-collector verification still require a repository owned by the user; no shareable URL has been fabricated. Public Pages includes the no-cost interactive fictional storybook; it does **not** run a continuously hosted Python or Ollama model.

See [Version 15 release notes](docs/V15_RELEASE_NOTES.md) and [the GitHub publishing guide](docs/GITHUB_PUBLISHING.md).

---

# ✺ The Garden of Democracy
**A Living Portrait of American Public Opinion · 2026 Midterm Elections**

A working, nonpartisan creative-data website. Accurate 50-state and District of Columbia coverage is selectable even where no state polling is collected. Documented polls become individually inspectable flowers; the atmosphere moves without fabricating political developments.

## Run the website locally (Mac / Windows / Linux)

Install Python 3.11+ and then, from **inside this project folder**, run:

```bash
python -m pip install -r requirements.txt
python -m uvicorn server:app --host 127.0.0.1 --port 8000
```

Open the local URL printed by the startup script (normally **http://127.0.0.1:8000**, or 8001–8003 if an earlier server is still running). Leave the terminal open while exploring. The API is at `/api/snapshot`, polling at `/api/polls`, and health at `/health`.

**No keys are needed to explore the initial website.** There are **10 sourced, dated observations** seeded from contemporary published polling reports, including state-level polls for Georgia, Michigan and Texas. These are **not** an automatic live-API sync, and the UI displays the difference. The original published-source link for every measurement is inspectable. No state-specific poll value is invented when none is available.

### Run the collector independently

```bash
python worker/collect.py --max-pages 2
python worker/coverage.py
```

The collector uses documented VoteHub and PollResults endpoints and the GDELT DOC API. Network access is required. Data remains in `site/data/snapshot.json` and local SQLite cache `data/garden.sqlite`. If one provider is unavailable, **old verified records remain** and the provider's visible status becomes `temporarily-unavailable`. The local API exposes a Server-Sent Events endpoint at `/api/events` and the frontend also polls the snapshot every five minutes. The bot is an independent process; opening the site is not required to run it.

To inspect the interface completely offline, use `python tests/browser_check.py` (requires a Chromium installation and the Python `playwright` package). This checks actual JS interactions against verified snapshots but **does not** count as live provider connectivity.

## Publish publicly for $0 — GitHub Pages + scheduled GitHub Actions

1. Sign into [GitHub](https://github.com/), create a **new public repository** (e.g., `garden-of-democracy`). Do not add API secrets to repository files.
2. Upload or push the **contents** of this folder to the repository's `main` branch. Ensure `.github/workflows/deploy.yml` is present. With a terminal:
   ```bash
   git init
   git add .
   git commit -m "Initial Garden of Democracy"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/garden-of-democracy.git
   git push -u origin main
   ```
   You'll need to create the remote repository first and authenticate to GitHub normally.
3. Go to the repository's **Settings → Pages → Build and deployment → Source: GitHub Actions**.
4. In **Actions**, enable workflows if prompted; open `Refresh civic data and publish garden` and choose **Run workflow**. Each workflow runs automated tests, refreshes data sources and publishes the static site. The schedule also runs roughly every two hours (GitHub may delay scheduled jobs).
5. Open **Settings → Pages → Visit site** after the green deployment check. For a project repository this will normally be `https://YOUR_USERNAME.github.io/garden-of-democracy/`. That example is **not a currently deployed URL**.

The deployed experience runs on GitHub Pages; scheduled GitHub Actions jobs (not a permanent server) retrieve updates and commit/republish a data snapshot. When published, the frontend checks for new snapshots periodically. **Source updates are not continuous streaming; animation continues regardless of publication rate.** Do not enable a private repo for this path if you need guaranteed $0 usage.

### Optional PostgreSQL (Supabase Free)

The $0 Pages version stores source-verified JSON snapshots in the public repository and supports a local SQLite cache. If you need an actual PostgreSQL mirror:

1. Open [Supabase](https://supabase.com/), create a **Free** project (never upgrade), and find the Postgres connection string under project settings / Connect. Prefer the IPv4-compatible session pooler if direct IPv6 connectivity fails.
2. In GitHub, set **Settings → Secrets and variables → Actions → New repository secret** with name `DATABASE_URL`, and paste the secret connection string there. **Never put this value in client JS or source-controlled files.**
3. The existing workflow detects the secret and runs `worker/postgres_sync.py`, which creates and upserts tables defined in `database/schema.sql`. The schema enables row-level security. This is an **optional mirror**; the public front end still reads the generated snapshot, so Supabase downtime cannot erase the garden.

Supabase Free can pause inactive projects after a low-activity period; it does not include managed backup guarantees, and free quotas can change. At $0, scheduled Jobs + static snapshots are the reliable baseline; a dedicated always-on paid database or worker is not required.

## Data and methodological safeguards

- The base release contains survey **measurements**, not election forecasts or actual midterm vote returns.
- Survey shares may not add to 100% if the publication omitted undecided or other categories; no residual is invented.
- National surveys remain **national**; the map's state regions do not inherit national poll results. Coverage is transparent in `site/data/coverage.json`.
- Every normalized poll retains pollster, geographic scope, source URL, population, publication date, field dates, and disclosed sampling uncertainty. Unavailable items are marked unknown rather than fabricated.
- Articles and public discussion activity do **not** measure public opinion. No personal political profiles are collected.
- Artwork's ambient particles do not represent fresh data. Verified newly ingested records can create new flowers and updated snapshots.
- Generator sound begins only after user interaction. Reduced-motion and mute options are included.

## Screens and controls

**The garden:** newly illustrated cottage-meadow national map (local accurate state-boundary line fallback; enhanced state polygons when US Atlas CDN is reachable), national and state record flowers, layers and topic controls. **Pollarium:** poll source inspections and response bars. **Understory:** issue navigation. **Conservatory:** debate catalog with source links. **Time machine:** publication-dated historical record playback selector. **Observatory:** operational source status. **Art studio:** nine natural garden atmospheres including Cottage Meadow, English Rose, Woodland Ferns, Bluebell Morning and Pressed-Flower Herbarium with intensity and sound controls. **Compare:** two animated living gardens, original-source evidence selections, notebook, record-count ledger, and meaningful educational quests, with explicit absent-data handling. **Exhibition mode:** immersive view.

### Architecture

- `site/`: deployable, framework-free HTML/CSS/JS front end with low-cost atmospheric SVG/canvas effects.
- `worker/collect.py`: deterministic source adapters, validation, deduplication, failure health and upsert.
- `worker/coverage.py`: automatic national coverage matrix.
- `worker/postgres_sync.py`, `database/schema.sql`: optional PostgreSQL persistence.
- `server.py`: local FastAPI server, SQLite cache, REST queries and SSE.
- `.github/workflows/deploy.yml`: independent scheduled data refresh / Pages deployment.
- `tests/`: API, data-methodology and in-browser interaction checks.
- `docs/`: progress, source integration status, coverage report and preview captures.

## Tests

```bash
python -m pip install -r requirements.txt pytest
pytest tests/test_pipeline.py -q
node --check site/app.js
```

Run `python tests/browser_check.py` for interactive checks (requires `pip install playwright` and locally installed Chromium). Browser tests cannot replace validation of externally hosted polling APIs.

## Verified/current providers, licenses, and limitations

- [PollResults.org API](https://pollresults.org/) — documented public 2026 House, Senate and gubernatorial feeds, CC BY 4.0 attribution; runtime was **unreachable** from the restricted initial development environment, so adapter production behavior is still unconfirmed.
- [VoteHub polling API](https://votehub.com/polls/api/) — public beta documentation, CC BY 4.0 attribution; runtime was **unreachable** from the initial development environment. Its separate newer polling endpoint can have authentication requirements; no assumption of compatibility is made.
- [GDELT DOC API](https://www.gdeltproject.org/data.html) — documented article metadata, not opinion polling; unreachable from initial runtime.
- [Fox News October 14, 2026 poll report](https://www.foxnews.com/politics/fox-news-poll-cost-living-concerns-weigh-gop-midterms), [Michigan](https://www.foxnews.com/politics/fox-news-poll-michigan-voters-split-between-el-sayed-rogers/), [Texas](https://www.foxnews.com/politics/fox-news-poll-its-lone-star-senate-showdown-between-talarico-paxton), [Georgia](https://www.foxnews.com/politics/fox-news-poll-early-look-georgia-senate-race.amp) — independently checked publication reports, used to transcribe reported numeric survey **facts** and metadata into the startup snapshot; not an automated Fox feed.
- [FEC OpenFEC](https://api.open.fec.gov/developers/), [Congress.gov](https://api.congress.gov/), [OpenStates](https://docs.openstates.org/api-v3/) — researched/planned credentialed sources, **not operational** in this version. Free keys may be requested from providers; use GitHub Actions secrets in later integrations.
- [US Atlas](https://github.com/topojson/us-atlas) — Census-derived boundary map loaded only when external asset reachable; bundled Basemap-derived US state border lines provide offline geographic continuity.

See `INTEGRATION_STATUS.md`, `DEVELOPMENT_PROGRESS.md`, `docs/TEST_REPORT.md` and source registry. No mock results, unsourced electoral forecasts, or claim of a public deployment has been made.

### $0 budget statement

| Component | Selected approach | Recurring expense |
|---|---|---:|
| Public website | GitHub Pages, public repo | $0 |
| Scheduled collectors | GitHub Actions, standard public-repository runner | $0 under stated free usage rules |
| Primary published storage | Versioned, source-verified JSON in public repo | $0 within repo/Pages limits |
| Local durable cache | SQLite | $0 |
| Optional PostgreSQL | Supabase Free (subject to quotas and pausing) | $0 |
| Poll data | Public APIs, CC BY attribution | $0 for permitted use |
| Sound and graphics | Native browser APIs + SVG/canvas | $0 |
| Domain | GitHub Pages included subdomain | $0 |

No paid dependency is used. Hosting provider policies and free quotas may change; actual public deployment requires a repository under an account you control.

### Historical publication-date replay (continuation)

The **Time Machine** now selects real publication dates in the local snapshot, not a percentage of records. Choose a date, then **Explore garden at…** to view only source records published by that cutoff. **Return to latest published data** clears the filter. This is an archive, not predictive election modeling or a substitute for the live feed.

## Version 3: switching from an older running Mac version
1. Stop the existing local server by returning to its Terminal window and pressing **Control-C**.
2. Unzip `Garden_of_Democracy_v3.zip` and open the **new** `garden-of-democracy` folder in Terminal (use `cd ` followed by dragging the new folder into Terminal).
3. Run `python3 -m venv .venv && source .venv/bin/activate`.
4. Run `python -m pip install -r requirements.txt eval-type-backport` (helps with older Python 3.9 annotation handling).
5. Run `python -m uvicorn server:app --host 127.0.0.1 --port 8000` and visit `http://127.0.0.1:8000`.
6. Reload Safari with Command-R; if it has cached styling, use Command-Option-R.

**Version 3 scope:** Nine color themes, configurable audio modes, source-honest election-night and finance views. These extra views have no financial returns or election returns until verified feeds are implemented. The previously configured polling collector remains available as `python worker/collect.py --max-pages 2` in a separate Terminal window, but internet feeds are not guaranteed operational.

## Version 4 — finance collection + Firefly Observatory

The site now includes the **Fireflies** tab, which displays GDELT article metadata without describing it as representative public opinion. The national-only classification is intentional: article mentions do not establish the reader's or publisher's home state. The site also has an FEC 2026-cycle candidate **aggregate** receipts/disbursements adapter for Money Rain. Aggregates represent already reported totals as of the data fetch—not new donations or real-time transactions. The collector does not pull individual contributor profiles.

### Enable federal campaign finance on a $0 budget

1. Visit https://api.open.fec.gov/developers/ and request a **free** OpenFEC developer API key.
2. For a local Mac collection run (with the `.venv` active), supply the key only in Terminal:

   ```bash
   read -s FEC_API_KEY; export FEC_API_KEY
   python worker/collect.py --providers fec --max-pages 2
   unset FEC_API_KEY
   ```

   At `read -s`, paste the key and press Return. The key will not echo. This command fetches at most two 100-record pages, so the data is a **bounded partial national list**, not exhaustive national finance coverage. Rerun against the provider's current API contract if any schema changes.
3. Refresh the site to see successfully fetched candidate totals. If you later deploy on GitHub, add `FEC_API_KEY` under repository **Settings → Secrets and variables → Actions**. Never commit keys or paste them into `site/`.

### Collect news metadata

```bash
python worker/collect.py --providers gdelt
```

Only when network access succeeds will Fireflies display fetched news metadata. Its date, provider, article URL, and topic are shown. This is **news coverage**, not voter sentiment. Network calls from the artifact creation environment are blocked, so external ingestion cannot currently be claimed tested.

### Local updates and hosting

Start with `python -m uvicorn server:app --host 127.0.0.1 --port 8000`, then browse `http://127.0.0.1:8000`. A running site does not itself perform unattended background collection: start the collector separately, or publish this repository with its existing GitHub Actions workflow. The GitHub Pages site is static; it loads data refreshed by scheduled Actions runs. GitHub Actions scheduling can be delayed or suspended by GitHub. An optional Supabase database is supported but not necessary for the public Pages site. Public publication cannot be completed from this archive without permission to a GitHub repository.

### Tests for this release

```bash
python -m pip install -r requirements.txt pytest playwright
pytest -q tests/test_pipeline.py
node --check site/app.js
python tests/test_v3_browser.py
python tests/test_v4_browser.py
```

The browser scripts require a Chromium executable at `/usr/bin/chromium` in the test environment. They use a mocked transport with the actual site files, and Version 4 injects **test-only** news/finance records without writing them to the release snapshot.

### Version 5: Living map layers
On **The garden** page, toggle **Poll flowers**, **Issue roots**, **Fireflies**, **Money rain**, **Debates**, and **Legislation** independently. Every data mark links to a stored record and its original source; click the symbol to inspect it. Vines link polls sharing the same recorded issue category and **do not** imply the surveys have comparable samples or results. Rain, news and legislative elements appear only after genuine data has been collected for a known state; **empty layers are expected before their integrations succeed**. Ambient background movement is decorative, not a data event. Use Time Machine for date-bounded exploration.


## Version 6: Activate government feeds ($0)
1. Request a free key at https://api.open.fec.gov/developers/ and another at https://api.congress.gov/sign-up.
2. In local Terminal, `export FEC_API_KEY='your-key'` and `export CONGRESS_API_KEY='your-other-key'`. Never paste your real keys into the website or upload them to the repository.
3. Run `python worker/collect.py --providers pollresults,votehub,gdelt,fec,congress --max-pages 2`. It preserves cached records if any source fails.
4. Restart or refresh your local garden. Click **Legislation** for official federal bill actions. Open **Sources** for actual provider statuses.
5. On GitHub, create a **public** repository, add all project files, then Settings → Secrets and variables → Actions → New repository secret. Add each key under its exact environment variable name. Under Settings → Pages choose **GitHub Actions** as source. Push to `main` or run the workflow manually.
6. Scheduled GitHub Actions refresh is best effort, not a guaranteed real-time stream; the public Pages site serves a newly published static snapshot. The Python/FastAPI server runs locally only and is not hosted by GitHub Pages.

**Status:** Internet DNS is restricted in this build container, so none of these external ingestion calls or public publishing can be truthfully marked successful yet.

## Version 7 — publication safety and $0 deployment preflight

Version 7 adds a production snapshot audit (`worker/audit.py`) and publication gate to the existing collector and GitHub Actions workflow. A malformed incoming record cannot overwrite the last verified published snapshot. It checks unique IDs, valid states, HTTPS evidence links, publication dates, and polling response values. A successful polling feed older than 36 hours is no longer called *recent verified feed*; that label describes ingestion freshness, **not** the age of the underlying survey's fieldwork.

Before pushing to GitHub:

```bash
python -m pip install -r requirements.txt pytest
python worker/audit.py
python -m pytest tests/test_pipeline.py tests/test_v5_layers.py tests/test_v6_integrations.py tests/test_v7_audit.py -q
node --check site/app.js
```

If the collection worker cannot reach a feed, open the GitHub Actions logs after a manual dispatch to see the source failures. **Never add `FEC_API_KEY`, `CONGRESS_API_KEY`, or `DATABASE_URL` to checked-in files.** For FEC and Congress.gov, place any keys you obtain under the repository's **Settings → Secrets and variables → Actions** with those exact names. The website can run without them, but the corresponding records cannot be imported.

To publish, first create a **public** GitHub repository under an account you control, then push this project's files and select **GitHub Actions** as the Pages build source. Navigate to **Actions → Refresh civic data and publish garden → Run workflow**. Wait for green checks and use **Settings → Pages → Visit site** for the actual URL. If the workflow fails, the code and failed log are available locally; the public URL is **not** established until Pages confirms a successful deployment.

> The website's published static data does not require a live Python server. The Python server is only for development. GitHub Actions supplies *scheduled* collector runs subject to free-tier limits and scheduling delays, not nonstop 24/7 streaming. The free PostgreSQL mirror is optional and does not power Pages directly.

---

## Version 8 — Simpler navigation and Ask the Garden

**Changes:** Instead of ten links across the header, five compact dropdowns have exactly two destinations each:

| Top menu | First destination | Second destination |
|---|---|---|
| Explore | Living Garden | Pollarium |
| Policy | Issue Roots | Legislation |
| Campaigns | Debate Butterflies | Money Rain |
| Conversation | Fireflies | Source Observatory |
| Through Time | Time Machine | Election Night |

There is one separate, highlighted **Ask the Garden** button for the source-grounded question companion. Keyboard users can tab to each menu and press Return/Space to open it, or Escape to close it.

### Ask the Garden: free evidence answers and optional on-device AI

The public, static GitHub Pages website works **without any AI subscription or server**. It searches the site's published `site/data/snapshot.json` and returns explicitly labeled **evidence summaries** with links to original source records. Visitors can choose:

- **Simple:** shorter explanations with a small set of dated examples.
- **Standard:** more supporting observations and important context.
- **Detailed:** expanded responses, fieldwork details and survey methodology where available.

These offline summaries are a deterministic evidence-search feature, **not a generative AI model**. They deliberately refuse unsupported predictions, distinguish surveys from votes, and never manufacture missing state data.

For **actual language-model narration** on your Mac, an optional **Ollama** integration is included. It runs entirely on your computer and uses the backend to retrieve a bounded set of public source records. No political-data API key is needed for the question companion itself.

1. Install Ollama for macOS from <https://ollama.com/download> (free). Check device capabilities before downloading a model.
2. Open a separate Terminal window and enter: `ollama pull gemma3:1b` (model files can require substantial free disk space). Start Ollama, for example with `ollama serve` if not already running in the background.
3. In the Garden project directory, activate your virtual environment: `source .venv/bin/activate`.
4. Start the Garden server with local AI enabled:

   ```bash
   GARDEN_ENABLE_OLLAMA=1 GARDEN_OLLAMA_MODEL=gemma3:1b python -m uvicorn server:app --host 127.0.0.1 --port 8000
   ```

The interface will show **Local AI explanation** only when Ollama actually responds. If it is not installed, is loading, or fails, the site gives the cited evidence summary instead. An LLM can still be mistaken: always use the source links to verify important claims. Ollama stays on localhost; the public GitHub Pages site cannot access your Mac's local model. To offer public generative AI at $0 would require separate publicly accessible inference capacity that is **not included** in this release. Do not advertise it as enabled on GitHub Pages.

**Data privacy:** Questions are processed locally in the browser in fallback mode. If Ollama is enabled, the question and selected public evidence go only to the local Garden server and local Ollama API; no outside AI provider receives them. There is no chat-history account or political profiling.

### Crucial: preserve the live data you collected in Version 6

**Do not overwrite, erase, or move your existing Version 6 folder.** Your Mac previously collected 1,906 additional polls, 200 FEC aggregates, and 200 Congress.gov legislative records. The packaged Version 8 ZIP includes only the small original verified snapshot (so it can be safely distributed); therefore **import your own bigger snapshot** before exploring the new version.

1. Stop the older server using `Control + C` in the Terminal that's running it.
2. Download/unzip Version 8 and open Terminal in the newly extracted `garden-of-democracy-v8` folder (Finder → right-click folder → New Terminal at Folder).
3. Install dependencies for the new folder:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   ```

4. Import your existing saved records **from your existing Version 6 folder**:

   ```bash
   python tools/import_existing_snapshot.py "$HOME/Downloads/garden-of-democracy 6/site/data/snapshot.json"
   ```

   If your older folder has a different name or location, drag the old `site/data/snapshot.json` into Terminal after `python tools/import_existing_snapshot.py ` to insert its exact path. The import validates the snapshot and makes a backup of the new version's initial snapshot before replacing it. It does not alter the old folder. You should see poll/finance/legislation record counts reported.

5. Start the website as normal:

   ```bash
   python -m uvicorn server:app --host 127.0.0.1 --port 8000
   ```

6. Open <http://127.0.0.1:8000> and select **✦ Ask the Garden**. The assistant can now answer using the records you already imported. Keep the server Terminal running.

   If you have a different directory, do not guess: check Finder first or type `pwd` and `ls` in Terminal.

### Testing

```bash
python -m pip install pytest playwright
python -m pytest -q tests/test_pipeline.py tests/test_v5_layers.py tests/test_v6_integrations.py tests/test_v7_audit.py tests/test_v8_assistant.py
node --test tests/test_ask_garden.mjs
python tests/test_v8_browser.py  # needs headless Chromium installed on the test machine
```

The source-confirmed poll and government ingestion jobs remain unchanged. The GitHub Pages/Actions deployment setup is still present, but a working public URL can only be verified after the repository has been published. Ask the Garden's *static evidence mode* works on GitHub Pages; its *generative AI mode* requires local Ollama or a separate authorized hosted service.


---

## Version 9 — OpenStates / Plural Open state legislation

Version 9 adds a **state-level legislation** adapter while retaining every Version 8 feature. The adapter reads the official OpenStates v3 `/bills` endpoint with `X-API-KEY`, verifies the returned jurisdiction against the requested state, keeps original bill links, and stores dated legislation in the same snapshot used by map leaves, the Legislative Understory, and Ask the Garden. Federal records from Congress.gov remain national-only. A bill's introduction or legislative action is never interpreted as enactment or voter support.

**Install without losing your successfully collected V6 records:**

1. Keep your existing `garden-of-democracy 6` folder. Download/unzip this V9 folder separately.
2. In the V9 folder, activate or create its Python environment and install requirements:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt eval-type-backport
   ```
3. Import your real previously collected snapshot from V6 (if you haven't imported it into V8; skip if you have a different newer snapshot to migrate):
   ```bash
   python tools/import_existing_snapshot.py "$HOME/Downloads/garden-of-democracy 6/site/data/snapshot.json"
   ```
   This does not modify the original folder. If your newest local snapshot is V8, point the importer to that instead.
4. **In a separate Terminal window** in the V9 folder (not in the running Uvicorn server process), enter the new OpenStates key securely. This is the macOS `zsh` syntax; the key does not echo:
   ```bash
   read -s 'OPENSTATES_API_KEY?Paste your OpenStates key (hidden): '; echo
   export OPENSTATES_API_KEY
   ```
   Do **not** type the actual key literally into a command, the website, your screenshots, or this chat. Do not add it to `.env` files inside a public repository.
5. Test authentication/connectivity with a **header**, without printing the key or response body:
   ```bash
   curl -sS --max-time 35 -o /dev/null -w 'OpenStates HTTP %{http_code}\n' -H "X-API-KEY: $OPENSTATES_API_KEY" 'https://v3.openstates.org/bills?jurisdiction=Georgia&per_page=1'
   ```
   Expected: `OpenStates HTTP 200`. `401`/`403` implies missing/invalid access; `429` means rate limited.
6. Import a **small verified Georgia sample** into the V9 garden:
   ```bash
   python worker/collect.py --providers openstates --openstates-states GA --max-pages 1
   python worker/audit.py
   ```
   Look for `new_legislation` and `failures: []`. `new_legislation` may be zero when imported records are already present or a provider publishes incomplete metadata; use the source status panel and saved snapshot to check.
7. In Terminal window one, launch the site with `python -m uvicorn server:app --host 127.0.0.1 --port 8000`. Refresh Safari, choose **Georgia**, enable **Legislation**, and open **Policy → Legislation**. Try **Ask the Garden**: “What housing legislation is recorded in Georgia?”
8. For national coverage, the default OpenStates collector rotates through **four jurisdictions per scheduled run** rather than querying all states every two hours. To fetch a specific group use `--openstates-states GA,FL,NC`. For a one-time broader initial import, `--openstates-states all --max-pages 1` makes up to 51 authorized state/DC calls, only if the key's current rate limits permit it. These are bounded samples, not complete legislative archives.
9. For $0 hosted updates: add `OPENSTATES_API_KEY` under **GitHub repository → Settings → Secrets and variables → Actions → New repository secret**. The existing `deploy.yml` now provides that secret to the scheduled collector. **Do not publish the key**. A GitHub Pages deployment has still not been completed in this build environment.

Source: https://docs.openstates.org/api-v3/ and https://v3.openstates.org/docs/. The adapter has offline automated tests but **live OpenStates collection needs to be verified on your Mac or GitHub**. This development container cannot resolve outside hosts.


---

## Version 12 — Geography-locked living gardens

**What was fixed:** The previous map animated a flower on the same SVG element that also carried its geographic translation, potentially displacing it. Campaign-finance raindrops, butterflies and news fireflies were placed in a spiral around each state centroid and could float over other states. Issue vines could also join polls in different states.

**The new system:**

- Every state, including Washington, D.C., receives a true-boundary SVG clipping path, built from Census-derived topology. All associated flowers, financial raindrops, butterflies, news fireflies, legislative leaves and issue vines are drawn in that jurisdiction's clipped layer. Even when animated, **nothing can be rendered inside a neighboring state**.
- Geographic coordinates are assigned deterministically from each source record's stable ID; they are not real transaction or poll collection locations. The animation moves only the petal/glyph inside a stationary geographic anchor.
- The source-linked vines now link surveys sharing the same documented issue **within the same state**. No cross-state visual relationships are inferred. National-only polls remain in Pollarium instead of appearing over an arbitrary state.
- The nationwide garden distributes its limited visible blooms across available states (maximum four source-linked poll flowers per state); selecting one state allows up to 45. This is a visualization sample, **not** an opinion sample or an average. The original records remain inspectable in Pollarium.
- The app tries a locally bundled `site/data/states-albers-10m.json` file first and the public us-atlas@3 CDN second. On first startup, `start.command` attempts to download and validate a local copy. If neither source is available, the offline fallback displays **small stationary state-centroid symbols rather than moving artwork without accurate boundaries**. No data records are invented.
- The GitHub Actions workflow also tries to cache the public map geometry into the deployed static site. This requires network access during its initial run; success is **not verified** until the real GitHub deployment completes.
- Art Studio motion and reduced-motion controls remain available. These settings only affect presentation.

### Install on your Mac without losing your existing real data

1. Keep your currently working folder with the 1,906 newly imported polls, FEC records, and legislative records. Do not delete it.
2. Unzip Version 12 into a **new folder**. Stop the previous running site using `Control+C` in its server Terminal to free port 8000.
3. Open Terminal in the new `garden-of-democracy-v12` directory and run:
   ```bash
   python3 tools/import_existing_snapshot.py "$HOME/Downloads/garden-of-democracy 6/site/data/snapshot.json"
   bash start.command
   ```
   Use the path to your newest `snapshot.json` if you collected additional data in Version 9 or 11. Import validates the old records and refuses to overwrite a larger poll collection.
4. Open http://127.0.0.1:8000. Use the garden and switch between Georgia and other states. Flowers, raindrops, butterflies, news lights and legislative leaves remain geographically restricted. Small states may show scaled or partially cropped glyphs due to their true geographic area.
5. If port 8000 is occupied, stop the old Terminal's server first, or use: `source .venv/bin/activate && python -m uvicorn server:app --host 127.0.0.1 --port 8001` and open http://127.0.0.1:8001.

### Tests

```bash
python -m pytest -q tests/test_pipeline.py tests/test_v5_layers.py tests/test_v6_integrations.py tests/test_v7_audit.py tests/test_v8_assistant.py tests/test_v9_openstates.py tests/test_v12_state_motion.py
node --test tests/test_ask_garden.mjs
python tests/test_v11_browser.py
```

The geometry browser regression test uses **synthetic rectangles only in memory** to verify clip paths, positioning, interaction and redraws on desktop and mobile. The published website continues to use the authentic us-atlas map. The sandbox cannot currently fetch the remote topology, so an actual production CDN download or GitHub-hosted map geometry is not yet verified.

This release does not configure new API secrets, publish to GitHub, or replace your working snapshot. It preserves the integrations and $0-first approach.


## Version 13 — Harvest Journal, safer API headers, and Pages preflight

This version retains the V12 geographic motion containment and V11 natural flower-garden design. New features: a source-grounded Harvest Journal of real imported changes, more informative source-health details, safer `X-Api-Key` credentials for FEC/Congress.gov, throttled GDELT checks on the scheduled runner, and a reproducible GitHub Pages-style static-site smoke test. Run `python tools/deployment_doctor.py` before publishing. Use [Version 13 release notes](docs/V13_RELEASE_NOTES.md) and [the public publishing guide](docs/GITHUB_PUBLISHING.md). Online APIs and a GitHub Pages URL are not verified by this ZIP alone.


## Version 17 — original cottage garden map restored

# Version 17 — Original Cottage Map Restored

The national/state map artwork has been reverted to **Version 11** (the original cottage-garden map before state-locked motion). This rollback is intentional at the user's request.

- Restored original floating/swaying poll flowers, rain, butterfly, leaf, firefly and issue-vine placement and movement.
- Restored the original flower sizes, original softer natural map palette and symbol density.
- Removed geographic boundary clips and constrained state placement from map artwork; decorative symbols may drift across neighboring boundaries **as in Version 11**. Each underlying data record still retains its true state association.
- Preserved the Version 15 branching narrative game, source-grounded assistant, Parallel Gardens, updated collectors, Harvest Journal, and version 16 non-map site improvements.
- Preserved optional locally cached map geometry, which does not affect animation styling.
- This is a targeted visual rollback; it does not change source data or data ingestion.

Run `bash start.command` from the extracted folder. Import your latest `snapshot.json` first if you collected more data locally. Public hosting and remote API operation remain separate tasks.

---

## Version 18 — Public launch package

**Start here:** [`docs/V18_PUBLIC_LAUNCH.md`](docs/V18_PUBLIC_LAUNCH.md). This version adds a public build/collection status report to the Source Observatory, a hardened GitHub Pages workflow, and offline deployment checks. The original cottage garden and branching stories are unchanged. No public URL is claimed until GitHub Pages deployment is confirmed.

After importing a prior version's live `site/data/snapshot.json`, run `python3 tools/build_deployment_manifest.py --collection not-run` to regenerate public metadata, or run `bash start.command` for local use. The GitHub Actions workflow creates new metadata after each hosted collection attempt.
