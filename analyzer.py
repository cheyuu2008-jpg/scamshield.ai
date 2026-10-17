"""
ScamShield AI - Core Fraud & Scam Detection Engine
Multi-Vector Analysis: Psychological Urgency, Action Traps, URL/Domain Risks, and UPI/Payment Vectors.
Works standalone (offline NLP heuristics) with optional Gemini/LLM enhancement.
"""

import re
import urllib.parse
from typing import Dict, List, Any


class ScamShieldAnalyzer:
    """
    Advanced Heuristic & Pattern AI Engine to detect and dissect financial scams,
    phishing attacks, digital arrest threats, task scams, and UPI traps.
    """

    # High-Risk Psychological Patterns
    URGENCY_PATTERNS = [
        r"\b(?:within|in)\s+\d+\s*(?:mins?|minutes?|hours?)\b",
        r"\b(?:immediately|urgently|right\s+now|today\s+by\s+\d+|last\s+chance|expires\s+in)\b",
        r"\b(?:account\s+blocked|account\s+suspended|freeze\s+account|action\s+will\s+be\s+taken)\b",
        r"\b(?:warrant\s+issued|police\s+raid|arrest\s+warrant)\b"
    ]

    AUTHORITY_SPOOF_PATTERNS = [
        r"\b(?:cbi|central\s+bureau\s+of\s+investigation|customs|cyber\s+crime\s+cell|mumbai\s+police|delhi\s+police)\b",
        r"\b(?:digital\s+arrest|pmla\s+act|narcotics\s+control\s+bureau|rbi\s+verification|supreme\s+court)\b",
        r"\b(?:skype\s+video\s+call|interrogation\s+call|police\s+officer)\b"
    ]

    TASK_JOB_SCAM_PATTERNS = [
        r"\b(?:like\s+youtube\s+videos?|rate\s+hotels?|google\s+reviews?|subscribe\s+channels?)\b",
        r"\b(?:earn\s+[₹$€]\s*\d+[\d,]*\s*(?:daily|per\s+day)|daily\s+payouts?)\b",
        r"\b(?:work\s+from\s+home\s+\d+\s*mins?|part[\s-]?time\s+job)\b",
        r"\b(?:telegram\s+group|welcome\s+bonus|prepaid\s+tasks?)\b"
    ]

    PAYMENT_TRAP_PATTERNS = [
        r"\b(?:enter\s+(?:your\s+)?(?:6-digit\s+|4-digit\s+)?upi\s*pin\s+to\s+receive)\b",
        r"\b(?:scan\s+(?:this\s+)?(?:qr|qr\s*code)\s+to\s+receive)\b",
        r"\b(?:security\s+deposit|refundable\s+amount|processing\s+fee|clearance\s+fee)\b",
        r"\b(?:send\s+(?:otp|pin|cvv)|share\s+otp)\b"
    ]

    MALICIOUS_DOWNLOAD_PATTERNS = [
        r"\.apk\b",
        r"\b(?:download\s+(?:app|apk)|install\s+(?:quick|kyc|support)\s+app)\b",
        r"\b(?:anydesk|teamviewer|rustdesk|quicksupport)\b"
    ]

    def __init__(self):
        pass

    def extract_urls(self, text: str) -> List[str]:
        """Extract all URLs or web links from text."""
        url_regex = r"https?://[^\s<>\"'()]+"
        return re.findall(url_regex, text, re.IGNORECASE)

    def analyze_url_safety(self, url: str) -> Dict[str, Any]:
        """Inspect URL for phishing markers, suspicious TLDs, IP hosting, and typosquatting."""
        issues = []
        risk = 0
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc.lower()
            path = parsed.path.lower()

            # Check if domain uses raw IP address
            if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", domain):
                issues.append("Direct IP address used instead of reputable domain name")
                risk += 35

            # Suspicious / Cheap TLDs often abused in smishing campaigns
            suspicious_tlds = [".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top", ".support", ".vip", ".click", ".live"]
            if any(domain.endswith(tld) for tld in suspicious_tlds):
                issues.append(f"Domain uses high-abuse risk extension ({domain.split('.')[-1]})")
                risk += 25

            # Look for trusted brand names masqueraded inside subdomains
            masqueraded_brands = ["sbi", "hdfc", "icici", "axis", "indiapost", "amazon", "netflix", "fedex", "dhl", "paytm"]
            for brand in masqueraded_brands:
                if brand in domain and not (domain.endswith(f".{brand}.com") or domain.endswith(f".{brand}.co.in") or domain.endswith(f".gov.in")):
                    issues.append(f"Impersonating trusted organization '{brand}' inside unauthorized domain")
                    risk += 40
                    break

            # Check for APK downloads
            if path.endswith(".apk") or "download" in path and ".apk" in url:
                issues.append("Direct Android package (.apk) file download detected - malware threat")
                risk += 45

            # Check for Telegram channel redirect commonly used in task scams
            if "t.me/" in url or "telegram.me/" in url:
                issues.append("Redirects to unmonitored Telegram channel for unverified instructions")
                risk += 20

        except Exception as e:
            issues.append(f"Malformed or suspicious URL structure: {str(e)}")
            risk += 15

        return {
            "url": url,
            "domain": domain if 'domain' in locals() else "",
            "issues": issues,
            "url_risk_score": min(risk, 100)
        }

    def analyze(self, text: str, sender: str = "") -> Dict[str, Any]:
        """
        Run multi-vector heuristic scam detection on input message.
        Returns comprehensive structured report with risk score, category, red flags, and countermeasures.
        """
        if not text or not text.strip():
            return {
                "error": "Input text is empty",
                "risk_score": 0,
                "risk_level": "UNKNOWN"
            }

        text_clean = text.strip()
        red_flags: List[str] = []
        detected_categories: List[str] = []
        score = 0

        # 1. Authority Spoofing / Digital Arrest Analysis
        authority_matches = []
        for pat in self.AUTHORITY_SPOOF_PATTERNS:
            found = re.findall(pat, text_clean, re.IGNORECASE)
            if found:
                authority_matches.extend(found)

        if authority_matches:
            score += 35
            detected_categories.append("Digital Arrest / Law Enforcement Impersonation")
            red_flags.append(f"Law enforcement / government agency impersonated ({', '.join(set(authority_matches))})")
            if "digital arrest" in text_clean.lower():
                score += 30
                red_flags.append("'Digital Arrest' is a fraudulent concept. No police/CBI unit conducts digital detention.")

        # 2. Payment Traps (Reverse UPI, OTP, QR code fraud)
        payment_matches = []
        for pat in self.PAYMENT_TRAP_PATTERNS:
            found = re.findall(pat, text_clean, re.IGNORECASE)
            if found:
                payment_matches.extend(found)

        if payment_matches:
            score += 40
            detected_categories.append("Payment Fraud / Reverse UPI Trap")
            if re.search(r"\b(?:pin|upi\s*pin)\s+to\s+receive\b", text_clean, re.IGNORECASE) or \
               re.search(r"\bscan\s+.*qr.*to\s+receive\b", text_clean, re.IGNORECASE):
                red_flags.append("CRITICAL: Message asks to enter UPI PIN or scan QR to RECEIVE funds (UPI PIN is ONLY for paying)")

        # 3. Job / Task Scam Detection
        job_matches = []
        for pat in self.TASK_JOB_SCAM_PATTERNS:
            found = re.findall(pat, text_clean, re.IGNORECASE)
            if found:
                job_matches.extend(found)

        if job_matches:
            score += 30
            detected_categories.append("Part-time Task / Pyramid Investment Scam")
            red_flags.append("Unrealistic daily earnings for micro-tasks (YouTube likes, Google ratings)")

        # 4. Malware / Malicious APK Detection
        apk_matches = []
        for pat in self.MALICIOUS_DOWNLOAD_PATTERNS:
            found = re.findall(pat, text_clean, re.IGNORECASE)
            if found:
                apk_matches.extend(found)

        if apk_matches:
            score += 35
            detected_categories.append("Trojan / Screen Sharing Malware Trap")
            red_flags.append("Requests installation of third-party .APK or remote access screen-sharing app")

        # 5. Psychological Urgency & Panic Induction
        urgency_matches = []
        for pat in self.URGENCY_PATTERNS:
            found = re.findall(pat, text_clean, re.IGNORECASE)
            if found:
                urgency_matches.extend(found)

        if urgency_matches:
            score += 20
            red_flags.append(f"High-pressure artificial urgency window detected: '{urgency_matches[0]}'")

        # 6. Deep URL and Domain Analysis
        extracted_urls = self.extract_urls(text_clean)
        url_reports = []
        for u in extracted_urls:
            u_rep = self.analyze_url_safety(u)
            url_reports.append(u_rep)
            if u_rep["issues"]:
                score += u_rep["url_risk_score"]
                for iss in u_rep["issues"]:
                    red_flags.append(f"URL Alert: {iss}")

        # 7. Check Sender ID authenticity cues
        sender_lower = sender.lower()
        if sender and not sender_lower.startswith("+91") and any(code in sender_lower for code in ["+62", "+84", "+234", "+92", "+44"]):
            if "₹" in text_clean or "upi" in text_clean.lower() or "cbi" in text_clean.lower() or "sbi" in text_clean.lower():
                score += 20
                red_flags.append(f"Foreign country code sender ({sender}) targeting Indian domestic services/currency")

        # 8. Legitimate Safeguards (avoid false alarms on legitimate 2FA OTP messages)
        is_legit_otp = False
        if re.search(r"\bnever\s+share\s+this\s+otp\b", text_clean, re.IGNORECASE) or \
           re.search(r"\bdo\s+not\s+share\s+your\s+(?:otp|password|pin)\b", text_clean, re.IGNORECASE):
            if not payment_matches and not authority_matches and not apk_matches and not extracted_urls:
                is_legit_otp = True
                score = max(5, score - 50)

        # Cap score between 0 and 99
        final_score = min(max(score, 5 if not is_legit_otp and len(text_clean) > 20 else 2), 99)
        if is_legit_otp and final_score > 20:
            final_score = 8

        # Categorize Risk Level
        if final_score >= 75:
            risk_level = "CRITICAL"
            badge_color = "red"
        elif final_score >= 45:
            risk_level = "HIGH"
            badge_color = "orange"
        elif final_score >= 25:
            risk_level = "SUSPICIOUS"
            badge_color = "yellow"
        else:
            risk_level = "SAFE"
            badge_color = "emerald"

        primary_category = detected_categories[0] if detected_categories else ("Legitimate / Low Risk" if is_legit_otp else "Unverified Communication")

        # Generate Actionable Playbook
        action_playbook = self._generate_playbook(risk_level, primary_category)

        # Generate Safe Response Recommendation
        counter_reply = self._generate_safe_reply(risk_level, primary_category)

        return {
            "risk_score": final_score,
            "risk_level": risk_level,
            "badge_color": badge_color,
            "category": primary_category,
            "all_detected_categories": detected_categories,
            "red_flags": red_flags,
            "extracted_urls": url_reports,
            "urgency_triggers": list(set(urgency_matches)),
            "action_playbook": action_playbook,
            "suggested_safe_reply": counter_reply,
            "summary": self._generate_summary(risk_level, primary_category, len(red_flags))
        }

    def _generate_summary(self, level: str, category: str, flag_count: int) -> str:
        if level in ["CRITICAL", "HIGH"]:
            return f"⚠️ DANGER: Highly dangerous {category} pattern identified with {flag_count} critical red flags. Immediate threat to user funds/identity."
        elif level == "SUSPICIOUS":
            return f"⚡ CAUTION: Suspicious indicators detected. Exercise extreme vigilance before clicking links or replying."
        else:
            return "✅ LIKELY SAFE: Standard institutional message structure without extortion, credential phishing, or payment traps."

    def _generate_playbook(self, level: str, category: str) -> List[str]:
        if level in ["CRITICAL", "HIGH"]:
            steps = [
                "🛑 DO NOT send money, do not scan any QR code, and do NOT enter your UPI PIN.",
                "🚫 DO NOT click links, download .APK files, or accept screen-sharing requests.",
                "📞 If targeted by Digital Arrest / Police threats: Hang up immediately. Police/CBI never interrogate citizens on Skype or WhatsApp.",
                "🛡️ Report directly to National Cyber Crime Portal (cybercrime.gov.in) or call helpline 1930.",
                "🔒 Block and report the sender on WhatsApp / SMS."
            ]
        elif level == "SUSPICIOUS":
            steps = [
                "⚠️ Verify sender identity through independent official channels (official website/bank app).",
                "🔍 Do not click links received in unprompted SMS or Telegram messages.",
                "💬 Never disclose personal identifiers (Aadhaar, PAN, date of birth) via messaging apps."
            ]
        else:
            steps = [
                "✅ Keep your OTP confidential. No legitimate company employee will ever ask for it.",
                "📱 Verify the merchant and transaction amount match your expected activity."
            ]
        return steps

    def _generate_safe_reply(self, level: str, category: str) -> str:
        if "Digital Arrest" in category or "Law Enforcement" in category:
            return "I am reporting this communication to the local Cyber Crime police station and the 1930 helpline for official record verification. Do not contact me again."
        elif "Payment" in category or "QR" in category:
            return "UPI PIN is only used for sending money, not receiving. I will only accept direct standard bank transfer or cash in person."
        elif "Task" in category or "Job" in category:
            return "Please provide your corporate registration number and company website email domain. I do not conduct work via unverified Telegram channels."
        else:
            return "I will independently verify this request with customer care through their verified official portal."


if __name__ == "__main__":
    analyzer = ScamShieldAnalyzer()
    sample = "You are under DIGITAL ARREST by CBI. Transfer 50,000 to avoid police raid in 15 mins."
    result = analyzer.analyze(sample)
    print(f"Risk Score: {result['risk_score']}% ({result['risk_level']})")
    print(f"Category: {result['category']}")
    print("Red Flags:", result["red_flags"])
