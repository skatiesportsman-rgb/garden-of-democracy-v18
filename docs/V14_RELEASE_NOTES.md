# Version 14 — Civic Garden Quest

## Built in this version

- Seven-chapter playable, nonpartisan civics course with responsive cottage-garden artwork.
- Chapters: public issues, polling, debates, financial filings, federal legislation, voting administration and reporting/certification.
- Multiple-choice questions, four-way source-type matching, and a five-step federal lawmaking sequence puzzle.
- Immediate correct/incorrect feedback, hints, learning explanations, optional deeper context and official government reading links.
- Local field-guide badges and a botanical progress garden. Progress stays in browser local storage, never enters political data snapshots.
- Issue/state selections surface only imported, safely linked, source records; empty selections show a transparent data-coverage warning.
- Navigation now groups Ask the Garden and Civic Garden Quest under one paired Learn & Play menu; five other paired menus remain unchanged.
- Added a Play Civic Garden Quest shortcut below the national map.
- Added game data-quality and interaction tests to GitHub workflow.

## Verification

- Node game logic, answer accuracy and source-filter tests: PASS.
- Real Chromium desktop and mobile game interactions: PASS using the project's bundled records (no fake political data).
- Previous ingestion backend suite: tested separately; see DEVELOPMENT_PROGRESS.md.
- Public deployment and scheduled hosted ingestion: still pending user GitHub publishing and successful Actions runs.

## Content integrity

The classroom exercises are fictional and are not sourced political events. Each *real* evidence card is selected exclusively from the published garden snapshot, and if absent is labeled unavailable. Learning progress flowers are classroom badges, not polls or finance events. This game does not predict winners, suggest parties or solicit political preferences.

## Source references

- https://www.usa.gov/how-laws-are-made
- https://www.eac.gov/election-officials/election-results-canvass-and-certification
- https://www.eac.gov/voters/voter-faqs
