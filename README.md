# python-for-ai — Deployment

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
