import requests
import json

API_URL = "http://localhost:8000"

def test_update_stage():
    deal_id = 1 # Assuming deal 1 exists, or we might get 404, which is fine (means endpoint exists)
    url = f"{API_URL}/crm/deals/{deal_id}/stage"
    payload = {"stage": "qualified"}
    
    print(f"Testing PATCH {url}")
    try:
        response = requests.patch(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Also test OPTIONS
        print(f"Testing OPTIONS {url}")
        response_opt = requests.options(url)
        print(f"OPTIONS Status Code: {response_opt.status_code}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_update_stage()
