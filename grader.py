import requests
import json
import os
from dotenv import load_dotenv

def load_reference(filename):
    # This ensures the script finds the file regardless of where you run it from
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, 'references', filename)

    with open(file_path, 'r') as f:
        return json.load(f)

# Load environment variables from .env
load_dotenv()

# Usage
golden_ref = load_reference('dashboard_web_metrics_v1.json')
print(f"Loaded Golden Reference: {golden_ref['dashboard']['title']}")

GRAFANA_URL = os.getenv("GRAFANA_URL")
GRAFANA_API_KEY = os.getenv("GRAFANA_TOKEN")
DASHBOARD_ID = os.getenv("DASHBOARD_ID")

if not GRAFANA_URL or not GRAFANA_API_KEY or not DASHBOARD_ID:
    raise ValueError("Missing GRAFANA_URL, GRAFANA_TOKEN, or DASHBOARD_ID in .env")

headers = {
    "Authorization": f"Bearer {GRAFANA_API_KEY}",
    "Content-Type": "application/json"
}

def verify_dashboard_exists(uid):
    endpoint = f"{GRAFANA_URL}/api/dashboards/uid/{uid}"

    try:
        response = requests.get(endpoint, headers=headers)

        if response.status_code == 200:
            data = response.json()
            title = data.get('dashboard', {}).get('title', 'Unknown')
            print(f"Success: Dashboard '{title}' found.")

            panels = data.get('dashboard', {}).get('panels', [])
            print(f"Dashboard contains {len(panels)} panels.")

            return data
        elif response.status_code == 404:
            print(f"Failure: Dashboard with UID {uid} not found.")
        else:
            print(f"Error: Received status code {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Connection Error: {e}")

def grade_attempt(reference_json, ai_generated_json):
    score = 0
    total_points = 3

    # 1. Check Query Accuracy
    ref_query = reference_json['dashboard']['panels'][0]['targets'][0]['expr']
    ai_query = ai_generated_json['dashboard']['panels'][0]['targets'][0]['expr']

    if ref_query == ai_query:
        print("Point: Query logic is identical.")
        score += 1
    else:
        print(f"Fail: Expected '{ref_query}', but got '{ai_query}'")

    # 2. Check Unit Configuration
    if ai_generated_json['dashboard']['panels'][0]['fieldConfig']['defaults']['unit'] == "reqps":
        print("Point: Correct unit (reqps) applied.")
        score += 1

    # ... Add more checks ...

    print(f"\nFinal Score: {score}/{total_points}")

if __name__ == "__main__":
    verify_dashboard_exists(DASHBOARD_ID)