import os
import json
from pathlib import Path
from datetime import datetime

SUPPORTED_EXTENSIONS = [".md", ".txt"]
DATA_FOLDERS = {
    "notes": "data/notes",
    "books": "data/books",
    "journal": "data/journal"
}
OUTPUT_PATH = "ingested/memory.jsonl"

def extract_text(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def ingest():
    Path("ingested").mkdir(exist_ok=True)

    memory = []
    for source_type, folder in DATA_FOLDERS.items():
        folder_path = Path(folder)
        for file in folder_path.glob("*"):
            if file.suffix.lower() in SUPPORTED_EXTENSIONS:
                content = extract_text(file)
                metadata = {
                    "source": source_type,
                    "filename": file.name,
                    "path": str(file),
                    "created_at": datetime.fromtimestamp(file.stat().st_ctime).isoformat(),
                    "modified_at": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                }
                memory.append({
                    "text": content.strip(),
                    "metadata": metadata
                })

    # Sauvegarde en JSONL
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for entry in memory:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"✅ Ingestion terminée : {len(memory)} fichiers ingérés.")
    print(f"📄 Résultat enregistré dans : {OUTPUT_PATH}")

if __name__ == "__main__":
    ingest()
