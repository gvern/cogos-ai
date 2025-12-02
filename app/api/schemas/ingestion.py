"""
Pydantic schemas for the knowledge ingestion API
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    """Status of an ingestion job"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class FileType(str, Enum):
    """Supported file types for ingestion"""
    PDF = "pdf"
    DOCX = "docx"
    DOC = "doc"
    TXT = "txt"
    MD = "md"
    RTF = "rtf"
    PPTX = "pptx"
    PPT = "ppt"
    XLSX = "xlsx"
    XLS = "xls"
    CSV = "csv"
    JPG = "jpg"
    JPEG = "jpeg"
    PNG = "png"
    TIFF = "tiff"
    BMP = "bmp"
    MP3 = "mp3"
    WAV = "wav"
    MP4 = "mp4"
    MOV = "mov"
    AVI = "avi"
    EPUB = "epub"
    MOBI = "mobi"
    HTML = "html"
    XML = "xml"

class QualityLevel(str, Enum):
    """Quality control levels"""
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"

class ChunkingStrategy(str, Enum):
    """Text chunking strategies"""
    FIXED_SIZE = "fixed_size"
    SENTENCE_BASED = "sentence_based"
    SEMANTIC = "semantic"
    PARAGRAPH = "paragraph"

class CloudProvider(str, Enum):
    """Supported cloud storage providers"""
    GOOGLE_DRIVE = "google_drive"
    DROPBOX = "dropbox"
    ICLOUD = "icloud"
    ONEDRIVE = "onedrive"

class FileProcessingResponse(BaseModel):
    """Response for single file processing"""
    job_id: str
    filename: str
    status: JobStatus
    message: str
    file_size: Optional[int] = None
    estimated_completion: Optional[datetime] = None

class IngestionJobResponse(BaseModel):
    """Response for ingestion jobs"""
    job_id: str
    status: JobStatus
    total_files: Optional[int] = None
    processed_files: Optional[int] = None
    failed_files: Optional[int] = None
    message: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    progress_percentage: Optional[float] = None

class SearchResult(BaseModel):
    """Individual search result"""
    document_id: str
    chunk_id: str
    content: str
    similarity_score: float
    metadata: Dict[str, Any]
    source_file: str
    collection_name: str
    chunk_index: int
    created_at: datetime

class SearchRequest(BaseModel):
    """Request for semantic search"""
    query: str = Field(..., description="Search query")
    collection_name: Optional[str] = None
    user_id: Optional[str] = None
    limit: int = Field(default=10, ge=1, le=100)
    min_similarity: float = Field(default=0.0, ge=0.0, le=1.0)
    filters: Optional[Dict[str, Any]] = None

class SearchResponse(BaseModel):
    """Response for semantic search"""
    query: str
    results: List[SearchResult]
    total_results: int
    search_time_ms: Optional[float] = None

class BatchProcessingRequest(BaseModel):
    """Request for batch processing"""
    file_paths: List[str]
    collection_name: Optional[str] = None
    user_id: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    processing_config: Optional[Dict[str, Any]] = None

class CloudSyncConfig(BaseModel):
    """Configuration for cloud storage sync"""
    provider: CloudProvider
    enabled: bool = True
    credentials: Dict[str, str]
    sync_path: Optional[str] = None
    file_filters: Optional[List[str]] = None
    auto_sync_interval: Optional[int] = None  # minutes

class ProcessingConfig(BaseModel):
    """Configuration for content processing"""
    chunking_strategy: ChunkingStrategy = ChunkingStrategy.SEMANTIC
    chunk_size: int = Field(default=1000, ge=100, le=5000)
    chunk_overlap: int = Field(default=200, ge=0, le=1000)
    quality_level: QualityLevel = QualityLevel.STANDARD
    extract_metadata: bool = True
    ocr_enabled: bool = True
    language_detection: bool = True
    entity_extraction: bool = True

class IngestionConfig(BaseModel):
    """Complete ingestion system configuration"""
    processing: ProcessingConfig = ProcessingConfig()
    cloud_storage: List[CloudSyncConfig] = []
    supported_file_types: List[FileType] = []
    max_file_size_mb: int = Field(default=100, ge=1, le=1000)
    batch_size: int = Field(default=10, ge=1, le=100)
    concurrent_jobs: int = Field(default=5, ge=1, le=20)
    storage_path: str = "/tmp/ingestion"
    enable_deduplication: bool = True

class CollectionInfo(BaseModel):
    """Information about a knowledge collection"""
    name: str
    description: Optional[str] = None
    document_count: int
    total_chunks: int
    created_at: datetime
    updated_at: datetime
    user_id: Optional[str] = None
    tags: List[str] = []
    file_types: List[FileType] = []
    total_size_bytes: int
    avg_chunk_size: int

class IngestionStats(BaseModel):
    """Ingestion pipeline statistics"""
    total_documents: int
    total_chunks: int
    total_collections: int
    processing_jobs_active: int
    processing_jobs_completed: int
    processing_jobs_failed: int
    total_storage_used_bytes: int
    avg_processing_time_seconds: float
    supported_file_types: List[FileType]
    last_ingestion: Optional[datetime] = None

class JobDetails(BaseModel):
    """Detailed job information"""
    job_id: str
    status: JobStatus
    job_type: str  # single, batch, cloud_sync
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    user_id: Optional[str] = None
    collection_name: Optional[str] = None
    
    # File processing details
    total_files: int
    processed_files: int
    failed_files: int
    
    # Progress tracking
    progress_percentage: float
    estimated_completion: Optional[datetime] = None
    
    # Results
    documents_created: int
    chunks_created: int
    storage_used_bytes: int
    
    # Error information
    error_message: Optional[str] = None
    failed_file_details: List[Dict[str, Any]] = []
    
    # Performance metrics
    processing_time_seconds: Optional[float] = None
    throughput_files_per_minute: Optional[float] = None

class HealthStatus(BaseModel):
    """Health status of the ingestion system"""
    status: str  # healthy, degraded, unhealthy
    timestamp: datetime
    components: Dict[str, str]  # component -> status
    active_jobs: int
    queue_size: int
    storage_available_gb: float
    memory_usage_percentage: float
    cpu_usage_percentage: float
    errors: List[str] = []

class WebScrapingConfig(BaseModel):
    """Configuration for web scraping"""
    urls: List[str]
    max_depth: int = Field(default=2, ge=1, le=5)
    follow_links: bool = True
    respect_robots_txt: bool = True
    rate_limit_seconds: float = Field(default=1.0, ge=0.1, le=10.0)
    user_agent: str = "CogOS Knowledge Ingestion Bot"
    timeout_seconds: int = Field(default=30, ge=5, le=120)

class WebScrapingRequest(BaseModel):
    """Request for web scraping"""
    config: WebScrapingConfig
    collection_name: Optional[str] = None
    user_id: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
