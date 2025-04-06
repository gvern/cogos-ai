"""
Module UI pour l'onglet de mise à jour de contexte de CogOS
"""
import streamlit as st
import json
import time
import altair as alt
import pandas as pd
from datetime import datetime

from core.context_builder import (
    update_context_intelligently, 
    get_domain_scores,
    get_all_domains
)
from core.context_loader import get_raw_context, update_context

def render_domain_radar():
    """Affiche un graphique radar des compétences par domaine."""
    # Récupérer les scores par domaine
    domain_scores = get_domain_scores()
    
    # Convertir en dataframe pour Altair
    data = []
    for domain, score in domain_scores.items():
        data.append({"Domaine": domain, "Score": score})
    
    df = pd.DataFrame(data)
    
    # Créer le graphique radar avec Altair
    base = alt.Chart(df).encode(
        theta=alt.Theta("Domaine:N", sort=None),
        radius=alt.Radius("Score:Q", scale=alt.Scale(type="sqrt", zero=True, domain=[0, 100])),
        color=alt.Color("Domaine:N", legend=None)
    )
    
    chart = base.mark_area(opacity=0.6).encode(
        tooltip=["Domaine", "Score"]
    )
    
    line = base.mark_line(stroke="#041C32", strokeWidth=2).encode()
    points = base.mark_point(filled=True, size=80).encode()
    
    radar = (chart + line + points).properties(
        width=500,
        height=500,
        title="Progression par domaine"
    )
    
    st.altair_chart(radar, use_container_width=True)

def render_context_section():
    """Affiche le contexte actuel et permet sa modification."""
    ctx = get_raw_context()
    
    if not ctx:
        st.warning("Contexte non disponible. Exécutez une mise à jour d'abord.")
        return
    
    with st.expander("📝 Éditer le contexte manuellement", expanded=False):
        # Permettre l'édition des champs principaux
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Nom", value=ctx.get("name", ""))
            role = st.text_input("Rôle", value=ctx.get("persona", {}).get("role", ""))
        
        with col2:
            tone = st.text_input("Ton", value=ctx.get("persona", {}).get("tone", ""))
            last_updated = ctx.get("last_updated", "Jamais")
            st.text_input("Dernière mise à jour", value=last_updated, disabled=True)
        
        # Édition des objectifs
        st.markdown("### 🎯 Objectifs")
        goals = ctx.get("goals", [])
        updated_goals = []
        
        for i, goal in enumerate(goals):
            col1, col2 = st.columns([5, 1])
            with col1:
                updated_goal = st.text_input(f"Objectif {i+1}", value=goal, key=f"goal_{i}")
                updated_goals.append(updated_goal)
            with col2:
                if st.button("🗑️", key=f"delete_goal_{i}"):
                    # Ne pas ajouter cet objectif à la liste mise à jour
                    updated_goals.pop()
        
        # Ajouter un nouvel objectif
        new_goal = st.text_input("Nouvel objectif")
        if new_goal:
            updated_goals.append(new_goal)
        
        # Focus à court terme
        st.markdown("### 📌 Focus actuel")
        focus_items = ctx.get("memory", {}).get("short_term", [])
        updated_focus = []
        
        for i, focus in enumerate(focus_items):
            col1, col2 = st.columns([5, 1])
            with col1:
                updated_focus_item = st.text_input(f"Focus {i+1}", value=focus, key=f"focus_{i}")
                updated_focus.append(updated_focus_item)
            with col2:
                if st.button("🗑️", key=f"delete_focus_{i}"):
                    updated_focus.pop()
        
        # Ajouter un nouveau focus
        new_focus = st.text_input("Nouveau focus")
        if new_focus:
            updated_focus.append(new_focus)
        
        # Enregistrer les modifications
        if st.button("💾 Enregistrer les modifications"):
            # Mettre à jour le contexte
            updated_ctx = ctx.copy()
            updated_ctx["name"] = name
            
            if "persona" not in updated_ctx:
                updated_ctx["persona"] = {}
            
            updated_ctx["persona"]["role"] = role
            updated_ctx["persona"]["tone"] = tone
            updated_ctx["goals"] = updated_goals
            
            if "memory" not in updated_ctx:
                updated_ctx["memory"] = {}
            
            updated_ctx["memory"]["short_term"] = updated_focus
            updated_ctx["last_updated"] = datetime.now().isoformat()
            
            # Sauvegarder
            update_context(updated_ctx)
            st.success("✅ Contexte mis à jour avec succès!")
            st.rerun()

