# Deployment audit (2026-03-29)

## Findings

1. The existing Cloudflare workflow (`.github/workflows/deploy-worker.yml`) deploys only the Worker defined in `wrangler.toml`.
2. `wrangler.toml` points to `chat-widget/worker.js` and `workers_dev = true`, which targets Worker runtime deployment (API/backend behavior), not static site publishing.
3. The site UI updates (InterviewIQ HTML/CSS/JS) are in `index.html`, but no workflow was publishing static files to Cloudflare Pages.
4. Result: workflow can pass while `tonyabdelmalak.com` still serves unchanged static content.

## Root cause

A deployment scope mismatch: the "Deploy to Cloudflare" job was configured for Worker deployment only, but the observed changes were static site changes.

## Remediation added in this commit

- Clarified worker workflow name/scope so it cannot be mistaken for a full-site deploy.
- Added a dedicated static-site Cloudflare Pages deployment workflow:
  - `.github/workflows/deploy-static-site.yml`
  - Requires repository secrets: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_PAGES_PROJECT`.

## Operational verification checklist

- Confirm commits with site changes are merged to `main`.
- Confirm Cloudflare Pages project is connected to the same account/domain.
- Run the "Deploy Static Site (Cloudflare Pages)" workflow and verify successful deployment URL in workflow logs.
- Purge Cloudflare cache if stale content persists.
