import telebot
from telebot import types
import requests
import json
import logging
import random
from datetime import datetime, timedelta

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Инициализация бота
bot = telebot.TeleBot('8328415828:AAFBJ2yOBr3UzQZw6a9EI7y0h4GH91szmsU')


# Генераторы случайных данных
class DemoDataGenerator:
    def __init__(self):
        self.hero_names = [
            "Dragon Knight", "Phantom Assassin", "Storm Spirit", "Tidehunter", "Lina",
            "Lion", "Shadow Shaman", "Slark", "Venomancer", "Witch Doctor",
            "Zeus", "Riki", "Ursa", "Templar Assassin", "Nyx Assassin",
            "Magnus", "Invoker", "Dark Willow", "Mars", "Hoodwink"
        ]

        self.player_names = [
            "Dendi", "Arteezy", "Topson", "Ana", "Puppey",
            "KuroKy", "s4", "Universe", "Faith_Bian", "y`",
            "GH", "JerAx", "Ceb", "Notail", "Miracle-",
            "SumaiL", "Nisha", "MATUMBAMAN", "Zai", "iceiceice"
        ]

        self.abilities = [
            "Fireball", "Thunder Strike", "Shadow Walk", "Healing Wave", "Frost Nova",
            "Chain Lightning", "Poison Dart", "Time Lock", "Reality Rift", "Dream Coil",
            "Chaos Meteor", "Sun Strike", "Ice Wall", "Deafening Blast", "Ghost Walk",
            "Boulder Smash", "Rolling Thunder", "Static Storm", "Chronosphere", "Black Hole"
        ]

        self.hero_roles = ["Carry", "Support", "Nuker", "Disabler", "Initiator", "Durable", "Escape", "Pusher"]
        self.attributes = ["STRENGTH", "AGILITY", "INTELLIGENCE"]
        self.regions = ["Europe", "China", "SE Asia", "NA", "CIS", "SA"]
        self.items = ["Black King Bar", "Aghanim's Scepter", "Blink Dagger", "Heart of Tarrasque", "Butterfly",
                      "Divine Rapier"]

    def generate_hero(self, hero_id):
        name = random.choice(self.hero_names)
        attribute = random.choice(self.attributes)
        roles = random.sample(self.hero_roles, random.randint(2, 4))

        # Генерируем статистику для героя
        pick_rate = round(random.uniform(5.0, 25.0), 1)
        win_rate = round(random.uniform(45.0, 55.0), 1)
        kda = round(random.uniform(2.0, 4.5), 2)

        return {
            "id": hero_id,
            "name": name,
            "attribute": attribute,
            "roles": roles,
            "abilities": random.sample(self.abilities, 4),
            "lore": f"Легендарный герой, известный своими подвигами на полях сражений. {name} обладает уникальными способностями, которые делают его грозным противником.",
            "stats": {
                "health": random.randint(500, 800),
                "mana": random.randint(200, 500),
                "damage": f"{random.randint(45, 65)}-{random.randint(55, 85)}",
                "armor": round(random.uniform(1.0, 8.0), 1),
                "move_speed": random.randint(285, 325),
                "attack_range": random.choice([150, 350, 400, 450, 500, 600])
            },
            "hero_stats": {
                "pick_rate": pick_rate,
                "win_rate": win_rate,
                "kda": kda,
                "matches_played": random.randint(50000, 500000),
                "farm": random.randint(400, 800)
            }
        }

    def generate_player(self, user_name=None):
        if user_name:
            name = user_name
        else:
            name = random.choice(self.player_names)

        level = random.randint(30, 150)
        matches = random.randint(1000, 10000)
        wins = random.randint(matches // 2, matches - 100)

        return {
            "name": name,
            "level": level,
            "mmr": random.randint(3000, 11000),
            "matches": matches,
            "wins": wins,
            "win_rate": round((wins / matches) * 100, 1),
            "region": random.choice(self.regions),
            "favorite_heroes": random.sample(range(1, 21), 3),
            "achievements": random.sample([
                "Топ 100 Immortal", "Победитель мейджора", "Чемпион локальной лиги",
                "MVP турнира", "Рекордсмен по GPM", "Лучший саппорт сезона"
            ], random.randint(1, 3))
        }

    def generate_player_hero_stats(self, player_name, hero_id, hero_name):
        """Генерирует личную статистику игрока на герое"""
        matches = random.randint(5, 200)
        wins = random.randint(1, matches)
        win_rate = round((wins / matches) * 100, 1)

        return {
            "hero_id": hero_id,
            "hero_name": hero_name,
            "matches": matches,
            "wins": wins,
            "losses": matches - wins,
            "win_rate": win_rate,
            "kda": round(random.uniform(1.5, 5.0), 2),
            "avg_kills": round(random.uniform(3.0, 12.0), 1),
            "avg_deaths": round(random.uniform(2.0, 8.0), 1),
            "avg_assists": round(random.uniform(4.0, 15.0), 1),
            "avg_gpm": random.randint(350, 700),
            "avg_xpm": random.randint(400, 800),
            "last_played": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%d.%m.%Y"),
            "best_streak": random.randint(1, 10),
            "favorite_role": random.choice(["Carry", "Support", "Mid", "Offlane"]),
            "performance": random.choice(["Отлично", "Хорошо", "Удовлетворительно", "Нужна практика"])
        }

    def generate_matches_batch(self, player_name, count=30):
        """Генерирует пачку матчей для игрока"""
        matches = []
        for i in range(count):
            duration = random.randint(1200, 3600)
            kills = random.randint(2, 25)
            deaths = random.randint(2, 15)
            assists = random.randint(0, 30)

            match = {
                "id": random.randint(1000000, 9999999),
                "hero": random.choice(self.hero_names),
                "result": random.choice(["🏆 Победа", "💀 Поражение"]),
                "duration": f"{duration // 60}:{duration % 60:02d}",
                "kda": f"{kills}/{deaths}/{assists}",
                "gpm": random.randint(300, 800),
                "xpm": random.randint(400, 900),
                "hero_damage": random.randint(5000, 35000),
                "tower_damage": random.randint(500, 5000),
                "items": random.sample(self.items, 6),
                "date": (datetime.now() - timedelta(days=random.randint(i * 2, i * 2 + 10))).strftime("%d.%m.%Y"),
                "match_num": i + 1
            }
            matches.append(match)

        return matches


# Инициализация генератора
demo_gen = DemoDataGenerator()

# Генерация начальных данных
DEMO_HEROES = {i: demo_gen.generate_hero(i) for i in range(1, 21)}
DEMO_PLAYERS = [demo_gen.generate_player() for _ in range(10)]

# Словари для хранения состояний
user_states = {}
user_matches = {}
user_current_page = {}
user_profiles = {}
last_message_ids = {}
user_hero_stats = {}


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Главное меню бота"""
    try:
        markup = create_main_menu()

        # Создаем профиль пользователя если его нет
        user_id = message.chat.id
        if user_id not in user_profiles:
            user_name = message.from_user.first_name
            if message.from_user.last_name:
                user_name += f" {message.from_user.last_name}"
            user_profiles[user_id] = demo_gen.generate_player(user_name)

            # Генерируем начальную статистику по героям
            user_hero_stats[user_id] = {}
            for hero_id in range(1, 6):  # Статистика по первым 5 героям
                hero = DEMO_HEROES[hero_id]
                user_hero_stats[user_id][hero_id] = demo_gen.generate_player_hero_stats(
                    user_profiles[user_id]['name'], hero_id, hero['name']
                )

        welcome_text = f"""
🎮 *Dota 2 Stats Bot - Случайные демо-данные* 

👋 Привет, *{user_profiles[user_id]['name']}*!
📊 Твой MMR: *{user_profiles[user_id]['mmr']}*
🏆 Винрейт: *{user_profiles[user_id]['win_rate']}%*

*Сгенерировано для вас:*
🤺 {len(DEMO_HEROES)} уникальных героев
👥 {len(DEMO_PLAYERS)} профессиональных игроков
📈 Личная статистика по героям
🎯 Реалистичная статистика матчей

*Доступные команды:*
👤 Мои матчи - Твоя история матчей
📊 Герои - Список героев со статистикой
🔍 Инфо о герое - Детали любого героя
📈 Моя статистика - Личная статистика по героям
🎮 Матчи игрока - Матчи других игроков
🔄 Обновить данные - Новые случайные данные

💡 *Все данные генерируются случайно!*
        """

        msg = bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='Markdown')
        last_message_ids[user_id] = msg.message_id
        logging.info(f"Пользователь {message.chat.id} запустил бота")

    except Exception as e:
        logging.error(f"Ошибка в send_welcome: {e}")
        bot.send_message(message.chat.id, "❌ Произошла ошибка. Попробуйте еще раз.")


def create_main_menu():
    """Создает главное меню"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("👤 Мои матчи")
    btn2 = types.KeyboardButton("📊 Герои")
    btn3 = types.KeyboardButton("🔍 Инфо о герое")
    btn4 = types.KeyboardButton("📈 Моя статистика")
    btn5 = types.KeyboardButton("🎮 Матчи игрока")
    btn6 = types.KeyboardButton("🔄 Обновить данные")
    btn7 = types.KeyboardButton("ℹ️ Помощь")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
    return markup


def create_matches_keyboard(has_prev=True, has_next=True, is_my_matches=False):
    """Создает клавиатуру для навигации по матчам"""
    markup = types.InlineKeyboardMarkup(row_width=2)

    buttons = []

    # Кнопки навигации
    if has_prev:
        buttons.append(types.InlineKeyboardButton("⬅️ Назад", callback_data="matches_prev"))
    if has_next:
        buttons.append(types.InlineKeyboardButton("➡️ Вперед", callback_data="matches_next"))

    # Добавляем кнопки навигации в первый ряд
    if buttons:
        markup.add(*buttons)

    # Кнопки действий
    action_buttons = []
    if is_my_matches:
        action_buttons.append(types.InlineKeyboardButton("🔄 Обновить мои матчи", callback_data="my_matches_refresh"))
    else:
        action_buttons.append(types.InlineKeyboardButton("🔄 Новые матчи", callback_data="matches_new"))

    action_buttons.append(types.InlineKeyboardButton("↩️ В главное меню", callback_data="matches_back"))

    # Добавляем кнопки действий во второй ряд
    markup.add(*action_buttons)

    return markup


@bot.message_handler(func=lambda message: message.text == "👤 Мои матчи")
def show_my_matches(message):
    """Показывает матчи текущего пользователя"""
    try:
        user_id = message.chat.id

        # Получаем или создаем профиль пользователя
        if user_id not in user_profiles:
            user_name = message.from_user.first_name
            if message.from_user.last_name:
                user_name += f" {message.from_user.last_name}"
            user_profiles[user_id] = demo_gen.generate_player(user_name)

        player_info = user_profiles[user_id]

        # Генерируем матчи для пользователя если их нет
        if user_id not in user_matches or user_matches[user_id].get('player', {}).get('name') != player_info['name']:
            user_matches[user_id] = {
                'player': player_info,
                'matches': demo_gen.generate_matches_batch(player_info['name'], 30),
                'current_page': 0,
                'is_my_matches': True
            }

        user_current_page[user_id] = 0

        # Показываем первую страницу матчей
        show_matches_page(message.chat.id, player_info, 0, is_my_matches=True)

        logging.info(f"Пользователь {user_id} запросил свои матчи")

    except Exception as e:
        logging.error(f"Ошибка в show_my_matches: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при загрузке ваших матчей")


def show_matches_page(chat_id, player_info, page=0, is_my_matches=False, edit_message_id=None):
    """Показывает страницу с матчами"""
    try:
        user_data = user_matches.get(chat_id)
        if not user_data:
            return

        matches = user_data['matches']
        matches_per_page = 5
        start_idx = page * matches_per_page
        end_idx = start_idx + matches_per_page
        page_matches = matches[start_idx:end_idx]

        # Статистика страницы
        total_matches = len(matches)
        total_pages = (total_matches + matches_per_page - 1) // matches_per_page
        current_page = page + 1

        # Проверяем возможность навигации
        has_prev_page = page > 0
        has_next_page = end_idx < total_matches

        # Заголовок в зависимости от типа
        if is_my_matches:
            matches_text = f"👤 *Мои матчи*\n"
        else:
            matches_text = f"🎮 *Матчи игрока: {player_info['name']}*\n"

        matches_text += f"📊 {player_info['mmr']} MMR | 🏆 Винрейт: {player_info['win_rate']}%\n"
        matches_text += f"📄 Страница {current_page}/{total_pages} | Всего матчей: {total_matches}\n\n"

        if not page_matches:
            matches_text += "❌ Матчи не найдены\n"
        else:
            for match in page_matches:
                # Эмодзи для результата
                result_emoji = "✅" if "Победа" in match['result'] else "❌"

                matches_text += f"{result_emoji} *Матч #{match['match_num']}* ({match['date']})\n"
                matches_text += f"🎯 {match['hero']} | {match['result']}\n"
                matches_text += f"⏱️ {match['duration']} | ⚔️ {match['kda']} KDA\n"
                matches_text += f"💰 {match['gpm']} GPM | 📈 {match['xpm']} XPM\n"
                matches_text += f"🔥 {match['hero_damage']:,} урона | 🏰 {match['tower_damage']:,} урона по башням\n"

                # Случайные предметы (показываем 3)
                items_display = ", ".join(match['items'][:3])
                matches_text += f"🎒 {items_display}\n"
                matches_text += "─" * 30 + "\n\n"

        if is_my_matches:
            matches_text += "💡 *Это ваша личная история матчей*"
        else:
            matches_text += "💡 *Используйте кнопки ниже для навигации*"

        # Отправляем или редактируем сообщение
        markup = create_matches_keyboard(
            has_prev=has_prev_page,
            has_next=has_next_page,
            is_my_matches=is_my_matches
        )

        if edit_message_id:
            # Редактируем существующее сообщение
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=edit_message_id,
                text=matches_text,
                reply_markup=markup,
                parse_mode='Markdown'
            )
        else:
            # Отправляем новое сообщение
            msg = bot.send_message(chat_id, matches_text, reply_markup=markup, parse_mode='Markdown')
            last_message_ids[chat_id] = msg.message_id

        # Обновляем текущую страницу
        user_current_page[chat_id] = page
        user_matches[chat_id]['is_my_matches'] = is_my_matches

        logging.info(f"Пользователь {chat_id} просматривает страницу {current_page} матчей")

    except Exception as e:
        logging.error(f"Ошибка в show_matches_page: {e}")
        bot.send_message(chat_id, "❌ Ошибка при отображении матчей")


