# ==================== client.py ====================
import telebot
from telebot import types
import requests
import logging
import random
import time
from functools import wraps
import os
from dotenv import load_dotenv

# ==================== ЗАГРУЗКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ ====================
load_dotenv()
ADMIN_ID = os.getenv('ADMIN_ID')
# ==================== КОНФИГУРАЦИЯ ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ==================== ИНИЦИАЛИЗАЦИЯ БОТА ====================

BOT_TOKEN = os.getenv('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

# Настройки API
API_BASE_URL = os.getenv('API_BASE_URL', "http://localhost:8000")
API_TIMEOUT = int(os.getenv('API_TIMEOUT', '10'))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))


# ==================== КЭШ И СОСТОЯНИЯ ====================
class SafeDict:

    def __init__(self, max_age_seconds=3600):
        self.data = {}
        self.timestamps = {}
        self.max_age = max_age_seconds

    def __setitem__(self, key, value):
        self.data[key] = value
        self.timestamps[key] = time.time()
        self._cleanup()

    def __getitem__(self, key):
        self._cleanup()
        return self.data.get(key)

    def get(self, key, default=None):
        self._cleanup()
        return self.data.get(key, default)

    def pop(self, key, default=None):
        self.timestamps.pop(key, None)
        return self.data.pop(key, default)

    def _cleanup(self):
        """Удаляет старые записи"""
        current = time.time()
        to_delete = []
        for key, timestamp in self.timestamps.items():
            if current - timestamp > self.max_age:
                to_delete.append(key)

        for key in to_delete:
            self.data.pop(key, None)
            self.timestamps.pop(key, None)


# Инициализация безопасных словарей
user_states = SafeDict()
user_current_page = SafeDict()
user_selected_players = SafeDict()  # Для хранения выбранных игроков
last_message_ids = SafeDict()


# ==================== ДЕКОРАТОРЫ БЕЗОПАСНОСТИ ====================
def safe_api_call(func):
    """Декоратор для безопасных вызовов API"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        for attempt in range(MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.ConnectionError:
                if attempt == MAX_RETRIES - 1:
                    logging.error(f"API недоступно после {MAX_RETRIES} попыток")
                    return None
                time.sleep(1)
            except requests.exceptions.Timeout:
                logging.warning(f"Таймаут API (попытка {attempt + 1}/{MAX_RETRIES})")
                if attempt == MAX_RETRIES - 1:
                    return None
            except requests.exceptions.RequestException as e:
                logging.error(f"Ошибка API: {e}")
                return None
            except Exception as e:
                logging.error(f"Неожиданная ошибка в {func.__name__}: {e}")
                return None
        return None

    return wrapper


def safe_bot_handler(func):
    """Декоратор для обработчиков бота"""

    @wraps(func)
    def wrapper(message):
        try:
            user_id = str(message.chat.id)

            # Очищаем старые состояния при новом запросе
            if user_id in user_states.data and user_states[user_id]:
                old_state = user_states[user_id]
                # Если состояние старше 5 минут - очищаем
                if time.time() - user_states.timestamps.get(user_id, 0) > 300:
                    user_states.pop(user_id)

            return func(message)
        except Exception as e:
            logging.error(f"Критическая ошибка в {func.__name__}: {e}")
            try:
                bot.send_message(
                    message.chat.id,
                    "❌ Произошла внутренняя ошибка. Пожалуйста, попробуйте снова через минуту.",
                    reply_markup=create_main_menu()
                )
            except:
                pass

    return wrapper


def safe_callback_handler(func):
    """Декоратор для callback обработчиков"""

    @wraps(func)
    def wrapper(call):
        try:
            return func(call)
        except Exception as e:
            logging.error(f"Критическая ошибка в callback {func.__name__}: {e}")
            try:
                bot.answer_callback_query(call.id, "❌ Произошла ошибка. Попробуйте еще раз.")
            except:
                pass

    return wrapper


# ==================== API КЛИЕНТ ====================
@safe_api_call
def api_get(endpoint):
    """Безопасный GET запрос к API"""
    response = requests.get(
        f"{API_BASE_URL}{endpoint}",
        timeout=API_TIMEOUT
    )
    response.raise_for_status()
    data = response.json()

    # Проверка структуры ответа
    if not isinstance(data, dict):
        logging.error(f"Неверный формат ответа от API: {type(data)}")
        return None

    return data


@safe_api_call
def api_post(endpoint, data):
    """Безопасный POST запрос к API"""
    response = requests.post(
        f"{API_BASE_URL}{endpoint}",
        json=data,
        timeout=API_TIMEOUT
    )
    response.raise_for_status()
    data = response.json()

    if not isinstance(data, dict):
        logging.error(f"Неверный формат ответа от API: {type(data)}")
        return None

    return data


# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================
def create_main_menu():
    """Создает главное меню"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        types.KeyboardButton("👤 Мои матчи"),
        types.KeyboardButton("📊 Герои"),
        types.KeyboardButton("🔍 Инфо о герое"),
        types.KeyboardButton("📈 Моя статистика"),
        types.KeyboardButton("🎮 Матчи игрока"),
        types.KeyboardButton("🔄 Обновить данные"),
        types.KeyboardButton("ℹ️ Помощь")
    ]
    markup.add(*buttons)
    return markup


