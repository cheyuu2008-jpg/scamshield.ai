"""
ScamShield AI - Intelligent Scam & Fraud Detection Engine
Multi-modal analysis for SMS, URLs, Emails, Call Transcripts, and Social Engineering.
"""

import re
import urllib.parse
from typing import Dict, List, Any, Optional

# Known legitimate high-profile domains for typo-squatting detection
POPULAR_BRANDS = {
    "paypal": ["paypal.com"],
    "apple": ["apple.com", "icloud.com"],
    "amazon": ["amazon.com", "amazon.co.uk", "amazon.in"],
    "netflix": ["netflix.com"],
    "google": ["google.com", "gmail.com"],
    "microsoft": ["microsoft.com", "live.com", "outlook.com"],
    "chase": ["chase.com"],
    "wellsfargo": ["wellsfargo.com"],
    "bankofamerica": ["bankofamerica.com"],
    "usps": ["usps.com"],
    "fedex": ["fedex.com"],
    "dhl": ["dhl.com"],
    "ups": ["ups.com"],
    "coinbase": ["coinbase.com"],
    "binance": ["binance.com"],
    "meta": ["facebook.com", "instagram.com", "whatsapp.com"]
}

SUSPICIOUS_TLDS = {
    ".xyz", ".top", ".click", ".buzz", ".work", ".loan", ".surf",
    ".fit", ".gq", ".ml", ".cf", ".tk", ".ga", ".rest", ".monster",
    ".icu", ".stream", ".cam", ".vip", ".bid"
}

URL_SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "is.gd", "buff.ly", "ow.ly", "rb.gy"}

# Weighted scam linguistic patterns
SCAM_INDICATORS = [
    # Urgency & Panic Triggers
    {
        "id": "urgency_panic",
        "category": "Artificial Urgency",
        "weight": 25,
        "regex": r"\b(immediately|within\s+(?:24|12|1|2|48)\s*hours?|final\s+notice|action\s+required|urgent|critical\s+alert|suspended|terminated|deactivated\s+today|warrant\s+issued|arrest)\b",
        "explanation": "Pressures victim to react impulsively without verifying facts."
    },
    # Payment / Wire / Gift Card Extortion
    {
        "id": "untraceable_payment",
        "category": "Untraceable Payment Demands",
        "weight": 35,
        "regex": r"\b(gift\s*card|apple\s*gift\s*cards?|google\s*play\s*card|steam\s*card|target\s*card|bitcoin|crypto|btc\s+wallet|western\s*union|moneygram|wire\s*transfer|zelle\s+me)\b",
        "explanation": "Demands payment via irreversible or untraceable channels."
    },
    # Credential & Verification Harvesting
    {
        "id": "credential_harvesting",
        "category": "Credential Harvesting",
        "weight": 30,
        "regex": r"\b(verify\s+your\s+(?:account|password|identity|pin|ssn|social\s*security)|enter\s+your\s+otp|send\s+the\s+code|confirm\s+your\s+card|cvv|3-digit\s+code|login\s+here\s+to\s+restore)\b",
        "explanation": "Attempts to elicit confidential security credentials, passwords, or one-time passcodes."
    },
    # Greed / Lottery / Too Good to Be True
    {
        "id": "too_good_to_be_true",
        "category": "Lottery / Prize Lure",
        "weight": 30,
        "regex": r"\b(you\s+(?:have\s+)?won|lottery|winner|claim\s+your\s+(?:\$|prize|reward)|100%\s*guaranteed\s+(?:profit|return)|double\s+your\s+(?:money|crypto)|exclusive\s+investment\s+opportunity|congratulations!\s*you\s*are\s*selected)\b",
        "explanation": "Dangles unrealistic financial gains or fraudulent prize notifications."
    },
    # Tech Support / Remote Access
    {
        "id": "tech_support_takeover",
        "category": "Tech Support Hijack",
        "weight": 35,
        "regex": r"\b(anydesk|teamviewer|ultraviewer|quick\s*assist|remote\s*access|windows\s*defender\s*alert|virus\s+detected|geek\s*squad|toll\s*free\s*help\s*desk|call\s+(?:\+?1[-\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\s+to\s+cancel)\b",
        "explanation": "Instructs caller to install remote administration tools or call fake helpline."
    },
    # Delivery & Courier Smishing
    {
        "id": "delivery_smishing",
        "category": "Package / Courier Smishing",
        "weight": 25,
        "regex": r"\b(package\s+(?:on\s+hold|cannot\s+be\s+delivered|pending)|address\s+(?:incomplete|confirmation\s+needed)|redelivery\s+fee|unpaid\s+customs\s+fee|update\s+delivery\s+address)\b",
        "explanation": "Falsely claims an undelivered parcel to trick user into paying a fee or submitting card info."
    },
    # Family Impersonation ("Hi Mom / Hi Dad")
    {
        "id": "family_impersonation",
        "category": "Emergency Impersonation",
        "weight": 30,
        "regex": r"\b(hi\s+mom|hi\s+dad|hello\s+mum|broke\s+my\s+phone|this\s+is\s+my\s+new\s+number|can\s+you\s+pay\s+this\s+bill\s+for\s+me|don'?t\s+tell\s+dad|lost\s+my\s+wallet)\b",
        "explanation": "Impersonates a distressed child or relative using an unknown phone number."
    },
    # Bank / Transaction Alert Fraud
    {
        "id": "bank_fraud_alert",
        "category": "Fake Bank Alert",
        "weight": 25,
        "regex": r"\b(unrecognized\s+charge|transaction\s+of\s+\$?\d+|did\s+you\s+authorize|reply\s+no\s+to\s+cancel|fraud\s+prevention\s+team|card\s+temporarily\s+blocked)\b",
        "explanation": "Simulates banking security SMS to funnel victim into fake dispute call or link."
    }
]


