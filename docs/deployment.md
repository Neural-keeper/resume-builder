# Deployment Guide

This guide covers the cloud-ready FastAPI service. The local NiceGUI editor can continue to run independently while the API is deployed.

## Architecture

- **Frontend:** A web client calls the FastAPI service and sends a bearer token with each request.
- **API:** `backend/src/api.py` validates the token, scopes data to the authenticated user, and compiles PDFs.
- **Authentication:** Supabase Auth validates production access tokens. Local development uses a fixed development token.
- **Storage:** Supabase stores each user's master document. Without Supabase variables, the API uses `backend/data/` as a development fallback.
- **PDF generation:** Typst runs inside the API container and writes each build to an isolated temporary directory before streaming it to the client.

OAuth belongs on the frontend. The browser uses Supabase's public URL and anon key to start Google sign-in and receives a user session. The backend does not perform the OAuth redirect; it validates the frontend's Supabase access token, extracts the user ID, and applies the user scope to every database operation. The Supabase service role key stays on the backend only.

## Deployment order

Deploy the two services from the same GitHub repository in this order:

1. **Deploy the frontend first.** Create a Vercel or Netlify project with root directory `frontend/web`. Add `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY`. `VITE_API_URL` can temporarily point to `http://localhost:8000` while the API is being deployed. Copy the resulting frontend URL.
2. **Configure Google OAuth.** In Supabase, enable Google and add the deployed frontend URL to the provider's allowed redirect URLs. Also set the Supabase URL configuration's site URL to that frontend URL.
3. **Deploy the backend.** Create a Render Docker web service from the same repository. Configure the Supabase variables, set `FRONTEND_ORIGINS` to the exact frontend URL, and deploy on port `8000`.
4. **Connect the frontend.** Update the frontend's `VITE_API_URL` to the deployed backend URL and trigger a new frontend deployment.
5. **Verify the full path.** Sign in with Google, load the master resume, save a change, and export a PDF. Check the backend `/health` endpoint separately.

The frontend and backend do not need separate repositories. They are separate deployments with separate environment variables and can share this repository's Git history.

## Supabase configuration

1. Create a Supabase project.
2. Run [`backend/schema.sql`](../backend/schema.sql) in the Supabase SQL editor. This creates the user-scoped `master_documents` table and enables row-level security.
3. Enable Google under **Authentication > Providers**. Add the frontend URL to the provider's allowed redirect URLs and set it as the Supabase site URL.
4. Copy [.env.example](../.env.example) to a local `.env` file for development, or add the backend values as secrets in your hosting provider:

```text
APP_ENV=production
FRONTEND_ORIGINS=https://your-frontend.example.com
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

The frontend receives only the public values below through Vite environment variables:

```text
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_API_URL=https://your-api.example.com
```

Do not commit `.env` or expose `SUPABASE_SERVICE_ROLE_KEY` to a browser. The service role key is used only by the backend server.

## Run with Docker

Build and start the API locally:

```powershell
docker build -t resume-builder-api .
docker run --env-file .env -p 8000:8000 resume-builder-api
```

Check that it is running:

```powershell
curl http://localhost:8000/health
```

The included [Dockerfile](../Dockerfile) installs Python dependencies and the Typst CLI. The service listens on port `8000` and binds to `0.0.0.0`, as expected by container hosts.

## Deploy to Render or another container host

1. Create a Docker web service connected to this repository.
2. Set the service port to `8000`.
3. Add `APP_ENV`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`, and `SUPABASE_SERVICE_ROLE_KEY` as encrypted environment variables.
4. Add `FRONTEND_ORIGINS` with the exact deployed frontend URL, without a trailing slash.
5. Configure the health check path as `/health`.
6. Deploy and confirm that `/health` returns `{"status":"ok"}`.

Free container plans may sleep when idle, so the first request after inactivity can take longer than later requests.

## Deploy through GitHub Actions

You do not need Docker, Python, or npm installed locally. The workflow at [`.github/workflows/backend.yml`](../.github/workflows/backend.yml) runs on GitHub-hosted Ubuntu runners and will:

1. Install Python dependencies.
2. Compile the backend Python modules.
3. Build the Docker image from the repository's `Dockerfile`.
4. Trigger a Render deployment after validation succeeds, when a deploy hook is configured.

Configure the workflow once:

1. In Render, create a **Docker Web Service** connected to this GitHub repository.
2. Set the service environment variables and health check from the sections above.
3. In Render, open the service settings and create a **Deploy Hook**.
4. In GitHub, open **Settings > Secrets and variables > Actions > New repository secret**.
5. Name the secret `RENDER_DEPLOY_HOOK_URL` and paste the Render deploy hook URL as its value.
6. Push a change to `main`, or run **Actions > Backend CI and deploy > Run workflow**.

Pull requests run validation and build the image but never deploy. Pushes to `main` deploy only after validation passes. If the Render secret is absent, the workflow still validates the backend and reports that deployment was skipped.

The Render service still builds and runs the image itself. GitHub Actions is the gate and deployment trigger; it does not need to publish the image to a registry for this setup.

## API requests

Production clients should send the Supabase access token on every protected request:

```text
Authorization: Bearer <supabase-access-token>
```

Example master document request:

```powershell
curl https://your-api.example.com/api/v1/me/master `
  -H "Authorization: Bearer <supabase-access-token>"
```

The API derives the user ID from the validated token. Clients never provide a user ID, which prevents one user from requesting another user's document through the API.

## Security checklist

- Keep the Supabase service role key server-side only.
- Use `APP_ENV=production` in deployed environments; this disables the development token fallback.
- Keep row-level security enabled on Supabase tables.
- Require HTTPS at the hosting and frontend layers.
- Do not rely on the container filesystem for permanent files.
- Review logs before enabling request-body or token logging; access tokens and resume content are sensitive.

## Deploy the web frontend

The browser client lives in `frontend/web` and can be deployed independently to Vercel, Netlify, or GitHub Pages. It does not need a separate repository: use the existing GitHub repository and set the hosting provider's project root to `frontend/web`.

Build settings for Vercel or Netlify:

- **Root directory:** `frontend/web`
- **Build command:** `npm run build`
- **Output directory:** `dist`
- **Environment variables:** `VITE_API_URL`, `VITE_SUPABASE_URL`, and `VITE_SUPABASE_ANON_KEY`

When the Supabase frontend variables are present, the app shows Google sign-in and sends the resulting session token to the API. Without them, the app remains usable against the local API with `local-development-token`; do not use that fallback in production.