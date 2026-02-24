import requests
import json

def fetch_linkedin_companies():
    apify_token = "apify_api_mVrsfJOatiMFS52nDWQwheqdL7OTLX1O87id"
    actor_id = "harvestapi~linkedin-company"

    api_url = f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items?token={apify_token}"

    payload = {
        "companies": [
            "Distack Solutions"
        ]
    }

    print("🚀 Sending request to Apify...")
    response = requests.post(api_url, json=payload, timeout=300)

    print(f"✅ Response Status: {response.status_code}")

    try:
        data = response.json()
        print(json.dumps(data, indent=2))
    except Exception:
        print(response.text)


if __name__ == "__main__":
    fetch_linkedin_companies()
