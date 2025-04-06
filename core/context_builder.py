from core.context_loader import get_raw_context, update_context
from config.secrets import get_api_key
from openai import OpenAI
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

client = OpenAI(api_key=get_api_key())
MEMORY_PATH = Path("ingested/memory.jsonl")

# Domaines de connaissances pour suivi de progression
DEFAULT_DOMAINS = [
    "IA & Machine Learning", 
    "Programmation", 
    "Sciences", 
    "Philosophie", 
    "Art & Créativité", 
    "Productivité", 
    "Bien-être",
    "Connaissances générales"
]

# === INTELLIGENCE SEMANTIQUE ===

def summarize_recent_memory(n=5) -> str:
    if not MEMORY_PATH.exists():
        return "Aucune mémoire disponible."
    
    entries = [json.loads(line) for line in open(MEMORY_PATH, encoding="utf-8") if line.strip()]
    latest = sorted(entries, key=lambda x: x["metadata"]["created_at"], reverse=True)[:n]
    
    if not latest:
        return "Aucune entrée récente trouvée."
    
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
    if not MEMORY_PATH.exists():
        return ["Aucune mémoire disponible"]
    
    entries = [json.loads(line) for line in open(MEMORY_PATH, encoding="utf-8") if line.strip()]
    
    if not entries:
        return ["Aucune entrée trouvée"]
    
    latest = sorted(entries, key=lambda x: x["metadata"]["created_at"], reverse=True)[:10]
    text = "\n\n".join([e["text"] for e in latest])
    prompt = f"""
Analyse les textes suivants. Identifie les principaux thèmes cognitifs ou intellectuels qui intéressent l'utilisateur actuellement.

{text}

Donne une liste de {n} mots-clés ou tags représentatifs, un par ligne.
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    tags_raw = response.choices[0].message.content.strip()
    return [tag.strip(" -•").capitalize() for tag in tags_raw.splitlines() if tag.strip()]


def assess_progress_by_domain(domains: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
    """
    Évalue la progression dans chaque domaine et retourne un score et un commentaire.
    
    Args:
        domains: Liste des domaines à évaluer. Si None, utilise les domaines par défaut.
        
    Returns:
        Un dictionnaire avec les domaines comme clés et des dictionnaires contenant
        "score" (0-100) et "comment" comme valeurs.
    """
    if domains is None:
        domains = DEFAULT_DOMAINS
    
    if not MEMORY_PATH.exists():
        return {domain: {"score": 10, "comment": "Données insuffisantes"} for domain in domains}
    
    entries = [json.loads(line) for line in open(MEMORY_PATH, encoding="utf-8") if line.strip()]
    
    if not entries:
        return {domain: {"score": 10, "comment": "Données insuffisantes"} for domain in domains}
    
    text = "\n\n".join([e["text"] for e in entries[-50:]])  # dernière cinquantaine
    prompt = f"""
Voici un extrait de la mémoire utilisateur :

{text}

Évalue sa progression dans les domaines suivants :
{', '.join(domains)}

Pour chaque domaine, donne exactement ceci :
1. Un score entre 0 et 100 représentant le niveau (0=novice, 50=intermédiaire, 80=avancé, 95+=expert)
2. Un bref commentaire (1 phrase max) sur les forces/faiblesses/progression

Format pour chaque domaine (respecte exactement ce format JSON) :
```
"Nom du domaine": {"score": X, "comment": "Commentaire"}
```
Assure-toi que la sortie est un objet JSON valide contenant tous les domaines.
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    try:
        # Essayer de parser le JSON dans la réponse
        response_text = response.choices[0].message.content.strip()
        # Chercher du JSON dans le texte (peut être entouré de ```json et ```)
        start = response_text.find("{")
        end = response_text.rfind("}") + 1
        if start >= 0 and end > start:
            json_str = response_text[start:end]
            progress_data = json.loads(json_str)
            
            # Vérifier que chaque domaine a bien les champs attendus
            for domain in domains:
                if domain not in progress_data:
                    progress_data[domain] = {"score": 10, "comment": "Données manquantes"}
                elif "score" not in progress_data[domain] or "comment" not in progress_data[domain]:
                    progress_data[domain] = {"score": 10, "comment": "Format incorrect"}
            
            return progress_data
    except Exception as e:
        print(f"Erreur lors du parsing du JSON: {e}")
    
    # Fallback si le parsing échoue
    return {domain: {"score": 30, "comment": "Évaluation automatique indisponible"} for domain in domains}


