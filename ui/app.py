import streamlit as st
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
