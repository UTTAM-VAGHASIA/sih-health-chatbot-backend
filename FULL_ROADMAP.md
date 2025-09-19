# 🚀 SIH 2025 – Backend Implementation Plan (Full Roadmap)

This is the **end-to-end backend implementation plan** for the project *AI-Driven Public Health Chatbot for Disease Awareness* (Problem ID: 25049). It covers environment setup, repository strategy, milestones, deliverables, and integration steps. This document will serve as the **master execution guide**.

---

## 1. Environment Setup (Windows 11 + PowerShell)

### ✅ Already Done

* Git (latest)
* Node.js 22 LTS
* Python 3.12.x
* Docker Desktop (WSL2 backend)
* GitHub CLI (gh)
* WSL (Ubuntu 22.04 LTS)

### 🔄 To Do

* Configure Poetry (Python dependency manager)
* Setup Postgres DB with Docker Compose
* Setup VSCode Dev Environment (extensions: Python, Docker, GitHub Copilot, REST Client)

**Deliverable:** Local dev environment fully functional with linting + formatting tools.

---

## 2. Repository & Project Initialization

* Create GitHub repo: `sih-health-chatbot-backend`
* Add `.gitignore` (Python, Docker, Poetry)
* Initialize Poetry project
* Add FastAPI boilerplate (`/ping` endpoint)
* Setup pre-commit hooks (black, isort, flake8, mypy)
* Setup GitHub Actions for CI (lint + test)

**Deliverable:** CI-ready repo with base FastAPI app.

---

## 3. Project Structure

```
sih-backend/
├── src/
│   ├── main.py              # FastAPI entrypoint
│   ├── routers/             # API routes
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

**Deliverable:** Empty but structured codebase committed.

---

## 4. Messaging Integration

### WhatsApp (Meta Cloud API)

* Setup Meta Developer account
* Configure sandbox with test number
* Implement webhook in FastAPI (`routers/whatsapp.py`)
* Send/receive messages
* Route user queries to NLP engine

### SMS (Twilio / Gupshup)

* Register sandbox account
* Configure inbound webhook (`routers/sms.py`)
* Implement outbound SMS reply handler

**Deliverable (Phase 1):** WhatsApp bot echo response working.
**Deliverable (Phase 2):** SMS bot echo response working.

---

## 5. NLP/AI Engine Integration

### Option A: Rasa

* Deploy Rasa server (Docker)
* Define intents: `symptom_check`, `vaccine_info`, `outbreak_alert`
* Connect via REST API to FastAPI

### Option B: Dialogflow CX

* Create project in Google Cloud
* Export agent config
* Connect backend via Dialogflow API

### Option C: LLM API (Fallback)

* Integrate OpenAI/Gemini API for generic health Q\&A

**Deliverable:** Messages routed from WhatsApp/SMS → NLP → backend → response to user.

---

## 6. Health Data Integration

* Identify Govt. APIs (or mock JSON if not public)
* Build `services/vaccination.py`:

  * Input: age, state
  * Output: vaccine schedule
* Build `services/outbreak.py`:

  * Input: district
  * Output: current alerts
* NLP intents mapped to these services

**Deliverable:** Dynamic health info retrieval.

---

## 7. Database & Logging

* Postgres DB via Docker Compose
* Models: `User`, `Conversation`, `MessageLog`, `Analytics`
* CRUD utils for logs
* Log every query + response for analytics

**Deliverable:** Conversation logs stored persistently.

---

## 8. Admin/Dashboard API

* Endpoints for analytics:

  * `/admin/stats` → conversation counts, accuracy estimates
  * `/admin/users` → active users
  * `/admin/alerts` → outbreaks summary
* Role-based authentication (JWT)

**Deliverable:** Admin API ready for frontend dashboard.

---

## 9. Deployment

* Dockerize FastAPI backend
* Docker Compose with Postgres + Rasa
* GitHub Actions → build + push Docker image
* Deploy on **Render/Railway/AWS** (based on credits & hackathon feasibility)
* Use **ngrok** for local testing with WhatsApp API

**Deliverable:** Live backend accessible over internet.

---

## 10. Testing & QA

* Unit tests (pytest)
* Integration tests (FastAPI TestClient)
* API mocking for WhatsApp/SMS
* Load test with locust (simulate 500 concurrent users)

**Deliverable:** Test coverage ≥70%.

---

## 11. Documentation & Handover

* API docs (FastAPI auto-generated at `/docs`)
* README with setup instructions
* Contribution guide
* Deployment guide (step-by-step)

**Deliverable:** Project ready for judges & maintainers.

---

## 📌 Timeline (Suggested for Hackathon)

* **Day 1–2:** Env setup + repo init + boilerplate
* **Day 3–4:** WhatsApp + SMS integration (echo bot)
* **Day 5–6:** NLP integration (Rasa/Dialogflow)
* **Day 7:** Health data microservices
* **Day 8:** DB + logging
* **Day 9:** Deployment (Docker + cloud)
* **Day 10:** Testing + polishing

---

## ✅ Tracking Status (to update in Master Doc)

* Env setup → ✅ (done)
* Repo + boilerplate → ✅ (done)
* WhatsApp → 🚧 (in progress, echo bot setup)
* SMS → ❌ (pending)
* NLP → ❌
* Health APIs → ❌
* DB/logging → ❌
* Admin API → ❌
* Deployment → ❌
* Tests/docs → ❌

---

👉 This implementation plan should be **referenced alongside the Master Context Doc**. It gives you both the *roadmap* and the *execution checkpoints*.
