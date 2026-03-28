# app/routes/dashboard.py
from flask import Blueprint, render_template, send_file, request
from app import db
from app.models import Booking, Room, User
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from weasyprint import HTML

dashboard_bp = Blueprint('dashboard', __name__)

# ====================== DASHBOARD Z WYKRESAMI ======================
@dashboard_bp.route('/')
def index():
    # ... (twój poprzedni kod dashboardu z wykresami – zostawiam bez zmian) ...
    dept_stats = db.session.query(
        User.department, func.count(Booking.id).label('count')
    ).join(Booking).group_by(User.department).all()

    department_data = [{"department": dept or "Brak departamentu", "count": int(c)} for dept, c in dept_stats]

    # (heatmap i trend bez zmian)
    return render_template('dashboard.html',
                           department_data=department_data,
                           # ... reszta jak wcześniej ...
                           )


# ====================== RAPORT PDF – Zadanie 6 (z polskimi znakami) ======================
@dashboard_bp.route('/api/reports/monthly', methods=['GET'])
def monthly_report():
    month_str = request.args.get('month')
    if not month_str:
        return {"error": "Podaj ?month=YYYY-MM"}, 400

    year, month = map(int, month_str.split('-'))

    bookings = Booking.query.filter(
        extract('year', Booking.start_time) == year,
        extract('month', Booking.start_time) == month
    ).all()

    total_bookings = len(bookings)
    total_hours = sum(b.duration_hours for b in bookings)
    total_revenue = sum(float(b.room.hourly_rate or 0) * b.duration_hours for b in bookings)

    html_content = f"""
    <h1>Raport miesięczny – {month_str}</h1>
    <h2>Podsumowanie</h2>
    <p>Liczba rezerwacji: <strong>{total_bookings}</strong></p>
    <p>Łączny czas: <strong>{total_hours:.1f} godz.</strong></p>
    <p>Przychód: <strong>{total_revenue:.2f} zł</strong></p>
    <h2>Top 10 sal</h2>
    <table border="1" cellpadding="5">
        <tr><th>Sala</th><th>Godziny</th></tr>
        {"".join(f"<tr><td>{name}</td><td>{hours:.1f}</td></tr>" for name, hours in 
            sorted({b.room.name: sum(b.duration_hours for b in bookings if b.room and b.room.name == name) 
                   for name in {b.room.name for b in bookings if b.room}}, 
                   key=lambda x: x[1], reverse=True)[:10])}
    </table>
    """

    pdf = HTML(string=html_content).write_pdf()

    return send_file(
        io.BytesIO(pdf),
        as_attachment=True,
        download_name=f"raport_{month_str}.pdf",
        mimetype='application/pdf'
    )