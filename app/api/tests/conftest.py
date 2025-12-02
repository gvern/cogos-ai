import pytest
import os
import sys
from unittest.mock import MagicMock

# Ajouter le chemin parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration des fixtures pour les tests
@pytest.fixture
def mock_collection():
    """Mock pour la collection ChromaDB"""
    collection = MagicMock()
    collection.query.return_value = {
        "documents": [["Document de test 1", "Document de test 2"]],
        "distances": [[0.1, 0.2]]
    }
    return collection

@pytest.fixture
def mock_context():
    """Données de contexte simulées pour les tests"""
    return {
        "name": "Utilisateur Test",
        "role": "Développeur Python",
        "tone": "Professionnel",
        "goals": [
            "Apprendre le deep learning",
            "Construire une API REST",
            "Maîtriser FastAPI"
        ],
        "focus": [
            "Python",
            "Machine Learning",
            "Web Development"
        ],
        "domains": {
            "tech": 8.5,
            "science": 7.2,
            "art": 4.3,
            "histoire": 5.1,
            "économie": 6.7
        },
        "memory": {
            "short_term": ["FastAPI", "Next.js", "React"],
            "long_term": ["Python", "IA"]
        }
    }

@pytest.fixture
def mock_memory_entries():
    """Entrées de mémoire simulées pour les tests"""
    return [
        {
            "content": "FastAPI est un framework web moderne pour Python.",
            "timestamp": "2023-01-01T12:00:00",
            "tags": ["python", "web", "fastapi"],
            "source": "documentation",
            "embedding_id": "123"
        },
        {
            "content": "Next.js est un framework React pour la production.",
            "timestamp": "2023-01-02T14:30:00",
            "tags": ["javascript", "react", "nextjs"],
            "source": "article",
            "embedding_id": "456"
        }
    ]

@pytest.fixture
def mock_agent_actions():
    """Actions d'agent simulées pour les tests"""
    class MockAction:
        def __init__(self, id, title, action_type, priority=3, completed=False):
            self.id = id
            self.title = title
            self.description = f"Description pour {title}"
            self.action_type = action_type
            self.priority = priority
            self.deadline = "2023-12-31"
            self.created_at = "2023-01-01T12:00:00"
            self.completed = completed
            
        def __dict__(self):
            return {
                "id": self.id,
                "title": self.title,
                "description": self.description,
                "action_type": self.action_type,
                "priority": self.priority,
                "deadline": self.deadline,
                "created_at": self.created_at,
                "completed": self.completed
            }
    
    return [
        MockAction("1", "Apprendre FastAPI", "apprentissage", 4),
        MockAction("2", "Créer une API REST", "défi", 5),
        MockAction("3", "Réviser Python asyncio", "consolidation", 3),
        MockAction("4", "Finir le cours React", "apprentissage", 2, True)
    ] 