# Job Tracker - Ready to Deploy

Simple Flask app to track jobs with fields:
- Job Ref No
- Importer Name
- Received Time
- Status (Query / Pending / Complete)
- Query Details (shown only if Status = Query)

## Run locally
1. Create virtualenv and install:
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
2. Run:
```
python app.py
```
or with gunicorn:
```
gunicorn app:app --bind 0.0.0.0:5000
```

## Deploy
- Works on Render, Heroku, Replit. Include `Procfile` and `requirements.txt`.

The app uses SQLite database file `jobs.db` created automatically on start.
