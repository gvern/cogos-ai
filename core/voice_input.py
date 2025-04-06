import streamlit as st
import json
import os
import uuid
from pathlib import Path
from datetime import datetime

# Tentative d'importer SpeechRecognition (avec fallback)
try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False

# Tentative d'importer sounddevice (alternative à pyaudio)
try:
    import sounddevice as sd
    import soundfile as sf
    HAS_SOUNDDEVICE = True
except ImportError:
    HAS_SOUNDDEVICE = False

def start_new_session() -> str:
    """Commence une nouvelle session d'enregistrement vocal."""
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    return session_id

def listen_from_microphone(session_id: str = None, save_audio: bool = True) -> dict:
    """
    Capture audio from microphone and convert to text.
    Falls back to Streamlit file uploader if PyAudio is not available.
    
    Args:
        session_id: Identifiant de session pour regrouper les enregistrements
        save_audio: Si True, sauvegarde l'audio dans logs/voice_sessions/
        
    Returns:
        dict: {
            "text": texte reconnu,
            "success": booléen indiquant si la reconnaissance a réussi,
            "audio_file": chemin du fichier audio s'il a été sauvegardé,
            "timestamp": horodatage ISO
        }
    """
    timestamp = datetime.now().isoformat()
    result = {
        "text": "",
        "success": False,
        "audio_file": None,
        "timestamp": timestamp
    }
    
    if session_id is None:
        session_id = str(uuid.uuid4())[:8]
    
    # Créer le dossier de logs si nécessaire
    voice_logs_dir = Path("logs/voice_sessions") / session_id
    if save_audio:
        voice_logs_dir.mkdir(exist_ok=True, parents=True)
    
    if HAS_SR:
        try:
            r = sr.Recognizer()
            with sr.Microphone() as source:
                st.info("🎙️ Parle maintenant...")
                
                # Ajuster pour le bruit ambiant
                r.adjust_for_ambient_noise(source, duration=0.5)
                
                # Écouter
                audio = r.listen(source, timeout=5)
                
                # Sauvegarder l'audio si demandé
                if save_audio:
                    audio_file = voice_logs_dir / f"voice_{timestamp.replace(':', '-')}.wav"
                    with open(audio_file, "wb") as f:
                        f.write(audio.get_wav_data())
                    result["audio_file"] = str(audio_file)
                
                # Reconnaître
                try:
                    recognized_text = r.recognize_google(audio, language="fr-FR")
                    result["text"] = recognized_text
                    result["success"] = True
                    
                    # Journaliser le résultat
                    log_voice_recognition(session_id, result)
                    
                    return result
                except sr.UnknownValueError:
                    result["text"] = "🤖 Je n'ai pas compris."
                    return result
                except sr.RequestError:
                    result["text"] = "❌ Service de reconnaissance indisponible."
                    return result
                
        except (ImportError, OSError, AttributeError) as e:
            st.warning(f"Erreur microphone: {e}. Utilisation du mode fichier.")
            return _listen_from_file_fallback(session_id, save_audio)
    
    # Essayer avec sounddevice si disponible
    elif HAS_SOUNDDEVICE:
        try:
            return _listen_with_sounddevice(session_id, save_audio)
        except Exception as e:
            st.warning(f"Erreur avec sounddevice: {e}. Utilisation du mode fichier.")
            return _listen_from_file_fallback(session_id, save_audio)
    
    # Fallback à l'upload de fichier
    else:
        return _listen_from_file_fallback(session_id, save_audio)


