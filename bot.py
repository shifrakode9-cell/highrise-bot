import os
import subprocess
import sys

# نقوم بتشغيل البوت باستخدام أمر النظام بدلاً من استيراد المكتبة برمجياً
# لأن هذا هو الطريقة الوحيدة التي تدعمها نسخة 25.1.0
room_id = os.getenv("ROOM_ID")
api_key = os.getenv("API_KEY")

# أمر التشغيل الرسمي في الإصدارات الجديدة
cmd = [sys.executable, "-m", "highrise", room_id, api_key]

# تنفيذ الأمر
subprocess.run(cmd)
