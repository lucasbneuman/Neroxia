import requests

API_URL = "http://localhost:8000"
# API_URL = "http://127.0.0.1:8000"

def test_cors_preflight():
    deal_id = 1
    url = f"{API_URL}/crm/deals/{deal_id}/stage"
    
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "PATCH",
        "Access-Control-Request-Headers": "content-type"
    }
    
    print(f"Testing CORS Preflight OPTIONS {url}")
    print(f"Headers: {headers}")
    
    try:
        response = requests.options(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print("Response Headers:")
        for k, v in response.headers.items():
            print(f"  {k}: {v}")
            
        if response.status_code == 200:
            print("\nCORS Preflight seems OK (200 OK)")
        else:
            print(f"\nCORS Preflight FAILED ({response.status_code})")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_cors_preflight()
