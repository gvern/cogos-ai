import sys
import os
from pathlib import Path
import uvicorn

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    # Import app here to avoid issues during import if paths are wrong
    try:
        from app.api.main import app
        uvicorn.run(app, host="127.0.0.1", port=8000)
    except Exception as e:
        print(f"Failed to start server: {e}")
        sys.exit(1)
