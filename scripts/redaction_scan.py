"""Fail if any tracked text file contains an email address, a phone-number pattern, or a blocked name.
Blocked names are read from the environment (REDACT_NAMES="name1,name2") so the list itself is not published."""
import os, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"(?<![\w.])(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}(?![\w.])")
ALLOW_EMAIL = {"noreply@anthropic.com"}
names = [n.strip().lower() for n in os.environ.get("REDACT_NAMES", "").split(",") if n.strip()]
hits = []
for p in ROOT.rglob("*"):
    if not p.is_file() or any(part in {".git", "runs", "__pycache__", ".pytest_cache"} for part in p.parts):
        continue
    if p.suffix not in {".md", ".py", ".json", ".jsonl", ".feature", ".sh", ".txt", ".yml", ".yaml", ".ini", ".cfg", ""}:
        continue
    try:
        t = p.read_text()
    except Exception:
        continue
    for m in EMAIL.findall(t):
        if m not in ALLOW_EMAIL:
            hits.append((p, "email", m))
    for m in PHONE.findall(t):
        hits.append((p, "phone", m))
    low = t.lower()
    for n in names:
        if n in low:
            hits.append((p, "name", "[blocked name]"))
for h in hits:
    print(f"{h[0].relative_to(ROOT)}: {h[1]}: {h[2]}")
print("redaction scan:", "OK" if not hits else f"{len(hits)} hit(s)")
sys.exit(1 if hits else 0)
