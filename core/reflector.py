import json
from pathlib import Path
from openai import OpenAI
import os

MEMORY_PATH = "ingested/memory.jsonl"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_by_tag(tag: str) -> str:
    if not Path(MEMORY_PATH).exists():
        return "Aucune mémoire disponible."

    entries = [json.loads(line) for line in open(MEMORY_PATH, encoding="utf-8")]
    relevant = [e for e in entries if tag in e["metadata"].get("tags", [])]

    if not relevant:
        return f"Aucune entrée avec le tag '{tag}'."

    content = "\n\n".join([f"- {e['text'][:500]}" for e in relevant])
    prompt = f"""Voici des extraits de la mémoire de l'utilisateur, tous associés au tag '{tag}' :

{content}

Fais une synthèse claire de ses idées, réflexions ou apprentissages à ce sujet, comme si tu faisais un résumé personnel.
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


def reflect_on_last_entries(n=5) -> str:
    if not Path(MEMORY_PATH).exists():
        return "Mémoire vide."

    entries = [json.loads(line) for line in open(MEMORY_PATH, encoding="utf-8")]
    latest = sorted(entries, key=lambda x: x["metadata"]["created_at"], reverse=True)[:n]

    content = "\n\n".join([f"- {e['text'][:500]}" for e in latest])
    prompt = f"""Voici les dernières entrées mémorielles de l'utilisateur :

{content}

Quelles sont les thématiques récurrentes ? Vois-tu des tendances ? Suggère une réflexion personnelle ou une synthèse à partir de ça.
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()
