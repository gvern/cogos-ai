import json
from openai import OpenAI
from pathlib import Path

MEMORY_PATH = "ingested/memory.jsonl"
OUTPUT_JSONL = "finetune/personal_memory.jsonl"
Path("finetune").mkdir(exist_ok=True)

def build_finetune_dataset():
    entries = [json.loads(line) for line in open(MEMORY_PATH, encoding="utf-8")]
    examples = []

    for e in entries:
        examples.append({
            "messages": [
                {"role": "user", "content": f"Peux-tu me rappeler ce que j'ai noté dans : {e['metadata']['filename']} ?"},
                {"role": "assistant", "content": e["text"]}
            ]
        })

    with open(OUTPUT_JSONL, "w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    print(f"✅ Fichier de fine-tuning généré : {OUTPUT_JSONL}")
