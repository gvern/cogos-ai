#!/bin/bash
# Script de démarrage de l'environnement de développement CogOS

echo "🚀 Démarrage de l'environnement de développement CogOS"

# Chemin du projet
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# Activer l'environnement virtuel si besoin
if [ -d "$PROJECT_DIR/venv" ]; then
    echo "🐍 Activation de l'environnement virtuel"
    source "$PROJECT_DIR/venv/bin/activate"
fi

# Démarrer le backend
echo "🔄 Démarrage du serveur backend (FastAPI)"
cd "$BACKEND_DIR" && ./start_server.sh &
BACKEND_PID=$!
echo "✅ Serveur backend démarré (PID: $BACKEND_PID)"

# Attendre que le backend soit prêt
echo "⏳ Attente du démarrage du backend..."
sleep 5

# Démarrer le frontend
echo "🌐 Démarrage du frontend (Next.js)"
cd "$FRONTEND_DIR" && npm run dev &
FRONTEND_PID=$!
echo "✅ Frontend démarré (PID: $FRONTEND_PID)"

echo "
🧠 CogOS est prêt !
📡 Backend API: http://localhost:8000
🖥️ Frontend: http://localhost:3000
"

# Fonction pour arrêter proprement les processus
cleanup() {
    echo "🛑 Arrêt des services CogOS"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Capturer les signaux pour arrêter proprement
trap cleanup INT TERM

# Attendre que l'utilisateur appuie sur Ctrl+C
echo "Appuyez sur Ctrl+C pour arrêter tous les services"
wait 