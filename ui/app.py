import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from datetime import date
import multiprocessing
multiprocessing.set_start_method("fork", force=True)
from core.context_loader import update_context
import sys
from pathlib import Path
import json
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st

# === Thème Jarvis === (MUST BE FIRST STREAMLIT COMMAND)
st.set_page_config(
    page_title="CogOS — JARVIS Mode",
    layout="wide",
    page_icon="🧠",
)

import pandas as pd

from core.memory import query_memory
from core.audio import speak_response
from core.reflector import reflect_on_last_entries, summarize_by_tag
from core.editor import load_memory, update_entry, delete_entry
from core.context_builder import update_context_intelligently
from core.context_loader import get_raw_context
from visualizations.timeline import render_timeline
from visualizations.competence_sphere import render_competence_sphere
from core.voice_input import listen_from_microphone
from core.briefing import generate_briefing

# === Contexte latéral ===
ctx = get_raw_context()

with st.sidebar:
    st.markdown("## 🎯 Contexte actuel")
    st.markdown(f"**Rôle :** {ctx.get('persona', {}).get('role')}")
    st.markdown(f"**Ton :** {ctx.get('persona', {}).get('tone')}")
    st.markdown("### 📌 Focus")
    st.write(ctx.get("memory", {}).get("short_term", []))
    st.markdown("### 🚀 Objectifs")
    st.write(ctx.get("goals", []))

st.markdown("""
<style>
body {
    background-color: #0a0a0a;
    color: #39FF14;
}
h1, h2, h3, h4 {
    color: #00f0ff;
}
.stButton > button {
    background-color: #0f0f0f;
    color: #00f0ff;
    border: 1px solid #00f0ff;
}
.stTextInput>div>div>input {
    background-color: #1f1f1f;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# === Tabs principaux ===
tab_home, tab_query, tab_lifeline, tab_update, tab_memory, tab_reflect, tab_edit, tab_skills = st.tabs([
    "🏠 Dashboard", "💬 Query", "📆 Timeline", "🔄 Context Update",
    "📂 Memory", "🧠 Reflection", "✏️ Edit Memory", "📡 Skills"
])

# === Onglet accueil ===
with tab_home:
    st.markdown("### 🧠 Welcome to CogOS — Your JARVIS Interface")
    st.image("https://media.giphy.com/media/XIqCQx02E1U9W/giphy.gif", use_container_width=True)
    st.info("Statut : En ligne · Mode vocal activé · Mémoire active : ✅")
    ctx = get_raw_context()
    today = date.today().isoformat()

    if ctx.get("last_seen") != today:
        from core.briefing import generate_briefing
        st.success("🧠 Briefing quotidien :")
        st.code(generate_briefing())
        ctx["last_seen"] = today
        update_context(ctx)

    st.markdown("### 🧾 Briefing quotidien")
    if st.button("🧠 Générer mon briefing"):
        with st.spinner("Analyse cognitive en cours..."):
            briefing = generate_briefing()
            st.code(briefing)

# === Onglet Query ===
with tab_query:
    query = st.text_input("Ask something from your life memory:")
    if query:
        response = query_memory(query)
        st.markdown("### 🧠 Response:")
        st.write(response)

        if st.button("🔊 Lire à voix haute"):
            speak_response(response)
    
    st.markdown("### 🗣️ Ou utiliser le micro :")
    voice_col1, voice_col2 = st.columns([3, 1])
    with voice_col1:
        if st.button("🎙️ Parler à CogOS", help="Utilise le micro ou télécharge un fichier audio"):
            with st.spinner("Écoute en cours..."):
                text = listen_from_microphone()
                if text:
                    st.success(f"Tu as dit : {text}")
                    response = query_memory(text)
                    st.write(response)
    with voice_col2:
        with st.expander("ℹ️ Info"):
            st.markdown("""
            **Installation audio :**
            ```bash
            # Option 1 - Avec micro (si disponible) :
            pip install SpeechRecognition pyaudio
            
            # Sur Mac, installer d'abord portaudio :
            brew install portaudio
            
            # Option 2 - Alternative sans dépendances natives :
            pip install SpeechRecognition sounddevice
            ```
            """)

# === Timeline cognitive
with tab_lifeline:
    st.markdown("### 📆 Your Intellectual Timeline")
    render_timeline()

# === Mise à jour automatique du contexte
with tab_update:
    st.markdown("### 🔄 Mise à jour cognitive automatique")
    if st.button("🧠 Mettre à jour mon contexte maintenant"):
        with st.spinner("Mise à jour du contexte en cours..."):
            update_context_intelligently()
            st.success("✅ Contexte mis à jour avec succès !")

# === Mémoire brute (lecture seule)
with tab_memory:
    st.markdown("### 🧾 Ingested Memory")
    memory_path = Path("ingested/memory.jsonl")
    if memory_path.exists():
        with open(memory_path, "r", encoding="utf-8") as f:
            entries = [json.loads(line) for line in f.readlines()]
        if entries:
            source_filter = st.selectbox("Filtrer par source :", ["Toutes"] + sorted(set(e["metadata"]["source"] for e in entries)))
            for i, entry in enumerate(entries):
                if source_filter != "Toutes" and entry["metadata"]["source"] != source_filter:
                    continue
                with st.expander(f"{i+1}. {entry['metadata']['filename']} ({entry['metadata']['source']})"):
                    st.markdown(f"**Source**: `{entry['metadata']['source']}`")
                    st.markdown(f"**Created**: {entry['metadata']['created_at']}")
                    st.markdown(f"**Modified**: {entry['metadata']['modified_at']}")
                    st.text_area("🧠 Content", value=entry["text"], height=150)
        
        else:
            st.info("No entries found in memory.")
    else:
        st.warning("Run `python core/ingest.py` to ingest content.")

# === Réflexion intelligente
with tab_reflect:
    st.subheader("🧠 Reflect on Recent Entries")
    if st.button("🪞 Generate Reflection"):
        st.markdown(reflect_on_last_entries())

    st.subheader("📎 Synthesize by Tag")
    tag = st.text_input("Enter a tag to summarize:")
    if st.button("📘 Summarize Tag"):
        if tag:
            st.markdown(summarize_by_tag(tag))

# === Édition manuelle des souvenirs
with tab_edit:
    st.subheader("✏️ Modify or Delete Memory")
    entries = load_memory()
    for i, entry in enumerate(entries):
        with st.expander(f"{i+1}. {entry['metadata']['filename']}"):
            new_text = st.text_area("Edit text:", value=entry["text"], height=150)
            col1, col2 = st.columns(2)
            if col1.button(f"✅ Save", key=f"save_{i}"):
                update_entry(i, new_text)
                st.success("Saved!")
            if col2.button(f"🗑️ Delete", key=f"delete_{i}"):
                delete_entry(i)
                st.warning("Deleted.")

# Add the new tab for skills
with tab_skills:
    st.markdown("### 📡 Visualisation de ta progression cognitive")
    render_competence_sphere()
