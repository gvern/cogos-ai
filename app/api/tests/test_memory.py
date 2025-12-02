import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from datetime import datetime

# Ajouter le chemin parent pour pouvoir importer les modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import des modules à tester
from ...core.memory import query_memory, add_memory_entry, get_recent_entries

# Tests pour query_memory
@pytest.mark.parametrize("query,expected", [
    ("test query", True),  # Teste si une requête de base retourne une réponse
])
@patch("core.memory.get_collection")
@patch("core.memory.EMBEDDING_MODEL.encode")
@patch("core.memory.client.chat.completions.create")
def test_query_memory_success(mock_chat_create, mock_encode, mock_get_collection, query, expected):
    # Configurer les mocks
    mock_collection = MagicMock()
    mock_get_collection.return_value = mock_collection
    
    mock_encode.return_value = [0.1, 0.2, 0.3]
    
    mock_collection.query.return_value = {
        "documents": [["Document 1", "Document 2"]]
    }
    
    mock_chat_response = MagicMock()
    mock_chat_response.choices = [MagicMock()]
    mock_chat_response.choices[0].message.content = "Réponse test"
    mock_chat_create.return_value = mock_chat_response
    
    # Appeler la fonction
    result = query_memory(query)
    
    # Vérifier le résultat
    assert isinstance(result, str)
    assert result == "Réponse test"
    
    # Vérifier que les mocks ont été appelés correctement
    mock_get_collection.assert_called_once()
    mock_encode.assert_called_once_with(query)
    mock_collection.query.assert_called_once()
    mock_chat_create.assert_called_once()

@patch("core.memory.get_collection")
def test_query_memory_empty_results(mock_get_collection):
    # Configurer les mocks pour simuler aucun résultat
    mock_collection = MagicMock()
    mock_get_collection.return_value = mock_collection
    
    mock_collection.query.return_value = {
        "documents": [[]]  # Aucun document trouvé
    }
    
    # Appeler la fonction
    result = query_memory("query test")
    
    # Vérifier le résultat
    assert "Aucun souvenir trouvé" in result

# Tests pour add_memory_entry
@patch("core.memory.get_collection")
@patch("core.memory.EMBEDDING_MODEL.encode")
@patch("uuid.uuid4")
def test_add_memory_entry(mock_uuid, mock_encode, mock_get_collection):
    # Configurer les mocks
    mock_collection = MagicMock()
    mock_get_collection.return_value = mock_collection
    
    mock_encode.return_value = [0.1, 0.2, 0.3]
    mock_uuid.return_value = "test-uuid"
    
    # Appeler la fonction
    result = add_memory_entry("Test content", ["tag1", "tag2"], "test_source")
    
    # Vérifier le résultat
    assert result is True
    
    # Vérifier que les mocks ont été appelés correctement
    mock_get_collection.assert_called_once()
    mock_encode.assert_called_once_with("Test content")
    mock_collection.add.assert_called_once()
    
    # Vérifier les arguments du add
    add_args = mock_collection.add.call_args[1]
    assert add_args["ids"] == ["test-uuid"]
    assert add_args["documents"] == ["Test content"]
    assert "tag1,tag2" in str(add_args["metadatas"])
    assert "test_source" in str(add_args["metadatas"])

# Tests pour get_recent_entries
@patch("core.memory.get_collection")
def test_get_recent_entries(mock_get_collection):
    # Configurer les mocks
    mock_collection = MagicMock()
    mock_get_collection.return_value = mock_collection
    
    # Simuler des résultats de la collection
    now = datetime.now().isoformat()
    earlier = datetime.now().replace(hour=10).isoformat()
    
    mock_collection.get.return_value = {
        "documents": ["Doc 1", "Doc 2"],
        "metadatas": [
            {"timestamp": now, "source": "source1", "tags": "tag1,tag2"},
            {"timestamp": earlier, "source": "source2", "tags": "tag3"},
        ],
        "ids": ["id1", "id2"]
    }
    
    # Appeler la fonction
    result = get_recent_entries(limit=2)
    
    # Vérifier le résultat
    assert len(result) == 2
    assert result[0]["content"] == "Doc 1"  # Le plus récent d'abord
    assert result[0]["timestamp"] == now
    assert "tag1" in result[0]["tags"]
    assert result[0]["embedding_id"] == "id1"
    
    # Vérifier avec une limite
    result_limited = get_recent_entries(limit=1)
    assert len(result_limited) == 1 