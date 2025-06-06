#!/usr/bin/env python3
"""
Script pour générer les clés de sécurité pour NextGen-Agent.
"""
import secrets
import string
import os
from pathlib import Path

def generate_secret_key(length=64):
    """Génère une clé secrète sécurisée."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_jwt_secret(length=32):
    """Génère un secret JWT sécurisé."""
    return secrets.token_urlsafe(length)

def update_env_file():
    """Met à jour le fichier .env avec les nouvelles clés."""
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    
    # Générer les clés
    secret_key = generate_secret_key()
    jwt_secret = generate_jwt_secret()
    
    print("🔐 GÉNÉRATION DES CLÉS DE SÉCURITÉ")
    print("=" * 50)
    print(f"SECRET_KEY: {secret_key}")
    print(f"JWT_SECRET: {jwt_secret}")
    print("=" * 50)
    
    if env_file.exists():
        # Lire le fichier .env existant
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Remplacer les clés
        content = content.replace('SECRET_KEY=your_secret_key_here', f'SECRET_KEY={secret_key}')
        content = content.replace('JWT_SECRET=your_jwt_secret_here', f'JWT_SECRET={jwt_secret}')
        
        # Écrire le fichier mis à jour
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ Fichier .env mis à jour avec les nouvelles clés de sécurité")
        print(f"📁 Fichier: {env_file}")
    else:
        print("❌ Fichier .env non trouvé")
        print("Créez d'abord le fichier .env avec le template fourni")

if __name__ == "__main__":
    update_env_file()
