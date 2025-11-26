"""
RAG Service Diagnostic Script
Run this to check why RAG service is not initializing
"""
import os
import sys
from pathlib import Path

# Add bot-engine to path
bot_engine_path = Path(__file__).parent / "apps" / "bot-engine" / "src"
sys.path.insert(0, str(bot_engine_path))

print("=" * 60)
print("RAG SERVICE DIAGNOSTIC")
print("=" * 60)

# Check environment variables
print("\n1. Checking Environment Variables:")
print("-" * 60)

supabase_url = os.getenv("SUPABASE_URL")
supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")
supabase_service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
openai_key = os.getenv("OPENAI_API_KEY")

print(f"SUPABASE_URL: {'✅ Set' if supabase_url else '❌ Missing'}")
if supabase_url:
    print(f"  Value: {supabase_url}")

print(f"SUPABASE_SERVICE_KEY: {'✅ Set' if supabase_service_key else '❌ Missing'}")
if supabase_service_key:
    print(f"  Value: {supabase_service_key[:20]}...")

print(f"SUPABASE_SERVICE_ROLE_KEY: {'✅ Set' if supabase_service_role_key else '❌ Missing'}")
if supabase_service_role_key:
    print(f"  Value: {supabase_service_role_key[:20]}...")

print(f"OPENAI_API_KEY: {'✅ Set' if openai_key else '❌ Missing'}")
if openai_key:
    print(f"  Value: {openai_key[:20]}...")

# Check dependencies
print("\n2. Checking Dependencies:")
print("-" * 60)

try:
    from supabase import create_client
    print("✅ supabase-py installed")
except ImportError:
    print("❌ supabase-py NOT installed")

try:
    from langchain_community.vectorstores import SupabaseVectorStore
    print("✅ langchain-community installed")
except ImportError:
    print("❌ langchain-community NOT installed")

try:
    from langchain_openai import OpenAIEmbeddings
    print("✅ langchain-openai installed")
except ImportError:
    print("❌ langchain-openai NOT installed")

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    print("✅ langchain-text-splitters installed")
except ImportError:
    print("❌ langchain-text-splitters NOT installed")

# Try to initialize RAG service
print("\n3. Initializing RAG Service:")
print("-" * 60)

try:
    from services.rag_service import get_rag_service
    
    rag_service = get_rag_service()
    
    print(f"RAG Service Enabled: {'✅ YES' if rag_service.enabled else '❌ NO'}")
    
    if rag_service.enabled:
        print(f"Backend: {rag_service.backend}")
        
        # Try to get stats
        stats = rag_service.get_collection_stats()
        print(f"Stats: {stats}")
    else:
        print("\n⚠️  RAG Service is DISABLED")
        print("\nPossible reasons:")
        if not supabase_service_key:
            print("  - SUPABASE_SERVICE_KEY is missing in .env")
            print("    (Note: RAG service looks for SUPABASE_SERVICE_KEY, not SUPABASE_SERVICE_ROLE_KEY)")
        if not openai_key:
            print("  - OPENAI_API_KEY is missing in .env")
        
except Exception as e:
    print(f"❌ Error initializing RAG service: {e}")
    import traceback
    traceback.print_exc()

# Recommendations
print("\n4. Recommendations:")
print("-" * 60)

if not supabase_service_key and supabase_service_role_key:
    print("⚠️  You have SUPABASE_SERVICE_ROLE_KEY but not SUPABASE_SERVICE_KEY")
    print("   Add this to your .env file:")
    print(f"   SUPABASE_SERVICE_KEY={supabase_service_role_key}")
    print()

if not supabase_service_key and not supabase_service_role_key:
    print("❌ Missing Supabase credentials")
    print("   1. Go to https://supabase.com/dashboard")
    print("   2. Select your project")
    print("   3. Go to Settings > API")
    print("   4. Copy the 'service_role' key")
    print("   5. Add to .env:")
    print("      SUPABASE_SERVICE_KEY=your_service_role_key_here")
    print()

if not openai_key:
    print("❌ Missing OpenAI API key")
    print("   1. Go to https://platform.openai.com/api-keys")
    print("   2. Create a new API key")
    print("   3. Add to .env:")
    print("      OPENAI_API_KEY=your_openai_key_here")
    print()

print("=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)
