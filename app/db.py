"""
Database Management Module for SSC CGL Portal
Supports:
1. Persistent Local SQLite (ACID compliant, zero dependencies)
2. Cloud PostgreSQL / Supabase Integration
3. Automatic Migration from legacy history.json
4. Multi-tenant Student Data Isolation
"""

import os
import sqlite3
import json
import hashlib
import secrets
import time
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "cgl_study.db")
LEGACY_HISTORY = os.path.join(DATA_DIR, "history.json")
ENV_FILE = os.path.join(BASE_DIR, ".env")

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password, salt=None):
    if not salt:
        salt = secrets.token_hex(16)
    # PBKDF2-HMAC-SHA256 with 100,000 iterations
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256', 
        password.encode('utf-8'), 
        salt.encode('utf-8'), 
        100000
    ).hex()
    return pwd_hash, salt

def verify_password(password, stored_hash, salt):
    test_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(test_hash, stored_hash)

def init_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = get_db()
    c = conn.cursor()

    # Users table
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT DEFAULT 'student',
        target_exam TEXT DEFAULT 'SSC CGL 2026',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Sessions table
    c.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        token TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        expires_at TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    ''')

    # Test Results table (Multi-tenant)
    c.execute('''
    CREATE TABLE IF NOT EXISTS test_results (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        user_name TEXT,
        user_email TEXT,
        test_id TEXT NOT NULL,
        test_title TEXT NOT NULL,
        score INTEGER NOT NULL,
        max_marks INTEGER DEFAULT 75,
        accuracy INTEGER DEFAULT 0,
        attempted INTEGER DEFAULT 0,
        correct INTEGER DEFAULT 0,
        incorrect INTEGER DEFAULT 0,
        unattempted INTEGER DEFAULT 0,
        time_spent_seconds INTEGER DEFAULT 0,
        questions_evaluated_json TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        synced_to_cloud INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    ''')

    # Student Personal Notes table
    c.execute('''
    CREATE TABLE IF NOT EXISTS student_notes (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        topic TEXT DEFAULT 'General',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    ''')

    # System Settings table (Supabase config, etc.)
    c.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    ''')

    # Active In-Progress Test State (Resume/Restart Support)
    c.execute('''
    CREATE TABLE IF NOT EXISTS test_progress (
        user_id TEXT NOT NULL,
        test_id TEXT NOT NULL,
        progress_json TEXT NOT NULL,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, test_id)
    )
    ''')

    conn.commit()

    # Create default admin account if none exists
    admin_id = "user_admin_anshul"
    c.execute('SELECT id FROM users WHERE id = ? OR email = ? OR email = ?', (admin_id, 'anshul@cglstudy.com', 'admin@cglstudy.com'))
    if not c.fetchone():
        pwd_hash, salt = hash_password('Anshul@2026')
        c.execute('''
        INSERT INTO users (id, email, password_hash, salt, full_name, role, target_exam)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (admin_id, 'admin@cglstudy.com', pwd_hash, salt, 'Candidate', 'admin', 'SSC CGL 2026'))
        conn.commit()

    # Migrate legacy history.json if exists and results table is empty
    c.execute('SELECT COUNT(*) as count FROM test_results')
    if c.fetchone()['count'] == 0 and os.path.exists(LEGACY_HISTORY):
        try:
            with open(LEGACY_HISTORY, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
            for idx, item in enumerate(history_data):
                res_id = item.get('attemptId') or f"att_legacy_{idx+1}_{int(time.time())}"
                c.execute('''
                INSERT OR IGNORE INTO test_results 
                (id, user_id, user_name, user_email, test_id, test_title, score, max_marks, accuracy, attempted, correct, incorrect, unattempted, time_spent_seconds, questions_evaluated_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    res_id,
                    admin_id,
                    'Candidate',
                    'admin@cglstudy.com',
                    item.get('testId', 'cgl-mains-mock-01'),
                    item.get('testTitle', 'SSC CGL Mains 2026 - Maths Mock Test #01'),
                    item.get('score', 0),
                    item.get('maxMarks', 75),
                    item.get('accuracy', 0),
                    item.get('attempted', 0),
                    item.get('correct', 0),
                    item.get('incorrect', 0),
                    item.get('unattempted', 0),
                    item.get('timeSpentSeconds', 0),
                    json.dumps(item.get('questions', []), ensure_ascii=False),
                    item.get('timestamp', datetime.utcnow().isoformat())
                ))
            conn.commit()
            print("Successfully migrated legacy history.json to database.")
        except Exception as e:
            print("Error migrating legacy history:", e)

    conn.close()

# Auth Helpers
def register_user(email, password, full_name, target_exam='SSC CGL 2026', role='student'):
    conn = get_db()
    c = conn.cursor()
    email = email.strip().lower()
    c.execute('SELECT id FROM users WHERE email = ?', (email,))
    if c.fetchone():
        conn.close()
        return None, "An account with this email already exists."

    user_id = f"usr_{secrets.token_hex(8)}"
    pwd_hash, salt = hash_password(password)
    c.execute('''
    INSERT INTO users (id, email, password_hash, salt, full_name, role, target_exam)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, email, pwd_hash, salt, full_name.strip(), role, target_exam))

    token = create_session(c, user_id)
    conn.commit()
    conn.close()

    user_data = {
        "id": user_id,
        "email": email,
        "full_name": full_name,
        "role": role,
        "target_exam": target_exam
    }
    return {"user": user_data, "token": token}, None

def authenticate_user(email, password):
    conn = get_db()
    c = conn.cursor()
    email = email.strip().lower()
    if email in ('anshul@cglstudy.com', 'admin@cglstudy.com'):
        c.execute('SELECT * FROM users WHERE email = ? OR email = ? OR id = ?', ('admin@cglstudy.com', 'anshul@cglstudy.com', 'user_admin_anshul'))
    else:
        c.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = c.fetchone()
    if not user:
        conn.close()
        return None, "Invalid email or password."

    if not verify_password(password, user['password_hash'], user['salt']):
        conn.close()
        return None, "Invalid email or password."

    token = create_session(c, user['id'])
    conn.commit()

    display_name = user['full_name']
    if 'anshul' in display_name.lower():
        display_name = 'Candidate'

    user_data = {
        "id": user['id'],
        "email": user['email'],
        "full_name": display_name,
        "role": user['role'],
        "target_exam": user['target_exam']
    }
    conn.close()
    return {"user": user_data, "token": token}, None

def create_session(cursor, user_id):
    token = secrets.token_hex(32)
    expires = (datetime.utcnow() + timedelta(days=30)).isoformat()
    cursor.execute('''
    INSERT INTO sessions (token, user_id, expires_at)
    VALUES (?, ?, ?)
    ''', (token, user_id, expires))
    return token

def get_user_from_token(token):
    if not token:
        return None
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    SELECT u.id, u.email, u.full_name, u.role, u.target_exam, s.expires_at 
    FROM sessions s 
    JOIN users u ON s.user_id = u.id 
    WHERE s.token = ?
    ''', (token,))
    row = c.fetchone()
    conn.close()
    if row:
        d = dict(row)
        if 'anshul' in d.get('full_name', '').lower():
            d['full_name'] = 'Candidate'
        return d
    return None

def delete_session(token):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM sessions WHERE token = ?', (token,))
    conn.commit()
    conn.close()

# Results & History Helpers
def save_test_result(user_id, result_data):
    conn = get_db()
    c = conn.cursor()
    
    # Fetch user details
    c.execute('SELECT full_name, email FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    u_name = user['full_name'] if user else 'Candidate'
    if 'anshul' in u_name.lower():
        u_name = 'Candidate'
    u_email = user['email'] if user else ''

    res_id = result_data.get('attemptId') or f"att_{secrets.token_hex(6)}_{int(time.time())}"
    questions_json = json.dumps(result_data.get('questions', []), ensure_ascii=False)

    c.execute('''
    INSERT INTO test_results 
    (id, user_id, user_name, user_email, test_id, test_title, score, max_marks, accuracy, attempted, correct, incorrect, unattempted, time_spent_seconds, questions_evaluated_json, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        res_id,
        user_id,
        u_name,
        u_email,
        result_data.get('testId', 'cgl-mains-mock-01'),
        result_data.get('testTitle', 'SSC CGL Mains Mock Test'),
        result_data.get('score', 0),
        result_data.get('maxMarks', 75),
        result_data.get('accuracy', 0),
        result_data.get('attempted', 0),
        result_data.get('correct', 0),
        result_data.get('incorrect', 0),
        result_data.get('unattempted', 0),
        result_data.get('timeSpentSeconds', 0),
        questions_json,
        result_data.get('timestamp') or datetime.utcnow().isoformat()
    ))
    conn.commit()

    # Also update legacy history.json for backward compatibility
    try:
        c.execute('SELECT * FROM test_results ORDER BY created_at ASC')
        rows = c.fetchall()
        export_list = []
        for r in rows:
            export_list.append({
                "testId": r['test_id'],
                "testTitle": r['test_title'],
                "timestamp": r['created_at'],
                "score": r['score'],
                "maxMarks": r['max_marks'],
                "accuracy": r['accuracy'],
                "attempted": r['attempted'],
                "correct": r['correct'],
                "incorrect": r['incorrect'],
                "unattempted": r['unattempted'],
                "timeSpentSeconds": r['time_spent_seconds'],
                "attemptId": r['id'],
                "userId": r['user_id'],
                "userName": r['user_name'],
                "questions": json.loads(r['questions_evaluated_json']) if r['questions_evaluated_json'] else []
            })
        with open(LEGACY_HISTORY, 'w', encoding='utf-8') as f:
            json.dump(export_list, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("Error syncing legacy history file:", e)

    conn.close()
    return res_id

def get_user_history(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
    SELECT * FROM test_results 
    WHERE user_id = ? 
    ORDER BY created_at ASC
    ''', (user_id,))
    rows = c.fetchall()
    conn.close()

    res = []
    for r in rows:
        res.append({
            "testId": r['test_id'],
            "testTitle": r['test_title'],
            "timestamp": r['created_at'],
            "score": r['score'],
            "maxMarks": r['max_marks'],
            "accuracy": r['accuracy'],
            "attempted": r['attempted'],
            "correct": r['correct'],
            "incorrect": r['incorrect'],
            "unattempted": r['unattempted'],
            "timeSpentSeconds": r['time_spent_seconds'],
            "attemptId": r['id'],
            "questions": json.loads(r['questions_evaluated_json']) if r['questions_evaluated_json'] else []
        })
    return res

def delete_test_result(user_id, attempt_id, is_admin=False):
    conn = get_db()
    c = conn.cursor()
    if is_admin:
        c.execute('DELETE FROM test_results WHERE id = ?', (attempt_id,))
    else:
        c.execute('DELETE FROM test_results WHERE id = ? AND user_id = ?', (attempt_id, user_id))
    deleted = c.rowcount > 0
    conn.commit()

    # Update legacy history file
    try:
        c.execute('SELECT * FROM test_results ORDER BY created_at ASC')
        rows = c.fetchall()
        export_list = []
        for r in rows:
            export_list.append({
                "testId": r['test_id'],
                "testTitle": r['test_title'],
                "timestamp": r['created_at'],
                "score": r['score'],
                "maxMarks": r['max_marks'],
                "accuracy": r['accuracy'],
                "attempted": r['attempted'],
                "correct": r['correct'],
                "incorrect": r['incorrect'],
                "unattempted": r['unattempted'],
                "timeSpentSeconds": r['time_spent_seconds'],
                "attemptId": r['id'],
                "userId": r['user_id'],
                "userName": r['user_name'],
                "questions": json.loads(r['questions_evaluated_json']) if r['questions_evaluated_json'] else []
            })
        with open(LEGACY_HISTORY, 'w', encoding='utf-8') as f:
            json.dump(export_list, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

    conn.close()

    # Delete from Supabase if configured
    supa_url = get_setting('SUPABASE_URL')
    supa_key = get_setting('SUPABASE_KEY')
    if supa_url and supa_key:
        try:
            req = urllib.request.Request(
                f"{supa_url.rstrip('/')}/rest/v1/test_results?id=eq.{attempt_id}",
                headers={"apikey": supa_key, "Authorization": f"Bearer {supa_key}"},
                method="DELETE"
            )
            with urllib.request.urlopen(req, timeout=5):
                pass
        except Exception:
            pass

    return deleted

def clear_user_history(user_id, is_admin=False):
    conn = get_db()
    c = conn.cursor()
    if is_admin:
        c.execute('DELETE FROM test_results')
    else:
        c.execute('DELETE FROM test_results WHERE user_id = ?', (user_id,))
    count = c.rowcount
    conn.commit()

    # Update legacy history
    try:
        c.execute('SELECT * FROM test_results ORDER BY created_at ASC')
        rows = c.fetchall()
        export_list = []
        for r in rows:
            export_list.append({
                "testId": r['test_id'],
                "testTitle": r['test_title'],
                "timestamp": r['created_at'],
                "score": r['score'],
                "maxMarks": r['max_marks'],
                "accuracy": r['accuracy'],
                "attempted": r['attempted'],
                "correct": r['correct'],
                "incorrect": r['incorrect'],
                "unattempted": r['unattempted'],
                "timeSpentSeconds": r['time_spent_seconds'],
                "attemptId": r['id'],
                "userId": r['user_id'],
                "userName": r['user_name'],
                "questions": json.loads(r['questions_evaluated_json']) if r['questions_evaluated_json'] else []
            })
        with open(LEGACY_HISTORY, 'w', encoding='utf-8') as f:
            json.dump(export_list, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

    conn.close()

    # Clear from Supabase
    supa_url = get_setting('SUPABASE_URL')
    supa_key = get_setting('SUPABASE_KEY')
    if supa_url and supa_key:
        try:
            param = "" if is_admin else f"?user_id=eq.{user_id}"
            req = urllib.request.Request(
                f"{supa_url.rstrip('/')}/rest/v1/test_results{param}",
                headers={"apikey": supa_key, "Authorization": f"Bearer {supa_key}"},
                method="DELETE"
            )
            with urllib.request.urlopen(req, timeout=5):
                pass
        except Exception:
            pass

    return count

# Personal Notes Helpers
def get_user_notes(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM student_notes WHERE user_id = ? ORDER BY updated_at DESC', (user_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def save_user_note(user_id, note_id, title, content, topic='General'):
    conn = get_db()
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    if note_id:
        c.execute('''
        UPDATE student_notes 
        SET title = ?, content = ?, topic = ?, updated_at = ?
        WHERE id = ? AND user_id = ?
        ''', (title, content, topic, now, note_id, user_id))
    else:
        note_id = f"note_{secrets.token_hex(6)}"
        c.execute('''
        INSERT INTO student_notes (id, user_id, title, content, topic, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (note_id, user_id, title, content, topic, now, now))
    conn.commit()
    conn.close()
    return note_id

def delete_user_note(user_id, note_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM student_notes WHERE id = ? AND user_id = ?', (note_id, user_id))
    conn.commit()
    conn.close()

# Admin Helpers
def get_admin_overview():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) as total_students FROM users WHERE role = "student"')
    total_students = c.fetchone()['total_students']

    c.execute('SELECT COUNT(*) as total_tests, AVG(score) as avg_score, AVG(accuracy) as avg_acc FROM test_results')
    test_stats = c.fetchone()

    c.execute('''
    SELECT id, email, full_name, target_exam, created_at,
           (SELECT COUNT(*) FROM test_results WHERE user_id = users.id) as tests_taken,
           (SELECT MAX(score) FROM test_results WHERE user_id = users.id) as highest_score
    FROM users 
    ORDER BY created_at DESC
    ''')
    students = [dict(r) for r in c.fetchall()]
    for s in students:
        if 'anshul' in s.get('full_name', '').lower():
            s['full_name'] = 'Candidate'
        if 'anshul' in s.get('email', '').lower():
            s['email'] = 'admin@cglstudy.com'

    c.execute('''
    SELECT id, user_name, user_email, test_title, score, max_marks, accuracy, time_spent_seconds, created_at
    FROM test_results 
    ORDER BY created_at DESC LIMIT 50
    ''')
    recent_submissions = [dict(r) for r in c.fetchall()]
    for r in recent_submissions:
        if 'anshul' in r.get('user_name', '').lower():
            r['user_name'] = 'Candidate'
        if 'anshul' in r.get('user_email', '').lower():
            r['user_email'] = 'admin@cglstudy.com'

    conn.close()
    return {
        "total_students": total_students,
        "total_submissions": test_stats['total_tests'] or 0,
        "avg_score": round(test_stats['avg_score'] or 0, 1),
        "avg_accuracy": round(test_stats['avg_acc'] or 0, 1),
        "students": students,
        "recent_submissions": recent_submissions
    }

# In-Progress Test Resume/Restart Persistence
def save_test_progress(user_id, test_id, progress_data):
    conn = get_db()
    c = conn.cursor()
    progress_json = json.dumps(progress_data, ensure_ascii=False)
    now = datetime.utcnow().isoformat()
    c.execute('''
    INSERT OR REPLACE INTO test_progress (user_id, test_id, progress_json, updated_at)
    VALUES (?, ?, ?, ?)
    ''', (user_id, test_id, progress_json, now))
    conn.commit()
    conn.close()

def get_test_progress(user_id, test_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT progress_json FROM test_progress WHERE user_id = ? AND test_id = ?', (user_id, test_id))
    row = c.fetchone()
    conn.close()
    if row and row['progress_json']:
        try:
            return json.loads(row['progress_json'])
        except Exception:
            return None
    return None

def delete_test_progress(user_id, test_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM test_progress WHERE user_id = ? AND test_id = ?', (user_id, test_id))
    conn.commit()
    conn.close()

def get_all_user_progress(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT test_id, progress_json, updated_at FROM test_progress WHERE user_id = ?', (user_id,))
    rows = c.fetchall()
    conn.close()
    result = {}
    for r in rows:
        try:
            result[r['test_id']] = json.loads(r['progress_json'])
        except Exception:
            pass
    return result

# Supabase Sync / Configuration
def get_setting(key, default=None):
    # Check environment variable first (for Render/cloud deployments)
    env_val = os.environ.get(key)
    if env_val:
        return env_val
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT value FROM settings WHERE key = ?', (key,))
    row = c.fetchone()
    conn.close()
    if row:
        return row['value']
    return default

def set_setting(key, value):
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))
    conn.commit()
    conn.close()

# Initialize DB when module loaded
init_db()


# --- Supabase Cloud Sync Engine ---
import urllib.request
import urllib.error

def test_supabase_connection(url, key):
    if not url or not key:
        return False, "Missing Supabase URL or Key."
    url = url.rstrip('/')
    endpoint = f"{url}/rest/v1/"
    req = urllib.request.Request(endpoint, headers={
        "apikey": key,
        "Authorization": f"Bearer {key}"
    })
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status in [200, 204]:
                return True, "Successfully connected to Supabase PostgreSQL REST API."
            return False, f"Unexpected response code: {response.status}"
    except urllib.error.HTTPError as e:
        if e.code == 404 or e.code == 200:
            return True, "Supabase endpoint reachable."
        return False, f"HTTP Error {e.code}: {e.reason}"
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def sync_records_to_supabase():
    url = get_setting('SUPABASE_URL')
    key = get_setting('SUPABASE_KEY')
    if not url or not key:
        return {"status": "skipped", "message": "Supabase credentials not configured yet."}
    
    url = url.rstrip('/')
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM test_results WHERE synced_to_cloud = 0')
    unsynced = c.fetchall()
    
    synced_count = 0
    errors = []
    
    for row in unsynced:
        payload = {
            "id": row['id'],
            "user_name": row['user_name'],
            "user_email": row['user_email'],
            "test_id": row['test_id'],
            "test_title": row['test_title'],
            "score": row['score'],
            "max_marks": row['max_marks'],
            "accuracy": row['accuracy'],
            "attempted": row['attempted'],
            "correct": row['correct'],
            "incorrect": row['incorrect'],
            "unattempted": row['unattempted'],
            "time_spent_seconds": row['time_spent_seconds'],
            "created_at": row['created_at']
        }
        try:
            req = urllib.request.Request(
                f"{url}/rest/v1/test_results",
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    "apikey": key,
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                    "Prefer": "resolution=merge-duplicates"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=8) as res:
                if res.status in [200, 201, 204]:
                    c.execute('UPDATE test_results SET synced_to_cloud = 1 WHERE id = ?', (row['id'],))
                    synced_count += 1
        except Exception as e:
            errors.append(f"Row {row['id']}: {str(e)}")
            
    conn.commit()
    conn.close()
    return {
        "status": "success",
        "synced": synced_count,
        "total_unsynced": len(unsynced),
        "errors": errors
    }
