from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="Test Agent Server")

# Import agents
from agents import enrich_contact

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/agents/enrich")
async def enrich_endpoint(request: dict):
    contact_data = request.get('contact_data')
    enriched = enrich_contact(contact_data=contact_data)
    return {
        "status": "success",
        "enriched_contact": enriched,
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("test_agent_server:app", host="0.0.0.0", port=8001, reload=False)
