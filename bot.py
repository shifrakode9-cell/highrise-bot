import asyncio
import random
from highrise import BaseBot, User, CurrencyItem, Position

# تم ضبط اسم الكلاس ليكون MyBot ليتوافق تماماً مع إعدادات الـ Settings لديك
class MyBot(BaseBot):
    def __init__(self):
        super().__init__()
        # إعدادات اللعبة وحفظ البيانات
        self.game_active = False
        self.prediction_active = False
        self.players_paid = {}      
        self.predictions = {}       
        self.boxes = {}             
        self.max_players = 5
        self.room_users = set()  # لحفظ متواجدي الغرفة من أجل الدبكة الجماعية
        
        # ⚠️ إحداثيات الغرفة - قم بتغيير الأرقام لتناسب تصميم غرفتك بدقة
        # الـ Y هو الارتفاع، تأكد من ضبطه ليقف البوت فوق المنصة تماماً
        self.bot_platform_position = Position(2.5, 4.0, 3.5) 
        self.jail_position = Position(5.0, 0.0, 5.0)         
        self.winner_position = Position(10.0, 4.0, 10.0)     

    # حدث الدخول الفوري لوضع البوت على المنصة لكي يراه الجميع
    async def on_start(self, session_metadata) -> None:
        print("🤖 البوت متصل بنجاح وجاهز للعمل!")
        try:
            # النقل الفوري للبوت إلى منصته الخاصة عند بدء التشغيل
            await self.highrise.teleport(self.id, self.bot_platform_position)
        except Exception as e:
            print(f"فشل نقل البوت للمنصة، تحقق من الإحداثيات: {e}")

    # تسجيل الحاضرين للدبكة الجماعية
    async def on_user_join(self, user: User, position: Position) -> None:
        self.room_users.add(user.id)

    async def on_user_leave(self, user: User) -> None:
        if user.id in self.room_users:
            self.room_users.remove(user.id)

    # 1. نظام الحصالة الذكي (استقبال الـ 5 ذهبات والترحيب والتسجيل)
    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem) -> None:
        if receiver.id != self.id or tip.amount != 5:
            return

        # جولة الاشتراك الأولي للمتسابقين
        if not self.game_active and not self.prediction_active:
            if len(self.players_paid) >= self.max_players:
                await self.highrise.chat(f"⚠️ @{sender.username} العدد مكتمل حالياً! انتظر الجولة القادمة.")
                return
            
            self.players_paid[sender.id] = sender.username
            await self.highrise.chat(f"✅ تم تسجيل @{sender.username} | عدد المسجلين الحاليين: {len(self.players_paid)}/{self.max_players}. ننتظر أمر الإدارة لبدء اللعبة.")

        # جولة التوقعات الأخيرة
        elif self.prediction_active:
            self.predictions[sender.id] = {"username": sender.username, "box": None}
            await self.highrise.chat(f"🟢 تم تفعيل توقعك يا @{sender.username}! اكتب رقم صندوقك الآن في الشات.")

    # 2. قراءة الشات (الأوامر الخاصة بك وبالمشرفين + فحص أرقام التوقعات)
    async def on_chat(self, user: User, message: str) -> None:
        msg = message.strip()
        
        # ⚠️ استبدل الأسماء هنا بأسماء حساباتكم بدقة في اللعبة (الحروف الكبيرة والصغيرة تفرق)
        is_admin = user.username in ["Qais", "Owner_Name", "Admin1"]

        if is_admin:
            if msg == "/start" and not self.game_active:
                if len(self.players_paid) < 2:
                    await self.highrise.chat("❌ لا يمكن بدء اللعبة، عدد المسجلين قليل جداً!")
                    return
                await self.start_main_game()
                return
                
            elif msg == "/end" and self.prediction_active:
                await self.reveal_prediction_results()
                return

        # استقبال أرقام الصناديق في جولة التوقعات
        if self.prediction_active:
            if msg.isdigit() and int(msg) in self.boxes:
                box_num = int(msg)
                if user.id in self.predictions:
                    self.predictions[user.id]["box"] = box_num
                    await self.highrise.chat(f"📌 تم حفظ توقعك للصندوق [{box_num}] يا @{user.username}")
                    
                    # المؤقت الذكي: بدء تلقائي وفوري للنتائج إذا كتب جميع الدافعين أرقامهم دون انتظار
                    if all(info["box"] is not None for info in self.predictions.values()):
                        await self.reveal_prediction_results()
                else:
                    # التنبيه الذكي لمنع التوقع قبل الدفع
                    await self.highrise.chat(f"⛔ @{user.username}، توقعك غير محسوب! يجب أن تدفع 5 أولاً في الحصالة لتفعيل التوقع.")

    # 3. بدء اللعبة الأساسية
    async def start_main_game(self):
        self.game_active = True
        await self.highrise.chat("🎮 <color=#FFD700>بدأت الجولة الرسمية! الصناديق الثابتة مغلقة بالكامل الآن!</color>")
        
        # إعداد محتويات الصناديق الـ 10 سرياً في الذاكرة للبدء
        all_contents = ["50", "فخ", "فخ", "1", "1", "فارغ", "فارغ", "فارغ", "فارغ", "فارغ"]
        random.shuffle(all_contents)
        self.boxes = {i+1: all_contents[i] for i in range(10)}
        
        await asyncio.sleep(2)
        await self.check_and_trigger_predictions()

    # 4. التنبيه المرن لفتح جولة التوقعات (بين 2 إلى 4 صناديق متبقية)
    async def check_and_trigger_predictions(self):
        remaining_boxes = list(self.boxes.keys())
        if "50" in self.boxes.values() and 2 <= len(remaining_boxes) <= 4:
            self.game_active = False
            self.prediction_active = True
            
            # الإعلان بألوان حماسية مميزة في الشات
            await self.highrise.chat("🚨 <color=#FF3333><b>[ جولة تنبؤ الحضور والمشرفين ]</b></color> 🚨")
            await self.highrise.chat(f"📦 <color=#FFD700>المتبقي {len(remaining_boxes)} صناديق فقط والـ 50 بالداخل!</color>")
            await self.highrise.chat(f"الصناديق المتاحة هي: {remaining_boxes}")
            await self.highrise.chat("👥 البوت جاهز! من يريد دفع 5 وتوقع الصندوق؟ (أمامكم 45 ثانية أو اكتب /end)")
            
            # وقت مريح وغير ممل للتوقعات
            await asyncio.sleep(45)
            if self.prediction_active:
                await self.reveal_prediction_results()

    # 5. حساب الأرباح بنسبة (70% للفائزين و 30% لك) وإعلان النتائج صندوق صندوق مع الحركات
    async def reveal_prediction_results(self):
        self.prediction_active = False
        await self.highrise.chat("🔒 <color=#FF3333>انتهى الوقت! تم إغلاق باب التوقعات، وبدء الحسم والنتائج...</color>")
        await asyncio.sleep(2)

        # حساب نسبة الـ 70% المضافة فوق الـ 50 الكبرى من توقعات آخر صناديق فقط
        total_prediction_players = len(self.predictions)
        bonus_gold = int((total_prediction_players * 5) * 0.70) 
        final_prize = 50 + bonus_gold                 
        
        await self.highrise.chat(f"📊 <color=#00FF00>الجائزة الإجمالية المحدثة: [ {final_prize} ]</color>")
        await asyncio.sleep(2)

        winning_box = [k for k, v in self.boxes.items() if v == "50"][0]
        winners_list = []
        
        # قائمة رقصات عشوائية متنوعة لمنع الملل عند فتح صندوق فارغ أو 1 جولد
        bad_luck_emotes = ["emote-punch", "emote-pissed", "emote-shock", "emote-damaged", "emote-sad"]

        # حسم وإعلان النتائج سطر سطر (صندوق صندوق) للتشويق وقراءة الجميع
        for box_num, content in sorted(self.boxes.items()):
            players_chosen = [info["username"] for uid, info in self.predictions.items() if info["box"] == box_num]
            players_str = ", ".join(players_chosen) if players_chosen else "لا أحد"
            
            # حالة الصندوق الرابح الكبرى (50+)
            if content == "50":
                await self.highrise.chat(f"📦 الصندوق [{box_num}] لـ ({players_str}) -> 🎉 <color=#FFD700><b>هو الرابح وجائزته {final_prize}!</b></color>")
                
                # إشعال الغرفة بالدبكة والرقص الجماعي لـ كـــل الحاضرين فوراً 🔥🕺
                await self.highrise.chat("🔥 <color=#00FF00><b>كل الغرفة تدبك وترقص احتفالاً بالفوز الجماعي!!</b></color> 🔥")
                for user_id in list(self.room_users):
                    try:
                        await self.highrise.send_emote("emote-dancing", user_id)
                    except:
                        pass 

                # تجميع الفائزين ونقلهم لمنصة الفوز
                for uid, info in self.predictions.items():
                    if info["box"] == box_num:
                        winners_list.append(uid)
                        try:
                            await self.highrise.teleport(uid, self.winner_position)
                        except:
                            pass
            
            # حالة الفخ وسجن اللاعبين
            elif content == "فخ":
                await self.highrise.chat(f"📦 الصندوق [{box_num}] لـ ({players_str}) -> 💀 <color=#FF0000>فخ السجن الفوري!</color>")
                for uid, info in self.predictions.items():
                    if info["box"] == box_num:
                        try:
                            await self.highrise.send_emote("emote-scared", uid)
                            # await self.highrise.teleport(uid, self.jail_position) 
                        except:
                            pass
            
            # حالة الصناديق الفارغة أو 1 جولد (تفعيل الرقصات والحركات العشوائية كالكمة وغيرها)
            elif content in ["1", "فارغ"]:
                await self.highrise.chat(f"📦 الصندوق [{box_num}] لـ ({players_str}) -> ❌ <color=#7F8C8D>صندوق فارغ أو يحتوي 1 فقط!</color>")
                for uid, info in self.predictions.items():
                    if info["box"] == box_num:
                        try:
                            # اختيار حركة عشوائية مختلفة لكل لاعب سيء الحظ (لكمة، صدمة، بكاء...)
                            random_emote = random.choice(bad_luck_emotes)
                            await self.highrise.send_emote(random_emote, uid)
                        except:
                            pass
            
            await asyncio.sleep(3) # فارق 3 ثوانٍ مريح ومشوق جداً بين الصناديق

        # توزيع الذهب النهائي بالتساوي بين الفائزين بالتوقع الصحيح
        if winners_list:
            prize_per_person = final_prize // len(winners_list)
            await self.highrise.chat(f"👑 مبروك للفائزين! تم تقسيم الذهب بالتساوي واستلم كل منكم {prize_per_person}.")
        else:
            await self.highrise.chat("😢 لم يتوقع أحد الصندوق الصحيح! ترحل الأرباح بالكامل لخزنة قيس وبدء جولة جديدة.")

        # تصفير البيانات وتجهيز البوت للجولة التالية
        self.players_paid.clear()
        self.predictions.clear()
        self.boxes.clear()
