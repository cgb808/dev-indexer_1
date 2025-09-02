from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ZenGlow UI Development Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "UI Development Server"}

@app.get("/metrics/dashboard")
async def get_metrics():
    return {
        "ts": "2025-01-31T12:00:00Z",
        "runtime_stats": {
            "response_time": [{"metric": "response_time", "window": "5m", "count": 150, "avg": 245, "p50": 230, "p95": 450}],
            "cpu_usage": [{"metric": "cpu_usage", "window": "5m", "count": 150, "avg": 35, "p50": 32, "p95": 65}],
            "memory_usage": [{"metric": "memory_usage", "window": "5m", "count": 150, "avg": 512, "p50": 498, "p95": 756}]
        },
        "queue": [
            {"status": "processing", "count": 2},
            {"status": "pending", "count": 5},
            {"status": "completed", "count": 143}
        ],
        "queue_oldest_pending_age_s": 45
    }

@app.post("/rag/query")
async def rag_query(query: dict):
    return {
        "response": "This is a mock response for UI development. The full RAG system will be integrated later.",
        "confidence": 0.85,
        "sources": ["mock_source_1", "mock_source_2"]
    }

@app.get("/config")
async def get_config():
    return {
        "backends": ["auto", "edge", "ollama", "leonardo"],
        "voices": ["amy", "jarvis", "leonardo", "alan"],
        "features": {
            "tts": True,
            "stt": True,
            "rag": True,
            "metrics": True
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
