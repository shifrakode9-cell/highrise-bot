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
        self.wfile.write("🤖 البوت يعمل بأعلى كفاءة".encode('utf-8'))
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
        
        # موقع المنصة الافتراضي (يتحدث تلقائياً بأمر تعال)
        self.bot_platform_position = Position(0.0, 0.0, 0.0) 
        self.winner_position = Position(10.0, 4.0, 10.0)     

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("🤖 متصل!")
        try: await self.highrise.chat("🤖 تم تشغيل البوت بنجاح! الأوامر الإدارية (تعال / سحب الغرفة) جاهزة الآن.")
        except: pass

    # 🟢 الترحيب التلقائي الفعال والمضمون لكل من يدخل
    async def on_user_join(self, user: User, position: Position) -> None:
        self.room_users.add(user.id)
        try:
            await asyncio.sleep(2) # مهلة ثانيتين لضمان استقرار اللاعب بالغرفة ورؤية الشات
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
            # 📌 أمر (تعال) أو (الموقع) - لسحب البوت وتثبيت المنصة عندك
            if msg == "تعال" or msg == "الموقع":
                try:
                    response = await self.highrise.get_room_users()
                    for room_user, pos in response.content:
                        if room_user.id == user.id:
                            self.bot_platform_position = pos
                            await self.highrise.teleport(self.id, pos)
                            await self.highrise.chat(f"🏃‍♂️ تم سحب البوت بنجاح يا @{user.username} وتثبيت المنصة في موقعك!")
                            return
                    await self.highrise.chat("❌ تحرك خطوة واحدة في الغرفة ثم اكتب الأمر مجدداً.")
                except Exception as e:
                    print(f"خطأ في سحب البوت: {e}")
                return

            # 📌 أمر (سحب الغرفة) - يسحب جميع حضور الغرفة إلى موقعك أنت كإدارة فوراً
            elif msg == "سحب الغرفة":
                try:
                    response = await self.highrise.get_room_users()
                    admin_pos = None
                    for room_user, pos in response.content:
                        if room_user.id == user.id:
                            admin_pos = pos
                            break
                    
                    if admin_pos:
                        await self.highrise.chat("⚡ جاري سحب جميع الحضور إلى موقع الإدارة الآن...")
                        for room_user, pos in response.content:
                            if room_user.id != self.id and room_user.id != user.id:
                                try: await self.highrise.teleport(room_user.id, admin_pos)
                                except: pass
                    else:
                        await self.highrise.chat("❌ تحرك خطوة ثم اكتب الأمر مجدداً ليتم تحديد موقعك.")
                except Exception as e:
                    print(f"خطأ في سحب الغرفة: {e}")
                return

            # 📌 أمر (ابدأ) - لبدء اللعبة الرسمية وقفل الصناديق
            if msg == "ابدأ" and not self.game_active:
                if len(self.players_paid) < 1:
                    await self.highrise.chat("❌ لا يوجد مشتركين بالذهب حالياً لبدء اللعبة!")
                    return
                self.game_active = True
                await self.highrise.chat("🎮 بدأت الجولة الرسمية! الصناديق مغلقة ومحمية الآن!")
                return
            
            # 📌 أمر (توقع) - لبدء مرحلة توقعات الحضور
            elif msg == "توقع" and self.game_active and not self.prediction_active:
                remaining_boxes = list(self.boxes.keys()) if self.boxes else list(range(1, 11))
                self.game_active = False
                self.prediction_active = True
                
                # إذا لم تكن الصناديق قد خلطت بعد، يتم خلطها فوراً
                if not self.boxes:
                    all_contents = ["50", "10", "5", "5", "1", "1", "فارغ", "فارغ", "فارغ", "فارغ"]
                    random.shuffle(all_contents)
                    self.boxes = {i+1: all_contents[i] for i in range(10)}
                    remaining_boxes = list(self.boxes.keys())

                await self.highrise.chat(f"🚨 جولة التوقعات بدأت! الصناديق المتاحة هي: {remaining_boxes}. أمامكم 45 ثانية واكتبوا أرقامكم بالشات!")
                await asyncio.sleep(45)
                if self.prediction_active:
                    await self.reveal_prediction_results()
                return
                
            # 📌 أمر (انتهى) - لتصفير اللعبة بالكامل
            elif msg == "انتهى":
                self.game_active = False
                self.prediction_active = False
                self.players_paid.clear()
                self.predictions.clear()
                self.boxes.clear()
                await self.highrise.chat("🔄 تم إنهاء اللعبة وتصفير البيانات لجولة جديدة تماماً!")
                return

        if self.prediction_active:
            if msg.isdigit() and int(msg) in self.boxes:
                box_num = int(msg)
                if user.id in self.predictions:
                    self.predictions[user.id]["box"] = box_num
                    await self.highrise.chat(f"📌 تم حفظ توقعك للصندوق [{box_num}] يا @{user.username}")
                    if all(info.get("box") is not None for info in self.predictions.values()):
                        await self.reveal_prediction_results()

    async def reveal_prediction_results(self):
        self.prediction_active = False
        await self.highrise.chat("🔒 انتهى الوقت! جاري كشف محتويات الصناديق والنتائج...")
        await asyncio.sleep(2)

        total_players = len(self.predictions)
        final_prize = 50 + int((total_players * 5) * 0.70)
        winners_list = []

        for box_num, content in sorted(self.boxes.items()):
            players_chosen = [info["username"] for uid, info in self.predictions.items() if info.get("box") == box_num]
            players_str = ", ".join(players_chosen) if players_chosen else "لا أحد"
            
            if content == "50":
                await self.highrise.chat(f"📦 صندوق [{box_num}] لـ ({players_str}) -> 🎉 الرابح الأكبر بالجائزة الكبرى بقيمة {final_prize} نقطة!")
                for uid, info in self.predictions.items():
                    if info.get("box") == box_num: winners_list.append(info["username"])
            else:
                await self.highrise.chat(f"📦 صندوق [{box_num}] لـ ({players_str}) -> [{content}]")
            await asyncio.sleep(2)

        if winners_list:
            await self.highrise.chat(f"👑 ألف مبروك للفائزين معنا في هذه الجولة: {', '.join(winners_list)}")
        else:
            await self.highrise.chat("😢 الحظ لم يحالف أحد، لم يتوقع أحد الصندوق الصحيح للجائزة الكبرى.")

if __name__ == '__main__':
    Thread(target=run_web_server, daemon=True).start()
