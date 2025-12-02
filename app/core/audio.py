"""
CogOS Audio Module - Gestion de la synthèse vocale (TTS) et des sorties audio
"""
from openai import OpenAI
from config.secrets import get_api_key
import os
import subprocess
import platform
from pathlib import Path
from datetime import datetime
import json

client = OpenAI(api_key=get_api_key())

# Voix disponibles
AVAILABLE_VOICES = {
    "nova": "Voix féminine claire et naturelle",
    "alloy": "Voix neutre et équilibrée",
    "echo": "Voix profonde avec une tonalité plus grave",
    "fable": "Voix narrative expressive",
    "onyx": "Voix masculine profonde et autoritaire",
    "shimmer": "Voix légère et mélodieuse"
}

DEFAULT_VOICE = "nova"

def speak_response(text: str, voice: str = DEFAULT_VOICE, save_history: bool = True) -> str:
    """
    Convertit le texte en audio et le lit.
    
    Args:
        text: Le texte à lire
        voice: La voix à utiliser (doit être dans AVAILABLE_VOICES)
        save_history: Si True, enregistre l'historique des lectures
        
    Returns:
        Le chemin du fichier audio généré
    """
    if voice not in AVAILABLE_VOICES:
        voice = DEFAULT_VOICE
    
    # Créer le dossier de sortie
    output_dir = Path("output/tts")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Générer un nom de fichier unique
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"tts_{voice}_{timestamp}.mp3"
    
    try:
        # Générer la réponse vocale
        speech = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        
        # Enregistrer le fichier
        with open(output_file, "wb") as f:
            f.write(speech.content)
        
        # Jouer le fichier selon le système d'exploitation
        play_audio_file(output_file)
        
        # Enregistrer dans l'historique
        if save_history:
            log_tts_response(text, str(output_file), voice)
        
        return str(output_file)
    
    except Exception as e:
        print(f"Erreur lors de la génération audio: {e}")
        return ""


def play_audio_file(file_path: str) -> bool:
    """
    Joue un fichier audio selon le système d'exploitation.
    
    Args:
        file_path: Chemin vers le fichier audio à lire
        
    Returns:
        True si la lecture a réussi, False sinon
    """
    system = platform.system()
    
    try:
        if system == "Darwin":  # macOS
            subprocess.run(["afplay", file_path], check=True)
        elif system == "Windows":
            from winsound import PlaySound, SND_FILENAME
            PlaySound(file_path, SND_FILENAME)
        elif system == "Linux":
            subprocess.run(["ffplay", "-nodisp", "-autoexit", file_path], check=True)
        else:
            print(f"Système d'exploitation non pris en charge: {system}")
            return False
        
        return True
    
    except Exception as e:
        print(f"Erreur lors de la lecture audio: {e}")
        return False


def log_tts_response(text: str, file_path: str, voice: str) -> None:
    """
    Enregistre l'historique des générations TTS.
    
    Args:
        text: Le texte converti en audio
        file_path: Le chemin du fichier audio généré
        voice: La voix utilisée
    """
    log_dir = Path("logs/tts_history")
    log_dir.mkdir(exist_ok=True, parents=True)
    
    log_file = log_dir / "tts_history.jsonl"
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "text": text,
        "file_path": file_path,
        "voice": voice
    }
    
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        print(f"Erreur lors de la journalisation TTS: {e}")


def get_tts_history(limit: int = 10) -> list:
    """
    Récupère l'historique des générations TTS.
    
    Args:
        limit: Nombre maximum d'entrées à récupérer
        
    Returns:
        Une liste des dernières entrées TTS
    """
    log_file = Path("logs/tts_history/tts_history.jsonl")
    
    if not log_file.exists():
        return []
    
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            entries = [json.loads(line) for line in f if line.strip()]
        
        # Trier par horodatage (le plus récent en premier)
        entries.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Limiter le nombre d'entrées
        return entries[:limit]
    
    except Exception as e:
        print(f"Erreur lors de la lecture de l'historique TTS: {e}")
        return []


def get_available_voices():
    """Retourne les voix disponibles et leurs descriptions."""
    return AVAILABLE_VOICES