def create_matches_keyboard(has_prev=True, has_next=True, is_my_matches=False):
    """Создает безопасную клавиатуру для навигации"""
    markup = types.InlineKeyboardMarkup(row_width=2)

    buttons = []
    if has_prev:
        buttons.append(types.InlineKeyboardButton("⬅️ Назад", callback_data=f"matches_prev_{is_my_matches}"))
    if has_next:
        buttons.append(types.InlineKeyboardButton("➡️ Вперед", callback_data=f"matches_next_{is_my_matches}"))

    if buttons:
        markup.add(*buttons)

    action_buttons = []
    if is_my_matches:
        action_buttons.append(types.InlineKeyboardButton("🔄 Обновить", callback_data="my_matches_refresh"))
    else:
        action_buttons.append(types.InlineKeyboardButton("🔄 Новые", callback_data="matches_new"))

    action_buttons.append(types.InlineKeyboardButton("↩️ Меню", callback_data="matches_back"))

    if action_buttons:
        markup.add(*action_buttons)

    return markup


def validate_user_input(text, max_length=100):
    """Валидация пользовательского ввода"""
    if not text or not isinstance(text, str):
        return False
    if len(text.strip()) == 0:
        return False
    if len(text) > max_length:
        return False
    return True


# ==================== ОСНОВНЫЕ ОБРАБОТЧИКИ ====================
def notify_admin(message_text):
    """Отправляет сообщение администратору"""
    try:
        if ADMIN_ID:
            bot.send_message(ADMIN_ID, f"🤖 Бот: {message_text}")
    except Exception as e:
        logging.error(f"Не удалось отправить уведомление админу: {e}")

@bot.message_handler(commands=['start', 'help', 'restart'])
@safe_bot_handler
def send_welcome(message):
    """Главное меню бота"""
    user_id = str(message.chat.id)

    # Полная очистка состояний пользователя
    user_states.pop(user_id)
    user_current_page.pop(user_id)
    user_selected_players.pop(user_id)

    # Получение или создание профиля
    user_name = "Игрок"
    if message.from_user and message.from_user.first_name:
        user_name = message.from_user.first_name
        if message.from_user.last_name:
            user_name = f"{user_name} {message.from_user.last_name}"

    # Безопасное создание профиля
    profile_data = {"user_id": user_id, "user_name": user_name}
    response = api_post("/player/create", profile_data)

    welcome_text = "🎮 *Dota 2 Stats Bot*\n\n"
    if response and response.get("success"):
        player = response.get("player", {})
        welcome_text += f"👋 Привет, *{player.get('name', user_name)}*!\n"
        welcome_text += f"📊 MMR: *{player.get('mmr', 0)}*\n"
        welcome_text += f"🏆 Винрейт: *{player.get('win_rate', 0)}%*\n\n"
    else:
        welcome_text += f"👋 Привет, *{user_name}*!\n\n"

    welcome_text += (
        "📋 *Доступные команды:*\n"
        "• 👤 Мои матчи - Ваша история\n"
        "• 📊 Герои - Список героев\n"
        "• 🔍 Инфо о герое - Детали героя\n"
        "• 📈 Моя статистика - Ваши статы\n"
        "• 🎮 Матчи игрока - Матчи других\n"
        "• 🔄 Обновить - Новые данные\n\n"
        "💡 *Все данные случайны!*"
    )

    markup = create_main_menu()
    try:
        msg = bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='Markdown')
        last_message_ids[user_id] = msg.message_id
    except Exception as e:
        logging.error(f"Ошибка отправки welcome: {e}")
    notify_admin(f"Пользователь {user_name} запустил бота (ID: {user_id})")

