import os
import json
<<<<<<< HEAD
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

# === Config ===
SUPPORTED_TEXT_EXTENSIONS = [".md", ".txt"]
SUPPORTED_PDF_EXTENSIONS = [".pdf"]
SUPPORTED_EPUB_EXTENSIONS = [".epub"]
=======
from pathlib import Path
from datetime import datetime

SUPPORTED_EXTENSIONS = [".md", ".txt"]
>>>>>>> 8159adc914993503bf86350ffdcd5cb351b49b99
DATA_FOLDERS = {
    "notes": "data/notes",
    "books": "data/books",
    "journal": "data/journal"
}
<<<<<<< HEAD
OUTPUT_JSONL = "ingested/memory.jsonl"
EMBEDDING_INDEX = "embeddings/memory.index"
EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
EMBEDDING_DIM = EMBEDDING_MODEL.get_sentence_embedding_dimension()


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

=======
OUTPUT_PATH = "ingested/memory.jsonl"

def extract_text(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def ingest():
    Path("ingested").mkdir(exist_ok=True)

    memory = []
    for source_type, folder in DATA_FOLDERS.items():
        folder_path = Path(folder)
        for file in folder_path.glob("*"):
            if file.suffix.lower() in SUPPORTED_EXTENSIONS:
                content = extract_text(file)
>>>>>>> 8159adc914993503bf86350ffdcd5cb351b49b99
                metadata = {
                    "source": source_type,
                    "filename": file.name,
                    "path": str(file),
                    "created_at": datetime.fromtimestamp(file.stat().st_ctime).isoformat(),
<<<<<<< HEAD
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

    # Write vector index (FAISS)
    if vectors:
        vectors_np = np.array(vectors).astype("float32")

        if vectors_np.shape[1] != EMBEDDING_DIM:
            raise ValueError(f"Inconsistent vector dimensions: got {vectors_np.shape[1]}, expected {EMBEDDING_DIM}")

        index = faiss.IndexFlatL2(EMBEDDING_DIM)
        index.add(vectors_np)

        faiss.write_index(index, EMBEDDING_INDEX)
        print(f"✅ {len(vectors)} documents vectorisés et indexés.")
    else:
        print("❌ Aucun vecteur généré.")

    print(f"✅ Ingestion complète — {len(memory)} fichiers analysés.")

=======
                    "modified_at": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                }
                memory.append({
                    "text": content.strip(),
                    "metadata": metadata
                })

    # Sauvegarde en JSONL
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for entry in memory:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"✅ Ingestion terminée : {len(memory)} fichiers ingérés.")
    print(f"📄 Résultat enregistré dans : {OUTPUT_PATH}")
>>>>>>> 8159adc914993503bf86350ffdcd5cb351b49b99

if __name__ == "__main__":
    ingest()
