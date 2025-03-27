import sys
from pathlib import Path
import json
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
from core.memory import query_memory
from visualizations.timeline import render_timeline


st.set_page_config(page_title="CogOS", layout="wide")
st.title("🧠 CogOS: Your Cognitive Operating System")

tab1, tab2, tab3, tab4 = st.tabs(["💬 Ask Your Brain", "📆 Lifeline", "📊 Dashboard", "📂 Ingested Memory"])

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

with tab4:
    st.markdown("### 🧾 Ingested Memory")
    memory_path = Path("ingested/memory.jsonl")
    if memory_path.exists():
        with open(memory_path, "r", encoding="utf-8") as f:
            entries = [json.loads(line) for line in f.readlines()]
        if entries:
            for i, entry in enumerate(entries):
                with st.expander(f"{i+1}. {entry['metadata']['filename']} ({entry['metadata']['source']})"):
                    st.markdown(f"**Source**: `{entry['metadata']['source']}`")
                    st.markdown(f"**Created**: {entry['metadata']['created_at']}")
                    st.markdown(f"**Modified**: {entry['metadata']['modified_at']}")
                    st.text_area("🧠 Content", value=entry["text"], height=150)
        else:
            st.info("No entries found in memory.")
    else:
        st.warning("Run `python core/ingest.py` to ingest content.")