@bot.message_handler(func=lambda message: message.text == "👤 Мои матчи")
@safe_bot_handler
def show_my_matches(message):
    """Показывает матчи текущего пользователя"""
    user_id = str(message.chat.id)

    # Очищаем состояние выбора игрока
    user_selected_players.pop(user_id)

    # Получаем матчи
    response = api_post("/matches", {
        "user_id": user_id,
        "is_my_matches": True
    })

    if not response or not response.get("success"):
        bot.send_message(message.chat.id,
                         "❌ Не удалось загрузить ваши матчи.\nПопробуйте позже.",
                         reply_markup=create_main_menu())
        return

    player_info = response.get("player", {})
    user_current_page[user_id] = {
        "page": 0,
        "player_name": player_info.get("name", ""),
        "is_my_matches": True,
        "timestamp": time.time()
    }

    # Показываем первую страницу
    show_matches_page_safe(message.chat.id, 0, True)


@bot.message_handler(func=lambda message: message.text == "🎮 Матчи игрока")
@safe_bot_handler
def show_player_matches_menu(message):
    """Меню выбора игрока для просмотра матчей"""
    user_id = str(message.chat.id)

    # Очищаем предыдущее состояние
    user_states.pop(user_id)
    user_selected_players.pop(user_id)

    # Устанавливаем состояние и создаем чистое меню
    user_states[user_id] = "waiting_player_for_matches"

    # Создаем чистое меню без старых кнопок
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("❌ Отмена"),
        types.KeyboardButton("🎲 Случайный")
    )

    # Получаем список игроков
    response = api_get("/players")
    players = []
    if response and response.get("success"):
        players = response.get("players", [])

    help_text = "🎮 *Выберите игрока:*\n\n"
    if players:
        help_text += "*Доступные игроки:*\n"
        for player in players[:4]:
            help_text += f"• {player.get('name', 'Unknown')}\n"
        help_text += "\n*Или:*\n• Введите имя игрока\n• Нажмите '🎲 Случайный'\n• '❌ Отмена' - в меню"
    else:
        help_text += "Введите имя игрока или нажмите '🎲 Случайный'"

    try:
        bot.send_message(message.chat.id, help_text, reply_markup=markup, parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Ошибка отправки меню игроков: {e}")
        bot.send_message(message.chat.id,
                         "❌ Ошибка при загрузке меню.\nИспользуйте команды из главного меню.",
                         reply_markup=create_main_menu())


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "waiting_player_for_matches")
@safe_bot_handler
def handle_player_matches_request(message):
    """Обработка выбора игрока"""
    user_id = str(message.chat.id)
    user_input = message.text.strip()

    # Обработка отмены
    if user_input == "❌ Отмена":
        user_states.pop(user_id)
        user_selected_players.pop(user_id)
        send_welcome(message)
        return

    # Определяем имя игрока
    player_name = ""
    if user_input == "🎲 Случайный":
        response = api_get("/players")
        if response and response.get("success"):
            players = response.get("players", [])
            if players:
                player_name = random.choice(players).get('name', 'DemoPlayer')
        if not player_name:
            player_name = "DemoPlayer"
    else:
        player_name = user_input

    # Сохраняем выбранного игрока
    user_selected_players[user_id] = player_name
    user_states.pop(user_id)

    # Устанавливаем состояние для пагинации
    user_current_page[user_id] = {
        "page": 0,
        "player_name": player_name,
        "is_my_matches": False,
        "timestamp": time.time()
    }

    # Показываем матчи
    show_matches_page_safe(message.chat.id, 0, False)


