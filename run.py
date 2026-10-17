"""
ScamShield AI - Quick Launcher
Starts the backend server and opens the interactive dashboard in your browser.
"""

import sys
import os
import webbrowser
import threading
import time

# Ensure UTF-8 console output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Ensure backend directory is in python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

def open_browser():
    time.sleep(1.2)
    print("\n🌐 Launching ScamShield AI Dashboard at http://localhost:8000 ...")
    webbrowser.open("http://localhost:8000")

def main():
    print("=" * 60)
    print("🛡️   SCAMSHIELD AI - INTELLIGENT FRAUD DEFENSE PROTOTYPE")
    print("=" * 60)
    print("• Multi-Modal AI Smishing & Scam Detection Engine")
    print("• Real-Time Threat Scoring & Psychological Tactic Decomposition")
    print("• Typo-Squatting & Phishing Domain Safety Inspector")
    print("• Scam Awareness Interactive Quiz & Emergency Response Guide")
    print("=" * 60)

    try:
        import uvicorn
        from main import app
    except ImportError as e:
        print(f"❌ Missing required library: {e}")
        print("Please install requirements using: pip install -r requirements.txt")
        sys.exit(1)

    # Launch browser in a background thread
    threading.Thread(target=open_browser, daemon=True).start()

    print("🚀 Starting ScamShield AI FastAPI Service on http://localhost:8000 (Ctrl+C to stop)")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False, app_dir=BACKEND_DIR)

if __name__ == "__main__":
    main()
