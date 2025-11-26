import asyncio
import os
import sys
from pathlib import Path
import aiohttp
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test configuration
API_URL = "http://localhost:8000"
TEST_EMAIL = "rag_test@example.com"
TEST_PASSWORD = "password123"
TEST_FILE_CONTENT = "This is a test document for RAG verification."
TEST_FILENAME = "rag_verification.txt"

async def verify_rag_upload():
    print(f"🚀 Starting RAG verification against {API_URL}")
    
    async with aiohttp.ClientSession() as session:
        # 1. Signup/Login
        print(f"\n1. Authenticating as {TEST_EMAIL}...")
        token = None
        
        # Try login first
        try:
            async with session.post(f"{API_URL}/auth/login", json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    token = data["access_token"]
                    print("   ✅ Login successful")
                else:
                    print(f"   Login failed ({resp.status}), trying signup...")
        except Exception as e:
            print(f"   Login error: {e}")

        # If login failed, try signup
        if not token:
            try:
                async with session.post(f"{API_URL}/auth/signup", json={
                    "email": TEST_EMAIL,
                    "password": TEST_PASSWORD,
                    "name": "RAG Tester"
                }) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        # Signup might return token or just success
                        if "access_token" in data:
                            token = data["access_token"]
                        else:
                            # Try login again after signup
                            async with session.post(f"{API_URL}/auth/login", json={
                                "email": TEST_EMAIL,
                                "password": TEST_PASSWORD
                            }) as login_resp:
                                login_data = await login_resp.json()
                                token = login_data.get("access_token")
                        print("   ✅ Signup successful")
                    else:
                        text = await resp.text()
                        print(f"   ❌ Signup failed: {text}")
                        return
            except Exception as e:
                print(f"   Signup error: {e}")
                return

        if not token:
            print("   ❌ Could not obtain auth token")
            return

        # 2. Create test file
        print(f"\n2. Creating test file '{TEST_FILENAME}'...")
        with open(TEST_FILENAME, "w") as f:
            f.write(TEST_FILE_CONTENT)
        
        # 3. Upload file
        print(f"\n3. Uploading file to RAG...")
        headers = {"Authorization": f"Bearer {token}"}
        data = aiohttp.FormData()
        data.add_field('files',
                       open(TEST_FILENAME, 'rb'),
                       filename=TEST_FILENAME,
                       content_type='text/plain')
        
        try:
            async with session.post(f"{API_URL}/rag/upload", data=data, headers=headers) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    print(f"   ✅ Upload successful!")
                    print(f"   Response: {json.dumps(result, indent=2)}")
                else:
                    text = await resp.text()
                    print(f"   ❌ Upload failed ({resp.status}): {text}")
        except Exception as e:
            print(f"   Upload error: {e}")
        finally:
            # Cleanup
            if os.path.exists(TEST_FILENAME):
                os.remove(TEST_FILENAME)

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(verify_rag_upload())
