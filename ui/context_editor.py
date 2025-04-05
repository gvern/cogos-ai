import streamlit as st
import json
from pathlib import Path
import sys
from typing import Dict, Any

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core.context_loader import get_raw_context, update_context
from core.context_builder import (
    update_short_term_memory,
    add_to_long_term_memory,
    update_goals,
    update_persona,
    get_memory_summary
)

st.set_page_config(page_title="CogOS Context Editor", layout="wide")

st.title("CogOS Context Editor")
st.write("Edit and view your personal cognitive context")

# Load current context
context = get_raw_context()

# Basic Information
st.header("Basic Information")
name = st.text_input("Name", context.get("name", ""))
if name != context.get("name"):
    context["name"] = name
    update_context(context)

# Persona Settings
st.header("Persona Settings")
col1, col2 = st.columns(2)
with col1:
    role = st.text_input("Role", context["persona"]["role"])
with col2:
    tone = st.text_input("Tone", context["persona"]["tone"])
if role != context["persona"]["role"] or tone != context["persona"]["tone"]:
    update_persona(role, tone)

# Short-term Memory
st.header("Short-term Memory")
short_term = st.text_area(
    "Current Focus (one item per line)",
    "\n".join(context["memory"]["short_term"])
)
if short_term != "\n".join(context["memory"]["short_term"]):
    update_short_term_memory([item.strip() for item in short_term.split("\n") if item.strip()])

# Long-term Memory
st.header("Long-term Memory")
for category, items in context["memory"]["long_term"].items():
    st.subheader(category.title())
    items_text = st.text_area(
        f"{category} (one item per line)",
        "\n".join(items),
        key=f"long_term_{category}"
    )
    if items_text != "\n".join(items):
        add_to_long_term_memory(category, [item.strip() for item in items_text.split("\n") if item.strip()])

# Goals
st.header("Goals")
goals = st.text_area(
    "Goals (one per line)",
    "\n".join(context["goals"])
)
if goals != "\n".join(context["goals"]):
    update_goals([goal.strip() for goal in goals.split("\n") if goal.strip()])

# Tools
st.header("Available Tools")
for tool in context["tools"]:
    st.write(f"- {tool}")

# Raw JSON View
st.header("Raw Context")
st.json(context)

# Memory Summary
st.header("Memory Summary")
summary = get_memory_summary()
st.json(summary) 

# Progression cognitive
st.header("📡 Progression Cognitive")
if "progress" in context:
    for domain, score in context["progress"].items():
        st.slider(f"{domain}", 0, 100, score, key=f"progress_{domain}")

# Dernière réflexion
st.header("🪞 Dernière synthèse")
st.markdown(context.get("memory", {}).get("last_reflection", "Aucune réflexion enregistrée."))
