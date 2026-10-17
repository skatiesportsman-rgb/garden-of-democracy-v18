# Version 18 release test report

Test date: 2026-10-17 UTC. All tests executed on the packaged project files in the sandbox.

| Check | Observed result |
|---|---|
| Python integration, source audits, V17 map preservation, V18 manifest and offline browser checks | 40 passed |
| JavaScript Ask the Garden and three-character branching stories | 14 passed |
| Python source compilation and JS syntax | Passed |
| Snapshot provenance and geographic record audit | Passed |
| Local static GitHub Pages nested path, all required assets and 51 jurisdictions | Passed |
| GitHub Actions YAML parsing and required trigger structure | Passed |
| New Source Observatory build information on desktop/mobile synthetic-browser test | Passed |
| Live network requests to political APIs from hosted Github runners | **Not tested** |
| GitHub Pages account permissions and actual public URL | **Not verified** |
| GitHub workflow commit/write permission for persistent updated snapshots | **Not verified** |

The Chromium browser test uses inline frontend code with source-linked baseline records and synthetic polygons **only in the test runtime**, because direct browser access to the loopback HTTP server was blocked by this sandbox. The static nested-path HTTP server was tested independently using a Python HTTP client. Neither constitutes a hosted deployment.

**Important baseline limitation:** The ZIP includes the project's original small source-linked snapshot (10 polls and 4 debate records). It does not contain the approximately 1,906 polls, 200 FEC summaries and 200 bills imported on the user's Mac in earlier versions. Import the newest known-good `snapshot.json` before publishing.

**Security:** No real API credentials are bundled. The public manifest intentionally excludes API keys. Earlier screenshots shared a government key; rotate/revoke it before creating GitHub repository secrets.
