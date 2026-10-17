"""
Pydantic Schemas for ScamShield AI REST API.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class AnalyzeRequest(BaseModel):
    content: str = Field(..., description="Message text, transcript, or URL to analyze")
    type: str = Field(default="text", description="'text', 'url', 'email', or 'call'")

class ReportScamRequest(BaseModel):
    sender: Optional[str] = None
    content: str
    channel: str = "sms"
    reported_by: Optional[str] = "Anonymous"
    notes: Optional[str] = ""

class URLAnalyzeRequest(BaseModel):
    url: str

class AnalyzeResponse(BaseModel):
    risk_score: int
    risk_level: str
    status_color: str
    is_scam: bool
    confidence: int
    primary_category: str
    brand_impersonated: Optional[str] = None
    tactics: List[Dict[str, Any]]
    highlights: List[Dict[str, Any]]
    url_analysis: List[Dict[str, Any]]
    recommendations: List[str]
    stats: Dict[str, Any]
