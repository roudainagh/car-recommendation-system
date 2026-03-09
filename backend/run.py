"""
Script to run the FastAPI server - FIXED VERSION
"""

import uvicorn
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

if __name__ == "__main__":
    print("="*60)
    print("🚀 Starting Car Recommender API")
    print("="*60)
    
    # Check if data exists
    data_path = Path(__file__).parent.parent / "data"
    required_files = [
        "cars_processed.csv",
        "cars_versions_specs.csv", 
        "users_processed.csv",
        "users_dataset.csv"
    ]
    
    missing_files = []
    for file in required_files:
        if not (data_path / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        sys.exit(1)
    else:
        print("✅ All data files found")
    
    print("\n📡 Starting server...")
    print("   🌐 Local: http://localhost:8000")
    print("   📚 API Docs: http://localhost:8000/api/docs")
    print("   🔍 Alternative Docs: http://localhost:8000/api/redoc")
    print("\n   Press Ctrl+C to stop\n")
    
    try:
        uvicorn.run(
            "api.main:app",
            host="127.0.0.1",  # Changed from 0.0.0.0 to localhost
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)