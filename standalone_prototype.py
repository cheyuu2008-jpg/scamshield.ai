"""
Project Title: Scam Shield
Tagline: Know before you trust.
Problem: Modern phishing, SMS fraud, and spoofing scams are becoming increasingly sophisticated.
Average users struggle to evaluate suspicious messages, urgency-based demands, and unknown URLs in real time.

Lightweight Single-File Prototype:
Contains both the FastAPI Backend Engine and the Embedded Frontend UI.
Run: python standalone_prototype.py
Visit: http://127.0.0.1:8000
"""

import re
import sys
import os
import urllib.parse
from typing import Dict, Any, List

# Ensure UTF-8 console output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("Please install requirements: pip install fastapi uvicorn pydantic")
    sys.exit(1)

app = FastAPI(title="Scam Shield", description="Know before you trust.")

# --- DETECTION HEURISTICS ---
SUSPICIOUS_TLDS = {".xyz", ".top", ".click", ".buzz", ".work", ".surf", ".cam", ".vip"}
KNOWN_BRANDS = ["chase", "wells fargo", "usps", "netflix", "amazon", "apple", "paypal", "geek squad"]

PATTERNS = [
    {
        "category": "Artificial Urgency",
        "regex": r"\b(immediately|within\s+(?:24|12|1|2|48)\s*hours?|urgent|action\s+required|suspended|arrest\s+warrant|final\s+notice)\b",
        "weight": 28,
        "detail": "Pressures victim to act quickly before verifying authenticity."
    },
    {
        "category": "Untraceable Payment",
        "regex": r"\b(gift\s*card|apple\s*gift\s*card|target\s*card|bitcoin|crypto|wire\s*transfer|zelle)\b",
        "weight": 35,
        "detail": "Demands payment via non-refundable or anonymous channels."
    },
    {
        "category": "Credential Harvesting",
        "regex": r"\b(verify\s+your\s+(?:account|password|identity)|enter\s+your\s+otp|send\s+the\s+code|ssn|cvv|pin)\b",
        "weight": 32,
        "detail": "Attempts to elicit sensitive passwords, PINs, or one-time codes."
    },
    {
        "category": "Delivery / Fee Bait",
        "regex": r"\b(package\s+(?:on\s+hold|cannot\s+be\s+delivered)|redelivery\s+fee|unpaid\s+customs)\b",
        "weight": 25,
        "detail": "Fake courier alert intended to harvest credit card details."
    },
    {
        "category": "Impersonation",
        "regex": r"\b(hi\s+mom|hi\s+dad|broke\s+my\s+phone|this\s+is\s+my\s+new\s+number)\b",
        "weight": 30,
        "detail": "Simulates a distressed family member from an unknown number."
    }
]

def analyze_input(text: str) -> Dict[str, Any]:
    score = 0
    matched_flags = []
    highlights = []
    brand_detected = None

    # 1. Match linguistic and urgency triggers
    for p in PATTERNS:
        matches = list(re.finditer(p["regex"], text, re.IGNORECASE))
        if matches:
            score += p["weight"]
            matched_flags.append({"tactic": p["category"], "reason": p["detail"]})
            for m in matches:
                highlights.append(m.group(0))

    # 2. Check for suspicious URLs
    urls = re.findall(r"(?:https?:\/\/|www\.)[^\s<>\"']+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}(?:\/[^\s<>\"']*)?", text)
    url_flags = []
    for u in urls:
        parsed = urllib.parse.urlparse(u if "://" in u else "http://" + u)
        netloc = parsed.netloc.lower()
        if any(netloc.endswith(tld) for tld in SUSPICIOUS_TLDS):
            score += 35
            url_flags.append(f"High-Risk disposable TLD in link ({netloc})")
            highlights.append(u)
        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", netloc):
            score += 40
            url_flags.append(f"Naked IP address used ({netloc})")
            highlights.append(u)

    # 3. Check for brand mimicry
    for b in KNOWN_BRANDS:
        if b in text.lower():
            brand_detected = b.title()

    score = min(100, score)

    # Determine risk level
    if score >= 70:
        level = "CRITICAL HAZARD"
        color = "#ef4444"
        is_scam = True
    elif score >= 35:
        level = "SUSPICIOUS / ELEVATED RISK"
        color = "#f59e0b"
        is_scam = True
    else:
        level = "SAFE / CLEAN MESSAGE"
        color = "#10b981"
        is_scam = False

    recommendations = []
    if is_scam:
        recommendations.append("⛔ DO NOT click any links, open attachments, or call provided numbers.")
        if brand_detected:
            recommendations.append(f"🔍 Directly visit the official {brand_detected} app or website independently.")
        recommendations.append("🔒 Never disclose SMS one-time passcodes (OTPs), PINs, or passwords.")
        recommendations.append("🛡️ Block sender and report message to consumer fraud authorities.")
    else:
        recommendations.append("✅ No obvious scam patterns found. Always verify the sender domain.")

    return {
        "risk_score": score,
        "risk_level": level,
        "color": color,
        "is_scam": is_scam,
        "brand_detected": brand_detected,
        "matched_flags": matched_flags,
        "url_flags": url_flags,
        "highlights": list(set(highlights)),
        "recommendations": recommendations
    }

