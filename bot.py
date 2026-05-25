import asyncio
import random
from highrise import BaseBot, User, CurrencyItem, Position

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
        
        # إحداثيات مرنة تتحدث تلقائياً بأمر (الموقع) داخل الغرفة
        self.bot_platform_position = Position(0.0, 0.0, 0.0) 
        self.jail_position = Position(5.0, 0.0, 5.0)         
        self.winner_position = Position(10.0, 4.0, 10.0)     

    async def on_start(self, session_metadata) -> None:
        print("🤖 البوت متصل بنجاح! اكتب أمر (الموقع) في الشات لتحديد مكاني.")

    async def on_user_join(self, user: User, position: Position) -> None:
        self.room_users.add(user.id)
        # 🟢 الترحيب التلقائي عند دخول أي شخص للغرفة
        await self.highrise.chat(f"أهلاً بك @{user.username} في غرفتنا! 🎮 نحن نلعب لعبة الصناديق المثيرة. ادفع 5 ذهبات لتشترك وتصعد للمنصة فوراً!")

    async def on_user_leave(self, user: User) -> None:
        if user.id in self.room_users:
            self.room_users.remove(user.id)

    # 1. نظام الاستشعار الذكي والسحب الفوري للمنصة
    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem) -> None:
        if receiver.id != self.id or tip.amount < 5:
            return

        # في المرحلة الأساسية: البوت يستشعر ويسحب المشترك للمنصة فوراً ويطلب منه الرقم
        if not self.game_active and not self.prediction_active:
            if len(self.players_paid) >= self.max_players:
                await self.highrise.chat(f"⚠️ @{sender.username} العدد مكتمل حالياً! انتظر الجولة القادمة.")
                return
            
            self.players_paid[sender.id] = sender.username
            await self.highrise.chat(f"✅ تم تسجيل اشتراك @{sender.username} | عدد المشتركين الحاليين: {len(self.players_paid)}/{self.max_players}.")
            
            # 🚀 سحب المشترك تلقائياً للمنصة ليقف بجانب البوت
            try:
                await self.highrise.teleport(sender.id, self.bot_platform_position)
                await self.highrise.chat(f"مبارك السحب يا @{sender.username}! من فضلك اختر رقم صندوقك الآن (1-10) سأحفظه عندي لحين بدء الجولة.")
            except Exception as e:
                print(f"فشل سحب اللاعب للمنصة: {e}")

        # في مرحلة التوقعات: يستقبل الاشتراك "دون سحب الشخص" لمنع الزحمة
        elif self.prediction_active:
            self.predictions[sender.id] = {"username": sender.username, "box": None}
            await self.highrise.chat(f"🟢 تم تفعيل التوقع الخاص بك يا @{sender.username}! اكتب رقم صندوقك الآن في الشات.")

    # 2. قراءة الشات والأوامر الإدارية باللغة العربية
    async def on_chat(self, user: User, message: str) -> None:
        msg = message.strip()
        is_admin = user.username in ["qais29", "sweet_Lulus"]

        # 🟢 استقبال أرقام الصناديق من المتسابقين المسحوبين للمنصة وحفظها سراً لحين بدء الجولة
        if user.id in self.players_paid and not self.game_active and not self.prediction_active:
            if msg.isdigit():
                box_num = int(msg)
                if 1 <= box_num <= 10:
                    self.predictions[user.id] = {"username": user.username, "box": box_num}
                    await self.highrise.chat(f"📌 تم حفظ الصندوق رقم [{box_num}] لـ @{user.username} بنجاح.")
                    return

        if is_admin:
            # 📌 أمر ضبط وتحديد المنصة (تم إصلاحه ليعمل مباشرة بدون شروط معقدة)
            if msg == "الموقع":
                try:
                    room_users = await self.highrise.get_room_users()
                    for u, pos in room_users.content:
                        if u.id == user.id:
                            self.bot_platform_position = pos
                            await self.highrise.teleport(self.id, self.bot_platform_position)
                            await self.highrise.chat("⚡ [تم بنجاح] تم حفظ مكان المنصة الجديد والوقوف فوقها!")
                            return
                except Exception as e:
                    print(f"خطأ أثناء تحديد المنصة: {e}")
                return

            # 📌 أمر سحب البوت إلى موقعك الحالي فوراً
            elif msg == "تعال":
                try:
                    room_users = await self.highrise.get_room_users()
                    for u, pos in room_users.content:
                        if u.id == user.id:
                            await self.highrise.teleport(self.id, pos)
                            await self.highrise.chat("🏃‍♂️ أنا قادم إليك فوراً!")
                            return
                except Exception as e:
                    print(f"خطأ في أمر تعال: {e}")
                return

            # 📌 أمر سحب جميع المتواجدين في الغرفة إلى موقعك الحالي
            elif msg == "سحب الغرفة":
                try:
                    room_users = await self.highrise.get_room_users()
                    my_pos = None
                    for u, pos in room_users.content:
                        if u.id == user.id:
                            my_pos = pos
                            break
                    if my_pos:
                        await self.highrise.chat("⚡ جاري سحب جميع الحضور إلى موقع الإدارة...")
                        for u, pos in room_users.content:
                            if u.id != self.id and u.id != user.id:
                                try: await self.highrise.teleport(u.id, my_pos)
                                except: pass
                except Exception as e:
                    print(f"خطأ في سحب الغرفة: {e}")
                return

            # 📌 أمر بدء اللعبة الأساسية
            if msg == "ابدأ" and not self.game_active:
                if len(self.players_paid) < 1:
                    await self.highrise.chat("❌ لا يمكن بدء اللعبة، عدد المشتركين قليل جداً!")
                    return
                self.game_active = True
                await self.highrise.chat("🎮 <color=#FFD700>بدأت الجولة الرسمية! الصناديق الثابتة مغلقة بالكامل الآن!</color>")
                
                for uid, info in self.predictions.items():
                    if info.get("box") is not None:
                        await self.highrise.chat(f"👤 المتسابق @{info['username']} يشارك بالصندوق رقم: {info['box']}")

                # التوزيع المعتمد (50، 10، خمستين، وواحدين، و4 فارغ)
                all_contents = ["50", "10", "5", "5", "1", "1", "فارغ", "فارغ", "فارغ", "فارغ"]
                random.shuffle(all_contents)
                self.boxes = {i+1: all_contents[i] for i in range(10)}
                return
            
            # 📌 الأمر المنفصل لبدء مرحلة التوقعات وحسمها تلقائياً بعد المهلة
            elif msg == "توقع" and self.game_active and not self.prediction_active:
                remaining_boxes = list(self.boxes.keys())
                self.game_active = False
                self.prediction_active = True
                
                await self.highrise.chat("🚨 <color=#FF3333><b>[ جولة تنبؤ الحضور والمشرفين ]</b></color> 🚨")
                await self.highrise.chat(f"📦 <color=#FFD700>المتبقي {len(remaining_boxes)} صناديق فقط والمفاجأة الكبرى بالداخل!</color>")
                await self.highrise.chat(f"الصناديق المتاحة هي: {remaining_boxes}")
                await self.highrise.chat("👥 البوت جاهز لتلقي التوقعات! من يريد الاشتراك وتوقع الصندوق؟ (أمامكم 45 ثانية للبدء التلقائي)")
                
                # إعطاء مهلة للتوقعات، ثم الفتح والاحتفال تلقائياً
                await asyncio.sleep(45)
                if self.prediction_active:
                    await self.reveal_prediction_results()
                return
                
            # 📌 أمر التصفير وبدء لعبة جديدة كلياً
            elif msg == "انتهى":
                self.game_active = False
                self.prediction_active = False
                self.players_paid.clear()
                self.predictions.clear()
                self.boxes.clear()
                await self.highrise.chat("🔄 <color=#00FF00><b>[ تم إنهاء اللعبة وتصفيرها بالكامل ] تم خلط الجوائز عشوائياً وفتح باب الاشتراك لجولة جديدة كلياً!</b></color>")
                return

        # استقبال أرقام التوقعات من اللاعبين المشتركين في الشات
        if self.prediction_active:
            if msg.isdigit() and int(msg) in self.boxes:
                box_num = int(msg)
                if user.id in self.predictions:
                    self.predictions[user.id]["box"] = box_num
                    await self.highrise.chat(f"📌 تم حفظ توقعك للصندوق [{box_num}] يا @{user.username}")
                    
                    # إذا أدخل الجميع توقعاتهم، يفتح تلقائياً دون انتظار الـ 45 ثانية
                    if all(info.get("box") is not None for info in self.predictions.values()):
                        await self.reveal_prediction_results()
                else:
                    await self.highrise.chat(f"⛔ @{user.username}، توقعك غير محسوب! يرجى الاشتراك أولاً لتفعيل خانة التوقع الخاص بك.")

    # 3. فتح الصناديق والاحتفال التلقائي الفوري فور ظهور الـ 50
    async def reveal_prediction_results(self):
        self.prediction_active = False
        await self.highrise.chat("🔒 <color=#FF3333>انتهى الوقت! تم قفل باب التوقعات، وبدء الحسم والنتائج...</color>")
        await asyncio.sleep(2)

        total_prediction_players = len(self.predictions)
        bonus_gold = int((total_prediction_players * 5) * 0.70) 
        final_prize = 50 + bonus_gold                  
        
        await self.highrise.chat(f"📊 <color=#00FF00>القيمة الإجمالية الحالية للجائزة الكبرى: [ {final_prize} نقطة ]</color>")
        await asyncio.sleep(2)

        winners_list = []
        bad_luck_emotes = ["emote-punch", "emote-pissed", "emote-shock", "emote-damaged", "emote-sad", "emote-wrong"]
        
        empty_box_messages = [
            "💨 طار الهوا! الصندوق فارغ تماماً.. حظاً أوفر الجولة القادمة!",
            "🕸️ للأسف! فتحنا الصندوق ووجدنا شبكة عنكبوت.. فارغ!",
            "🤫 هسسس.. لا يوجد شيء هنا! صندوق فارغ تماماً وخالٍ من المفاجآت.",
            "💸 ياللحظ! الصندوق مصفر وفارغ، الحظ لم يبتسم لك هذه المرة."
        ]

        for box_num, content in sorted(self.boxes.items()):
            players_chosen = [info["username"] for uid, info in self.predictions.items() if info.get("box") == box_num]
            players_str = ", ".join(players_chosen) if players_chosen else "لا أحد"
            
            # 🎉 بمجرد ظهور الـ 50 تبدأ الاحتفالات الكبرى فوراً تلقائياً
            if content == "50":
                await self.highrise.chat(f"📦 الصندوق [{box_num}] لـ ({players_str}) -> 🎉 <color=#FFD700><b>هو الرابح الأكبر وحصل على الجائزة الكبرى بقيمة {final_prize} نقطة!</b></color>")
                
                # 🔥 الدبكة والرقص الجماعي لكل الغرفة فوراً عند الفوز
                await self.highrise.chat("🔥 <color=#00FF00><b>كل الغرفة تدبك وترقص احتفالاً بالفوز الجماعي!!</b></color> 🔥")
                for user_id in list(self.room_users):
                    try: await self.highrise.send_emote("emote-dancing", user_id)
                    except: pass 

                for uid, info in self.predictions.items():
                    if info.get("box") == box_num:
                        winners_list.append(info["username"])
                        try: await self.highrise.teleport(uid, self.winner_position)
                        except: pass
            
            elif content == "10":
                await self.highrise.chat(f"📦 الصندوق [{box_num}] لـ ({players_str}) -> ⭐ <color=#00FFFF>مبارك! يحتوي على جائزة بقيمة 10 نقاط!</color>")
                for uid, info in self.predictions.items():
                    if info.get("box") == box_num:
                        try: await self.highrise.send_emote("emote-celebrate", uid) 
                        except: pass

            elif content == "5":
                await self.highrise.chat(f"📦 الصندوق [{box_num}] لـ ({players_str}) -> 🪙 <color=#FFFF00>جيد! يحتوي على جائزة بقيمة 5 نقاط!</color>")
                for uid, info in self.predictions.items():
                    if info.get("box") == box_num:
                        try: await self.highrise.send_emote("emote-yes", uid)
                        except: pass

            elif content == "1":
                await self.highrise.chat(f"📦 الصندوق [{box_num}] لـ ({players_str}) -> 🎯 <color=#95A5A6>يحتوي على نقطة واحدة كترضية بسيطة!</color>")
                for uid, info in self.predictions.items():
                    if info.get("box") == box_num:
                        try: await self.highrise.send_emote("emote-sad", uid)
                        except: pass
            
            elif content == "فارغ":
                chosen_msg = random.choice(empty_box_messages)
                await self.highrise.chat(f"📦 الصندوق [{box_num}] لـ ({players_str}) -> <color=#E74C3C><b>{chosen_msg}</b></color>")
                for uid, info in self.predictions.items():
                    if info.get("box") == box_num:
                        try:
                            random_emote = random.choice(bad_luck_emotes)
                            await self.highrise.send_emote(random_emote, uid)
                        except: pass
            
            await asyncio.sleep(3) 

        if winners_list:
            prize_per_person = final_prize // len(winners_list)
            await self.highrise.chat(f"👑 مبروك للفائزين: ({', '.join(winners_list)})! يرجى من الإدارة تسليمهم الجائزة الخاصة بهم المستحقة يدوياً.")
        else:
            await self.highrise.chat("😢 لم يتوقع أحد الصندوق الصحيح للجائزة الكبرى! ترحل الجوائز للجولة القادمة.")
