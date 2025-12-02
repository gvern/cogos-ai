# 🧠 CogOS - Personal Cognitive Operating System

Une constellation de connaissances interactive qui organise et visualise votre savoir personnel.

## 🏗️ Structure du Projet

```
cogos-ai/
├── app/                    # Application principale
│   ├── api/               # Backend FastAPI
│   ├── core/              # Logique métier core
│   └── web/               # Interface web
├── data/                  # Données utilisateur
├── config/                # Configuration
├── docs/                  # Documentation
├── tools/                 # Scripts et outils
└── cogos.yaml            # Configuration principale
```

## 🚀 Démarrage Rapide

1. **Installation des dépendances**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r app/api/requirements.txt
   ```

2. **Lancement de CogOS**
   ```bash
   ./start_cogos.sh
   ```

3. **Accès à l'interface**
   - API: http://localhost:8000
   - Constellation: http://localhost:8000/static/constellation.html
   - Documentation: http://localhost:8000/docs

## 🌌 Fonctionnalités

- **Constellation de Connaissances**: Visualisation interactive de vos données
- **API REST**: Interface programmatique pour accéder aux données
- **Ingestion Automatique**: Import de données depuis diverses sources
- **Graphe de Relations**: Connexions intelligentes entre concepts

## 📁 Composants

### app/api/
Backend FastAPI avec:
- Routes pour la constellation de connaissances
- Système de mémoire et contexte
- Ingestion de données
- WebSockets pour temps réel

### app/core/
Logique métier:
- Gestion de la mémoire
- Construction du contexte
- Agent intelligent
- Traitement audio/vocal

### app/web/
Interface utilisateur:
- Visualisation de la constellation
- Assets statiques
- Interface interactive

## 🛠️ Développement

Voir `docs/` pour la documentation complète du développement.

## 📊 État du Projet

✅ API Backend fonctionnelle  
✅ Visualisation constellation  
✅ Système de mémoire  
🔄 Ingestion de données  
🔄 Interface utilisateur avancée  
