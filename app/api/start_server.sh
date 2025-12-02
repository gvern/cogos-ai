#!/bin/bash
# Script de démarrage du serveur API CogOS

cd "$(dirname "$0")"  # Se placer dans le répertoire du script
export PYTHONPATH="$(cd .. && pwd):$PYTHONPATH"  # Ajouter le répertoire parent au PYTHONPATH

# Démarrer le serveur avec uvicorn directement
python -c "import sys; sys.path.append('..'); from backend.api.main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000, reload=True)" 