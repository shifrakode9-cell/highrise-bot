import asyncio
import random
import sys
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer
from highrise import BaseBot, User, CurrencyItem, Position
from highrise.models import SessionMetadata

# 🌐 سيرفر الويب لإبقاء البوت حياً على Render ومنع خطأ الـ Ports
class RenderHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write("🤖 البوت يعمل بأعلى كفاءة ومستقر 100%".encode('utf-8'))
    def log_message(self, format, *args): return

def run_web_server():
    # ريندر يبحث عن المنفذ 8000 افتراضياً
    server = HTTPServer(('0.0.0.0', 8000), RenderHandler)
    server.serve_forever()

class MyBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.game_active = False
        self.prediction_active = False
        self.players_paid = {}      
        self.predictions = {}       
        self.boxes = {}             
        self.max_players = 5
        self.room_users = set()  
        
        # موقع المنصة الافتراضي (يتحدث تلقائياً بأمر تعال)
        self.bot_platform_position = Position(0.0, 0.0, 0.0) 
        self.winner_position = Position(10.0, 4.0, 10.0)     

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("🤖 متصل!")
        try: await self.highrise.chat("🤖 تم تشغيل البوت بنجاح! الأوامر الإدارية (تعال / سحب الغرفة) جاهزة الآن.")
        except: pass

    # 🟢 الترحيب التلقائي الفعال والمضمون لكل من يدخل الغرفة
    async def on_user_join(self, user: User, position: Position) -> None:
        self.room_users.add(user.id)
        try:
            await asyncio.sleep(2) # مهلة ثانيتين لضمان استقرار اللاعب ورؤية الشات
            await self.highrise.chat(f"أهلاً بك @{user.username} في غرفتنا! 🎮 نحن نلعب لعبة الصناديق المثيرة. ادفع 5 ذهبات لتشترك وتصعد للمنصة فوراً!")
        except: pass

    async def on_user_leave(self, user: User) -> None:
        if user.id in self.room_users: self.room_users.remove(user.id)

    # 🟢 نظام استلام الذهب الفوري والسحب للمنصة
    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem) -> None:
        if receiver.id != self.id or tip.amount < 5: return

        if not self.game_active and not self.prediction_active:
            if len(self.players_paid) >= self.max_players:
                await self.highrise.chat(f"⚠️ @{sender.username} العدد مكتمل حالياً في هذه الجولة!")
                return
            
            self.players_paid[sender.id] = sender.username
            await self.highrise.chat(f"✅ تم تسجيل اشتراكك بنجاح يا @{sender.username}")
            try:
                await self.highrise.teleport(sender.id, self.bot_platform_position)
                await self.highrise.chat(f"مبارك السحب يا @{sender.username}! اختر رقم صندوقك الآن من (1-10) في الشات.")
            except: pass

    # 🟢 نظام الشات والأوامر الإدارية المطور بالكامل
    async def on_chat(self, user: User, message: str) -> None:
        msg = message.strip()
        is_admin = user.username.lower() in ["qais29", "sweet_lulus", "@qais29", "@sweet_lulus"]

        # استقبال أرقام الصناديق من المتسابقين المشتركين
        if user.id in self.players_paid and not self.game_active and not self.prediction_active:
            if msg.isdigit():
                box_num = int(msg)
                if 1 <= box_num <= 10:
                    self.predictions[user.id] = {"username": user.username, "box": box_num}
                    await self.highrise.chat(f"📌 تم حفظ الصندوق [{box_num}] لـ @{user.username}")
                    return

        if is_admin:
            # 📌 أمر (تعال)
