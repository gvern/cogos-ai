import os
import json
from pathlib import Path
import streamlit as st
try:
    from streamlit_lottie import st_lottie
    HAS_LOTTIE = True
except ImportError:
    HAS_LOTTIE = False
    st.warning("streamlit_lottie not installed. Install with: pip install streamlit_lottie")

# Imports depuis tes modules
from core.context_builder import update_context_intelligently
from core.memory import query_memory
from core.editor import load_memory, update_entry, delete_entry
from core.reflector import reflect_on_last_entries, summarize_by_tag
from core.briefing import generate_briefing
from core.voice_input import listen_from_microphone
from visualizations.timeline import render_timeline
from visualizations.competence_sphere import render_competence_sphere
from core.context_loader import update_context, get_raw_context
from datetime import date

#############################
# Fonctions utilitaires
#############################

def load_lottiefile(filepath: str):
    """Charge un fichier .lottie localement avec gestion d'erreur."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        st.warning(f"Trying binary mode for animation ({str(e)}).")
        try:
            # Try binary mode as fallback - using a safer approach
            with open(filepath, "rb") as f:
                # Don't try to decode as base64, just read as binary
                bytes_data = f.read()
                # Try to decode with various encodings
                for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        decoded = bytes_data.decode(encoding)
                        return json.loads(decoded)
                    except (UnicodeDecodeError, json.JSONDecodeError):
                        continue
                
                # If all decoding attempts fail, try to use the binary data directly
                import io
                try:
                    # Create a binary stream and parse as JSON
                    return json.load(io.BytesIO(bytes_data))
                except:
                    st.warning("Failed to load animation with any encoding method")
        except Exception as e:
            st.warning(f"Binary load failed: {str(e)}")
    except FileNotFoundError:
        st.warning(f"Animation file not found: {filepath}")
    
    # Default Lottie animation (minimal)
    return {
        "v": "5.5.7",
        "fr": 30,
        "ip": 0,
        "op": 60,
        "w": 200,
        "h": 200,
        "layers": []
    }

def save_conversation():
    """Enregistre la conversation dans un fichier logs/conversation.jsonl."""
    os.makedirs("logs", exist_ok=True)
    with open("logs/conversation.jsonl", "a", encoding="utf-8") as f:
        for msg in st.session_state["conversation"]:
            f.write(json.dumps(msg) + "\n")
    st.success("Conversation sauvegardée dans logs/conversation.jsonl")


#############################
# Layout principal (onglets)
#############################

def render_main_layout():
    # Initialisation session state pour le mode conversation
    if "conversation" not in st.session_state:
        st.session_state["conversation"] = []

    # Lecture du contexte
    ctx = get_raw_context()

    # Charger l'animation lottie (ex: assets/cogos_lottie.lottie)
    # Avec gestion d'erreur
    lottie_jarvis = None
    if HAS_LOTTIE:
        try:
            # Try loading the main lottie file
            lottie_jarvis = load_lottiefile("assets/cogos_lottie.lottie")
        except Exception as e:
            st.warning(f"Error loading primary animation: {e}")
            try:
                # Try the fallback JSON file
                lottie_jarvis = load_lottiefile("assets/cogos_lottie_fallback.json")
                st.success("Loaded fallback animation")
            except Exception as e2:
                st.warning(f"Error loading fallback animation: {e2}")
                lottie_jarvis = None

    # Création des onglets
    tab_home, tab_query, tab_lifeline, tab_update, tab_memory, tab_reflect, tab_edit, tab_skills, tab_chat = st.tabs([
        "🏠 Dashboard", "💬 Query", "📆 Timeline", "🔄 Context Update",
        "📂 Memory", "🧠 Reflection", "✏️ Edit Memory", "📡 Skills", "🚀 Conversation"
    ])

    #########################
    # Onglet 1 : Home
    #########################
    with tab_home:
        st.markdown("### 🧠 Welcome to CogOS — Your JARVIS Interface")
        # Affiche l'animation en haut pour ambiance
        if HAS_LOTTIE and lottie_jarvis:
            try:
                st_lottie(lottie_jarvis, speed=1, height=180, key="lottie_jarvis_home")
            except Exception as e:
                st.error(f"Failed to display animation: {e}")
                st.image("https://media.giphy.com/media/XIqCQx02E1U9W/giphy.gif", use_column_width=True)
        else:
            st.image("https://media.giphy.com/media/XIqCQx02E1U9W/giphy.gif", use_column_width=True)

        st.info("Statut : En ligne · Mode vocal activé · Mémoire active : ✅")

        today = date.today().isoformat()
        if ctx.get("last_seen") != today:
            st.success("🧠 Briefing quotidien :")
            st.code(generate_briefing())
            ctx["last_seen"] = today
            update_context(ctx)

        st.markdown("### 🧾 Briefing quotidien")
        if st.button("🧠 Générer mon briefing"):
            with st.spinner("Analyse cognitive en cours..."):
                briefing = generate_briefing()
                st.code(briefing)

    #########################
    # Onglet 2 : Query
    #########################
    with tab_query:
        if HAS_LOTTIE and lottie_jarvis:
            try:
                st_lottie(lottie_jarvis, speed=1, height=120, key="lottie_jarvis_query")
            except:
                # Just skip the animation if it fails
                pass

        query = st.text_input("Ask something from your life memory:")
        if query:
            response = query_memory(query)
            st.markdown("### 🧠 Response:")
            st.write(response)

            # Enregistrer dans la conversation
            st.session_state["conversation"].append({"role": "user", "content": query})
            st.session_state["conversation"].append({"role": "assistant", "content": response})

            if st.button("🔊 Lire à voix haute"):
                from core.audio import speak_response
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
                        # Log conversation
                        st.session_state["conversation"].append({"role": "user", "content": text})
                        st.session_state["conversation"].append({"role": "assistant", "content": response})
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

    #########################
    # Onglet 3 : Timeline
    #########################
    with tab_lifeline:
        st.markdown("### 📆 Your Intellectual Timeline")
        render_timeline()

    #########################
    # Onglet 4 : Update
    #########################
    with tab_update:
        st.markdown("### 🔄 Mise à jour cognitive automatique")
        if st.button("🧠 Mettre à jour mon contexte maintenant"):
            with st.spinner("Mise à jour du contexte en cours..."):
                update_context_intelligently()
                st.success("✅ Contexte mis à jour avec succès !")

    #########################
    # Onglet 5 : Memory
    #########################
    with tab_memory:
        st.markdown("### 🧾 Ingested Memory")
        memory_path = Path("ingested/memory.jsonl")
        if memory_path.exists():
            with open(memory_path, "r", encoding="utf-8") as f:
                entries = [json.loads(line) for line in f.readlines() if line.strip()]
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

    #########################
    # Onglet 6 : Reflection
    #########################
    with tab_reflect:
        st.subheader("🧠 Reflect on Recent Entries")
        if st.button("🪞 Generate Reflection"):
            st.markdown(reflect_on_last_entries())

        st.subheader("📎 Synthesize by Tag")
        tag = st.text_input("Enter a tag to summarize:")
        if st.button("📘 Summarize Tag"):
            if tag:
                st.markdown(summarize_by_tag(tag))

    #########################
    # Onglet 7 : Edit
    #########################
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

    #########################
    # Onglet 8 : Skills (3D sphere)
    #########################
    with tab_skills:
        st.markdown("### 📡 Visualisation de ta progression cognitive")
        render_competence_sphere()

    #########################
    # Onglet 9 : Conversation
    #########################
    with tab_chat:
        st.subheader("🚀 Mode Conversation")

        # Affiche l'historique
        st.write("#### Historique de conversation")
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state["conversation"]:
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div style='background-color:#1E3C5C; padding:10px; border-radius:5px; margin-bottom:10px;'>
                        <strong>👤 Toi :</strong> {msg['content']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style='background-color:#162B40; padding:10px; border-radius:5px; margin-bottom:10px;'>
                        <strong>🤖 CogOS :</strong> {msg['content']}
                    </div>
                    """, unsafe_allow_html=True)

        # Input pour nouveau message
        st.write("#### Nouvelle question")
        chat_input = st.text_input("Ton message :", key="chat_input")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if st.button("💬 Envoyer"):
                if chat_input:
                    # Ajoute le message à la conversation
                    st.session_state["conversation"].append({"role": "user", "content": chat_input})
                    
                    # Obtient la réponse
                    with st.spinner("CogOS réfléchit..."):
                        response = query_memory(chat_input)
                    
                    # Ajoute la réponse à la conversation
                    st.session_state["conversation"].append({"role": "assistant", "content": response})
                    
                    # Recharge la page pour afficher la mise à jour
                    st.rerun()
        
        with col2:
            if st.button("🎙️ Parler"):
                with st.spinner("Écoute en cours..."):
                    text = listen_from_microphone()
                    if text:
                        # Ajoute le message à la conversation
                        st.session_state["conversation"].append({"role": "user", "content": text})
                        
                        # Obtient la réponse
                        with st.spinner("CogOS réfléchit..."):
                            response = query_memory(text)
                        
                        # Ajoute la réponse à la conversation
                        st.session_state["conversation"].append({"role": "assistant", "content": response})
                        
                        # Recharge la page pour afficher la mise à jour
                        st.rerun()

        # Actions
        st.write("#### Actions")
        col1, col2 = st.columns(2)
        with col1:
            # Bouton pour sauvegarder la conversation en local
            if st.button("💾 Sauvegarder la conversation"):
                save_conversation()
                st.success("Conversation enregistrée!")
        
        with col2:
            # Bouton pour effacer la conversation
            if st.button("🗑️ Effacer l'historique"):
                st.session_state["conversation"] = []
                st.success("Conversation réinitialisée!")
                st.rerun()
