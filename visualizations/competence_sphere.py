import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def render_competence_sphere():
    # Exemples fictifs, remplacer par analyse réelle du contexte
    data = pd.DataFrame({
        "Domaines": ["Data Science", "Philo", "LLM", "Musique", "Vie perso"],
        "Score": [85, 60, 95, 40, 70]
    })

    fig = go.Figure(data=go.Scatterpolar(
        r=data["Score"],
        theta=data["Domaines"],
        fill='toself',
        mode='lines+markers',
        line_color='cyan'
    ))
    fig.update_layout(
        polar=dict(bgcolor="#0a0a0a", radialaxis=dict(visible=True, range=[0,100])),
        paper_bgcolor="#0a0a0a",
        font=dict(color="white"),
        title="Progression par domaine"
    )
    st.plotly_chart(fig, use_container_width=True)