def _listen_with_sounddevice(session_id: str, save_audio: bool) -> dict:
    """Utilise sounddevice pour l'enregistrement."""
    timestamp = datetime.now().isoformat()
    result = {
        "text": "",
        "success": False,
        "audio_file": None,
        "timestamp": timestamp
    }
    
    voice_logs_dir = Path("logs/voice_sessions") / session_id
    if save_audio:
        voice_logs_dir.mkdir(exist_ok=True, parents=True)
    
    # Configuration d'enregistrement
    fs = 44100  # Fréquence d'échantillonnage
    duration = 5  # Durée en secondes
    
    # Afficher l'indicateur d'enregistrement
    st.info("🎙️ Enregistrement en cours... (5 secondes)")
    
    # Enregistrer
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()  # Attendre la fin de l'enregistrement
    
    # Sauvegarder
    audio_file = voice_logs_dir / f"voice_{timestamp.replace(':', '-')}.wav"
    sf.write(audio_file, recording, fs)
    result["audio_file"] = str(audio_file)
    
    # Reconnaissance avec SpeechRecognition
    if HAS_SR:
        r = sr.Recognizer()
        try:
            with sr.AudioFile(str(audio_file)) as source:
                audio_data = r.record(source)
                recognized_text = r.recognize_google(audio_data, language="fr-FR")
                result["text"] = recognized_text
                result["success"] = True
                
                # Journaliser
                log_voice_recognition(session_id, result)
                
                return result
        except Exception as e:
            result["text"] = f"Erreur de reconnaissance: {e}"
            return result
    
    result["text"] = "⚠️ SpeechRecognition n'est pas installé pour la reconnaissance."
    return result


def _listen_from_file_fallback(session_id: str, save_audio: bool) -> dict:
    """Fallback method using audio file upload instead of microphone."""
    timestamp = datetime.now().isoformat()
    result = {
        "text": "",
        "success": False,
        "audio_file": None,
        "timestamp": timestamp
    }
    
    voice_logs_dir = Path("logs/voice_sessions") / session_id
    if save_audio:
        voice_logs_dir.mkdir(exist_ok=True, parents=True)
    
    st.info("💡 Le mode micro n'est pas disponible. Tu peux télécharger un fichier audio à la place.")
    audio_file = st.file_uploader("Télécharge un fichier audio (WAV, MP3, etc.)", type=["wav", "mp3", "m4a"])
    
    if audio_file is not None:
        if HAS_SR:
            r = sr.Recognizer()
            try:
                # Sauvegarder temporairement le fichier
                temp_file = "temp_audio.wav"
                with open(temp_file, "wb") as f:
                    f.write(audio_file.getvalue())
                
                # Copier vers les logs si demandé
                if save_audio:
                    saved_file = voice_logs_dir / f"voice_{timestamp.replace(':', '-')}.wav"
                    saved_file.parent.mkdir(exist_ok=True, parents=True)
                    with open(temp_file, "rb") as src, open(saved_file, "wb") as dst:
                        dst.write(src.read())
                    result["audio_file"] = str(saved_file)
                
                # Reconnaissance
                with sr.AudioFile(temp_file) as source:
                    audio_data = r.record(source)
                    recognized_text = r.recognize_google(audio_data, language="fr-FR")
                    result["text"] = recognized_text
                    result["success"] = True
                    
                    # Journaliser
                    log_voice_recognition(session_id, result)
                    
                    return result
            except Exception as e:
                result["text"] = f"Erreur de reconnaissance: {e}"
                return result
            finally:
                # Nettoyage
                if os.path.exists(temp_file):
                    os.remove(temp_file)
        else:
            result["text"] = "⚠️ SpeechRecognition n'est pas installé. Utilise 'pip install SpeechRecognition'."
            return result
    
    return result


def log_voice_recognition(session_id: str, result: dict) -> None:
    """Enregistre les résultats de reconnaissance vocale dans un fichier de logs."""
    log_dir = Path("logs/voice_recognition")
    log_dir.mkdir(exist_ok=True, parents=True)
    
    log_file = log_dir / f"{session_id}.jsonl"
    
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(result) + "\n")
    except Exception as e:
        print(f"Erreur lors de la journalisation de la reconnaissance vocale: {e}")


def get_session_history(session_id: str) -> list:
    """Récupère l'historique des reconnaissances vocales pour une session."""
    log_file = Path("logs/voice_recognition") / f"{session_id}.jsonl"
    
    if not log_file.exists():
        return []
    
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]
    except Exception as e:
        print(f"Erreur lors de la lecture de l'historique de session: {e}")
        return [] 