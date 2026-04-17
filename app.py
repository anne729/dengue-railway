from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import sqlite3, os, uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db():
    conn = sqlite3.connect('reports.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS reports (
            id TEXT PRIMARY KEY,
            lat REAL,
            lng REAL,
            description TEXT,
            photo_path TEXT,
            kelurahan TEXT,
            created_at TEXT
        )''')
init_db()

# ── HALAMAN ──
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/statistik')
def statistik():
    return render_template('statistik.html')

@app.route('/edukasi')
def edukasi():
    return render_template('edukasi.html')

@app.route('/peta')
def peta():
    return render_template('peta.html')

# ── API ──
@app.route('/api/report', methods=['POST'])
def submit_report():
    data = request.form
    photo = request.files.get('photo')
    photo_path = None

    if photo:
        filename = f"{uuid.uuid4().hex}.jpg"
        photo.save(os.path.join(UPLOAD_FOLDER, filename))
        photo_path = filename

    report_id = uuid.uuid4().hex
    with get_db() as conn:
        conn.execute('INSERT INTO reports VALUES (?,?,?,?,?,?,?)', (
            report_id,
            float(data.get('lat', 0)),
            float(data.get('lng', 0)),
            data.get('description', ''),
            photo_path,
            data.get('kelurahan', 'Tidak diketahui'),
            datetime.now().isoformat()
        ))
    return jsonify({'status': 'ok', 'id': report_id})

@app.route('/api/reports', methods=['GET'])
def get_reports():
    with get_db() as conn:
        rows = conn.execute(
            'SELECT * FROM reports ORDER BY created_at DESC'
        ).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/stats', methods=['GET'])
def get_stats():
    with get_db() as conn:
        rows = conn.execute('''
            SELECT kelurahan, COUNT(*) as total
            FROM reports
            GROUP BY kelurahan
            ORDER BY total DESC
        ''').fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