def show_matches_page_safe(chat_id, page, is_my_matches):
    """Безопасное отображение страницы матчей"""
    try:
        user_id = str(chat_id)
        page_data = user_current_page.get(user_id)

        if not page_data:
            bot.send_message(chat_id, "❌ Сессия устарела. Начните заново.")
            return

        player_name = page_data.get("player_name", "")

        # Получаем страницу через API
        endpoint = f"/matches/{user_id}/{page}"
        params = f"?player_name={player_name}&is_my_matches={is_my_matches}"
        response = api_get(endpoint + params)

        if not response or not response.get("success"):
            bot.send_message(chat_id, "❌ Не удалось загрузить матчи.")
            return

        player_info = response.get("player", {})
        matches = response.get("matches", [])
        pagination = response.get("pagination", {})

        # Форматируем текст
        if is_my_matches:
            text = f"👤 *Мои матчи*\n"
        else:
            text = f"🎮 *Матчи: {player_info.get('name', player_name)}*\n"

        text += f"📊 {player_info.get('mmr', 0)} MMR | 🏆 {player_info.get('win_rate', 0)}%\n"
        text += f"📄 Страница {page + 1}/{pagination.get('total_pages', 1)}\n\n"

        if not matches:
            text += "📭 Матчи не найдены\n"
        else:
            for match in matches[:5]:
                result = "✅" if "Победа" in str(match.get('result', '')) else "❌"
                text += f"{result} *Матч #{match.get('match_num', 0)}*\n"
                text += f"🎯 {match.get('hero', '?')} | {match.get('result', '?')}\n"
                text += f"⏱️ {match.get('duration', '0:00')} | ⚔️ {match.get('kda', '0/0/0')}\n"
                text += f"💰 {match.get('gpm', 0)} | 📈 {match.get('xpm', 0)}\n"
                text += "─" * 25 + "\n"

        # Создаем клавиатуру
        has_prev = pagination.get('has_prev', False) and page > 0
        has_next = pagination.get('has_next', False)
        markup = create_matches_keyboard(has_prev, has_next, is_my_matches)

        # Обновляем страницу
        user_current_page[user_id] = {
            **page_data,
            "page": page,
            "timestamp": time.time()
        }

        # Отправляем или редактируем
        last_msg_id = last_message_ids.get(user_id)
        if last_msg_id:
            try:
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=last_msg_id,
                    text=text,
                    reply_markup=markup,
                    parse_mode='Markdown'
                )
                return
            except Exception as e:
                logging.warning(f"Не удалось редактировать сообщение: {e}")

        # Отправляем новое
        msg = bot.send_message(chat_id, text, reply_markup=markup, parse_mode='Markdown')
        last_message_ids[user_id] = msg.message_id

    except Exception as e:
        logging.error(f"Ошибка show_matches_page: {e}")
        bot.send_message(chat_id, "❌ Ошибка при отображении матчей.")


