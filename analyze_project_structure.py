#!/usr/bin/env python3
"""
Script d'analyse de la structure du projet NextGen-Agent
Génère un rapport complet des fichiers et dossiers
"""

import os
import json
from pathlib import Path
from collections import defaultdict
import hashlib

def get_file_info(file_path):
    """Récupère les informations d'un fichier"""
    try:
        stat = os.stat(file_path)
        with open(file_path, 'rb') as f:
            content = f.read()
        
        return {
            'size': stat.st_size,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'lines': len(content.decode('utf-8', errors='ignore').splitlines()) if content else 0,
            'hash': hashlib.md5(content).hexdigest()[:8],
            'empty': len(content.strip()) == 0 if content else True
        }
    except Exception as e:
        return {
            'size': 0,
            'size_mb': 0,
            'lines': 0,
            'hash': 'error',
            'empty': True,
            'error': str(e)
        }

def analyze_project():
    """Analyse complète du projet"""
    
    # Dossiers à ignorer
    ignore_dirs = {
        '.git', '__pycache__', '.next', 'node_modules', 
        '.vscode', '.idea', 'dist', 'build', '.env',
        'logs', 'data/vector_db', 'data/graph_db'
    }
    
    # Extensions à analyser
    code_extensions = {
        '.py', '.js', '.ts', '.tsx', '.jsx', '.json', 
        '.md', '.yml', '.yaml', '.txt', '.sh', '.css'
    }
    
    project_structure = {
        'folders': defaultdict(list),
        'files_by_type': defaultdict(list),
        'duplicates': defaultdict(list),
        'empty_files': [],
        'large_files': [],
        'stats': {
            'total_files': 0,
            'total_size_mb': 0,
            'total_lines': 0
        }
    }
    
    file_hashes = defaultdict(list)
    
    print("🔍 Analyse de la structure du projet...")
    print("=" * 60)
    
    # Parcourir tous les fichiers
    for root, dirs, files in os.walk('.'):
        # Filtrer les dossiers à ignorer
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        folder_path = root.replace('./', '').replace('.\\', '')
        if not folder_path:
            folder_path = 'ROOT'
        
        # Analyser chaque fichier
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = file_path.replace('./', '').replace('.\\', '')
            
            # Ignorer certains fichiers
            if file.startswith('.') and file not in ['.env', '.env.example']:
                continue
            
            file_ext = Path(file).suffix.lower()
            file_info = get_file_info(file_path)
            
            # Informations du fichier
            file_data = {
                'path': rel_path,
                'name': file,
                'folder': folder_path,
                'extension': file_ext,
                **file_info
            }
            
            # Catégoriser
            project_structure['folders'][folder_path].append(file_data)
            project_structure['files_by_type'][file_ext].append(file_data)
            
            # Détecter les doublons
            if file_info['hash'] != 'error':
                file_hashes[file_info['hash']].append(file_data)
            
            # Fichiers vides
            if file_info['empty']:
                project_structure['empty_files'].append(file_data)
            
            # Gros fichiers (>1MB)
            if file_info['size_mb'] > 1:
                project_structure['large_files'].append(file_data)
            
            # Stats globales
            project_structure['stats']['total_files'] += 1
            project_structure['stats']['total_size_mb'] += file_info['size_mb']
            project_structure['stats']['total_lines'] += file_info['lines']
    
    # Identifier les vrais doublons
    for hash_val, files in file_hashes.items():
        if len(files) > 1:
            project_structure['duplicates'][hash_val] = files
    
    return project_structure

