import json
from pathlib import Path

MEMORY_PATH = "ingested/memory.jsonl"

def load_memory():
    if not Path(MEMORY_PATH).exists():
        return []
    with open(MEMORY_PATH, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def save_memory(entries):
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")

def update_entry(index, new_text):
    entries = load_memory()
    if 0 <= index < len(entries):
        entries[index]["text"] = new_text
        save_memory(entries)
        return True
    return False

def delete_entry(index):
    entries = load_memory()
    if 0 <= index < len(entries):
        del entries[index]
        save_memory(entries)
        return True
    return False
