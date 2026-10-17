# Publish The Garden of Democracy for $0 with GitHub Pages

The project is ready for **a user-controlled public repository**; no public site has been created in this working environment. GitHub Pages hosts **the static `site/` folder**. The workflow in `.github/workflows/deploy.yml` pulls new civic records with scheduled GitHub Actions and republishes the resulting validated JSON.

## Before uploading

1. Keep previous Garden folders as backups; the ZIP's bundled snapshot is small. If your newest verified snapshot lives in Version 6, 9, 11, or 12, import that file into Version 15 first:

   ```bash
   python3 tools/import_existing_snapshot.py "$HOME/Downloads/garden-of-democracy 6/site/data/snapshot.json"
   ```

   Change the path if your most recent data is in a different version. The import tool performs a data audit and keeps a backup. **Inspect the imported counts before publication.**
2. Run `python tools/deployment_doctor.py`. A pass only verifies local static structure and source data—it is not an online connection test.
3. Make sure `.venv/`, `.env`, API keys, private databases, and credentials are **not** committed. Do not put secrets in `site/`, `README.md`, screenshots, or frontend JavaScript.
4. Previously exposed API keys must be deactivated and replaced by their issuer.

## Publish

1. Create a **public** repository named `garden-of-democracy` under your own GitHub account. Public GitHub Pages + standard GitHub Actions workflows can use GitHub's free plan subject to current service limits.
2. Open GitHub Desktop, choose **File → Add Local Repository** and select the extracted Version 15 folder. If asked, choose **Create a Repository Here**. Commit the application files, then **Publish repository** with **Keep this code private** unchecked. Keep `.github/workflows/deploy.yml` in the project.
3. In the GitHub repository choose **Settings → Pages → Build and deployment → Source: GitHub Actions**.
4. Under **Settings → Secrets and variables → Actions**, add only the relevant free credentials as repository secrets. Their exact names are `FEC_API_KEY`, `CONGRESS_API_KEY` and `OPENSTATES_API_KEY`. Do not paste secrets into code files. The public polling adapters don't require a separate key. Optional `DATABASE_URL` is only for a PostgreSQL mirror, not needed for static Pages.
5. Go to **Actions → Refresh civic data and publish garden → Run workflow**. Wait for the job to finish. Inspect every step, especially the source collection logs, audit, nested-site preflight and Pages deployment.
6. Only after GitHub confirms success, use **Settings → Pages → Visit site** to obtain the *actual* URL. A typical project URL is `https://YOUR_USERNAME.github.io/garden-of-democracy/`; this is an illustrative URL, not an existing deployment.

## What to verify after publishing

- The homepage opens on a phone and desktop and preserves cottage-garden styling.
- The national map and all 51 jurisdictions are navigable; no decorative element leaks outside real state outlines when geometry is available.
- The **Source Observatory** shows real successful API-check times. If source authentication or rate limits fail, it reports that rather than simulating data.
- The **Harvest Journal** contains only truly new or revised records from successful collection. Old publications retain old publication dates.
- Clicking a flower opens its original poll; finance raindrops and bill leaves appear only where valid records and credible geography exist.
- After at least one scheduled run, the GitHub Actions log and snapshot's source status confirm whether automatic updates actually work. Expect schedule delays; scheduled automation is not a permanently operating server.
- Public **The Stories We Grow** works locally in each visitor’s browser with branching paths and optional source cards; story choices cannot affect real politics.
- Public **Ask the Garden** works using source-grounded summaries in the browser. AI narration with locally installed Ollama works only on a Mac running the optional backend.

## Debugging common problems

**The workflow is missing:** Verify `.github/workflows/deploy.yml` is committed on `main`; enable Actions if GitHub prompts you.

**The site returns a 404:** Confirm Pages source is **GitHub Actions** and the deployment step passed. The site link appears in Pages settings; don't invent a URL.

**The site loads but has no flowers:** Ensure `site/data/snapshot.json` has imported valid polls. Review the `Run independent collection bots` step: API reachability can vary, and 429 means rate limited.

**The map only shows stationary centroids:** The authentic state TopoJSON download did not succeed. Inspect the `Cache accurate state boundaries` step; the offline fallback intentionally avoids unbounded animation.

**Git push failed:** GitHub Actions' content write permissions and branch protection settings must allow the bot to commit snapshots. A workflow may be able to deploy successfully even if its snapshot commit failed; verify both steps.

**A GitHub Actions secret was exposed:** Revoke it immediately with the provider and create a new key. Don't post key-bearing screenshots.

## Ongoing $0 considerations

GitHub Pages is a static host; it cannot run FastAPI continuously. Actions runs are scheduled jobs, which can be delayed or skipped and have plan/service limits. If the free plan changes, do not silently migrate to a paid tier. Public polling, FEC, Congress.gov and OpenStates feeds have independent access restrictions and limits. Review them before raising collection frequency.
