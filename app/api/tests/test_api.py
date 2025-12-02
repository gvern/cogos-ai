import pytest
from fastapi.testclient import TestClient
import os
import sys
import json
from unittest.mock import patch, MagicMock

# Ajouter le chemin parent pour pouvoir importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import des modules à tester
from ..main import app

# Client de test
client = TestClient(app)

# Tests pour les routes générales
def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "status" in response.json()
    assert response.json()["status"] == "online"

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "api_version" in response.json()

def test_ping_endpoint():
    response = client.get("/ping")
    assert response.status_code == 200
    assert "status" in response.json()
    assert "alive" in response.json()["status"]

# Tests pour l'API mémoire
@patch("core.memory.query_memory")
def test_memory_query(mock_query_memory):
    # Configuration du mock
    mock_query_memory.return_value = "Réponse de test"
    
    # Requête de test
    payload = {"question": "Quelle est la question?"}
    response = client.post("/memory/query", json=payload)
    
    # Vérifications
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["data"]["response"] == "Réponse de test"
    
    # Vérifier que le mock a été appelé correctement
    mock_query_memory.assert_called_once_with("Quelle est la question?")

@patch("core.memory.add_memory_entry")
def test_memory_add(mock_add_memory_entry):
    # Configuration du mock
    mock_add_memory_entry.return_value = True
    
    # Requête de test
    payload = {
        "content": "Nouveau souvenir",
        "tags": ["test", "mémoire"],
        "timestamp": "2023-01-01T12:00:00",
        "source": "test_api"
    }
    response = client.post("/memory/add", json=payload)
    
    # Vérifications
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    
    # Vérifier que le mock a été appelé correctement
    mock_add_memory_entry.assert_called_once()
    args = mock_add_memory_entry.call_args[0]
    assert args[0] == "Nouveau souvenir"
    assert "test" in args[1]
    assert args[2] == "test_api"

# Tests pour l'API contexte
@patch("core.context_loader.get_raw_context")
def test_context_get(mock_get_raw_context):
    # Configuration du mock
    mock_context = {
        "name": "Test User",
        "role": "Développeur",
        "tone": "Professionnel",
        "goals": ["Apprendre Python", "Construire une IA"],
        "focus": ["Machine Learning", "Web Development"],
        "domains": {"tech": 8.5, "art": 3.2}
    }
    mock_get_raw_context.return_value = mock_context
    
    # Requête de test
    response = client.get("/context")
    
    # Vérifications
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["data"] == mock_context
    
    # Vérifier que le mock a été appelé correctement
    mock_get_raw_context.assert_called_once()

@patch("core.context_loader.update_context")
def test_context_update(mock_update_context):
    # Configuration du mock
    mock_update_context.return_value = True
    
    # Requête de test
    payload = {
        "name": "Test User",
        "role": "Développeur",
        "tone": "Professionnel",
        "goals": ["Apprendre Python", "Construire une IA"],
        "focus": ["Machine Learning", "Web Development"],
        "domains": {"tech": 8.5, "art": 3.2}
    }
    response = client.put("/context/update", json=payload)
    
    # Vérifications
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    
    # Vérifier que le mock a été appelé correctement
    mock_update_context.assert_called_once()
    # Vérifier que les données ont été transmises correctement
    args = mock_update_context.call_args[0]
    assert args[0]["name"] == "Test User"
    assert "Apprendre Python" in args[0]["goals"]

# Tests pour l'API agent
@patch("core.agent.get_actions_for_display")
def test_agent_get_actions(mock_get_actions):
    # Configuration du mock pour simuler des actions
    class MockAction:
        def __init__(self, id, title, completed=False):
            self.id = id
            self.title = title
            self.description = "Description test"
            self.action_type = "apprentissage"
            self.priority = 3
            self.deadline = None
            self.created_at = "2023-01-01T12:00:00"
            self.completed = completed
    
    mock_actions = [
        MockAction("1", "Action 1"),
        MockAction("2", "Action 2", True)
    ]
    
    mock_get_actions.return_value = mock_actions
    
    # Requête de test
    response = client.get("/agent/actions?include_completed=true")
    
    # Vérifications
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert len(response.json()["data"]["actions"]) == 2
    
    # Vérifier que le mock a été appelé correctement
    mock_get_actions.assert_called_once_with(True) 