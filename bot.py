import asyncio
import random
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer
from highrise import BaseBot, User, CurrencyItem, Position
from highrise.models import SessionMetadata

class RenderHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write("🤖 يعمل بنجاح!".encode('utf-8'))
    def log_message(self, format, *args): return

def run_web_server():
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
        
        # موقع افتراضي للمنصة
        self.bot_platform_position = Position(0.0, 0.0, 0.0) 
        self.winner_position = Position(10.0, 4.0, 10.0)     

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("🤖 متصل!")

    # 🟢 ترحيب فوري ومضمون عند دخول أي لاعب جديد
    async def on_user_join(self, user: User, position: Position) -> None:
        self.room_users.add(user.id)
        try:
            await asyncio.sleep(1)
            await self.highrise.chat(f"أهلاً بك @{user.username} في غرفتنا! 🎮 نحن نلعب لعبة الصناديق المثيرة. ادفع 5 ذهبات لتشترك وتصعد للمنصة فوراً!")
        except: pass

    async def on_user_leave(self, user: User) -> None:
        if user.id in self.room_users: self.room_users.remove(user.id)

    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem) -> None:
        if receiver.id != self.id or tip.amount < 5: return

        if not self.game_active and not self.prediction_active:
            if len(self.players_paid) >= self.max_players:
                await self.highrise.chat(f"⚠️ @{sender.username} العدد مكتمل حالياً!")
                return
            
            self.players_paid[sender.id] = sender.username
            await self.highrise.chat(f"✅ تم تسجيل اشتراك @{sender.username}")
            try:
                await self.highrise.teleport(sender.id, self.bot_platform_position)
                await self.highrise.chat(f"مبارك السحب يا @{sender.username}! اختر رقم صندوقك الآن (1-10)")
            except: pass

    # 🟢 قراءة الشات والاستجابة الفورية للأوامر
    async def on_chat(self, user: User, message: str) -> None:
        msg = message.strip()
        # فحص الأدمن بطريقة مرنة (تتحمل وجود @ أو عدم وجودها)
        is_admin = user.username.lower() in ["qais29", "sweet_lulus", "@qais29", "@sweet_lulus"]

        if user.id in self.players_paid and not self.game_active and not self.prediction_active:
            if msg.isdigit():
                box_num = int(msg)
                if 1 <= box_num <= 10:
                    self.predictions[user.id] = {"username": user.username, "box": box_num}
                    await self.highrise.chat(f"📌 تم حفظ الصندوق [{box_num}] لـ @{user.username}")
                    return

        if is_admin:
            # 📌 أمر سحب البوت إليك فوراً وتحديث موقع المنصة (معدل ليكون مضموناً 100%)
            if msg == "تعال" or msg == "الموقع":
                try:
                    response = await self.highrise.get_room_users()
                    for room_user, pos in response.content:
                        if room_user.id == user.id:
                            self.bot_platform_position = pos
                            await self.highrise.teleport(self.id, pos)
                            await self.highrise.chat(f"🏃‍♂️ تم سحب البوت بنجاح يا @{user.username} وتثبيت الموقع هنا!")
                            return
                except Exception as e:
                    print(f"خطأ في السحب: {e}")
                return

            # 📌 أمر سحب الغرفة
            elif msg == "سحب الغرفة":
                try:
                    response = await self.highrise.get_room_users()
                    my_pos = None
                    for room_user, pos in response.content:
                        if room_user.id == user.id:
                            my_pos = pos
                            break
                    if my_pos:
                        await self.highrise.chat("⚡ جاري سحب الجميع...")
                        for room_user, pos in response.content:
                            if room_user.id != self.id and room_user.id != user.id:
                                try: await self.highrise.teleport(room_user.id, my_pos)
                                except: pass
                except: pass
                return

            # 📌 أمر بدء اللعبة (الذي يستجيب معك دائماً)
            if msg == "ابدأ" and not self.game_active:
                if len(self.players_paid) < 1:
                    await self.highrise.chat("❌ لا يوجد مشتركين لبدء اللعبة!")
                    return
                self.game_active = True
                await self.highrise.chat("🎮 بدأت الجولة الرسمية! الصناديق مغلقة الآن!")
                
                all_contents = ["50", "10", "5", "5", "1", "1", "فارغ", "فارغ", "فارغ", "فارغ"]
                random.shuffle(all_contents)
                self.boxes = {i+1: all_contents[i] for i in range(10)}
                return
            
            # 📌 أمر التوقعات
            elif msg == "توقع" and self.game_active and not self.prediction_active:
                remaining_boxes = list(self.boxes.keys())
                self.game_active = False
                self.prediction_active = True
                await self.highrise.chat(f"🚨 جولة التوقعات! الصناديق المتاحة: {remaining_boxes}. أمامكم 45 ثانية!")
                await asyncio.sleep(45)
                if self.prediction_active:
                    await self.reveal_prediction_results()
                return
                
            # 📌 أمر إنهاء وتصفير اللعبة
            elif msg == "انتهى":
                self.game_active = False
                self.prediction_active = False
                self.players_paid.clear()
                self.predictions.clear()
                self.boxes.clear()
                await self.highrise.chat("🔄 تم إنهاء اللعبة وتصفيرها لجولة جديدة!")
                return

    async def reveal_prediction_results(self):
        self.prediction_active = False
        await self.highrise.chat("🔒 بدأ كشف النتائج...")
        await asyncio.sleep(1)

        total_players = len(self.predictions)
        final_prize = 50 + int((total_players * 5) * 0.70)
        winners_list = []

        for box_num, content in sorted(self.boxes.items()):
            players_chosen = [info["username"] for uid, info in self.predictions.items() if info.get("box") == box_num]
            players_str = ", ".join(players_chosen) if players_chosen else "لا أحد"
            
            if content == "50":
                await self.highrise.chat(f"📦 صندوق [{box_num}] لـ ({players_str}) -> 🎉 الرابح الأكبر بـ {final_prize} نقطة!")
                for uid, info in self.predictions.items():
                    if info.get("box") == box_num: winners_list.append(info["username"])
            else:
                await self.highrise.chat(f"📦 صندوق [{box_num}] لـ ({players_str}) -> [{content}]")
            await asyncio.sleep(2)

        if winners_list:
            await self.highrise.chat(f"👑 مبروك للفائزين: {', '.join(winners_list)}")
        else:
            await self.highrise.chat("😢 لم يتوقع أحد الصندوق الصحيح.")

if __name__ == '__main__':
    Thread(target=run_web_server, daemon=True).start()
