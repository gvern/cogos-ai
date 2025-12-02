# CogOS Frontend

Ce répertoire contient le code frontend de l'application CogOS, un système cognitif personnel qui transforme votre expérience d'interaction avec l'IA.

## Technologies utilisées

- **Next.js** : Framework React pour le rendu côté serveur et le routage
- **React** : Bibliothèque UI pour la construction d'interfaces
- **TypeScript** : Typage statique pour JavaScript
- **Tailwind CSS** : Framework CSS utilitaire
- **Framer Motion** : Animation pour React
- **Zustand** : Gestion d'état minimaliste
- **React Query** : Gestion des requêtes et du cache
- **Chart.js** : Visualisation de données

## Structure du projet

```
frontend/
├── public/           # Fichiers statiques
├── src/
│   ├── components/   # Composants réutilisables
│   │   ├── features/ # Composants spécifiques aux fonctionnalités
│   │   ├── layout/   # Composants de mise en page
│   │   └── ui/       # Composants d'interface utilisateur
│   ├── lib/          # Utilitaires et fonctions d'aide
│   ├── pages/        # Pages de l'application (routage Next.js)
│   └── styles/       # Styles globaux
├── README.md         # Documentation du projet
└── package.json      # Dépendances et scripts
```

## Fonctionnalités principales

- **Tableau de bord** : Vue d'ensemble des activités et des insights
- **Conversation** : Interface de chat avec l'IA
- **Mise à jour du contexte** : Modification du profil et des préférences
- **Visualisation des données** : Graphiques radar et tableaux de bord
- **Mode JARVIS** : Interface immersive pour une expérience enrichie

## Installation

1. Assurez-vous d'avoir Node.js installé (version 16 ou supérieure)
2. Clonez le dépôt
3. Installez les dépendances :

```bash
npm install
```

## Développement

Pour lancer le serveur de développement :

```bash
npm run dev
```

L'application sera disponible sur http://localhost:3000

## Construction

Pour construire l'application pour la production :

```bash
npm run build
```

## Déploiement

Pour démarrer le serveur de production :

```bash
npm start
```

## Intégration avec le backend

Le frontend communique avec le backend Python via une API RESTful. Les points de terminaison principaux incluent :

- `/api/context` : Gestion du contexte utilisateur
- `/api/conversations` : Gestion des conversations
- `/api/memory` : Accès à la mémoire et aux connaissances

## Licence

Ce projet est sous licence MIT. 