# Version 15 — The Stories We Grow

**October 17, 2026 · Branching civic storybook**

## What changed

- Removed the old multiple-choice civics game and its legacy test and JS file.
- Introduced three illustrated fictional protagonists and 21 authored, branching scenes about relatable policy concerns: housing, debate reporting and school transportation.
- Choices actually change narrative routes, consequences and endings. There are three reachable endings per character (nine endings across the release), none depicting a real election result or official policy success.
- New story navigation supports previous choices, undo, restart, switch/resume another character and per-browser save when available.
- New reading mode offers story-only or expanded civic context.
- Each scene offers a clearly separated, optional evidence panel showing only real source-linked garden records in appropriate jurisdictions and date ranges.
- Existing source-backed U.S. garden, poll flowers, rain, vines, state map clipping, Parallel Gardens, other features and collection infrastructure are preserved.

## Design

- Illustrated editorial characters using inline SVG (not photos or depictions of named real politicians).
- Spring meadow, rose, bluebell and autumn palettes aligned with the previous natural cottage-garden redesign.
- Organic flower movement only, optional reduced motion, screen-reader text for portraits and keyboard-operable choices.
- All character names, towns, encounters and dialogues are explicitly labeled fiction.

## Data safety

No story choice changes real political data. A journalist's source check is a story action, not an actual documented debate outcome. Polling references preserve original geography. No real voter or character profiles are collected: local progress saves only selected scene IDs and choice history in this browser.

## Verification

- `node --test tests/test_ask_garden.mjs tests/test_v15_stories.mjs`: passing in release build.
- `python3 -m pytest tests/test_v15_browser.py`: passing in Chromium desktop and mobile using actual client code and bundled data, with isolated network calls.
- Static public deployment **not verified**; free hosting configuration remains available and unchanged except for updating story tests.

## Installation / existing data

Unzip Version 15, keep the old version as a backup, import the newest validated `site/data/snapshot.json` with `tools/import_existing_snapshot.py`, then run `bash start.command` on Mac. Use **Learn & Play → The Stories We Grow**. The installer never includes personal API keys.
