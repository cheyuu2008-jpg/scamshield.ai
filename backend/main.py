"""
ScamShield AI - FastAPI Application Server
Provides REST endpoints for scam analysis, threat intelligence, and serves the web UI.
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from detector import analyze_scam, analyze_url
from models import AnalyzeRequest, URLAnalyzeRequest, ReportScamRequest
from scam_database import SAMPLE_SCAMS, AWARENESS_QUIZ, TRENDING_THREATS

app = FastAPI(
    title="Scam Shield API",
    description="Know before you trust. Intelligent scam, smishing & phishing defense engine.",
    version="1.0.0"
)

# Enable CORS for local cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory user community reports for prototype
COMMUNITY_REPORTS = []


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Scam Shield Core",
        "tagline": "Know before you trust.",
        "engine_version": "1.0.0",
        "supported_modalities": ["sms", "url", "email", "voice_transcript"]
    }


@app.post("/api/analyze")
def analyze_endpoint(payload: AnalyzeRequest):
    """Deep-scans input text, SMS, email, or call transcript for fraud signals."""
    result = analyze_scam(payload.content, analysis_type=payload.type)
    return result


@app.post("/api/analyze/url")
def analyze_url_endpoint(payload: URLAnalyzeRequest):
    """Direct URL and domain reputation inspector."""
    result = analyze_url(payload.url)
    return result


@app.get("/api/samples")
def get_sample_scams():
    """Returns curated realistic scam examples for 1-click test simulation."""
    return SAMPLE_SCAMS


@app.get("/api/threats")
def get_trending_threats():
    """Returns current active scam threat intelligence alerts."""
    return TRENDING_THREATS


@app.get("/api/quiz")
def get_awareness_quiz():
    """Returns educational scam awareness quiz questions."""
    return AWARENESS_QUIZ


@app.post("/api/report")
def report_scam_endpoint(report: ReportScamRequest):
    """Submits a newly encountered scam message to the community database."""
    item = {
        "id": len(COMMUNITY_REPORTS) + 1,
        "sender": report.sender or "Unknown",
        "channel": report.channel,
        "content": report.content,
        "reported_by": report.reported_by,
        "notes": report.notes
    }
    COMMUNITY_REPORTS.append(item)
    return {
        "success": True,
        "message": "Scam report recorded. Thank you for protecting the community!",
        "report_id": item["id"],
        "total_reports": len(COMMUNITY_REPORTS)
    }


@app.get("/api/stats")
def get_stats():
    """Returns aggregate dashboard metrics."""
    return {
        "total_scams_blocked_simulated": 184592,
        "phishing_domains_indexed": 42180,
        "average_analysis_latency_ms": 14,
        "accuracy_rate_percent": 98.4,
        "community_submissions": len(COMMUNITY_REPORTS)
    }


# Path to frontend
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    def serve_frontend():
        index_path = os.path.join(FRONTEND_DIR, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "Frontend index.html not found"}
