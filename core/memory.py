import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from pathlib import Path

EMBEDDING_DIM = 768
INDEX_PATH = "embeddings/memory.index"
MEMORY_PATH = "ingested/memory.jsonl"
EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

# Charge FAISS index + documents
def load_memory():
    index = faiss.read_index(INDEX_PATH)
    with open(MEMORY_PATH, "r", encoding="utf-8") as f:
        docs = [json.loads(line) for line in f]
    return index, docs

# Requête mémoire par similarité + synthèse LLM
def query_memory(query: str, top_k=5) -> str:
    if not Path(INDEX_PATH).exists() or not Path(MEMORY_PATH).exists():
        return "⚠️ Mémoire non disponible. Lancer `python core/ingest.py`."

    index, docs = load_memory()
    query_vec = EMBEDDING_MODEL.encode(query, convert_to_numpy=True).astype("float32").reshape(1, -1)
    scores, indices = index.search(query_vec, top_k)

    context = "\n\n".join([f"- {docs[i]['text'][:500]}" for i in indices[0] if i < len(docs)])

    prompt = f"""Tu es un assistant personnel qui puise dans les souvenirs de ton utilisateur. 
Voici ce que tu as trouvé en mémoire concernant la question : "{query}"

{context}

Donne une réponse claire, fidèle, et personnelle en français.
"""

    # Utilise OpenAI (remplacer par Gemini ou local LLM si besoin)
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()
