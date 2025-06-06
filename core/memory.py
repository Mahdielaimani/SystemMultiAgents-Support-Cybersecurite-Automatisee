"""
Module de gestion de la mémoire pour NextGen-Agent.
"""
from typing import Dict, List, Any, Optional
import os
import json
from datetime import datetime
from pathlib import Path

class ConversationMemory:
    """
    Gestionnaire de mémoire conversationnelle.
    """
    
    def __init__(self, session_id: str = None):
        """Initialise la mémoire conversationnelle."""
        self.session_id = session_id or "default"
        self.memory_dir = Path("./data/memory")
        self.memory_dir.mkdir(exist_ok=True, parents=True)
        self.messages = []
        self.load_session()
    
    def load_session(self):
        """Charge la session existante."""
        session_file = self.memory_dir / f"{self.session_id}.json"
        if session_file.exists():
            try:
                with open(session_file, "r") as f:
                    data = json.load(f)
                    self.messages = data.get("messages", [])
            except Exception as e:
                print(f"Erreur lors du chargement: {e}")
                self.messages = []
    
    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Ajoute un message à la mémoire."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.messages.append(message)
        self.save_session()
    
    def get_formatted_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Récupère l'historique formaté."""
        return self.messages[-limit:] if limit else self.messages
    
    def save_session(self):
        """Sauvegarde la session."""
        session_file = self.memory_dir / f"{self.session_id}.json"
        data = {
            "session_id": self.session_id,
            "messages": self.messages,
            "last_updated": datetime.now().isoformat()
        }
        with open(session_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def clear(self):
        """Efface la mémoire."""
        self.messages = []
        self.save_session()

class MemoryManager:
    """
    Gestionnaire de mémoire pour les conversations et données des agents.
    Version simplifiée pour le démarrage initial.
    """
    
    def __init__(self):
        """Initialise le gestionnaire de mémoire."""
        self.memory_dir = Path("./data/memory")
        self.memory_dir.mkdir(exist_ok=True, parents=True)
        self.sessions = {}
        self.load_sessions()
    
    def load_sessions(self):
        """Charge les sessions existantes."""
        for session_file in self.memory_dir.glob("*.json"):
            try:
                with open(session_file, "r") as f:
                    session_data = json.load(f)
                    session_id = session_file.stem
                    self.sessions[session_id] = session_data
            except Exception as e:
                print(f"Erreur lors du chargement de la session {session_file}: {e}")
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Récupère une session par son ID.
        
        Args:
            session_id: ID de la session
            
        Returns:
            Données de la session
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "messages": [],
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat()
                }
            }
        return self.sessions[session_id]
    
    def add_message(self, session_id: str, message: Dict[str, Any]):
        """
        Ajoute un message à une session.
        
        Args:
            session_id: ID de la session
            message: Message à ajouter
        """
        session = self.get_session(session_id)
        message["timestamp"] = datetime.now().isoformat()
        session["messages"].append(message)
        session["metadata"]["last_updated"] = datetime.now().isoformat()
        self.save_session(session_id)
    
    def save_session(self, session_id: str):
        """
        Sauvegarde une session.
        
        Args:
            session_id: ID de la session
        """
        session_file = self.memory_dir / f"{session_id}.json"
        with open(session_file, "w") as f:
            json.dump(self.sessions[session_id], f, indent=2)
    
    def get_messages(self, session_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Récupère les messages d'une session.
        
        Args:
            session_id: ID de la session
            limit: Nombre maximum de messages à récupérer
            
        Returns:
            Liste des messages
        """
        session = self.get_session(session_id)
        messages = session["messages"]
        if limit:
            return messages[-limit:]
        return messages
    
    def clear_session(self, session_id: str):
        """
        Efface une session.
        
        Args:
            session_id: ID de la session
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            session_file = self.memory_dir / f"{session_id}.json"
            if session_file.exists():
                session_file.unlink()


class ConversationMemory:
    """
    Classe de mémoire conversationnelle pour les agents.
    """
    
    def __init__(self):
        self.memory_manager = MemoryManager()
    
    def get_formatted_history(self, session_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Récupère l'historique formaté d'une session.
        
        Args:
            session_id: ID de la session
            limit: Nombre maximum de messages
            
        Returns:
            Liste des messages formatés
        """
        messages = self.memory_manager.get_messages(session_id, limit)
        formatted = []
        
        for msg in messages:
            formatted.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", ""),
                "timestamp": msg.get("timestamp", "")
            })
        
        return formatted
    
    def add_message(self, session_id: str, role: str, content: str, metadata: Dict[str, Any] = None):
        """
        Ajoute un message à la mémoire.
        
        Args:
            session_id: ID de la session
            role: Rôle (user, assistant, system)
            content: Contenu du message
            metadata: Métadonnées additionnelles
        """
        message = {
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }
        self.memory_manager.add_message(session_id, message)
