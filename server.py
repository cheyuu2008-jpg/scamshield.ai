"""
ScamShield AI - FastAPI Backend & Web Server
Serves the interactive threat defense dashboard and provides real-time fraud analysis.
Compatible with Vercel Serverless Python and local execution.
"""

import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from analyzer import ScamShieldAnalyzer

app = FastAPI(
    title="ScamShield AI",
    description="Real-Time Fraud & Social Engineering Interceptor",
    version="1.0.0"
)

# Enable CORS for cross-origin integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
analyzer = ScamShieldAnalyzer()


@app.get("/")
def serve_home():
    """Serves the main ScamShield AI interactive web dashboard."""
    index_file = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file, media_type="text/html")
    return {"message": "ScamShield AI is running. index.html not found."}


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "service": "ScamShield AI",
        "version": "1.0.0"
    }


@app.get("/api/scenarios")
def get_scenarios():
    scenarios_file = os.path.join(BASE_DIR, "demo_scenarios.json")
    if os.path.exists(scenarios_file):
        with open(scenarios_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"scenarios": []}


@app.post("/api/analyze")
async def analyze_message(request: Request):
    """Deep multi-vector analysis endpoint."""
    try:
        payload = await request.json()
        text = payload.get("text", "")
        sender = payload.get("sender", "")
        result = analyzer.analyze(text, sender)
        return result
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


if __name__ == "__main__":
    try:
        import uvicorn
        print("Starting ScamShield AI on http://localhost:8080...")
        uvicorn.run("server:app", host="0.0.0.0", port=8080, reload=True)
    except ImportError:
        # Fallback to standard library
        import http.server
        import socketserver
        PORT = 8080
        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            print(f"Fallback server running at http://localhost:{PORT}")
            httpd.serve_forever()
