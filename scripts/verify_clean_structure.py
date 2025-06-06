#!/usr/bin/env python3
"""
Vérification de la structure après nettoyage
"""

import os
from pathlib import Path

def verify_structure():
    """Vérifie que la structure est propre"""
    print("🔍 VÉRIFICATION DE LA STRUCTURE NETTOYÉE")
    print("=" * 50)
    
    # Structure attendue
    expected_structure = {
        "agents/": ["base_agent.py", "support_agent/", "cybersecurity_agent/"],
        "api/": ["server.py", "__init__.py"],
        "app/": ["page.tsx", "layout.tsx", "globals.css"],
        "components/": ["ui/", "main-interface.tsx"],
        "config/": ["settings.py", "models_urls.py"],
        "core/": ["router.py", "memory.py", "system.py"],
        "data/": ["vector_db/", "knowledge_base/"],
        "scripts/": ["test_agentic_support.py"],
        "utils/": ["logger.py", "complete_model_loader.py"]
    }
    
    print("✅ DOSSIERS PRINCIPAUX:")
    for folder, expected_files in expected_structure.items():
        folder_path = Path(folder)
        if folder_path.exists():
            print(f"  ✅ {folder}")
            for expected_file in expected_files:
                file_path = folder_path / expected_file
                if file_path.exists():
                    print(f"    ✅ {expected_file}")
                else:
                    print(f"    ❌ {expected_file} - MANQUANT")
        else:
            print(f"  ❌ {folder} - MANQUANT")
    
    # Vérifier l'absence de fichiers indésirables
    print(f"\n🧹 VÉRIFICATION NETTOYAGE:")
    
    unwanted_patterns = [
        "**/*.bak*",
        "**/chroma_db",
        "**/*.syntax_backup",
        ".next/",
        "ui/src/"
    ]
    
    found_unwanted = []
    for pattern in unwanted_patterns:
        matches = list(Path(".").glob(pattern))
        if matches:
            found_unwanted.extend(matches)
    
    if found_unwanted:
        print("  ❌ Fichiers indésirables trouvés:")
        for file in found_unwanted:
            print(f"    - {file}")
    else:
        print("  ✅ Aucun fichier indésirable trouvé")
    
    # Vérifier les fichiers critiques
    print(f"\n🎯 FICHIERS CRITIQUES:")
    critical_files = [
        "api/server.py",
        "agents/support_agent/agentic_support_agent.py",
        "app/page.tsx",
        "package.json",
        "requirements.txt",
        ".env"
    ]
    
    for file in critical_files:
        if Path(file).exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - CRITIQUE MANQUANT")

if __name__ == "__main__":
    verify_structure()