def render_progress_bars(domain_scores):
    """Affiche des barres de progression pour chaque domaine."""
    for domain, score in domain_scores.items():
        st.markdown(f"**{domain}**")
        st.progress(score / 100)
        
        # Ajouter un indicateur de niveau
        if score < 30:
            level = "🔰 Novice"
        elif score < 50:
            level = "📚 Apprenant"
        elif score < 70:
            level = "🧩 Intermédiaire"
        elif score < 90:
            level = "🏆 Avancé"
        else:
            level = "🌟 Expert"
        
        st.caption(f"{level} - Score: {score}/100")

def render_context_update_tab():
    """Affiche l'onglet de mise à jour du contexte."""
    st.markdown("## 🔄 Mise à jour du contexte cognitif")
    st.markdown("""
    Votre contexte mental est mis à jour automatiquement en fonction de votre activité.
    Vous pouvez également lancer une mise à jour manuelle ici.
    """)
    
    # Onglets
    tab1, tab2, tab3 = st.tabs(["📊 Vue d'ensemble", "🧠 Mise à jour", "🛠️ Configuration"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Afficher le graphique radar
            render_domain_radar()
        
        with col2:
            # Afficher le contexte actuel
            ctx = get_raw_context()
            
            if ctx:
                st.markdown("### 🎯 Objectifs")
                for goal in ctx.get("goals", []):
                    st.markdown(f"- {goal}")
                
                st.markdown("### 📌 Focus actuel")
                for focus in ctx.get("memory", {}).get("short_term", []):
                    st.markdown(f"- {focus}")
                
                last_updated = ctx.get("last_updated", "Jamais")
                if last_updated != "Jamais":
                    try:
                        last_updated_dt = datetime.fromisoformat(last_updated)
                        last_updated = last_updated_dt.strftime("%d/%m/%Y %H:%M")
                    except:
                        pass
                
                st.caption(f"Dernière mise à jour: {last_updated}")
            else:
                st.warning("Aucun contexte disponible.")
    
    with tab2:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("### 🧠 Mise à jour intelligente")
            st.markdown("""
            La mise à jour intelligente analyse vos données récentes pour mettre à jour votre contexte mental.
            Cela inclut vos objectifs, vos intérêts actuels et votre progression dans différents domaines.
            """)
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🔄 Mise à jour rapide", help="Met à jour uniquement les objectifs et focus"):
                    with st.spinner("Mise à jour rapide en cours..."):
                        report = update_context_intelligently(run_all=False)
                        st.success("✅ Mise à jour rapide terminée avec succès!")
                        
                        # Afficher un résumé
                        st.markdown("#### Résumé de la mise à jour")
                        st.markdown(f"**Tags identifiés**: {', '.join(report['tags'])}")
                        st.markdown(f"**Timestamp**: {report['timestamp']}")
            
            with col_b:
                if st.button("🧠 Mise à jour complète", help="Analyse approfondie de tous les domaines"):
                    with st.spinner("Analyse complète en cours..."):
                        # Simuler une barre de progression
                        progress_bar = st.progress(0)
                        for i in range(100):
                            time.sleep(0.01)
                            progress_bar.progress(i + 1)
                        
                        report = update_context_intelligently(run_all=True)
                        st.success("✅ Mise à jour complète terminée avec succès!")
                        
                        # Afficher un résumé
                        st.markdown("#### Résumé de la mise à jour")
                        st.markdown(f"**Tags identifiés**: {', '.join(report['tags'])}")
                        
                        # Afficher les progrès par domaine
                        domains_data = report.get("domains", {})
                        if domains_data:
                            st.markdown("#### Progression par domaine")
                            for domain, data in domains_data.items():
                                st.markdown(f"**{domain}**: {data['score']}/100 - {data['comment']}")
        
        with col2:
            st.markdown("### 🏆 Progression")
            domain_scores = get_domain_scores()
            render_progress_bars(domain_scores)
    
    with tab3:
        render_context_section()

if __name__ == "__main__":
    st.set_page_config(page_title="CogOS Context Update", layout="wide")
    render_context_update_tab() 