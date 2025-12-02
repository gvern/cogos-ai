"""
Digital Library Collector
=========================

Collecteur pour récupérer le contenu des livres depuis les bibliothèques
numériques légales plutôt que de scanner physiquement.
"""

import requests
import json
import time
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
import logging
from pathlib import Path
import re
import cv2
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)

@dataclass
class BookIdentification:
    """Identification d'un livre depuis photo"""
    title: str
    author: str
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    year: Optional[int] = None
    confidence: float = 0.0

@dataclass
class DigitalBookContent:
    """Contenu numérique d'un livre"""
    isbn: str
    title: str
    author: str
    description: str
    categories: List[str]
    page_count: int
    language: str
    published_date: str
    thumbnail_url: str
    preview_url: Optional[str]
    full_text_available: bool
    legal_excerpts: List[str]
    metadata: Dict


class DigitalLibraryCollector:
    """Collecteur de bibliothèques numériques"""
    
    def __init__(self):
        self.apis = {
            'google_books': 'https://www.googleapis.com/books/v1/volumes',
            'openlibrary': 'https://openlibrary.org/api/books',
            'gallica': 'https://gallica.bnf.fr/api/sru',
            'gutenberg': 'https://www.gutenberg.org/ebooks/search/'
        }
        
        # Cache pour éviter les requêtes répétées
        self.cache = {}
        
        # Statistiques
        self.stats = {
            'books_identified': 0,
            'digital_versions_found': 0,
            'excerpts_extracted': 0,
            'api_calls': 0
        }
    
    def identify_books_from_photos(self, library_photos_dir: str) -> List[BookIdentification]:
        """
        Identification des livres depuis photos des bibliothèques
        
        Args:
            library_photos_dir: Dossier contenant les photos des bibliothèques
            
        Returns:
            Liste des livres identifiés
        """
        logger.info(f"📚 Identification livres depuis photos dans {library_photos_dir}")
        
        identified_books = []
        photos_dir = Path(library_photos_dir)
        
        if not photos_dir.exists():
            logger.warning(f"❌ Dossier photos introuvable: {library_photos_dir}")
            return identified_books
        
        for photo_path in photos_dir.glob("*.{jpg,jpeg,png,heic}"):
            try:
                books_in_photo = self._extract_books_from_photo(photo_path)
                identified_books.extend(books_in_photo)
                logger.info(f"📖 {len(books_in_photo)} livres identifiés dans {photo_path.name}")
                
            except Exception as e:
                logger.error(f"❌ Erreur traitement photo {photo_path}: {e}")
                continue
        
        logger.info(f"✅ Total: {len(identified_books)} livres identifiés")
        self.stats['books_identified'] = len(identified_books)
        return identified_books
    
    def _extract_books_from_photo(self, photo_path: Path) -> List[BookIdentification]:
        """Extraction OCR des titres depuis une photo de bibliothèque"""
        try:
            # Chargement et préprocessing de l'image
            image = cv2.imread(str(photo_path))
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Amélioration contraste pour OCR
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            
            # OCR avec Tesseract
            custom_config = r'--oem 3 --psm 6 -l fra+eng'
            text = pytesseract.image_to_string(enhanced, config=custom_config)
            
            # Extraction des titres potentiels
            books = self._parse_book_titles_from_text(text)
            return books
            
        except Exception as e:
            logger.error(f"❌ Erreur OCR photo {photo_path}: {e}")
            return []
    
    def _parse_book_titles_from_text(self, ocr_text: str) -> List[BookIdentification]:
        """Parse le texte OCR pour extraire les titres de livres"""
        books = []
        lines = ocr_text.split('\n')
        
        # Patterns pour identifier titres et auteurs
        title_patterns = [
            r'^[A-Z][A-Za-z\s\-\'\"]{10,}$',  # Titres en majuscules
            r'^[A-Z][a-z\s\-\'\"]{5,}[A-Z][a-z\s\-\'\"]{5,}$'  # Titre + Auteur
        ]
        
        for line in lines:
            line = line.strip()
            if len(line) < 5:
                continue
                
            for pattern in title_patterns:
                if re.match(pattern, line):
                    # Tentative de séparation titre/auteur
                    parts = line.split(' - ')
                    if len(parts) == 2:
                        title, author = parts
                    else:
                        title = line
                        author = "Auteur inconnu"
                    
                    books.append(BookIdentification(
                        title=title.strip(),
                        author=author.strip(),
                        confidence=0.7  # Confidence basique pour OCR
                    ))
                    break
        
        return books
    
    def search_digital_versions(self, books: List[BookIdentification]) -> List[DigitalBookContent]:
        """
        Recherche versions numériques pour les livres identifiés
        
        Args:
            books: Liste des livres identifiés
            
        Returns:
            Liste du contenu numérique trouvé
        """
        logger.info(f"🔍 Recherche versions numériques pour {len(books)} livres")
        
        digital_content = []
        
        for book in books:
            try:
                # Recherche séquentielle dans les APIs
                content = self._search_google_books(book.title, book.author)
                if not content:
                    content = self._search_openlibrary(book.title, book.author)
                if not content:
                    content = self._search_gallica(book.title, book.author)
                
                if content:
                    digital_content.append(content)
                    self.stats['digital_versions_found'] += 1
                    logger.info(f"✅ Version numérique trouvée: {content.title}")
                
                # Délai pour respecter les limites API
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"❌ Erreur recherche numérique {book.title}: {e}")
                continue
        
        logger.info(f"📚 {len(digital_content)} versions numériques trouvées")
        return digital_content
    
    def _search_google_books(self, title: str, author: str) -> Optional[DigitalBookContent]:
        """Recherche dans Google Books API"""
        try:
            query = f'intitle:"{title}" inauthor:"{author}"'
            url = f"{self.apis['google_books']}?q={query}&maxResults=1"
            
            response = requests.get(url, timeout=10)
            self.stats['api_calls'] += 1
            
            if response.status_code == 200:
                data = response.json()
                if data.get('totalItems', 0) > 0:
                    item = data['items'][0]
                    volume_info = item['volumeInfo']
                    
                    # Extraction des extraits disponibles
                    excerpts = self._extract_google_books_excerpts(item)
                    
                    return DigitalBookContent(
                        isbn=self._extract_isbn(volume_info.get('industryIdentifiers', [])),
                        title=volume_info.get('title', title),
                        author=', '.join(volume_info.get('authors', [author])),
                        description=volume_info.get('description', ''),
                        categories=volume_info.get('categories', []),
                        page_count=volume_info.get('pageCount', 0),
                        language=volume_info.get('language', 'fr'),
                        published_date=volume_info.get('publishedDate', ''),
                        thumbnail_url=volume_info.get('imageLinks', {}).get('thumbnail', ''),
                        preview_url=volume_info.get('previewLink'),
                        full_text_available=bool(excerpts),
                        legal_excerpts=excerpts,
                        metadata=volume_info
                    )
            
        except Exception as e:
            logger.error(f"❌ Erreur Google Books API: {e}")
        
        return None
    
    def _search_openlibrary(self, title: str, author: str) -> Optional[DigitalBookContent]:
        """Recherche dans OpenLibrary API"""
        try:
            # Recherche par titre et auteur
            query = f"title:{title} author:{author}"
            url = f"https://openlibrary.org/search.json?q={query}&limit=1"
            
            response = requests.get(url, timeout=10)
            self.stats['api_calls'] += 1
            
            if response.status_code == 200:
                data = response.json()
                if data.get('numFound', 0) > 0:
                    doc = data['docs'][0]
                    
                    return DigitalBookContent(
                        isbn=doc.get('isbn', [''])[0] if doc.get('isbn') else '',
                        title=doc.get('title', title),
                        author=', '.join(doc.get('author_name', [author])),
                        description=doc.get('first_sentence', [''])[0] if doc.get('first_sentence') else '',
                        categories=doc.get('subject', [])[:5],  # Limitation à 5 catégories
                        page_count=doc.get('number_of_pages_median', 0),
                        language=doc.get('language', ['fr'])[0] if doc.get('language') else 'fr',
                        published_date=str(doc.get('first_publish_year', '')),
                        thumbnail_url=f"https://covers.openlibrary.org/b/id/{doc.get('cover_i', '')}-M.jpg" if doc.get('cover_i') else '',
                        preview_url=f"https://openlibrary.org{doc.get('key', '')}",
                        full_text_available=doc.get('has_fulltext', False),
                        legal_excerpts=[],
                        metadata=doc
                    )
            
        except Exception as e:
            logger.error(f"❌ Erreur OpenLibrary API: {e}")
        
        return None
    
    def _search_gallica(self, title: str, author: str) -> Optional[DigitalBookContent]:
        """Recherche dans Gallica (BnF)"""
        try:
            # Construction requête SRU pour Gallica
            query = f'title any "{title}" and creator any "{author}"'
            params = {
                'operation': 'searchRetrieve',
                'version': '1.2',
                'query': query,
                'maximumRecords': 1
            }
            
            response = requests.get(self.apis['gallica'], params=params, timeout=10)
            self.stats['api_calls'] += 1
            
            if response.status_code == 200:
                # Parsing XML basique (à améliorer avec lxml)
                if '<srw:numberOfRecords>0</srw:numberOfRecords>' not in response.text:
                    # Document trouvé - extraction basique
                    return DigitalBookContent(
                        isbn='',  # Gallica n'utilise pas ISBN
                        title=title,
                        author=author,
                        description='Document historique de la BnF',
                        categories=['Histoire', 'Patrimoine'],
                        page_count=0,
                        language='fr',
                        published_date='',
                        thumbnail_url='',
                        preview_url='https://gallica.bnf.fr/',
                        full_text_available=True,
                        legal_excerpts=[],
                        metadata={'source': 'gallica'}
                    )
            
        except Exception as e:
            logger.error(f"❌ Erreur Gallica API: {e}")
        
        return None
    
    def _extract_isbn(self, identifiers: List[Dict]) -> str:
        """Extraction ISBN depuis les identifiants"""
        for identifier in identifiers:
            if identifier.get('type') in ['ISBN_13', 'ISBN_10']:
                return identifier.get('identifier', '')
        return ''
    
    def _extract_google_books_excerpts(self, item: Dict) -> List[str]:
        """Extraction des extraits légaux disponibles"""
        excerpts = []
        
        # Vérification de la disponibilité de preview
        access_info = item.get('accessInfo', {})
        if access_info.get('viewability') in ['PARTIAL', 'ALL_PAGES']:
            # L'extrait est disponible via l'API
            volume_info = item['volumeInfo']
            if volume_info.get('description'):
                excerpts.append(volume_info['description'])
        
        return excerpts
    
    def get_collection_statistics(self) -> Dict:
        """Statistiques de la collecte"""
        return {
            **self.stats,
            'success_rate': self.stats['digital_versions_found'] / max(1, self.stats['books_identified']),
            'avg_api_calls_per_book': self.stats['api_calls'] / max(1, self.stats['books_identified'])
        }


def main():
    """Test du collecteur de bibliothèques numériques"""
    collector = DigitalLibraryCollector()
    
    # Test avec quelques livres de démonstration
    test_books = [
        BookIdentification("Le Petit Prince", "Antoine de Saint-Exupéry"),
        BookIdentification("Les Misérables", "Victor Hugo"),
        BookIdentification("L'Étranger", "Albert Camus")
    ]
    
    digital_content = collector.search_digital_versions(test_books)
    
    for content in digital_content:
        print(f"📚 {content.title} par {content.author}")
        print(f"   📖 {content.page_count} pages - {content.language}")
        print(f"   🔗 Preview: {content.preview_url}")
        print(f"   📝 Description: {content.description[:100]}...")
        print()
    
    print(f"📊 Statistiques: {collector.get_collection_statistics()}")


if __name__ == "__main__":
    main()
