"""
Quality Control System - Validate and ensure high-quality knowledge ingestion
"""
import re
import hashlib
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class QualityLevel(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    REJECTED = "rejected"

@dataclass
class QualityReport:
    content_id: str
    quality_level: QualityLevel
    score: float
    issues: List[str]
    suggestions: List[str]
    metadata: Dict[str, Any]
    timestamp: str

class QualityController:
    """Comprehensive quality control for ingested content"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.min_quality_score = config.get('min_quality_score', 3.0)
        self.duplicate_threshold = config.get('duplicate_threshold', 0.85)
        self.min_content_length = config.get('min_content_length', 50)
        self.max_content_length = config.get('max_content_length', 1000000)
        
        # Track processed content for duplicate detection
        self.content_hashes: Set[str] = set()
        self.content_fingerprints: Dict[str, str] = {}
        
        # Quality thresholds
        self.quality_thresholds = {
            QualityLevel.EXCELLENT: 8.0,
            QualityLevel.GOOD: 6.0,
            QualityLevel.ACCEPTABLE: 4.0,
            QualityLevel.POOR: 2.0
        }
    
    async def validate_content_batch(self, content_items: List[Dict[str, Any]]) -> List[QualityReport]:
        """Validate a batch of content items"""
        tasks = []
        for item in content_items:
            tasks.append(self.validate_single_content(item))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        quality_reports = []
        for result in results:
            if isinstance(result, QualityReport):
                quality_reports.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Quality validation error: {result}")
        
        return quality_reports
    
    async def validate_single_content(self, content_item: Dict[str, Any]) -> QualityReport:
        """Validate a single content item"""
        content_id = content_item.get('id', '') or content_item.get('content_id', '')
        content = content_item.get('content', '') or content_item.get('processed_content', '')
        
        if isinstance(content, bytes):
            content = content.decode('utf-8', errors='ignore')
        
        issues = []
        suggestions = []
        score = 10.0  # Start with perfect score and deduct points
        
        # Basic validation checks
        length_issues, length_score = self._validate_content_length(content)
        issues.extend(length_issues)
        score -= (10.0 - length_score)
        
        # Duplicate detection
        duplicate_issues, duplicate_score = self._check_duplicates(content, content_id)
        issues.extend(duplicate_issues)
        score -= (10.0 - duplicate_score)
        
        # Content quality analysis
        quality_issues, quality_score = self._analyze_content_quality(content)
        issues.extend(quality_issues)
        score = min(score, quality_score)
        
        # Format and structure validation
        format_issues, format_score = self._validate_format(content, content_item)
        issues.extend(format_issues)
        score = min(score, format_score)
        
        # Information density check
        density_issues, density_score = self._check_information_density(content)
        issues.extend(density_issues)
        score = min(score, density_score)
        
        # Metadata validation
        metadata_issues, metadata_score = self._validate_metadata(content_item)
        issues.extend(metadata_issues)
        score = min(score, metadata_score)
        
        # Source reliability check
        source_issues, source_score = self._check_source_reliability(content_item)
        issues.extend(source_issues)
        score = min(score, source_score)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(issues, content, content_item)
        
        # Determine quality level
        quality_level = self._determine_quality_level(score)
        
        # Record content fingerprint for future duplicate detection
        if quality_level != QualityLevel.REJECTED:
            content_hash = self._generate_content_hash(content)
            self.content_hashes.add(content_hash)
            self.content_fingerprints[content_id] = content_hash
        
        return QualityReport(
            content_id=content_id,
            quality_level=quality_level,
            score=round(score, 2),
            issues=issues,
            suggestions=suggestions,
            metadata={
                'content_length': len(content),
                'word_count': len(content.split()),
                'validation_time': datetime.now().isoformat(),
                'source': content_item.get('source', 'unknown')
            },
            timestamp=datetime.now().isoformat()
        )
    
    async def validate_content(self, processed_content, metadata: Dict[str, Any] = None):
        """Validate processed content and return validation results"""
        if metadata is None:
            metadata = {}
        
        try:
            # Handle both ProcessedContent objects and dictionaries
            if hasattr(processed_content, 'processed_content'):
                # It's a ProcessedContent dataclass object
                content_text = processed_content.processed_content
                content_item = {
                    'content': content_text,
                    'metadata': {**metadata, **processed_content.metadata},
                    'content_id': processed_content.content_id,
                    'content_type': processed_content.content_type.value if hasattr(processed_content.content_type, 'value') else str(processed_content.content_type),
                    'keywords': processed_content.keywords,
                    'entities': processed_content.entities,
                    'summary': processed_content.summary,
                    'topics': processed_content.topics,
                    'quality_score': processed_content.quality_score
                }
            else:
                # It's a dictionary
                content_text = processed_content.get('processed_content', processed_content.get('content', ''))
                if isinstance(content_text, str):
                    content_item = {
                        'content': content_text,
                        'metadata': metadata,
                        'content_id': processed_content.get('content_id', ''),
                        'content_type': processed_content.get('content_type', 'text'),
                        'keywords': processed_content.get('keywords', []),
                        'entities': processed_content.get('entities', []),
                        'summary': processed_content.get('summary', ''),
                        'topics': processed_content.get('topics', []),
                        'quality_score': processed_content.get('quality_score', 0.0)
                    }
                else:
                    # Handle case where content is still an object
                    content_item = {
                        'content': str(content_text),
                        'metadata': metadata,
                        'content_id': processed_content.get('content_id', ''),
                        'content_type': 'text',
                        'keywords': [],
                        'entities': [],
                        'summary': '',
                        'topics': [],
                        'quality_score': 0.0
                    }
            
            # Use existing validation method
            quality_report = await self.validate_single_content(content_item)
            
            # Return validation results with approved attribute for compatibility
            class ValidationResult:
                def __init__(self, is_valid, quality_score, issues, suggestions, quality_report):
                    self.approved = is_valid
                    self.is_valid = is_valid
                    self.quality_score = quality_score
                    self.issues = issues
                    self.suggestions = suggestions
                    self.quality_report = quality_report
            
            return ValidationResult(
                is_valid=quality_report.score >= self.min_quality_score,
                quality_score=quality_report.score,
                issues=quality_report.issues,
                suggestions=quality_report.suggestions,
                quality_report=quality_report
            )
            
        except Exception as e:
            logger.error(f"Error validating content: {e}")
            
            class ValidationResult:
                def __init__(self, is_valid, quality_score, issues, suggestions, error=None):
                    self.approved = is_valid
                    self.is_valid = is_valid
                    self.quality_score = quality_score
                    self.issues = issues
                    self.suggestions = suggestions
                    self.error = error
            
            return ValidationResult(
                is_valid=False,
                quality_score=0.0,
                issues=[f"Validation error: {e}"],
                suggestions=['Fix validation error and try again'],
                error=str(e)
            )
    
    def _validate_content_length(self, content: str) -> Tuple[List[str], float]:
        """Validate content length"""
        issues = []
        score = 10.0
        
        length = len(content.strip())
        
        if length < self.min_content_length:
            issues.append(f"Content too short ({length} chars, minimum {self.min_content_length})")
            score = 1.0
        elif length > self.max_content_length:
            issues.append(f"Content too long ({length} chars, maximum {self.max_content_length})")
            score = 3.0
        elif length < 100:
            issues.append("Content is quite short, may lack detail")
            score = 6.0
        elif length > 500000:
            issues.append("Content is very long, may need chunking")
            score = 7.0
        
        return issues, score
    
    def _check_duplicates(self, content: str, content_id: str) -> Tuple[List[str], float]:
        """Check for duplicate content"""
        issues = []
        score = 10.0
        
        content_hash = self._generate_content_hash(content)
        
        # Exact duplicate check
        if content_hash in self.content_hashes:
            issues.append("Exact duplicate content detected")
            score = 0.0
            return issues, score
        
        # Near-duplicate check using content fingerprinting
        similarity_score = self._calculate_content_similarity(content, content_hash)
        
        if similarity_score > self.duplicate_threshold:
            issues.append(f"Near-duplicate content detected (similarity: {similarity_score:.2f})")
            score = 2.0
        elif similarity_score > 0.7:
            issues.append(f"Similar content exists (similarity: {similarity_score:.2f})")
            score = 6.0
        
        return issues, score
    
    def _analyze_content_quality(self, content: str) -> Tuple[List[str], float]:
        """Analyze overall content quality"""
        issues = []
        score = 10.0
        
        # Check for meaningful content
        if self._is_mostly_garbled(content):
            issues.append("Content appears to be garbled or corrupted")
            score = 1.0
            return issues, score
        
        # Check for excessive repetition
        if self._has_excessive_repetition(content):
            issues.append("Content has excessive repetition")
            score = min(score, 4.0)
        
        # Check language consistency
        if self._has_language_mixing_issues(content):
            issues.append("Content has language mixing or encoding issues")
            score = min(score, 6.0)
        
        # Check for coherence
        coherence_score = self._assess_coherence(content)
        if coherence_score < 0.3:
            issues.append("Content lacks coherence or structure")
            score = min(score, 5.0)
        elif coherence_score < 0.6:
            issues.append("Content structure could be improved")
            score = min(score, 7.0)
        
        # Check for information value
        info_value = self._assess_information_value(content)
        if info_value < 0.3:
            issues.append("Content has low information value")
            score = min(score, 4.0)
        elif info_value < 0.6:
            issues.append("Content could be more informative")
            score = min(score, 7.0)
        
        return issues, score
    
    def _validate_format(self, content: str, content_item: Dict[str, Any]) -> Tuple[List[str], float]:
        """Validate content format and structure"""
        issues = []
        score = 10.0
        
        # Check for proper encoding
        try:
            content.encode('utf-8')
        except UnicodeEncodeError:
            issues.append("Content has encoding issues")
            score = min(score, 5.0)
        
        # Check for excessive special characters
        special_char_ratio = len(re.findall(r'[^\w\s\.,!?;:\-()"\']', content)) / len(content)
        if special_char_ratio > 0.1:
            issues.append("Content has too many special characters or symbols")
            score = min(score, 6.0)
        
        # Check for proper sentence structure
        sentences = re.split(r'[.!?]+', content)
        if len(sentences) > 10:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            if avg_sentence_length < 3:
                issues.append("Sentences are too short on average")
                score = min(score, 7.0)
            elif avg_sentence_length > 50:
                issues.append("Sentences are too long on average")
                score = min(score, 7.0)
        
        # Check file format consistency
        source = content_item.get('source', '')
        file_name = content_item.get('name', '')
        
        if 'pdf' in file_name.lower() and len(content.split()) < 50:
            issues.append("PDF extraction may have failed")
            score = min(score, 4.0)
        
        return issues, score
    
    def _check_information_density(self, content: str) -> Tuple[List[str], float]:
        """Check information density of content"""
        issues = []
        score = 10.0
        
        words = content.split()
        if not words:
            issues.append("No extractable words found")
            return issues, 1.0
        
        # Calculate unique word ratio
        unique_words = set(word.lower() for word in words if word.isalpha())
        unique_ratio = len(unique_words) / len(words) if words else 0
        
        if unique_ratio < 0.3:
            issues.append("Low vocabulary diversity")
            score = min(score, 5.0)
        elif unique_ratio < 0.5:
            issues.append("Moderate vocabulary diversity")
            score = min(score, 7.0)
        
        # Check for meaningful content vs filler
        filler_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        filler_ratio = sum(1 for word in words if word.lower() in filler_words) / len(words)
        
        if filler_ratio > 0.5:
            issues.append("High ratio of filler words")
            score = min(score, 6.0)
        
        # Check for technical or specialized content
        technical_indicators = self._count_technical_indicators(content)
        if technical_indicators > 5:
            # Technical content is valuable
            score = min(score + 1.0, 10.0)
        
        return issues, score
    
    def _validate_metadata(self, content_item: Dict[str, Any]) -> Tuple[List[str], float]:
        """Validate metadata completeness and accuracy"""
        issues = []
        score = 10.0
        
        required_fields = ['source', 'collection_time']
        recommended_fields = ['created_time', 'modified_time', 'title', 'path']
        
        # Check required fields
        for field in required_fields:
            if field not in content_item or not content_item[field]:
                issues.append(f"Missing required metadata: {field}")
                score = min(score, 6.0)
        
        # Check recommended fields
        missing_recommended = [field for field in recommended_fields if field not in content_item]
        if missing_recommended:
            issues.append(f"Missing recommended metadata: {', '.join(missing_recommended)}")
            score = min(score, 8.0)
        
        # Validate timestamp formats
        for time_field in ['created_time', 'modified_time', 'collection_time']:
            if time_field in content_item and content_item[time_field]:
                try:
                    datetime.fromisoformat(content_item[time_field].replace('Z', '+00:00'))
                except:
                    issues.append(f"Invalid timestamp format in {time_field}")
                    score = min(score, 7.0)
        
        return issues, score
    
    def _check_source_reliability(self, content_item: Dict[str, Any]) -> Tuple[List[str], float]:
        """Check source reliability and trustworthiness"""
        issues = []
        score = 10.0
        
        source = content_item.get('source', '').lower()
        
        # High-reliability sources
        high_reliability = ['academic', 'research', 'documentation', 'official', 'apple_notes', 'obsidian']
        if any(reliable in source for reliable in high_reliability):
            score = min(score + 1.0, 10.0)
        
        # Medium-reliability sources
        medium_reliability = ['safari_bookmarks', 'chrome_bookmarks', 'bear_notes']
        
        # Low-reliability sources (might need extra validation)
        low_reliability = ['unknown', 'temp', 'cache']
        if any(unreliable in source for unreliable in low_reliability):
            issues.append("Content from potentially unreliable source")
            score = min(score, 6.0)
        
        # Check for suspicious content patterns
        content = content_item.get('content', '')
        if isinstance(content, str):
            if 'viagra' in content.lower() or 'click here' in content.lower():
                issues.append("Content may contain spam or promotional material")
                score = min(score, 3.0)
        
        return issues, score
    
    def _generate_suggestions(self, issues: List[str], content: str, content_item: Dict[str, Any]) -> List[str]:
        """Generate improvement suggestions based on identified issues"""
        suggestions = []
        
        if "Content too short" in str(issues):
            suggestions.append("Consider combining with related content or adding more context")
        
        if "excessive repetition" in str(issues):
            suggestions.append("Remove repeated sections and consolidate similar information")
        
        if "encoding issues" in str(issues):
            suggestions.append("Re-extract content with proper encoding handling")
        
        if "Low vocabulary diversity" in str(issues):
            suggestions.append("Content may be incomplete or require manual review")
        
        if "Missing metadata" in str(issues):
            suggestions.append("Enrich metadata by analyzing file properties and content")
        
        if "PDF extraction may have failed" in str(issues):
            suggestions.append("Try alternative PDF extraction methods or manual processing")
        
        if "garbled or corrupted" in str(issues):
            suggestions.append("Re-extract from original source or exclude from processing")
        
        if "duplicate content" in str(issues):
            suggestions.append("Merge with existing content or identify as reference")
        
        return suggestions
    
    def _determine_quality_level(self, score: float) -> QualityLevel:
        """Determine quality level based on score"""
        if score >= self.quality_thresholds[QualityLevel.EXCELLENT]:
            return QualityLevel.EXCELLENT
        elif score >= self.quality_thresholds[QualityLevel.GOOD]:
            return QualityLevel.GOOD
        elif score >= self.quality_thresholds[QualityLevel.ACCEPTABLE]:
            return QualityLevel.ACCEPTABLE
        elif score >= self.quality_thresholds[QualityLevel.POOR]:
            return QualityLevel.POOR
        else:
            return QualityLevel.REJECTED
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate hash for duplicate detection"""
        # Normalize content for comparison
        normalized = re.sub(r'\s+', ' ', content.lower().strip())
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()
    
    def _calculate_content_similarity(self, content: str, content_hash: str) -> float:
        """Calculate similarity to existing content"""
        max_similarity = 0.0
        
        # Simple similarity check with existing fingerprints
        # In production, use more sophisticated algorithms like MinHash or SimHash
        
        normalized_content = re.sub(r'\s+', ' ', content.lower().strip())
        content_words = set(normalized_content.split())
        
        for existing_id, existing_hash in self.content_fingerprints.items():
            if existing_hash == content_hash:
                continue
            
            # Simple Jaccard similarity
            # This is a placeholder - implement proper similarity matching
            similarity = len(content_words) / (len(content_words) + 100)  # Simplified
            max_similarity = max(max_similarity, similarity)
        
        return max_similarity
    
    def _is_mostly_garbled(self, content: str) -> bool:
        """Check if content is mostly garbled"""
        if not content:
            return True
        
        # Check ratio of printable characters
        printable_chars = sum(1 for c in content if c.isprintable())
        printable_ratio = printable_chars / len(content)
        
        if printable_ratio < 0.8:
            return True
        
        # Check for excessive non-alphabetic characters
        alpha_chars = sum(1 for c in content if c.isalpha())
        alpha_ratio = alpha_chars / len(content)
        
        if alpha_ratio < 0.3:
            return True
        
        return False
    
    def _has_excessive_repetition(self, content: str) -> bool:
        """Check for excessive repetition in content"""
        lines = content.split('\n')
        if len(lines) < 5:
            return False
        
        # Check for repeated lines
        line_counts = {}
        for line in lines:
            line_stripped = line.strip()
            if len(line_stripped) > 10:  # Only check substantial lines
                line_counts[line_stripped] = line_counts.get(line_stripped, 0) + 1
        
        # If any line appears more than 20% of the time, it's excessive
        max_repetition = max(line_counts.values()) if line_counts else 0
        repetition_ratio = max_repetition / len(lines)
        
        return repetition_ratio > 0.2
    
    def _has_language_mixing_issues(self, content: str) -> bool:
        """Check for language mixing or encoding issues"""
        # Look for suspicious character patterns
        suspicious_patterns = [
            r'[^\x00-\x7F]{5,}',  # Long sequences of non-ASCII
            r'[\x00-\x1F]{2,}',   # Control characters
            r'�{2,}',             # Replacement characters
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, content):
                return True
        
        return False
    
    def _assess_coherence(self, content: str) -> float:
        """Assess content coherence (simplified)"""
        sentences = re.split(r'[.!?]+', content)
        if len(sentences) < 3:
            return 1.0
        
        # Simple coherence metrics
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        # Reasonable sentence length indicates coherence
        if 5 <= avg_sentence_length <= 30:
            coherence = 0.8
        elif 3 <= avg_sentence_length <= 50:
            coherence = 0.6
        else:
            coherence = 0.3
        
        # Check for paragraph structure
        paragraphs = content.split('\n\n')
        if len(paragraphs) > 1:
            coherence += 0.2
        
        return min(coherence, 1.0)
    
    def _assess_information_value(self, content: str) -> float:
        """Assess information value of content"""
        words = content.split()
        if not words:
            return 0.0
        
        value = 0.5  # Base value
        
        # Technical terms increase value
        technical_score = self._count_technical_indicators(content)
        value += min(technical_score * 0.05, 0.3)
        
        # Proper nouns and entities increase value
        proper_nouns = sum(1 for word in words if word[0].isupper() and word.isalpha())
        value += min(proper_nouns / len(words), 0.2)
        
        # Numbers and dates often indicate factual content
        numbers = len(re.findall(r'\b\d+\b', content))
        value += min(numbers / len(words), 0.1)
        
        return min(value, 1.0)
    
    def _count_technical_indicators(self, content: str) -> int:
        """Count technical indicators in content"""
        technical_patterns = [
            r'\b[A-Z]{2,}\b',     # Acronyms
            r'\b\w+\(\)',         # Function calls
            r'https?://',         # URLs
            r'\b\d+\.\d+\b',      # Version numbers
            r'[{}[\]()]',         # Brackets (code/data)
            r'\b[a-z]+_[a-z]+\b', # Snake_case
            r'\b[a-z]+[A-Z]\w*\b' # CamelCase
        ]
        
        count = 0
        for pattern in technical_patterns:
            count += len(re.findall(pattern, content))
        
        return count
