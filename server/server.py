# ==================== server.py ====================
import json
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time
import logging
import os
from dotenv import load_dotenv

# ==================== ЗАГРУЗКА ПЕРЕМЕННЫХ ====================
load_dotenv()


SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.getenv('SERVER_PORT', '8000'))
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ==================== МОДЕЛИ ДАННЫХ ====================
class Database:
    """Имитация базы данных"""

    def __init__(self):
        self.players = {}
        self.matches = {}
        self.heroes = {}
        self._init_data()

    def _init_data(self):
        # Герои
        heroes_list = [
            {"id": 1, "name": "Anti-Mage", "attribute": "Agility"},
            {"id": 2, "name": "Axe", "attribute": "Strength"},
            {"id": 3, "name": "Bane", "attribute": "Intelligence"},
            {"id": 4, "name": "Bloodseeker", "attribute": "Agility"},
            {"id": 5, "name": "Crystal Maiden", "attribute": "Intelligence"},
            {"id": 6, "name": "Drow Ranger", "attribute": "Agility"},
            {"id": 7, "name": "Earthshaker", "attribute": "Strength"},
            {"id": 8, "name": "Juggernaut", "attribute": "Agility"},
            {"id": 9, "name": "Mirana", "attribute": "Agility"},
            {"id": 10, "name": "Morphling", "attribute": "Agility"},
            {"id": 11, "name": "Shadow Fiend", "attribute": "Agility"},
            {"id": 12, "name": "Phantom Lancer", "attribute": "Agility"},
            {"id": 13, "name": "Puck", "attribute": "Intelligence"},
            {"id": 14, "name": "Pudge", "attribute": "Strength"},
            {"id": 15, "name": "Razor", "attribute": "Agility"},
            {"id": 16, "name": "Sand King", "attribute": "Strength"},
            {"id": 17, "name": "Storm Spirit", "attribute": "Intelligence"},
            {"id": 18, "name": "Sven", "attribute": "Strength"},
            {"id": 19, "name": "Tiny", "attribute": "Strength"},
            {"id": 20, "name": "Vengeful Spirit", "attribute": "Agility"}
        ]

        for hero in heroes_list:
            self.heroes[hero["id"]] = {
                **hero,
                "hero_stats": {
                    "win_rate": random.randint(45, 55),
                    "pick_rate": random.randint(1, 30),
                    "avg_kills": random.uniform(5.0, 12.0),
                    "avg_deaths": random.uniform(3.0, 8.0),
                    "avg_assists": random.uniform(8.0, 15.0)
                }
            }

        # Демо игроки
        demo_players = ["Alex", "Ben", "Charlie", "Diana", "Ethan", "Fiona", "George", "Helen"]
        for i, name in enumerate(demo_players, 1):
            player_id = f"demo_{i}"
            mmr = random.randint(1000, 6000)
            games = random.randint(50, 500)
            wins = random.randint(games // 3, games // 2)

            self.players[player_id] = {
                "id": player_id,
                "name": name,
                "mmr": mmr,
                "games": games,
                "wins": wins,
                "losses": games - wins,
                "win_rate": round((wins / games) * 100, 1) if games > 0 else 0,
                "avg_kills": random.uniform(3.0, 10.0),
                "avg_deaths": random.uniform(4.0, 8.0),
                "avg_assists": random.uniform(6.0, 12.0),
                "created_at": time.time()
            }

            # Создаем демо матчи для игрока
            player_matches = []
            for match_num in range(1, random.randint(20, 50)):
                hero = random.choice(list(self.heroes.values()))
                result = random.choice(["Победа", "Поражение"])
                duration_min = random.randint(20, 60)
                gpm = random.randint(300, 800)
                xpm = random.randint(400, 900)

                player_matches.append({
                    "match_id": f"{player_id}_match_{match_num}",
                    "player_id": player_id,
                    "match_num": match_num,
                    "hero": hero["name"],
                    "result": result,
                    "duration": f"{duration_min}:{random.randint(0, 59):02d}",
                    "kda": f"{random.randint(2, 15)}/{random.randint(2, 10)}/{random.randint(5, 25)}",
                    "gpm": gpm,
                    "xpm": xpm,
                    "hero_damage": random.randint(10000, 50000),
                    "tower_damage": random.randint(1000, 10000),
                    "timestamp": time.time() - random.randint(0, 2592000)  # До 30 дней назад
                })

            self.matches[player_id] = player_matches

    def get_or_create_player(self, user_id, user_name):
        """Получить или создать игрока"""
        if user_id not in self.players:
            mmr = random.randint(1000, 4000)
            self.players[user_id] = {
                "id": user_id,
                "name": user_name,
                "mmr": mmr,
                "games": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0,
                "avg_kills": 0.0,
                "avg_deaths": 0.0,
                "avg_assists": 0.0,
                "created_at": time.time()
            }

        return self.players[user_id]

    def get_player_by_name(self, player_name):
        """Найти игрока по имени"""
        player_name_lower = player_name.lower()
        for player in self.players.values():
            if player["name"].lower() == player_name_lower:
                return player

        # Если не найден, создаем демо
        player_id = f"demo_{int(time.time())}"
        mmr = random.randint(1000, 6000)
        games = random.randint(50, 200)
        wins = random.randint(games // 3, games // 2)

        player_data = {
            "id": player_id,
            "name": player_name,
            "mmr": mmr,
            "games": games,
            "wins": wins,
            "losses": games - wins,
            "win_rate": round((wins / games) * 100, 1) if games > 0 else 0,
            "avg_kills": random.uniform(3.0, 10.0),
            "avg_deaths": random.uniform(4.0, 8.0),
            "avg_assists": random.uniform(6.0, 12.0),
            "created_at": time.time()
        }

        self.players[player_id] = player_data
        return player_data

    def get_player_matches(self, player_id, player_name=None, is_my_matches=False, page=0, per_page=5):
        """Получить матчи игрока с пагинацией"""
        if is_my_matches:
            # Для текущего пользователя
            player_data = self.get_or_create_player(player_id, "Player")
            matches = self.matches.get(player_id, [])
            player_info = player_data
        else:
            # Для другого игрока
            if not player_name:
                return None

            player_info = self.get_player_by_name(player_name)
            matches = self.matches.get(player_info["id"], [])

        # Сортируем по времени (новые первые)
        matches_sorted = sorted(matches, key=lambda x: x["timestamp"], reverse=True)

        # Пагинация
        total_matches = len(matches_sorted)
        total_pages = (total_matches + per_page - 1) // per_page

        start_idx = page * per_page
        end_idx = start_idx + per_page
        page_matches = matches_sorted[start_idx:end_idx]

        return {
            "player": player_info,
            "matches": page_matches,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_matches": total_matches,
                "total_pages": total_pages,
                "has_prev": page > 0,
                "has_next": (page + 1) < total_pages
            }
        }

    def add_match_for_player(self, player_id, match_data):
        """Добавить матч для игрока"""
        if player_id not in self.matches:
            self.matches[player_id] = []

        match_num = len(self.matches[player_id]) + 1
        new_match = {
            "match_id": f"{player_id}_match_{match_num}",
            "player_id": player_id,
            "match_num": match_num,
            "timestamp": time.time(),
            **match_data
        }

        self.matches[player_id].append(new_match)

        # Обновляем статистику игрока
        player = self.players.get(player_id)
        if player:
            player["games"] += 1
            if new_match["result"] == "Победа":
                player["wins"] += 1
            else:
                player["losses"] += 1

            if player["games"] > 0:
                player["win_rate"] = round((player["wins"] / player["games"]) * 100, 1)

        return new_match


# Глобальная база данных
db = Database()


# ==================== HTTP ОБРАБОТЧИК ====================
class APIHandler(BaseHTTPRequestHandler):
    """Обработчик HTTP запросов"""

    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        """Обработка preflight запросов"""
        self._set_headers(200)

    def do_GET(self):
        """Обработка GET запросов"""
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        try:
            if path == '/':
                response = {"status": "API is running", "version": "1.0.0"}

            elif path == '/heroes':
                heroes_list = list(db.heroes.values())
                response = {"success": True, "heroes": heroes_list}

            elif path == '/players':
                players_list = list(db.players.values())
                response = {"success": True, "players": players_list}

            elif path.startswith('/matches/'):
                # /matches/{user_id}/{page}
                parts = path.split('/')
                if len(parts) >= 4:
                    user_id = parts[2]
                    page = int(parts[3])

                    player_name = query.get('player_name', [None])[0]
                    is_my_matches = query.get('is_my_matches', ['false'])[0].lower() == 'true'

                    matches_data = db.get_player_matches(
                        user_id,
                        player_name,
                        is_my_matches,
                        page
                    )

                    if matches_data:
                        response = {"success": True, **matches_data}
                    else:
                        response = {"success": False, "error": "Matches not found"}
                else:
                    response = {"success": False, "error": "Invalid endpoint"}

            elif path.startswith('/hero/'):
                # /hero/{hero_id}
                parts = path.split('/')
                if len(parts) >= 3:
                    hero_id = int(parts[2])
                    hero = db.heroes.get(hero_id)
                    if hero:
                        response = {"success": True, "hero": hero}
                    else:
                        response = {"success": False, "error": "Hero not found"}
                else:
                    response = {"success": False, "error": "Invalid endpoint"}

            elif path.startswith('/stats/'):
                # /stats/{user_id}
                parts = path.split('/')
                if len(parts) >= 3:
                    user_id = parts[2]
                    player = db.players.get(user_id)
                    if player:
                        response = {"success": True, "stats": player}
                    else:
                        response = {"success": False, "error": "Player not found"}
                else:
                    response = {"success": False, "error": "Invalid endpoint"}

            else:
                response = {"success": False, "error": "Endpoint not found"}

            self._set_headers(200)
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

        except Exception as e:
            logging.error(f"GET Error: {e}")
            self._set_headers(500)
            response = {"success": False, "error": str(e)}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def do_POST(self):
        """Обработка POST запросов"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b'{}'

        try:
            data = json.loads(post_data.decode('utf-8'))
            path = self.path

            if path == '/player/create':
                user_id = data.get('user_id', '')
                user_name = data.get('user_name', 'Player')

                player = db.get_or_create_player(user_id, user_name)
                response = {"success": True, "player": player}

            elif path == '/matches':
                user_id = data.get('user_id', '')
                is_my_matches = data.get('is_my_matches', False)
                player_name = data.get('player_name')

                matches_data = db.get_player_matches(
                    user_id,
                    player_name,
                    is_my_matches,
                    0  # Первая страница
                )

                if matches_data:
                    response = {"success": True, **matches_data}
                else:
                    response = {"success": False, "error": "Matches not found"}

            elif path == '/match/add':
                user_id = data.get('user_id', '')

                # Генерируем случайный матч
                hero = random.choice(list(db.heroes.values()))
                match_data = {
                    "hero": hero["name"],
                    "result": random.choice(["Победа", "Поражение"]),
                    "duration": f"{random.randint(20, 60)}:{random.randint(0, 59):02d}",
                    "kda": f"{random.randint(2, 15)}/{random.randint(2, 10)}/{random.randint(5, 25)}",
                    "gpm": random.randint(300, 800),
                    "xpm": random.randint(400, 900),
                    "hero_damage": random.randint(10000, 50000),
                    "tower_damage": random.randint(1000, 10000)
                }

                new_match = db.add_match_for_player(user_id, match_data)
                response = {"success": True, "match": new_match}

            elif path == '/hero/info':
                hero_id = data.get('hero_id')
                hero = db.heroes.get(hero_id)
                if hero:
                    response = {"success": True, "hero": hero}
                else:
                    response = {"success": False, "error": "Hero not found"}

            else:
                response = {"success": False, "error": "Endpoint not found"}

            self._set_headers(200)
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

        except json.JSONDecodeError:
            self._set_headers(400)
            response = {"success": False, "error": "Invalid JSON"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            logging.error(f"POST Error: {e}")
            self._set_headers(500)
            response = {"success": False, "error": str(e)}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def log_message(self, format, *args):
        """Кастомное логирование запросов"""
        logging.info(f"{self.address_string()} - {format % args}")


# ==================== ЗАПУСК СЕРВЕРА ====================
def run_server(port=SERVER_PORT):  # ← ИСПОЛЬЗУЕМ ПЕРЕМЕННУЮ
    """Запуск HTTP сервера"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, APIHandler)

    print("=" * 50)
    print(f"🚀 Сервер запущен на порту {port}")
    print(f"🌐 Доступен по адресу: http://localhost:{port}")
    print("=" * 50)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен пользователем")
    except Exception as e:
        print(f"💥 Ошибка сервера: {e}")
    finally:
        httpd.server_close()
        print("🔒 Сервер завершил работу")


if __name__ == "__main__":
    run_server(8000)