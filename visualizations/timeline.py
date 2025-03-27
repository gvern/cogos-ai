import streamlit as st
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
