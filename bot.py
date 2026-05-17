import random
import asyncio
import sys
import multiprocessing
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

# 🚀 حل مشكلة الحزمة وتوافق الإصدار في الذاكرة (25.1.0)
from types import ModuleType
pkg_mod = ModuleType("pkg_resources")
pkg_mod.declare_namespace = lambda name: None
pkg_mod.get_distribution = lambda name: type("Dist", (), {"version": "25.1.0"})()
sys.modules["pkg_resources"] = pkg_mod

from highrise import BaseBot, User, Position
from highrise.models import CurrencyItem

# 🌐 خادم الويب المطور للرد على جميع طلبات منصة Render بنجاح
class WebServerHandler(BaseHTTPRequestHandler):
    def send_sucess_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Bot is running smoothly!")

    def do_GET(self):
        self.send_sucess_response()

    def do_HEAD(self):
        # 🛠️ تم إضافة هذا المعالج لحل مشكلة الخطأ 501 التي ظهرت في السجلات
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), WebServerHandler)
    server.serve_forever()

class MyBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.admin_username = "qais29"  # 👑 اسم حسابك المصرح له بالأوامر
        self.bot_id = None              

        self.allowed_to_predict = set() 
        self.paid_predictions = {}      
        self.ignored_players = set()    

        self.center_position = Position(8.5, 0, 8.5, "facingFront") 
        self.podium_position = Position(0, 0, 0, "facingFront")      

        self.dance_emotes = [
            "emote-celebrate", "emote-dance-tiktok", "emote-robot", 
            "emote-disco", "emote-fail", "emote-hot", "emote-laughing", "emote-wild"
        ]

    async def on_start(self, session_metadata) -> None:
        self.bot_id = session_metadata.user_id 
        await self.highrise.walk_to(self.center_position)
        print("🤖 تم تشغيل البوت المستقر والتوجه إلى منتصف الغرفة!")

    async def on_user_join(self, user: User, position: Position) -> None:
        await self.highrise.chat(f"أهلاً بك يا {user.username}! 🌟 للتوقع ادفع 5 g بالحصالة واكتب رقم صندوقك.")

    async def on_chat(self, user: User, message: str) -> None:
        text = message.strip()

        if text == "منتصف" and user.username.lower() == self.admin_username.lower():
            room_users = await self.highrise.get_room_users()
            for room_user, pos in room_users.content:
                if room_user.id == user.id:
                    self.center_position = pos
                    await self.highrise.chat(" ✅ تم حفظ موقع منتصف الغرفة الجديد بنجاح!")
                    await self.highrise.walk_to(self.center_position)
                    break
            return

        if text == "منصة" and user.username.lower() == self.admin_username.lower():
            room_users = await self.highrise.get_room_users()
            for room_user, pos in room_users.content:
                if room_user.id == user.id:
                    self.podium_position = pos
                    await self.highrise.chat(" ✅ تم حفظ موقع المنصة الجديد بنجاح!")
                    break
            return

        if text.startswith("لكم ") and user.username.lower() == self.admin_username.lower():
            target_username = text.replace("لكم ", "").strip().replace("@", "")
            room_users = await self.highrise.get_room_users()
            target_found = False

            for room_user, pos in room_users.content:
                if room_user.username.lower() == target_username.lower():
                    target_found = True
                    punch_position = Position(pos.x + 0.5, pos.y, pos.z, "facingFront")
                    await self.highrise.chat(f"👊 جاري التوجه للكم @{room_user.username} بطلب من الزعيم!")
                    await self.highrise.walk_to(punch_position)
                    await self.highrise.send_emote("emote-punch")
                    await asyncio.sleep(2)
                    await self.highrise.chat(" 🏃‍♂️ تم اللكم بنجاح! جاري العودة لمنتصف الغرفة المحفوظ.")
                    await self.highrise.walk_to(self.center_position)
                    break

            if not target_found:
                await self.highrise.chat(f"❌ لم أجد اللاعب @{target_username} في الغرفة حالياً!")
            return

        if text == "مسح" and user.username.lower() == self.admin_username.lower():
            self.allowed_to_predict.clear()
            self.paid_predictions.clear()
            self.ignored_players.clear()
            await self.highrise.chat("🔄 تم مسح سجلات الجولة، التوقعات، وقائمة تجسير لاعبي الـ 10 g!")
            return

        if text.startswith("فائز خمسين ") and user.username.lower() == self.admin_username.lower():
            winning_number = text.replace("فائز خمسين ", "").strip()
            if winning_number.isdigit():
                winners = []
                for player_id, data in self.paid_predictions.items():
                    if data["prediction"] == winning_number:
                        winners.append(f"@{data['username']}")

                if winners:
                    winners_list = ", ".join(winners)
                    await self.highrise.chat(f"🎉 الفائزون بالصندوق رقم ({winning_number}) والذين دفعوا 5 g هم: {winners_list} 🔥")
                    await self.highrise.walk_to(self.podium_position)
                    random_dance = random.choice(self.dance_emotes)
                    await self.highrise.send_emote(random_dance)
                    await asyncio.sleep(4)
                    self.allowed_to_predict.clear()
                    self.paid_predictions.clear()
                    await self.highrise.walk_to(self.center_position)
                    await self.highrise.chat(" 🔄 تم تصفير السجل تلقائياً والعودة للمنتصف. البوت جاهز للجولة الجديدة! 🚀")
                else:
                    await self.highrise.chat(f"❌ لا يوجد أي لاعب توقع الرقم ({winning_number}) ودفع 5 g!")
            return

        if text.isdigit():
            if user.id in self.ignored_players:
                return
            if user.id in self.allowed_to_predict:
                self.paid_predictions[user.id] = {"username": user.username, "prediction": text}
                await self.highrise.chat(f"✅ تم بنجاح تسجيل وتثبيت توقعك يا {user.username} للصندوق رقم ({text})! بالتوفيق 🔮")
                self.allowed_to_predict.remove(user.id)
            else:
                await self.highrise.chat(f"⚠️ يا {user.username}، لتوقع رقم صندوق رابح يجب عليك وضع 5 g في الحصالة أولاً!")

    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem) -> None:
        try:
            if receiver.id == self.bot_id and tip.item == "gold":
                if tip.amount == 10:
                    self.ignored_players.add(sender.id)
                    await self.highrise.chat(f"✅ تم تسجيل استلام (10 g) من {sender.username}. [تم تشغيل وضع تجاهل أرقامه في الشات بنجاح].")
                elif tip.amount == 5:
                    if sender.id in self.ignored_players:
                        self.ignored_players.remove(sender.id)
                    self.allowed_to_predict.add(sender.id)
                    await self.highrise.chat(f"💰 شكراً للاعب {sender.username} على دفع 5 g بالحصالة! اكتب الآن رقم الصندوق الذي تتوقعه بالشات ليتم تثبيته رسمياً.")
        except Exception as e:
            print(f"حدث خطأ في استقبال الدفع: {e}")

if __name__ == "__main__":
    # ⚙️ تشغيل خادم الويب الشامل كعملية مستقلة
    server_process = multiprocessing.Process(target=run_web_server, daemon=True)
    server_process.start()

    # 🤖 تشغيل البوت
    from highrise.__main__ import run
    sys.argv = ["highrise", "bot:MyBot", "6a04970a90ee23ef0aaff651", "22b0110e1d415ec868f62fae55770b6b6c39edf1f02f8ec935e1741b2f61b2a5"]
    run()
