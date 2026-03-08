"""
Test the agent API endpoints via HTTP
"""
import requests
import json

# Test data
contact_data = {
    "contact_data": {
        "name": "Sarah Chen",
        "role": "ML Engineer",
        "company": "Google",
        "topics_discussed": ["AI safety", "LLM alignment"],
        "follow_ups": ["Send GitHub repo"],
        "conversation_summary": "Discussed AI safety work at Google",
        "met_at": "DevFest Kolkata 2026",
        "met_date": "2026-02-15"
    }
}

# Test health check first
print("Testing health endpoint...")
response = requests.get("http://localhost:8000/health")
print(f"Health Status: {response.status_code}")
print(f"Response: {response.json()}\n")

# Test root endpoint
print("Testing root endpoint...")
response = requests.get("http://localhost:8000/")
print(f"Root Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}\n")

# Test agent enrichment endpoint
print("Testing agent enrichment endpoint...")
try:
    response = requests.post(
        "http://localhost:8000/api/agents/enrich",
        json=contact_data,
        headers={"Content-Type": "application/json"}
    )
    print(f"Agent Enrich Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print("SUCCESS! Agent enrichment endpoint works!")
        print(f"\nEnriched Contact: {result['enriched_contact']['name']}")
        print(f"Priority Score: {result['enriched_contact']['followup_strategy']['priority_score']}")
        print(f"Urgency: {result['enriched_contact']['followup_strategy']['urgency']}")
    else:
        print(f"ERROR: {response.text}")
except Exception as e:
    print(f"ERROR: {e}")