@bot.callback_query_handler(func=lambda call: call.data.startswith(('matches_', 'my_matches_')))
def handle_matches_callback(call):
    """Обрабатывает callback'и для навигации по матчам"""
    try:
        user_id = call.message.chat.id
        user_data = user_matches.get(user_id)

        if not user_data:
            bot.answer_callback_query(call.id, "❌ Данные матчей устарели")
            return

        player_info = user_data['player']
        current_page = user_current_page.get(user_id, 0)
        is_my_matches = user_data.get('is_my_matches', False)

        if call.data == "matches_next" or call.data == "my_matches_next":
            # Следующая страница
            next_page = current_page + 1
            show_matches_page(
                user_id,
                player_info,
                next_page,
                is_my_matches,
                edit_message_id=call.message.message_id
            )
            bot.answer_callback_query(call.id, f"📄 Страница {next_page + 1}")

        elif call.data == "matches_prev" or call.data == "my_matches_prev":
            # Предыдущая страница
            prev_page = current_page - 1
            if prev_page >= 0:
                show_matches_page(
                    user_id,
                    player_info,
                    prev_page,
                    is_my_matches,
                    edit_message_id=call.message.message_id
                )
                bot.answer_callback_query(call.id, f"📄 Страница {prev_page + 1}")
            else:
                bot.answer_callback_query(call.id, "❌ Это первая страница")

        elif call.data == "matches_new":
            # Новые матчи (регенерация)
            user_data['matches'] = demo_gen.generate_matches_batch(player_info['name'], 30)
            user_current_page[user_id] = 0
            show_matches_page(
                user_id,
                player_info,
                0,
                is_my_matches=False,
                edit_message_id=call.message.message_id
            )
            bot.answer_callback_query(call.id, "🔄 Матчи обновлены!")

        elif call.data == "my_matches_refresh":
            # Обновление моих матчей
            user_data['matches'] = demo_gen.generate_matches_batch(player_info['name'], 30)
            user_current_page[user_id] = 0
            show_matches_page(
                user_id,
                player_info,
                0,
                is_my_matches=True,
                edit_message_id=call.message.message_id
            )
            bot.answer_callback_query(call.id, "🔄 Ваши матчи обновлены!")

        elif call.data == "matches_back":
            # Возврат в главное меню
            markup = create_main_menu()
            bot.send_message(user_id, "↩️ Возвращаемся в главное меню...", reply_markup=markup)
            bot.answer_callback_query(call.id, "Возврат в меню")

    except Exception as e:
        logging.error(f"Ошибка в handle_matches_callback: {e}")
        bot.answer_callback_query(call.id, "❌ Произошла ошибка")


