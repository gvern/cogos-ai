import chromadb
try:
    from sentence_transformers import SentenceTransformer
    SentenceTransformer_available = True
except ImportError as e:
    print(f"Warning: Could not import SentenceTransformer: {e}")
    SentenceTransformer_available = False

EMBEDDING_MODEL = None

def get_embedding_model():
    """Lazy initialization of the embedding model."""
    global EMBEDDING_MODEL
    if EMBEDDING_MODEL is None and SentenceTransformer_available:
        try:
            EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            print(f"Warning: Could not initialize SentenceTransformer: {e}")
            EMBEDDING_MODEL = None
    return EMBEDDING_MODEL
    
from config.secrets import get_api_key
from openai import OpenAI
from pathlib import Path
import chromadb.errors
from datetime import datetime
import uuid
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
        embedding_model = get_embedding_model()
        if embedding_model is None:
            return "🤖 Système d'embedding non disponible. Vérifiez la configuration des dépendances."
            
        collection = get_collection()

        # Embedding de la requête
        query_vec = embedding_model.encode(query).tolist()

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

def add_memory_entry(content: str, tags: list = None, source: str = None) -> bool:
    """
    Ajoute une entrée dans la mémoire vectorielle.
    
    Args:
        content: Le contenu textuel de l'entrée
        tags: Liste de tags pour catégoriser l'entrée
        source: Source de l'information (optionnel)
        
    Returns:
        bool: True si l'ajout a réussi, False sinon
    """
    try:
        embedding_model = get_embedding_model()
        if embedding_model is None:
            print("Warning: EMBEDDING_MODEL is not available. Cannot add entry.")
            return False
            
        collection = get_collection()
        
        # Générer un ID unique
        entry_id = str(uuid.uuid4())
        
        # Créer les métadonnées
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "source": source or "direct_input"
        }
        
        # Ajouter les tags aux métadonnées s'ils existent
        if tags:
            metadata["tags"] = ",".join(tags)
        
        # Encoder le contenu
        embedding = embedding_model.encode(content).tolist()
        
        # Ajouter à la collection
        collection.add(
            ids=[entry_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata]
        )
        
        return True
    except Exception as e:
        print(f"Erreur lors de l'ajout à la mémoire: {str(e)}")
        return False

def get_recent_entries(limit: int = 10) -> list:
    """
    Récupère les entrées les plus récentes de la mémoire.
    
    Args:
        limit: Nombre maximum d'entrées à récupérer
        
    Returns:
        list: Liste des entrées récentes avec leurs métadonnées
    """
    try:
        collection = get_collection()
        
        # Récupérer toutes les entrées (Chroma n'a pas de tri intégré)
        results = collection.get()
        
        entries = []
        
        # Traiter les résultats
        for i, doc in enumerate(results.get("documents", [])):
            metadata = results.get("metadatas", [])[i]
            entry_id = results.get("ids", [])[i]
            
            # Extraire les tags
            tags = []
            if metadata and "tags" in metadata:
                tags = metadata["tags"].split(",")
            
            entry = {
                "content": doc,
                "timestamp": metadata.get("timestamp", ""),
                "tags": tags,
                "source": metadata.get("source", ""),
                "embedding_id": entry_id
            }
            
            entries.append(entry)
        
        # Trier par timestamp (du plus récent au plus ancien)
        entries.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Limiter le nombre d'entrées
        return entries[:limit]
    except Exception as e:
        print(f"Erreur lors de la récupération des entrées récentes: {str(e)}")
        return []
