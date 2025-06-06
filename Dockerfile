FROM python:3.10-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Créer les répertoires nécessaires
RUN mkdir -p data/vector_db data/feedback models

# Exposer le port
EXPOSE 8000

# Commande par défaut
CMD ["python", "main.py", "--mode", "api", "--host", "0.0.0.0", "--port", "8000"]