@bot.message_handler(func=lambda message: message.text == "🎮 Матчи игрока")
def show_player_matches_menu(message):
    """Показывает меню выбора игрока для просмотра матчей"""
    try:
        user_states[message.chat.id] = "waiting_player_for_matches"

        # Создаем клавиатуру с игроками
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons = []

        # Выбираем 4 случайных игрока для кнопок
        random_players = random.sample(DEMO_PLAYERS, 4)
        for player in random_players:
            buttons.append(types.KeyboardButton(f"🎮 {player['name']}"))

        buttons.append(types.KeyboardButton("🎲 Случайный игрок"))
        buttons.append(types.KeyboardButton("❌ Отмена"))

        # Разделяем кнопки на ряды
        for i in range(0, len(buttons), 2):
            markup.add(*buttons[i:i + 2])

        help_text = """
🎮 *Просмотр матчей игрока*

*Выберите игрока из списка или:*
• Введите имя игрока
• Нажмите 'Случайный игрок'

*Доступные игроки:*
"""
        # Добавляем примеры
        for player in random_players[:3]:
            help_text += f"• {player['name']} ({player['mmr']} MMR)\n"

        help_text += "\n💡 Будут показаны последние 15 матчей с возможностью листать вперед и назад"

        bot.send_message(message.chat.id, help_text, reply_markup=markup, parse_mode='Markdown')
        logging.info(f"Пользователь {message.chat.id} запросил меню матчей игрока")

    except Exception as e:
        logging.error(f"Ошибка в show_player_matches_menu: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при загрузке меню матчей")


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "waiting_player_for_matches")
def handle_player_matches_request(message):
    """Обрабатывает запрос на просмотр матчей игрока"""
    try:
        user_input = message.text.strip()

        # Обработка кнопки отмена
        if user_input == "❌ Отмена":
            user_states[message.chat.id] = None
            send_welcome(message)
            return

        # Определяем игрока
        player_info = None

        if user_input == "🎲 Случайный игрок":
            player_info = random.choice(DEMO_PLAYERS)
        elif user_input.startswith("🎮 "):
            player_name = user_input[2:]
            for player in DEMO_PLAYERS:
                if player['name'] == player_name:
                    player_info = player
                    break
        else:
            # Поиск по имени
            for player in DEMO_PLAYERS:
                if player['name'].lower() == user_input.lower():
                    player_info = player
                    break

        if not player_info:
            # Если игрок не найден, создаем случайного
            player_info = random.choice(DEMO_PLAYERS)

        # Генерируем матчи для этого игрока
        user_id = message.chat.id
        user_matches[user_id] = {
            'player': player_info,
            'matches': demo_gen.generate_matches_batch(player_info['name'], 30),
            'current_page': 0,
            'is_my_matches': False
        }
        user_current_page[user_id] = 0

        # Показываем первую страницу матчей
        show_matches_page(message.chat.id, player_info, 0, is_my_matches=False)

        # Сбрасываем состояние
        user_states[message.chat.id] = None

    except Exception as e:
        logging.error(f"Ошибка в handle_player_matches_request: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при загрузке матчей игрока")
        user_states[message.chat.id] = None


