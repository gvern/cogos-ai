import json
from pathlib import Path
from openai import OpenAI

MEMORY_PATH = "ingested/memory.jsonl"
client = OpenAI()

def lint_entry(text: str) -> str:
    prompt = f"""
Tu es un assistant qui nettoie et améliore des notes personnelles.
Voici une note brute :

{text}

Réécris-la de manière plus claire, synthétique et lisible, sans changer le fond. Ajoute des listes ou titres si nécessaire.
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def auto_improve_memory():
    if not Path(MEMORY_PATH).exists():
        return

    entries = [json.loads(line) for line in open(MEMORY_PATH, encoding="utf-8")]
    improved = []

    for e in entries:
        improved_text = lint_entry(e["text"])
        e["text"] = improved_text
        improved.append(e)

    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        for e in improved:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")

    print(f"✅ {len(improved)} notes nettoyées et réécrites.")
