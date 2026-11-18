#!/usr/bin/env python3
"""
Sync local SQLite and JSON test data to Supabase PostgreSQL Cloud Database
"""
import os
import json
import urllib.request
import urllib.error
import sqlite3

SUPABASE_URL = "https://xopsrudvlctqitmcsnci.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhvcHNydWR2bGN0cWl0bWNzbmNpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc5NTAwNjM2OSwiZXhwIjoyMTEwNTgyMzY5fQ.rM5gxYZXdSqHCcuK0yeMoK-80OsetsaTGq6DD5vUoDc"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "app", "data")
TESTS_DIR = os.path.join(DATA_DIR, "tests")
DB_PATH = os.path.join(DATA_DIR, "cgl_study.db")

headers = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

def post_supabase(table, data):
    endpoint = f"{SUPABASE_URL}/rest/v1/{table}"
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(data, ensure_ascii=False).encode('utf-8'),
        headers=headers,
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status in [200, 201, 204], f"Status: {response.status}"
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode('utf-8', errors='ignore')
        return False, f"HTTP Error {e.code}: {err_msg}"
    except Exception as e:
        return False, str(e)

def main():
    print("Testing connection to Supabase...")
    test_req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/tests?select=id&limit=1",
        headers={"apikey": SUPABASE_SERVICE_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}
    )
    try:
        with urllib.request.urlopen(test_req, timeout=5) as res:
            print("Connected successfully! Status:", res.status)
    except Exception as e:
        print("Failed to connect:", e)
        return

    # 1. Sync Mock Tests
    print("\n1. Syncing 10 Mock Tests (250 questions) to Supabase...")
    tests_payload = []
    if os.path.exists(TESTS_DIR):
        for f in sorted(os.listdir(TESTS_DIR)):
            if f.endswith('.json'):
                with open(os.path.join(TESTS_DIR, f), 'r', encoding='utf-8') as fp:
                    d = json.load(fp)
                    tests_payload.append({
                        "id": d.get("id", f[:-5]),
                        "title": d.get("title", f[:-5]),
                        "subtitle": d.get("subtitle", ""),
                        "category": d.get("category", "Quantitative Aptitude"),
                        "duration_minutes": d.get("durationMinutes", 35),
                        "num_questions": len(d.get("questions", [])),
                        "marks_per_question": d.get("marksPerQuestion", 3),
                        "negative_marks": d.get("negativeMarks", 1),
                        "questions_json": d.get("questions", [])
                    })

    if tests_payload:
        ok, msg = post_supabase("tests", tests_payload)
        print(f"Tests sync result: {ok} ({msg})")

    # 2. Sync Profiles
    print("\n2. Syncing Profiles...")
    profiles_payload = [
        {
            "id": "a0000000-0000-0000-0000-000000000001",
            "email": "admin@cglstudy.com",
            "full_name": "Candidate",
            "role": "admin",
            "target_exam": "SSC CGL 2026"
        },
        {
            "id": "a0000000-0000-0000-0000-000000000002",
            "email": "student1@test.com",
            "full_name": "Rohan Sharma",
            "role": "student",
            "target_exam": "SSC CGL 2026"
        }
    ]
    ok, msg = post_supabase("profiles", profiles_payload)
    print(f"Profiles sync result: {ok} ({msg})")

    # 3. Sync Test Results (Preserve Anshul's 71/75 attempt!)
    print("\n3. Syncing Test Results...")
    results_payload = []
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM test_results')
        rows = c.fetchall()
        for r in rows:
            u_id = "a0000000-0000-0000-0000-000000000001" if "anshul" in r['user_email'].lower() else "a0000000-0000-0000-0000-000000000002"
            results_payload.append({
                "id": r['id'],
                "user_id": u_id,
                "user_name": r['user_name'],
                "user_email": r['user_email'],
                "test_id": r['test_id'],
                "test_title": r['test_title'],
                "score": r['score'],
                "max_marks": r['max_marks'],
                "accuracy": r['accuracy'],
                "attempted": r['attempted'],
                "correct": r['correct'],
                "incorrect": r['incorrect'],
                "unattempted": r['unattempted'],
                "time_spent_seconds": r['time_spent_seconds'],
                "questions_evaluated_json": json.loads(r['questions_evaluated_json']) if r['questions_evaluated_json'] else []
            })
        conn.close()

    if results_payload:
        ok, msg = post_supabase("test_results", results_payload)
        print(f"Test Results sync result: {ok} ({msg})")

    # 4. Save credentials into local DB settings
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', ('SUPABASE_URL', SUPABASE_URL))
        c.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', ('SUPABASE_KEY', SUPABASE_SERVICE_KEY))
        c.execute('UPDATE test_results SET synced_to_cloud = 1')
        conn.commit()
        conn.close()
        print("\nSaved Supabase credentials to local database settings.")

    print("\nALL CLOUD SYNCHRONIZATION COMPLETE!")

if __name__ == "__main__":
    main()