def extract_urls(text: str) -> List[str]:
    """Finds all HTTP/HTTPS and bare domain links in text."""
    url_pattern = r"(?:https?:\/\/|www\.)[^\s<>\"']+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}(?:\/[^\s<>\"']*)?"
    matches = re.findall(url_pattern, text)
    cleaned = []
    for m in matches:
        if "." in m and not m.endswith((".", ",")):
            if not m.startswith(("http://", "https://")):
                cleaned.append("https://" + m)
            else:
                cleaned.append(m)
    return list(dict.fromkeys(cleaned))


def analyze_url(url: str) -> Dict[str, Any]:
    """Inspects a URL for deceptive patterns, typosquatting, high-risk TLDs, and path anomalies."""
    issues = []
    score = 0
    brand_impersonated = None

    try:
        parsed = urllib.parse.urlparse(url)
        netloc = parsed.netloc.lower()
        # strip port if present
        if ":" in netloc:
            netloc = netloc.split(":")[0]

        # Check IP address as host
        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", netloc):
            score += 45
            issues.append({
                "factor": "Raw IP Address",
                "severity": "CRITICAL",
                "detail": f"Domain is a raw IP ({netloc}), commonly used to bypass domain reputation checks."
            })

        # Check Shortened URLs
        if any(shortener in netloc for shortener in URL_SHORTENERS):
            score += 20
            issues.append({
                "factor": "URL Shortener Detected",
                "severity": "MEDIUM",
                "detail": f"Shortened link ({netloc}) hides true final destination."
            })

        # Check Suspicious TLD
        for tld in SUSPICIOUS_TLDS:
            if netloc.endswith(tld):
                score += 35
                issues.append({
                    "factor": "High-Risk TLD Extension",
                    "severity": "HIGH",
                    "detail": f"Domain uses '{tld}', an extension frequently utilized by disposable phishing campaigns."
                })
                break

        # Check Brand Spoofing / Typosquatting in Domain or Subdomain
        for brand, valid_domains in POPULAR_BRANDS.items():
            if brand in netloc:
                # Is it an exact valid domain?
                is_legit = any(netloc == vd or netloc.endswith("." + vd) for vd in valid_domains)
                if not is_legit:
                    brand_impersonated = brand.title()
                    score += 45
                    issues.append({
                        "factor": f"Suspected {brand.title()} Impersonation",
                        "severity": "CRITICAL",
                        "detail": f"Host '{netloc}' contains brand '{brand}' but is NOT an official domain ({', '.join(valid_domains)})."
                    })

        # Check for excessive hyphens or deceptive subdomain chaining
        if netloc.count("-") >= 2:
            score += 15
            issues.append({
                "factor": "Suspicious Hyphen Chaining",
                "severity": "MEDIUM",
                "detail": f"Domain contains {netloc.count('-')} hyphens, commonly seen in spoofed landing pages."
            })

        subdomains = netloc.split(".")
        if len(subdomains) >= 4 and not is_legit_domain(netloc):
            score += 20
            issues.append({
                "factor": "Excessive Subdomain Stacking",
                "severity": "HIGH",
                "detail": "Multiple layered subdomains configured to deceive mobile browser address bars."
            })

        # Suspicious keywords in path
        path_lower = parsed.path.lower()
        if re.search(r"(login|verify|secure|update|banking|account|signin|wallet|claim)", path_lower) and score > 0:
            score += 15
            issues.append({
                "factor": "Credential Lure in Path",
                "severity": "HIGH",
                "detail": f"URL path matches sensitive login or verification keywords: '{parsed.path}'."
            })

    except Exception as e:
        issues.append({"factor": "Malformed URL", "severity": "MEDIUM", "detail": str(e)})

    score = min(100, score)
    return {
        "url": url,
        "url_risk_score": score,
        "is_suspicious": score >= 40,
        "issues": issues,
        "brand_impersonated": brand_impersonated
    }


