# 📖 SIH Health Chatbot Backend

AI-Driven **Public Health Chatbot** for disease awareness, preventive healthcare, vaccination schedules, and outbreak alerts. Built as part of **SIH 2025 (Problem ID: 25049)** for Govt. of Odisha (Electronics & IT Dept.).

---

## 🚀 Features

* Multilingual AI chatbot for **symptoms, vaccination info, outbreak alerts**
* Integration with **government health databases**
* Accessible via **WhatsApp & SMS**
* Admin API for dashboards & analytics
* Cloud-native (Dockerized FastAPI backend)

---

## 🏗️ Architecture

```
 User (WhatsApp/SMS)
        │
        ▼
 WhatsApp Cloud API / SMS Gateway
        │ Webhooks
        ▼
  Backend (FastAPI)
    ├── NLP Engine Connector (Rasa/Dialogflow/LLM API)
    ├── Health Data APIs (Vaccination, Outbreak Alerts)
    ├── Persistence (Postgres/MongoDB)
    ├── Admin/Dashboard API
    └── Message Router
        │
        ▼
   Response → WhatsApp/SMS → User
```

---

## 📂 Project Structure

```
sih-backend/
├── src/
│   ├── main.py              # FastAPI entrypoint
│   ├── routers/             # Endpoints
│   │   ├── whatsapp.py
│   │   ├── sms.py
│   │   ├── health.py
│   │   └── admin.py
│   ├── services/            # Business logic
│   │   ├── nlp_connector.py
│   │   ├── vaccination.py
│   │   └── outbreak.py
│   ├── db/                  # Database layer
│   │   ├── models.py
│   │   └── crud.py
│   ├── utils/               # Helpers
│   └── config.py            # Env + settings
│
├── tests/                   # Unit/integration tests
├── docker/
│   └── Dockerfile
├── pyproject.toml            # Poetry deps
├── requirements.txt (export)
├── README.md
└── .github/
    └── workflows/ci.yml
```

---

## ⚙️ Setup Instructions

### 1. Clone Repo

```bash
git clone https://github.com/<your-username>/sih-health-chatbot-backend.git
cd sih-health-chatbot-backend
```

### 2. Setup Python Environment (Poetry)

```bash
poetry install
poetry shell
```

### 3. Run FastAPI Backend

```bash
uvicorn src.main:app --reload --port 8000
```

Check health endpoint: [http://127.0.0.1:8000/ping](http://127.0.0.1:8000/ping)

### 4. Run with Docker

```bash
docker build -t sih-chatbot-backend .
docker run -p 8000:8000 sih-chatbot-backend
```

---

## 🔌 Integrations

* **WhatsApp Cloud API** → Webhook for chatbot messaging
* **SMS Gateway (Twilio/Gupshup)** → SMS-based interactions
* **Rasa/Dialogflow/LLM API** → NLP for intent recognition
* **Postgres** → Conversation logging & analytics
* **Admin API** → Data for dashboard frontend

---

## 🧪 Testing

Run tests with:

```bash
pytest
```

---

## 🚧 Roadmap

* [x] Environment setup (Git, Node.js, Python, Docker, gh, WSL)
* [x] Repo initialization + FastAPI boilerplate (`/ping`)
* [ ] WhatsApp & SMS bot integration
* [ ] NLP engine connection
* [ ] Health data APIs
* [ ] Database models & logging
* [ ] Admin API
* [ ] Dockerized deployment with CI/CD
* [ ] Test coverage ≥70%

---

## 📜 License

MIT License © 2025

---

## 👨‍💻 Contributors

* **Uttam Vaghasia** – Backend Developer
* Team SIH 2025
