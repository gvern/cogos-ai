import sys
from pathlib import Path
import json
sys.path.append(str(Path(__file__).resolve().parent.parent))
<<<<<<< HEAD
import streamlit as st
from core.memory import query_memory
from visualizations.timeline import render_timeline
import pandas as pd
from core.reflector import reflect_on_last_entries, summarize_by_tag
from core.editor import load_memory, update_entry, delete_entry

# === Streamlit UI ===
st.set_page_config(page_title="CogOS", layout="wide")
st.title("🧠 CogOS: Your Cognitive Operating System")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["💬 Ask", "📆 Lifeline", "📊 Stats", "📂 Memory", "🧠 Reflect", "✏️ Edit Memory"])
=======

import streamlit as st
from core.memory import query_memory
from visualizations.timeline import render_timeline


st.set_page_config(page_title="CogOS", layout="wide")
st.title("🧠 CogOS: Your Cognitive Operating System")

tab1, tab2, tab3, tab4 = st.tabs(["💬 Ask Your Brain", "📆 Lifeline", "📊 Dashboard", "📂 Ingested Memory"])
>>>>>>> 8159adc914993503bf86350ffdcd5cb351b49b99

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
<<<<<<< HEAD
    st.markdown("### 📊 Knowledge Stats")
    if Path("ingested/memory.jsonl").exists():
        entries = [json.loads(line) for line in open("ingested/memory.jsonl", encoding="utf-8")]
        df = pd.DataFrame([{
            "Source": e["metadata"]["source"],
            "Tags": ", ".join(e["metadata"].get("tags", [])),
            "Words": len(e["text"].split()),
            "Date": e["metadata"]["created_at"]
        } for e in entries])
        st.dataframe(df)
        st.bar_chart(df["Source"].value_counts())
    else:
        st.warning("Pas encore de mémoire. Lance `python core/ingest.py`.")
=======
    st.markdown("### 📊 Knowledge Radar / Domain Progression (coming soon)")
    st.info("Visual insights into your knowledge domains will appear here.")
>>>>>>> 8159adc914993503bf86350ffdcd5cb351b49b99

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
<<<<<<< HEAD
        st.warning("Run `python core/ingest.py` to ingest content.")
        
with tab5:
    st.subheader("🧠 Reflect on Recent Entries")
    if st.button("🪞 Generate Reflection"):
        st.markdown(reflect_on_last_entries())

    st.subheader("📎 Synthesize by Tag")
    tag = st.text_input("Enter a tag to summarize:")
    if st.button("📘 Summarize Tag"):
        if tag:
            st.markdown(summarize_by_tag(tag))

with tab6:
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
=======
        st.warning("Run `python core/ingest.py` to ingest content.")
>>>>>>> 8159adc914993503bf86350ffdcd5cb351b49b99
