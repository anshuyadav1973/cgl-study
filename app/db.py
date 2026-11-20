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

    # Automatically synchronize cloud accounts from Supabase to SQLite on startup
    try:
        synced = sync_cloud_users_to_sqlite()
        if synced > 0:
            print(f"Synchronized {synced} user account(s) from Supabase cloud.")
    except Exception as e:
        pass

    try:
        synced_res = sync_results_from_supabase()
        if synced_res > 0:
            print(f"Synchronized {synced_res} test result(s) from Supabase cloud.")
    except Exception as e:
        pass

# --- Supabase Cloud Persistence for Accounts, Sessions & In-Progress Tests ---
import urllib.request
import urllib.error
import urllib.parse

def supabase_get_headers():
    key = get_setting('SUPABASE_KEY')
    return {
        'apikey': key,
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json'
    }

def supabase_save_user(user_dict):
    url = get_setting('SUPABASE_URL')
    key = get_setting('SUPABASE_KEY')
    if not url or not key:
        return False
    url = url.rstrip('/')
    email = user_dict['email'].strip().lower()
    note_id = 'auth_' + hashlib.sha256(email.encode('utf-8')).hexdigest()[:20]
    payload = {
        'id': note_id,
        'title': email,
        'content': json.dumps(user_dict, ensure_ascii=False),
        'topic': '__sys_auth_user'
    }
    try:
        req = urllib.request.Request(
            f"{url}/rest/v1/student_notes",
            data=json.dumps(payload).encode('utf-8'),
            headers={
                **supabase_get_headers(),
                'Prefer': 'resolution=merge-duplicates'
            },
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            return resp.status in [200, 201, 204]
    except Exception as e:
        print("Error saving user to Supabase:", e)
        return False

def supabase_get_user_by_email(email):
    url = get_setting('SUPABASE_URL')
    key = get_setting('SUPABASE_KEY')
    if not url or not key:
        return None
    url = url.rstrip('/')
    email = email.strip().lower()
    quoted = urllib.parse.quote(email)
    try:
        req = urllib.request.Request(
            f"{url}/rest/v1/student_notes?topic=eq.__sys_auth_user&title=eq.{quoted}&select=*",
            headers=supabase_get_headers()
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            rows = json.loads(resp.read().decode('utf-8'))
            if rows and rows[0].get('content'):
                return json.loads(rows[0]['content'])
    except Exception as e:
        print("Error fetching user from Supabase:", e)
    return None

def supabase_get_user_by_id(user_id):
    url = get_setting('SUPABASE_URL')
    key = get_setting('SUPABASE_KEY')
    if not url or not key:
        return None
    url = url.rstrip('/')
    try:
        req = urllib.request.Request(
            f"{url}/rest/v1/student_notes?topic=eq.__sys_auth_user&select=*&limit=100",
            headers=supabase_get_headers()
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            rows = json.loads(resp.read().decode('utf-8'))
            for r in rows:
                if r.get('content'):
                    try:
                        u = json.loads(r['content'])
                        if u.get('id') == user_id:
                            return u
                    except Exception:
                        pass
    except Exception as e:
        print("Error fetching user by id from Supabase:", e)
    return None

def supabase_save_session(token, user_id, expires_at):
    url = get_setting('SUPABASE_URL')
    key = get_setting('SUPABASE_KEY')
    if not url or not key:
        return False
    url = url.rstrip('/')
    note_id = 'sess_' + hashlib.sha256(token.encode('utf-8')).hexdigest()[:20]
    payload = {
        'id': note_id,
        'title': token,
        'content': json.dumps({'user_id': user_id, 'expires_at': expires_at}),
        'topic': '__sys_auth_session'
    }
    try:
        req = urllib.request.Request(
            f"{url}/rest/v1/student_notes",
            data=json.dumps(payload).encode('utf-8'),
            headers={
                **supabase_get_headers(),
                'Prefer': 'resolution=merge-duplicates'
            },
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            return resp.status in [200, 201, 204]
    except Exception as e:
        return False

def supabase_get_session(token):
    url = get_setting('SUPABASE_URL')
    key = get_setting('SUPABASE_KEY')
    if not url or not key:
        return None
    url = url.rstrip('/')
    quoted = urllib.parse.quote(token)
    try:
        req = urllib.request.Request(
            f"{url}/rest/v1/student_notes?topic=eq.__sys_auth_session&title=eq.{quoted}&select=*",
            headers=supabase_get_headers()
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            rows = json.loads(resp.read().decode('utf-8'))
            if rows and rows[0].get('content'):
                return json.loads(rows[0]['content'])
    except Exception as e:
        pass
    return None

def supabase_save_progress(user_id, test_id, progress_data):
    url = get_setting('SUPABASE_URL')
    key = get_setting('SUPABASE_KEY')
    if not url or not key:
        return False
    url = url.rstrip('/')
    composite_key = f"{user_id}:::{test_id}"
    note_id = 'prog_' + hashlib.sha256(composite_key.encode('utf-8')).hexdigest()[:20]
    payload = {
        'id': note_id,
        'title': composite_key,
        'content': json.dumps(progress_data, ensure_ascii=False),
        'topic': '__sys_test_progress'
    }
    try:
        req = urllib.request.Request(
            f"{url}/rest/v1/student_notes",
            data=json.dumps(payload).encode('utf-8'),
            headers={
                **supabase_get_headers(),
                'Prefer': 'resolution=merge-duplicates'
            },
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            return resp.status in [200, 201, 204]
    except Exception as e:
        print("Error saving progress to Supabase:", e)
        return False

def supabase_get_progress(user_id, test_id):
    url = get_setting('SUPABASE_URL')
    key = get_setting('SUPABASE_KEY')
    if not url or not key:
        return None
    url = url.rstrip('/')
    composite_key = f"{user_id}:::{test_id}"
    quoted = urllib.parse.quote(composite_key)
    try:
        req = urllib.request.Request(
            f"{url}/rest/v1/student_notes?topic=eq.__sys_test_progress&title=eq.{quoted}&select=*",
            headers=supabase_get_headers()
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            rows = json.loads(resp.read().decode('utf-8'))
            if rows and rows[0].get('content'):
                return json.loads(rows[0]['content'])
    except Exception as e:
        pass
    return None

def supabase_delete_progress(user_id, test_id):
    url = get_setting('SUPABASE_URL')
    key = get_setting('SUPABASE_KEY')
    if not url or not key:
        return False
    url = url.rstrip('/')
    composite_key = f"{user_id}:::{test_id}"
    quoted = urllib.parse.quote(composite_key)
    try:
        req = urllib.request.Request(
            f"{url}/rest/v1/student_notes?topic=eq.__sys_test_progress&title=eq.{quoted}",
            headers=supabase_get_headers(),
            method='DELETE'
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            return resp.status in [200, 204]
    except Exception as e:
        pass
    return False

def supabase_get_all_progress(user_id):
    url = get_setting('SUPABASE_URL')
    key = get_setting('SUPABASE_KEY')
    if not url or not key:
        return {}
    url = url.rstrip('/')
    prefix = f"{user_id}:::"
    try:
        req = urllib.request.Request(
            f"{url}/rest/v1/student_notes?topic=eq.__sys_test_progress&select=*&limit=100",
            headers=supabase_get_headers()
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            rows = json.loads(resp.read().decode('utf-8'))
            res = {}
            for r in rows:
                title = r.get('title', '')
                if title.startswith(prefix) and r.get('content'):
                    t_id = title[len(prefix):]
                    try:
                        res[t_id] = json.loads(r['content'])
                    except Exception:
                        pass
            return res
    except Exception as e:
        pass
    return {}

def sync_cloud_users_to_sqlite():
    url = get_setting('SUPABASE_URL')
    key = get_setting('SUPABASE_KEY')
    if not url or not key:
        return 0
    url = url.rstrip('/')
    try:
        req = urllib.request.Request(
            f"{url}/rest/v1/student_notes?topic=eq.__sys_auth_user&select=*&limit=200",
            headers=supabase_get_headers()
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            rows = json.loads(resp.read().decode('utf-8'))
            if not rows:
                return 0
            conn = get_db()
            c = conn.cursor()
            synced = 0
            for r in rows:
                if r.get('content'):
                    try:
                        u = json.loads(r['content'])
                        c.execute('''
                        INSERT OR REPLACE INTO users (id, email, password_hash, salt, full_name, role, target_exam)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (u['id'], u['email'], u['password_hash'], u['salt'], u['full_name'], u.get('role', 'student'), u.get('target_exam', 'SSC CGL 2026')))
                        synced += 1
                    except Exception:
                        pass
            conn.commit()
            conn.close()
            return synced
    except Exception as e:
        print("Error syncing cloud users to SQLite:", e)
        return 0

# Auth Helpers
def register_user(email, password, full_name, target_exam='SSC CGL 2026', role='student'):
    conn = get_db()
    c = conn.cursor()
    email = email.strip().lower()

    # Check local SQLite
    c.execute('SELECT * FROM users WHERE email = ?', (email,))
    existing_user = c.fetchone()

    # If not in SQLite, check Supabase
    if not existing_user:
        cloud_u = supabase_get_user_by_email(email)
        if cloud_u:
            c.execute('''
            INSERT OR REPLACE INTO users (id, email, password_hash, salt, full_name, role, target_exam)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (cloud_u['id'], cloud_u['email'], cloud_u['password_hash'], cloud_u['salt'], cloud_u['full_name'], cloud_u.get('role', 'student'), cloud_u.get('target_exam', 'SSC CGL 2026')))
            conn.commit()
            c.execute('SELECT * FROM users WHERE id = ?', (cloud_u['id'],))
            existing_user = c.fetchone()

    if existing_user:
        # If user already exists and provided their matching password, log them in directly!
        if verify_password(password, existing_user['password_hash'], existing_user['salt']):
            token = create_session(c, existing_user['id'])
            conn.commit()
            expires = (datetime.utcnow() + timedelta(days=30)).isoformat()
            supabase_save_session(token, existing_user['id'], expires)
            user_data = {
                "id": existing_user['id'],
                "email": existing_user['email'],
                "full_name": existing_user['full_name'],
                "role": existing_user['role'],
                "target_exam": existing_user['target_exam']
            }
            conn.close()
            return {"user": user_data, "token": token, "already_existed": True}, None
        else:
            conn.close()
            return None, "An account with this email already exists. Please switch to the Sign In tab to log in."

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
        "full_name": full_name.strip(),
        "role": role,
        "target_exam": target_exam
    }

    # Persist user & session to Supabase immediately
    cloud_record = {
        "id": user_id,
        "email": email,
        "password_hash": pwd_hash,
        "salt": salt,
        "full_name": full_name.strip(),
        "role": role,
        "target_exam": target_exam
    }
    supabase_save_user(cloud_record)
    expires = (datetime.utcnow() + timedelta(days=30)).isoformat()
    supabase_save_session(token, user_id, expires)

    return {"user": user_data, "token": token}, None

def authenticate_user(email, password):
    conn = get_db()
    c = conn.cursor()
    email = email.strip().lower()

    # 1. Check local SQLite
    if email in ('anshul@cglstudy.com', 'admin@cglstudy.com'):
        c.execute('SELECT * FROM users WHERE email = ? OR email = ? OR id = ?', ('admin@cglstudy.com', 'anshul@cglstudy.com', 'user_admin_anshul'))
    else:
        c.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = c.fetchone()

    # 2. If not found in SQLite, check Supabase Cloud!
    if not user:
        cloud_u = supabase_get_user_by_email(email)
        if cloud_u:
            c.execute('''
            INSERT OR REPLACE INTO users (id, email, password_hash, salt, full_name, role, target_exam)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (cloud_u['id'], cloud_u['email'], cloud_u['password_hash'], cloud_u['salt'], cloud_u['full_name'], cloud_u.get('role', 'student'), cloud_u.get('target_exam', 'SSC CGL 2026')))
            conn.commit()
            c.execute('SELECT * FROM users WHERE id = ?', (cloud_u['id'],))
            user = c.fetchone()

    if not user:
        conn.close()
        return None, "No account found with this email. Please click 'Create New Account' to register."

    if not verify_password(password, user['password_hash'], user['salt']):
        conn.close()
        return None, "Incorrect password. Please verify your password and try again."

    token = create_session(c, user['id'])
    conn.commit()

    # Persist session to Supabase
    expires = (datetime.utcnow() + timedelta(days=30)).isoformat()
    supabase_save_session(token, user['id'], expires)

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
    if row:
        conn.close()
        d = dict(row)
        if 'anshul' in d.get('full_name', '').lower():
            d['full_name'] = 'Candidate'
        return d

    # If session not in SQLite, check Supabase
    cloud_sess = supabase_get_session(token)
    if cloud_sess:
        user_id = cloud_sess.get('user_id')
        c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        u_row = c.fetchone()
        if not u_row:
            cloud_u = supabase_get_user_by_id(user_id)
            if cloud_u:
                c.execute('''
                INSERT OR REPLACE INTO users (id, email, password_hash, salt, full_name, role, target_exam)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (cloud_u['id'], cloud_u['email'], cloud_u['password_hash'], cloud_u['salt'], cloud_u['full_name'], cloud_u.get('role', 'student'), cloud_u.get('target_exam', 'SSC CGL 2026')))
                conn.commit()
                c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
                u_row = c.fetchone()

        if u_row:
            c.execute('INSERT OR REPLACE INTO sessions (token, user_id, expires_at) VALUES (?, ?, ?)',
                      (token, user_id, cloud_sess.get('expires_at')))
            conn.commit()
            conn.close()
            d = dict(u_row)
            if 'anshul' in d.get('full_name', '').lower():
                d['full_name'] = 'Candidate'
            return d

    conn.close()
    return None

def delete_session(token):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM sessions WHERE token = ?', (token,))
    conn.commit()
    conn.close()

# Results & History Helpers
def get_test_stats(test_id, user_score=None):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM test_results')
    if c.fetchone()[0] == 0:
        conn.close()
        sync_results_from_supabase()
        conn = get_db()
        c = conn.cursor()

    c.execute('SELECT COUNT(*) as cnt, MAX(score) as max_s, AVG(score) as avg_s, MAX(accuracy) as max_acc, AVG(accuracy) as avg_acc, MIN(time_spent_seconds) as min_t, AVG(time_spent_seconds) as avg_t, MAX(attempted) as max_att, AVG(attempted) as avg_att FROM test_results WHERE test_id = ?', (test_id,))
    row = c.fetchone()

    total_candidates = (row['cnt'] or 0)
    if total_candidates == 0:
        conn.close()
        u_score = user_score if user_score is not None else 0
        return {
            "totalCandidates": 1 if user_score is not None else 0,
            "realRank": 1,
            "realPercentile": 100.0,
            "topper": {
                "score": u_score,
                "maxMarks": 75,
                "accuracy": 100,
                "attempted": 25,
                "timeFormatted": "15m 00s"
            },
            "average": {
                "score": u_score,
                "accuracy": 100,
                "attempted": 25,
                "timeFormatted": "15m 00s"
            }
        }

    c.execute('SELECT score, max_marks, accuracy, attempted, time_spent_seconds FROM test_results WHERE test_id = ? ORDER BY score DESC, accuracy DESC, time_spent_seconds ASC LIMIT 1', (test_id,))
    topper_row = c.fetchone()
    topper_t = topper_row['time_spent_seconds'] if topper_row else 0

    topper_stats = {
        "score": topper_row['score'] if topper_row else 0,
        "maxMarks": topper_row['max_marks'] if topper_row else 75,
        "accuracy": topper_row['accuracy'] if topper_row else 0,
        "attempted": topper_row['attempted'] if topper_row else 0,
        "timeFormatted": f"{(topper_t // 60)}m {(topper_t % 60):02d}s"
    }

    avg_t = int(row['avg_t'] or 0)
    average_stats = {
        "score": round(row['avg_s'] or 0, 1),
        "accuracy": round(row['avg_acc'] or 0, 1),
        "attempted": round(row['avg_att'] or 0, 1),
        "timeFormatted": f"{(avg_t // 60)}m {(avg_t % 60):02d}s"
    }

    real_rank = 1
    if user_score is not None:
        c.execute('SELECT COUNT(*) FROM test_results WHERE test_id = ? AND score > ?', (test_id, user_score))
        real_rank = c.fetchone()[0] + 1

    real_percentile = round(((total_candidates - real_rank + 1) / total_candidates) * 100, 1)

    conn.close()
    return {
        "totalCandidates": total_candidates,
        "realRank": real_rank,
        "realPercentile": real_percentile,
        "topper": topper_stats,
        "average": average_stats
    }

def get_real_leaderboard(test_id=None, current_user_id=None):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM test_results')
    if c.fetchone()[0] == 0:
        conn.close()
        sync_results_from_supabase()
        conn = get_db()
        c = conn.cursor()

    if test_id:
        c.execute('''
        SELECT 
            tr.id as attempt_id,
            tr.user_id,
            COALESCE(u.full_name, tr.user_name, 'Aspirant') as user_name,
            tr.test_id,
            tr.test_title,
            tr.score,
            tr.max_marks,
            tr.accuracy,
            tr.attempted,
            tr.time_spent_seconds,
            tr.created_at
        FROM test_results tr
        LEFT JOIN users u ON tr.user_id = u.id
        WHERE tr.test_id = ?
        ORDER BY tr.score DESC, tr.accuracy DESC, tr.time_spent_seconds ASC, tr.created_at ASC
        LIMIT 100
        ''', (test_id,))
    else:
        # Overall Leaderboard: highest score per user across all mock tests
        c.execute('''
        SELECT 
            tr.id as attempt_id,
            tr.user_id,
            COALESCE(u.full_name, tr.user_name, 'Aspirant') as user_name,
            tr.test_id,
            tr.test_title,
            tr.score,
            tr.max_marks,
            tr.accuracy,
            tr.attempted,
            tr.time_spent_seconds,
            tr.created_at
        FROM test_results tr
        LEFT JOIN users u ON tr.user_id = u.id
        WHERE tr.id IN (
            SELECT id FROM test_results t1
            WHERE t1.score = (
                SELECT MAX(t2.score) FROM test_results t2 WHERE t2.user_id = t1.user_id
            )
            GROUP BY t1.user_id
        )
        ORDER BY tr.score DESC, tr.accuracy DESC, tr.time_spent_seconds ASC, tr.created_at ASC
        LIMIT 100
        ''')

    rows = c.fetchall()
    total_entries = len(rows)
    leaderboard = []

    for idx, r in enumerate(rows):
        rank = idx + 1
        name = r['user_name'] or 'Aspirant'
        if 'anshul' in name.lower():
            name = 'Candidate'

        time_sec = r['time_spent_seconds'] or 0
        mins = time_sec // 60
        secs = time_sec % 60
        time_formatted = f"{mins}m {secs:02d}s"

        percentile = round(((total_entries - rank + 1) / total_entries) * 100, 1) if total_entries > 0 else 100.0
        is_you = bool(current_user_id and r['user_id'] == current_user_id)

        leaderboard.append({
            "rank": rank,
            "name": name,
            "isYou": is_you,
            "userId": r['user_id'],
            "testTitle": r['test_title'],
            "score": r['score'],
            "maxMarks": r['max_marks'],
            "scoreFormatted": f"{r['score']} / {r['max_marks']}",
            "accuracy": r['accuracy'],
            "accuracyFormatted": f"{r['accuracy']}%",
            "timeSpentSeconds": time_sec,
            "timeFormatted": time_formatted,
            "percentile": percentile,
            "percentileFormatted": f"{percentile}%",
            "attempted": r['attempted'],
            "date": (r['created_at'] or '')[:10]
        })

    conn.close()
    return leaderboard

def sync_results_from_supabase():
    url = get_setting('SUPABASE_URL')
    key = get_setting('SUPABASE_KEY')
    if not url or not key:
        return 0
    url = url.rstrip('/')
    try:
        req = urllib.request.Request(
            f"{url}/rest/v1/test_results?select=*&limit=500",
            headers=supabase_get_headers()
        )
        with urllib.request.urlopen(req, timeout=8) as res:
            rows = json.loads(res.read().decode('utf-8'))
            if not rows:
                return 0
            conn = get_db()
            c = conn.cursor()
            synced = 0
            for r in rows:
                c.execute('''
                INSERT OR IGNORE INTO test_results 
                (id, user_id, user_name, user_email, test_id, test_title, score, max_marks, accuracy, attempted, correct, incorrect, unattempted, time_spent_seconds, created_at, synced_to_cloud)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                ''', (
                    r['id'],
                    r.get('user_id') or 'usr_guest',
                    r.get('user_name', 'Candidate'),
                    r.get('user_email', ''),
                    r.get('test_id', 'cgl-mains-mock-01'),
                    r.get('test_title', 'SSC CGL Mock Test'),
                    r.get('score', 0),
                    r.get('max_marks', 75),
                    r.get('accuracy', 0),
                    r.get('attempted', 0),
                    r.get('correct', 0),
                    r.get('incorrect', 0),
                    r.get('unattempted', 0),
                    r.get('time_spent_seconds', 0),
                    r.get('created_at', datetime.utcnow().isoformat())
                ))
                synced += 1
            conn.commit()
            conn.close()
            return synced
    except Exception as e:
        print("Error pulling results from Supabase:", e)
        return 0

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
    test_id = result_data.get('testId', 'cgl-mains-mock-01')
    score = result_data.get('score', 0)

    c.execute('''
    INSERT INTO test_results 
    (id, user_id, user_name, user_email, test_id, test_title, score, max_marks, accuracy, attempted, correct, incorrect, unattempted, time_spent_seconds, questions_evaluated_json, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        res_id,
        user_id,
        u_name,
        u_email,
        test_id,
        result_data.get('testTitle', 'SSC CGL Mains Mock Test'),
        score,
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

    # Compute real stats & real rank for this candidate
    stats = get_test_stats(test_id, user_score=score)
    stats['attemptId'] = res_id

    # Sync to Supabase
    try:
        sync_records_to_supabase()
    except Exception:
        pass

    return stats

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
    c.execute("SELECT * FROM student_notes WHERE user_id = ? AND topic NOT LIKE '__sys_%' ORDER BY updated_at DESC", (user_id,))
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

    # Also persist to Supabase cloud
    try:
        supabase_save_progress(user_id, test_id, progress_data)
    except Exception:
        pass

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
            pass

    # If not in SQLite, check Supabase
    try:
        cloud_p = supabase_get_progress(user_id, test_id)
        if cloud_p:
            # Cache into SQLite
            conn = get_db()
            c = conn.cursor()
            c.execute('INSERT OR REPLACE INTO test_progress (user_id, test_id, progress_json) VALUES (?, ?, ?)',
                      (user_id, test_id, json.dumps(cloud_p, ensure_ascii=False)))
            conn.commit()
            conn.close()
            return cloud_p
    except Exception:
        pass
    return None

def delete_test_progress(user_id, test_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM test_progress WHERE user_id = ? AND test_id = ?', (user_id, test_id))
    conn.commit()
    conn.close()

    try:
        supabase_delete_progress(user_id, test_id)
    except Exception:
        pass

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

    # Merge with Supabase
    try:
        cloud_map = supabase_get_all_progress(user_id)
        for t_id, p_obj in cloud_map.items():
            if t_id not in result:
                result[t_id] = p_obj
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
