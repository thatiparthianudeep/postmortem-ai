"""
Postmortem AI - Upgraded FastAPI Server Entrypoint
Includes support for Dual-Mode Postmortem Generation (With Memory vs Standard LLM)
and Continuous Learning Loop (Commit Fixes to Hindsight Memory Bank).
"""

import os
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agent import PostmortemAgent, IncidentMemoryEngine, GROQ_API_KEY, HINDSIGHT_API_KEY
from mock_incidents import get_all_incidents, MOCK_INCIDENTS

app = FastAPI(
    title="Postmortem AI API - Hindsight Hackathon Edition",
    description="AI-driven Incident Postmortem & Root Cause Analysis Platform with Hindsight Memory Engine",
    version="2.0.0"
)

# Enable CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class AnalyzeRequest(BaseModel):
    title: str = Field(..., example="PostgreSQL Connection Pool Exhaustion")
    description: str = Field(..., example="Checkout API 500 error rates spiked during high traffic.")
    logs: str = Field(..., example="[ERROR] db.Pool: connection checkout timeout after 3000ms")
    severity: str = Field("P1", example="P0")
    affected_component: str = Field("Checkout Microservice", example="Auth Service")
    use_memory: bool = Field(True, example=True)

class ChatRequest(BaseModel):
    query: str = Field(..., example="How do we prevent connection pool exhaustion?")
    current_postmortem: Optional[Dict[str, Any]] = None

class SearchRequest(BaseModel):
    query: str = Field(..., example="Redis memory leak JWT")

class CommitMemoryRequest(BaseModel):
    incident_id: str = Field(..., example="INC-2026-AUTO")
    title: str = Field(..., example="PostgreSQL Connection Pool Exhaustion")
    severity: str = Field("P0", example="P0")
    category: str = Field("Database & Infrastructure", example="Database")
    component: str = Field("Checkout Service", example="Checkout Service")
    custom_fix: str = Field(..., example="Deployed PgBouncer sidecar with transaction pooling and 3s socket timeout")
    engineer_feedback: Optional[str] = Field("Verified fix in production", example="Verified")
    tags: List[str] = Field(["postgresql", "pgbouncer", "database", "p0"])

# API Endpoints
@app.get("/api/health")
def health_check():
    """Returns system status & API key configuration state."""
    has_groq = bool(GROQ_API_KEY and not GROQ_API_KEY.startswith("gsk_mock"))
    return {
        "status": "healthy",
        "service": "Postmortem AI Backend (Hindsight Hackathon Edition)",
        "groq_api_configured": has_groq,
        "hindsight_memory_bank_count": len(get_all_incidents()),
        "engine_mode": "Groq LLM + Hindsight Memory (Live)" if has_groq else "Hindsight Smart Memory Engine (Demo / Fallback)"
    }

@app.get("/api/incidents")
def list_incidents():
    """Fetch all seeded historical incident memories."""
    return {
        "count": len(MOCK_INCIDENTS),
        "incidents": MOCK_INCIDENTS
    }

@app.get("/api/incidents/{incident_id}")
def get_incident(incident_id: str):
    """Fetch details of a specific historical incident by ID."""
    incidents = get_all_incidents()
    for inc in incidents:
        if inc["id"].upper() == incident_id.upper():
            return inc
    raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found in memory bank")

@app.post("/api/search")
def search_memories(req: SearchRequest):
    """Search historical incident memories using Hindsight similarity engine."""
    results = IncidentMemoryEngine.search_similar_incidents(req.query, top_k=5)
    return {
        "query": req.query,
        "matches_found": len(results),
        "results": results
    }

@app.post("/api/analyze")
def analyze_incident(req: AnalyzeRequest):
    """Generate a postmortem report supporting dual-mode (With Memory vs Standard LLM)."""
    try:
        report = PostmortemAgent.generate_postmortem(
            title=req.title,
            description=req.description,
            logs=req.logs,
            severity=req.severity,
            affected_component=req.affected_component,
            use_memory=req.use_memory
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate postmortem: {str(e)}")

@app.post("/api/chat")
def chat_copilot(req: ChatRequest):
    """Ask follow-up questions to the Incident Copilot."""
    try:
        res = PostmortemAgent.ask_incident_copilot(
            user_query=req.query,
            current_postmortem=req.current_postmortem
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Copilot error: {str(e)}")

@app.post("/api/incidents/commit_memory")
def commit_memory(req: CommitMemoryRequest):
    """Continuous Learning Loop: Commit verified engineer resolution back to Hindsight Memory."""
    new_id = f"INC-2026-{len(MOCK_INCIDENTS) + 101}"
    
    new_inc = {
        "id": new_id,
        "title": req.title,
        "severity": req.severity,
        "category": req.category or "Verified Field Resolution",
        "timestamp": "2026-09-29T15:30:00Z",
        "duration_minutes": 25,
        "impact_summary": f"Verified in production: {req.custom_fix}",
        "summary": f"Engineer verified fix: {req.custom_fix}. Feedback: {req.engineer_feedback or 'Verified Resolution'}",
        "root_cause": f"Field Resolution: {req.custom_fix}",
        "timeline": [
            {"time": "00:00 UTC", "event": "Incident resolved & verified by engineer"},
            {"time": "00:05 UTC", "event": "Resolution committed permanently to Hindsight Memory Bank"}
        ],
        "five_whys": [
            f"Why was this resolution committed? -> Engineer confirmed fix: {req.custom_fix}",
            "Why was this fix effective? -> Prevented resource contention and stabilized service SLAs."
        ],
        "action_items": [
            {"priority": "P0", "task": req.custom_fix, "owner": "Verified Engineer", "status": "VERIFIED_COMMITTED"}
        ],
        "tags": list(set(req.tags + ["verified_commit", "hindsight_memory", req.component.lower().replace(" ", "_")]))
    }
    
    # Store permanently into Hindsight memory array
    MOCK_INCIDENTS.insert(0, new_inc)
    
    return {
        "success": True,
        "message": f"Incident {new_id} permanently committed to Hindsight Memory Bank. Agent knowledge updated.",
        "new_memory_count": len(MOCK_INCIDENTS),
        "committed_incident": new_inc
    }

# Static file serving for Frontend UI (CSS, JS, Assets & Index)
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")
    print(f"🚀 Starting Postmortem AI Hackathon Server on http://{host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=True)