class AnalyzeRequest(BaseModel):
    content: str

@app.post("/api/analyze")
def analyze_endpoint(req: AnalyzeRequest):
    return analyze_input(req.content)

@app.get("/api/health")
def health():
    return {"status": "active", "service": "Scam Shield", "tagline": "Know before you trust."}

# --- LIGHTWEIGHT EMBEDDED UI ---
HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Scam Shield - Know before you trust.</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    :root {
      --bg: #0b1120; --card: #152238; --border: #233554;
      --text: #f1f5f9; --muted: #94a3b8; --cyan: #38bdf8;
      --safe: #10b981; --warning: #f59e0b; --danger: #ef4444;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
    body { background: var(--bg); color: var(--text); padding: 30px 15px; }
    .container { max-width: 760px; margin: 0 auto; }
    .header { text-align: center; margin-bottom: 24px; }
    .header h1 { font-size: 2rem; color: #fff; display: flex; align-items: center; justify-content: center; gap: 8px; }
    .header p { color: var(--cyan); font-size: 1rem; font-weight: 500; margin-top: 4px; }
    .card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 8px 24px rgba(0,0,0,0.3); }
    .samples { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px; }
    .sample-btn { background: #0f172a; border: 1px solid var(--border); color: var(--muted); padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; cursor: pointer; transition: 0.2s; }
    .sample-btn:hover { color: var(--cyan); border-color: var(--cyan); }
    textarea { width: 100%; height: 120px; background: #080d1a; border: 1px solid var(--border); border-radius: 8px; padding: 12px; color: #fff; font-size: 0.95rem; resize: vertical; }
    textarea:focus { outline: none; border-color: var(--cyan); }
    .btn-row { display: flex; gap: 10px; margin-top: 12px; }
    .btn-scan { flex: 1; background: linear-gradient(135deg, #0284c7, #2563eb); color: #fff; border: none; padding: 12px; border-radius: 8px; font-weight: 700; cursor: pointer; font-size: 0.95rem; }
    .btn-clear { background: transparent; border: 1px solid var(--border); color: var(--muted); padding: 12px 18px; border-radius: 8px; cursor: pointer; }
    .results { display: none; margin-top: 20px; }
    .meter-row { display: flex; align-items: center; justify-content: space-between; padding-bottom: 14px; border-bottom: 1px solid var(--border); margin-bottom: 14px; }
    .score-badge { font-size: 1.8rem; font-weight: 900; }
    .risk-tag { padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 800; text-transform: uppercase; }
    .flag-list { list-style: none; margin: 12px 0; }
    .flag-item { background: #0d1729; border-left: 3px solid var(--danger); padding: 8px 12px; margin-bottom: 6px; border-radius: 4px; font-size: 0.85rem; }
    .rec-box { background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 12px; margin-top: 14px; }
    .rec-title { font-weight: 700; color: #34d399; font-size: 0.85rem; margin-bottom: 6px; }
    .rec-item { font-size: 0.82rem; color: #cbd5e1; margin-bottom: 4px; }
    mark { background: rgba(239, 68, 68, 0.35); color: #fca5a5; padding: 1px 4px; border-radius: 3px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🛡️ Scam Shield</h1>
      <p>Know before you trust.</p>
    </div>

    <div class="card">
      <div style="font-size: 0.78rem; color: var(--muted); margin-bottom: 8px; font-weight: 700;">TEST SAMPLES:</div>
      <div class="samples">
        <button class="sample-btn" onclick="setSample('Chase Bank SMS')">Chase Fake SMS</button>
        <button class="sample-btn" onclick="setSample('USPS Redelivery')">USPS Delivery Scam</button>
        <button class="sample-btn" onclick="setSample('Hi Mom')">WhatsApp 'Hi Mom'</button>
        <button class="sample-btn" onclick="setSample('Clean 2FA')">Clean Bank OTP (Safe)</button>
      </div>

      <textarea id="inputText" placeholder="Paste suspicious SMS, urgent email, or unknown URL here..."></textarea>
      
      <div class="btn-row">
        <button class="btn-scan" onclick="scan()">⚡ Analyze with Scam Shield</button>
        <button class="btn-clear" onclick="clearAll()">Clear</button>
      </div>
    </div>

    <div id="results" class="card results">
      <div class="meter-row">
        <div>
          <div style="font-size: 0.75rem; color: var(--muted); text-transform: uppercase;">Threat Index</div>
          <div id="scoreText" class="score-badge">0/100</div>
        </div>
        <div id="riskBadge" class="risk-tag">ANALYZING</div>
      </div>

      <div id="brandBox" style="font-size: 0.85rem; color: #fca5a5; margin-bottom: 10px; font-weight: 600; display: none;"></div>

      <div style="font-size: 0.8rem; color: var(--muted); margin-bottom: 6px; font-weight: 700;">IDENTIFIED RED FLAGS:</div>
      <div id="flagsList" class="flag-list"></div>

      <div class="rec-box">
        <div class="rec-title">🛡️ RECOMMENDED NEXT ACTIONS:</div>
        <div id="recList"></div>
      </div>
    </div>
  </div>

  <script>
    const SAMPLES = {
      'Chase Bank SMS': 'CHASE ALERT: Unauthorized charge of $1,429.50 on debit card. Verify identity immediately to avoid suspension: https://chase-security-verify-auth.xyz/login?ref=9102',
      'USPS Redelivery': 'USPS Notification: Parcel delivery failed due to incomplete address. Please update address and pay $1.99 redelivery fee within 24 hours: https://usps-redelivery-tracking.top/parcel',
      'Hi Mom': 'Hi mom! I broke my phone in water and this is my new number. I need to pay an urgent bill right now. Can you wire $850 to this Zelle or Apple Gift Card? Please don\\\'t tell dad yet!',
      'Clean 2FA': 'Wells Fargo: Your one-time verification code is 492019. Valid for 10 minutes. Wells Fargo will NEVER call or text asking for this code.'
    };

    function setSample(name) {
      document.getElementById('inputText').value = SAMPLES[name];
      scan();
    }

    function clearAll() {
      document.getElementById('inputText').value = '';
      document.getElementById('results').style.display = 'none';
    }

    async function scan() {
      const text = document.getElementById('inputText').value.trim();
      if (!text) return;

      try {
        const res = await fetch('/api/analyze', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ content: text })
        });
        const data = await res.json();
        render(data);
      } catch (e) {
        alert('API error or server offline');
      }
    }

    function render(data) {
      const r = document.getElementById('results');
      r.style.display = 'block';

      const s = document.getElementById('scoreText');
      s.textContent = data.risk_score + '/100';
      s.style.color = data.color;

      const badge = document.getElementById('riskBadge');
      badge.textContent = data.risk_level;
      badge.style.backgroundColor = data.color + '22';
      badge.style.color = data.color;
      badge.style.border = '1px solid ' + data.color;

      const bBox = document.getElementById('brandBox');
      if (data.brand_detected) {
        bBox.style.display = 'block';
        bBox.innerHTML = '⚠️ <strong>Suspected Impersonation:</strong> Deceptively mimicking ' + data.brand_detected;
      } else {
        bBox.style.display = 'none';
      }

      const fList = document.getElementById('flagsList');
      fList.innerHTML = '';
      if (data.matched_flags.length === 0 && data.url_flags.length === 0) {
        fList.innerHTML = '<div style="font-size:0.82rem; color:var(--muted);">No predatory red flags detected.</div>';
      } else {
        data.matched_flags.forEach(f => {
          fList.innerHTML += '<div class="flag-item"><strong>🚩 ' + f.tactic + ':</strong> ' + f.reason + '</div>';
        });
        data.url_flags.forEach(u => {
          fList.innerHTML += '<div class="flag-item"><strong>🌐 URL Anomaly:</strong> ' + u + '</div>';
        });
      }

      const recs = document.getElementById('recList');
      recs.innerHTML = '';
      data.recommendations.forEach(rec => {
        recs.innerHTML += '<div class="rec-item">' + rec + '</div>';
      });
    }
  </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(content=HTML_PAGE)

if __name__ == "__main__":
    print("=" * 60)
    print("🛡️  Scam Shield - Know before you trust.")
    print("=" * 60)
    print("Server running on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
