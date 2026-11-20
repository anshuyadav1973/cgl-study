#!/usr/bin/env python3
import http.server
import socketserver
import json
import os
import sys
import urllib.parse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
DATA_DIR = os.path.join(BASE_DIR, "data")
TESTS_DIR = os.path.join(DATA_DIR, "tests")
PORT = int(os.environ.get("PORT", 3000))

# Import Database and Auth module
sys.path.insert(0, os.path.dirname(BASE_DIR))
import app.db as db

class ProductionAppHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)

    def get_auth_user(self):
        auth_header = self.headers.get("Authorization", "")
        token = None
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
        elif "token=" in self.path:
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            token = params.get("token", [None])[0]

        if token:
            return db.get_user_from_token(token)
        return None

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, DELETE")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, DELETE")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # Health Check
        if path == "/healthz" or path == "/api/health":
            return self.send_json({"status": "healthy", "service": "SSC CGL Blackhole Platform"})

        # API: Current Authenticated User
        if path == "/api/auth/me":
            user = self.get_auth_user()
            if user:
                return self.send_json({"authenticated": True, "user": user})
            return self.send_json({"authenticated": False, "user": None})

        # API: Available Tests List
        if path == "/api/tests":
            tests = []
            if os.path.exists(TESTS_DIR):
                for filename in sorted(os.listdir(TESTS_DIR)):
                    if filename.endswith(".json"):
                        filepath = os.path.join(TESTS_DIR, filename)
                        try:
                            with open(filepath, "r", encoding="utf-8") as f:
                                data = json.load(f)
                                tests.append({
                                    "id": data.get("id", filename[:-5]),
                                    "title": data.get("title", filename[:-5]),
                                    "subtitle": data.get("subtitle", ""),
                                    "category": data.get("category", "General"),
                                    "durationMinutes": data.get("durationMinutes", 25),
                                    "numQuestions": len(data.get("questions", [])),
                                    "marksPerQuestion": data.get("marksPerQuestion", 3),
                                    "negativeMarks": data.get("negativeMarks", 1)
                                })
                        except Exception:
                            pass
            return self.send_json(tests)

        # API: Specific Test Details (Protected: Login required to access test content)
        if path.startswith("/api/tests/"):
            user = self.get_auth_user()
            if not user:
                return self.send_json({"error": "Sign in required to access test content. Please log in or register."}, status=401)
            test_id = path.split("/api/tests/")[1].split("?")[0]
            target_file = None
            if os.path.exists(TESTS_DIR):
                for filename in os.listdir(TESTS_DIR):
                    if filename.endswith(".json"):
                        if filename == f"{test_id}.json" or filename[:-5] == test_id:
                            target_file = os.path.join(TESTS_DIR, filename)
                            break
                        filepath = os.path.join(TESTS_DIR, filename)
                        try:
                            with open(filepath, "r", encoding="utf-8") as f:
                                d = json.load(f)
                                if d.get("id") == test_id:
                                    target_file = filepath
                                    break
                        except Exception:
                            pass

            if target_file and os.path.exists(target_file):
                with open(target_file, "r", encoding="utf-8") as f:
                    return self.send_json(json.load(f))
            return self.send_json({"error": "Test not found"}, status=404)

        # API: In-Progress Test Resume Support
        if path == "/api/progress":
            user = self.get_auth_user()
            if not user:
                return self.send_json({})
            return self.send_json(db.get_all_user_progress(user['id']))

        if path.startswith("/api/progress/"):
            user = self.get_auth_user()
            if not user:
                return self.send_json({"error": "Unauthorized"}, status=401)
            t_id = path.split("/api/progress/")[1].split("?")[0]
            prog = db.get_test_progress(user['id'], t_id)
            return self.send_json(prog or {})

        # API: User Attempt History (Multi-Tenant, strict privacy: only authenticated user's history!)
        if path == "/api/history":
            user = self.get_auth_user()
            if not user:
                return self.send_json([])  # Guest/unauthenticated users have NO history displayed!
            history = db.get_user_history(user['id'])
            return self.send_json(history)

        # API: Real Live Leaderboard & All India Rankings
        if path == "/api/leaderboard":
            user = self.get_auth_user()
            current_user_id = user['id'] if user else None
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            test_id = params.get("testId", [None])[0]
            leaderboard_data = db.get_real_leaderboard(test_id=test_id, current_user_id=current_user_id)
            return self.send_json(leaderboard_data)

        # API: Real Test Statistics & Rank Comparison
        if path == "/api/test-stats":
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            test_id = params.get("testId", ['cgl-mains-mock-01'])[0]
            score_param = params.get("score", [None])[0]
            user_score = float(score_param) if score_param is not None else None
            stats = db.get_test_stats(test_id, user_score=user_score)
            return self.send_json(stats)

        # API: Personal Study Notes
        if path == "/api/notes":
            user = self.get_auth_user()
            if not user:
                return self.send_json({"error": "Unauthorized"}, status=401)
            notes = db.get_user_notes(user['id'])
            return self.send_json(notes)

        # API: Study Materials & Guides
        if path == "/api/study-materials":
            ga_plan_path = os.path.join(os.path.dirname(BASE_DIR), "General_Awareness_60_Day_Plan.md")
            math_tracker_path = os.path.join(os.path.dirname(BASE_DIR), "study_profile.md")
            ga_content = ""
            math_content = ""
            if os.path.exists(ga_plan_path):
                with open(ga_plan_path, "r", encoding="utf-8") as f:
                    ga_content = f.read()
            if os.path.exists(math_tracker_path):
                with open(math_tracker_path, "r", encoding="utf-8") as f:
                    math_content = f.read()

            materials = [
                {
                    "id": "mat_ga_plan",
                    "title": "SSC CGL 60-Day General Awareness Master Strategy",
                    "category": "General Awareness",
                    "description": "TCS 80/20 High-ROI theme breakdown, subject-wise weightage, daily 3-hour study timetable, and 60-day day-by-day plan.",
                    "content": ga_content
                },
                {
                    "id": "mat_math_tracker",
                    "title": "Mathematics Syllabus & Topic Mastery Tracker",
                    "category": "Quantitative Aptitude",
                    "description": "11 core mathematical modules, diagnostic weakness log, and progress monitoring.",
                    "content": math_content
                }
            ]
            return self.send_json(materials)

        # API: Admin Overview
        if path == "/api/admin/overview":
            user = self.get_auth_user()
            if not user or user.get('role') != 'admin':
                return self.send_json({"error": "Admin access required"}, status=403)
            overview = db.get_admin_overview()
            return self.send_json(overview)

        # API: Admin DB Status
        if path == "/api/admin/db-status":
            user = self.get_auth_user()
            if not user or user.get('role') != 'admin':
                return self.send_json({"error": "Admin access required"}, status=403)
            supa_url = db.get_setting("SUPABASE_URL", "")
            supa_key = db.get_setting("SUPABASE_KEY", "")
            connected = False
            msg = "Not configured"
            if supa_url and supa_key:
                connected, msg = db.test_supabase_connection(supa_url, supa_key)
            return self.send_json({
                "supabase_configured": bool(supa_url and supa_key),
                "supabase_url": supa_url[:12] + "..." if supa_url else "",
                "connection_status": msg,
                "is_connected": connected
            })

        # Candidate Profile
        if path == "/api/user/profile":
            user = self.get_auth_user()
            if not user:
                return self.send_json({"error": "Unauthorized. Please sign in."}, status=401)
            prof = db.get_user_profile(user['id'])
            return self.send_json(prof or user)

        # Static File Delivery
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b"{}"

        try:
            payload = json.loads(post_data.decode("utf-8")) if post_data else {}
        except Exception:
            payload = {}

        # Auth: Register
        if path == "/api/auth/register":
            email = payload.get("email", "")
            password = payload.get("password", "")
            full_name = payload.get("full_name", "")
            target_exam = payload.get("target_exam", "SSC CGL 2026")
            if not email or not password or not full_name:
                return self.send_json({"error": "All fields are required"}, status=400)
            if len(password) < 6:
                return self.send_json({"error": "Password must be at least 6 characters"}, status=400)
            data, err = db.register_user(email, password, full_name, target_exam)
            if err:
                return self.send_json({"error": err}, status=400)
            return self.send_json(data)

        # Auth: Login
        if path == "/api/auth/login":
            email = payload.get("email", "")
            password = payload.get("password", "")
            if not email or not password:
                return self.send_json({"error": "Email and password are required"}, status=400)
            data, err = db.authenticate_user(email, password)
            if err:
                return self.send_json({"error": err}, status=401)
            return self.send_json(data)

        # Auth: Logout
        if path == "/api/auth/logout":
            token = payload.get("token")
            if token:
                db.delete_session(token)
            return self.send_json({"status": "logged_out"})

        # Auth: Send OTP (Mobile / Gmail)
        if path == "/api/auth/send-otp":
            identifier = payload.get("identifier", "").strip()
            if not identifier:
                return self.send_json({"error": "Please provide your Mobile Number or Gmail address."}, status=400)
            clean_id = identifier.replace(" ", "").replace("-", "")
            otp = db.create_or_update_otp(clean_id)
            masked = clean_id[:3] + "•••" + (clean_id[-3:] if len(clean_id) > 6 else "")
            return self.send_json({
                "status": "success",
                "message": f"6-digit OTP code sent successfully to {masked}",
                "otp": otp
            })

        # Auth: Verify OTP & Sign In / Register
        if path == "/api/auth/verify-otp":
            identifier = payload.get("identifier", "").strip()
            otp = str(payload.get("otp", "")).strip()
            full_name = payload.get("full_name")
            target_exam = payload.get("target_exam", "SSC CGL 2026")
            if not identifier or not otp:
                return self.send_json({"error": "Identifier and 6-digit OTP code are required."}, status=400)
            clean_id = identifier.replace(" ", "").replace("-", "")
            valid, err = db.verify_otp_code(clean_id, otp)
            if not valid:
                return self.send_json({"error": err or "Invalid OTP code."}, status=400)
            user_data, token = db.login_or_register_with_otp(clean_id, full_name, target_exam)
            return self.send_json({"status": "success", "user": user_data, "token": token})

        # Candidate Profile Update
        if path in ["/api/user/profile", "/api/user/profile/update"]:
            user = self.get_auth_user()
            if not user:
                return self.send_json({"error": "Unauthorized. Please sign in."}, status=401)
            full_name = payload.get("full_name")
            target_exam = payload.get("target_exam")
            mobile = payload.get("mobile")
            email = payload.get("email")
            updated_prof, err = db.update_user_profile(user['id'], full_name, target_exam, mobile, email)
            if err:
                return self.send_json({"error": err}, status=400)
            return self.send_json({"status": "success", "profile": updated_prof})

        # Submit Test Result
        if path == "/api/submit":
            user = self.get_auth_user()
            user_id = user['id'] if user else "user_guest"
            stats = db.save_test_result(user_id, payload)
            return self.send_json({"status": "success", **stats})

        # Save Personal Note
        if path == "/api/notes":
            user = self.get_auth_user()
            if not user:
                return self.send_json({"error": "Unauthorized"}, status=401)
            note_id = payload.get("id")
            title = payload.get("title", "Untitled Note")
            content = payload.get("content", "")
            topic = payload.get("topic", "General")
            saved_id = db.save_user_note(user['id'], note_id, title, content, topic)
            return self.send_json({"status": "success", "id": saved_id})

        # Save In-Progress Test Progress
        if path == "/api/progress":
            user = self.get_auth_user()
            if not user:
                return self.send_json({"error": "Unauthorized"}, status=401)
            test_id = payload.get("testId")
            if not test_id:
                return self.send_json({"error": "testId is required"}, status=400)
            db.save_test_progress(user['id'], test_id, payload)
            return self.send_json({"status": "saved", "testId": test_id})

        # Admin: Configure Supabase
        if path == "/api/admin/db-config":
            user = self.get_auth_user()
            if not user or user.get('role') != 'admin':
                return self.send_json({"error": "Admin access required"}, status=403)
            url = payload.get("supabase_url", "").strip()
            key = payload.get("supabase_key", "").strip()
            if url and key:
                ok, msg = db.test_supabase_connection(url, key)
                if not ok:
                    return self.send_json({"error": f"Failed to connect to Supabase: {msg}"}, status=400)
                db.set_setting("SUPABASE_URL", url)
                db.set_setting("SUPABASE_KEY", key)
                return self.send_json({"status": "success", "message": "Supabase configured and connected!"})
            return self.send_json({"error": "URL and Key are required"}, status=400)

        # Admin: Sync to Supabase
        if path == "/api/admin/db-sync":
            user = self.get_auth_user()
            if not user or user.get('role') != 'admin':
                return self.send_json({"error": "Admin access required"}, status=403)
            result = db.sync_records_to_supabase()
            return self.send_json(result)

        # Admin: Save Custom Test
        if path == "/api/save-test":
            user = self.get_auth_user()
            if not user or user.get('role') != 'admin':
                return self.send_json({"error": "Admin access required"}, status=403)
            test_id = payload.get("id") or f"custom_test_{len(os.listdir(TESTS_DIR)) + 1}"
            payload["id"] = test_id
            target_file = os.path.join(TESTS_DIR, f"{test_id}.json")
            with open(target_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            return self.send_json({"status": "success", "id": test_id})

        # Clear User Test History
        if path == "/api/history/clear":
            user = self.get_auth_user()
            if not user:
                return self.send_json({"error": "Unauthorized. Please sign in."}, status=401)
            count = db.clear_user_history(user['id'], is_admin=False)
            return self.send_json({"status": "success", "cleared": count})

        # Admin: Clear All Test History Across Platform
        if path == "/api/admin/clear-all-data":
            user = self.get_auth_user()
            if not user or user.get('role') != 'admin':
                return self.send_json({"error": "Admin access required"}, status=403)
            count = db.clear_user_history(user['id'], is_admin=True)
            return self.send_json({"status": "success", "cleared_all": count})

        return self.send_json({"error": "Endpoint not found"}, status=404)

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path.startswith("/api/notes/"):
            user = self.get_auth_user()
            if not user:
                return self.send_json({"error": "Unauthorized"}, status=401)
            note_id = path.split("/api/notes/")[1]
            db.delete_user_note(user['id'], note_id)
            return self.send_json({"status": "success", "deleted": note_id})

        # Delete In-Progress Test Progress
        if path.startswith("/api/progress/"):
            user = self.get_auth_user()
            if not user:
                return self.send_json({"error": "Unauthorized"}, status=401)
            test_id = path.split("/api/progress/")[1]
            db.delete_test_progress(user['id'], test_id)
            return self.send_json({"status": "success", "deleted_progress": test_id})

        # Delete Single Test Attempt
        if path.startswith("/api/history/"):
            user = self.get_auth_user()
            if not user:
                return self.send_json({"error": "Unauthorized"}, status=401)
            attempt_id = path.split("/api/history/")[1]
            is_admin = user.get('role') == 'admin'
            deleted = db.delete_test_result(user['id'], attempt_id, is_admin=is_admin)
            if deleted:
                return self.send_json({"status": "success", "deleted": attempt_id})
            return self.send_json({"error": "Attempt not found or access denied"}, status=404)

        return self.send_json({"error": "Not found"}, status=404)

    def do_PUT(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            payload = json.loads(post_data.decode("utf-8")) if post_data else {}
        except Exception:
            payload = {}

        if path == "/api/user/profile":
            user = self.get_auth_user()
            if not user:
                return self.send_json({"error": "Unauthorized. Please sign in."}, status=401)
            full_name = payload.get("full_name")
            target_exam = payload.get("target_exam")
            mobile = payload.get("mobile")
            email = payload.get("email")
            updated_prof, err = db.update_user_profile(user['id'], full_name, target_exam, mobile, email)
            if err:
                return self.send_json({"error": err}, status=400)
            return self.send_json({"status": "success", "profile": updated_prof})

        return self.send_json({"error": "Not found"}, status=404)

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    allow_reuse_address = True

if __name__ == "__main__":
    print(f"Starting SSC CGL Production Platform on http://0.0.0.0:{PORT}")
    server = ThreadedHTTPServer(("0.0.0.0", PORT), ProductionAppHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        server.server_close()
