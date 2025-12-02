"""
Application Data Collector - Extract knowledge from installed applications
"""
import os
import sqlite3
import json
import plistlib
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import subprocess

logger = logging.getLogger(__name__)

class ApplicationDataCollector:
    """Collect data from various applications on the system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.home_dir = os.path.expanduser("~")
        self.applications = config.get('applications', {})
    
    async def collect_all_applications(self) -> List[Dict[str, Any]]:
        """Collect data from all configured applications"""
        all_data = []
        
        tasks = []
        if self.applications.get('notes', {}).get('enabled', True):
            tasks.append(self.collect_apple_notes())
        if self.applications.get('safari', {}).get('enabled', True):
            tasks.append(self.collect_safari_data())
        if self.applications.get('chrome', {}).get('enabled', True):
            tasks.append(self.collect_chrome_data())
        if self.applications.get('obsidian', {}).get('enabled', True):
            tasks.append(self.collect_obsidian_data())
        if self.applications.get('notion', {}).get('enabled', True):
            tasks.append(self.collect_notion_data())
        if self.applications.get('bear', {}).get('enabled', True):
            tasks.append(self.collect_bear_notes())
        if self.applications.get('readwise', {}).get('enabled', True):
            tasks.append(self.collect_readwise_data())
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, list):
                    all_data.extend(result)
                elif isinstance(result, Exception):
                    logger.error(f"Application collection error: {result}")
        
        return all_data
    
    async def collect_apple_notes(self) -> List[Dict[str, Any]]:
        """Collect notes from Apple Notes app"""
        try:
            notes_data = []
            
            # Apple Notes are stored in a SQLite database
            notes_db_path = os.path.join(
                self.home_dir, 
                "Library/Group Containers/group.com.apple.notes/NoteStore.sqlite"
            )
            
            if not os.path.exists(notes_db_path):
                logger.warning("Apple Notes database not found")
                return []
            
            conn = sqlite3.connect(notes_db_path)
            cursor = conn.cursor()
            
            # Query to get notes with their content
            query = """
            SELECT 
                ZNOTE.Z_PK as note_id,
                ZNOTE.ZTITLE as title,
                ZNOTE.ZCREATIONDATE as created,
                ZNOTE.ZMODIFICATIONDATE as modified,
                ZNOTEBODY.ZDATA as content
            FROM ZNOTE
            LEFT JOIN ZNOTEBODY ON ZNOTE.Z_PK = ZNOTEBODY.ZNOTE
            WHERE ZNOTE.ZTRASHED = 0
            ORDER BY ZNOTE.ZMODIFICATIONDATE DESC
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            for row in rows:
                note_id, title, created, modified, content_data = row
                
                # Convert Apple's timestamp format (seconds since 2001-01-01)
                if created:
                    created_date = datetime(2001, 1, 1) + timedelta(seconds=created)
                else:
                    created_date = None
                
                if modified:
                    modified_date = datetime(2001, 1, 1) + timedelta(seconds=modified)
                else:
                    modified_date = None
                
                # Extract text content from binary data
                content_text = ""
                if content_data:
                    try:
                        # Apple Notes content is stored in a protobuf-like format
                        # This is a simplified extraction
                        content_text = content_data.decode('utf-8', errors='ignore')
                        # Clean up the content
                        content_text = ''.join(char for char in content_text if char.isprintable() or char.isspace())
                    except:
                        content_text = str(content_data)[:1000]  # Fallback
                
                if title or content_text:
                    notes_data.append({
                        'source': 'apple_notes',
                        'id': f"apple_note_{note_id}",
                        'title': title or "Untitled Note",
                        'content': content_text,
                        'created_time': created_date.isoformat() if created_date else None,
                        'modified_time': modified_date.isoformat() if modified_date else None,
                        'collection_time': datetime.now().isoformat(),
                        'type': 'note',
                        'priority_score': self._calculate_content_priority(content_text)
                    })
            
            conn.close()
            logger.info(f"Collected {len(notes_data)} Apple Notes")
            return notes_data
            
        except Exception as e:
            logger.error(f"Apple Notes collection failed: {e}")
            return []
    
    async def collect_safari_data(self) -> List[Dict[str, Any]]:
        """Collect bookmarks and reading list from Safari"""
        try:
            safari_data = []
            
            # Safari bookmarks
            bookmarks_path = os.path.join(self.home_dir, "Library/Safari/Bookmarks.plist")
            if os.path.exists(bookmarks_path):
                with open(bookmarks_path, 'rb') as f:
                    bookmarks = plistlib.load(f)
                
                def extract_bookmarks(item, folder_path=""):
                    if isinstance(item, dict):
                        if item.get('WebBookmarkType') == 'WebBookmarkTypeLeaf':
                            url = item.get('URLString', '')
                            title = item.get('URIDictionary', {}).get('title', url)
                            
                            safari_data.append({
                                'source': 'safari_bookmarks',
                                'id': f"safari_bookmark_{hash(url)}",
                                'title': title,
                                'url': url,
                                'folder': folder_path,
                                'type': 'bookmark',
                                'collection_time': datetime.now().isoformat(),
                                'priority_score': 2.0
                            })
                        
                        elif item.get('WebBookmarkType') == 'WebBookmarkTypeList':
                            folder_name = item.get('Title', 'Unnamed Folder')
                            current_path = f"{folder_path}/{folder_name}" if folder_path else folder_name
                            
                            children = item.get('Children', [])
                            for child in children:
                                extract_bookmarks(child, current_path)
                
                if 'Children' in bookmarks:
                    for child in bookmarks['Children']:
                        extract_bookmarks(child)
            
            # Safari Reading List
            reading_list_path = os.path.join(self.home_dir, "Library/Safari/ReadingList.plist")
            if os.path.exists(reading_list_path):
                with open(reading_list_path, 'rb') as f:
                    reading_list = plistlib.load(f)
                
                for item in reading_list.get('ReadingList', []):
                    url = item.get('URLString', '')
                    title = item.get('Title', url)
                    preview_text = item.get('PreviewText', '')
                    date_added = item.get('DateAdded')
                    
                    safari_data.append({
                        'source': 'safari_reading_list',
                        'id': f"safari_reading_{hash(url)}",
                        'title': title,
                        'url': url,
                        'content': preview_text,
                        'date_added': date_added.isoformat() if date_added else None,
                        'type': 'reading_list',
                        'collection_time': datetime.now().isoformat(),
                        'priority_score': 3.0  # Reading list items are high priority
                    })
            
            logger.info(f"Collected {len(safari_data)} Safari items")
            return safari_data
            
        except Exception as e:
            logger.error(f"Safari data collection failed: {e}")
            return []
    
    async def collect_chrome_data(self) -> List[Dict[str, Any]]:
        """Collect bookmarks and history from Chrome"""
        try:
            chrome_data = []
            
            # Chrome profile directory
            chrome_dir = os.path.join(self.home_dir, "Library/Application Support/Google/Chrome/Default")
            
            # Chrome bookmarks
            bookmarks_path = os.path.join(chrome_dir, "Bookmarks")
            if os.path.exists(bookmarks_path):
                with open(bookmarks_path, 'r', encoding='utf-8') as f:
                    bookmarks = json.load(f)
                
                def extract_chrome_bookmarks(node, folder_path=""):
                    if node.get('type') == 'url':
                        chrome_data.append({
                            'source': 'chrome_bookmarks',
                            'id': f"chrome_bookmark_{node.get('id')}",
                            'title': node.get('name', ''),
                            'url': node.get('url', ''),
                            'folder': folder_path,
                            'date_added': node.get('date_added'),
                            'type': 'bookmark',
                            'collection_time': datetime.now().isoformat(),
                            'priority_score': 2.0
                        })
                    
                    elif node.get('type') == 'folder':
                        folder_name = node.get('name', 'Unnamed')
                        current_path = f"{folder_path}/{folder_name}" if folder_path else folder_name
                        
                        for child in node.get('children', []):
                            extract_chrome_bookmarks(child, current_path)
                
                roots = bookmarks.get('roots', {})
                for root_name, root_data in roots.items():
                    if isinstance(root_data, dict) and 'children' in root_data:
                        for child in root_data['children']:
                            extract_chrome_bookmarks(child, root_name)
            
            logger.info(f"Collected {len(chrome_data)} Chrome items")
            return chrome_data
            
        except Exception as e:
            logger.error(f"Chrome data collection failed: {e}")
            return []
    
    async def collect_obsidian_data(self) -> List[Dict[str, Any]]:
        """Collect notes from Obsidian vaults"""
        try:
            obsidian_data = []
            
            # Look for Obsidian vaults in common locations
            potential_locations = [
                os.path.join(self.home_dir, "Documents/Obsidian"),
                os.path.join(self.home_dir, "Library/Mobile Documents/iCloud~md~obsidian/Documents"),
                os.path.join(self.home_dir, "obsidian-vaults")
            ]
            
            for location in potential_locations:
                if os.path.exists(location):
                    for vault_name in os.listdir(location):
                        vault_path = os.path.join(location, vault_name)
                        if os.path.isdir(vault_path):
                            vault_notes = await self._collect_obsidian_vault(vault_path, vault_name)
                            obsidian_data.extend(vault_notes)
            
            logger.info(f"Collected {len(obsidian_data)} Obsidian notes")
            return obsidian_data
            
        except Exception as e:
            logger.error(f"Obsidian data collection failed: {e}")
            return []
    
    async def _collect_obsidian_vault(self, vault_path: str, vault_name: str) -> List[Dict[str, Any]]:
        """Collect all markdown files from an Obsidian vault"""
        vault_data = []
        
        for root, dirs, files in os.walk(vault_path):
            # Skip .obsidian directory
            if '.obsidian' in dirs:
                dirs.remove('.obsidian')
            
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        stat = os.stat(file_path)
                        relative_path = os.path.relpath(file_path, vault_path)
                        
                        vault_data.append({
                            'source': 'obsidian',
                            'id': f"obsidian_{vault_name}_{hash(relative_path)}",
                            'title': file.replace('.md', ''),
                            'content': content,
                            'vault': vault_name,
                            'path': relative_path,
                            'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                            'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            'collection_time': datetime.now().isoformat(),
                            'type': 'note',
                            'priority_score': self._calculate_content_priority(content)
                        })
                    except Exception as e:
                        logger.error(f"Error reading Obsidian file {file_path}: {e}")
        
        return vault_data
    
    async def collect_bear_notes(self) -> List[Dict[str, Any]]:
        """Collect notes from Bear app"""
        try:
            bear_data = []
            
            # Bear notes database
            bear_db_path = os.path.join(
                self.home_dir,
                "Library/Group Containers/9K33E3U3T4.net.shinyfrog.bear/Application Data/database.sqlite"
            )
            
            if not os.path.exists(bear_db_path):
                logger.warning("Bear database not found")
                return []
            
            conn = sqlite3.connect(bear_db_path)
            cursor = conn.cursor()
            
            query = """
            SELECT 
                ZUNIQUEIDENTIFIER as id,
                ZTITLE as title,
                ZTEXT as content,
                ZCREATIONDATE as created,
                ZMODIFICATIONDATE as modified,
                ZTRASHED as trashed
            FROM ZSFNOTE
            WHERE ZTRASHED = 0
            ORDER BY ZMODIFICATIONDATE DESC
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            for row in rows:
                note_id, title, content, created, modified, trashed = row
                
                # Convert timestamps
                created_date = datetime(2001, 1, 1) + timedelta(seconds=created) if created else None
                modified_date = datetime(2001, 1, 1) + timedelta(seconds=modified) if modified else None
                
                bear_data.append({
                    'source': 'bear_notes',
                    'id': f"bear_{note_id}",
                    'title': title or "Untitled",
                    'content': content or "",
                    'created_time': created_date.isoformat() if created_date else None,
                    'modified_time': modified_date.isoformat() if modified_date else None,
                    'collection_time': datetime.now().isoformat(),
                    'type': 'note',
                    'priority_score': self._calculate_content_priority(content or "")
                })
            
            conn.close()
            logger.info(f"Collected {len(bear_data)} Bear notes")
            return bear_data
            
        except Exception as e:
            logger.error(f"Bear notes collection failed: {e}")
            return []
    
    async def collect_notion_data(self) -> List[Dict[str, Any]]:
        """Collect data from Notion (requires API key)"""
        # This would require Notion API integration
        # For now, return empty list
        logger.info("Notion collection requires API setup - skipping for now")
        return []
    
    async def collect_readwise_data(self) -> List[Dict[str, Any]]:
        """Collect highlights and notes from Readwise"""
        # This would require Readwise API integration
        # For now, return empty list
        logger.info("Readwise collection requires API setup - skipping for now")
        return []
    
    def _calculate_content_priority(self, content: str) -> float:
        """Calculate priority score based on content characteristics"""
        if not content:
            return 0.0
        
        score = 1.0
        
        # Length factor
        if len(content) > 1000:
            score += 2.0
        elif len(content) > 500:
            score += 1.5
        elif len(content) > 100:
            score += 1.0
        
        # Content quality indicators
        content_lower = content.lower()
        
        # Technical/academic content
        technical_keywords = ['algorithm', 'analysis', 'research', 'study', 'method', 'framework', 'theory']
        if any(keyword in content_lower for keyword in technical_keywords):
            score += 1.5
        
        # Code or technical documentation
        if any(marker in content for marker in ['```', 'def ', 'function', 'class ', 'import ', 'export']):
            score += 2.0
        
        # URLs or references
        if 'http' in content_lower or 'www.' in content_lower:
            score += 0.5
        
        # Structured content (lists, headers)
        if content.count('\n-') > 2 or content.count('\n#') > 1:
            score += 1.0
        
        return score