@bot.message_handler(func=lambda message: message.text == "📈 Моя статистика")
def show_my_stats(message):
    """Показывает личную статистику пользователя по героям"""
    try:
        user_id = message.chat.id

        # Проверяем есть ли статистика у пользователя
        if user_id not in user_hero_stats or not user_hero_stats[user_id]:
            bot.send_message(message.chat.id, "❌ Статистика не найдена. Сначала сыграйте несколько матчей!")
            return

        player_info = user_profiles[user_id]
        stats = user_hero_stats[user_id]

        stats_text = f"📈 *Моя статистика по героям*\n\n"
        stats_text += f"👤 *{player_info['name']}*\n"
        stats_text += f"📊 MMR: {player_info['mmr']} | 🏆 Общий винрейт: {player_info['win_rate']}%\n\n"

        # Показываем статистику по всем героям
        for hero_id, hero_stats in stats.items():
            hero = DEMO_HEROES.get(hero_id)
            if hero:
                stats_text += f"🎯 *{hero['name']}*\n"
                stats_text += f"📊 Матчи: {hero_stats['matches']} "
                stats_text += f"({hero_stats['wins']}🏆/{hero_stats['losses']}💀) "
                stats_text += f"- {hero_stats['win_rate']}%\n"
                stats_text += f"⚔️ KDA: {hero_stats['kda']} "
                stats_text += f"({hero_stats['avg_kills']}/{hero_stats['avg_deaths']}/{hero_stats['avg_assists']})\n"
                stats_text += f"💰 GPM: {hero_stats['avg_gpm']} | 📈 XPM: {hero_stats['avg_xpm']}\n"
                stats_text += f"🎮 Роль: {hero_stats['favorite_role']} | 📅 Последняя игра: {hero_stats['last_played']}\n"
                stats_text += f"📊 Результативность: {hero_stats['performance']}\n"
                stats_text += "─" * 30 + "\n\n"

        stats_text += "💡 *Для детальной статистики по конкретному герою используйте '🔍 Инфо о герое'*"

        bot.send_message(message.chat.id, stats_text, parse_mode='Markdown')
        logging.info(f"Пользователь {user_id} запросил свою статистику")

    except Exception as e:
        logging.error(f"Ошибка в show_my_stats: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при загрузке статистики")


