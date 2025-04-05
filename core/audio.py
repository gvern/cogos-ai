from openai import OpenAI
from config.secrets import get_api_key
import os

client = OpenAI(api_key=get_api_key())

def speak_response(text: str):
    speech = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text
    )
    with open("output.mp3", "wb") as f:
        f.write(speech.content)
    os.system("afplay output.mp3")  # macOS
