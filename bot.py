import os
import sys
import subprocess
from highrise import BaseBot

# تأكد أن اسم الكلاس هنا MyBot كما هو مطلوب
class MyBot(BaseBot):
    async def on_start(self, session_metadata):
        print("--- تم الاتصال بنجاح! ---")

# هذا الجزء يحل مشكلة تشغيل البورت والاتصال معاً
if __name__ == "__main__":
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import threading

    # بورت وهمي لإرضاء Render
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
    
    # تشغيل الخادم الوهمي في الخلفية
    threading.Thread(target=lambda: HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 10000))), HealthHandler).serve_forever(), daemon=True).start()

    # تشغيل البوت
    room_id = os.getenv("ROOM_ID")
    api_key = os.getenv("API_KEY")
    command = [sys.executable, "-m", "highrise", "bot:MyBot", room_id, api_key]
    subprocess.run(command)
