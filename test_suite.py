"""
ScamShield AI - Automated Verification & Test Suite
Runs end-to-end tests across all detection vectors and REST API endpoints.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from detector import analyze_scam, analyze_url
from main import health_check, analyze_endpoint, analyze_url_endpoint, get_sample_scams, get_awareness_quiz, get_stats
from models import AnalyzeRequest, URLAnalyzeRequest

def run_all_tests():
    print("=" * 65)
    print("[*] RUNNING SCAMSHIELD AI VERIFICATION SUITE")
    print("=" * 65)

    passed = 0
    total = 0

    # Test 1: Health check endpoint
    total += 1
    health = health_check()
    assert health["status"] == "healthy", "Health check failed"
    print("[OK] [1/7] Health Endpoint: OK")
    passed += 1

    # Test 2: Smishing detection with suspicious domain
    total += 1
    smish = analyze_scam(
        "CHASE ALERT: Unauthorized charge of $1,429 detected. Verify identity immediately: https://chase-security-verify-auth.xyz",
        analysis_type="text"
    )
    assert smish["is_scam"] is True, "Smishing detection failed"
    assert smish["risk_score"] >= 80, f"Expected high risk score, got {smish['risk_score']}"
    assert smish["brand_impersonated"] == "Chase", f"Expected Chase, got {smish['brand_impersonated']}"
    print(f"[OK] [2/7] Smishing Detection: OK (Score: {smish['risk_score']}, Brand: {smish['brand_impersonated']})")
    passed += 1

    # Test 3: Raw IP address & Typosquatting in URL Analyzer
    total += 1
    url_res = analyze_url("http://192.168.1.50/login/paypal-secure-verify")
    assert url_res["url_risk_score"] >= 70, f"Expected high URL risk, got {url_res['url_risk_score']}"
    assert any(i["factor"] == "Raw IP Address" for i in url_res["issues"])
    print(f"[OK] [3/7] Phishing URL & IP Host Detection: OK (Score: {url_res['url_risk_score']})")
    passed += 1

    # Test 4: Extortion voice call transcript
    total += 1
    call_res = analyze_scam(
        "This is Officer Davis from IRS. Active arrest warrant issued. Stay on the line right now. Pay via gift cards.",
        analysis_type="call"
    )
    assert call_res["is_scam"] is True
    assert any("Urgency" in t["name"] or "Payment" in t["name"] or "Coercive" in t["name"] for t in call_res["tactics"])
    print(f"[OK] [4/7] Call Transcript & Extortion Detection: OK (Score: {call_res['risk_score']})")
    passed += 1

    # Test 5: Clean control message (False Positive Prevention)
    total += 1
    clean_msg = analyze_scam(
        "Wells Fargo: Your one-time verification code is 492019. Expires in 10 minutes. Do not share.",
        analysis_type="text"
    )
    assert clean_msg["is_scam"] is False, f"Clean message falsely flagged as scam (Score: {clean_msg['risk_score']})"
    assert clean_msg["risk_score"] <= 30
    print(f"[OK] [5/7] False Positive Prevention (Clean Control): OK (Score: {clean_msg['risk_score']})")
    passed += 1

    # Test 6: Database & Samples
    total += 1
    samples = get_sample_scams()
    quiz = get_awareness_quiz()
    assert len(samples) >= 5, "Sample scams collection incomplete"
    assert len(quiz) >= 3, "Quiz questions incomplete"
    print(f"[OK] [6/7] Curated Threat Database & Quiz: OK ({len(samples)} samples, {len(quiz)} quiz scenarios)")
    passed += 1

    # Test 7: API Request Model Processing
    total += 1
    req = AnalyzeRequest(content="Update delivery address at https://usps-redelivery.top", type="text")
    api_out = analyze_endpoint(req)
    assert api_out["is_scam"] is True
    assert "Usps" in (api_out["brand_impersonated"] or "")
    print(f"[OK] [7/7] REST API Pydantic Handler: OK (Score: {api_out['risk_score']})")
    passed += 1

    print("=" * 65)
    print(f"[SUCCESS] ALL {passed}/{total} VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 65)

if __name__ == "__main__":
    run_all_tests()