def generate_mindmap() -> Dict[str, Any]:
    """
    Génère une carte mentale basée sur les connaissances récentes.
    
    Returns:
        Un dictionnaire représentant une carte mentale simple.
    """
    if not MEMORY_PATH.exists():
        return {"root": "Connaissances", "children": []}
    
    entries = [json.loads(line) for line in open(MEMORY_PATH, encoding="utf-8") if line.strip()]
    
    if not entries:
        return {"root": "Connaissances", "children": []}
    
    # Extraire les 20 dernières entrées
    latest = sorted(entries, key=lambda x: x["metadata"]["created_at"], reverse=True)[:20]
    text = "\n\n".join([e["text"] for e in latest])
    
    prompt = f"""
Analyse ces textes et crée une carte mentale simple qui représente les connaissances de l'utilisateur.
La carte doit avoir un nœud central, et plusieurs branches principales avec des sous-branches.

{text}

Format exact attendu (JSON) :
{{
  "root": "Nœud central",
  "children": [
    {{
      "name": "Branche principale 1",
      "children": [
        {{ "name": "Sous-sujet 1.1" }},
        {{ "name": "Sous-sujet 1.2" }}
      ]
    }},
    {{
      "name": "Branche principale 2",
      "children": [
        {{ "name": "Sous-sujet 2.1" }}
      ]
    }}
  ]
}}

Limite la complexité à 4-5 branches principales maximum, chacune avec 2-3 sous-sujets.
Assure-toi que la sortie est un objet JSON valide respectant exactement cette structure.
"""
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    try:
        response_text = response.choices[0].message.content.strip()
        # Chercher le JSON dans la réponse
        start = response_text.find("{")
        end = response_text.rfind("}") + 1
        if start >= 0 and end > start:
            json_str = response_text[start:end]
            mindmap = json.loads(json_str)
            return mindmap
    except Exception as e:
        print(f"Erreur lors de la génération de la carte mentale: {e}")
    
    # Carte mentale par défaut en cas d'erreur
    return {
        "root": "Connaissances",
        "children": [
            {
                "name": "Sujet 1",
                "children": [{"name": "Sous-sujet 1.1"}]
            },
            {
                "name": "Sujet 2",
                "children": [{"name": "Sous-sujet 2.1"}]
            }
        ]
    }


# === MCP UPDATE ===

def update_context_intelligently(run_all: bool = False) -> Dict[str, Any]:
    """
    Met à jour le contexte de façon intelligente et renvoie un rapport de progression.
    
    Args:
        run_all: Si True, exécute toutes les analyses (plus long mais plus complet)
        
    Returns:
        Un dictionnaire contenant les données de progression
    """
    context = get_raw_context()
    
    # Initialiser le contexte s'il est vide
    if not context:
        context = {
            "name": "Utilisateur",
            "persona": {
                "role": "Chercheur en IA",
                "tone": "Curieux et analytique"
            },
            "goals": [],
            "memory": {
                "short_term": [],
                "long_term": []
            },
            "domains": {},
            "last_updated": ""
        }
    
    # Mise à jour du résumé récent
    summary = summarize_recent_memory()
    tags = generate_focus_tags()
    
    # Mettre à jour les champs de base
    context["memory"]["short_term"] = tags
    
    # Si goals est vide ou run_all est True, mettre à jour les objectifs
    if not context.get("goals") or run_all:
        context["goals"] = tags[:3]  # Utiliser les 3 premiers tags comme objectifs
    
    # Mettre à jour la progression par domaine si run_all est True
    if run_all:
        domains_progress = assess_progress_by_domain()
        context["domains"] = domains_progress
        
        # Générer une carte mentale
        context["mindmap"] = generate_mindmap()
    
    # Mise à jour de la date
    context["last_updated"] = datetime.now().isoformat()
    
    # Enregistrer le contexte mis à jour
    update_context(context)
    
    # Préparer le rapport
    report = {
        "summary": summary,
        "tags": tags,
        "timestamp": datetime.now().isoformat(),
    }
    
    if run_all:
        report["domains"] = context.get("domains", {})
        report["mindmap"] = context.get("mindmap", {})
    
    return report


def get_domain_scores() -> Dict[str, int]:
    """
    Récupère les scores de progression par domaine.
    
    Returns:
        Un dictionnaire avec les domaines comme clés et les scores comme valeurs.
    """
    context = get_raw_context()
    domains = context.get("domains", {})
    
    scores = {}
    for domain, data in domains.items():
        if isinstance(data, dict) and "score" in data:
            scores[domain] = data["score"]
        else:
            scores[domain] = 10  # Valeur par défaut
    
    # Ajouter les domaines manquants
    for domain in DEFAULT_DOMAINS:
        if domain not in scores:
            scores[domain] = 10
    
    return scores


def get_all_domains() -> List[str]:
    """Récupère la liste de tous les domaines connus."""
    context = get_raw_context()
    domains = list(context.get("domains", {}).keys())
    
    # Ajouter les domaines manquants depuis la liste par défaut
    for domain in DEFAULT_DOMAINS:
        if domain not in domains:
            domains.append(domain)
    
    return domains
