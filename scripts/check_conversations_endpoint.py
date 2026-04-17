import asyncio
import aiohttp
import json
import sys

API_URL = "http://localhost:8001"
# Use the test user credentials
TEST_EMAIL = "rag_test@example.com" 
TEST_PASSWORD = "password123"

async def check_conversations():
    print(f"🚀 Checking GET {API_URL}/conversations/")
    
    async with aiohttp.ClientSession() as session:
        # 1. Login
        print(f"1. Authenticating...")
        token = None
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
                    text = await resp.text()
                    print(f"   ❌ Login failed ({resp.status}): {text}")
                    # Try to signup if login fails
                    print("   Trying signup...")
                    async with session.post(f"{API_URL}/auth/signup", json={
                        "email": TEST_EMAIL,
                        "password": TEST_PASSWORD,
                        "name": "Test User"
                    }) as signup_resp:
                        if signup_resp.status == 200:
                            data = await signup_resp.json()
                            token = data["access_token"]
                            print("   ✅ Signup successful")
                        else:
                            text = await signup_resp.text()
                            print(f"   ❌ Signup failed ({signup_resp.status}): {text}")
                            return
        except Exception as e:
            print(f"   Auth error: {e}")
            return

        if not token:
            return

        # 2. Get Conversations
        print(f"\n2. Fetching conversations...")
        headers = {"Authorization": f"Bearer {token}"}
        try:
            async with session.get(f"{API_URL}/conversations/", headers=headers) as resp:
                print(f"   Status: {resp.status}")
                try:
                    data = await resp.json()
                    print(f"   Response type: {type(data)}")
                    if isinstance(data, list):
                        print(f"   ✅ Response is a list of {len(data)} items")
                        if len(data) > 0:
                            print(f"   First item: {json.dumps(data[0], indent=2)}")
                    else:
                        print(f"   ❌ Response is NOT a list: {json.dumps(data, indent=2)}")
                except Exception as e:
                    text = await resp.text()
                    print(f"   ❌ Failed to parse JSON: {text}")
        except Exception as e:
            print(f"   Request error: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check_conversations())