@bot.message_handler(func=lambda message: message.text == "📊 Герои")
def get_heroes(message):
    """Показывает список героев со статистикой"""
    try:
        # Берем всех героев
        heroes_text = "🎯 *Все герои Dota 2*\n\n"

        for hero_id in sorted(DEMO_HEROES.keys()):
            hero = DEMO_HEROES[hero_id]
            hero_stats = hero['hero_stats']

            heroes_text += f"• *{hero_id}.* {hero['name']}\n"
            heroes_text += f"  📊 {hero['attribute']} | 🎯 {', '.join(hero['roles'][:2])}\n"
            heroes_text += f"  📈 Пик-рейт: {hero_stats['pick_rate']}% | 🏆 Винрейт: {hero_stats['win_rate']}%\n"
            heroes_text += f"  ⚔️ KDA: {hero_stats['kda']} | 👥 Матчи: {hero_stats['matches_played']:,}\n\n"

        heroes_text += "💡 *Для детальной информации используйте '🔍 Инфо о герое'*"

        bot.send_message(message.chat.id, heroes_text, parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Ошибка в get_heroes: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при получении списка героев")


@bot.message_handler(func=lambda message: message.text == "🔍 Инфо о герое")
def ask_hero_info(message):
    """Запрашивает ID героя"""
    try:
        user_id = message.chat.id
        user_states[user_id] = "waiting_hero_id"

        # Создаем клавиатуру со случайными героями
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        buttons = []

        # Выбираем 6 случайных героев для кнопок
        random_heroes = random.sample(list(DEMO_HEROES.values()), 6)
        for hero in random_heroes:
            buttons.append(types.KeyboardButton(f"{hero['id']} - {hero['name']}"))

        buttons.append(types.KeyboardButton("🎲 Случайный герой"))
        buttons.append(types.KeyboardButton("📊 Моя стата"))
        buttons.append(types.KeyboardButton("❌ Отмена"))

        # Разделяем кнопки на ряды
        for i in range(0, len(buttons), 3):
            markup.add(*buttons[i:i + 3])

        help_text = f"""
🎯 *Выберите героя:*

*Доступные ID:* 1-{len(DEMO_HEROES)}
Или введите любой номер от 1 до {len(DEMO_HEROES)}

*Примеры героев со статистикой:*
"""
        # Добавляем примеры
        for hero in random_heroes[:3]:
            stats = hero['hero_stats']
            help_text += f"• {hero['id']} - {hero['name']} (🏆 {stats['win_rate']}% | 📈 {stats['pick_rate']}%)\n"

        help_text += "\n🎲 Нажмите 'Случайный герой' для автоматического выбора"
        help_text += "\n📊 Нажмите 'Моя стата' для просмотра вашей статистики по всем героям"

        bot.send_message(message.chat.id, help_text, reply_markup=markup, parse_mode='Markdown')
        logging.info(f"Пользователь {message.chat.id} запросил информацию о герое")

    except Exception as e:
        logging.error(f"Ошибка в ask_hero_info: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при запросе информации о герое")
        user_states[message.chat.id] = None


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "waiting_hero_id")
def handle_hero_info(message):
    """Обрабатывает запрос информации о герое"""
    try:
        user_input = message.text.strip()
        user_id = message.chat.id

        # Обработка кнопки отмены
        if user_input == "❌ Отмена":
            user_states[user_id] = None
            send_welcome(message)
            return

        # Обработка кнопки "Моя стата"
        if user_input == "📊 Моя стата":
            user_states[user_id] = None
            show_my_stats(message)
            return

        # Обработка случайного героя
        if user_input == "🎲 Случайный герой":
            hero_id = random.randint(1, len(DEMO_HEROES))
        else:
            # Извлекаем ID из текста (если формат "1 - Dragon Knight")
            if " - " in user_input:
                hero_id_str = user_input.split(" - ")[0]
            else:
                hero_id_str = user_input

            # Проверяем, что введено число
            if not hero_id_str.isdigit():
                bot.send_message(message.chat.id, "❌ Пожалуйста, введите число (ID героя)")
                return

            hero_id = int(hero_id_str)

        # Проверяем, что герой существует
        if hero_id not in DEMO_HEROES:
            bot.send_message(message.chat.id,
                             f"❌ Герой с ID {hero_id} не найден. Попробуйте ID от 1 до {len(DEMO_HEROES)}.")
            return

        # Создаем клавиатуру для выбора типа информации
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton(f"📊 Моя стата по герою {hero_id}")
        btn2 = types.KeyboardButton("📈 Общая статистика")
        btn3 = types.KeyboardButton("↩️ Назад к героям")
        markup.add(btn1, btn2, btn3)

        hero_info = DEMO_HEROES[hero_id]
        choice_text = f"""
🎯 *{hero_info['name']}*

Выберите тип информации:
• *📊 Моя стата* - ваша личная статистика по этому герою
• *📈 Общая статистика* - общая информация о герое

Или нажмите кнопку ниже:
        """

        user_states[user_id] = f"waiting_hero_info_type_{hero_id}"
        bot.send_message(message.chat.id, choice_text, reply_markup=markup, parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Ошибка в handle_hero_info: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при получении информации о герое")
        user_states[message.chat.id] = None


@bot.message_handler(func=lambda message: user_states.get(message.chat.id, "").startswith("waiting_hero_info_type_"))
def handle_hero_info_type(message):
    """Обрабатывает выбор типа информации о герое"""
    try:
        user_id = message.chat.id
        user_state = user_states.get(user_id, "")

        # Проверяем что состояние корректно
        if not user_state or not user_state.startswith("waiting_hero_info_type_"):
            bot.send_message(user_id, "❌ Сессия устарела. Начните заново.")
            user_states[user_id] = None
            return

        # Извлекаем ID героя
        try:
            hero_id = int(user_state.split("_")[-1])
        except (ValueError, IndexError):
            bot.send_message(user_id, "❌ Ошибка в данных героя. Начните заново.")
            user_states[user_id] = None
            return

        user_input = message.text.strip()

        if user_input == "↩️ Назад к героям":
            user_states[user_id] = None
            ask_hero_info(message)
            return

        # Проверяем что герой существует
        if hero_id not in DEMO_HEROES:
            bot.send_message(user_id, f"❌ Герой с ID {hero_id} не найден.")
            user_states[user_id] = None
            return

        hero_info = DEMO_HEROES[hero_id]

        if "Моя стата" in user_input:
            # Показываем личную статистику по герою
            show_personal_hero_stats(message, hero_id, hero_info)
        elif user_input == "📈 Общая статистика":
            # Показываем общую информацию о герое
            show_general_hero_info(message, hero_id, hero_info)
        else:
            bot.send_message(message.chat.id, "❌ Пожалуйста, выберите тип информации из предложенных вариантов")

    except Exception as e:
        logging.error(f"Ошибка в handle_hero_info_type: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при обработке запроса")
        user_states[message.chat.id] = None


def show_personal_hero_stats(message, hero_id, hero_info):
    """Показывает личную статистику пользователя по конкретному герою"""
    try:
        user_id = message.chat.id

        # Проверяем есть ли профиль пользователя
        if user_id not in user_profiles:
            bot.send_message(user_id, "❌ Профиль не найден. Нажмите /start для создания профиля.")
            user_states[user_id] = None
            return

        # Получаем или генерируем статистику по герою
        if user_id not in user_hero_stats:
            user_hero_stats[user_id] = {}

        if hero_id not in user_hero_stats[user_id]:
            user_hero_stats[user_id][hero_id] = demo_gen.generate_player_hero_stats(
                user_profiles[user_id]['name'], hero_id, hero_info['name']
            )

        hero_stats = user_hero_stats[user_id][hero_id]
        player_info = user_profiles[user_id]

        # Создаем детальную статистику
        stats_text = f"📊 *Моя статистика по {hero_info['name']}*\n\n"
        stats_text += f"👤 Игрок: *{player_info['name']}*\n"
        stats_text += f"📊 MMR: {player_info['mmr']} | 🎯 Герой: {hero_info['name']}\n\n"

        # Основная статистика
        stats_text += "*📈 Основная статистика:*\n"
        stats_text += f"• 🎮 Матчей сыграно: {hero_stats['matches']}\n"
        stats_text += f"• 🏆 Побед: {hero_stats['wins']} | 💀 Поражений: {hero_stats['losses']}\n"
        stats_text += f"• 📊 Винрейт: {hero_stats['win_rate']}%\n"
        stats_text += f"• ⚔️ KDA: {hero_stats['kda']}\n"
        stats_text += f"• 🔥 Убийств в среднем: {hero_stats['avg_kills']}\n"
        stats_text += f"• 💀 Смертей в среднем: {hero_stats['avg_deaths']}\n"
        stats_text += f"• 🤝 Помощи в среднем: {hero_stats['avg_assists']}\n\n"

        # Экономика
        stats_text += "*💰 Экономика:*\n"
        stats_text += f"• 🎯 GPM в среднем: {hero_stats['avg_gpm']}\n"
        stats_text += f"• 📈 XPM в среднем: {hero_stats['avg_xpm']}\n\n"

        # Дополнительная информация
        stats_text += "*🎮 Дополнительно:*\n"
        stats_text += f"• 🎯 Предпочитаемая роль: {hero_stats['favorite_role']}\n"
        stats_text += f"• 📅 Последняя игра: {hero_stats['last_played']}\n"
        stats_text += f"• 🏆 Лучшая серия побед: {hero_stats['best_streak']}\n"
        stats_text += f"• 📊 Результативность: {hero_stats['performance']}\n\n"

        # Сравнение с общей статистикой
        global_stats = hero_info['hero_stats']
        stats_text += "*🌐 Сравнение с общей статистикой:*\n"
        stats_text += f"• 📊 Ваш винрейт: {hero_stats['win_rate']}% vs Общий: {global_stats['win_rate']}%\n"
        stats_text += f"• ⚔️ Ваш KDA: {hero_stats['kda']} vs Общий: {global_stats['kda']}\n"

        win_rate_diff = hero_stats['win_rate'] - global_stats['win_rate']
        if win_rate_diff > 0:
            stats_text += f"• ✅ Вы играете лучше среднего на {abs(win_rate_diff):.1f}%\n"
        else:
            stats_text += f"• 📉 Вы играете хуже среднего на {abs(win_rate_diff):.1f}%\n"

        stats_text += "\n🎲 *Сгенерировано случайно*"

        # Возвращаем основное меню
        markup = create_main_menu()
        bot.send_message(message.chat.id, stats_text, reply_markup=markup, parse_mode='Markdown')

        # Сбрасываем состояние пользователя
        user_states[user_id] = None
        logging.info(f"Пользователь {user_id} получил личную статистику по герою {hero_id}")

    except Exception as e:
        logging.error(f"Ошибка в show_personal_hero_stats: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при получении личной статистики")
        user_states[message.chat.id] = None


def show_general_hero_info(message, hero_id, hero_info):
    """Показывает общую информацию о герое"""
    try:
        hero_stats = hero_info['hero_stats']

        # Создаем детальное описание
        hero_text = f"🎯 *{hero_info['name']}*\n\n"
        hero_text += f"*ID:* {hero_info['id']}\n"
        hero_text += f"*Основной атрибут:* {hero_info['attribute']}\n"
        hero_text += f"*Роли:* {', '.join(hero_info['roles'])}\n\n"

        # Статистика героя
        hero_text += "*📊 Общая статистика героя:*\n"
        hero_text += f"• 📈 Пик-рейт: {hero_stats['pick_rate']}%\n"
        hero_text += f"• 🏆 Винрейт: {hero_stats['win_rate']}%\n"
        hero_text += f"• ⚔️ KDA: {hero_stats['kda']}\n"
        hero_text += f"• 👥 Матчей сыграно: {hero_stats['matches_played']:,}\n"
        hero_text += f"• 🎯 Фарм: {hero_stats['farm']} GPM\n\n"

        # Характеристики
        stats = hero_info['stats']
        hero_text += "*❤️ Характеристики:*\n"
        hero_text += f"• ❤️ Здоровье: {stats['health']}\n"
        hero_text += f"• 🔮 Мана: {stats['mana']}\n"
        hero_text += f"• ⚔️ Урон: {stats['damage']}\n"
        hero_text += f"• 🛡️ Броня: {stats['armor']}\n"
        hero_text += f"• 🏃 Скорость: {stats['move_speed']}\n"
        hero_text += f"• 🎯 Дальность: {stats['attack_range']}\n\n"

        # Способности
        hero_text += "*🔮 Способности:*\n"
        for ability in hero_info['abilities']:
            hero_text += f"• {ability}\n"

        hero_text += f"\n*📖 Лор:*\n{hero_info['lore']}\n\n"
        hero_text += "🎲 *Сгенерировано случайно*"

        # Возвращаем основное меню
        markup = create_main_menu()
        bot.send_message(message.chat.id, hero_text, reply_markup=markup, parse_mode='Markdown')

        # Сбрасываем состояние пользователя
        user_states[message.chat.id] = None
        logging.info(f"Пользователь {message.chat.id} получил общую информацию о герое {hero_id}")

    except Exception as e:
        logging.error(f"Ошибка в show_general_hero_info: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при получении информации о герое")
        user_states[message.chat.id] = None


@bot.message_handler(func=lambda message: message.text == "🔄 Обновить данные")
def refresh_data(message):
    """Обновляет все демо-данные"""
    try:
        global DEMO_HEROES, DEMO_PLAYERS

        DEMO_HEROES = {i: demo_gen.generate_hero(i) for i in range(1, 21)}
        DEMO_PLAYERS = [demo_gen.generate_player() for _ in range(10)]

        # Также обновляем профиль пользователя и статистику
        user_id = message.chat.id
        if user_id in user_profiles:
            user_name = user_profiles[user_id]['name']
            user_profiles[user_id] = demo_gen.generate_player(user_name)

            # Обновляем статистику по героям
            user_hero_stats[user_id] = {}
            for hero_id in range(1, 6):
                hero = DEMO_HEROES[hero_id]
                user_hero_stats[user_id][hero_id] = demo_gen.generate_player_hero_stats(
                    user_profiles[user_id]['name'], hero_id, hero['name']
                )

        refresh_text = "🔄 *Данные успешно обновлены!*\n\n"
        refresh_text += "• Обновлены герои и игроки\n"
        refresh_text += "• Сброшена ваша статистика\n"
        refresh_text += "• Сгенерированы новые матчи\n\n"
        refresh_text += "🎲 *Все данные полностью случайны*"

        bot.send_message(message.chat.id, refresh_text, parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Ошибка в refresh_data: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при обновлении данных")


@bot.message_handler(func=lambda message: message.text == "ℹ️ Помощь")
def show_help(message):
    """Показывает справку"""
    help_text = """
🎮 *Dota 2 Stats Bot - Случайные демо-данные*

*📈 Новое - Личная статистика:*
• Ваша статистика по каждому герою
• Сравнение с общей статистикой
• KDA, винрейт, экономика
• Предпочитаемые роли и результативность

*👤 Мои матчи:*
• Персональная история матчей
• Ваш уникальный профиль
• Обновление ваших матчей

*🔄 Улучшенная навигация:*
• Листание вперед и назад по матчам
• Замена сообщений вместо новых
• Удобные кнопки навигации

*📋 Доступные функции:*
• 👤 Мои матчи - Ваша личная история матчей
• 📊 Герои - Список героев со статистикой
• 🔍 Инфо о герое - Детали любого героя
• 📈 Моя статистика - Личная статистика по героям
• 🎮 Матчи игрока - Матчи других игроков
• 🔄 Обновить данные - Новые случайные данные

💡 *Теперь вы можете отслеживать свою статистику по каждому герою!*
    """
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')


@bot.message_handler(func=lambda message: True)
def handle_unknown(message):
    """Обрабатывает неизвестные команды"""
    if message.chat.id not in user_states or user_states[message.chat.id] is None:
        bot.send_message(message.chat.id,
                         "🤔 Не понял вашу команду.\n\n"
                         "Используйте кнопки меню ниже или нажмите /start для начала работы.",
                         reply_markup=create_main_menu())


if __name__ == "__main__":
    print("=" * 50)
    print("🎮 Dota 2 Stats Bot запущен!")
    print("📈 Добавлена личная статистика по героям")
    print("👤 Кнопка 'Моя статистика' в главном меню")
    print("🔄 Листание вперед и назад по матчам")
    print("📱 Ожидаю сообщения от пользователей...")
    print("=" * 50)

    try:
        bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")
        print("🔄 Попытка перезапуска...")