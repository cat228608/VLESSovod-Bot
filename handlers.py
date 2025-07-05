import random
import os
from aiogram import types, Dispatcher
from aiogram.types import InputFile, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import db
from utils import add_client, check_stats, generate_qr_code

def get_main_menu(user_has_config: bool):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    if user_has_config:
        keyboard.add(KeyboardButton("Профиль"), KeyboardButton("Посмотреть конфигурацию"), KeyboardButton("Инструкции"))
    else:
        keyboard.add(KeyboardButton("Создать конфиг"), KeyboardButton("Инструкции"))
    return keyboard

def register_handlers(dp: Dispatcher):
    @dp.message_handler(commands=["start"])
    async def start_cmd(msg: types.Message):
        user_id = msg.from_user.id
        config = db.get_user_config(user_id)
        has_config = config is not None
        menu = get_main_menu(has_config)
        await msg.answer("Добро пожаловать! 👋", reply_markup=menu)

    @dp.message_handler(lambda m: m.text == "Создать конфиг")
    async def handle_create_config(message: types.Message):
        user_id = message.from_user.id
        if db.get_user_config(user_id):
            await message.answer("❗ У вас уже есть конфигурация.")
            return

        servers = db.get_all_servers()
        if not servers:
            await message.answer("⚠️ Нет доступных серверов.")
            return

        markup = InlineKeyboardMarkup()
        for server_id, name, user_count in servers:
            button_text = f"{name} [{user_count}/150]"
            markup.add(InlineKeyboardButton(text=button_text, callback_data=f"server_{server_id}"))

        await message.answer("Выберите сервер для генерации конфигурации:", reply_markup=markup)
        
    @dp.message_handler(lambda m: m.text == "Посмотреть конфигурацию")
    async def view_config_handler(message: types.Message):
        user_id = message.from_user.id
        config = db.get_user_config(user_id)
        if not config:
            await message.answer("У вас еще нет конфигурации. Создайте ее.", reply_markup=get_main_menu(False))
            return

        _, _, config_url = config
        qr_filename = f"{user_id}_qr_code.png"
        qr_result = generate_qr_code(config_url, qr_filename)

        if qr_result == 'error':
            await message.answer(f"✅ Ваша конфигурация:\n<code>{config_url}</code>", parse_mode="HTML")
        else:
            await message.bot.send_photo(
                chat_id=message.chat.id,
                photo=InputFile(qr_filename),
                caption=f"✅ Ваша конфигурация:\n<code>{config_url}</code>",
                parse_mode="HTML"
            )
            if os.path.exists(qr_filename):
                os.remove(qr_filename)

    @dp.message_handler(lambda m: m.text == "Профиль")
    async def profile_handler(message: types.Message):
        user_id = message.from_user.id
        config = db.get_user_config(user_id)
        
        profile_text = f"<b>📝 Ваш профиль</b>:\n\n🔑 <b>ID:</b> <code>{user_id}</code>\n"

        if config:
            server_id, config_id, _ = config
            server = db.get_server_by_id(server_id)
            if server:
                url, username, password = server
                traffic_data = check_stats(url, username, password, config_id)
                if traffic_data:
                    traffic_info = (f"\n<b>📊 Трафик конфига</b>:\n"
                                    f"📥 Загружено: <i>{traffic_data['down']:.2f} MB</i>\n"
                                    f"📤 Выгружено: <i>{traffic_data['up']:.2f} MB</i>")
                    profile_text += traffic_info
        else:
            profile_text += "\nУ вас нет активной конфигурации."

        await message.reply(profile_text, parse_mode="HTML")

    @dp.callback_query_handler(lambda c: c.data.startswith("server_"))
    async def server_selected(callback_query: types.CallbackQuery):
        user_id = callback_query.from_user.id
        server_id = int(callback_query.data.split("_")[1])

        if db.get_user_config(user_id):
            await callback_query.message.answer("❗ У вас уже есть конфигурация.")
            await callback_query.answer()
            return

        server = db.get_server_by_id(server_id)
        if not server:
            await callback_query.message.answer("❌ Сервер не найден.")
            await callback_query.answer()
            return
            
        if db.get_server_user_count(server_id) >= 150:
            await callback_query.message.answer("🚫 Все места на сервере заняты. Попробуйте другой.")
            await callback_query.answer()
            return

        await callback_query.message.edit_text("⏳ Генерирую конфигурацию...")
        url, username, password = server
        config_id_num = int("".join([str(random.randint(0, 9)) for _ in range(7)]))
        config_id_str = str(user_id) + "_" + str(config_id_num)

        conf = {
            "id": config_id_str, "flow": "xtls-rprx-vision", "email": config_id_str, "limitIp": 0,
            "totalGB": 0, "expiryTime": 0, "enable": True, "tgId": str(user_id), "subId": "", "reset": 0
        }
        
        config_url = add_client(url, username, password, server_id, conf, config_id_str, sni='t.me')

        if config_url == 'error':
            await callback_query.message.edit_text("❌ Ошибка генерации конфигурации. Попробуйте позже.")
            return

        db.save_user_config(user_id, server_id, config_id_str, config_url)
        qr_filename = f"{user_id}_qr_code.png"
        generate_qr_code(config_url, qr_filename)
        await callback_query.bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        
        menu = get_main_menu(user_has_config=True)
        await callback_query.bot.send_photo(
            chat_id=callback_query.message.chat.id,
            photo=InputFile(qr_filename),
            caption=f"✅ Ваша конфигурация создана:\n<code>{config_url}</code>",
            parse_mode="HTML",
            reply_markup=menu
        )
        if os.path.exists(qr_filename):
            os.remove(qr_filename)

        menu = get_main_menu(user_has_config=True)
        await callback_query.bot.send_message(callback_query.from_user.id, "Меню обновлено:", reply_markup=menu)