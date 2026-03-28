# run.py — główny plik startowy aplikacji
from app import create_app

# Tworzymy aplikację w trybie development
app = create_app()

if __name__ == '__main__':
    print("🚀 Uruchamiam aplikację System Rezerwacji Sal...")
    app.run(debug=True, port=5000)