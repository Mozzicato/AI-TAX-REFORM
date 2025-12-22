RENDER DEPLOYMENT

Quick checklist and step-by-step guide for deploying the backend to Render and safely rotating secrets.

1) Remove secrets from the repo (if present)
   - Remove file from git index (keeps local file):
     git rm --cached backend/.env
     git commit -m "chore: remove committed secrets"
     git push origin main
   - Rotate any exposed keys (esp. RENDER_API_KEY and GOOGLE_API_KEY) — create new keys in the services' dashboards.
   - If you need to purge secrets from history, use `git filter-repo` or BFG. Example with git-filter-repo (recommended):
     pip install git-filter-repo
     git filter-repo --path backend/.env --invert-paths
   - Note: Be careful rewriting history for shared branches.

2) Ensure .gitignore is set (it already includes `.env`) — this will prevent future `.env` files from being added.

3) Add a `.env.example` (included in this repo) and copy it to `.env` locally:
   cp .env.example .env
   fill in your real values locally or in your CI / Render dashboard.

4) Create a new Web Service on Render (via dashboard)
   - Visit: https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect to GitHub and choose the `Mozzicato/AI-TAX-REFORM` repo
   - Deploy from the `main` branch
   - Build type: Docker (this repo has `backend/Dockerfile`) or use auto-detected build commands
   - Start Command (if not using Docker): `uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --app-dir=backend`
   - Health check path: `/health` (or use Docker HEALTHCHECK)

  - Optional: you can apply the bundled `render.yaml` manifest to create/configure the service declaratively. After installing the Render CLI, run:

      render services create -f render.yaml

    Or set up secrets in the Render dashboard and use `render up` or the dashboard UI to deploy.
    The `render.yaml` in the repo contains placeholders for required env vars; keep secret values in the dashboard or create them via `render secrets create`.
     - GOOGLE_API_KEY / GEMINI_API_KEY
     - PINECONE_API_KEY, PINECONE_ENVIRONMENT, PINECONE_INDEX_NAME
     - NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE
     - OPENAI_API_KEY (optional scripts)
     - ALLOWED_ORIGINS
     - any other values from `.env.example`
   - Save and deploy

6) Optional: Enable "Auto Deploys" so pushes to `main` trigger a new deploy automatically.

7) Trigger a deploy via API (checks / script included)
   - After creating the service, obtain the service id from the Render dashboard URL (it starts with `srv-...`).
   - Set `RENDER_API_KEY` locally (this is your personal/render API token)
   - Set `RENDER_SERVICE_ID` and run:
     ./scripts/deploy_to_render.sh

8) Verify
   - Check Render dashboard logs
   - Visit the service URL
   - Hit `/health` to confirm `200 OK`

Notes & Security
- Do NOT commit secrets. Use `.env.example` and Render's dashboard secrets.
- Rotate any keys that were committed to the repo earlier.
- If you want CI-based deploys, store `RENDER_API_KEY` as a secret in your CI provider and run the `deploy_to_render.sh` script in a job.