def is_legit_domain(netloc: str) -> bool:
    """Helper to check if domain belongs to official major providers."""
    for valid_domains in POPULAR_BRANDS.values():
        if any(netloc == vd or netloc.endswith("." + vd) for vd in valid_domains):
            return True
    return False


def analyze_scam(content: str, analysis_type: str = "text") -> Dict[str, Any]:
    """
    Main evaluation pipeline:
    Analyzes message content, detects social engineering patterns,
    inspects extracted URLs, calculates composite risk score, and provides explainable countermeasures.
    """
    if not content or not content.strip():
        return {
            "risk_score": 0,
            "risk_level": "SAFE",
            "category": "Empty Input",
            "confidence": 100,
            "tactics": [],
            "highlights": [],
            "url_analysis": [],
            "recommendations": ["Enter or paste a message, email, or URL to begin detection."],
            "is_scam": False
        }

    raw_score = 0
    matched_tactics = []
    highlights = []
    detected_categories = set()
    brand_impersonated = None

    # 1. Linguistic Pattern Matching
    for ind in SCAM_INDICATORS:
        found_spans = list(re.finditer(ind["regex"], content, re.IGNORECASE))
        if found_spans:
            raw_score += ind["weight"]
            matched_tactics.append({
                "name": ind["category"],
                "explanation": ind["explanation"]
            })
            detected_categories.add(ind["category"])
            for match in found_spans:
                highlights.append({
                    "phrase": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "reason": ind["category"]
                })

    # 2. Extract and Deep-Inspect URLs
    extracted = extract_urls(content)
    url_reports = []
    for u in extracted:
        u_rep = analyze_url(u)
        url_reports.append(u_rep)
        if u_rep["url_risk_score"] > 0:
            raw_score += int(u_rep["url_risk_score"] * 0.75)
            if u_rep["brand_impersonated"]:
                brand_impersonated = u_rep["brand_impersonated"]

    # 3. Type-Specific Modifiers
    lower_content = content.lower()

    if analysis_type == "call":
        # Voice transcripts often involve threats of arrest or continuous stay-on-the-line tactics
        if re.search(r"(stay\s+on\s+the\s+(?:line|phone)|do\s+not\s+hang\s+up|police\s+at\s+your\s+door)", lower_content):
            raw_score += 30
            matched_tactics.append({
                "name": "Coercive Pressure / Hostage Tactics",
                "explanation": "Demanding victim stay on phone prevents them from verifying claim with family or authorities."
            })

        # Government & Law Enforcement Impersonation
        if re.search(r"\b(irs|internal\s+revenue|fbi|sheriff|social\s+security\s+administration|customs\s+and\s+border|department\s+of\s+justice)\b", lower_content):
            raw_score += 35
            matched_tactics.append({
                "name": "Authority & Law Enforcement Spoofing",
                "explanation": "Impersonates government or legal agencies to induce extreme panic and compliance."
            })

        # Telephony Cryptographic Attestation (STIR/SHAKEN)
        if re.search(r"\b(attestation\s*c|gateway\s+attestation|unverified\s+caller\s*id|spoofed\s+number)\b", lower_content):
            raw_score += 30
            matched_tactics.append({
                "name": "Unverified Telephony Gateway (STIR/SHAKEN Attestation C)",
                "explanation": "Call originated from an untrusted transit gateway with no cryptographic caller ID proof."
            })
        elif re.search(r"\b(attestation\s*a|verified\s+caller\s*id)\b", lower_content):
            raw_score = max(0, raw_score - 20)
    elif analysis_type == "email":
        # BEC / CEO Fraud indicators
        if re.search(r"(confidential\s+request|are\s+you\s+at\s+your\s+desk|need\s+you\s+to\s+handle\s+a\s+wire|payroll\s+update)", lower_content):
            raw_score += 25
            matched_tactics.append({
                "name": "Executive / BEC Impersonation",
                "explanation": "Mimics corporate leadership targeting employees to execute unauthorized transfers."
            })

    # 4. Check for Brand Mention without Official Domain
    for brand in POPULAR_BRANDS:
        if brand in lower_content:
            # If a brand is mentioned and there are suspicious links or urgency
            if (url_reports and any(r["url_risk_score"] >= 30 for r in url_reports)) or raw_score >= 35:
                if not brand_impersonated:
                    brand_impersonated = brand.title()

    # Normalize score between 0 and 100
    risk_score = min(100, max(0, raw_score))

    # Determine Risk Level
    if risk_score >= 70:
        risk_level = "CRITICAL HAZARD"
        is_scam = True
        status_color = "#ef4444"
    elif risk_score >= 35:
        risk_level = "SUSPICIOUS / ELEVATED RISK"
        is_scam = True
        status_color = "#f59e0b"
    elif risk_score > 10:
        risk_level = "LOW RISK / PROCEED WITH CAUTION"
        is_scam = False
        status_color = "#3b82f6"
    else:
        risk_level = "SAFE / NO SIGNIFICANT THREAT"
        is_scam = False
        status_color = "#10b981"

    # Primary Category Determination
    if matched_tactics:
        primary_category = matched_tactics[0]["name"]
    elif url_reports and any(u["is_suspicious"] for u in url_reports):
        primary_category = "Phishing Link Threat"
    else:
        primary_category = "General / Clean Message"

    # Actionable Countermeasures based on threat profile
    recommendations = generate_recommendations(risk_level, detected_categories, brand_impersonated, url_reports)

    # Confidence calculation
    confidence = calculate_confidence(content, matched_tactics, url_reports)

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "status_color": status_color,
        "is_scam": is_scam,
        "confidence": confidence,
        "primary_category": primary_category,
        "brand_impersonated": brand_impersonated,
        "tactics": matched_tactics,
        "highlights": highlights,
        "url_analysis": url_reports,
        "recommendations": recommendations,
        "stats": {
            "threat_signals_found": len(matched_tactics),
            "urls_scanned": len(url_reports),
            "suspicious_urls": sum(1 for u in url_reports if u["is_suspicious"])
        }
    }


