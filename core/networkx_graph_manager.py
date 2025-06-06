"""
Gestionnaire de graphes de connaissances avec NetworkX pour NetGuardian.
Alternative à Neo4j - plus simple et sans serveur externe.
"""
import time
import json
import pickle
import os
from typing import Dict, List, Optional, Any, Set, Tuple
from pathlib import Path
import networkx as nx
from dataclasses import dataclass, asdict
from datetime import datetime

from config.logging_config import get_logger

logger = get_logger("networkx_graph_manager")

@dataclass
class GraphEntity:
    """Entité du graphe de connaissances"""
    id: str
    name: str
    entity_type: str
    properties: Dict[str, Any]
    created_at: float
    updated_at: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class GraphRelation:
    """Relation du graphe de connaissances"""
    id: str
    source: str
    target: str
    relation_type: str
    properties: Dict[str, Any]
    created_at: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class NetworkXGraphManager:
    """
    Gestionnaire de graphes de connaissances avec NetworkX.
    
    Cette classe gère un graphe de connaissances en mémoire avec
    persistance sur disque, sans nécessiter de serveur externe.
    """
    
    def __init__(self, graph_file: str = "./data/graph_db/knowledge_graph.pkl"):
        """Initialise le gestionnaire de graphes NetworkX."""
        self.graph_file = Path(graph_file)
        self.graph = nx.MultiDiGraph()  # Graphe dirigé avec arêtes multiples
        self.entities: Dict[str, GraphEntity] = {}
        self.relations: Dict[str, GraphRelation] = {}
        
        # Créer le dossier si nécessaire
        self.graph_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Charger le graphe existant
        self._load_graph()
        
        logger.info(f"NetworkX Graph Manager initialisé - {len(self.entities)} entités, {len(self.relations)} relations")
    
    def _load_graph(self) -> None:
        """Charge le graphe depuis le disque."""
        try:
            if self.graph_file.exists():
                with open(self.graph_file, 'rb') as f:
                    data = pickle.load(f)
                    self.graph = data.get('graph', nx.MultiDiGraph())
                    self.entities = data.get('entities', {})
                    self.relations = data.get('relations', {})
                logger.info(f"Graphe chargé depuis {self.graph_file}")
            else:
                logger.info("Nouveau graphe créé")
        except Exception as e:
            logger.error(f"Erreur lors du chargement du graphe: {e}")
            self.graph = nx.MultiDiGraph()
            self.entities = {}
            self.relations = {}
    
    def _save_graph(self) -> None:
        """Sauvegarde le graphe sur disque."""
        try:
            data = {
                'graph': self.graph,
                'entities': self.entities,
                'relations': self.relations,
                'saved_at': time.time()
            }
            with open(self.graph_file, 'wb') as f:
                pickle.dump(data, f)
            logger.debug(f"Graphe sauvegardé dans {self.graph_file}")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du graphe: {e}")
    
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
        try:
            properties = properties or {}
            entity_id = f"{entity_type}_{name}".replace(" ", "_").lower()
            
            # Créer l'entité
            entity = GraphEntity(
                id=entity_id,
                name=name,
                entity_type=entity_type,
                properties=properties,
                created_at=time.time(),
                updated_at=time.time()
            )
            
            # Ajouter au graphe NetworkX
            self.graph.add_node(entity_id, **entity.to_dict())
            
            # Stocker l'entité
            self.entities[entity_id] = entity
            
            # Sauvegarder
            self._save_graph()
            
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
        try:
            properties = properties or {}
            
            # Trouver les IDs des entités
            from_id = self._find_entity_id(from_entity)
            to_id = self._find_entity_id(to_entity)
            
            if not from_id or not to_id:
                logger.warning(f"Entités non trouvées: {from_entity} -> {to_entity}")
                return None
            
            # Créer l'ID de la relation
            relation_id = f"{from_id}_{relation_type}_{to_id}_{int(time.time())}"
            
            # Créer la relation
            relation = GraphRelation(
                id=relation_id,
                source=from_id,
                target=to_id,
                relation_type=relation_type,
                properties=properties,
                created_at=time.time()
            )
            
            # Ajouter au graphe NetworkX
            self.graph.add_edge(from_id, to_id, key=relation_id, **relation.to_dict())
            
            # Stocker la relation
            self.relations[relation_id] = relation
            
            # Sauvegarder
            self._save_graph()
            
            logger.info(f"Relation ajoutée: {from_entity} -{relation_type}-> {to_entity}")
            return relation_id
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout de la relation: {e}")
            return None
    
    def _find_entity_id(self, entity_name: str) -> Optional[str]:
        """Trouve l'ID d'une entité par son nom."""
        for entity_id, entity in self.entities.items():
            if entity.name.lower() == entity_name.lower():
                return entity_id
        return None
    
    def search_entities(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Recherche des entités similaires à une requête.
        
        Args:
            query: Requête de recherche
            limit: Nombre maximum de résultats
            
        Returns:
            Liste d'entités
        """
        try:
            query_lower = query.lower()
            results = []
            
            for entity in self.entities.values():
                score = 0.0
                
                # Score basé sur le nom
                if query_lower in entity.name.lower():
                    score += 1.0
                
                # Score basé sur le type
                if query_lower in entity.entity_type.lower():
                    score += 0.5
                
                # Score basé sur les propriétés
                for key, value in entity.properties.items():
                    if isinstance(value, str) and query_lower in value.lower():
                        score += 0.3
                
                if score > 0:
                    results.append({
                        'name': entity.name,
                        'type': entity.entity_type,
                        'score': score,
                        'id': entity.id
                    })
            
            # Trier par score et limiter
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:limit]
            
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
        try:
            entity_id = self._find_entity_id(entity_name)
            if not entity_id:
                return {"nodes": [], "relationships": []}
            
            # Utiliser NetworkX pour trouver le voisinage
            subgraph_nodes = set([entity_id])
            
            # Ajouter les voisins à la profondeur spécifiée
            for d in range(depth):
                new_nodes = set()
                for node in subgraph_nodes:
                    # Voisins sortants
                    new_nodes.update(self.graph.successors(node))
                    # Voisins entrants
                    new_nodes.update(self.graph.predecessors(node))
                subgraph_nodes.update(new_nodes)
            
            # Créer le sous-graphe
            subgraph = self.graph.subgraph(subgraph_nodes)
            
            # Extraire les nœuds
            nodes = []
            for node_id in subgraph.nodes():
                if node_id in self.entities:
                    entity = self.entities[node_id]
                    nodes.append({
                        "id": entity.id,
                        "name": entity.name,
                        "type": entity.entity_type,
                        "properties": entity.properties
                    })
            
            # Extraire les relations
            relationships = []
            for source, target, key, data in subgraph.edges(keys=True, data=True):
                if key in self.relations:
                    relation = self.relations[key]
                    relationships.append({
                        "id": relation.id,
                        "type": relation.relation_type,
                        "source": relation.source,
                        "target": relation.target,
                        "properties": relation.properties
                    })
            
            return {
                "nodes": nodes,
                "relationships": relationships
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du voisinage: {e}")
            return {"nodes": [], "relationships": []}
    
    def get_entity_relations(self, entity_name: str) -> List[str]:
        """
        Récupère les relations d'une entité sous forme de texte.
        
        Args:
            entity_name: Nom de l'entité
            
        Returns:
            Liste de descriptions de relations
        """
        try:
            entity_id = self._find_entity_id(entity_name)
            if not entity_id:
                return []
            
            relations_text = []
            
            # Relations sortantes
            for target in self.graph.successors(entity_id):
                for key in self.graph[entity_id][target]:
                    if key in self.relations:
                        relation = self.relations[key]
                        target_entity = self.entities.get(target)
                        if target_entity:
                            relations_text.append(
                                f"{entity_name} {relation.relation_type} {target_entity.name}"
                            )
            
            # Relations entrantes
            for source in self.graph.predecessors(entity_id):
                for key in self.graph[source][entity_id]:
                    if key in self.relations:
                        relation = self.relations[key]
                        source_entity = self.entities.get(source)
                        if source_entity:
                            relations_text.append(
                                f"{source_entity.name} {relation.relation_type} {entity_name}"
                            )
            
            return relations_text
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des relations: {e}")
            return []
    
    def update_with_interaction(self, query: str, response: str, agent_type: str) -> None:
        """
        Met à jour le graphe de connaissances avec une interaction utilisateur.
        
        Args:
            query: Requête de l'utilisateur
            response: Réponse de l'agent
            agent_type: Type d'agent
        """
        try:
            # Créer un nœud d'interaction
            interaction_name = f"interaction_{int(time.time())}"
            self.add_entity(
                name=interaction_name,
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
                    from_entity=interaction_name,
                    relation_type="MENTIONS",
                    to_entity=entity,
                    properties={"source": "query"}
                )
            
            for entity, entity_type in response_entities:
                self.add_entity(entity, entity_type)
                self.add_relation(
                    from_entity=interaction_name,
                    relation_type="MENTIONS",
                    to_entity=entity,
                    properties={"source": "response"}
                )
                
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour avec interaction: {e}")
    
    def _extract_entities(self, text: str) -> List[Tuple[str, str]]:
        """
        Extrait les entités d'un texte.
        
        Args:
            text: Texte à analyser
            
        Returns:
            Liste de tuples (entité, type)
        """
        entities = []
        text_lower = text.lower()
        
        # Entités TeamSquare spécifiques
        teamsquare_entities = {
            'teamsquare': 'Platform',
            'plan starter': 'PricingPlan',
            'plan professional': 'PricingPlan', 
            'plan enterprise': 'PricingPlan',
            'api': 'Feature',
            'chat': 'Feature',
            'projets': 'Feature',
            'fichiers': 'Feature',
            'support': 'Service',
            'intégration': 'Feature'
        }
        
        for entity_name, entity_type in teamsquare_entities.items():
            if entity_name in text_lower:
                entities.append((entity_name, entity_type))
        
        return list(set(entities))  # Éliminer les doublons
    
    def get_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques du graphe."""
        return {
            'entities_count': len(self.entities),
            'relations_count': len(self.relations),
            'nodes_count': self.graph.number_of_nodes(),
            'edges_count': self.graph.number_of_edges(),
            'entity_types': list(set(e.entity_type for e in self.entities.values())),
            'relation_types': list(set(r.relation_type for r in self.relations.values())),
            'graph_file': str(self.graph_file),
            'is_connected': nx.is_weakly_connected(self.graph) if self.graph.number_of_nodes() > 0 else False
        }
    
    def export_to_json(self, output_file: str) -> bool:
        """Exporte le graphe au format JSON."""
        try:
            data = {
                'entities': [entity.to_dict() for entity in self.entities.values()],
                'relations': [relation.to_dict() for relation in self.relations.values()],
                'stats': self.get_stats(),
                'exported_at': time.time()
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Graphe exporté vers {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'export: {e}")
            return False
    
    def close(self) -> None:
        """Ferme le gestionnaire et sauvegarde."""
        self._save_graph()
        logger.info("NetworkX Graph Manager fermé")
