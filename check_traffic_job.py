import db
from utils import check_stats, del_client
from aiogram import Bot
from handlers import get_main_menu

async def check_traffic_job(bot: Bot):
    users = db.get_all_users_with_config()
    for user_id, server_id, config_id in users:
        server = db.get_server_by_id(server_id)
        if not server:
            continue

        url, username, password = server
        traffic_data = check_stats(url, username, password, config_id)
        
        if traffic_data is None:
            print(f"[Job Error] Не удалось получить статистику для пользователя {user_id}")
            continue

        total_mb = traffic_data['up'] + traffic_data['down']
        
        if total_mb < 100:
            delete_result = del_client(url, username, password, server_id, config_id)
            if delete_result == '1':
                db.delete_user_config(user_id)
                try:
                    new_menu = get_main_menu(user_has_config=False)
                    await bot.send_message(
                        user_id,
                        "❌ Ваша конфигурация была удалена из-за низкой активности (менее 100MB за 48ч).",
                        reply_markup=new_menu
                    )
                    
                    print(f"Пользователь {user_id} удален из-за неактивности.")
                except Exception as e:
                    print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
            else:
                print(f"Не удалось удалить клиента {config_id} для пользователя {user_id} с сервера.")