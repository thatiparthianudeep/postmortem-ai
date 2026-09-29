import urllib.request
import json

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    url = f"{BASE_URL}/api/health"
    req = urllib.request.urlopen(url)
    res = json.loads(req.read().decode('utf-8'))
    print("✅ /api/health Response:", json.dumps(res, indent=2))
    assert res["status"] == "healthy"

def test_incidents():
    url = f"{BASE_URL}/api/incidents"
    req = urllib.request.urlopen(url)
    res = json.loads(req.read().decode('utf-8'))
    print(f"✅ /api/incidents Response: Loaded {res['count']} historical incident memories")
    assert res["count"] >= 6

def test_analyze():
    url = f"{BASE_URL}/api/analyze"
    payload = {
        "title": "Checkout DB Pool Exhaustion Test",
        "severity": "P0",
        "affected_component": "Checkout Microservice",
        "description": "Checkout API error rate spiked to 40% with database connection checkout timeout.",
        "logs": "db.Pool: connection checkout timeout after 3000ms"
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    response = urllib.request.urlopen(req)
    res = json.loads(response.read().decode('utf-8'))
    print("✅ /api/analyze Response:")
    print(f"   Incident ID: {res.get('incident_id')}")
    print(f"   Title: {res.get('title')}")
    print(f"   5 Whys Count: {len(res.get('five_whys', []))}")
    print(f"   Matched Memories Count: {len(res.get('similar_incidents', []))}")
    assert "five_whys" in res

def test_chat():
    url = f"{BASE_URL}/api/chat"
    payload = {
        "query": "How do we prevent connection pool exhaustion?"
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    response = urllib.request.urlopen(req)
    res = json.loads(response.read().decode('utf-8'))
    print("✅ /api/chat Response:")
    print(f"   Copilot Answer length: {len(res.get('answer', ''))} chars")
    assert "answer" in res

if __name__ == "__main__":
    print("🚀 Testing Postmortem AI Backend REST APIs...")
    test_health()
    test_incidents()
    test_analyze()
    test_chat()
    print("🎉 All API verification checks PASSED successfully!")
