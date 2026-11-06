# Putting this on GitHub

Order matters: the prereg timestamp is the first commit that contains it.

1. Read `prereg/P1_PREREG.md`. Fill in §4 model IDs, §6 budget, and your own row in §8. Do not change anything else
   without a `prereg/DEVIATIONS.md` entry.
2. On the machine that will run Phase 1 (Linux):
   ```bash
   unzip agent-approval-gate-lab-*.zip && cd agent-approval-gate-lab
   python3 -m pip install pytest
   sudo bash scripts/setup_enforced.sh
   REDACT_NAMES="<names to keep out, comma-separated>" sudo -E bash scripts/verify.sh --full
   ```
   It must print `VERIFY OK` and `enforced mode available: True`. If not, stop (Phase 0 gate).
3. Regenerate the reference outputs on this machine and the manifest, then commit:
   ```bash
   sudo -E python3 scripts/self_audit.py
   bash scripts/make_manifest.sh
   git init && git add -A && git commit -m "Phase 0: instrument + P1 preregistration (frozen)"
   gh repo create <owner>/agent-approval-gate-lab --private --source . --push
   ```
4. Optional external timestamp: `pip install opentimestamps-client && ots stamp prereg/P1_PREREG.md`, commit the `.ots`.
5. Phase 0.5 pilot, then Phase 1, following `docs/PLAN.md`. After each batch: commit raw, then `python3 scripts/analyze.py`, then commit its output.

Keep the repo private until you decide otherwise. Never commit API keys (`.env` is ignored).
