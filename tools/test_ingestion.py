#!/usr/bin/env python3
"""
Test script for the knowledge ingestion system
"""
import asyncio
import sys
import os
import tempfile
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.api.ingestion.ingestion_coordinator import IngestionCoordinator

async def test_basic_functionality():
    """Test basic ingestion functionality"""
    print("🧪 Testing CogOS Knowledge Ingestion System")
    print("=" * 50)
    
    # Initialize coordinator with test config
    test_config = {
        "file_system": {
            "enabled": True,
            "supported_formats": ["txt", "md", "pdf", "docx"],
            "max_file_size_mb": 100
        },
        "processing": {
            "chunking_strategy": "fixed_size",
            "chunk_size": 500,
            "chunk_overlap": 50,
            "quality_level": "basic",
            "extract_metadata": True,
            "ocr_enabled": False,
            "language_detection": True,
            "entity_extraction": False
        },
        "storage": {
            "vector_db": {
                "type": "chromadb",
                "persist_directory": str(project_root / "backend" / "embeddings" / "test_chroma"),
                "collection_name": "test_knowledge"
            },
            "file_storage": {
                "base_path": str(project_root / "test_ingested"),
                "organize_by_date": False,
                "preserve_structure": True
            }
        },
        "quality_control": {
            "min_content_length": 10,
            "max_content_length": 10000,
            "deduplication_enabled": False
        }
    }
    
    # Save test config
    config_path = project_root / "test_config.json"
    with open(config_path, 'w') as f:
        json.dump(test_config, f, indent=2)
    
    try:
        # Initialize coordinator
        print("📋 Initializing ingestion coordinator...")
        coordinator = IngestionCoordinator(str(config_path))
        
        # Test 1: Health check
        print("\n🏥 Testing health check...")
        health = await coordinator.health_check()
        print(f"Health status: {health['status']}")
        print(f"Components: {health['components']}")
        
        # Test 2: Create a test file
        print("\n📄 Creating test file...")
        test_dir = tempfile.mkdtemp()
        test_file = os.path.join(test_dir, "test_document.txt")
        
        test_content = """
        This is a test document for the CogOS knowledge ingestion system.
        
        It contains multiple paragraphs to test the chunking functionality.
        
        The system should be able to:
        1. Process this text file
        2. Extract meaningful content
        3. Create chunks for embedding
        4. Store everything in the vector database
        
        This is additional content to ensure we have enough text for proper testing.
        """
        
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        print(f"Created test file: {test_file}")
        
        # Test 3: Process single file
        print("\n⚙️ Testing single file processing...")
        job_id = "test_single_file"
        
        try:
            result = await coordinator.process_single_file(
                file_path=test_file,
                job_id=job_id,
                collection_name="test_collection",
                user_id="test_user",
                tags=["test", "demo"],
                metadata={"source": "test_script", "purpose": "validation"}
            )
            
            print(f"✅ Single file processing completed:")
            print(f"   Status: {result['status']}")
            print(f"   Documents created: {result['documents_created']}")
            print(f"   Chunks created: {result['chunks_created']}")
            
        except Exception as e:
            print(f"❌ Single file processing failed: {str(e)}")
        
        # Test 4: Search functionality
        print("\n🔍 Testing search functionality...")
        try:
            search_results = await coordinator.search_knowledge(
                query="CogOS knowledge ingestion system",
                collection_name="test_collection",
                user_id="test_user",
                limit=5
            )
            
            print(f"✅ Search completed:")
            print(f"   Found {len(search_results)} results")
            for i, result in enumerate(search_results[:2]):
                print(f"   Result {i+1}: {result.get('content', '')[:100]}...")
                
        except Exception as e:
            print(f"❌ Search failed: {str(e)}")
        
        # Test 5: Statistics
        print("\n📊 Testing statistics...")
        try:
            stats = await coordinator.get_stats(user_id="test_user")
            print(f"✅ Statistics retrieved:")
            print(f"   Total documents: {stats.get('total_documents', 0)}")
            print(f"   Total chunks: {stats.get('total_chunks', 0)}")
            print(f"   Active jobs: {stats.get('processing_jobs_active', 0)}")
            
        except Exception as e:
            print(f"❌ Statistics failed: {str(e)}")
        
        # Test 6: List collections
        print("\n📚 Testing collection listing...")
        try:
            collections = await coordinator.list_collections(user_id="test_user")
            print(f"✅ Collections listed:")
            for collection in collections:
                print(f"   - {collection.get('name', 'Unknown')}: {collection.get('document_count', 0)} documents")
                
        except Exception as e:
            print(f"❌ Collection listing failed: {str(e)}")
        
        print("\n🎉 Testing completed!")
        
        # Cleanup
        os.remove(test_file)
        os.rmdir(test_dir)
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup config file
        if config_path.exists():
            config_path.unlink()

if __name__ == "__main__":
    asyncio.run(test_basic_functionality())
