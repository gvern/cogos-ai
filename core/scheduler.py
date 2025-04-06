"""
CogOS Scheduler - Module de planification et notification
Gère les rappels, le briefing quotidien et les notifications système
"""
import os
import json
import smtplib
import subprocess
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from core.briefing import generate_briefing
from core.agent import get_actions_for_display
from core.context_loader import get_raw_context

# Structure pour un événement planifié
class ScheduledEvent:
    def __init__(self, 
                 title: str, 
                 description: str, 
                 event_type: str,
                 scheduled_time: str,  # Format ISO: YYYY-MM-DDTHH:MM:SS
                 repeat: Optional[str] = None,  # "daily", "weekly", "monthly", None
                 last_triggered: Optional[str] = None,
                 enabled: bool = True):
        self.title = title
        self.description = description
        self.event_type = event_type  # "briefing", "reminder", "action", "custom"
        self.scheduled_time = scheduled_time
        self.repeat = repeat
        self.last_triggered = last_triggered
        self.enabled = enabled
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'événement en dictionnaire pour la sérialisation."""
        return {
            "title": self.title,
            "description": self.description,
            "event_type": self.event_type,
            "scheduled_time": self.scheduled_time,
            "repeat": self.repeat,
            "last_triggered": self.last_triggered,
            "enabled": self.enabled
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScheduledEvent':
        """Crée un événement à partir d'un dictionnaire."""
        return cls(
            title=data["title"],
            description=data["description"],
            event_type=data["event_type"],
            scheduled_time=data["scheduled_time"],
            repeat=data.get("repeat"),
            last_triggered=data.get("last_triggered"),
            enabled=data.get("enabled", True)
        )
    
    def is_due(self) -> bool:
        """Vérifie si l'événement doit être déclenché."""
        if not self.enabled:
            return False
        
        now = datetime.now()
        scheduled = datetime.fromisoformat(self.scheduled_time)
        
        # Cas d'un événement non répété
        if not self.repeat:
            return now >= scheduled
        
        # Si jamais déclenché ou trop vieux
        if not self.last_triggered:
            return now >= scheduled
        
        last = datetime.fromisoformat(self.last_triggered)
        
        # Vérification selon la répétition
        if self.repeat == "daily":
            next_due = last + timedelta(days=1)
            return now >= next_due
        elif self.repeat == "weekly":
            next_due = last + timedelta(weeks=1)
            return now >= next_due
        elif self.repeat == "monthly":
            # Approximatif - utilise 30 jours
            next_due = last + timedelta(days=30)
            return now >= next_due
        
        return False


def load_scheduled_events() -> List[ScheduledEvent]:
    """Charge les événements planifiés."""
    events_file = Path("data/scheduled_events.json")
    
    if not events_file.exists():
        # Créer des événements par défaut
        return [create_default_briefing_event()]
    
    try:
        with open(events_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return [ScheduledEvent.from_dict(event_data) for event_data in data]
    except Exception as e:
        print(f"Erreur lors du chargement des événements: {e}")
        return [create_default_briefing_event()]


def save_scheduled_events(events: List[ScheduledEvent]) -> bool:
    """Enregistre les événements planifiés."""
    events_file = Path("data/scheduled_events.json")
    events_file.parent.mkdir(exist_ok=True)
    
    try:
        with open(events_file, "w", encoding="utf-8") as f:
            json.dump([event.to_dict() for event in events], f, indent=2)
        return True
    except Exception as e:
        print(f"Erreur lors de l'enregistrement des événements: {e}")
        return False


def create_default_briefing_event() -> ScheduledEvent:
    """Crée un événement de briefing quotidien par défaut."""
    # Par défaut à 8h du matin
    tomorrow = datetime.now().replace(hour=8, minute=0, second=0) + timedelta(days=1)
    
    return ScheduledEvent(
        title="Briefing quotidien",
        description="Résumé quotidien de tes activités et objectifs",
        event_type="briefing",
        scheduled_time=tomorrow.isoformat(),
        repeat="daily"
    )


def check_due_events() -> List[ScheduledEvent]:
    """Vérifie les événements à déclencher et les retourne."""
    events = load_scheduled_events()
    due_events = []
    
    for event in events:
        if event.is_due():
            # Mettre à jour last_triggered
            event.last_triggered = datetime.now().isoformat()
            due_events.append(event)
    
    # Sauvegarder les modifications
    if due_events:
        save_scheduled_events(events)
    
    return due_events


def create_reminder_event(title: str, description: str, when: datetime, repeat: Optional[str] = None) -> bool:
    """Crée un nouvel événement de rappel."""
    events = load_scheduled_events()
    
    new_event = ScheduledEvent(
        title=title,
        description=description,
        event_type="reminder",
        scheduled_time=when.isoformat(),
        repeat=repeat
    )
    
    events.append(new_event)
    return save_scheduled_events(events)


def handle_due_event(event: ScheduledEvent) -> bool:
    """Traite un événement qui doit être déclenché."""
    if event.event_type == "briefing":
        briefing = generate_briefing()
        return send_notification(event.title, briefing)
    
    elif event.event_type == "reminder" or event.event_type == "action":
        return send_notification(event.title, event.description)
    
    # Pour les types personnalisés, envoyer simplement une notification
    return send_notification(event.title, event.description)


def send_notification(title: str, message: str) -> bool:
    """Envoie une notification via le système approprié (Mac/Email)."""
    # D'abord essayer la notification système Mac
    if send_macos_notification(title, message):
        return True
    
    # Si ça échoue, essayer l'email
    return send_email_notification(title, message)


def send_macos_notification(title: str, message: str) -> bool:
    """Envoie une notification macOS via AppleScript."""
    try:
        script = f'''
        osascript -e 'display notification "{message}" with title "{title}"'
        '''
        subprocess.run(script, shell=True, check=True)
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de la notification macOS: {e}")
        return False


def send_email_notification(title: str, message: str) -> bool:
    """Envoie une notification par email."""
    email_config_file = Path("config/email_config.json")
    
    if not email_config_file.exists():
        print("Configuration email non trouvée")
        return False
    
    try:
        with open(email_config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        # Créer le message
        email_msg = MIMEMultipart()
        email_msg["From"] = config["from_email"]
        email_msg["To"] = config["to_email"]
        email_msg["Subject"] = f"CogOS - {title}"
        
        # Ajouter le contenu
        email_msg.attach(MIMEText(message, "plain"))
        
        # Envoyer l'email
        with smtplib.SMTP(config["smtp_server"], config["smtp_port"]) as server:
            server.starttls()
            server.login(config["username"], config["password"])
            server.send_message(email_msg)
        
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email: {e}")
        return False


def process_due_notifications():
    """Vérifie et traite toutes les notifications en attente."""
    due_events = check_due_events()
    
    for event in due_events:
        handle_due_event(event)
    
    return len(due_events)


def schedule_agent_actions():
    """Crée des événements pour les actions de l'agent qui ont des deadlines."""
    actions = get_actions_for_display(include_completed=False)
    events = load_scheduled_events()
    
    # Vérifier si des actions ont des deadlines et ne sont pas déjà planifiées
    for action in actions:
        if action.deadline:
            # Vérifier si cette action est déjà planifiée
            action_title = action.title
            
            if not any(event.title == action_title and event.event_type == "action" for event in events):
                # Créer un rappel la veille de la deadline
                deadline_date = datetime.fromisoformat(action.deadline)
                reminder_date = deadline_date - timedelta(days=1)
                
                # Ajouter à midi
                reminder_date = reminder_date.replace(hour=12, minute=0, second=0)
                
                # Créer l'événement
                new_event = ScheduledEvent(
                    title=action_title,
                    description=f"Rappel pour l'action: {action.description}",
                    event_type="action",
                    scheduled_time=reminder_date.isoformat()
                )
                
                events.append(new_event)
    
    # Sauvegarder les événements mis à jour
    return save_scheduled_events(events)


if __name__ == "__main__":
    # Vérifier et traiter les notifications
    num_notifications = process_due_notifications()
    print(f"✅ {num_notifications} notifications traitées.") 