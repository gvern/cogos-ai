"""
Cloud Drive Collector - Sync and analyze files from Google Drive, Dropbox, iCloud, etc.
"""
import os
import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

try:
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    # Define a placeholder for type hints when Google libraries aren't available
    Credentials = Any

try:
    import dropbox
    DROPBOX_AVAILABLE = True
except ImportError:
    DROPBOX_AVAILABLE = False

logger = logging.getLogger(__name__)

class CloudDriveCollector:
    """Collect and sync files from various cloud storage providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.supported_formats = config.get('supported_formats', [
            'pdf', 'docx', 'doc', 'txt', 'md', 'rtf',
            'pptx', 'ppt', 'xlsx', 'xls', 'csv',
            'jpg', 'jpeg', 'png', 'tiff', 'bmp',
            'mp3', 'wav', 'mp4', 'mov', 'avi'
        ])
        self.sync_directory = config.get('sync_directory', '/tmp/cloud_sync')
        os.makedirs(self.sync_directory, exist_ok=True)
    
    async def collect_all_drives(self) -> List[Dict[str, Any]]:
        """Collect files from all configured cloud drives"""
        all_files = []
        
        tasks = []
        if self.config.get('google_drive', {}).get('enabled', False):
            tasks.append(self.collect_google_drive())
        if self.config.get('dropbox', {}).get('enabled', False):
            tasks.append(self.collect_dropbox())
        if self.config.get('icloud', {}).get('enabled', False):
            tasks.append(self.collect_icloud())
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, list):
                    all_files.extend(result)
                elif isinstance(result, Exception):
                    logger.error(f"Cloud collection error: {result}")
        
        return all_files
    
    async def collect_google_drive(self) -> List[Dict[str, Any]]:
        """Collect files from Google Drive"""
        if not GOOGLE_AVAILABLE:
            logger.warning("Google API libraries not available. Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
            return []
        
        try:
            creds = self._get_google_credentials()
            if not creds:
                return []
            
            service = build('drive', 'v3', credentials=creds)
            
            # Query for all files with supported formats
            query_parts = []
            for fmt in self.supported_formats:
                query_parts.append(f"name contains '.{fmt}'")
            query = ' or '.join(query_parts)
            
            results = service.files().list(
                q=query,
                fields="nextPageToken, files(id, name, mimeType, size, createdTime, modifiedTime, parents, webViewLink)",
                pageSize=1000
            ).execute()
            
            files = results.get('files', [])
            collected_files = []
            
            for file_info in files:
                try:
                    # Download file content
                    file_content = self._download_google_drive_file(service, file_info)
                    if file_content:
                        collected_files.append({
                            'source': 'google_drive',
                            'file_id': file_info['id'],
                            'name': file_info['name'],
                            'path': f"google_drive/{file_info['name']}",
                            'mime_type': file_info.get('mimeType'),
                            'size': int(file_info.get('size', 0)),
                            'created_time': file_info.get('createdTime'),
                            'modified_time': file_info.get('modifiedTime'),
                            'content': file_content,
                            'web_link': file_info.get('webViewLink'),
                            'collection_time': datetime.now().isoformat(),
                            'priority_score': self._calculate_priority_score(file_info)
                        })
                except Exception as e:
                    logger.error(f"Error downloading Google Drive file {file_info['name']}: {e}")
            
            logger.info(f"Collected {len(collected_files)} files from Google Drive")
            return collected_files
            
        except Exception as e:
            logger.error(f"Google Drive collection failed: {e}")
            return []
    
    async def collect_dropbox(self) -> List[Dict[str, Any]]:
        """Collect files from Dropbox"""
        if not DROPBOX_AVAILABLE:
            logger.warning("Dropbox library not available. Install with: pip install dropbox")
            return []
        
        try:
            access_token = self.config.get('dropbox', {}).get('access_token')
            if not access_token:
                logger.warning("Dropbox access token not configured")
                return []
            
            dbx = dropbox.Dropbox(access_token)
            collected_files = []
            
            # List all files recursively
            result = dbx.files_list_folder('', recursive=True)
            
            while True:
                for entry in result.entries:
                    if isinstance(entry, dropbox.files.FileMetadata):
                        # Check if file format is supported
                        file_ext = entry.name.split('.')[-1].lower()
                        if file_ext in self.supported_formats:
                            try:
                                # Download file content
                                _, response = dbx.files_download(entry.path_lower)
                                content = response.content
                                
                                collected_files.append({
                                    'source': 'dropbox',
                                    'file_id': entry.id,
                                    'name': entry.name,
                                    'path': entry.path_lower,
                                    'size': entry.size,
                                    'modified_time': entry.server_modified.isoformat(),
                                    'content': content,
                                    'collection_time': datetime.now().isoformat(),
                                    'priority_score': self._calculate_priority_score({
                                        'name': entry.name,
                                        'size': entry.size,
                                        'modifiedTime': entry.server_modified.isoformat()
                                    })
                                })
                            except Exception as e:
                                logger.error(f"Error downloading Dropbox file {entry.name}: {e}")
                
                if not result.has_more:
                    break
                result = dbx.files_list_folder_continue(result.cursor)
            
            logger.info(f"Collected {len(collected_files)} files from Dropbox")
            return collected_files
            
        except Exception as e:
            logger.error(f"Dropbox collection failed: {e}")
            return []
    
    async def collect_icloud(self) -> List[Dict[str, Any]]:
        """Collect files from iCloud Drive"""
        # iCloud requires accessing the local sync folder
        try:
            icloud_path = os.path.expanduser("~/Library/Mobile Documents/com~apple~CloudDocs")
            if not os.path.exists(icloud_path):
                logger.warning("iCloud Drive folder not found")
                return []
            
            collected_files = []
            
            # Walk through iCloud directory
            for root, dirs, files in os.walk(icloud_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = file.split('.')[-1].lower()
                    
                    if file_ext in self.supported_formats:
                        try:
                            stat = os.stat(file_path)
                            with open(file_path, 'rb') as f:
                                content = f.read()
                            
                            relative_path = os.path.relpath(file_path, icloud_path)
                            
                            collected_files.append({
                                'source': 'icloud',
                                'file_id': f"icloud_{hash(file_path)}",
                                'name': file,
                                'path': f"icloud/{relative_path}",
                                'size': stat.st_size,
                                'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                                'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                                'content': content,
                                'collection_time': datetime.now().isoformat(),
                                'priority_score': self._calculate_priority_score({
                                    'name': file,
                                    'size': stat.st_size,
                                    'modifiedTime': datetime.fromtimestamp(stat.st_mtime).isoformat()
                                })
                            })
                        except Exception as e:
                            logger.error(f"Error reading iCloud file {file_path}: {e}")
            
            logger.info(f"Collected {len(collected_files)} files from iCloud")
            return collected_files
            
        except Exception as e:
            logger.error(f"iCloud collection failed: {e}")
            return []
    
    def _get_google_credentials(self) -> Optional[Credentials]:
        """Get Google Drive API credentials"""
        creds = None
        token_path = self.config.get('google_drive', {}).get('token_path', 'token.json')
        credentials_path = self.config.get('google_drive', {}).get('credentials_path', 'credentials.json')
        
        # Load existing token
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path)
        
        # If no valid credentials, run OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(credentials_path):
                    logger.error(f"Google credentials file not found: {credentials_path}")
                    return None
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, ['https://www.googleapis.com/auth/drive.readonly'])
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        return creds
    
    def _download_google_drive_file(self, service, file_info: Dict) -> Optional[bytes]:
        """Download file content from Google Drive"""
        try:
            # Handle Google Workspace files (Docs, Sheets, etc.)
            mime_type = file_info.get('mimeType', '')
            if mime_type.startswith('application/vnd.google-apps'):
                # Export Google Workspace files
                export_mime_types = {
                    'application/vnd.google-apps.document': 'application/pdf',
                    'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'application/vnd.google-apps.presentation': 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
                }
                
                export_mime = export_mime_types.get(mime_type)
                if export_mime:
                    request = service.files().export_media(fileId=file_info['id'], mimeType=export_mime)
                    return request.execute()
            else:
                # Download regular files
                request = service.files().get_media(fileId=file_info['id'])
                return request.execute()
        except Exception as e:
            logger.error(f"Error downloading file {file_info['name']}: {e}")
            return None
    
    def _calculate_priority_score(self, file_info: Dict) -> float:
        """Calculate priority score for file based on various factors"""
        score = 0.0
        
        # File extension priority
        name = file_info.get('name', '').lower()
        if any(ext in name for ext in ['pdf', 'docx', 'doc']):
            score += 3.0
        elif any(ext in name for ext in ['md', 'txt', 'rtf']):
            score += 2.5
        elif any(ext in name for ext in ['pptx', 'xlsx']):
            score += 2.0
        else:
            score += 1.0
        
        # Size factor (prefer substantial files)
        size = file_info.get('size', 0)
        if isinstance(size, str):
            size = int(size) if size.isdigit() else 0
        
        if size > 1024 * 1024:  # > 1MB
            score += 2.0
        elif size > 100 * 1024:  # > 100KB
            score += 1.0
        
        # Recent modification bonus
        modified_time = file_info.get('modifiedTime')
        if modified_time:
            try:
                from datetime import datetime, timedelta
                if isinstance(modified_time, str):
                    mod_date = datetime.fromisoformat(modified_time.replace('Z', '+00:00'))
                else:
                    mod_date = modified_time
                
                days_old = (datetime.now().replace(tzinfo=mod_date.tzinfo) - mod_date).days
                if days_old < 30:
                    score += 1.5
                elif days_old < 90:
                    score += 1.0
                elif days_old < 365:
                    score += 0.5
            except:
                pass
        
        return score
