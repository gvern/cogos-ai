import streamlit as st

# Tentative d'importer SpeechRecognition (avec fallback)
try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False

def listen_from_microphone() -> str:
    """
    Capture audio from microphone and convert to text.
    Falls back to Streamlit file uploader if PyAudio is not available.
    """
    if HAS_SR:
        try:
            r = sr.Recognizer()
            with sr.Microphone() as source:
                st.info("🎙️ Parle maintenant...")
                audio = r.listen(source, timeout=5)
                try:
                    return r.recognize_google(audio, language="fr-FR")
                except sr.UnknownValueError:
                    return "🤖 Je n'ai pas compris."
                except sr.RequestError:
                    return "❌ Service de reconnaissance indisponible."
        except (ImportError, OSError, AttributeError) as e:
            st.warning(f"Erreur microphone: {e}. Utilisation du mode fichier.")
            return _listen_from_file_fallback()
    else:
        return _listen_from_file_fallback()

def _listen_from_file_fallback() -> str:
    """Fallback method using audio file upload instead of microphone."""
    st.info("💡 Le mode micro n'est pas disponible. Tu peux télécharger un fichier audio à la place.")
    audio_file = st.file_uploader("Télécharge un fichier audio (WAV, MP3, etc.)", type=["wav", "mp3", "m4a"])
    
    if audio_file is not None:
        if HAS_SR:
            r = sr.Recognizer()
            try:
                # Sauvegarde temporaire du fichier
                with open("temp_audio.wav", "wb") as f:
                    f.write(audio_file.getvalue())
                
                # Reconnaissance depuis le fichier
                with sr.AudioFile("temp_audio.wav") as source:
                    audio_data = r.record(source)
                    text = r.recognize_google(audio_data, language="fr-FR")
                    return text
            except Exception as e:
                return f"Erreur de reconnaissance: {e}"
            finally:
                # Nettoyage
                import os
                if os.path.exists("temp_audio.wav"):
                    os.remove("temp_audio.wav")
        else:
            return "⚠️ SpeechRecognition n'est pas installé. Utilise 'pip install SpeechRecognition'."
    
    return "" 