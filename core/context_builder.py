from core.context_loader import get_raw_context, update_context
from config.secrets import get_api_key
from openai import OpenAI
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

client = OpenAI(api_key=get_api_key())
MEMORY_PATH = Path("ingested/memory.jsonl")

# === INTELLIGENCE SEMANTIQUE ===

def summarize_recent_memory(n=5) -> str:
    entries = [json.loads(line) for line in open(MEMORY_PATH, encoding="utf-8")]
    latest = sorted(entries, key=lambda x: x["metadata"]["created_at"], reverse=True)[:n]
    text = "\n\n".join([e["text"] for e in latest])
    prompt = f"""
Voici les dernières notes personnelles de l'utilisateur :

{text}

Synthétise ce contenu en 2-3 phrases claires et utiles, identifiant les idées clés ou questions émergentes.
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


def generate_focus_tags(n=5) -> List[str]:
    entries = [json.loads(line) for line in open(MEMORY_PATH, encoding="utf-8")]
    latest = sorted(entries, key=lambda x: x["metadata"]["created_at"], reverse=True)[:10]
    text = "\n\n".join([e["text"] for e in latest])
    prompt = f"""
        Analyse les textes suivants. Identifie les principaux thèmes cognitifs ou intellectuels qui intéressent l'utilisateur actuellement.

        {text}

        Donne une liste de {n} mots-clés ou tags représentatifs.
        """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    tags_raw = response.choices[0].message.content.strip()
    return [tag.strip(" -•") for tag in tags_raw.splitlines() if tag.strip()]


def assess_progress_by_domain(domains: List[str]) -> Dict[str, str]:
    entries = [json.loads(line) for line in open(MEMORY_PATH, encoding="utf-8")]
    text = "\n\n".join([e["text"] for e in entries[-50:]])  # dernière cinquantaine
    prompt = f"""
        Voici un extrait de la mémoire utilisateur :

        {text}

        Évalue sa progression dans les domaines suivants :
        {', '.join(domains)}

        Pour chaque domaine, donne une étiquette : "novice", "intermédiaire", "avancé", "expert" + un commentaire.
        """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return {"progress_report": response.choices[0].message.content.strip()}

# === MCP UPDATE ===

def update_context_intelligently():
    context = get_raw_context()
    summary = summarize_recent_memory()
    tags = generate_focus_tags()
    context["memory"]["short_term"] = [summary]
    context["goals"] = tags  # provisoirement utilisé comme objectifs dynamiques
    update_context(context)
    print("✅ Contexte enrichi automatiquement.")
