python-for-ai — Weather data viewer

Summary
-------
This is a small Flask application that fetches historical weather data (Open-Meteo), saves raw JSON + a cleaned CSV, and generates a temperature plot per run.

Repository layout
-----------------
- `index.py` — Flask app (exposes `app`) and web routes.
- `get_data.py` — data fetching, processing, plotting, and logging.
- `templates/index.html` — main HTML template.
- `plots/` — generated CSVs, JSON backups, and PNG plots (runtime output).
- `requirements.txt` — Python dependencies.
- `Dockerfile`, `.dockerignore`, `Procfile` — deployment helpers.
- `README.md` — this file.

Run locally (Windows PowerShell)
-------------------------------
1. Create and activate a venv:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies and start (dev server):

```powershell
pip install -r requirements.txt
python index.py
```

The app listens on port 5000 by default. Open http://localhost:5000

Run with Gunicorn (production-like)
----------------------------------
On Linux/WSL/macOS or in a container:

```bash
pip install gunicorn
gunicorn app.index:app -b 0.0.0.0:5000 --workers 2
```

Docker (recommended for deployment)
----------------------------------
Build and run the included Docker image:

```bash
docker build -t python-for-ai:latest .
docker run -p 5000:5000 python-for-ai:latest
```

Heroku / Platform-as-a-Service
--------------------------------
This repo contains a `Procfile` so Heroku can run `gunicorn index:app`. Push to a Heroku remote and the platform will install `requirements.txt` and run the `web` process.

Notes, recommendations, and housekeeping
---------------------------------------
- `plots/` contains runtime output; add it to `.gitignore` if you don't want these files committed.
- `get_data.py` sets a non-interactive matplotlib backend so plotting works in containers.
- The app writes to `saved_data_log.csv`; ensure the process user has write permission to the project folder.

Recommended future organization (non-breaking)
---------------------------------------------
If you plan to grow this project, consider:
- Move Flask code into a package (e.g., `app/`) and put a small launcher in the repo root.
- Split static files and templates into `static/` and `templates/` (Flask-friendly layout).
- Add tests under `tests/` and a CI workflow to run them on push.

Troubleshooting
---------------
- If `docker` is not recognized, install Docker Desktop (Windows) and enable WSL2, or deploy to a PaaS (Heroku/Render).
- If `git push` is rejected, run `git pull --rebase origin main` or merge remote changes, then push.

What I did
---------
- Audited the repo structure (kept current layout unchanged to avoid breaking imports).
- Rewrote this `README.md` with clear run and deploy instructions and recommendations.

Next steps I can take (pick one)
-------------------------------
- Add `.gitignore` entries to exclude `plots/` and `.venv`.
- Auto-migrate the code into a package layout (`app/`) and update imports.
- Create a GitHub Actions workflow to build and test on push.

Updated: January 2026
wather-viewer — Deployment

This repository is a small Flask app that fetches historical weather data and generates plots and CSVs.

Quick steps to run locally (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python index.py
```

Run with Gunicorn (Linux/macOS or in container):

```bash
# run locally (requires gunicorn)
gunicorn index:app -b 0.0.0.0:5000 --workers 2

# build & run with Docker
docker build -t python-for-ai:latest .
docker run -p 5000:5000 python-for-ai:latest
```

Deployment notes:
- `index.py` exposes a Flask `app` object; use `gunicorn index:app` as the WSGI entrypoint.
- `.dockerignore` excludes the `plots` folder and venv files from the build context.
- `get_data.py` uses a non-interactive matplotlib backend (Agg) so it runs headless in containers.

If you want, I can run a local sanity check next (install deps in your venv and start the server). 
