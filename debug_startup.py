import sys
import os
from pathlib import Path

# Add apps/api to path so we can import src
api_path = Path("apps/api")
sys.path.insert(0, str(api_path.absolute()))

print("Attempting to import src.main...")
try:
    from src.main import app
    print("✅ Successfully imported src.main")
except Exception as e:
    print("❌ Failed to import src.main")
    import traceback
    traceback.print_exc()
