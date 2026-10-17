"""
ScamShield AI - Automated Multi-Modal Scenario Test Suite
Runs end-to-end evaluations on realistic scam vectors and verifies detection accuracy.
"""

import sys
import os

# Ensure UTF-8 console output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from detector import analyze_scam, analyze_url
from scam_database import SAMPLE_SCAMS

def run_tests():
    print("=" * 70)
    print("🛡️   SCAMSHIELD AI - MULTI-MODAL EVALUATION SUITE")
    print("=" * 70)
    
    passed = 0
    total = len(SAMPLE_SCAMS)

    for i, test in enumerate(SAMPLE_SCAMS, 1):
        print(f"\n[Test #{i}] Category: {test['category']} | Title: '{test['title']}'")
        print(f"Content: {test['content'][:85]}...")
        
        result = analyze_scam(test["content"], analysis_type=test["type"])
        
        score = result["risk_score"]
        level = result["risk_level"]
        is_scam = result["is_scam"]
        impersonated = result.get("brand_impersonated") or "None"
        tactics = [t["name"] for t in result.get("tactics", [])]

        print(f"➜ Risk Score:  {score}/100 [{level}]")
        print(f"➜ Brand Mimic: {impersonated}")
        print(f"➜ Key Tactics: {', '.join(tactics) if tactics else 'None (Clean)'}")
        print(f"➜ Primary Rec: {result['recommendations'][0]}")

        # Verification check
        if test["id"] == "legit_bank":
            if not is_scam and score < 30:
                print("✅ PASSED: Accurately identified clean benign message (False Positive Avoided).")
                passed += 1
            else:
                print("❌ FAILED: Benign message flagged as scam.")
        else:
            if is_scam and score >= 35:
                print("✅ PASSED: Threat successfully detected and categorized.")
                passed += 1
            else:
                print("❌ FAILED: Scam was not flagged with sufficient risk score.")

    print("\n" + "=" * 70)
    print(f"🏁 RESULTS: {passed}/{total} Scenarios Passed ({int((passed/total)*100)}% Accuracy)")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