def generate_recommendations(
    risk_level: str,
    categories: set,
    brand_impersonated: Optional[str],
    url_reports: List[Dict[str, Any]]
) -> List[str]:
    """Builds prioritized defensive instructions for the user."""
    recs = []

    if "CRITICAL" in risk_level or "SUSPICIOUS" in risk_level:
        recs.append("⛔ DO NOT click any links, download attachments, or call phone numbers provided in this message.")

        if brand_impersonated:
            recs.append(f"🔍 Directly navigate to the legitimate {brand_impersonated} mobile app or official website independently — never use the provided shortcut.")

        if "Credential Harvesting" in categories or "Fake Bank Alert" in categories:
            recs.append("🔒 Never disclose SMS OTPs, authentication codes, or passwords. Legitimate banks and services will NEVER ask for them.")

        if "Untraceable Payment Demands" in categories:
            recs.append("💳 Refuse all requests for gift cards, cryptocurrency, or wire transfers. Government agencies and major retailers never settle disputes via gift cards.")

        if "Tech Support Hijack" in categories:
            recs.append("💻 Do NOT install AnyDesk, TeamViewer, or give remote access. Disconnect your internet immediately if remote access was already granted.")

        if "Emergency Impersonation" in categories:
            recs.append("📞 Call your family member on their known saved phone number or contact another mutual relative to confirm their safety.")

        if any(u["is_suspicious"] for u in url_reports):
            recs.append("🌐 The linked web address does not match verified corporate servers. Report the domain to Google Safe Browsing / PhishTank.")

        recs.append("🛡️ Block the sender number/email immediately and submit a scam report to your local consumer fraud authority (e.g. FTC / Cyber Crime portal).")
    else:
        recs.append("✅ No overt scam indicators found. Always confirm the sender's email address matches the official company domain.")
        recs.append("💡 Stay alert: If any party subsequently requests passwords, PINs, or money transfers, stop and re-verify.")

    return recs


def calculate_confidence(content: str, tactics: list, urls: list) -> int:
    """Calculates model confidence percentage based on signal density."""
    if not content:
        return 100
    word_count = len(content.split())
    signals = len(tactics) + len(urls)
    if signals >= 2 and word_count >= 10:
        return 96
    elif signals >= 1:
        return 91
    elif word_count > 15:
        return 88
    return 82
