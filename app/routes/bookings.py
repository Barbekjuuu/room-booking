# app/routes/bookings.py
from flask import Blueprint, request, render_template_string
from app import db
from app.models import Booking
from datetime import datetime
from dateutil.rrule import rrule, WEEKLY, MONTHLY, DAILY
import uuid

bookings_bp = Blueprint('bookings', __name__)

@bookings_bp.route('/')
def index():
    bookings = Booking.query.order_by(Booking.start_time.desc()).all()
    return render_template_string('''
    <h1>Rezerwacje</h1>
    <a href="/bookings/create_single">→ Nowa pojedyncza rezerwacja</a><br>
    <a href="/bookings/create_recurring">→ Nowa rezerwacja cykliczna</a><br>
    <a href="/bookings/cancel">→ Anuluj rezerwację / serię</a><br><br>
    <table border="1" cellpadding="5">
        <tr><th>ID</th><th>Tytuł</th><th>Data</th><th>Series ID</th></tr>
        {% for b in bookings %}
        <tr>
            <td>{{ b.id }}</td>
            <td>{{ b.title }}</td>
            <td>{{ b.start_time.strftime('%Y-%m-%d %H:%M') }}</td>
            <td>{{ b.series_id or '-' }}</td>
        </tr>
        {% endfor %}
    </table>
    ''', bookings=bookings)


# ====================== POJEDYNCZA REZERWACJA ======================
@bookings_bp.route('/create_single', methods=['GET', 'POST'])
def create_single():
    if request.method == 'GET':
        return render_template_string('''
        <h2>Nowa pojedyncza rezerwacja</h2>
        <form method="POST">
            Room ID: <input type="number" name="room_id" value="1"><br>
            User ID: <input type="number" name="user_id" value="1"><br>
            Tytuł: <input type="text" name="title" value="Spotkanie"><br>
            Start (ISO): <input type="text" name="start_time" value="2026-04-10T09:00:00"><br>
            Koniec (ISO): <input type="text" name="end_time" value="2026-04-10T10:00:00"><br>
            <button type="submit">Zapisz rezerwację</button>
        </form>
        ''')
    data = request.form
    booking = Booking(
        room_id=int(data['room_id']),
        user_id=int(data['user_id']),
        title=data['title'],
        start_time=datetime.fromisoformat(data['start_time']),
        end_time=datetime.fromisoformat(data['end_time'])
    )
    db.session.add(booking)
    db.session.commit()
    return f"<h2>Sukces!</h2><p>Rezerwacja nr {booking.id} została utworzona.</p><a href='/bookings'>← Lista</a>"


# ====================== CYKLICZNA REZERWACJA ======================
@bookings_bp.route('/create_recurring', methods=['GET', 'POST'])
def create_recurring():
    if request.method == 'GET':
        return render_template_string('''
        <h2>Tworzenie rezerwacji cyklicznej</h2>
        <form method="POST">
            Room ID: <input type="number" name="room_id" value="1"><br>
            User ID: <input type="number" name="user_id" value="1"><br>
            Tytuł: <input type="text" name="title" value="Cotygodniowe spotkanie zespołu"><br>
            Data startu (ISO): <input type="text" name="start_time" value="2026-04-10T09:00:00"><br>
            Data końca (ISO): <input type="text" name="end_time" value="2026-04-10T10:00:00"><br>
            Typ cyklu: 
            <select name="recurrence_rule">
                <option value="WEEKLY">Co tydzień</option>
                <option value="BIWEEKLY">Co 2 tygodnie</option>
                <option value="MONTHLY">Co miesiąc</option>
            </select><br>
            Liczba powtórzeń: <input type="number" name="occurrences" value="4"><br>
            <button type="submit">Utwórz serię rezerwacji</button>
        </form>
        ''')

    data = request.form
    room_id = int(data.get('room_id'))
    user_id = int(data.get('user_id'))
    title = data.get('title')
    start_time = datetime.fromisoformat(data.get('start_time'))
    end_time = datetime.fromisoformat(data.get('end_time'))
    recurrence_rule = data.get('recurrence_rule')
    occurrences = int(data.get('occurrences', 4))

    series_id = str(uuid.uuid4())
    rule_map = {"WEEKLY": WEEKLY, "BIWEEKLY": WEEKLY, "MONTHLY": MONTHLY}
    freq = rule_map.get(recurrence_rule)
    interval = 2 if recurrence_rule == "BIWEEKLY" else 1

    created = 0
    for dt in rrule(freq, interval=interval, count=occurrences, dtstart=start_time):
        booking = Booking(
            room_id=room_id,
            user_id=user_id,
            title=title,
            start_time=dt,
            end_time=dt + (end_time - start_time),
            recurrence_rule=recurrence_rule,
            series_id=series_id
        )
        db.session.add(booking)
        created += 1

    db.session.commit()
    return f"""
    <h2>Sukces!</h2>
    <p>Utworzono <strong>{created}</strong> rezerwacji w serii.</p>
    <p>Series ID: <code>{series_id}</code></p>
    <p><a href="/bookings/create_recurring">Utwórz kolejną serię</a></p>
    <p><a href="/">← Powrót na stronę główną</a></p>
    """