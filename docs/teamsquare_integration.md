# Intégration TeamSquare pour NetGuardian

Ce document décrit l'intégration spécifique du système multi-agents NetGuardian pour TeamSquare, un cabinet de conseil spécialisé en management de projet, du changement et de la transformation.

## À propos de TeamSquare

TeamSquare est un cabinet de conseil spécialisé qui accompagne les organisations dans leurs projets de transformation digitale et organisationnelle. Avec des bureaux à Lyon, Paris et Genève, TeamSquare offre une expertise reconnue avec un taux de satisfaction client de 98/100.

### Services principaux
- Management de la Transformation
- Conseil en Organisation
- Solutions Digitales
- Formation

### Valeurs
- Excellence
- Innovation
- Collaboration
- Engagement
- Adaptabilité

## Fonctionnalités spécifiques à TeamSquare

Le système multi-agents NetGuardian a été adapté pour répondre aux besoins spécifiques de TeamSquare avec les fonctionnalités suivantes:

1. **Agent TeamSquare dédié**: Un agent spécialisé qui combine support client et expertise métier, capable de répondre aux questions sur les services, l'entreprise et les méthodologies de TeamSquare.

2. **Base de connaissances enrichie**: Intégration des informations spécifiques à TeamSquare, incluant:
   - Informations sur l'entreprise
   - Services et expertise
   - Vision et valeurs
   - Partenariats
   - FAQ

3. **Routeur d'intentions personnalisé**: Adaptation du routeur pour reconnaître les intentions spécifiques à TeamSquare et diriger les requêtes vers l'agent approprié.

4. **Modèle de classification entraîné**: Un modèle de classification d'intentions entraîné avec des exemples spécifiques à TeamSquare pour une meilleure compréhension des requêtes.

5. **Intégration de cybersécurité**: Capacité à répondre aux questions de sécurité informatique et à effectuer des analyses de vulnérabilités, adaptées au contexte de TeamSquare.

## Configuration et déploiement

### Prérequis
- Python 3.9+
- Docker et Docker Compose
- Clé API OpenAI
- Accès à Weights & Biases (optionnel pour le suivi des modèles)

### Variables d'environnement
\`\`\`
OPENAI_API_KEY=votre_clé_api_openai
EMBEDDING_MODEL=BAAI/bge-large-en-v1.5
TEAMSQUARE_MODEL=gpt-4
WANDB_API_KEY=votre_clé_api_wandb (optionnel)
\`\`\`

### Installation

1. Cloner le dépôt:
\`\`\`bash
git clone https://github.com/votre-organisation/netguardian.git
cd netguardian
\`\`\`

2. Créer un fichier .env avec les variables d'environnement nécessaires.

3. Construire et démarrer les conteneurs:
\`\`\`bash
docker-compose up -d
\`\`\`

4. Ingérer les données TeamSquare:
\`\`\`bash
docker-compose exec app python scripts/ingest_teamsquare_data.py
\`\`\`

### Utilisation

Une fois le système déployé, vous pouvez interagir avec lui via:

1. **API REST**: Accessible à l'adresse `http://localhost:8000/api`
2. **Interface Web**: Accessible à l'adresse `http://localhost:3000`

## Personnalisation

Le système peut être davantage personnalisé pour TeamSquare en:

1. Enrichissant la base de connaissances avec plus de contenu spécifique à TeamSquare
2. Ajoutant des exemples supplémentaires pour l'entraînement du classificateur d'intentions
3. Développant des agents spécialisés pour des domaines d'expertise spécifiques de TeamSquare

## Maintenance et mise à jour

Pour maintenir le système à jour:

1. Mettre à jour régulièrement la base de connaissances avec les nouvelles informations de TeamSquare
2. Réentraîner périodiquement le modèle de classification d'intentions
3. Surveiller les performances et ajuster les configurations selon les besoins

## Support

Pour toute question ou assistance concernant l'intégration TeamSquare, veuillez contacter:

- Support technique: support@netguardian.ai
- Responsable de l'intégration: integration@netguardian.ai
