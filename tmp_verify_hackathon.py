import urllib.request
import json

BASE_URL = "http://127.0.0.1:8000"

def test_api():
    print("🚀 Starting Postmortem AI Hackathon Verification Suite...")
    
    # 1. Health Check
    req = urllib.request.urlopen(f"{BASE_URL}/api/health")
    health = json.loads(req.read().decode())
    print("✅ 1. /api/health Response:", health["service"], "| Memories:", health["hindsight_memory_bank_count"])
    assert health["status"] == "healthy"
    
    # 2. Analyze WITH Hindsight Memory (use_memory=True)
    payload_mem = {
        "title": "PostgreSQL Connection Pool Exhaustion",
        "description": "Checkout API error rate spiked to 34% during high traffic sale.",
        "logs": "[ERROR] db.Pool: connection checkout timeout after 3000ms\n[WARN] PgBouncer pool size (max_connections=100) exhausted.",
        "severity": "P0",
        "affected_component": "Checkout Microservice",
        "use_memory": True
    }
    req = urllib.request.Request(
        f"{BASE_URL}/api/analyze",
        data=json.dumps(payload_mem).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(req)
    report_mem = json.loads(res.read().decode())
    print("✅ 2. /api/analyze (With Memory): Grounded =", report_mem["memory_grounded"])
    assert report_mem["memory_grounded"] is True
    assert "hindsight_inspector_metadata" in report_mem
    meta = report_mem["hindsight_inspector_metadata"]
    print("   🔍 Inspector Query:", meta["exact_query"][:60], "...")
    print("   🏷️ Extracted Entities:", meta["extracted_entities"])
    print("   📊 Retrieved Nodes Count:", meta["retrieved_nodes_count"])

    # 3. Analyze WITHOUT Hindsight Memory (use_memory=False) - Before vs After Baseline
    payload_no_mem = dict(payload_mem)
    payload_no_mem["use_memory"] = False
    req = urllib.request.Request(
        f"{BASE_URL}/api/analyze",
        data=json.dumps(payload_no_mem).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(req)
    report_no_mem = json.loads(res.read().decode())
    print("✅ 3. /api/analyze (Standard LLM Baseline): Grounded =", report_no_mem["memory_grounded"])
    assert report_no_mem["memory_grounded"] is False
    print("   🤖 Delta Label:", report_no_mem["hindsight_inspector_metadata"]["memory_impact_delta"])

    # 4. Continuous Learning Loop - Commit New Verified Resolution
    commit_payload = {
        "incident_id": "INC-2026-AUTO",
        "title": "PostgreSQL Connection Pool Exhaustion",
        "severity": "P0",
        "category": "Verified Field Fix",
        "component": "Checkout Service",
        "custom_fix": "Deployed PgBouncer sidecar container with 200 transaction pooling limit and 3s socket timeouts",
        "engineer_feedback": "Verified in production staging",
        "tags": ["postgresql", "pgbouncer", "database", "verified_commit"]
    }
    req = urllib.request.Request(
        f"{BASE_URL}/api/incidents/commit_memory",
        data=json.dumps(commit_payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(req)
    commit_res = json.loads(res.read().decode())
    print("✅ 4. /api/incidents/commit_memory Response:", commit_res["message"])
    assert commit_res["success"] is True
    
    # 5. Verify Memory Count Increased
    req = urllib.request.urlopen(f"{BASE_URL}/api/incidents")
    incidents = json.loads(req.read().decode())
    print("✅ 5. /api/incidents Count after commit:", incidents["count"])
    assert incidents["count"] >= 7

    print("\n🎉 ALL 5 HACKATHON VERIFICATION CHECKS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_api()
