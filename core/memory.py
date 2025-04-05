import chromadb
from sentence_transformers import SentenceTransformer
from config.secrets import get_api_key
from openai import OpenAI
from pathlib import Path

EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
client = OpenAI(api_key=get_api_key())

# Initialize ChromaDB client with the new API
chroma_client = chromadb.PersistentClient(path="embeddings/chroma")

def query_memory(query: str, top_k=5) -> str:
    try:
        # Try to get the collection
        collection = chroma_client.get_collection(name="cogos_memory")
        
        query_vec = EMBEDDING_MODEL.encode(query).tolist()

        results = collection.query(
            query_embeddings=[query_vec],
            n_results=top_k
        )

        docs = results["documents"][0]
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
        
    except (ValueError, chromadb.errors.NoIndexException) as e:
        return "⚠️ Mémoire non disponible. Lancer `python core/ingest.py` pour indexer vos documents."
    except Exception as e:
        return f"⚠️ Erreur lors de la recherche en mémoire: {str(e)}"
