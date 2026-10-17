# V8 release test results — October 15, 2026

## Verified in this build environment
- 33 automated Python data, ingestion, security, API, local-assistant and migration tests passed.
- 8 independent JavaScript question-answer accuracy/regression tests passed.
- Browser-level desktop (1440 x 900) and mobile (390 x 844) navigation & Ask the Garden interaction checks passed in in-memory Chromium. Both five paired menus and all three answer lengths are present. Questions return source-linked evidence; unsupported winner predictions are refused.
- `site/app.js` and `site/garden-answer.js` pass syntax checks, Python backend and collector modules compile, and the bundled snapshot passes the data audit.
- An optional Ollama inference response was tested with a **mock HTTP response only**; actual downloaded local AI model availability on the user's Mac has not been tested.

## Not verified
- The user must import the larger V6 snapshot from their Mac (1,906 newly collected polls, 200 finance, 200 legislation) before those records are present in V8. The packaged baseline is 10 historical/publication-linked polls, 4 debates, and no bundled finance or legislation rows.
- No public GitHub Pages URL has been published by this release.
- No Ollama model has been installed or started in the build environment.
- No additional external API ingestion was performed in the build environment.

## Accuracy boundaries
- Public static Q&A answers are deterministic source extracts, not LLM-generated text.
- On-device local-AI responses are independent prose and can still be mistaken; they require source validation. Unsupported percentage claims trigger a factual fallback.
- No claims about future elections, debate winners, unsupported geography, or missing survey values are synthesized.
