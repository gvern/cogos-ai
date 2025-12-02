import sqlite3
import os
import datetime
from pathlib import Path
import json

OUTPUT_JSONL = "ingested/history.jsonl"

def fetch_chrome_history(limit=100):
    history_path = os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/History")
    if not Path(history_path).exists():
        print("❌ Historique Chrome non trouvé.")
        return

    conn = sqlite3.connect(history_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT ?
    """, (limit,))

    entries = []
    for url, title, last_visit_time in cursor.fetchall():
        # Chrome timestamps start from Jan 1, 1601 — convert to readable datetime
        ts = datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=last_visit_time)
        entries.append({
            "text": f"{title} — {url}",
            "metadata": {
                "source": "browser",
                "created_at": ts.isoformat(),
                "tags": ["chrome", "navigation", "web"]
            }
        })

    with open(OUTPUT_JSONL, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"✅ {len(entries)} entrées importées depuis Chrome.")

if __name__ == "__main__":
    fetch_chrome_history()
