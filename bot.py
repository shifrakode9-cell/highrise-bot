import os
import subprocess
import sys

# نقوم بقراءة الإعدادات
room_id = os.getenv("ROOM_ID")
api_key = os.getenv("API_KEY")

# هذا السطر يقوم بتشغيل المكتبة كأنها أمر نظام (System Command)
# وهو الحل الأخير لتجنب مشاكل التوافق في الإصدار 25.1.0
command = [sys.executable, "-m", "highrise", "bot:MyBot", room_id, api_key]

# تنفيذ الأمر
process = subprocess.Popen(command)
process.wait()
