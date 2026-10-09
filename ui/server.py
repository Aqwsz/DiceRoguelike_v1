"""Local HTTP server for the Dice Roguelike browser UI.

Run from the project root:
  python3 -m ui.server
Then open http://127.0.0.1:8765
"""

from __future__ import annotations

import json
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

# Project root on sys.path when run as python3 -m ui.server
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from ui.session import GameSession  # noqa: E402

HOST = "127.0.0.1"
PORT = 8765
SESSION = GameSession()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC, **kwargs)

    def log_message(self, fmt, *args):
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), fmt % args))

    def _json(self, code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def end_headers(self):
        # Avoid stale JS/CSS after edits (normal refresh was serving cached app.js).
        if self.path.endswith((".js", ".css", ".html")) or self.path in ("/", "/index.html"):
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/state":
            return self._json(200, SESSION.snapshot())
        if path in ("/", "/index.html"):
            self.path = "/index.html"
        return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/new":
            return self._json(200, SESSION.start(from_save=False))
        if path == "/api/continue":
            return self._json(200, SESSION.start(from_save=True))
        if path == "/api/save":
            return self._json(200, SESSION.save_game())
        if path == "/api/quit":
            data = self._read_json()
            return self._json(200, SESSION.quit_to_title(save=bool(data.get("save"))))
        if path == "/api/choose":
            data = self._read_json()
            index = data.get("index", 0)
            try:
                index = int(index)
            except (TypeError, ValueError):
                index = 0
            return self._json(200, SESSION.choose(index))
        if path == "/api/advance":
            return self._json(200, SESSION.advance())
        if path == "/api/settings":
            data = self._read_json()
            if "auto_play" in data:
                return self._json(200, SESSION.set_auto_play(bool(data["auto_play"])))
            return self._json(200, SESSION.snapshot())
        if path == "/api/inventory/equip":
            data = self._read_json()
            try:
                item_id = int(data.get("item_id"))
                hero_index = int(data.get("hero_index", 0))
            except (TypeError, ValueError):
                return self._json(400, {"error": "bad item_id or hero_index"})
            face_slot = data.get("face_slot", None)
            if face_slot is not None:
                try:
                    face_slot = int(face_slot)
                except (TypeError, ValueError):
                    face_slot = None
            return self._json(200, SESSION.equip_from_bag(item_id, hero_index, face_slot))
        if path == "/api/inventory/unequip":
            data = self._read_json()
            try:
                item_id = int(data.get("item_id"))
            except (TypeError, ValueError):
                return self._json(400, {"error": "bad item_id"})
            return self._json(200, SESSION.unequip_to_bag(item_id))
        self._json(404, {"error": "not found"})


def main():
    os.chdir(STATIC)
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Dice Roguelike UI → http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nBye.")
        server.server_close()


if __name__ == "__main__":
    main()
