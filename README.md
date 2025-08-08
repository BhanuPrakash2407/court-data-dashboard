# Court Data Dashboard (Django + React)

A full-stack microservices-based app that scrapes Delhi High Court case data using Selenium and displays it through a React frontend.

---

## 🔧 Setup Instructions

### 1. Backend (Django)

#### Create virtual environment & install dependencies:
```bash
python -m venv venv
venv\Scripts\activate         # For Windows
# source venv/bin/activate   # For Linux/Mac

pip install -r requirements.txt

Run Django server:
cd court_backend
python manage.py runserver

Install frontend dependencies:
cd frontend
npm install
npm start

