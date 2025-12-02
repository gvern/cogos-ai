"""
File System Crawler
==================

Collecteur principal pour scanner récursivement le système de fichiers
et extraire tous les documents personnels avec métadonnées complètes.
"""

import os
import hashlib
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Generator
import logging
from dataclasses import dataclass

# Configuration logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FileMetadata:
    """Métadonnées complètes d'un fichier"""
    path: str
    name: str
    extension: str
    size_bytes: int
    created_at: datetime
    modified_at: datetime
    accessed_at: datetime
    mime_type: str
    hash_sha256: str
    category: str
    priority_score: float


class FileSystemCollector:
    """Collecteur système de fichiers avec priorisation intelligente"""
    
    def __init__(self, base_path: str = "/Users/gustavevernay"):
        self.base_path = Path(base_path)
        self.priority_extensions = {
            'documents': ['.pdf', '.docx', '.txt', '.md', '.rtf', '.pages'],
            'presentations': ['.pptx', '.key', '.odp'],
            'spreadsheets': ['.xlsx', '.csv', '.numbers'],
            'code': ['.py', '.js', '.ts', '.html', '.css', '.json', '.yaml'],
            'images': ['.jpg', '.png', '.gif', '.tiff', '.heic', '.svg'],
            'audio': ['.mp3', '.m4a', '.wav', '.aac', '.flac'],
            'video': ['.mp4', '.mov', '.avi', '.mkv', '.webm']
        }
        
        # Dossiers à exclure du scan
        self.excluded_dirs = {
            '.git', '.venv', '__pycache__', 'node_modules', '.cache',
            'Library/Caches', 'Library/Logs', '.Trash', '.npm'
        }
        
        # Stats de collecte
        self.stats = {
            'files_scanned': 0,
            'files_processed': 0,
            'total_size_mb': 0,
            'errors': 0
        }
    
    def scan_and_prioritize(self) -> Generator[FileMetadata, None, None]:
        """
        Scanner récursif avec priorisation par importance
        
        Yields:
            FileMetadata: Métadonnées de chaque fichier trouvé
        """
        logger.info(f"🔍 Début du scan récursif depuis {self.base_path}")
        
        for file_path in self._walk_filesystem():
            try:
                metadata = self._extract_file_metadata(file_path)
                if metadata and self._is_relevant_file(metadata):
                    self.stats['files_processed'] += 1
                    self.stats['total_size_mb'] += metadata.size_bytes / (1024 * 1024)
                    yield metadata
                    
                self.stats['files_scanned'] += 1
                
                # Log de progression tous les 1000 fichiers
                if self.stats['files_scanned'] % 1000 == 0:
                    logger.info(f"📊 Progression: {self.stats['files_scanned']} fichiers scannés, "
                              f"{self.stats['files_processed']} retenus")
                    
            except Exception as e:
                logger.error(f"❌ Erreur processing {file_path}: {e}")
                self.stats['errors'] += 1
                continue
    
    def _walk_filesystem(self) -> Generator[Path, None, None]:
        """Parcours récursif du système de fichiers"""
        for root, dirs, files in os.walk(self.base_path):
            # Exclure les dossiers système
            dirs[:] = [d for d in dirs if d not in self.excluded_dirs]
            
            for file in files:
                file_path = Path(root) / file
                
                # Ignorer les fichiers système et cachés
                if not file.startswith('.') and file_path.stat().st_size > 0:
                    yield file_path
    
    def _extract_file_metadata(self, file_path: Path) -> Optional[FileMetadata]:
        """Extraction métadonnées complètes d'un fichier"""
        try:
            stat = file_path.stat()
            
            # Calcul hash pour détection doublons
            file_hash = self._calculate_file_hash(file_path)
            
            # Détection type MIME
            mime_type, _ = mimetypes.guess_type(str(file_path))
            
            # Catégorisation
            category = self._categorize_file(file_path.suffix.lower())
            
            # Score de priorité basé sur extension, taille, date
            priority_score = self._calculate_priority_score(file_path, stat)
            
            return FileMetadata(
                path=str(file_path),
                name=file_path.name,
                extension=file_path.suffix.lower(),
                size_bytes=stat.st_size,
                created_at=datetime.fromtimestamp(stat.st_ctime),
                modified_at=datetime.fromtimestamp(stat.st_mtime),
                accessed_at=datetime.fromtimestamp(stat.st_atime),
                mime_type=mime_type or 'application/octet-stream',
                hash_sha256=file_hash,
                category=category,
                priority_score=priority_score
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur métadonnées {file_path}: {e}")
            return None
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calcul SHA256 pour détection doublons"""
        try:
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                # Lecture par chunks pour gros fichiers
                for chunk in iter(lambda: f.read(8192), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return ""
    
    def _categorize_file(self, extension: str) -> str:
        """Catégorisation par extension"""
        for category, extensions in self.priority_extensions.items():
            if extension in extensions:
                return category
        return 'other'
    
    def _calculate_priority_score(self, file_path: Path, stat) -> float:
        """
        Calcul score de priorité (0.0 à 1.0)
        Facteurs: extension, taille, récence, localisation
        """
        score = 0.0
        
        # Bonus par catégorie (documents = plus important)
        category_scores = {
            'documents': 0.4,
            'code': 0.3,
            'presentations': 0.25,
            'spreadsheets': 0.2,
            'images': 0.1,
            'audio': 0.05,
            'video': 0.05
        }
        category = self._categorize_file(file_path.suffix.lower())
        score += category_scores.get(category, 0.0)
        
        # Bonus récence (fichiers modifiés récemment)
        days_since_modified = (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).days
        if days_since_modified < 30:
            score += 0.3
        elif days_since_modified < 365:
            score += 0.2
        elif days_since_modified < 365 * 3:
            score += 0.1
        
        # Bonus taille (ni trop petit ni trop gros)
        size_mb = stat.st_size / (1024 * 1024)
        if 0.1 < size_mb < 50:  # Taille optimale
            score += 0.2
        elif size_mb > 100:  # Très gros fichiers moins prioritaires
            score -= 0.1
        
        # Bonus localisation (Desktop, Documents = plus important)
        important_dirs = ['Desktop', 'Documents', 'Projets', 'Projects']
        if any(dir_name in str(file_path) for dir_name in important_dirs):
            score += 0.1
        
        return min(1.0, max(0.0, score))
    
    def _is_relevant_file(self, metadata: FileMetadata) -> bool:
        """Filtrage des fichiers pertinents"""
        # Ignorer les très petits fichiers
        if metadata.size_bytes < 100:
            return False
        
        # Ignorer les fichiers système
        if metadata.name.startswith('.') or metadata.name.startswith('~'):
            return False
        
        # Garder seulement les catégories pertinentes
        if metadata.category == 'other':
            return False
        
        return True
    
    def get_scan_statistics(self) -> Dict:
        """Statistiques du scan"""
        return {
            **self.stats,
            'total_size_gb': round(self.stats['total_size_mb'] / 1024, 2),
            'error_rate': self.stats['errors'] / max(1, self.stats['files_scanned']),
            'processing_rate': self.stats['files_processed'] / max(1, self.stats['files_scanned'])
        }


def main():
    """Test du collecteur système de fichiers"""
    collector = FileSystemCollector()
    
    # Limitation pour test (premiers 100 fichiers)
    count = 0
    for metadata in collector.scan_and_prioritize():
        print(f"📄 {metadata.name} ({metadata.category}) - Score: {metadata.priority_score:.2f}")
        count += 1
        if count >= 100:  # Limitation pour test
            break
    
    print(f"\n📊 Statistiques: {collector.get_scan_statistics()}")


if __name__ == "__main__":
    main()
