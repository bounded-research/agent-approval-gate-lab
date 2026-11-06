"""Host side of an offline-container model bridge for engineering smoke runs.

Only forwards a request body to the fixed, local LM Studio endpoint. No arbitrary
destination, headers, or URL can be chosen by the container. The bridge directory
must be accessible to the harness root process and inaccessible to labagent.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def main() -> int:
    root = Path(sys.argv[1])
    requests_dir = root / "requests"
    responses_dir = root / "responses"
    requests_dir.mkdir(parents=True, exist_ok=True)
    responses_dir.mkdir(parents=True, exist_ok=True)
    last_work = time.monotonic()
    while time.monotonic() - last_work < 900:
        pending = sorted(requests_dir.glob("*.json"))
        if not pending:
            time.sleep(0.1)
            continue
        for request_path in pending:
            request_id = request_path.stem
            try:
                body = request_path.read_bytes()
                req = urllib.request.Request(
                    "http://127.0.0.1:1234/v1/chat/completions",
                    data=body,
                    headers={"content-type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=240) as response:
                    payload = response.read()
                result = {"ok": True, "body": json.loads(payload)}
            except Exception as exc:
                result = {"ok": False, "error": f"{type(exc).__name__}: {exc}"[:300]}
            temp_path = responses_dir / f"{request_id}.tmp"
            final_path = responses_dir / f"{request_id}.json"
            temp_path.write_text(json.dumps(result))
            os.replace(temp_path, final_path)
            request_path.unlink()
            last_work = time.monotonic()
            print(f"bridge_request={request_id} ok={result['ok']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
