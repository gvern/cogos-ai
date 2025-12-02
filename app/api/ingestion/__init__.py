"""
CogOS Knowledge Ingestion System
================================

Infrastructure complète pour la collecte, traitement et intégration 
de toutes les sources de connaissances personnelles.

Modules:
- collectors: Collecteurs spécialisés par type de source
- processors: Traitement intelligent et enrichissement
- quality_control: Validation et contrôle qualité
- storage: Stockage et indexation des connaissances
"""

__version__ = "1.0.0"

from .ingestion_coordinator import IngestionCoordinator, run_knowledge_ingestion
from .collectors.file_system_crawler import FileSystemCollector
from .collectors.digital_library_collector import DigitalLibraryCollector
from .collectors.cloud_drive_collector import CloudDriveCollector
from .collectors.application_data_collector import ApplicationDataCollector
from .processors.content_processor import ContentProcessor
from .quality_control.quality_controller import QualityController
from .storage.storage_manager import StorageManager

__all__ = [
    'IngestionCoordinator',
    'run_knowledge_ingestion',
    'FileSystemCollector',
    'DigitalLibraryCollector', 
    'CloudDriveCollector',
    'ApplicationDataCollector',
    'ContentProcessor',
    'QualityController',
    'StorageManager'
]

__author__ = "CogOS Team"

# Configuration globale de l'ingestion
INGESTION_CONFIG = {
    "base_path": "/Users/gustavevernay",
    "supported_extensions": {
        'documents': ['.pdf', '.docx', '.txt', '.md', '.rtf'],
        'presentations': ['.pptx', '.key', '.odp'],
        'spreadsheets': ['.xlsx', '.csv', '.numbers'],
        'code': ['.py', '.js', '.ts', '.html', '.css', '.json'],
        'images': ['.jpg', '.png', '.gif', '.tiff', '.heic'],
        'audio': ['.mp3', '.m4a', '.wav', '.aac'],
        'video': ['.mp4', '.mov', '.avi', '.mkv']
    },
    "cloud_services": {
        "google_drive": True,
        "dropbox": False,  # À activer si utilisé
        "icloud": True,
        "onedrive": False
    },
    "digital_libraries": {
        "google_books": True,
        "openlibrary": True,
        "gallica": True,
        "gutenberg": True,
        "jstor": False,  # Nécessite accès institutionnel
        "cairn": False   # Nécessite abonnement
    },
    "quality_thresholds": {
        "ocr_accuracy": 0.95,
        "classification_accuracy": 0.90,
        "duplicate_detection": 0.99,
        "metadata_completeness": 0.90
    },
    "processing": {
        "batch_size": 100,
        "max_file_size_mb": 500,
        "ocr_languages": ["fra", "eng"],
        "embedding_model": "text-embedding-3-large",
        "llm_model": "gpt-4-turbo"
    }
}
