"""
Modele bazy danych dla systemu rezerwacji sal konferencyjnych.
Tutaj definiujemy wszystkie tabele i relacje.
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Ten sam obiekt db, który został stworzony w app/__init__.py
from app import db

# ================================================================
# TABELA ŁĄCZĄCA (Association Table) — Many-to-Many
# ================================================================
# Łączy Sale z Wyposażeniem (np. sala może mieć projektor + tablicę)
room_equipment = db.Table(
    'room_equipment',
    db.Column('room_id', db.Integer, db.ForeignKey('rooms.id'), primary_key=True),
    db.Column('equipment_id', db.Integer, db.ForeignKey('equipment.id'), primary_key=True)
)

# ================================================================
# MODEL: User (Użytkownik)
# ================================================================
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(50))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacja 1:N — jeden użytkownik może mieć wiele rezerwacji
    bookings = db.relationship('Booking', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.email}>'

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'department': self.department,
            'is_admin': self.is_admin
        }

# ================================================================
# MODEL: Equipment (Wyposażenie sali)
# ================================================================
class Equipment(db.Model):
    __tablename__ = 'equipment'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)   # np. "Projektor", "Tablica"
    icon = db.Column(db.String(50), default="default")             # do przyszłego UI

    def __repr__(self):
        return f'<Equipment {self.name}>'

# ================================================================
# MODEL: Room (Sala konferencyjna)
# ================================================================
class Room(db.Model):
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    floor = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    hourly_rate = db.Column(db.Numeric(10, 2), default=0.0)

    # Relacja 1:N — jedna sala może mieć wiele rezerwacji
    bookings = db.relationship('Booking', backref='room', lazy='dynamic',
                               cascade='all, delete-orphan')

    # Relacja M:N — sala może mieć wiele elementów wyposażenia
    equipment = db.relationship(
        'Equipment',
        secondary=room_equipment,      # tabela łącząca
        lazy='subquery',
        backref=db.backref('rooms', lazy=True)
    )

    def __repr__(self):
        return f'<Room {self.name} (cap: {self.capacity})>'

    def is_available(self, start_time, end_time, exclude_booking_id=None):
        """Sprawdza czy sala jest wolna w podanym terminie."""
        from app.models import Booking   # unikamy circular import

        query = Booking.query.filter(
            Booking.room_id == self.id,
            Booking.status != 'cancelled',
            Booking.start_time < end_time,
            Booking.end_time > start_time
        )

        if exclude_booking_id:
            query = query.filter(Booking.id != exclude_booking_id)

        return query.count() == 0

# ================================================================
# MODEL: Booking (Rezerwacja)
# ================================================================
class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='confirmed')   # confirmed / cancelled / completed
    
    # === NOWE POLA DLA CYKLICZNYCH REZERWACJI (Zadanie 5 punkt 1 i 2) ===
    recurrence_rule = db.Column(db.String(20), nullable=True)   # np. "WEEKLY", "BIWEEKLY", "MONTHLY" lub None
    series_id = db.Column(db.String(36), nullable=True)         # UUID serii (łączy wszystkie rezerwacje w cykl)

    attendees_count = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Booking {self.title} ({self.start_time})>'

    @property
    def duration_hours(self):
        delta = self.end_time - self.start_time
        return delta.total_seconds() / 3600
    
    # ================================================================
# MODEL: Notification (Powiadomienia) — Zadanie 4
# ================================================================
class Notification(db.Model):
    """Model powiadomień dla użytkowników i adminów."""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacja do użytkownika (żeby łatwo pobrać powiadomienia użytkownika)
    user = db.relationship('User', backref=db.backref('notifications', lazy='dynamic'))

    def __repr__(self):
        return f'<Notification {self.id} for user {self.user_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat()
        }
# ================================================================
# AUTOMATYCZNE POWIADOMIENIA (Zadanie 4 punkt 2)
# ================================================================
from sqlalchemy import event

@event.listens_for(Booking, 'after_insert')
def create_notification_after_booking(mapper, connection, target):
    """Automatycznie tworzy powiadomienie gdy ktoś doda nową rezerwację"""

    # Powiadomienie dla admina
    admin_message = f"Nowa rezerwacja: {target.title} w sali {target.room.name if target.room else 'nieznana'}"

    # Zakładamy, że admin ma id=1 (możesz to zmienić później)
    admin_notification = Notification(
        user_id=1,                    # ID admina
        message=admin_message,
        is_read=False
    )
    db.session.add(admin_notification)

    # Przypomnienie dla użytkownika (jeśli rezerwacja jest za mniej niż 1h)
    if target.start_time:
        time_diff = target.start_time - datetime.utcnow()
        if time_diff.total_seconds() < 3600:   # mniej niż 1 godzina
            user_message = f"Przypomnienie: Twoja rezerwacja '{target.title}' zaczyna się za mniej niż godzinę!"
            user_notification = Notification(
                user_id=target.user_id,
                message=user_message,
                is_read=False
            )
            db.session.add(user_notification)

       