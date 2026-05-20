async def on_chat(self, user: User, message: str) -> None:
        message = message.strip().lower()
        username_lower = user.username.lower()

        # تشغيل الـ 10 رقصات لجميع اللاعبين تلقائياً بالرقم
        if message in self.dance_moves:
            try:
                await self.highrise.send_emote(self.dance_moves[message])
            except Exception as e:
                print(f"Error dancing: {e}")
            return

        # 👑 التحكم الحصري والكامل للقائد qais29
        if username_lower == "qais29":
            
            # أمر تثبيت مكان البوت الحالي المطور
            if message == "/setbotpos":
                room_users = await self.highrise.get_room_users()
                for u, pos in room_users.content:
                    if u.id == user.id and isinstance(pos, Position):
                        self.bot_fixed_position = Position(pos.x, pos.y, pos.z, pos.facing)
                        bot_info = await self.highrise.get_bot_info()
                        await self.highrise.teleport(bot_info.user.id, self.bot_fixed_position)
                        await self.highrise.chat("🤖 تم تثبيت موقع وقوف البوت بنجاح!")
                        break

            elif message == "/setprison":
                room_users = await self.highrise.get_room_users()
                for u, pos in room_users.content:
                    if u.id == user.id and isinstance(pos, Position):
                        self.prison_position = pos
                        await self.highrise.chat("🔒 تم تسجيل موقع السجن الحالي بنجاح!")
                        break
            
            elif message == "/setspawn":
                room_users = await self.highrise.get_room_users()
                for u, pos in room_users.content:
                    if u.id == user.id and isinstance(pos, Position):
                        self.spawn_position = pos
                        await self.highrise.chat("🟩 تم تسجيل خط الانطلاق بنجاح!")
                        break

            elif message == "/setvip":
                room_users = await self.highrise.get_room_users()
                for u, pos in room_users.content:
                    if u.id == user.id and isinstance(pos, Position):
                        self.vip_position = pos
                        await self.highrise.chat("💎 تم تحديد منصة الـ VIP الخاصة بك وحمايتها!")
                        break

            elif message == "/setfinish":
                room_users = await self.highrise.get_room_users()
                for u, pos in room_users.content:
                    if u.id == user.id and isinstance(pos, Position):
                        self.finish_position = pos
                        await self.highrise.chat("🏁 تم تسجيل خط نهاية الأمان للتحكيم التلقائي.")
                        break

            elif message == "نسخ اللباس":
                try:
                    room_users = await self.highrise.get_room_users()
                    for u, pos in room_users.content:
                        if u.username.lower() == "qais29":
                            await self.highrise.set_outfit(u.outfit)
                            await self.highrise.chat("👕 تم نسخ لباسك وارتداؤه بنجاح يا قائد!")
                            break
                except Exception as e:
                    print(f"Error copying outfit: {e}")
                    await self.highrise.chat("⚠️ عذراً يا قائد، واجهت مشكلة في قراءة خزانة الملابس.")

            elif message == "ابدأ اللعبة":
                if not self.game_active:
                    self.game_active = True
                    self.game_task = asyncio.create_task(self.game_loop())
                    await self.highrise.chat("🎮 تم تفعيل الإدارة الآلية! البوت مستعد للمراقبة والتحكيم.")

            elif message == "اوقف اللعبة":
                if self.game_active:
                    self.game_active = False
                    self.light = "red"
                    if self.game_task:
                        self.game_task.cancel()
                    await self.highrise.chat("🛑 تم إيقاف اللعبة بنجاح.")

            elif message.startswith("vip"):
                parts = message.split()
                if len(parts) == 1 and self.vip_position.x != 0:
                    await self.highrise.teleport(user.id, self.vip_position)
                    await self.highrise.chat(f"👑 مرحباً بك في منصتك الخاصة يا قائد @{user.username}!")
                elif len(parts) > 1 and self.vip_position.x != 0:
                    target_username = parts[1].replace("@", "").lower()
                    room_users = await self.highrise.get_room_users()
                    found = False
                    for u, pos in room_users.content:
                        if u.username.lower() == target_username:
                            await self.highrise.teleport(u.id, self.vip_position)
                            await self.highrise.chat(f"👑 تم نقل الضيف @{u.username} إلى منصة الـ VIP بنجاح.")
                            found = True
                            break
                    if not found:
                        await self.highrise.chat("تعذر العثور على هذا اللاعب في الغرفة.")

            elif message.startswith("افراج"):
                parts = message.split()
                if len(parts) > 1:
                    target_username = parts[1].replace("@", "").lower()
                    if target_username in self.prisoners:
                        self.prisoners.remove(target_username)
                        await self.highrise.chat(f"🕊️ أمر من القائد! تم العفو اليدوي عن @{target_username} والعودة للعب!")
                        if self.spawn_position.x != 0:
                            room_users = await self.highrise.get_room_users()
                            for u, pos in room_users.content:
                                if u.username.lower() == target_username:
                                    await self.highrise.teleport(u.id, self.spawn_position)
                                    break
                    else:
                        await self.highrise.chat("هذا اللاعب ليس في قائمة المساجين حالياً.")
                        
        else:
            # حماية الأوامر من استخدام بقية اللاعبين المتطفلين
            protected_commands = ["/setbotpos", "/setprison", "/setspawn", "/setvip", "/setfinish", "نسخ اللباس", "ابدأ اللعبة", "اوقف اللعبة"]
            if message in protected_commands or message.startswith("vip") or message.startswith("افراج"):
                await self.highrise.chat(f"❌ عذراً @{user.username}، هذه الأوامر والامتيازات حصرية للقائد qais29 فقط!")
