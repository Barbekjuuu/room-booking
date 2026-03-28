# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config

# Jeden wspólny obiekt db dla całego projektu
db = SQLAlchemy()

def create_app(config_name='development'):
    """Fabryka aplikacji Flask"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # NAJWAŻNIEJSZE: Najpierw łączymy db z aplikacją
    db.init_app(app)

    # =============================================================
    # AUTOMATYCZNE TWORZENIE TABEL PRZY URUCHOMIENIU (tylko na etapie development)
    # =============================================================
    with app.app_context():
        db.create_all()          # tworzy wszystkie tabele z models.py
        print("✅ Tabele w bazie zostały utworzone / zweryfikowane")

    # Dopiero teraz importujemy blueprinty (po init_app!)
    from app.routes.rooms import rooms_bp
    from app.routes.bookings import bookings_bp
    from app.routes.dashboard import dashboard_bp

    app.register_blueprint(rooms_bp, url_prefix='/rooms')
    app.register_blueprint(bookings_bp, url_prefix='/bookings')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

    # Test połączenia z bazą
    @app.route('/test-db')
    def test_db():
        try:
            with app.app_context():
                db.create_all()
                db.session.execute(db.text('SELECT 1'))
            return "<h1>✅ Połączenie z bazą OK!</h1>"
        except Exception as e:
            return f"<h1>❌ Błąd: {str(e)}</h1>"

    # Strona główna
    @app.route('/')
    def home():
        return """
        <h1>✅ System Rezerwacji Sal Konferencyjnych</h1>
        <hr>
        <a href="/rooms">Zarządzanie salami</a><br>
        <a href="/bookings">Rezerwacje</a><br>
        <a href="/dashboard">Dashboard</a>
        """

    return app