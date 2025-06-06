# NextGen-Agent 🤖

Système d'agents IA intelligents pour le support client et la cybersécurité, utilisant LangChain, LangGraph et des modèles d'IA avancés.

## 🚀 Démarrage rapide

### Prérequis
- Python 3.8+
- Node.js 16+
- npm ou yarn
- Git

### Installation automatique

\`\`\`bash
# Cloner le projet
git clone <votre-repo>
cd nextgen-agent

# Lancer l'installation automatique
chmod +x setup.sh
./setup.sh
\`\`\`

### Installation manuelle

1. **Configuration de l'environnement**
\`\`\`bash
python scripts/setup_environment.py
\`\`\`

2. **Configuration des clés API**
\`\`\`bash
cp .env.example .env
# Éditez .env avec vos clés API
\`\`\`

3. **Téléchargement des modèles**
\`\`\`bash
python scripts/auto_setup_models.py
\`\`\`

4. **Validation du système**
\`\`\`bash
python scripts/validate_models.py
\`\`\`

5. **Démarrage du système**
\`\`\`bash
python scripts/start_system.py
\`\`\`

## 🏗️ Architecture

### Composants principaux

- **Frontend**: Next.js avec TypeScript et Tailwind CSS
- **Backend**: FastAPI avec Python
- **Agents IA**: LangChain et LangGraph
- **Base de données**: ChromaDB (vectorielle) + Neo4j (graphe)
- **Modèles**: Modèles personnalisés entraînés sur Kaggle

### Agents disponibles

1. **Agent de Support** 🎧
   - Réponse aux questions clients
   - Recherche dans la base de connaissances
   - Génération de réponses contextuelles

2. **Agent Cybersécurité** 🛡️
   - Classification des vulnérabilités
   - Analyse du trafic réseau
   - Détection d'anomalies

## 📁 Structure du projet

\`\`\`
nextgen-agent/
├── app/                    # Frontend Next.js
├── api/                    # API FastAPI
├── agents/                 # Agents IA
│   ├── support_agent/
│   └── cybersecurity_agent/
├── core/                   # Composants centraux
├── config/                 # Configuration
├── data/                   # Données et bases
├── models/                 # Modèles IA
├── scripts/                # Scripts utilitaires
└── tests/                  # Tests
\`\`\`

## 🔧 Configuration

### Variables d'environnement

Copiez `.env.example` vers `.env` et configurez:

\`\`\`env
# API Keys
OPENAI_API_KEY=sk-your_key_here
ANTHROPIC_API_KEY=your_key_here

# Kaggle (pour les modèles)
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_key

# Ports
API_PORT=8000
UI_PORT=3000
\`\`\`

### Configuration Kaggle

1. Créez un compte sur [Kaggle](https://kaggle.com)
2. Générez une clé API dans vos paramètres
3. Placez le fichier `kaggle.json` dans `~/.kaggle/`

## 🤖 Utilisation

### Interface web
- Frontend: http://localhost:3000
- API Documentation: http://localhost:8000/docs

### API REST

\`\`\`bash
# Statut du système
curl http://localhost:8000/health

# Chat avec l'agent de support
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Comment puis-je vous aider?"}'

# Scan de sécurité
curl -X POST http://localhost:8000/security/scan \
  -H "Content-Type: application/json" \
  -d '{"target": "example.com"}'
\`\`\`

## 🧪 Tests

\`\`\`bash
# Tests unitaires
pytest tests/

# Tests d'intégration
python scripts/validate_models.py

# Tests de performance
python scripts/benchmark.py
\`\`\`

## 📊 Monitoring

Le système inclut:
- Logs structurés avec Loguru
- Métriques de performance
- Monitoring des agents
- Alertes en temps réel

## 🔒 Sécurité

- Authentification JWT
- Validation des entrées
- Chiffrement des données sensibles
- Audit des actions

## 🚀 Déploiement

### Docker

\`\`\`bash
# Construction
docker-compose build

# Démarrage
docker-compose up -d
\`\`\`

### Production

\`\`\`bash
# Configuration production
export ENVIRONMENT=production

# Démarrage optimisé
python scripts/start_production.py
\`\`\`

## 🤝 Contribution

1. Fork le projet
2. Créez une branche feature
3. Committez vos changements
4. Poussez vers la branche
5. Ouvrez une Pull Request

## 📝 Licence

MIT License - voir le fichier [LICENSE](LICENSE)

## 🆘 Support

- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/votre-repo/issues)
- Email: support@nextgen-agent.com

## 🎯 Roadmap

- [ ] Interface de chat en temps réel
- [ ] Intégration Slack/Teams
- [ ] Modèles multilingues
- [ ] API GraphQL
- [ ] Mobile app
- [ ] Plugins personnalisés

---

Développé avec ❤️ par l'équipe NextGen-Agent
