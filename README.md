# 🏛️ Court Data Dashboard (Django + React)

A full-stack microservices-based web application that scrapes Delhi High Court case data using Selenium and presents it via a React frontend.

---

## 🔧 Setup Instructions

### 1. Backend (Django)

#### ✅ Create virtual environment and install dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate          # On Windows
# source venv/bin/activate     # On Mac/Linux

# Install required packages
pip install -r requirements.txt
```

#### ✅ Run Django server

```bash
cd court_backend
python manage.py runserver
```

---

### 2. Frontend (React)

#### ✅ Install frontend dependencies

```bash
cd frontend
npm install
```

#### ✅ Start React development server

```bash
npm start
```
