import os
import subprocess
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# هذا الجزء يرد على Render ليخبره أن الخدمة تعمل
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def start_health_check():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

if __name__ == "__main__":
    # تشغيل خادم الصحة في الخلفية
    threading.Thread(target=start_health_check, daemon=True).start()
    
    # تشغيل البوت
    room_id = os.getenv("ROOM_ID")
    api_key = os.getenv("API_KEY")
    command = [sys.executable, "-m", "highrise", "bot:MyBot", room_id, api_key]
    subprocess.run(command)
