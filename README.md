# Resume Builder

<<<<<<< HEAD
Resume Builder keeps one master resume and helps you create targeted versions for different roles. Instead of rewriting the same experience repeatedly, you maintain reusable entries and choose which ones belong in each version.

## Tech stack

- **NiceGUI:** The current local web interface for editing resume data.
- **FastAPI:** The cloud-ready API for reading, saving, and building resumes.
- **Supabase:** Planned production authentication and PostgreSQL-backed storage.
- **Typst:** Generates polished PDF resumes from structured data.
- **Docker:** Packages the API and Typst runtime for deployment.
- **Python:** Connects the editor, API, persistence layer, and document generator.

## Use locally

Install the dependencies from the project directory:

```powershell
python -m pip install -r requirements.txt
```

Start the local editor:

```powershell
python frontend/src/gui.py
```

Open `http://localhost:8080`. Use **Master Editor** to maintain your contact information, education, work experience, projects, certifications, and skills. Use **Modular Builder** to select the experience entries for a targeted resume and save reusable profile choices.

Your local master data is stored in `backend/master_data/master_resume.json`, and local targeted profiles are stored in `backend/profiles/`. These files are useful for local development and backups.

## Use the API locally

Start the API in a second terminal:

```powershell
uvicorn backend.src.api:app --reload --port 8000
```

The API uses `local-development-token` by default during development. Its main operations are:

- `GET /health` checks whether the service is running.
- `GET /api/v1/me/master` reads your master document.
- `PUT /api/v1/me/master` saves your master document.
- `POST /api/v1/me/build` generates and downloads a PDF.

Send the development token with API requests:

```powershell
curl http://localhost:8000/api/v1/me/master `
	-H "Authorization: Bearer local-development-token"
```

## Use the web frontend

The deployable React client is in `frontend/web`. Run it locally with Node.js:

```powershell
cd frontend/web
npm install
npm run dev
```

It expects the API at `http://localhost:8000` by default. To use another API, copy `frontend/web/.env.example` to `frontend/web/.env` and set `VITE_API_URL`.

For cloud deployment, authentication and persistent storage configuration are documented in [docs/deployment.md](docs/deployment.md).
=======
For a forgetful mind, this is the anchor to bring your thoughts together. 
>>>>>>> 5cf2b2bc48764b22a03aa1d3e091e4e2d0ecf58c
