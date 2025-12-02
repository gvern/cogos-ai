"""
Storage Manager - Handle data persistence and retrieval for ingested content
"""
import os
import json
import sqlite3
import asyncio
import pickle
from typing import Dict, List, Any, Optional, Iterator
from datetime import datetime
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class StorageManager:
    """Manage storage and retrieval of processed knowledge content"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.storage_path = config.get('storage_path', '/tmp/cogos_storage')
        self.db_path = os.path.join(self.storage_path, 'knowledge.db')
        self.content_path = os.path.join(self.storage_path, 'content')
        self.embeddings_path = os.path.join(self.storage_path, 'embeddings')
        
        # Create directories
        os.makedirs(self.storage_path, exist_ok=True)
        os.makedirs(self.content_path, exist_ok=True)
        os.makedirs(self.embeddings_path, exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main content table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS content (
            id TEXT PRIMARY KEY,
            title TEXT,
            content_type TEXT,
            source TEXT,
            file_path TEXT,
            content_hash TEXT,
            created_time TEXT,
            modified_time TEXT,
            collection_time TEXT,
            processing_time TEXT,
            quality_score REAL,
            quality_level TEXT,
            word_count INTEGER,
            size INTEGER,
            language TEXT,
            metadata TEXT
        )
        ''')
        
        # Keywords table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS keywords (
            content_id TEXT,
            keyword TEXT,
            frequency INTEGER,
            FOREIGN KEY (content_id) REFERENCES content (id)
        )
        ''')
        
        # Entities table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS entities (
            content_id TEXT,
            entity_text TEXT,
            entity_type TEXT,
            start_pos INTEGER,
            end_pos INTEGER,
            confidence REAL,
            FOREIGN KEY (content_id) REFERENCES content (id)
        )
        ''')
        
        # Relationships table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS relationships (
            content_id TEXT,
            relationship_type TEXT,
            target TEXT,
            strength REAL,
            description TEXT,
            FOREIGN KEY (content_id) REFERENCES content (id)
        )
        ''')
        
        # Topics table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS topics (
            content_id TEXT,
            topic TEXT,
            relevance REAL,
            FOREIGN KEY (content_id) REFERENCES content (id)
        )
        ''')
        
        # Quality issues table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS quality_issues (
            content_id TEXT,
            issue_type TEXT,
            description TEXT,
            severity TEXT,
            suggestion TEXT,
            FOREIGN KEY (content_id) REFERENCES content (id)
        )
        ''')
        
        # Collections table (for organizing content)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS collections (
            id TEXT PRIMARY KEY,
            name TEXT,
            description TEXT,
            created_time TEXT,
            metadata TEXT
        )
        ''')
        
        # Collection memberships
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS collection_memberships (
            collection_id TEXT,
            content_id TEXT,
            added_time TEXT,
            FOREIGN KEY (collection_id) REFERENCES collections (id),
            FOREIGN KEY (content_id) REFERENCES content (id)
        )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_type ON content (content_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_source ON content (source)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_quality ON content (quality_level)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_keywords_content ON keywords (content_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entities_content ON entities (content_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_relationships_content ON relationships (content_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_topics_content ON topics (content_id)')
        
        conn.commit()
        conn.close()
        
        logger.info(f"Storage database initialized at {self.db_path}")
    
    async def store_processed_content(self, processed_content: Any, quality_report: Any) -> bool:
        """Store processed content with quality information"""
        try:
            content_id = processed_content.content_id
            
            # Store main content file
            content_file_path = os.path.join(self.content_path, f"{content_id}.json")
            content_data = {
                'id': content_id,
                'original_content': processed_content.original_content,
                'processed_content': processed_content.processed_content,
                'summary': processed_content.summary,
                'metadata': processed_content.metadata
            }
            
            with open(content_file_path, 'w', encoding='utf-8') as f:
                json.dump(content_data, f, ensure_ascii=False, indent=2)
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert main content record
            cursor.execute('''
            INSERT OR REPLACE INTO content (
                id, title, content_type, source, file_path, content_hash,
                created_time, modified_time, collection_time, processing_time,
                quality_score, quality_level, word_count, size, language, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                content_id,
                processed_content.metadata.get('title', 'Untitled'),
                processed_content.content_type.value,
                processed_content.metadata.get('source'),
                content_file_path,
                processed_content.metadata.get('content_hash'),
                processed_content.metadata.get('created_time'),
                processed_content.metadata.get('modified_time'),
                processed_content.metadata.get('collection_time'),
                datetime.now().isoformat(),
                quality_report.quality_score,
                quality_report.quality_report.quality_level.value,
                processed_content.metadata.get('word_count', 0),
                processed_content.metadata.get('size', 0),
                processed_content.metadata.get('language', 'unknown'),
                json.dumps(processed_content.metadata)
            ))
            
            # Clear existing related data
            cursor.execute('DELETE FROM keywords WHERE content_id = ?', (content_id,))
            cursor.execute('DELETE FROM entities WHERE content_id = ?', (content_id,))
            cursor.execute('DELETE FROM relationships WHERE content_id = ?', (content_id,))
            cursor.execute('DELETE FROM topics WHERE content_id = ?', (content_id,))
            cursor.execute('DELETE FROM quality_issues WHERE content_id = ?', (content_id,))
            
            # Insert keywords
            for keyword in processed_content.keywords:
                cursor.execute('''
                INSERT INTO keywords (content_id, keyword, frequency) VALUES (?, ?, ?)
                ''', (content_id, keyword, 1))  # Frequency tracking could be enhanced
            
            # Insert entities
            for entity in processed_content.entities:
                cursor.execute('''
                INSERT INTO entities (content_id, entity_text, entity_type, start_pos, end_pos, confidence)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    content_id,
                    entity.get('text'),
                    entity.get('label'),
                    entity.get('start', 0),
                    entity.get('end', 0),
                    1.0  # Confidence could be calculated
                ))
            
            # Insert relationships
            for relationship in processed_content.relationships:
                cursor.execute('''
                INSERT INTO relationships (content_id, relationship_type, target, strength, description)
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    content_id,
                    relationship.get('type'),
                    relationship.get('target'),
                    relationship.get('strength', 0.5),
                    relationship.get('description')
                ))
            
            # Insert topics
            for topic in processed_content.topics:
                cursor.execute('''
                INSERT INTO topics (content_id, topic, relevance) VALUES (?, ?, ?)
                ''', (content_id, topic, 1.0))  # Relevance could be calculated
            
            # Insert quality issues
            for issue in quality_report.issues:
                cursor.execute('''
                INSERT INTO quality_issues (content_id, issue_type, description, severity)
                VALUES (?, ?, ?, ?)
                ''', (content_id, 'general', issue, 'medium'))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Successfully stored content: {content_id}")
            return {
                'success': True,
                'content_id': content_id,
                'chunks': processed_content.topics,  # Use topics as chunks for now
                'size_bytes': len(processed_content.processed_content.encode('utf-8'))
            }
            
        except Exception as e:
            logger.error(f"Error storing content {processed_content.content_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'chunks': [],
                'size_bytes': 0
            }
    
    async def retrieve_content(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve content by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get main content record
            cursor.execute('SELECT * FROM content WHERE id = ?', (content_id,))
            content_row = cursor.fetchone()
            
            if not content_row:
                return None
            
            # Load content file
            content_file_path = content_row['file_path']
            if os.path.exists(content_file_path):
                with open(content_file_path, 'r', encoding='utf-8') as f:
                    content_data = json.load(f)
            else:
                content_data = {}
            
            # Get related data
            cursor.execute('SELECT * FROM keywords WHERE content_id = ?', (content_id,))
            keywords = [row['keyword'] for row in cursor.fetchall()]
            
            cursor.execute('SELECT * FROM entities WHERE content_id = ?', (content_id,))
            entities = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute('SELECT * FROM relationships WHERE content_id = ?', (content_id,))
            relationships = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute('SELECT * FROM topics WHERE content_id = ?', (content_id,))
            topics = [row['topic'] for row in cursor.fetchall()]
            
            cursor.execute('SELECT * FROM quality_issues WHERE content_id = ?', (content_id,))
            quality_issues = [row['description'] for row in cursor.fetchall()]
            
            conn.close()
            
            # Combine all data
            result = {
                'id': content_id,
                'title': content_row['title'],
                'content_type': content_row['content_type'],
                'source': content_row['source'],
                'content': content_data.get('processed_content', ''),
                'original_content': content_data.get('original_content', ''),
                'summary': content_data.get('summary', ''),
                'keywords': keywords,
                'entities': entities,
                'relationships': relationships,
                'topics': topics,
                'quality_score': content_row['quality_score'],
                'quality_level': content_row['quality_level'],
                'quality_issues': quality_issues,
                'created_time': content_row['created_time'],
                'modified_time': content_row['modified_time'],
                'metadata': json.loads(content_row['metadata']) if content_row['metadata'] else {}
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving content {content_id}: {e}")
            return None
    
    async def search_content(self, query: str, filters: Optional[Dict[str, Any]] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Search content with optional filters"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Build search query
            where_clauses = []
            params = []
            
            if query:
                # Simple text search in title and keywords
                where_clauses.append('''
                (content.title LIKE ? OR 
                 content.id IN (SELECT content_id FROM keywords WHERE keyword LIKE ?))
                ''')
                params.extend([f'%{query}%', f'%{query}%'])
            
            if filters:
                if 'content_type' in filters:
                    where_clauses.append('content.content_type = ?')
                    params.append(filters['content_type'])
                
                if 'source' in filters:
                    where_clauses.append('content.source = ?')
                    params.append(filters['source'])
                
                if 'quality_level' in filters:
                    where_clauses.append('content.quality_level = ?')
                    params.append(filters['quality_level'])
                
                if 'min_quality_score' in filters:
                    where_clauses.append('content.quality_score >= ?')
                    params.append(filters['min_quality_score'])
                
                if 'topic' in filters:
                    where_clauses.append('content.id IN (SELECT content_id FROM topics WHERE topic = ?)')
                    params.append(filters['topic'])
            
            where_clause = ' AND '.join(where_clauses) if where_clauses else '1=1'
            
            sql = f'''
            SELECT DISTINCT content.* 
            FROM content 
            WHERE {where_clause}
            ORDER BY content.quality_score DESC, content.processing_time DESC
            LIMIT ?
            '''
            
            params.append(limit)
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                result = {
                    'id': row['id'],
                    'title': row['title'],
                    'content_type': row['content_type'],
                    'source': row['source'],
                    'quality_score': row['quality_score'],
                    'quality_level': row['quality_level'],
                    'word_count': row['word_count'],
                    'created_time': row['created_time'],
                    'modified_time': row['modified_time'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else {}
                }
                results.append(result)
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Error searching content: {e}")
            return []
    
    async def get_content_statistics(self) -> Dict[str, Any]:
        """Get statistics about stored content"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total content count
            cursor.execute('SELECT COUNT(*) FROM content')
            total_content = cursor.fetchone()[0]
            
            # Content by type
            cursor.execute('SELECT content_type, COUNT(*) FROM content GROUP BY content_type')
            content_by_type = dict(cursor.fetchall())
            
            # Content by source
            cursor.execute('SELECT source, COUNT(*) FROM content GROUP BY source ORDER BY COUNT(*) DESC LIMIT 10')
            content_by_source = dict(cursor.fetchall())
            
            # Quality distribution
            cursor.execute('SELECT quality_level, COUNT(*) FROM content GROUP BY quality_level')
            quality_distribution = dict(cursor.fetchall())
            
            # Average quality score
            cursor.execute('SELECT AVG(quality_score) FROM content')
            avg_quality = cursor.fetchone()[0] or 0
            
            # Total word count
            cursor.execute('SELECT SUM(word_count) FROM content')
            total_words = cursor.fetchone()[0] or 0
            
            # Top keywords
            cursor.execute('''
            SELECT keyword, COUNT(*) as frequency 
            FROM keywords 
            GROUP BY keyword 
            ORDER BY frequency DESC 
            LIMIT 20
            ''')
            top_keywords = dict(cursor.fetchall())
            
            # Top topics
            cursor.execute('''
            SELECT topic, COUNT(*) as frequency 
            FROM topics 
            GROUP BY topic 
            ORDER BY frequency DESC 
            LIMIT 15
            ''')
            top_topics = dict(cursor.fetchall())
            
            # Recent content
            cursor.execute('''
            SELECT DATE(processing_time) as date, COUNT(*) 
            FROM content 
            WHERE processing_time >= datetime('now', '-30 days')
            GROUP BY DATE(processing_time)
            ORDER BY date DESC
            ''')
            recent_activity = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'total_content': total_content,
                'content_by_type': content_by_type,
                'content_by_source': content_by_source,
                'quality_distribution': quality_distribution,
                'average_quality_score': round(avg_quality, 2),
                'total_words': total_words,
                'top_keywords': top_keywords,
                'top_topics': top_topics,
                'recent_activity': recent_activity,
                'storage_path': self.storage_path,
                'database_size': os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting content statistics: {e}")
            return {}
    
    async def create_collection(self, name: str, description: str = "") -> str:
        """Create a new content collection"""
        try:
            collection_id = f"collection_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO collections (id, name, description, created_time, metadata)
            VALUES (?, ?, ?, ?, ?)
            ''', (collection_id, name, description, datetime.now().isoformat(), '{}'))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Created collection: {collection_id}")
            return collection_id
            
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            return ""
    
    async def add_to_collection(self, collection_id: str, content_ids: List[str]) -> bool:
        """Add content to a collection"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for content_id in content_ids:
                cursor.execute('''
                INSERT OR REPLACE INTO collection_memberships (collection_id, content_id, added_time)
                VALUES (?, ?, ?)
                ''', (collection_id, content_id, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Added {len(content_ids)} items to collection {collection_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding to collection: {e}")
            return False
    
    async def export_content(self, output_path: str, format: str = 'json') -> bool:
        """Export all content to file"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM content ORDER BY processing_time DESC')
            rows = cursor.fetchall()
            
            export_data = []
            for row in rows:
                content_data = dict(row)
                content_data['metadata'] = json.loads(content_data['metadata']) if content_data['metadata'] else {}
                export_data.append(content_data)
            
            conn.close()
            
            if format.lower() == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
            else:
                raise ValueError(f"Unsupported export format: {format}")
            
            logger.info(f"Exported {len(export_data)} content items to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting content: {e}")
            return False
    
    async def cleanup_storage(self, days_old: int = 30, quality_threshold: float = 2.0) -> int:
        """Clean up low-quality or old content"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Find content to delete
            cursor.execute('''
            SELECT id, file_path FROM content 
            WHERE quality_score < ? 
            OR (processing_time < datetime('now', '-{} days') AND quality_score < 5.0)
            '''.format(days_old), (quality_threshold,))
            
            to_delete = cursor.fetchall()
            
            deleted_count = 0
            for content_id, file_path in to_delete:
                # Delete from database
                cursor.execute('DELETE FROM content WHERE id = ?', (content_id,))
                cursor.execute('DELETE FROM keywords WHERE content_id = ?', (content_id,))
                cursor.execute('DELETE FROM entities WHERE content_id = ?', (content_id,))
                cursor.execute('DELETE FROM relationships WHERE content_id = ?', (content_id,))
                cursor.execute('DELETE FROM topics WHERE content_id = ?', (content_id,))
                cursor.execute('DELETE FROM quality_issues WHERE content_id = ?', (content_id,))
                
                # Delete content file
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                
                deleted_count += 1
            
            conn.commit()
            conn.close()
            
            logger.info(f"Cleaned up {deleted_count} content items")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return 0
    
    async def search_similar(self, query: str, collection_name: str = None, limit: int = 10, 
                           min_similarity: float = 0.5, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search for similar content using the existing search_content method"""
        try:
            # Use the existing search_content method which has more sophisticated search capabilities
            search_filters = filters or {}
            if collection_name:
                search_filters['content_type'] = collection_name
                
            return await self.search_content(query, filters=search_filters, limit=limit)
        except Exception as e:
            logger.error(f"Error in search_similar: {e}")
            return []
    
    async def get_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total content count
            cursor.execute("SELECT COUNT(*) FROM content")
            total_content = cursor.fetchone()[0]
            
            # Get content by type
            cursor.execute("SELECT content_type, COUNT(*) FROM content GROUP BY content_type")
            content_by_type = dict(cursor.fetchall())
            
            # Get recent content count (last 30 days)
            cursor.execute("SELECT COUNT(*) FROM content WHERE created_time > datetime('now', '-30 days')")
            recent_content = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_content': total_content,
                'content_by_type': content_by_type,
                'recent_content': recent_content,
                'storage_path': self.storage_path,
                'user_id': user_id
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                'total_content': 0,
                'content_by_type': {},
                'recent_content': 0,
                'storage_path': self.storage_path,
                'error': str(e)
            }
    
    async def list_collections(self, user_id: str = None) -> List[str]:
        """List available collections/content types"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT DISTINCT content_type FROM content WHERE content_type IS NOT NULL")
            collections = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            return collections
            
        except Exception as e:
            logger.error(f"Error listing collections: {e}")
            return []
    
    async def health_check(self) -> bool:
        """Check if the storage system is healthy"""
        try:
            # Test database connection
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM content LIMIT 1")
            cursor.fetchone()
            conn.close()
            
            # Check if storage directories exist
            return (
                os.path.exists(self.storage_path) and
                os.path.exists(self.content_path) and
                os.path.exists(self.embeddings_path)
            )
        except Exception as e:
            logger.error(f"Storage health check failed: {e}")
            return False
