import streamlit as st
from core.context_loader import get_raw_context

st.set_page_config(page_title="CogOS - Dashboard", layout="wide")
st.title("📊 Cognitive Dashboard")

context = get_raw_context()

col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 Objectifs actuels")
    for goal in context.get("goals", []):
        st.markdown(f"- {goal}")

with col2:
    st.subheader("🧠 Focus cognitif (mémoire court terme)")
    for item in context["memory"].get("short_term", []):
        st.info(item)

st.divider()
st.subheader("📚 Connaissances long terme")
for category, items in context["memory"].get("long_term", {}).items():
    st.markdown(f"**{category.title()}** ({len(items)} items)")
    st.write(", ".join(items))
