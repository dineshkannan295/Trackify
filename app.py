from flask import Flask, render_template, request, redirect, url_for, g, jsonify
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'jobs.db')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.execute('''CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_ref TEXT NOT NULL,
        importer_name TEXT,
        received_time TEXT,
        status TEXT,
        query_details TEXT
    )''')
    db.commit()

@app.before_request
def before_request():
    init_db()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    db = get_db()
    cur = db.execute('SELECT * FROM jobs ORDER BY id DESC')
    jobs = cur.fetchall()
    return render_template('index.html', jobs=jobs)

@app.route('/add', methods=['POST'])
def add_job():
    job_ref = request.form.get('job_ref')
    importer = request.form.get('importer_name')
    received = request.form.get('received_time') or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    status = request.form.get('status')
    query = request.form.get('query_details') if status == 'Query' else ''
    db = get_db()
    db.execute('INSERT INTO jobs (job_ref, importer_name, received_time, status, query_details) VALUES (?, ?, ?, ?, ?)',
               (job_ref, importer, received, status, query))
    db.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:job_id>', methods=['GET','POST'])
def edit_job(job_id):
    db = get_db()
    if request.method == 'POST':
        job_ref = request.form.get('job_ref')
        importer = request.form.get('importer_name')
        received = request.form.get('received_time')
        status = request.form.get('status')
        query = request.form.get('query_details') if status == 'Query' else ''
        db.execute('UPDATE jobs SET job_ref=?, importer_name=?, received_time=?, status=?, query_details=? WHERE id=?',
                   (job_ref, importer, received, status, query, job_id))
        db.commit()
        return redirect(url_for('index'))
    else:
        cur = db.execute('SELECT * FROM jobs WHERE id=?', (job_id,))
        job = cur.fetchone()
        if not job:
            return 'Not found', 404
        return render_template('edit.html', job=job)

@app.route('/delete/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    db = get_db()
    db.execute('DELETE FROM jobs WHERE id=?', (job_id,))
    db.commit()
    return redirect(url_for('index'))

# Simple API to get job details (useful for external integration)
@app.route('/api/jobs')
def api_jobs():
    db = get_db()
    cur = db.execute('SELECT * FROM jobs ORDER BY id DESC')
    jobs = [dict(row) for row in cur.fetchall()]
    return jsonify(jobs)

if __name__ == '__main__':
    # Run with: gunicorn app:app --bind 0.0.0.0:$PORT
    app.run(host='0.0.0.0', port=5000, debug=True)
