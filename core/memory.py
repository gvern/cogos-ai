import chromadb
from sentence_transformers import SentenceTransformer
from config.secrets import get_api_key
from openai import OpenAI
from pathlib import Path
import chromadb.errors

# Chargement des modèles
EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
client = OpenAI(api_key=get_api_key())

# ChromaDB client (local persistent store)
CHROMA_DIR = "embeddings/chroma"
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)

# Nom de la collection
COLLECTION_NAME = "cogos_memory"

def get_collection():
    try:
        return chroma_client.get_collection(name=COLLECTION_NAME)
    except chromadb.errors.CollectionNotFoundError:
        # Si la collection n'existe pas encore, la créer vide
        return chroma_client.create_collection(name=COLLECTION_NAME)

def query_memory(query: str, top_k: int = 5) -> str:
    try:
        collection = get_collection()

        # Embedding de la requête
        query_vec = EMBEDDING_MODEL.encode(query).tolist()

        # Recherche vectorielle
        results = collection.query(
            query_embeddings=[query_vec],
            n_results=top_k
        )

        docs = results.get("documents", [[]])[0]

        if not docs:
            return "🤖 Aucun souvenir trouvé en mémoire."

        # Contexte concaténé
        context = "\n\n".join([f"- {doc[:500]}" for doc in docs])

        prompt = f"""Tu es un assistant personnel qui puise dans les souvenirs de ton utilisateur. 
Voici ce que tu as trouvé en mémoire concernant la question : "{query}"

{context}

Donne une réponse claire, fidèle, et personnelle en français.
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content.strip()

    except chromadb.errors.NoIndexException:
        return "⚠️ Index mémoire manquant. Lance `python core/ingest.py` pour construire la mémoire."
    except Exception as e:
        return f"⚠️ Erreur mémoire : {str(e)}"
