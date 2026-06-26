import json
import os
import hashlib
import time
import uuid
import urllib.parse
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

CHEAT_PIPE = "C:\\Windows\\Temp\\spectral_web_state.json"
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cheat_state.json")

KEYAUTH_NAME = "PANEL PRO"
KEYAUTH_OWNERID = "aI0QJLilxAN4DRFQpHJXruod74FZUh4I"
KEYAUTH_SECRET = "wq4kvTApTBOX8vOnW0U3X1y1Bl10xaHvpBzcZCqV8qj6RN9k"
KEYAUTH_VERSION = "1.0"

KEYAUTH_API = "https://www.keyauthpro.xyz/api/1.0"

cheat_state = {}
active_sessions = {}
keyauth_session = None
PORT = int(os.environ.get("SPECTRAL_PORT", 8080))


def keyauth_init():
    global keyauth_session
    try:
        payload = json.dumps({
            "type": "init",
            "name": KEYAUTH_NAME,
            "ownerid": KEYAUTH_OWNERID,
            "ver": KEYAUTH_VERSION
        }).encode()
        req = urllib.request.Request(KEYAUTH_API, data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        if data.get("success"):
            keyauth_session = data.get("sessionid", "")
            print(f"  [KeyAuth] Sesion iniciada: {keyauth_session[:8]}...")
            return True
        else:
            print(f"  [KeyAuth] Error: {data.get('message', 'unknown')}")
            return False
    except Exception as e:
        print(f"  [KeyAuth] Error de conexion: {e}")
        return False


def keyauth_login(username, password):
    global keyauth_session
    if not keyauth_session:
        keyauth_init()
    if not keyauth_session:
        return False, "KeyAuth no conectado", None
    try:
        payload = json.dumps({
            "type": "login",
            "username": username,
            "pass": password,
            "sessionid": keyauth_session,
            "name": KEYAUTH_NAME,
            "ownerid": KEYAUTH_OWNERID
        }).encode()
        req = urllib.request.Request(KEYAUTH_API, data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        if data.get("success"):
            info = data.get("info", {})
            subs = info.get("subscriptions", [])
            sub_info = subs[0] if subs else {}
            user_data = {
                "username": info.get("username", username),
                "subscriptions": subs,
                "ip": info.get("ip", ""),
                "hwid": info.get("hwid", ""),
                "expiry": sub_info.get("expiry", 0),
                "timeleft": sub_info.get("timeleft", 0),
                "subscription": sub_info.get("subscription", ""),
                "level": sub_info.get("level", "0")
            }
            return True, "Login exitoso", user_data
        else:
            return False, data.get("message", "Error desconocido"), None
    except Exception as e:
        return False, f"Error: {str(e)}", None


def load_state():
    global cheat_state
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                cheat_state = json.load(f)
        else:
            cheat_state = {}
    except Exception:
        cheat_state = {}


def save_state():
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(cheat_state, f, indent=2)
    except Exception:
        pass
    try:
        with open(CHEAT_PIPE, "w") as f:
            json.dump(cheat_state, f)
    except Exception:
        pass


class SpectralHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path == "/" or self.path == "/index.html":
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
                with open(html_path, "rb") as f:
                    self.wfile.write(f.read())
            elif self.path == "/api/status":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                pipe_ok = os.path.exists(CHEAT_PIPE)
                status = {"connected": pipe_ok, "keyauth": bool(keyauth_session)}
                self.wfile.write(json.dumps(status).encode())
            else:
                self.send_response(404)
                self.end_headers()
        except Exception:
            try:
                self.send_response(500)
                self.end_headers()
            except Exception:
                pass

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            data = json.loads(body)

            if self.path == "/api/auth":
                username = data.get("username", "")
                password = data.get("password", "")
                if not username or not password:
                    self._respond({"ok": False, "error": "Ingresa usuario y contrasena"})
                    return
                ok, msg, user_data = keyauth_login(username, password)
                if ok:
                    token = hashlib.md5((username + str(time.time())).encode()).hexdigest()
                    active_sessions[token] = {
                        "username": username,
                        "time": time.time(),
                        "user_data": user_data
                    }
                    self._respond({
                        "ok": True,
                        "token": token,
                        "user": user_data
                    })
                else:
                    self._respond({"ok": False, "error": msg})
                return

            token = self.headers.get("Authorization", "")
            if not self._check_token(token):
                self._respond({"error": "unauthorized"}, 401)
                return

            if self.path == "/api/toggle":
                feature = data.get("feature")
                value = data.get("value", False)
                cheat_state[feature] = value
                save_state()
                self._respond({"ok": True, "feature": feature, "value": value})

            elif self.path == "/api/slider":
                feature = data.get("feature")
                value = data.get("value", 0)
                cheat_state[feature] = value
                save_state()
                self._respond({"ok": True})

            elif self.path == "/api/select":
                feature = data.get("feature")
                value = data.get("value", 0)
                cheat_state[feature] = value
                save_state()
                self._respond({"ok": True})

            elif self.path == "/api/color":
                feature = data.get("feature")
                value = data.get("value", "#ffffff")
                cheat_state[feature] = value
                save_state()
                self._respond({"ok": True})

            elif self.path == "/api/runcmd":
                cmd = data.get("command", "")
                try:
                    os.system(cmd)
                    self._respond({"ok": True})
                except Exception as e:
                    self._respond({"ok": False, "error": str(e)})
            else:
                self._respond({"error": "unknown endpoint"})
        except Exception:
            try:
                self._respond({"error": "server error"})
            except Exception:
                pass

    def do_OPTIONS(self):
        try:
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            self.end_headers()
        except Exception:
            pass

    def _check_token(self, token):
        if not token.startswith("Bearer "):
            return False
        t = token[7:]
        if t in active_sessions:
            if time.time() - active_sessions[t]["time"] < 86400:
                return True
            del active_sessions[t]
        return False

    def _respond(self, obj, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode())

    def log_message(self, format, *args):
        pass


def main():
    load_state()
    cheat_state = {}
    save_state()

    print()
    print("  ╔════════════════════════════════════════════════╗")
    print("  ║       SPECTRAL X PRO - Panel de Control        ║")
    print("  ╚════════════════════════════════════════════════╝")
    print()
    print("  [1/2] Conectando con KeyAuth...")
    ka_ok = keyauth_init()
    if ka_ok:
        print("  [OK] KeyAuth conectado")
    else:
        print("  [!] KeyAuth sin conexion - modo offline")
    print()
    print(f"  Servidor en http://localhost:{PORT}")
    print()
    print("  Presiona Ctrl+C para detener")
    print()

    server = HTTPServer(("0.0.0.0", PORT), SpectralHandler)
    server.daemon_threads = True
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  [*] Servidor detenido")
        server.server_close()


if __name__ == "__main__":
    main()