@bot.callback_query_handler(func=lambda call: call.data.startswith('matches_'))
@safe_callback_handler
def handle_matches_callback(call):
    """Обработка навигации по матчам"""
    user_id = str(call.message.chat.id)

    if call.data == "matches_back":
        # Возврат в меню с полной очисткой
        user_states.pop(user_id)
        user_current_page.pop(user_id)
        user_selected_players.pop(user_id)

        markup = create_main_menu()
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="↩️ Возвращаемся в главное меню...",
            reply_markup=None
        )
        bot.send_message(user_id, "Главное меню:", reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    # Проверяем наличие данных о странице
    page_data = user_current_page.get(user_id)
    if not page_data:
        bot.answer_callback_query(call.id, "❌ Сессия устарела")
        return

    current_page = page_data.get("page", 0)
    is_my_matches = page_data.get("is_my_matches", False)

    # Определяем новую страницу
    new_page = current_page
    if call.data.startswith("matches_prev_"):
        new_page = max(0, current_page - 1)
    elif call.data.startswith("matches_next_"):
        new_page = current_page + 1
    elif call.data == "my_matches_refresh":
        new_page = 0
    elif call.data == "matches_new":
        new_page = 0

    # Показываем страницу
    show_matches_page_safe(call.message.chat.id, new_page, is_my_matches)
    bot.answer_callback_query(call.id, f"📄 Страница {new_page + 1}")


@bot.message_handler(func=lambda message: message.text == "📊 Герои")
@safe_bot_handler
def get_heroes(message):
    """Список героев"""
    response = api_get("/heroes")

    if not response or not response.get("success"):
        bot.send_message(message.chat.id, "❌ Не удалось загрузить героев.")
        return

    heroes = response.get("heroes", [])
    text = "🎯 *Герои Dota 2*\n\n"

    for hero in sorted(heroes, key=lambda x: x.get('id', 0))[:15]:
        stats = hero.get('hero_stats', {})
        text += f"• *{hero.get('id', 0)}.* {hero.get('name', '?')}\n"
        text += f"  📊 {hero.get('attribute', '?')} | 🏆 {stats.get('win_rate', 0)}%\n"

    text += "\n💡 *Используйте '🔍 Инфо о герое' для деталей*"

    bot.send_message(message.chat.id, text, parse_mode='Markdown')


@bot.message_handler(func=lambda message: message.text == "🔍 Инфо о герое")
@safe_bot_handler
def show_hero_info_menu(message):
    """Меню запроса информации о герое"""
    user_id = str(message.chat.id)
    user_states[user_id] = "waiting_hero_info"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("🎲 Случайный герой"),
        types.KeyboardButton("❌ Отмена")
    )

    help_text = (
        "🔍 *Получение информации о герое*\n\n"
        "*Как использовать:*\n"
        "• Введите ID героя (1-20)\n"
        "• Или имя героя\n"
        "• Или нажмите '🎲 Случайный герой'\n\n"
        "*Пример:*\n"
        "`8` или `Juggernaut`"
    )

    bot.send_message(message.chat.id, help_text, reply_markup=markup, parse_mode='Markdown')


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "waiting_hero_info")
@safe_bot_handler
def handle_hero_info_request(message):
    """Обработка запроса информации о герое"""
    user_id = str(message.chat.id)
    user_input = message.text.strip()

    if user_input == "❌ Отмена":
        user_states.pop(user_id)
        send_welcome(message)
        return

    # Определяем hero_id
    hero_id = None
    if user_input == "🎲 Случайный герой":
        hero_id = random.randint(1, 20)
    else:
        # Пробуем как число
        if user_input.isdigit():
            hero_id = int(user_input)
            if hero_id < 1 or hero_id > 20:
                bot.send_message(message.chat.id, "❌ ID героя должен быть от 1 до 20")
                return
        else:
            # Ищем по имени
            response = api_get("/heroes")
            if response and response.get("success"):
                heroes = response.get("heroes", [])
                for hero in heroes:
                    if user_input.lower() in hero.get('name', '').lower():
                        hero_id = hero.get('id')
                        break

            if not hero_id:
                bot.send_message(message.chat.id, "❌ Герой не найден. Введите ID (1-20) или имя")
                return

    # Получаем информацию о герое
    response = api_post("/hero/info", {"hero_id": hero_id})

    if not response or not response.get("success"):
        bot.send_message(message.chat.id, "❌ Не удалось получить информацию о герое")
        user_states.pop(user_id)
        send_welcome(message)
        return

    hero = response.get("hero", {})
    stats = hero.get('hero_stats', {})

    # Форматируем текст
    text = f"🎯 *{hero.get('name', '?')}*\n"
    text += f"📊 Атрибут: *{hero.get('attribute', '?')}*\n\n"

    text += "*Статистика:*\n"
    text += f"🏆 Винрейт: *{stats.get('win_rate', 0)}%*\n"
    text += f"📈 Пик рейт: *{stats.get('pick_rate', 0)}%*\n"
    text += f"⚔️ Средний KDA: *{stats.get('avg_kills', 0):.1f}*/{stats.get('avg_deaths', 0):.1f}*/{stats.get('avg_assists', 0):.1f}*\n"

    # Случайные советы
    tips = [
        "Сильный в ранней игре, фокусируйтесь на фарме",
        "Отличный инициатор, используйте ульту в тимфайтах",
        "Силен в поздней игре, избегайте ранних конфликтов",
        "Хорош в роами, помогайте другим линиям",
        "Требует много фарма, защищайте его в лейте"
    ]

    text += f"\n💡 *Совет:* {random.choice(tips)}"

    markup = create_main_menu()
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='Markdown')
    user_states.pop(user_id)


@bot.message_handler(func=lambda message: message.text == "📈 Моя статистика")
@safe_bot_handler
def show_my_stats(message):
    """Показывает статистику текущего пользователя"""
    user_id = str(message.chat.id)

    response = api_get(f"/stats/{user_id}")

    if not response or not response.get("success"):
        bot.send_message(message.chat.id, "❌ Не удалось загрузить статистику")
        return

    stats = response.get("stats", {})

    text = f"📊 *Статистика: {stats.get('name', 'Игрок')}*\n\n"
    text += f"🏆 MMR: *{stats.get('mmr', 0)}*\n"
    text += f"📈 Винрейт: *{stats.get('win_rate', 0)}%* ({stats.get('wins', 0)}/{stats.get('games', 0)})\n\n"

    text += "*Средние показатели:*\n"
    text += f"⚔️ KDA: *{stats.get('avg_kills', 0):.1f}*/{stats.get('avg_deaths', 0):.1f}*/{stats.get('avg_assists', 0):.1f}\n"

    # Расчет эффективности
    if stats.get('games', 0) > 0:
        efficiency = (stats.get('win_rate', 0) * 0.7 +
                      (stats.get('avg_kills', 0) + stats.get('avg_assists', 0)) /
                      max(stats.get('avg_deaths', 1), 1) * 30)
        text += f"📊 Эффективность: *{efficiency:.1f}/100*\n"

    # Рандомные достижения
    achievements = [
        "🏅 Мастер фарма",
        "⚡ Быстрая реакция",
        "🛡️ Надежный союзник",
        "🎯 Точно в цель",
        "👑 Лидер команды"
    ]

    text += f"\n🏅 *Достижение:* {random.choice(achievements)}"

    markup = create_main_menu()
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='Markdown')


