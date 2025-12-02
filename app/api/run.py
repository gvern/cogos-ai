#!/usr/bin/env python
"""
Script de lancement du serveur API CogOS
"""
import uvicorn
import argparse
from dotenv import load_dotenv
import os

def main():
    # Charger les variables d'environnement
    load_dotenv()
    
    # Parser les arguments de ligne de commande
    parser = argparse.ArgumentParser(description="Lancer le serveur API CogOS")
    parser.add_argument("--host", default="0.0.0.0", help="Adresse d'écoute")
    parser.add_argument("--port", default=8000, type=int, help="Port d'écoute")
    parser.add_argument("--reload", action="store_true", help="Activer le rechargement à chaud")
    args = parser.parse_args()
    
    # Configuration du serveur
    print(f"🧠 Démarrage du serveur API CogOS sur {args.host}:{args.port}")
    print(f"📝 Mode debug: {'Activé' if args.reload else 'Désactivé'}")
    print(f"🌐 Environnement: {os.getenv('ENV', 'development')}")
    
    # Lancer le serveur
    uvicorn.run(
        "backend.api.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )

if __name__ == "__main__":
    main() 