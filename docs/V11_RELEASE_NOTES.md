# Version 11 — The Cottage Garden

## Actual updates
- Replaced the neon, sci-fi visual language with a warm editorial **daylight flower garden**: ivory paper, sage and fern greens, muted floral pinks, terracotta, ochre, and sky blue. Nine Art Studio presets are now nature-based and non-neon.
- Created an original SVG wildflower border for the landing header. Its flowers are **decorative**, unlike data-linked flowers on the map and in the comparison beds.
- Updated map petals to use botanical blossoms with stems and leaves, and changed state geography from dark neon to soft botanical shades. Existing map and data animations remain.
- Rebuilt **Parallel Gardens** as two side-by-side animated SVG flower beds, responsive down to narrow mobile screens. Each source-backed symbol is keyboard- and pointer-selectable: poll flower, bill leaf, finance raindrop, debate butterfly, or article firefly. Vines connect only polls sharing an indexed issue topic; a connection is not proof of comparability.
- Added a **source-coverage ledger** comparing imported counts (not opinions) and an in-session **field notebook** recording source-linked discoveries. Original source URLs open safely in separate tabs.
- Added a research trail with four quests. Source detective requires selecting an actual record, time traveler requires a selected historical cutoff, and coverage / evidence-caution trails teach record limitations. No scores compare politics or states' worth.
- Included a self-contained `start.command` for simple Mac startup and kept API keys out of the project and client.

## Verification in this environment
- 40 Python backend/integration tests passed.
- 9 JavaScript Q&A tests passed.
- JavaScript syntax and Python compilation passed.
- Website HTTP request returned `200 OK` from an actually running local FastAPI instance.
- Desktop (1440 × 950) and mobile (390 × 844) Chromium browser interaction tests passed using an **offline, source-linked snapshot fixture**. Confirmed each garden bed renders, state and issue selection, interactive source opening and notebook, quest progress, shuffle and reset, with no uncaught page errors.
- Screenshots: `docs/v11-garden-1440.png`, `docs/v11-compare-1440.png`, `docs/v11-garden-390.png`, `docs/v11-compare-390.png`.
- Browser automation cannot directly navigate the local network endpoint in this restricted environment, so it loaded the *actual HTML/CSS/JS* into Chromium with bundled data and the hero illustration. The running FastAPI HTTP check was separate.
- Old `test_v3_browser.py` and `test_v4_browser.py` are standalone historical scripts that cannot evaluate the newer module source as plain script; they are superseded by `test_v11_browser.py`.

## Outstanding tasks
- **Not deployed publicly**. GitHub repository ownership and GitHub Pages workflow activation still need to be completed by the user.
- External FEC, OpenStates, Congress.gov, polling, and GDELT feeds have not been reconnected in this sandbox. The user previously reported successful local FEC/Congress/poll collection in an earlier local installation; import that installation's newest `site/data/snapshot.json` to preserve actual data.
- As always, source coverage differs among states and publication dates. Missing records are never substituted with fictional ones. No new polling or other political records were invented for this visual update.

## Mac installation and migration
1. Keep the old folder containing collected data.
2. Extract `Garden_of_Democracy_v11_Cottage_Garden.zip` into Downloads.
3. From inside the new `garden-of-democracy-v11` folder, run `bash start.command` to install and launch. Or use the standard `.venv` instructions in README.
4. **Before first run or collection**, import the most recent real-data snapshot, for example:
   `python tools/import_existing_snapshot.py "$HOME/Downloads/garden-of-democracy 6/site/data/snapshot.json"`
   Use the newer Version 9/10 path instead if that contains more current polls and legislative records.
5. Run `python worker/collect.py --max-pages 2` from an **additional terminal**, with authorized provider keys already set as environment variables. Do not send keys over chat or embed them in public files.

## Source data, colors, and source boundaries
Colors are decor, not party identifiers or good/bad outcome labels. Scene movement does not increase source counts. A poll flower is one stored survey record. A bill leaf is one stored legislative record. A finance droplet depicts one stored finance aggregate/filing, **not an individual transaction at that instant**. National records are not invented into state gardens.