def print_analysis(structure):
    """Affiche l'analyse"""
    
    print(f"\n📊 STATISTIQUES GLOBALES")
    print("=" * 40)
    stats = structure['stats']
    print(f"�� Total fichiers: {stats['total_files']}")
    print(f"💾 Taille totale: {stats['total_size_mb']:.2f} MB")
    print(f"📝 Total lignes: {stats['total_lines']:,}")
    
    print(f"\n📂 STRUCTURE DES DOSSIERS")
    print("=" * 40)
    for folder, files in sorted(structure['folders'].items()):
        total_size = sum(f['size_mb'] for f in files)
        total_lines = sum(f['lines'] for f in files)
        print(f"📁 {folder:<30} | {len(files):>3} fichiers | {total_size:>6.2f}MB | {total_lines:>6} lignes")
    
    print(f"\n📄 FICHIERS PAR TYPE")
    print("=" * 40)
    for ext, files in sorted(structure['files_by_type'].items()):
        if ext in ['.py', '.js', '.ts', '.tsx', '.json', '.md']:
            total_size = sum(f['size_mb'] for f in files)
            total_lines = sum(f['lines'] for f in files)
            print(f"{ext:<8} | {len(files):>3} fichiers | {total_size:>6.2f}MB | {total_lines:>6} lignes")
    
    print(f"\n🗑️  FICHIERS POTENTIELLEMENT INUTILES")
    print("=" * 50)
    
    # Fichiers vides
    if structure['empty_files']:
        print(f"\n📄 FICHIERS VIDES ({len(structure['empty_files'])}):")
        for file in structure['empty_files'][:10]:  # Limiter à 10
            print(f"   ❌ {file['path']}")
        if len(structure['empty_files']) > 10:
            print(f"   ... et {len(structure['empty_files']) - 10} autres")
    
    # Doublons
    if structure['duplicates']:
        print(f"\n🔄 FICHIERS DUPLIQUÉS ({len(structure['duplicates'])}):")
        for hash_val, files in list(structure['duplicates'].items())[:5]:
            print(f"   🔄 Hash {hash_val}:")
            for file in files:
                print(f"      - {file['path']}")
    
    # Gros fichiers
    if structure['large_files']:
        print(f"\n📦 GROS FICHIERS (>1MB) ({len(structure['large_files'])}):")
        large_sorted = sorted(structure['large_files'], key=lambda x: x['size_mb'], reverse=True)
        for file in large_sorted[:10]:
            print(f"   📦 {file['path']:<50} | {file['size_mb']:>6.2f}MB")
    
    # Fichiers suspects
    print(f"\n🚨 FICHIERS SUSPECTS:")
    suspects = []
    
    for folder, files in structure['folders'].items():
        for file in files:
            # Scripts de test multiples
            if 'test_' in file['name'] and file['lines'] < 10:
                suspects.append(f"   🧪 {file['path']} (test minimal)")
            
            # Scripts setup multiples
            if 'setup' in file['name'] and 'scripts' in file['folder']:
                suspects.append(f"   ⚙️  {file['path']} (setup script)")
            
            # Fichiers de fix
            if 'fix_' in file['name']:
                suspects.append(f"   🔧 {file['path']} (script de fix)")
    
    for suspect in suspects[:15]:  # Limiter à 15
        print(suspect)

def generate_cleanup_script(structure):
    """Génère un script de nettoyage"""
    
    cleanup_commands = []
    
    # Fichiers vides
    for file in structure['empty_files']:
        if file['extension'] not in ['.gitkeep', '.env']:
            cleanup_commands.append(f"rm '{file['path']}'")
    
    # Doublons (garder le premier)
    for hash_val, files in structure['duplicates'].items():
        for file in files[1:]:  # Supprimer tous sauf le premier
            cleanup_commands.append(f"rm '{file['path']}'")
    
    # Scripts de fix anciens
    for folder, files in structure['folders'].items():
        if 'scripts' in folder:
            fix_files = [f for f in files if 'fix_' in f['name']]
            if len(fix_files) > 3:  # Garder seulement les 3 plus récents
                for file in fix_files[3:]:
                    cleanup_commands.append(f"rm '{file['path']}'")
    
    # Sauvegarder le script
    with open('cleanup_project.sh', 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("# Script de nettoyage généré automatiquement\n")
        f.write("# ATTENTION: Vérifiez avant d'exécuter !\n\n")
        f.write("echo '🧹 Nettoyage du projet...'\n\n")
        
        for cmd in cleanup_commands:
            f.write(f"echo 'Suppression: {cmd.split()[-1]}'\n")
            f.write(f"# {cmd}\n\n")
        
        f.write("echo '✅ Nettoyage terminé !'\n")
    
    print(f"\n📝 Script de nettoyage généré: cleanup_project.sh")
    print(f"   Commandes de suppression: {len(cleanup_commands)}")

if __name__ == "__main__":
    try:
        structure = analyze_project()
        print_analysis(structure)
        generate_cleanup_script(structure)
        
        # Sauvegarder l'analyse complète
        with open('project_analysis.json', 'w') as f:
            json.dump(structure, f, indent=2, default=str)
        
        print(f"\n💾 Analyse complète sauvegardée: project_analysis.json")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
