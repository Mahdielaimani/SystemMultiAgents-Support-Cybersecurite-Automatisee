"""
Gestionnaire de graphes de connaissances pour NetGuardian.
"""
import time
from typing import Dict, List, Optional, Any, Set, Tuple
import re

from neo4j import GraphDatabase
from langchain_openai import OpenAIEmbeddings

from config.settings import settings
from config.logging_config import get_logger
from utils.preprocessing import clean_text

logger = get_logger("graph_manager")

class KnowledgeGraphManager:
    """
    Gestionnaire de graphes de connaissances pour NetGuardian.
    
    Cette classe gère l'interaction avec la base de données Neo4j
    pour stocker et récupérer des connaissances structurées.
    """
    
    def __init__(self):
        """Initialise le gestionnaire de graphes de connaissances."""
        self.uri = settings.NEO4J_URI
        self.username = settings.NEO4J_USERNAME
        self.password = settings.NEO4J_PASSWORD
        self.driver = None
        
        # Initialiser l'embedding pour la recherche sémantique
        try:
            self.embeddings = OpenAIEmbeddings(
                model=settings.DEFAULT_EMBEDDING_MODEL,
                openai_api_key=settings.OPENAI_API_KEY
            )
            self.embedding_enabled = True
        except Exception as e:
            logger.warning(f"Impossible d'initialiser les embeddings: {e}")
            self.embedding_enabled = False
        
        # Connexion à Neo4j
        self._connect()
    
    def _connect(self) -> None:
        """Établit la connexion à Neo4j."""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password)
            )
            logger.info(f"Connecté à Neo4j: {self.uri}")
            
            # Vérifier la connexion
            with self.driver.session() as session:
                result = session.run("RETURN 1 AS test")
                result.single()
        except Exception as e:
            logger.error(f"Erreur de connexion à Neo4j: {e}")
            self.driver = None
    
    def close(self) -> None:
        """Ferme la connexion à Neo4j."""
        if self.driver:
            self.driver.close()
            logger.info("Connexion Neo4j fermée")
    
    def add_entity(self, name: str, entity_type: str, properties: Dict[str, Any] = None) -> Optional[str]:
        """
        Ajoute une entité au graphe de connaissances.
        
        Args:
            name: Nom de l'entité
            entity_type: Type d'entité
            properties: Propriétés additionnelles
            
        Returns:
            ID de l'entité créée ou None en cas d'erreur
        """
        if not self.driver:
            logger.error("Pas de connexion à Neo4j")
            return None
        
        properties = properties or {}
        
        # Générer l'embedding si activé
        if self.embedding_enabled:
            try:
                embedding = self.embeddings.embed_query(name)
                properties["embedding"] = embedding
            except Exception as e:
                logger.warning(f"Erreur lors de la génération de l'embedding: {e}")
        
        # Ajouter l'horodatage
        properties["created_at"] = time.time()
        
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MERGE (e:Entity {name: $name})
                    SET e.type = $type
                    SET e.created_at = $created_at
                    """ + "".join([f"\nSET e.{k} = ${k}" for k in properties.keys()]) + """
                    RETURN id(e) as id
                    """,
                    name=name,
                    type=entity_type,
                    **properties
                )
                record = result.single()
                entity_id = str(record["id"])
                logger.info(f"Entité ajoutée: {name} (ID: {entity_id})")
                return entity_id
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout de l'entité: {e}")
            return None
    
    def add_relation(self, from_entity: str, relation_type: str, to_entity: str, properties: Dict[str, Any] = None) -> Optional[str]:
        """
        Ajoute une relation entre deux entités.
        
        Args:
            from_entity: Nom de l'entité source
            relation_type: Type de relation
            to_entity: Nom de l'entité cible
            properties: Propriétés additionnelles
            
        Returns:
            ID de la relation créée ou None en cas d'erreur
        """
        if not self.driver:
            logger.error("Pas de connexion à Neo4j")
            return None
        
        properties = properties or {}
        properties["created_at"] = time.time()
        
        try:
            with self.driver.session() as session:
                result = session.run(
                    f"""
                    MATCH (from:Entity {{name: $from_name}})
                    MATCH (to:Entity {{name: $to_name}})
                    MERGE (from)-[r:{relation_type}]->(to)
                    """ + "".join([f"\nSET r.{k} = ${k}" for k in properties.keys()]) + """
                    RETURN id(r) as id
                    """,
                    from_name=from_entity,
                    to_name=to_entity,
                    **properties
                )
                record = result.single()
                if record:
                    relation_id = str(record["id"])
                    logger.info(f"Relation ajoutée: {from_entity} -{relation_type}-> {to_entity} (ID: {relation_id})")
                    return relation_id
                else:
                    logger.warning(f"Impossible de créer la relation: entités non trouvées")
                    return None
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout de la relation: {e}")
            return None
    
    def update_with_interaction(self, query: str, response: str, agent_type: str) -> None:
        """
        Met à jour le graphe de connaissances avec une interaction utilisateur.
        
        Args:
            query: Requête de l'utilisateur
            response: Réponse de l'agent
            agent_type: Type d'agent
        """
        if not self.driver:
            logger.warning("Pas de connexion à Neo4j, impossible de mettre à jour le graphe")
            return
        
        # Créer un nœud d'interaction
        interaction_id = f"interaction_{int(time.time())}"
        self.add_entity(
            name=interaction_id,
            entity_type="Interaction",
            properties={
                "query": query,
                "response": response,
                "agent_type": agent_type,
                "timestamp": time.time()
            }
        )
        
        # Extraire les entités de la requête et de la réponse
        query_entities = self._extract_entities(query)
        response_entities = self._extract_entities(response)
        
        # Ajouter les entités et les relations
        for entity, entity_type in query_entities:
            self.add_entity(entity, entity_type)
            self.add_relation(
                from_entity=interaction_id,
                relation_type="MENTIONS",
                to_entity=entity,
                properties={"source": "query"}
            )
        
        for entity, entity_type in response_entities:
            self.add_entity(entity, entity_type)
            self.add_relation(
                from_entity=interaction_id,
                relation_type="MENTIONS",
                to_entity=entity,
                properties={"source": "response"}
            )
    
    def _extract_entities(self, text: str) -> List[Tuple[str, str]]:
        """
        Extrait les entités d'un texte.
        
        Args:
            text: Texte à analyser
            
        Returns:
            Liste de tuples (entité, type)
        """
        # Implémentation simple basée sur des règles
        # Dans un système réel, on utiliserait un modèle NER plus sophistiqué
        
        entities = []
        
        # Extraire les termes potentiellement liés à la cybersécurité
        security_terms = [
            "malware", "virus", "ransomware", "phishing", "hacker", "firewall",
            "VPN", "encryption", "vulnerability", "exploit", "backdoor", "botnet",
            "DDoS", "SQL injection", "XSS", "CSRF", "authentication", "authorization"
        ]
        
        for term in security_terms:
            if re.search(r'\b' + re.escape(term) + r'\b', text, re.IGNORECASE):
                entities.append((term.lower(), "SecurityConcept"))
        
        # Extraire les mots commençant par une majuscule (potentielles entités nommées)
        named_entities = re.findall(r'\b[A-Z][a-zA-Z]+\b', text)
        for entity in named_entities:
            if len(entity) > 1 and entity.lower() not in [e[0] for e in entities]:
                entities.append((entity, "NamedEntity"))
        
        return list(set(entities))  # Éliminer les doublons
    
    def search_entities(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Recherche des entités similaires à une requête.
        
        Args:
            query: Requête de recherche
            limit: Nombre maximum de résultats
            
        Returns:
            Liste d'entités
        """
        if not self.driver:
            logger.error("Pas de connexion à Neo4j")
            return []
        
        if self.embedding_enabled:
            try:
                # Recherche par similarité vectorielle
                query_embedding = self.embeddings.embed_query(query)
                
                with self.driver.session() as session:
                    result = session.run(
                        """
                        MATCH (e:Entity)
                        WHERE e.embedding IS NOT NULL
                        WITH e, gds.similarity.cosine(e.embedding, $embedding) AS score
                        ORDER BY score DESC
                        LIMIT $limit
                        RETURN e.name AS name, e.type AS type, score
                        """,
                        embedding=query_embedding,
                        limit=limit
                    )
                    
                    return [dict(record) for record in result]
            except Exception as e:
                logger.warning(f"Erreur lors de la recherche par embedding: {e}")
                # Continuer avec la recherche par texte
        
        # Recherche par texte
        try:
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (e:Entity)
                    WHERE toLower(e.name) CONTAINS toLower($query_text)
                    RETURN e.name AS name, e.type AS type, 1.0 AS score
                    LIMIT $limit
                    """,
                    query_text=query.lower(),
                    limit=limit
                )
                
                return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Erreur lors de la recherche d'entités: {e}")
            return []
    
    def get_entity_neighborhood(self, entity_name: str, depth: int = 1) -> Dict[str, Any]:
        """
        Récupère le voisinage d'une entité.
        
        Args:
            entity_name: Nom de l'entité
            depth: Profondeur de recherche
            
        Returns:
            Dictionnaire contenant les nœuds et les relations
        """
        if not self.driver:
            logger.error("Pas de connexion à Neo4j")
            return {"nodes": [], "relationships": []}
        
        try:
            with self.driver.session() as session:
                result = session.run(
                    f"""
                    MATCH path = (e:Entity {{name: $name}})-[*1..{depth}]-(related)
                    RETURN path
                    """,
                    name=entity_name
                )
                
                nodes = {}
                relationships = []
                
                for record in result:
                    path = record["path"]
                    
                    # Extraire les nœuds
                    for node in path.nodes:
                        if node.id not in nodes:
                            nodes[node.id] = {
                                "id": node.id,
                                "name": node["name"],
                                "type": node.get("type", "Unknown"),
                                "properties": {k: v for k, v in node.items() if k not in ["name", "type", "embedding"]}
                            }
                    
                    # Extraire les relations
                    for rel in path.relationships:
                        relationships.append({
                            "id": rel.id,
                            "type": rel.type,
                            "source": rel.start_node.id,
                            "target": rel.end_node.id,
                            "properties": {k: v for k, v in rel.items() if k != "embedding"}
                        })
                
                return {
                    "nodes": list(nodes.values()),
                    "relationships": relationships
                }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du voisinage: {e}")
            return {"nodes": [], "relationships": []}
