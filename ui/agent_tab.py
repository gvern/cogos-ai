"""
Module UI pour l'onglet Agent de CogOS
"""
import streamlit as st
from datetime import datetime, timedelta
import json

from core.agent import (
    get_actions_for_display, 
    generate_action_suggestions, 
    mark_action_completed, 
    delete_action,
    AgentAction
)

def format_priority(priority: int) -> str:
    """Formate la priorité en étoiles."""
    return "⭐" * priority

def format_deadline(deadline: str) -> str:
    """Formate la date limite de façon lisible."""
    if not deadline:
        return "Pas de date limite"
    
    try:
        deadline_date = datetime.fromisoformat(deadline)
        today = datetime.now().date()
        
        days_left = (deadline_date.date() - today).days
        
        if days_left < 0:
            return f"🚨 **En retard** ({-days_left} jours)"
        elif days_left == 0:
            return "⚠️ **Aujourd'hui**"
        elif days_left == 1:
            return "⏰ Demain"
        elif days_left < 7:
            return f"⏳ {days_left} jours"
        else:
            return deadline_date.strftime("%d/%m/%Y")
    except:
        return deadline

def get_badge_for_type(action_type: str) -> str:
    """Retourne un badge coloré selon le type d'action."""
    badges = {
        "apprentissage": "🧠",
        "défi": "🏆",
        "rappel": "⏰",
        "exploration": "🔍",
        "consolidation": "📚",
        "création": "🎨"
    }
    return badges.get(action_type, "📌")

def render_action_card(action, index: int):
    """Affiche une carte d'action avec les contrôles."""
    badge = get_badge_for_type(action.action_type)
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"### {badge} {action.title}")
        st.markdown(f"**Type**: {action.action_type.capitalize()}")
        st.markdown(f"**Priorité**: {format_priority(action.priority)}")
        st.markdown(f"**Échéance**: {format_deadline(action.deadline)}")
        st.markdown(f"{action.description}")
    
    with col2:
        # Utiliser un identifiant unique pour chaque bouton basé sur l'index et un identifiant unique de l'action
        action_id = getattr(action, 'id', str(index))
        if st.button(f"✅ Terminé", key=f"complete_{action_id}_{index}"):
            mark_action_completed(index)
            st.success("Action marquée comme terminée!")
            st.rerun()
        
        if st.button(f"🗑️ Supprimer", key=f"delete_{action_id}_{index}"):
            delete_action(index)
            st.warning("Action supprimée!")
            st.rerun()

def render_agent_tab():
    """Affiche l'onglet Agent avec les actions suggérées."""
    st.markdown("## 🧭 CogOS Agent")
    st.markdown("Votre assistant cognitif personnel qui vous suggère des actions pour progresser.")
    
    # Afficher les actions en cours
    actions = get_actions_for_display(include_completed=False)
    
    # Onglets: En cours / Terminées / Nouvelle action
    tab1, tab2, tab3 = st.tabs(["⏳ En cours", "✅ Terminées", "➕ Nouvelle action"])
    
    with tab1:
        if not actions:
            st.info("Aucune action en cours. Générez des suggestions ou créez une nouvelle action!")
        else:
            for i, action in enumerate(actions):
                with st.container():
                    st.markdown("---")
                    render_action_card(action, i)
        
        st.markdown("---")
        if st.button("🔄 Générer de nouvelles suggestions"):
            with st.spinner("Analyse en cours..."):
                new_actions = generate_action_suggestions(3)
                st.success(f"✅ {len(new_actions)} nouvelles actions générées!")
                st.rerun()
    
    with tab2:
        completed_actions = get_actions_for_display(include_completed=True)
        completed_actions = [a for a in completed_actions if a.completed]
        
        if not completed_actions:
            st.info("Aucune action terminée pour le moment.")
        else:
            for i, action in enumerate(completed_actions):
                with st.container():
                    st.markdown("---")
                    badge = get_badge_for_type(action.action_type)
                    st.markdown(f"### {badge} {action.title}")
                    st.markdown(f"**Type**: {action.action_type.capitalize()}")
                    st.markdown(f"**Priorité**: {format_priority(action.priority)}")
                    st.markdown(f"{action.description}")
                    st.markdown(f"**Statut**: ✅ Terminée")
                    
                    # Ajouter un bouton de suppression avec une clé unique
                    action_id = getattr(action, 'id', str(i))
                    if st.button(f"🗑️ Supprimer", key=f"delete_completed_{action_id}_{i}"):
                        # Trouver l'index réel de cette action dans la liste complète
                        all_actions = get_actions_for_display(include_completed=True)
                        for idx, a in enumerate(all_actions):
                            if getattr(a, 'id', '') == action_id:
                                delete_action(idx)
                                st.warning("Action supprimée!")
                                st.rerun()
                                break
    
    with tab3:
        st.markdown("### Créer une nouvelle action")
        
        title = st.text_input("Titre", key="new_action_title")
        description = st.text_area("Description", key="new_action_description")
        
        col1, col2 = st.columns(2)
        with col1:
            action_type = st.selectbox(
                "Type d'action",
                ["apprentissage", "défi", "rappel", "exploration", "consolidation", "création"],
                key="new_action_type"
            )
        with col2:
            priority = st.slider("Priorité", 1, 5, 3, key="new_action_priority")
        
        has_deadline = st.checkbox("Ajouter une date limite", key="has_deadline")
        deadline = None
        
        if has_deadline:
            deadline_date = st.date_input(
                "Date limite", 
                datetime.now().date() + timedelta(days=7),
                key="new_action_deadline"
            )
            deadline = deadline_date.isoformat()
        
        if st.button("💾 Créer l'action"):
            if title and description:
                # Créer une nouvelle action
                action = AgentAction(
                    title=title,
                    description=description,
                    action_type=action_type,
                    priority=priority,
                    deadline=deadline,
                    completed=False
                )
                
                # Récupérer les actions existantes
                actions = get_actions_for_display(include_completed=True)
                
                # Ajouter la nouvelle action
                actions.append(action)
                
                # Sauvegarder
                from core.agent import save_agent_actions
                save_agent_actions(actions)
                
                st.success("✅ Action créée avec succès!")
                # Vider les champs du formulaire via rerun
                st.rerun()
            else:
                st.error("Le titre et la description sont obligatoires.")

if __name__ == "__main__":
    st.set_page_config(page_title="CogOS Agent", layout="wide")
    render_agent_tab() 