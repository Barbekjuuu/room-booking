# System Rezerwacji Sal Konferencyjnych

**Zaawansowana aplikacja webowa do zarządzania rezerwacjami sal konferencyjnych** zbudowana w ramach lekcji Flask + PostgreSQL.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)

## ✨ Funkcjonalności

- **CRUD sal konferencyjnych** (dodawanie, edycja, usuwanie)
- **Zarządzanie wyposażeniem** (relacja wiele-do-wielu)
- **Rezerwacje z walidacją konfliktów**
- **Rezerwacje cykliczne** (co tydzień, co 2 tygodnie, co miesiąc)
- **System powiadomień** (automatyczne dla admina i użytkownika)
- **Rozszerzony dashboard** z wykresami (Chart.js)
- **Raport miesięczny w PDF**
- **API REST** do powiadomień i raportów

## 🛠 Technologie

- **Backend**: Flask + Flask-SQLAlchemy
- **Baza danych**: PostgreSQL
- **Frontend**: Bootstrap + Chart.js
- **PDF**: FPDF2 / ReportLab
- **Cykliczne daty**: python-dateutil

## 🚀 Uruchomienie projektu

### 1. Sklonuj repozytorium
```bash
git clone https://github.com/Barbekjuuu/room-booking.git
cd room-booking