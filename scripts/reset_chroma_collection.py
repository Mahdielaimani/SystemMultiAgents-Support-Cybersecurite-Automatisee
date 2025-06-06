"""
Script pour réinitialiser la collection ChromaDB avec le bon modèle d'embedding
"""
import os
import sys
import logging
import shutil
from pathlib import Path

# Ajouter le répertoire racine au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def reset_chroma_collection():
    """Réinitialise la collection ChromaDB"""
    try:
        # Chemins des collections ChromaDB
        chroma_paths = [
            "./data/vector_db/chroma_db",
            "./chroma_db",
            "./data/chroma_db"
        ]
        
        # Supprimer toutes les collections existantes
        for path in chroma_paths:
            if os.path.exists(path):
                logger.info(f"🗑️ Suppression de {path}")
                shutil.rmtree(path)
                logger.info(f"✅ {path} supprimé")
        
        # Créer le dossier principal
        os.makedirs("./data/vector_db/chroma_db", exist_ok=True)
        logger.info("✅ Dossier ./data/vector_db/chroma_db créé")
        
        # Tester la création d'une nouvelle collection
        try:
            import chromadb
            from chromadb.config import Settings
            from sentence_transformers import SentenceTransformer
            
            logger.info("🔄 Chargement du modèle BGE-Large-EN...")
            model = SentenceTransformer('BAAI/bge-large-en-v1.5')
            logger.info(f"✅ Modèle chargé - Dimension: {model.get_sentence_embedding_dimension()}")
            
            logger.info("🔄 Création d'une nouvelle collection ChromaDB...")
            client = chromadb.PersistentClient(
                path="./data/vector_db/chroma_db",
                settings=Settings(anonymized_telemetry=False)
            )
            
            collection = client.create_collection(
                name="knowledge_base",
                metadata={"description": "Base de connaissances NextGen-Agent"}
            )
            
            # Ajouter un document de test
            test_doc = "Ceci est un document de test pour vérifier la compatibilité des dimensions."
            embedding = model.encode([test_doc]).tolist()[0]  # Prendre le premier élément pour éviter la triple imbrication
            
            collection.add(
                embeddings=[embedding],  # embedding est déjà une liste de floats
                documents=[test_doc],
                metadatas=[{"source": "test"}],
                ids=["test_1"]
            )
            
            logger.info(f"✅ Collection créée et testée avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la création de la collection: {e}")
            raise
            
        logger.info("✅ Réinitialisation terminée avec succès")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la réinitialisation: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 RÉINITIALISATION DE LA COLLECTION CHROMADB")
    logger.info("=" * 50)
    
    success = reset_chroma_collection()
    
    if success:
        logger.info("✅ RÉINITIALISATION RÉUSSIE")
    else:
        logger.error("❌ ÉCHEC DE LA RÉINITIALISATION")
