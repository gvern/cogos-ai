import os
from pathlib import Path

# Dossier racine du projet
root = Path("cogos-ai")

# Arborescence du projet
structure = {
    "ui": {
        "app.py": '''import streamlit as st
from core.memory import query_memory
from visualizations.timeline import render_timeline

st.set_page_config(page_title="CogOS", layout="wide")
st.title("🧠 CogOS: Your Cognitive Operating System")

tab1, tab2, tab3 = st.tabs(["💬 Ask Your Brain", "📆 Lifeline", "📊 Dashboard"])

with tab1:
    query = st.text_input("Ask something from your life memory:")
    if query:
        response = query_memory(query)
        st.markdown("### 🧠 Response:")
        st.write(response)

with tab2:
    st.markdown("### 📆 Your Intellectual Timeline")
    render_timeline()

with tab3:
    st.markdown("### 📊 Knowledge Radar / Domain Progression (coming soon)")
    st.info("Visual insights into your knowledge domains will appear here.")
'''
    },
    "core": {
        "memory.py": '''def query_memory(query: str) -> str:
    # Placeholder for RAG-based semantic retrieval
    return f"🔍 I heard your question: '{query}'. Contextual memory search coming soon!"
'''
    },
    "visualizations": {
        "timeline.py": '''import streamlit as st
import pandas as pd
import plotly.express as px

def render_timeline():
    timeline_data = [
        {"date": "2023-01-01", "event": "Read 'The Beginning of Infinity'", "category": "Books"},
        {"date": "2023-05-12", "event": "Explored LLM fine-tuning", "category": "Work"},
        {"date": "2024-02-18", "event": "Watched lecture on Gödel", "category": "Philosophy"},
    ]
    df = pd.DataFrame(timeline_data)
    df["date"] = pd.to_datetime(df["date"])
    fig = px.timeline(df, x_start="date", x_end="date", y="category", color="category", text="event")
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)
'''
    },
    "data": {
        "notes/.keep": "",
        "books/.keep": "",
        "social/.keep": "",
        "music/.keep": "",
        "journal/.keep": "",
    },
    "embeddings": {
        ".keep": "",
    },
    "": {
        "README.md": '''# CogOS: Your AI-Powered Second Brain

CogOS is a modular, extensible cognitive operating system designed to help you store, reflect on, and grow your knowledge across your entire life.

## Features
- Chat interface for querying your memory
- Lifeline: visual timeline of your intellectual evolution
- Modular ingestion from books, notes, music, web
- Knowledge linting, reflection, and domain tracking (coming soon)

## Usage

```bash
streamlit run ui/app.py
''', "requirements.txt": '''streamlit plotly pandas openai ''' } }

###Création des fichiers
for folder, files in structure.items():
    folder_path = root / folder if folder else root
    folder_path.mkdir(parents=True, exist_ok=True)
    for filename, content in files.items():
        file_path = folder_path / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

print("✅ Projet 'cogos-ai' initialisé avec succès.") 
print("💡 Lance l'interface avec :") 
print(" streamlit run cogos-ai/ui/app.py")