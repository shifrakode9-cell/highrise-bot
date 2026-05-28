import os
import subprocess
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from highrise import BaseBot

# كلاس لفتح بورت وهمي لإرضاء Render
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_server():
    port = int(os.getenv("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

if __name__ == "__main__":
    # 1. تشغيل البورت الوهمي في خيط (Thread) منفصل
    threading.Thread(target=run_server, daemon=True).start()
    
    # 2. تشغيل البوت الأساسي
    room_id = os.getenv("ROOM_ID")
    api_key = os.getenv("API_KEY")
    command = [sys.executable, "-m", "highrise", "bot:MyBot", room_id, api_key]
    subprocess.run(command)
