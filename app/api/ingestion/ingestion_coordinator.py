"""
Ingestion Coordinator - Orchestrate the complete knowledge collection pipeline
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import os

from .collectors.file_system_crawler import FileSystemCollector
from .collectors.digital_library_collector import DigitalLibraryCollector
from .collectors.cloud_drive_collector import CloudDriveCollector
from .collectors.application_data_collector import ApplicationDataCollector
from .processors.content_processor import ContentProcessor
from .quality_control.quality_controller import QualityController, QualityLevel
from .storage.storage_manager import StorageManager

logger = logging.getLogger(__name__)

class IngestionCoordinator:
    """Main coordinator for the knowledge ingestion pipeline"""
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        
        # Initialize components
        file_system_config = self.config.get('file_system', {})
        base_path = file_system_config.get('base_path', '/Users/gustavevernay')
        self.file_collector = FileSystemCollector(base_path)
        self.library_collector = DigitalLibraryCollector()  # No config needed
        self.cloud_collector = CloudDriveCollector(self.config.get('cloud_drives', {}))
        self.app_collector = ApplicationDataCollector(self.config.get('applications', {}))
        self.content_processor = ContentProcessor(self.config.get('processing', {}))
        self.quality_controller = QualityController(self.config.get('quality_control', {}))
        self.storage_manager = StorageManager(self.config.get('storage', {}))
        
        # Job tracking
        self.active_jobs = {}
        self.completed_jobs = {}
        
        # Pipeline statistics
        self.stats = {
            'start_time': None,
            'end_time': None,
            'total_collected': 0,
            'total_processed': 0,
            'total_stored': 0,
            'total_rejected': 0,
            'collection_stats': {},
            'quality_stats': {},
            'errors': []
        }
    
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            'file_system': {
                'enabled': True,
                'scan_paths': [os.path.expanduser("~")],
                'exclude_patterns': [
                    '.git', '.svn', 'node_modules', '__pycache__', '.DS_Store',
                    'Library/Caches', 'Library/Logs', '.Trash'
                ],
                'max_file_size': 100 * 1024 * 1024,  # 100MB
                'supported_formats': [
                    'pdf', 'docx', 'doc', 'txt', 'md', 'rtf', 'odt',
                    'pptx', 'ppt', 'odp', 'xlsx', 'xls', 'ods', 'csv',
                    'html', 'htm', 'xml', 'json', 'yaml', 'yml',
                    'py', 'js', 'ts', 'java', 'cpp', 'c', 'h',
                    'jpg', 'jpeg', 'png', 'gif', 'tiff', 'bmp',
                    'mp3', 'wav', 'mp4', 'mov', 'avi'
                ]
            },
            'digital_library': {
                'enabled': True,
                'photo_scan_directories': [
                    os.path.expanduser("~/Pictures/Books"),
                    os.path.expanduser("~/Desktop/BookPhotos")
                ],
                'api_keys': {
                    'google_books': '',
                    'open_library': '',
                    'gallica': ''
                },
                'download_full_text': True,
                'max_books_per_session': 50
            },
            'cloud_drives': {
                'enabled': True,
                'google_drive': {
                    'enabled': False,
                    'credentials_path': 'credentials.json',
                    'token_path': 'token.json'
                },
                'dropbox': {
                    'enabled': False,
                    'access_token': ''
                },
                'icloud': {
                    'enabled': True
                }
            },
            'applications': {
                'enabled': True,
                'notes': {'enabled': True},
                'safari': {'enabled': True},
                'chrome': {'enabled': True},
                'obsidian': {'enabled': True},
                'bear': {'enabled': True},
                'notion': {'enabled': False},
                'readwise': {'enabled': False}
            },
            'processing': {
                'min_content_length': 50,
                'max_summary_length': 200,
                'batch_size': 10,
                'parallel_processing': True
            },
            'quality_control': {
                'min_quality_score': 3.0,
                'duplicate_threshold': 0.85,
                'min_content_length': 50,
                'max_content_length': 1000000
            },
            'storage': {
                'storage_path': os.path.expanduser("~/cogos_knowledge_storage"),
                'backup_enabled': True,
                'compression_enabled': False
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    file_config = json.load(f)
                # Merge with defaults
                for key, value in file_config.items():
                    if isinstance(value, dict) and key in default_config:
                        default_config[key].update(value)
                    else:
                        default_config[key] = value
            except Exception as e:
                logger.warning(f"Error loading config file {config_path}: {e}")
        
        return default_config
    
    async def run_full_ingestion(self) -> Dict[str, Any]:
        """Run the complete knowledge ingestion pipeline"""
        logger.info("Starting comprehensive knowledge ingestion pipeline")
        self.stats['start_time'] = datetime.now().isoformat()
        
        try:
            # Phase 1: Collection
            logger.info("Phase 1: Collecting content from all sources")
            collected_content = await self._collect_all_content()
            self.stats['total_collected'] = len(collected_content)
            logger.info(f"Collected {len(collected_content)} items")
            
            # Phase 2: Processing
            logger.info("Phase 2: Processing and analyzing content")
            processed_content = await self._process_content_batch(collected_content)
            self.stats['total_processed'] = len(processed_content)
            logger.info(f"Processed {len(processed_content)} items")
            
            # Phase 3: Quality Control
            logger.info("Phase 3: Quality validation and filtering")
            quality_reports = await self._validate_content_quality(processed_content)
            approved_content = self._filter_by_quality(processed_content, quality_reports)
            self.stats['total_rejected'] = len(processed_content) - len(approved_content)
            logger.info(f"Approved {len(approved_content)} items after quality control")
            
            # Phase 4: Storage
            logger.info("Phase 4: Storing approved content")
            stored_count = await self._store_approved_content(approved_content, quality_reports)
            self.stats['total_stored'] = stored_count
            logger.info(f"Successfully stored {stored_count} items")
            
            # Generate final report
            self.stats['end_time'] = datetime.now().isoformat()
            await self._generate_ingestion_report()
            
            logger.info("Knowledge ingestion pipeline completed successfully")
            return self.stats
            
        except Exception as e:
            logger.error(f"Ingestion pipeline failed: {e}")
            self.stats['errors'].append(str(e))
            self.stats['end_time'] = datetime.now().isoformat()
            return self.stats
    
    async def _collect_all_content(self) -> List[Dict[str, Any]]:
        """Collect content from all enabled sources"""
        all_content = []
        
        collection_tasks = []
        
        # File system collection
        if self.config['file_system']['enabled']:
            collection_tasks.append(('file_system', self.file_collector.scan_directories()))
        
        # Digital library collection
        if self.config['digital_library']['enabled']:
            collection_tasks.append(('digital_library', self.library_collector.collect_digital_books()))
        
        # Cloud drives collection
        if self.config['cloud_drives']['enabled']:
            collection_tasks.append(('cloud_drives', self.cloud_collector.collect_all_drives()))
        
        # Application data collection
        if self.config['applications']['enabled']:
            collection_tasks.append(('applications', self.app_collector.collect_all_applications()))
        
        # Run collections in parallel
        if collection_tasks:
            tasks = [task for _, task in collection_tasks]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, (source_name, _) in enumerate(collection_tasks):
                result = results[i]
                if isinstance(result, list):
                    all_content.extend(result)
                    self.stats['collection_stats'][source_name] = len(result)
                    logger.info(f"Collected {len(result)} items from {source_name}")
                elif isinstance(result, Exception):
                    logger.error(f"Collection failed for {source_name}: {result}")
                    self.stats['errors'].append(f"{source_name}: {result}")
                    self.stats['collection_stats'][source_name] = 0
        
        return all_content
    
    async def _process_content_batch(self, content_items: List[Dict[str, Any]]) -> List[Any]:
        """Process content in batches"""
        processed_items = []
        batch_size = self.config['processing']['batch_size']
        
        for i in range(0, len(content_items), batch_size):
            batch = content_items[i:i + batch_size]
            
            try:
                if self.config['processing']['parallel_processing']:
                    batch_results = await self.content_processor.process_content_batch(batch)
                else:
                    batch_results = []
                    for item in batch:
                        result = await self.content_processor.process_single_content(item)
                        batch_results.append(result)
                
                processed_items.extend(batch_results)
                logger.info(f"Processed batch {i//batch_size + 1}/{(len(content_items) + batch_size - 1)//batch_size}")
                
            except Exception as e:
                logger.error(f"Error processing batch {i//batch_size + 1}: {e}")
                self.stats['errors'].append(f"Processing batch {i//batch_size + 1}: {e}")
        
        return processed_items
    
    async def _validate_content_quality(self, processed_content: List[Any]) -> List[Any]:
        """Validate content quality"""
        try:
            quality_reports = await self.quality_controller.validate_content_batch(
                [{'id': item.content_id, 'content': item.processed_content, **item.metadata} 
                 for item in processed_content]
            )
            
            # Update statistics
            quality_levels = {}
            for report in quality_reports:
                level = report.quality_level.value
                quality_levels[level] = quality_levels.get(level, 0) + 1
            
            self.stats['quality_stats'] = quality_levels
            return quality_reports
            
        except Exception as e:
            logger.error(f"Quality validation failed: {e}")
            self.stats['errors'].append(f"Quality validation: {e}")
            return []
    
    def _filter_by_quality(self, processed_content: List[Any], quality_reports: List[Any]) -> List[Any]:
        """Filter content based on quality reports"""
        approved_content = []
        quality_map = {report.content_id: report for report in quality_reports}
        
        for content in processed_content:
            quality_report = quality_map.get(content.content_id)
            if quality_report and quality_report.quality_level != QualityLevel.REJECTED:
                approved_content.append(content)
        
        return approved_content
    
    async def _store_approved_content(self, approved_content: List[Any], quality_reports: List[Any]) -> int:
        """Store approved content"""
        stored_count = 0
        quality_map = {report.content_id: report for report in quality_reports}
        
        for content in approved_content:
            quality_report = quality_map.get(content.content_id)
            if quality_report:
                try:
                    success = await self.storage_manager.store_processed_content(content, quality_report)
                    if success:
                        stored_count += 1
                except Exception as e:
                    logger.error(f"Error storing content {content.content_id}: {e}")
                    self.stats['errors'].append(f"Storage {content.content_id}: {e}")
        
        return stored_count
    
    async def _generate_ingestion_report(self):
        """Generate detailed ingestion report"""
        storage_stats = await self.storage_manager.get_content_statistics()
        
        report = {
            'ingestion_summary': self.stats,
            'storage_statistics': storage_stats,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save report
        report_path = os.path.join(
            self.config['storage']['storage_path'], 
            f"ingestion_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Ingestion report saved to {report_path}")
    
    async def run_incremental_ingestion(self) -> Dict[str, Any]:
        """Run incremental ingestion for new/modified content"""
        logger.info("Starting incremental knowledge ingestion")
        
        # This would implement logic to only process new or modified content
        # For now, it's a simplified version
        
        # Check for new files in monitored directories
        new_content = []
        
        if self.config['file_system']['enabled']:
            # Only scan for files modified in the last 24 hours
            recent_files = await self.file_collector.scan_recent_files(hours=24)
            new_content.extend(recent_files)
        
        if self.config['applications']['enabled']:
            # Check for new notes/bookmarks
            recent_app_data = await self.app_collector.collect_recent_data(hours=24)
            new_content.extend(recent_app_data)
        
        if new_content:
            logger.info(f"Found {len(new_content)} new/modified items")
            return await self._process_and_store_content(new_content)
        else:
            logger.info("No new content found")
            return {'status': 'no_new_content', 'processed': 0}
    
    async def _process_and_store_content(self, content_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process and store a batch of content items"""
        processed_content = await self._process_content_batch(content_items)
        quality_reports = await self._validate_content_quality(processed_content)
        approved_content = self._filter_by_quality(processed_content, quality_reports)
        stored_count = await self._store_approved_content(approved_content, quality_reports)
        
        return {
            'status': 'completed',
            'collected': len(content_items),
            'processed': len(processed_content),
            'approved': len(approved_content),
            'stored': stored_count
        }
    
    async def search_knowledge(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search the knowledge base"""
        return await self.storage_manager.search_content(query, filters)
    
    async def get_knowledge_statistics(self) -> Dict[str, Any]:
        """Get comprehensive knowledge base statistics"""
        return await self.storage_manager.get_content_statistics()
    
    async def export_knowledge(self, output_path: str, format: str = 'json') -> bool:
        """Export entire knowledge base"""
        return await self.storage_manager.export_content(output_path, format)
    
    async def cleanup_knowledge(self, days_old: int = 30, quality_threshold: float = 2.0) -> int:
        """Clean up low-quality or old content"""
        return await self.storage_manager.cleanup_storage(days_old, quality_threshold)
    
    def save_config(self, config_path: str):
        """Save current configuration to file"""
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            logger.info(f"Configuration saved to {config_path}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")

    async def process_single_file(
        self,
        file_path: str,
        job_id: str,
        collection_name: Optional[str] = None,
        user_id: Optional[str] = None,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process a single file and store it in the knowledge base"""
        job_info = {
            'job_id': job_id,
            'status': 'processing',
            'job_type': 'single',
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'user_id': user_id,
            'collection_name': collection_name,
            'total_files': 1,
            'processed_files': 0,
            'failed_files': 0,
            'progress_percentage': 0.0,
            'documents_created': 0,
            'chunks_created': 0,
            'storage_used_bytes': 0
        }
        
        self.active_jobs[job_id] = job_info
        
        try:
            # Process the file
            logger.info(f"Processing file: {file_path}")
            process_result = await self.content_processor.process_file(
                file_path, 
                metadata=metadata or {}
            )
            
            # Extract the processed content object
            if process_result.get('status') == 'error':
                raise ValueError(f"Processing failed: {process_result.get('error')}")
            
            processed_content = process_result.get('processed_content')
            if not processed_content:
                raise ValueError("No processed content returned")
            
            job_info['progress_percentage'] = 50.0
            job_info['updated_at'] = datetime.now()
            
            # Quality control
            quality_report = await self.quality_controller.validate_content(processed_content)
            if not quality_report.approved:
                raise ValueError(f"Content quality check failed: {quality_report.issues}")
            
            job_info['progress_percentage'] = 75.0
            
            # Store in knowledge base
            storage_result = await self.storage_manager.store_processed_content(
                processed_content,
                quality_report
            )
            
            # Update job status
            job_info.update({
                'status': 'completed',
                'progress_percentage': 100.0,
                'processed_files': 1,
                'documents_created': 1,
                'chunks_created': len(storage_result.get('chunks', [])),
                'storage_used_bytes': storage_result.get('size_bytes', 0),
                'completed_at': datetime.now(),
                'updated_at': datetime.now()
            })
            
            # Move to completed jobs
            self.completed_jobs[job_id] = job_info
            del self.active_jobs[job_id]
            
            logger.info(f"Successfully processed file: {file_path}")
            return job_info
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            job_info.update({
                'status': 'failed',
                'failed_files': 1,
                'error_message': str(e),
                'completed_at': datetime.now(),
                'updated_at': datetime.now()
            })
            
            self.completed_jobs[job_id] = job_info
            del self.active_jobs[job_id]
            
            raise

    async def process_batch_files(
        self,
        file_paths: List[str],
        job_id: str,
        collection_name: Optional[str] = None,
        user_id: Optional[str] = None,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process multiple files as a batch"""
        job_info = {
            'job_id': job_id,
            'status': 'processing',
            'job_type': 'batch',
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'user_id': user_id,
            'collection_name': collection_name,
            'total_files': len(file_paths),
            'processed_files': 0,
            'failed_files': 0,
            'progress_percentage': 0.0,
            'documents_created': 0,
            'chunks_created': 0,
            'storage_used_bytes': 0,
            'failed_file_details': []
        }
        
        self.active_jobs[job_id] = job_info
        
        try:
            processed_count = 0
            total_chunks = 0
            total_size = 0
            
            for i, file_path in enumerate(file_paths):
                try:
                    # Process individual file
                    processed_content = await self.content_processor.process_file(
                        file_path,
                        metadata=metadata or {}
                    )
                    
                    # Quality control
                    quality_report = await self.quality_controller.validate_content(processed_content)
                    if quality_report.approved:
                        # Store in knowledge base
                        storage_result = await self.storage_manager.store_processed_content(
                            processed_content,
                            quality_report
                        )
                        
                        processed_count += 1
                        total_chunks += len(storage_result.get('chunks', []))
                        total_size += storage_result.get('size_bytes', 0)
                    else:
                        job_info['failed_file_details'].append({
                            'file_path': file_path,
                            'error': f"Quality check failed: {quality_report.issues}"
                        })
                        job_info['failed_files'] += 1
                        
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {str(e)}")
                    job_info['failed_file_details'].append({
                        'file_path': file_path,
                        'error': str(e)
                    })
                    job_info['failed_files'] += 1
                
                # Update progress
                job_info.update({
                    'processed_files': processed_count,
                    'progress_percentage': ((i + 1) / len(file_paths)) * 100,
                    'documents_created': processed_count,
                    'chunks_created': total_chunks,
                    'storage_used_bytes': total_size,
                    'updated_at': datetime.now()
                })
            
            # Final status
            if job_info['failed_files'] == 0:
                job_info['status'] = 'completed'
            elif processed_count > 0:
                job_info['status'] = 'completed'  # Partial success
            else:
                job_info['status'] = 'failed'
            
            job_info.update({
                'completed_at': datetime.now(),
                'updated_at': datetime.now()
            })
            
            # Move to completed jobs
            self.completed_jobs[job_id] = job_info
            del self.active_jobs[job_id]
            
            logger.info(f"Batch processing completed: {processed_count}/{len(file_paths)} files processed")
            return job_info
            
        except Exception as e:
            logger.error(f"Batch processing failed: {str(e)}")
            job_info.update({
                'status': 'failed',
                'error_message': str(e),
                'completed_at': datetime.now(),
                'updated_at': datetime.now()
            })
            
            self.completed_jobs[job_id] = job_info
            del self.active_jobs[job_id]
            
            raise

    async def sync_cloud_drives(
        self,
        job_id: str,
        config: Dict[str, Any] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Sync and process files from cloud drives"""
        job_info = {
            'job_id': job_id,
            'status': 'processing',
            'job_type': 'cloud_sync',
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'user_id': user_id,
            'total_files': 0,
            'processed_files': 0,
            'failed_files': 0,
            'progress_percentage': 0.0,
            'documents_created': 0,
            'chunks_created': 0,
            'storage_used_bytes': 0
        }
        
        self.active_jobs[job_id] = job_info
        
        try:
            # Update config if provided
            if config:
                self.cloud_collector.config.update(config)
            
            # Collect files from cloud drives
            cloud_files = await self.cloud_collector.collect_all_drives()
            job_info['total_files'] = len(cloud_files)
            job_info['progress_percentage'] = 25.0
            job_info['updated_at'] = datetime.now()
            
            # Process collected files
            processed_count = 0
            total_chunks = 0
            total_size = 0
            
            for i, file_info in enumerate(cloud_files):
                try:
                    # Process the file
                    processed_content = await self.content_processor.process_file(
                        file_info['local_path'],
                        metadata=file_info.get('metadata', {})
                    )
                    
                    # Quality control
                    quality_report = await self.quality_controller.validate_content(processed_content)
                    if quality_report.approved:
                        # Store in knowledge base
                        storage_result = await self.storage_manager.store_processed_content(
                            processed_content,
                            quality_report
                        )
                        
                        processed_count += 1
                        total_chunks += len(storage_result.get('chunks', []))
                        total_size += storage_result.get('size_bytes', 0)
                    else:
                        job_info['failed_files'] += 1
                        
                except Exception as e:
                    logger.error(f"Error processing cloud file {file_info.get('path')}: {str(e)}")
                    job_info['failed_files'] += 1
                
                # Update progress
                progress = 25.0 + ((i + 1) / len(cloud_files)) * 75.0
                job_info.update({
                    'processed_files': processed_count,
                    'progress_percentage': progress,
                    'documents_created': processed_count,
                    'chunks_created': total_chunks,
                    'storage_used_bytes': total_size,
                    'updated_at': datetime.now()
                })
            
            # Final status
            job_info.update({
                'status': 'completed' if processed_count > 0 else 'failed',
                'completed_at': datetime.now(),
                'updated_at': datetime.now()
            })
            
            # Move to completed jobs
            self.completed_jobs[job_id] = job_info
            del self.active_jobs[job_id]
            
            logger.info(f"Cloud sync completed: {processed_count} files processed")
            return job_info
            
        except Exception as e:
            logger.error(f"Cloud sync failed: {str(e)}")
            job_info.update({
                'status': 'failed',
                'error_message': str(e),
                'completed_at': datetime.now(),
                'updated_at': datetime.now()
            })
            
            self.completed_jobs[job_id] = job_info
            del self.active_jobs[job_id]
            
            raise

    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific job"""
        if job_id in self.active_jobs:
            return self.active_jobs[job_id]
        elif job_id in self.completed_jobs:
            return self.completed_jobs[job_id]
        else:
            return None

    async def list_jobs(
        self,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List jobs with optional filtering"""
        all_jobs = []
        
        # Add active jobs
        for job in self.active_jobs.values():
            if user_id is None or job.get('user_id') == user_id:
                if status is None or job.get('status') == status:
                    all_jobs.append(job)
        
        # Add completed jobs
        for job in self.completed_jobs.values():
            if user_id is None or job.get('user_id') == user_id:
                if status is None or job.get('status') == status:
                    all_jobs.append(job)
        
        # Sort by creation time (newest first)
        all_jobs.sort(key=lambda x: x.get('created_at', datetime.min), reverse=True)
        
        # Apply limit
        return all_jobs[:limit]

    async def search_knowledge(
        self,
        query: str,
        collection_name: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 10,
        min_similarity: float = 0.0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search through ingested knowledge using semantic similarity"""
        try:
            search_filters = filters or {}
            if user_id:
                search_filters['user_id'] = user_id
            
            results = await self.storage_manager.search_similar(
                query=query,
                collection_name=collection_name,
                limit=limit,
                min_similarity=min_similarity,
                filters=search_filters
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching knowledge: {str(e)}")
            raise

    async def list_collections(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available knowledge collections"""
        try:
            collections = await self.storage_manager.list_collections(user_id=user_id)
            
            # Format the response as list of dictionaries
            formatted_collections = []
            for collection_name in collections:
                # Get stats for this collection
                stats = await self.storage_manager.get_stats(user_id=user_id)
                content_by_type = stats.get('content_by_type', {})
                document_count = content_by_type.get(collection_name, 0)
                
                formatted_collections.append({
                    'name': collection_name,
                    'document_count': document_count,
                    'content_type': collection_name
                })
            
            return formatted_collections
        except Exception as e:
            logger.error(f"Error listing collections: {str(e)}")
            raise

    async def delete_collection(
        self,
        collection_name: str,
        user_id: Optional[str] = None
    ) -> bool:
        """Delete a knowledge collection and all its documents"""
        try:
            success = await self.storage_manager.delete_collection(
                collection_name=collection_name,
                user_id=user_id
            )
            return success
        except Exception as e:
            logger.error(f"Error deleting collection: {str(e)}")
            raise

    async def get_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get ingestion pipeline statistics"""
        try:
            storage_stats = await self.storage_manager.get_stats(user_id=user_id)
            
            # Combine with job stats
            active_jobs = len([j for j in self.active_jobs.values() 
                             if user_id is None or j.get('user_id') == user_id])
            completed_jobs = len([j for j in self.completed_jobs.values() 
                                if user_id is None or j.get('user_id') == user_id])
            failed_jobs = len([j for j in self.completed_jobs.values() 
                             if (user_id is None or j.get('user_id') == user_id) 
                             and j.get('status') == 'failed'])
            
            stats = {
                **storage_stats,
                'processing_jobs_active': active_jobs,
                'processing_jobs_completed': completed_jobs,
                'processing_jobs_failed': failed_jobs,
                'supported_file_types': self.config.get('file_system', {}).get('supported_formats', [])
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            raise

    async def update_config(self, new_config: Dict[str, Any]) -> bool:
        """Update ingestion configuration"""
        try:
            # Validate config structure
            required_sections = ['file_system', 'processing', 'storage']
            for section in required_sections:
                if section not in new_config:
                    return False
            
            # Update configuration
            self.config.update(new_config)
            
            # Reinitialize components with new config
            self.file_collector = FileSystemCollector(self.config.get('file_system', {}))
            self.content_processor = ContentProcessor(self.config.get('processing', {}))
            self.quality_controller = QualityController(self.config.get('quality_control', {}))
            self.storage_manager = StorageManager(self.config.get('storage', {}))
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating config: {str(e)}")
            return False

    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the ingestion system"""
        try:
            components = {}
            
            # Check storage health
            try:
                storage_healthy = await self.storage_manager.health_check()
                components['storage'] = 'healthy' if storage_healthy else 'unhealthy'
            except Exception as e:
                components['storage'] = 'unhealthy'
            
            # Check processors
            try:
                # Test content processor
                test_result = await self.content_processor.health_check()
                if isinstance(test_result, dict):
                    components['content_processor'] = test_result.get('status', 'unhealthy')
                else:
                    components['content_processor'] = 'healthy' if test_result else 'unhealthy'
            except Exception as e:
                components['content_processor'] = 'unhealthy'
            
            # Check quality controller
            try:
                components['quality_controller'] = 'healthy'
            except:
                components['quality_controller'] = 'unhealthy'
            
            # Overall status
            unhealthy_components = [k for k, v in components.items() if v == 'unhealthy']
            if len(unhealthy_components) == 0:
                status = 'healthy'
            elif len(unhealthy_components) < len(components) / 2:
                status = 'degraded'
            else:
                status = 'unhealthy'
            
            # Get system metrics
            import psutil
            
            health = {
                'status': status,
                'timestamp': datetime.now(),
                'components': components,
                'active_jobs': len(self.active_jobs),
                'queue_size': 0,  # TODO: Implement job queue
                'memory_usage_percentage': psutil.virtual_memory().percent,
                'cpu_usage_percentage': psutil.cpu_percent(),
                'errors': []
            }
            
            # Add storage space if available
            try:
                disk_usage = psutil.disk_usage('/')
                health['storage_available_gb'] = disk_usage.free / (1024**3)
            except:
                health['storage_available_gb'] = 0
            
            return health
            
        except Exception as e:
            logger.error(f"Error checking health: {str(e)}")
            return {
                'status': 'unhealthy',
                'timestamp': datetime.now(),
                'error': str(e),
                'components': {},
                'active_jobs': 0,
                'queue_size': 0,
                'memory_usage_percentage': 0,
                'cpu_usage_percentage': 0,
                'storage_available_gb': 0,
                'errors': [str(e)]
            }

# Convenience function for easy usage
async def run_knowledge_ingestion(config_path: str = None) -> Dict[str, Any]:
    """Run complete knowledge ingestion with default or custom configuration"""
    coordinator = IngestionCoordinator(config_path)
    return await coordinator.run_full_ingestion()
