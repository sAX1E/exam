from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import redis

app = Flask(__name__)

# Настройка БД: тот же путь, но новая схема магазина игр
_data_dir = os.environ.get("DATA_DIR")
if not _data_dir:
    _data_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
    )
os.makedirs(_data_dir, exist_ok=True)
_db_path = os.path.join(_data_dir, "auction.db")

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URI", "sqlite:///" + _db_path.replace("\\", "/")
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "games-store-secret-key")

redis_host = os.environ.get("REDIS_HOST", "localhost")
redis_port = int(os.environ.get("REDIS_PORT", 6379))
redis_client = redis.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)

db = SQLAlchemy(app)
CORS(app)


# Модели приложения «Онлайн‑магазин игр»
class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    genre = db.Column(db.String(50), nullable=False)


class StoreUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    purchased_game_id = db.Column(db.Integer, db.ForeignKey("game.id"), nullable=False)

    purchased_game = db.relationship("Game")


# Инициализация БД и заполнение тестовыми данными из задания
with app.app_context():
    db.create_all()

    if Game.query.count() == 0:
        games_seed = [
            {"id": 1, "title": "Genshin Impact", "price": "Бесплатная", "genre": "Гача"},
            {"id": 2, "title": "ARMA", "price": "999", "genre": "Симулятор"},
            {"id": 3, "title": "Disco Elisyum", "price": "725", "genre": "Ролевая"},
            {"id": 4, "title": "The Witcher 3", "price": "1500", "genre": "Приключения"},
        ]
        for g in games_seed:
            db.session.add(
                Game(id=g["id"], title=g["title"], price=g["price"], genre=g["genre"])
            )
        db.session.commit()

    if StoreUser.query.count() == 0:
        users_seed = [
            {"id": 1, "login": "paimon", "password": "raidenei", "purchased_game_id": 1},
            {"id": 2, "login": "tu134", "password": "piupiupiu", "purchased_game_id": 2},
            {
                "id": 3,
                "login": "kimkitsuragi",
                "password": "garrystop",
                "purchased_game_id": 3,
            },
        ]
        for u in users_seed:
            db.session.add(
                StoreUser(
                    id=u["id"],
                    login=u["login"],
                    password=u["password"],
                    purchased_game_id=u["purchased_game_id"],
                )
            )
        db.session.commit()


@app.route("/")
def index():
    """
    Простая главная страница с описанием API.
    """
    return render_template("index.html")


@app.route("/login", methods=["GET"])
def login_page():
    """
    Страница логина (форму можно использовать для ручной проверки логина/пароля).
    """
    return render_template("login.html")


@app.route("/api/games", methods=["GET"])
def get_games():
    """
    Получение информации о всех играх:
    название, стоимость и жанр.
    """
    games = Game.query.all()
    return jsonify(
        [
            {
                "id": g.id,
                "title": g.title,
                "price": g.price,
                "genre": g.genre,
            }
            for g in games
        ]
    )


@app.route("/api/user-games", methods=["POST"])
def get_user_games():
    """
    Получение информации о купленных играх пользователя.
    Аутентификация: сверка логина и пароля с записями в БД.
    Ожидается JSON:
    {
      "login": "...",
      "password": "..."
    }
    """
    data = request.get_json(silent=True) or {}
    login = data.get("login")
    password = data.get("password")

    if not login or not password:
        return jsonify({"error": "Необходимо передать логин и пароль"}), 400

    user = StoreUser.query.filter_by(login=login, password=password).first()
    if not user:
        try:
            redis_client.incr("failed_logins")
        except Exception:
            pass
        return (
            jsonify({"error": "Неверная пара логин‑пароль или пользователя нет в БД"}),
            401,
        )

    try:
        redis_client.incr("successful_logins")
    except Exception:
        pass

    game = user.purchased_game
    if not game:
        return jsonify({"message": "У пользователя нет купленных игр"}), 200

    return jsonify(
        {
            "user": {
                "id": user.id,
                "login": user.login,
            },
            "purchased_game": {
                "id": game.id,
                "title": game.title,
                "price": game.price,
                "genre": game.genre,
            },
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
