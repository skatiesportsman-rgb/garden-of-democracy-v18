# Version 9 — Test and integration report

2026-10-15 (artifact build)

## Verified locally
- 40 Python tests passed, including 7 OpenStates adapter tests: source-jurisdiction validation, secure key header, bounded collection, rotating coverage, missing-key preservation, revision detection, and atomic snapshot publication with test-only data.
- 9 source-grounded Ask the Garden JavaScript tests passed (including OpenStates state-bill source attribution).
- Browser tests (Chromium) at 1440x900 desktop and 390x844 mobile passed for V8 navigation/question interface and V9 state legislative record in the map, Legislative Understory, and question answers. V9 browser test uses a **synthetic fixture injected in memory only**, not production data.
- JS syntax and Python compilation passed, and the included static snapshot passed `worker/audit.py`.
- `worker/coverage.py` recognizes all 51 states/D.C. and writes counts for state legislative records.

## Not yet independently verified
- OpenStates API retrieval with the user's newly obtained key (the key has not been shared, which is correct). The build environment lacks external DNS access. A 200 API response on the user's Mac and a successful collector run are required before marking OpenStates operational.
- All-state full dataset coverage: the free-tier collector samples at most 4 jurisdictions per scheduled job, up to 2 pages per jurisdiction. It does not claim exhaustive state legislative activity.
- Github Pages publication and scheduled remote collector runs; no public deployment URL is available.
- Existing 1,906 additional polls, 200 finance and 200 federal bill records reside on the user's Mac in V6; the ZIP contains the original small, sourced snapshot and includes a migration tool.
