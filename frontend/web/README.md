# Resume Builder Web

This is the deployable React/Vite frontend for Resume Builder. It lives in the main repository so the frontend and FastAPI backend can evolve together, but it deploys independently.

## Local development

```powershell
npm install
npm run dev
```

Set `VITE_API_URL` in `.env` if the API is not running at `http://localhost:8000`. The local API accepts `local-development-token` by default. For production OAuth, also set `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY`; the app then starts Google sign-in in the browser and sends the resulting access token to the API.

## GitHub deployment

For Vercel or Netlify, connect the repository and set the project root to `frontend/web`. Use `npm run build` as the build command, `dist` as the output directory, and set `VITE_API_URL`, `VITE_SUPABASE_URL`, and `VITE_SUPABASE_ANON_KEY`. Configure the backend CORS origin to the deployed frontend URL.
