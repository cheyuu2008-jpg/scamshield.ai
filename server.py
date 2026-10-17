"""
ScamShield AI - Lightweight Zero-Dependency Server
Serves static frontend and provides REST API for real-time scam detection.
Uses Python's standard library http.server, so judges don't need any pip packages!
"""

import http.server
import socketserver
import json
import os
import sys
from analyzer import ScamShieldAnalyzer

PORT = 8080
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

analyzer = ScamShieldAnalyzer()

class ScamShieldRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def end_headers(self):
        # Enable CORS for local testing & demos
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/scenarios":
            scenarios_file = os.path.join(BASE_DIR, "demo_scenarios.json")
            if os.path.exists(scenarios_file):
                with open(scenarios_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(data).encode("utf-8"))
            else:
                self.send_response(404)
                self.end_headers()
        elif self.path == "/api/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy", "service": "ScamShield AI"}).encode("utf-8"))
        else:
            # Default to serving static files (index.html, etc.)
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/analyze":
            content_length = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_length).decode("utf-8")
            try:
                payload = json.loads(post_body)
                text = payload.get("text", "")
                sender = payload.get("sender", "")
                result = analyzer.analyze(text, sender)
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()


def run_server():
    # Allow port reuse to avoid 'Address already in use' during rapid restarts
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), ScamShieldRequestHandler) as httpd:
        print(f"=====================================================")
        print(f"🛡️  ScamShield AI Hackathon Prototype Server Running")
        print(f"🌐  Open Web UI: http://localhost:{PORT}")
        print(f"📡  API Endpoint: http://localhost:{PORT}/api/analyze")
        print(f"=====================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")

if __name__ == "__main__":
    run_server()
