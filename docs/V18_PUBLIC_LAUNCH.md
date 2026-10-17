# Version 18 — Public launch, $0, source-grounded

**This is a deployment-ready project, NOT a claim that a public URL already exists.**
The project keeps the preferred Version 11 cottage-garden map renderer restored in Version 17, its three-character interactive story, garden art, sound, Pollarium, Parallel Gardens, and Ask the Garden.

## 1. Protect your keys

Your earlier government key appeared in screenshots. **Revoke or rotate the exposed key before uploading the project.** Never save API keys in the GitHub repository, website assets, screenshots, or issue discussions. For your OpenStates key, use a separate repository secret.

## 2. Prepare the latest snapshot on your Mac

1. Download and unzip Version 18. Keep the older Garden folder.
2. Open a Terminal inside `garden-of-democracy-v18` (type `cd `, drag the folder into Terminal, press Return).
3. Import your newest known-good prior snapshot **before uploading**:

```bash
python3 tools/import_existing_snapshot.py "$HOME/Downloads/garden-of-democracy 6/site/data/snapshot.json"
```

If a newer version has a more complete `site/data/snapshot.json`, use that path instead. The importer audits the data and preserves a backup.

4. Build the public status file and run the local launch checks:

```bash
python3 tools/build_deployment_manifest.py --collection not-run
python3 worker/audit.py
python3 tools/deployment_doctor.py
```

The included `site/data/deployment.json` must match the snapshot being uploaded. `bash start.command` also regenerates local metadata and launches the application.

## 3. Create a free public repository

- Sign up or sign in at [GitHub](https://github.com/), and use [GitHub Desktop](https://desktop.github.com/) if you prefer not to use Terminal Git commands.
- Add the extracted project directory as a local repository (create a repository there when prompted), make an initial commit, then choose **Publish repository**.
- Name it `garden-of-democracy` (or use your own repo name), and make it **public**.
- Confirm `.github/workflows/deploy.yml` appears under the **Code** tab after publishing.
- **Do not upload the ZIP itself instead of the project contents.** If the GitHub web upload hides `.github`, use GitHub Desktop.
- `.venv/`, `.env`, private files, and database files are covered by `.gitignore`, but inspect changes before committing.

## 4. Configure GitHub Pages

- Open your GitHub repository → **Settings** → **Pages** → **Build and deployment** → **Source: GitHub Actions**.
- Under **Settings → Secrets and variables → Actions**, create these three *repository secrets* (not plain variables): `FEC_API_KEY`, `CONGRESS_API_KEY`, `OPENSTATES_API_KEY`.
- The FEC and Congress.gov integrations may accept the same api.data.gov key; never put it into the frontend or README. Use the rotated replacement.
- Optional `DATABASE_URL` is **not needed** for $0 static hosting. A persistent PostgreSQL mirror is an optional separate service, not included in the zero-cost deployment.

## 5. Verify the first hosted run

- Open **Actions → Refresh civic data and publish garden → Run workflow** on the default `main` branch.
- Wait for the Pages upload and deploy steps to succeed. Read the job summary for collection outcome, record counts, and timestamps.
- If collectors are rate-limited, the public website can still deploy using the last audited snapshot. The **Source Observatory** shows `success`, `partial`, or `failed` for that *run*, separately from underlying publication dates.
- Under **Settings → Pages**, click **Visit site**. Confirm the **actual** URL; typical project-site form is `https://YOUR-USERNAME.github.io/garden-of-democracy/` but this example is not a live address.
- Test Garden, Pollarium, sources, story, map regions, and the question assistant on both phone and laptop.
- Open `https://YOUR-REAL-PAGES-URL/data/deployment.json` to inspect the latest deployment metadata (substitute actual project URL). No key should ever appear in it.

## 6. Verify scheduled updates

The workflow requests new data approximately every two hours and news less often. This is **scheduled collection**, not an always-on server. GitHub may delay or skip scheduled runs; after 60 days of no repository activity, public-repository schedules may be disabled. Check **Actions** after a scheduled interval. A green workflow proves the site deployed; separately inspect whether a provider was contacted and whether records changed.

The workflow persists validated JSON back to the repository after deploying. If repository policy prevents `git push`, the Pages publication can still work, but **future scheduled runs may start from an older snapshot** until you correct Actions permissions. Check the `Commit refreshed public records for next run` step; a warning there needs attention.

## 7. $0 limitations and safety

- GitHub Pages hosts HTML/CSS/JavaScript/JSON only, not your local FastAPI or Ollama process. **Ask the Garden's rule-based source retrieval** works publicly; optional generative Ollama narration remains local until a separate privacy-safe hosted service is arranged.
- No continuously running PostgreSQL server, push streaming, or unrestricted AI API is included. The GitHub-hosted garden reads static JSON refreshed by scheduled jobs.
- API quotas, third-party dataset permissions, GitHub policies, and size limits still apply. Do not upgrade to paid services.
- The garden may be visually animated while its official political observations remain unchanged; **no animation means a new poll or transaction unless tied to a verified record.**
- Do not activate fabricated election results or forecasts. Election returns stay inactive before actual results are available.

## What success means

- Actual Pages URL loads in an unconnected browser or phone.
- Actions shows at least one successful `deploy-pages` step, and a scheduled run later completes.
- Source Observatory shows correct timestamps and a non-fabricated `collection_outcome`.
- Original source links work, all 51 jurisdictions are accessible, and the original floral map style is preserved.
- No API secrets leaked to public files. The complete deployment stays at $0.
