# app/routes/rooms.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, Room

rooms_bp = Blueprint('rooms', __name__)

# ====================== LISTA SAL ======================
@rooms_bp.route('/')
def index():
    rooms = Room.query.order_by(Room.name).all()
    return render_template('rooms.html', rooms=rooms)


# ====================== DODAJ SALĘ ======================
@rooms_bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form.get('name')
        capacity = request.form.get('capacity', type=int)
        floor = request.form.get('floor', type=int)
        description = request.form.get('description')
        hourly_rate = request.form.get('hourly_rate', type=float)

        new_room = Room(
            name=name,
            capacity=capacity,
            floor=floor,
            description=description,
            hourly_rate=hourly_rate
        )

        db.session.add(new_room)
        db.session.commit()

        flash(f'Sala "{name}" została dodana!', 'success')
        return redirect(url_for('rooms.index'))

    return render_template('rooms_add.html')


# ====================== USUŃ SALĘ ======================
@rooms_bp.route('/delete/<int:room_id>')
def delete(room_id):
    room = Room.query.get_or_404(room_id)
    db.session.delete(room)
    db.session.commit()
    flash(f'Sala "{room.name}" została usunięta.', 'danger')
    return redirect(url_for('rooms.index'))