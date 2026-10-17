# Version 18 — Launch reliability & public data transparency

### Implemented
- Kept the original pre-state-lock cottage-garden map and modern branching stories from Version 17.
- Revised GitHub Actions publishing workflow so successful website publication does not depend on the success of *each external API* or on pushing the current snapshot back to GitHub.
- Added `tools/build_deployment_manifest.py`, creating a safe public `site/data/deployment.json` with build time, source-data time, source health counts, record counts, workflow run link and success/partial/failure status.
- Added Observatory launch-health panel. Public page updates never imply an old poll was just published.
- Updated static publishing preflight to validate deployment manifest and nested GitHub Pages URL structure.
- Added offline unit and desktop/mobile browser regression checks for deployment metadata, actual map, and branching stories.
- Improved Mac startup script to regenerate local status after old snapshots are imported.
- Created `docs/V18_PUBLIC_LAUNCH.md` with verified setup, secrets, and budget constraints.

### Not yet verified or still blocked
- No live public GitHub Pages URL or remote scheduled job was created from this sandbox. Requires publishing to the user's GitHub repository.
- No live provider requests were made in this release. Successful local runs in the user's earlier Version 6 do not verify hosted API reachability.
- Public site uses GitHub Pages static hosting; a permanent PostgreSQL server and hosted generative model are outside the $0 stack.

### Important
The bundled `site/data/snapshot.json` contains only the original small sample of source-linked observations. Import the user's newest collected snapshot before uploading the public repository.
