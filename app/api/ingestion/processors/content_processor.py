"""
Content Processor - Analyze and enrich collected content
"""
import re
import os
import hashlib
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
from dataclasses import dataclass
from enum import Enum
import os

logger = logging.getLogger(__name__)

class ContentType(Enum):
    TEXT = "text"
    CODE = "code"
    ACADEMIC = "academic"
    TECHNICAL = "technical"
    PERSONAL = "personal"
    REFERENCE = "reference"
    MULTIMEDIA = "multimedia"

@dataclass
class ProcessedContent:
    content_id: str
    original_content: str
    processed_content: str
    content_type: ContentType
    keywords: List[str]
    entities: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    summary: str
    topics: List[str]
    quality_score: float
    metadata: Dict[str, Any]

class ContentProcessor:
    """Process and analyze collected content to extract meaningful information"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.min_content_length = config.get('min_content_length', 50)
        self.max_summary_length = config.get('max_summary_length', 200)
        
        # Initialize NLP tools if available
        self.nlp_available = False
        try:
            import spacy
            # Try to load English model
            self.nlp = spacy.load("en_core_web_sm")
            self.nlp_available = True
            logger.info("SpaCy NLP model loaded successfully")
        except:
            logger.warning("SpaCy not available. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    async def process_content_batch(self, content_items: List[Dict[str, Any]]) -> List[ProcessedContent]:
        """Process a batch of content items"""
        tasks = []
        for item in content_items:
            tasks.append(self.process_single_content(item))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        processed_items = []
        for result in results:
            if isinstance(result, ProcessedContent):
                processed_items.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Content processing error: {result}")
        
        return processed_items
    
    async def process_single_content(self, content_item: Dict[str, Any]) -> ProcessedContent:
        """Process a single content item"""
        content_text = content_item.get('content', '')
        if isinstance(content_text, bytes):
            content_text = content_text.decode('utf-8', errors='ignore')
        
        # Skip if content is too short
        if len(content_text.strip()) < self.min_content_length:
            content_text = content_item.get('title', '') + ' ' + content_text
        
        content_id = content_item.get('id', '') or self._generate_content_id(content_text)
        
        # Classify content type
        content_type = self._classify_content_type(content_text, content_item)
        
        # Extract keywords
        keywords = self._extract_keywords(content_text)
        
        # Extract entities
        entities = self._extract_entities(content_text)
        
        # Find relationships
        relationships = self._find_relationships(content_text, content_item)
        
        # Generate summary
        summary = self._generate_summary(content_text)
        
        # Extract topics
        topics = self._extract_topics(content_text, keywords)
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(content_text, content_item)
        
        # Clean and normalize content
        processed_content = self._clean_content(content_text)
        
        # Compile metadata
        metadata = self._extract_metadata(content_item, content_text)
        
        return ProcessedContent(
            content_id=content_id,
            original_content=content_text,
            processed_content=processed_content,
            content_type=content_type,
            keywords=keywords,
            entities=entities,
            relationships=relationships,
            summary=summary,
            topics=topics,
            quality_score=quality_score,
            metadata=metadata
        )
    
    async def process_file(self, file_path: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a single file and return processed content"""
        if metadata is None:
            metadata = {}
            
        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create content item structure
            content_item = {
                'content': content,
                'source_path': file_path,
                'filename': os.path.basename(file_path),
                'file_type': os.path.splitext(file_path)[1].lower(),
                **metadata  # Merge additional metadata
            }
            
            # Process the content
            processed = await self.process_single_content(content_item)
            
            return {
                'original_path': file_path,
                'processed_content': processed,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return {
                'original_path': file_path,
                'error': str(e),
                'status': 'error'
            }
    
    async def health_check(self) -> Dict[str, str]:
        """Check the health of the content processor"""
        try:
            # Test basic functionality
            test_content = "This is a test content for health check."
            test_item = {
                'content': test_content,
                'id': 'health_check_test'
            }
            
            # Try to process a simple content item
            result = await self.process_single_content(test_item)
            
            if result and hasattr(result, 'content_id'):
                return {'status': 'healthy', 'message': 'Content processor is working normally'}
            else:
                return {'status': 'unhealthy', 'message': 'Content processing failed'}
                
        except Exception as e:
            return {'status': 'unhealthy', 'message': f'Health check failed: {e}'}
    
    def _classify_content_type(self, content: str, item: Dict[str, Any]) -> ContentType:
        """Classify content into categories"""
        content_lower = content.lower()
        source = item.get('source', '').lower()
        file_ext = item.get('name', '').split('.')[-1].lower() if 'name' in item else ''
        
        # Code detection
        code_indicators = [
            'def ', 'function', 'class ', 'import ', 'export ', 'const ', 'var ', 'let ',
            '```', 'github.com', 'stackoverflow', 'def main(', 'if __name__'
        ]
        if any(indicator in content for indicator in code_indicators):
            return ContentType.CODE
        
        # Academic content
        academic_indicators = [
            'abstract', 'methodology', 'hypothesis', 'research', 'study shows',
            'journal', 'peer review', 'bibliography', 'citation', 'doi:', 'arxiv'
        ]
        if any(indicator in content_lower for indicator in academic_indicators):
            return ContentType.ACADEMIC
        
        # Technical documentation
        technical_indicators = [
            'api', 'documentation', 'tutorial', 'guide', 'specification',
            'installation', 'configuration', 'troubleshooting', 'setup'
        ]
        if any(indicator in content_lower for indicator in technical_indicators):
            return ContentType.TECHNICAL
        
        # Personal content
        personal_indicators = [
            'notes', 'diary', 'journal', 'personal', 'todo', 'reminder'
        ]
        if (any(indicator in source for indicator in personal_indicators) or
            any(indicator in content_lower for indicator in personal_indicators)):
            return ContentType.PERSONAL
        
        # Reference material
        reference_indicators = [
            'wikipedia', 'encyclopedia', 'dictionary', 'glossary', 'reference'
        ]
        if any(indicator in content_lower for indicator in reference_indicators):
            return ContentType.REFERENCE
        
        # Multimedia content
        multimedia_extensions = ['jpg', 'png', 'gif', 'mp4', 'mp3', 'pdf']
        if file_ext in multimedia_extensions:
            return ContentType.MULTIMEDIA
        
        return ContentType.TEXT
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract important keywords from content"""
        keywords = []
        
        if self.nlp_available and self.nlp:
            # Use SpaCy for advanced keyword extraction
            doc = self.nlp(content[:10000])  # Limit processing to first 10k chars
            
            # Extract named entities
            for ent in doc.ents:
                if ent.label_ in ['PERSON', 'ORG', 'GPE', 'PRODUCT', 'EVENT']:
                    keywords.append(ent.text.lower())
            
            # Extract important nouns and adjectives
            for token in doc:
                if (token.pos_ in ['NOUN', 'PROPN'] and 
                    len(token.text) > 3 and 
                    not token.is_stop and 
                    token.is_alpha):
                    keywords.append(token.lemma_.lower())
        else:
            # Fallback: simple regex-based extraction
            words = re.findall(r'\b[A-Za-z]{4,}\b', content)
            word_freq = {}
            for word in words:
                word_lower = word.lower()
                if word_lower not in self._get_stop_words():
                    word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
            
            # Get top keywords by frequency
            keywords = sorted(word_freq.keys(), key=lambda x: word_freq[x], reverse=True)[:20]
        
        return keywords[:15]  # Return top 15 keywords
    
    def _extract_entities(self, content: str) -> List[Dict[str, Any]]:
        """Extract named entities from content"""
        entities = []
        
        if self.nlp_available and self.nlp:
            doc = self.nlp(content[:10000])
            
            for ent in doc.ents:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'description': spacy.explain(ent.label_) if hasattr(spacy, 'explain') else ent.label_
                })
        else:
            # Fallback: regex-based entity extraction
            # URLs
            urls = re.findall(r'https?://[^\s]+', content)
            for url in urls:
                entities.append({
                    'text': url,
                    'label': 'URL',
                    'start': content.find(url),
                    'end': content.find(url) + len(url),
                    'description': 'Web URL'
                })
            
            # Email addresses
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
            for email in emails:
                entities.append({
                    'text': email,
                    'label': 'EMAIL',
                    'start': content.find(email),
                    'end': content.find(email) + len(email),
                    'description': 'Email address'
                })
            
            # Dates
            dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', content)
            for date in dates:
                entities.append({
                    'text': date,
                    'label': 'DATE',
                    'start': content.find(date),
                    'end': content.find(date) + len(date),
                    'description': 'Date'
                })
        
        return entities[:20]  # Return top 20 entities
    
    def _find_relationships(self, content: str, item: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find relationships between content elements"""
        relationships = []
        
        # File-based relationships
        source = item.get('source', '')
        file_path = item.get('path', '')
        
        if file_path:
            # Folder relationship
            folder = '/'.join(file_path.split('/')[:-1])
            if folder:
                relationships.append({
                    'type': 'belongs_to_folder',
                    'target': folder,
                    'strength': 1.0,
                    'description': f"Located in folder: {folder}"
                })
        
        # Source application relationship
        if source:
            relationships.append({
                'type': 'created_by',
                'target': source,
                'strength': 1.0,
                'description': f"Created/stored by: {source}"
            })
        
        # Content-based relationships
        # Links to other files or URLs
        links = re.findall(r'\[\[([^\]]+)\]\]', content)  # Wiki-style links
        for link in links:
            relationships.append({
                'type': 'references',
                'target': link,
                'strength': 0.8,
                'description': f"References: {link}"
            })
        
        # URLs
        urls = re.findall(r'https?://[^\s]+', content)
        for url in urls[:5]:  # Limit to first 5 URLs
            relationships.append({
                'type': 'links_to',
                'target': url,
                'strength': 0.6,
                'description': f"Links to external resource"
            })
        
        # Tag relationships
        tags = re.findall(r'#(\w+)', content)
        for tag in set(tags):  # Remove duplicates
            relationships.append({
                'type': 'tagged_with',
                'target': tag,
                'strength': 0.7,
                'description': f"Tagged with: #{tag}"
            })
        
        return relationships
    
    def _generate_summary(self, content: str) -> str:
        """Generate a summary of the content"""
        if len(content) <= self.max_summary_length:
            return content.strip()
        
        # Simple extractive summarization
        sentences = re.split(r'[.!?]+', content)
        
        if len(sentences) <= 3:
            return content[:self.max_summary_length] + "..."
        
        # Score sentences based on position and content
        sentence_scores = []
        for i, sentence in enumerate(sentences):
            score = 0
            
            # Position score (beginning sentences are more important)
            if i < 3:
                score += 2
            elif i < len(sentences) // 2:
                score += 1
            
            # Length score (avoid very short sentences)
            if 10 < len(sentence) < 200:
                score += 1
            
            # Content score (sentences with important words)
            important_words = ['important', 'key', 'main', 'primary', 'significant', 'essential']
            if any(word in sentence.lower() for word in important_words):
                score += 1
            
            sentence_scores.append((sentence.strip(), score))
        
        # Select top sentences
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        selected_sentences = [s[0] for s in sentence_scores[:3] if s[0]]
        
        summary = '. '.join(selected_sentences)
        
        if len(summary) > self.max_summary_length:
            summary = summary[:self.max_summary_length] + "..."
        
        return summary
    
    def _extract_topics(self, content: str, keywords: List[str]) -> List[str]:
        """Extract topics from content"""
        topics = []
        
        # Topic mapping based on keywords and content patterns
        topic_patterns = {
            'artificial_intelligence': ['ai', 'machine learning', 'neural', 'deep learning', 'algorithm'],
            'programming': ['code', 'programming', 'development', 'software', 'python', 'javascript'],
            'science': ['research', 'study', 'experiment', 'theory', 'hypothesis', 'scientific'],
            'technology': ['technology', 'tech', 'digital', 'computer', 'internet', 'web'],
            'business': ['business', 'management', 'strategy', 'market', 'finance', 'startup'],
            'education': ['learning', 'education', 'course', 'tutorial', 'teaching', 'training'],
            'health': ['health', 'medical', 'medicine', 'wellness', 'fitness', 'nutrition'],
            'philosophy': ['philosophy', 'ethics', 'moral', 'existence', 'consciousness', 'metaphysics'],
            'creativity': ['creative', 'art', 'design', 'music', 'writing', 'innovation'],
            'productivity': ['productivity', 'efficiency', 'optimization', 'workflow', 'time management']
        }
        
        content_lower = content.lower()
        
        for topic, patterns in topic_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in content_lower:
                    score += content_lower.count(pattern)
                # Check keywords too
                if any(pattern in keyword for keyword in keywords):
                    score += 2
            
            if score > 0:
                topics.append((topic, score))
        
        # Sort by score and return top topics
        topics.sort(key=lambda x: x[1], reverse=True)
        return [topic[0] for topic in topics[:5]]
    
    def _calculate_quality_score(self, content: str, item: Dict[str, Any]) -> float:
        """Calculate content quality score"""
        score = 0.0
        
        # Length factor
        length = len(content.strip())
        if length > 1000:
            score += 3.0
        elif length > 500:
            score += 2.0
        elif length > 100:
            score += 1.0
        else:
            score += 0.5
        
        # Structure indicators
        if content.count('\n') > 5:  # Multi-paragraph
            score += 1.0
        
        if re.search(r'#+ ', content):  # Headers
            score += 1.0
        
        if content.count('- ') > 2:  # Lists
            score += 0.5
        
        # Content quality indicators
        quality_indicators = [
            'analysis', 'conclusion', 'summary', 'important', 'key points',
            'methodology', 'results', 'discussion', 'background', 'introduction'
        ]
        
        for indicator in quality_indicators:
            if indicator in content.lower():
                score += 0.3
        
        # Source reliability
        source = item.get('source', '').lower()
        reliable_sources = ['academic', 'research', 'official', 'documentation']
        if any(reliable in source for reliable in reliable_sources):
            score += 1.0
        
        # Recency bonus
        modified_time = item.get('modified_time')
        if modified_time:
            try:
                from datetime import datetime, timedelta
                mod_date = datetime.fromisoformat(modified_time.replace('Z', '+00:00'))
                days_old = (datetime.now().replace(tzinfo=mod_date.tzinfo) - mod_date).days
                
                if days_old < 30:
                    score += 1.0
                elif days_old < 90:
                    score += 0.5
            except:
                pass
        
        return min(score, 10.0)  # Cap at 10.0
    
    def _clean_content(self, content: str) -> str:
        """Clean and normalize content"""
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        
        # Remove control characters
        content = ''.join(char for char in content if ord(char) >= 32 or char in '\n\t')
        
        # Normalize line endings
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        return content.strip()
    
    def _extract_metadata(self, item: Dict[str, Any], content: str) -> Dict[str, Any]:
        """Extract comprehensive metadata"""
        metadata = {}
        
        # Basic item metadata
        for key in ['source', 'name', 'path', 'size', 'created_time', 'modified_time', 'collection_time']:
            if key in item:
                metadata[key] = item[key]
        
        # Content analysis metadata
        metadata.update({
            'word_count': len(content.split()),
            'character_count': len(content),
            'line_count': content.count('\n') + 1,
            'has_urls': bool(re.search(r'https?://', content)),
            'has_emails': bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)),
            'has_code': bool(re.search(r'```|def |function |class ', content)),
            'has_links': bool(re.search(r'\[\[.*?\]\]|\[.*?\]\(.*?\)', content)),
            'language': self._detect_language(content),
            'processing_time': datetime.now().isoformat()
        })
        
        return metadata
    
    def _detect_language(self, content: str) -> str:
        """Simple language detection"""
        # This is a very basic implementation
        # For production, consider using langdetect or similar library
        
        english_indicators = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of']
        french_indicators = ['le', 'la', 'les', 'de', 'du', 'des', 'et', 'ou', 'dans', 'sur']
        
        content_lower = content.lower()
        
        english_score = sum(content_lower.count(word) for word in english_indicators)
        french_score = sum(content_lower.count(word) for word in french_indicators)
        
        if english_score > french_score:
            return 'en'
        elif french_score > 0:
            return 'fr'
        else:
            return 'unknown'
    
    def _generate_content_id(self, content: str) -> str:
        """Generate unique content ID"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:16]
    
    def _get_stop_words(self) -> set:
        """Get common stop words"""
        return {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'this', 'that', 'these', 'those', 'is', 'are', 'was', 'were', 'be', 'been',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'must', 'can', 'cannot', 'it', 'its', 'he', 'she', 'they', 'we',
            'you', 'i', 'me', 'him', 'her', 'them', 'us', 'my', 'your', 'his', 'our', 'their'
        }
