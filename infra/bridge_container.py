"""Root-only file bridge exposed as localhost HTTP inside a networkless container."""
from __future__ import annotations

import json
import os
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(os.environ["APPROVAL_GATE_BRIDGE_DIR"])


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/v1/chat/completions":
            self.send_error(404)
            return
        length = int(self.headers.get("content-length", "0"))
        if not 0 < length <= 4_000_000:
            self.send_error(413)
            return
        payload = self.rfile.read(length)
        request_id = uuid.uuid4().hex
        request_path = ROOT / "requests" / f"{request_id}.json"
        response_path = ROOT / "responses" / f"{request_id}.json"
        request_path.write_bytes(payload)
        deadline = time.monotonic() + 250
        while not response_path.exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        if not response_path.exists():
            self.send_error(504)
            return
        result = json.loads(response_path.read_text())
        response_path.unlink()
        if not result["ok"]:
            self.send_error(502, result["error"])
            return
        body = json.dumps(result["body"]).encode()
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
