import streamlit as st
import pandas as pd
import plotly.express as px
import pandas as pd
import plotly.express as px
from pathlib import Path
import json

def render_timeline():
    

    memory_path = Path("ingested/memory.jsonl")
    if not memory_path.exists():
        st.info("Aucune donnée mémoire disponible.")
        return

    with open(memory_path, encoding="utf-8") as f:
        entries = []
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"⚠️ Ligne JSON invalide ignorée : {e}")



    data = []
    for e in entries:
        data.append({
            "date": e["metadata"]["created_at"][:10],
            "event": e["metadata"]["filename"],
            "category": e["metadata"]["source"]
        })

    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    fig = px.timeline(df, x_start="date", x_end="date", y="category", color="category", text="event")
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)
