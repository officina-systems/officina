#!/usr/bin/env python3
"""
deploy_filter.py — OFFICINA Governance Filter deploy script.

Reads src/filters/officina_governance_filter.py from disk (Git source of truth)
and updates the filter in Open WebUI via direct SQLite write to webui.db.

Architecture:
  - Git (src/filters/officina_governance_filter.py) is the source of truth.
  - OWU stores functions in webui.db (SQLite), bind-mounted at data/open-webui/webui.db.
  - This script writes directly to webui.db — no REST API needed for code updates.
  - Valves (postgres_password, ollama_eval_model, etc.) are set manually in OWU Admin UI.

Usage:
    python scripts/deploy_filter.py

Environment variables (all optional):
    OWU_DB_PATH     Path to webui.db       (default: data/open-webui/webui.db)
    OWU_URL         Open WebUI base URL    (default: http://localhost:3000)
    OWU_API_KEY     OWU API key            (for valve reads only, optional)
    FILTER_ID       Filter id in OWU       (default: officina_governance_probe)
    DRY_RUN         Set to '1' to print actions without executing

v0.5.0 change: GEMINI_API_KEY removed — outlet now uses Ollama local (qwen2.5:3b).
No API keys required to run this script.

Secrets: OWU_API_KEY lives in Bitwarden (DEC-003). Never pass secrets as CLI args.
"""

import os
import sys
import json
import sqlite3
import requests
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Config from environment
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.join(SCRIPT_DIR, "..")

OWU_DB_PATH = os.environ.get(
    "OWU_DB_PATH",
    os.path.join(REPO_ROOT, "data", "open-webui", "webui.db")
)
OWU_URL = os.environ.get("OWU_URL", "http://localhost:3000").rstrip("/")
OWU_API_KEY = os.environ.get("OWU_API_KEY", "")
FILTER_ID = os.environ.get("FILTER_ID", "officina_governance_probe")
DRY_RUN = os.environ.get("DRY_RUN", "0") == "1"

FILTER_SOURCE_PATH = os.path.join(REPO_ROOT, "src", "filters", "officina_governance_filter.py")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def bail(msg):
    print(f"[ERROR] {msg}", file=sys.stderr)
    sys.exit(1)


def log(msg):
    print(f"[deploy_filter] {msg}")


def api_headers():
    return {
        "Authorization": f"Bearer {OWU_API_KEY}",
        "Content-Type": "application/json",
    }

# ---------------------------------------------------------------------------
# Steps
# ---------------------------------------------------------------------------

def read_source() -> str:
    path = os.path.abspath(FILTER_SOURCE_PATH)
    if not os.path.exists(path):
        bail(f"Filter source not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()
    log(f"Source read: {path} ({len(source)} bytes)")
    return source


def update_filter_sqlite(source: str):
    """Update filter content directly in webui.db."""
    db_path = os.path.abspath(OWU_DB_PATH)
    if not os.path.exists(db_path):
        bail(f"webui.db not found at: {db_path}")

    if DRY_RUN:
        log(f"[DRY RUN] Would UPDATE function '{FILTER_ID}' in {db_path}")
        return

    now = int(datetime.now(timezone.utc).timestamp())
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM function WHERE id = ?", (FILTER_ID,)
        )
        row = cursor.fetchone()
        if not row:
            bail(f"Filter '{FILTER_ID}' not found in webui.db. Install it manually first.")

        cursor.execute(
            "UPDATE function SET content = ?, updated_at = ? WHERE id = ?",
            (source, now, FILTER_ID)
        )
        conn.commit()
        log(f"webui.db updated — rows affected: {cursor.rowcount}")
    finally:
        conn.close()


def get_valves_api() -> dict:
    """Get current valves via OWU REST API (optional, for verification)."""
    if not OWU_API_KEY:
        return {}
    url = f"{OWU_URL}/api/v1/functions/{FILTER_ID}/valves"
    try:
        resp = requests.get(url, headers=api_headers(), timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return {}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    log(f"Filter ID: {FILTER_ID}")
    log(f"DB path:   {os.path.abspath(OWU_DB_PATH)}")
    if DRY_RUN:
        log("DRY RUN mode — no changes will be applied.")

    # 1. Read source from Git
    source = read_source()

    # 2. Update filter code directly in webui.db
    log("Updating filter code in webui.db...")
    update_filter_sqlite(source)
    log("Filter code updated OK.")

    # 3. Show current valves (optional, requires OWU_API_KEY)
    if OWU_API_KEY:
        valves = get_valves_api()
        if valves:
            log(f"Current valves: {json.dumps(valves, indent=2)}")
    else:
        log("OWU_API_KEY not set — skipping valve verification.")
        log("Verify valves manually in OWU Admin → Functions → officina_governance_probe → Valves.")

    log("")
    log("Deploy complete.")
    log("")
    log("Next steps:")
    log("  1. OWU Admin → Functions → officina_governance_probe → toggle OFF then ON")
    log("  2. Verify valves: postgres_password, ollama_eval_model=qwen2.5:3b")
    log("  3. Send a message in OWU and verify crystallization pressure detection.")


if __name__ == "__main__":
    main()
