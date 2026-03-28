"""
Konfiguracja aplikacji Flask.
NIGDY nie commituj haseł do repozytorium!
"""
import os
from dotenv import load_dotenv

load_dotenv()  # Ładuje zmienne z pliku .env

class Config:
    """Bazowa konfiguracja."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-me')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """Konfiguracja deweloperska."""
    DEBUG = True
    # Format: postgresql://USER:PASSWORD@HOST:PORT/DATABASE
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://postgres:admin123@localhost:5432/room_booking'   # <-- zmienione
    )
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Konfiguracja produkcyjna."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_ECHO = False


# Słownik do łatwego wyboru konfiguracji
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}