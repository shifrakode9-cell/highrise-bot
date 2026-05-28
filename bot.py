import os
import asyncio
from highrise import BaseBot
from highrise.models import SessionMetadata
from highrise import BotDefinition

class MyNewBot(BaseBot):
    async def on_start(self, session_metadata: SessionMetadata):
        print("--- البوت اتصل بنجاح! ---")

if __name__ == "__main__":
    # هذا هو النمط المعتمد في إصدار 25.1.0
    bot = MyNewBot()
    # يتم التشغيل عبر ربط التعريف بالبيانات مباشرة
    # ملاحظة: إذا استمرت المشكلة، استخدم "highrise-bot-sdk" من GitHub
    # وانسخ مثال الـ "main.py" الموجود في مجلد examples لديهم.