@bot.message_handler(func=lambda message: message.text == "🔄 Обновить данные")
@safe_bot_handler
def refresh_data(message):
    """Добавляет новый матч для пользователя"""
    user_id = str(message.chat.id)

    response = api_post("/match/add", {"user_id": user_id})

    if not response or not response.get("success"):
        bot.send_message(message.chat.id, "❌ Не удалось добавить матч")
        return

    match = response.get("match", {})

    text = "🔄 *Добавлен новый матч!*\n\n"
    result_emoji = "✅" if match.get('result') == "Победа" else "❌"
    text += f"{result_emoji} *Матч #{match.get('match_num', 0)}*\n"
    text += f"🎯 Герой: *{match.get('hero', '?')}*\n"
    text += f"📊 Результат: *{match.get('result', '?')}*\n"
    text += f"⏱️ Длительность: *{match.get('duration', '0:00')}*\n"
    text += f"⚔️ KDA: *{match.get('kda', '0/0/0')}*\n"
    text += f"💰 GPM: *{match.get('gpm', 0)}* | 📈 XPM: *{match.get('xpm', 0)}*\n"

    # Случайный комментарий
    comments = [
        "Отличная игра! Продолжайте в том же духе!",
        "Неплохо, но есть куда расти!",
        "Хороший фарм, но нужно больше участвовать в тимфайтах",
        "Отличные инициации!",
        "Попробуйте другого героя в следующей игре"
    ]

    text += f"\n💡 *Комментарий:* {random.choice(comments)}"

    markup = create_main_menu()
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='Markdown')


@bot.message_handler(func=lambda message: message.text == "ℹ️ Помощь")
@safe_bot_handler
def show_help(message):
    """Помощь"""
    help_text = (
        "🎮 *Dota 2 Stats Bot*\n\n"
        "*Основные функции:*\n"
        "• 👤 Мои матчи - Ваша история\n"
        "• 📊 Герои - Список героев\n"
        "• 🔍 Инфо о герое - Детали\n"
        "• 📈 Моя статистика - Ваши статы\n"
        "• 🎮 Матчи игрока - Другие игроки\n"
        "• 🔄 Обновить - Новые данные\n\n"
        "*Управление:*\n"
        "• Используйте кнопки меню\n"
        "• Для матчей: ⬅️➡️ навигация\n"
        "• /start - Перезапуск\n\n"
        "💡 *Все данные случайны!*"
    )
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')


# Обработчик для остальных сообщений
@bot.message_handler(func=lambda message: True)
@safe_bot_handler
def handle_unknown(message):
    """Обработка неизвестных команд"""
    user_id = str(message.chat.id)
    current_state = user_states.get(user_id)

    # Если есть активное состояние - обрабатываем
    if current_state == "waiting_player_for_matches":
        handle_player_matches_request(message)
    elif current_state == "waiting_hero_info":
        handle_hero_info_request(message)
    else:
        # Иначе показываем меню
        bot.send_message(
            message.chat.id,
            "🤔 Не понял команду.\n\nИспользуйте кнопки меню ниже:",
            reply_markup=create_main_menu()
        )


# ==================== ЗАПУСК БОТА ====================
if __name__ == "__main__":
    print("=" * 50)
    print("🤖 Dota 2 Stats Bot запускается...")
    print(f"🔗 API: {API_BASE_URL}")
    print("🛡️  Режим: Защищенный от сбоев")
    print("=" * 50)

    try:
        # Проверка подключения к API
        print("🔌 Проверка подключения к API...")
        try:
            test_response = requests.get(f"{API_BASE_URL}/", timeout=5)
            if test_response.status_code == 200:
                print("✅ API доступно")
            else:
                print(f"⚠️  API отвечает с кодом {test_response.status_code}")
        except Exception as e:
            print(f"❌ API недоступно: {e}")
            print("⚠️  Бот будет работать в ограниченном режиме")

        print("📱 Запуск polling...")
        bot.polling(none_stop=True, interval=1, timeout=20)

    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
        print("🔄 Попробуйте перезапустить бота")