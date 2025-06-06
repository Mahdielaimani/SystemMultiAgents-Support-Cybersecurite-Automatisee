"""
Gestionnaire pour la base de données graphe Neo4j.
"""
import logging
import os
from typing import Dict, Any, List, Optional, Union
import json

from neo4j import GraphDatabase, Driver

logger = logging.getLogger(__name__)

class Neo4jManager:
    """
    Gestionnaire pour la base de données graphe Neo4j.
    """
    
    def __init__(self, uri: str, username: str, password: str):
        """
        Initialise le gestionnaire Neo4j.
        
        Args:
            uri: URI de la base Neo4j
            username: Nom d'utilisateur
            password: Mot de passe
        """
        self.uri = uri
        self.username = username
        self.password = password
        self.driver = None
        self._initialize_driver()
    
    def _initialize_driver(self):
        """Initialise le driver Neo4j."""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password)
            )
            logger.info(f"Neo4j driver initialized for URI: {self.uri}")
        except Exception as e:
            logger.error(f"Error initializing Neo4j driver: {str(e)}")
            raise
    
    def close(self):
        """Ferme le driver Neo4j."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j driver closed")
    
    def verify_connectivity(self) -> bool:
        """
        Vérifie la connectivité avec la base Neo4j.
        
        Returns:
            True si la connexion est établie, False sinon
        """
        try:
            with self.driver.session() as session:
                result = session.run("RETURN 1 AS result")
                return result.single()["result"] == 1
        except Exception as e:
            logger.error(f"Error verifying Neo4j connectivity: {str(e)}")
            return False
    
    async def create_document_node(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crée un nœud Document dans Neo4j.
        
        Args:
            document: Document à ajouter
            
        Returns:
            Résultat de l'opération
        """
        try:
            # Extraire les métadonnées
            metadata = document.get("metadata", {})
            source = metadata.get("source", "")
            title = metadata.get("title", "")
            
            # Créer le nœud Document
            query = """
            MERGE (d:Document {source: $source})
            SET d.title = $title,
                d.content_preview = $content_preview,
                d.last_updated = datetime()
            RETURN d
            """
            
            with self.driver.session() as session:
                result = session.run(
                    query,
                    source=source,
                    title=title,
                    content_preview=document.get("content", "")[:200]
                )
                
                record = result.single()
                if record:
                    logger.info(f"Document node created or updated: {source}")
                    return {"success": True, "node_id": record["d"].id}
                else:
                    logger.error("Failed to create document node")
                    return {"success": False, "error": "Failed to create document node"}
        except Exception as e:
            logger.error(f"Error creating document node: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def create_vulnerability_node(self, vulnerability: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crée un nœud Vulnerability dans Neo4j.
        
        Args:
            vulnerability: Vulnérabilité à ajouter
            
        Returns:
            Résultat de l'opération
        """
        try:
            # Extraire les informations
            name = vulnerability.get("name", "")
            severity = vulnerability.get("severity", "low")
            description = vulnerability.get("description", "")
            
            # Créer le nœud Vulnerability
            query = """
            MERGE (v:Vulnerability {name: $name})
            SET v.severity = $severity,
                v.description = $description,
                v.last_updated = datetime()
            RETURN v
            """
            
            with self.driver.session() as session:
                result = session.run(
                    query,
                    name=name,
                    severity=severity,
                    description=description
                )
                
                record = result.single()
                if record:
                    logger.info(f"Vulnerability node created or updated: {name}")
                    return {"success": True, "node_id": record["v"].id}
                else:
                    logger.error("Failed to create vulnerability node")
                    return {"success": False, "error": "Failed to create vulnerability node"}
        except Exception as e:
            logger.error(f"Error creating vulnerability node: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def link_document_to_vulnerability(self, document_source: str, vulnerability_name: str) -> Dict[str, Any]:
        """
        Crée une relation entre un document et une vulnérabilité.
        
        Args:
            document_source: Source du document
            vulnerability_name: Nom de la vulnérabilité
            
        Returns:
            Résultat de l'opération
        """
        try:
            # Créer la relation
            query = """
            MATCH (d:Document {source: $source})
            MATCH (v:Vulnerability {name: $name})
            MERGE (d)-[r:MENTIONS]->(v)
            SET r.created_at = datetime()
            RETURN d, v
            """
            
            with self.driver.session() as session:
                result = session.run(
                    query,
                    source=document_source,
                    name=vulnerability_name
                )
                
                record = result.single()
                if record:
                    logger.info(f"Linked document {document_source} to vulnerability {vulnerability_name}")
                    return {"success": True}
                else:
                    logger.error("Failed to link document to vulnerability")
                    return {"success": False, "error": "Failed to link document to vulnerability"}
        except Exception as e:
            logger.error(f"Error linking document to vulnerability: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_related_vulnerabilities(self, document_source: str) -> Dict[str, Any]:
        """
        Récupère les vulnérabilités liées à un document.
        
        Args:
            document_source: Source du document
            
        Returns:
            Liste des vulnérabilités liées
        """
        try:
            # Récupérer les vulnérabilités
            query = """
            MATCH (d:Document {source: $source})-[:MENTIONS]->(v:Vulnerability)
            RETURN v.name AS name, v.severity AS severity, v.description AS description
            """
            
            with self.driver.session() as session:
                result = session.run(
                    query,
                    source=document_source
                )
                
                vulnerabilities = []
                for record in result:
                    vulnerabilities.append({
                        "name": record["name"],
                        "severity": record["severity"],
                        "description": record["description"]
                    })
                
                logger.info(f"Retrieved {len(vulnerabilities)} vulnerabilities for document {document_source}")
                return {"success": True, "vulnerabilities": vulnerabilities}
        except Exception as e:
            logger.error(f"Error getting related vulnerabilities: {str(e)}")
            return {"success": False, "error": str(e)}
