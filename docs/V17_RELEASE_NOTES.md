# Version 17 — Original Cottage Map Restored

The national/state map artwork has been reverted to **Version 11** (the original cottage-garden map before state-locked motion). This rollback is intentional at the user's request.

- Restored original floating/swaying poll flowers, rain, butterfly, leaf, firefly and issue-vine placement and movement.
- Restored the original flower sizes, original softer natural map palette and symbol density.
- Removed geographic boundary clips and constrained state placement from map artwork; decorative symbols may drift across neighboring boundaries **as in Version 11**. Each underlying data record still retains its true state association.
- Preserved the Version 15 branching narrative game, source-grounded assistant, Parallel Gardens, updated collectors, Harvest Journal, and version 16 non-map site improvements.
- Preserved optional locally cached map geometry, which does not affect animation styling.
- This is a targeted visual rollback; it does not change source data or data ingestion.

Run `bash start.command` from the extracted folder. Import your latest `snapshot.json` first if you collected more data locally. Public hosting and remote API operation remain separate tasks.

## Release verification (October 17, 2026)

- Python test suite: **49 passed, 2 skipped** (obsolete V12 state-lock checks; intentionally incompatible with requested rollback).
- JavaScript assistant and story tests: **14 passed**.
- Version 17 restored-map browser tests: passed in Chromium at **1440×900 and 390×844** with synthetic map shapes for test isolation. Real source geometry is used at runtime when downloaded; this does not constitute a live geographic-source test.
- JavaScript syntax checks: passed.
- Local server: HTTP 200 for `/`, `/app.js`, `/style.css`, and `/data/snapshot.json`.
- External API ingestion and hosted deployment: not reverified in this release.
