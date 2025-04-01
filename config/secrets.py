import os
from dotenv import load_dotenv

load_dotenv()

# Fournisseur par défaut (modifiable dynamiquement si tu veux)
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "openai").lower()

def get_api_key():
    if MODEL_PROVIDER == "openai":
        return os.getenv("OPENAI_API_KEY")
    elif MODEL_PROVIDER == "openrouter":
        return os.getenv("OPENROUTER_API_KEY")
    else:
        raise ValueError("❌ MODEL_PROVIDER inconnu dans .env")
