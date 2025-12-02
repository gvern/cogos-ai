#!/bin/bash
# Script d'initialisation du frontend CogOS

# Se placer dans le répertoire du script
cd "$(dirname "$0")"

# Nettoyer le répertoire actuel (sauf ce script)
find . -maxdepth 1 ! -name 'setup_frontend.sh' ! -name '.' -exec rm -rf {} \;

# Initialiser un nouveau projet Next.js
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --no-git

# Créer la structure des dossiers
mkdir -p src/components/{ui,layout,features}
mkdir -p src/lib/{api,hooks,store}
mkdir -p src/app/{dashboard,agent,context,memory,timeline}
mkdir -p public/assets

# Installer les dépendances supplémentaires
npm install zustand @tanstack/react-query chart.js react-chartjs-2 date-fns framer-motion 