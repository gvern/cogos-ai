# core/notify.py
import subprocess

def send_system_notification(message: str):
    subprocess.run([
        "osascript", "-e",
        f'display notification "{message}" with title "CogOS 🧠 Briefing du jour"'
    ])
