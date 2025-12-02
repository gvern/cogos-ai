# CogOS - Système Cognitif Personnel

CogOS est un système cognitif personnel avec interface JARVIS, conçu pour la gestion des connaissances, le tracking cognitif et la productivité augmentée par IA.

## Nouvelle Architecture (v2)

CogOS a été restructuré avec une architecture moderne et modulaire :

### Backend (FastAPI)

Le backend est maintenant une API RESTful complète avec FastAPI :

```
backend/
├── api/           # API FastAPI
│   ├── routes/    # Points d'entrée API
│   ├── schemas/   # Modèles Pydantic
│   └── main.py    # Point d'entrée
├── services/      # Services métier
└── run.py         # Script de lancement
```

### Frontend (Next.js)

Le frontend est une application moderne avec Next.js, React et Tailwind CSS :

```
frontend/
├── src/
│   ├── app/              # Pages de l'application
│   ├── components/       # Composants UI
│   ├── lib/              # Utilitaires et hooks
│   └── styles/           # Styles globaux
└── public/               # Assets statiques
```

## Fonctionnalités Principales

- **Interface JARVIS** avec reconnaissance vocale et TTS
- **Dashboard** interactif et visuellement riche
- **Timeline** avec graphe sémantique des connaissances
- **Agent Intelligent** qui propose des actions et défis
- **Contexte Cognitif** avec visualisation radar
- **Système de Mémoire** vectorielle pour stocker et retrouver l'information

## Installation et Démarrage

### Backend

```bash
# Installation des dépendances
cd backend
pip install -r requirements.txt

# Lancement du serveur API
python run.py --reload
```

### Frontend

```bash
# Installation des dépendances
cd frontend
npm install

# Lancement en développement
npm run dev
```

## Ancien système (Streamlit)

L'ancienne interface Streamlit est toujours disponible pour rétrocompatibilité :

```bash
# Lancement de l'interface Streamlit
streamlit run ui/app.py
```

## Technologies

- **Backend**: FastAPI, Pydantic, Uvicorn, OpenAI, ChromaDB
- **Frontend**: Next.js, TypeScript, Tailwind CSS, Chart.js, Zustand
- **Mémoire**: Embeddings vectoriels, RAG (Retrieval Augmented Generation)

## Licence

Projet personnel - Tous droits réservés

```bash
streamlit run ui/app.py
