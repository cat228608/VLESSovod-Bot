
<p align="center">
  <img src="https://i.postimg.cc/RVPNdfL9/ava.png" width="200" height="100" alt="Bot Avatar">
</p>

# VLESSovod Bot

Телеграм-бот для раздачи vless конфигураций.

---

## 🚀 Возможности

- Генерация VLESS-конфигураций
- Автоматическое удаление неактивных пользователей (менее 100MB за 48ч)
- Интерактивное Telegram-меню
- Просмотр трафика и QR-кодов
- Поддержка нескольких серверов

---

## ⚙️ Установка и запуск

### 1. Установите необходимые библиотеки

```bash
pip install aiogram==2.20 requests qrcode
```

> Используется `requests` вместо `aiohttp` из-за проблем с авторизацией и cookie в некоторых X-UI-панелях.

### 2. Укажите токен бота

Открой файл `main.py` и добавь свой токен:

```python
API_TOKEN = "ТУТ ТОКЕН"
```

### 3. Добавление сервера

Чтобы бот начал работать с новым сервером, необходимо добавить его вручную в базу данных.

### Шаги:

1. **Открой базу данных `base.db`** любым удобным SQLite-редактором (например, `DB Browser for SQLite` или через консоль).

2. **Найди таблицу `servers`** (или `server`, если используется такое имя).

3. **Добавь новую строку** со следующими значениями:

| Поле            | Значение                                                    |
|-----------------|-------------------------------------------------------------|
| `url`           | Полный URL до X-UI панели (например, `http://ip:port/bsbs`) |
| `username`      | Логин для входа в X-UI панель                               |
| `password`      | Пароль для входа в X-UI панель                              |
| `user_count`    | `0` (при добавлении нового сервера)                         |
| `name`          | Название локации (например, `"Germany"`)                    |

> ⚠️ Убедись, что `url` **включает протокол** (`http://` или `https://`), иначе авторизация не сработает.

### Пример SQL-запроса для добавления (через терминал):

```sql
INSERT INTO servers (id, url, username, password, user_count, location_name)
VALUES ('1', 'http://123.123.123.123:54321', 'admin', 'mypassword', 0, 'Germany');
```

### 4. Где изменить лимиты и пороги

В файле `check_traffic_job.py` находятся параметры автоудаления:

```python
if total_mb < 100:
```

Измени `100` на нужный лимит в мегабайтах.

Также максимальное количество пользователей на сервер задаётся в `handlers.py`, в этом месте:

```python
if db.get_server_user_count(server_id) >= 150:
```

Измени `150` на нужный лимит.

---

## 🧹 Очистка неактивных пользователей

Скрипт `check_traffic_job.py` можно запускать вручную или через планировщик (`cron`, `apscheduler` и т.п.)

### Пример с cron (каждые 30 минут):

```bash
*/30 * * * * /usr/bin/python3 /path/to/check_traffic_job.py
```

---

## 📦 Команды в боте

| Команда / Кнопка            | Описание                                      |
|----------------------------|-----------------------------------------------|
| `/start`                   | Запуск и главное меню                         |
| `Создать конфиг`           | Генерация конфигурации                        |
| `Посмотреть конфигурацию`  | Получение QR-кода и ссылки                    |
| `Профиль`                  | Текущий трафик и статус пользователя          |

---

## ℹ️ Примечания

- Вся логика API взаимодействия с сервером находится в `utils.py`
- Отображение кнопок — в `handlers.py`
- Взаимодействие с Telegram — через `aiogram` версии 2.20


## 🤝 Поддержка и авторство

Этот бот является частью экосистемы основного проекта [@hostvless_bot](https://t.me/hostvless_bot), который обеспечивает всю серверную инфраструктуру и управление.

