import os
import json
import fitz  # PyMuPDF
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
from typing import Optional

from openai import OpenAI  # Optionnel, remplacer si besoin

from sentence_transformers import SentenceTransformer, util
import faiss
import numpy as np
import chromadb

# === Config ===
SUPPORTED_TEXT_EXTENSIONS = [".md", ".txt"]
SUPPORTED_PDF_EXTENSIONS = [".pdf"]
SUPPORTED_EPUB_EXTENSIONS = [".epub"]
DATA_FOLDERS = {
    "notes": "data/notes",
    "books": "data/books",
    "journal": "data/journal",
    "local_files": "/Users/gustavevernay/Documents",  # Exemple : adapter ton chemin
}

OUTPUT_JSONL = "ingested/memory.jsonl"
EMBEDDING_INDEX = "embeddings/memory.index"
EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
EMBEDDING_DIM = EMBEDDING_MODEL.get_sentence_embedding_dimension()

# Initialize the new ChromaDB client
chroma_client = chromadb.PersistentClient(path="embeddings/chroma")

# === Extracteurs ===
def extract_text_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_text_pdf(path: Path) -> str:
    doc = fitz.open(path)
    return "\n".join([page.get_text() for page in doc])


def extract_text_epub(path: Path) -> str:
    book = epub.read_epub(str(path))
    text = ""
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), "html.parser")
            text += soup.get_text() + "\n"
    return text


def extract_tags(text: str, max_tags=5) -> list[str]:
    # Fallback simple, remplacer par LLM si souhaité
    keywords = set()
    for word in text.split():
        if word.istitle() and len(word) > 3:
            keywords.add(word.strip(".,()"))
        if len(keywords) >= max_tags:
            break
    return list(keywords)


def embed_text(text: str) -> np.ndarray:
    return EMBEDDING_MODEL.encode(text, convert_to_numpy=True)


# === Pipeline principal ===
def ingest():
    Path("ingested").mkdir(exist_ok=True)
    Path("embeddings").mkdir(exist_ok=True)

    memory = []
    vectors = []
    metadata_list = []

    for source_type, folder in DATA_FOLDERS.items():
        for file in Path(folder).glob("*"):
            try:
                if file.suffix in SUPPORTED_TEXT_EXTENSIONS:
                    text = extract_text_txt(file)
                elif file.suffix in SUPPORTED_PDF_EXTENSIONS:
                    text = extract_text_pdf(file)
                elif file.suffix in SUPPORTED_EPUB_EXTENSIONS:
                    text = extract_text_epub(file)
                else:
                    continue

                cleaned = text.strip()
                if not cleaned:
                    continue

                tags = extract_tags(cleaned)

                metadata = {
                    "source": source_type,
                    "filename": file.name,
                    "path": str(file),
                    "created_at": datetime.fromtimestamp(file.stat().st_ctime).isoformat(),
                    "modified_at": datetime.fromtimestamp(file.stat().st_mtime).isoformat(),
                    "tags": tags
                }

                memory.append({
                    "text": cleaned,
                    "metadata": metadata
                })

                vector = embed_text(cleaned)
                vectors.append(vector)
                metadata_list.append(metadata)

            except Exception as e:
                print(f"⚠️ Erreur fichier {file}: {e}")

    # Write memory to JSONL
    with open(OUTPUT_JSONL, "w", encoding="utf-8") as f:
        for entry in memory:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # Crée ou récupère une collection
    collection = chroma_client.get_or_create_collection(name="cogos_memory")

    # Vide l'ancienne indexation si besoin
    try:
        # Get all existing IDs in the collection
        existing_ids = collection.get()["ids"]
        if existing_ids:
            # Delete all existing documents
            collection.delete(ids=existing_ids)
            print(f"🧹 {len(existing_ids)} anciens documents supprimés.")
    except Exception as e:
        print(f"⚠️ Aucun document précédent à supprimer: {e}")

    # Ajoute les documents à Chroma
    for i, (text, vector, meta) in enumerate(zip([e["text"] for e in memory], vectors, metadata_list)):
        # Convert the tags list to a string for ChromaDB compatibility
        meta_copy = meta.copy()
        if "tags" in meta_copy and isinstance(meta_copy["tags"], list):
            meta_copy["tags"] = ", ".join(meta_copy["tags"])
        
        collection.add(
            documents=[text],
            embeddings=[vector.tolist()],
            metadatas=[meta_copy],
            ids=[f"doc_{i}"]
        )

    chroma_client.persist()
    print(f"✅ {len(memory)} documents indexés dans Chroma.")

    print(f"✅ Ingestion complète — {len(memory)} fichiers analysés.")


if __name__ == "__main__":
    ingest()
