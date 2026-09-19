# Deployment Guide

This guide covers the cloud-ready FastAPI service. The local NiceGUI editor can continue to run independently while the API is deployed.

## Architecture

- **Frontend:** A web client calls the FastAPI service and sends a bearer token with each request.
- **API:** `backend/src/api.py` validates the token, scopes data to the authenticated user, and compiles PDFs.
- **Authentication:** Supabase Auth validates production access tokens. Local development uses a fixed development token.
- **Storage:** Supabase stores each user's master document. Without Supabase variables, the API uses `backend/data/` as a development fallback.
- **PDF generation:** Typst runs inside the API container and writes each build to an isolated temporary directory before streaming it to the client.

## Supabase configuration

1. Create a Supabase project.
2. Run [`backend/schema.sql`](../backend/schema.sql) in the Supabase SQL editor. This creates the user-scoped `master_documents` table and enables row-level security.
3. Enable Google under **Authentication > Providers** and configure the Google OAuth redirect URL required by your frontend.
4. Copy [.env.example](../.env.example) to a local `.env` file for development, or add the same values as secrets in your hosting provider:

```text
APP_ENV=production
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
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
4. Configure the health check path as `/health`.
5. Deploy and confirm that `/health` returns `{"status":"ok"}`.

Free container plans may sleep when idle, so the first request after inactivity can take longer than later requests.

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