# 🚀 SIH 2025 – Backend Master Document (Living Context)

## 1. Problem Statement (ID: 25049)

**Title:** AI-Driven Public Health Chatbot for Disease Awareness
**Organization:** Govt. of Odisha (Electronics & IT Dept.)
**Category:** Software – HealthTech
**Goal:**

* Multilingual AI chatbot for **preventive healthcare, symptoms, vaccination schedules**.
* **Integrates with gov health databases**.
* **Provides outbreak alerts**.
* **Accessible via WhatsApp & SMS**.
* **Target outcomes:** ≥80% query accuracy, +20% awareness increase.

---

## 2. My Role

👉 Handling **Backend**:

* WhatsApp bot integration.
* SMS integration.
* Backend ↔ AI engine (Rasa/Dialogflow/LLM).
* APIs for health data.
* Logging & analytics DB.
* Cloud deploy (Docker).
* Provide APIs for frontend/dashboard.

---

## 3. Development Environment (Windows 11 + PowerShell)

✅ Installed so far:

* **Git (latest)**
* **Node.js 22 LTS**
* **Python 3.12.x**
* **Docker Desktop (Windows + WSL2 backend)**
* **GitHub CLI (gh)**
* **WSL (Ubuntu 22.04 LTS)**

📌 Notes:

* **Primary backend:** Python + FastAPI (latest 0.115.x as of Sep 2025).
* **Messaging bridges (WhatsApp/SMS):** Node.js helper scripts if needed.
* Use **Poetry** for Python dependency management (instead of pip venv).

---

## 4. High-Level Architecture

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

## 5. Repository Strategy

* **Main Repo:** GitHub (`sih-health-chatbot-backend`)
* Branching:

  * `main` → stable
  * `dev` → active development
  * feature branches: `feature/whatsapp-bot`, `feature/rasa-integration`, etc.
* CI/CD: GitHub Actions (Docker build + push).

---

## 6. Backend Folder Structure (Planned)

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
│   ├── utils/               # Helper functions
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

## 7. Backend Milestones & Status

### ✅ Environment Setup

* [x] Install Git, Node.js, Python, Docker, WSL, GitHub CLI.
* [ ] Configure Poetry for Python deps.
* [ ] Setup Postgres DB (Dockerized).

### 🔄 Repo & Basic Skeleton

* [ ] Create GitHub repo (`sih-health-chatbot-backend`).
* [ ] Add base FastAPI app (`main.py + /ping`).
* [ ] Setup pre-commit hooks + linting (black, isort, mypy).

### 🔄 Messaging Integration

* [ ] WhatsApp bot (Meta Cloud API).
* [ ] SMS bot (Twilio / Gupshup).

### 🔄 NLP & AI Engine

* [ ] Connect to Rasa/Dialogflow API.
* [ ] Define health intents (symptoms, vaccines, outbreak info).

### 🔄 Health Data Integration

* [ ] Vaccination schedule API wrapper.
* [ ] Outbreak alert API wrapper.

### 🔄 Persistence & Analytics

* [ ] DB models (users, conversations, analytics).
* [ ] Logging queries → Postgres.

### 🔄 Deployment

* [ ] Dockerize FastAPI backend.
* [ ] Setup CI/CD with GitHub Actions.
* [ ] Deploy to cloud (Render/Railway/AWS).

---

## 8. Implementation Status (as of now)

* ✅ Installed environment prerequisites (Git, Node.js, Python, Docker, gh, WSL).
* 🚧 Next step: **Initialize GitHub repo + push boilerplate FastAPI app**.

---

## 9. Next Action Items (Immediate)

1. Create repo:

```powershell
gh repo create sih-health-chatbot-backend --public --source=. --remote=origin --push
```

2. Initialize FastAPI app (`main.py` with `/ping`).
3. Push initial commit.
4. Share repo link here so I can guide you with WhatsApp API integration.

---

⚡ This document will evolve as you implement features. You just need to update **Section 8 + 9** with what’s done and what’s pending.


---

# 🛠 Implementation Details (Milestone 1)

## 1. Create Local Project Folder

```powershell
# Choose location (e.g., Documents or D:\Projects)
cd D:\Projects

# Make folder
mkdir sih-health-chatbot-backend
cd sih-health-chatbot-backend

# Initialize Git
git init
```

---

## 2. Setup Python Environment (Poetry)

Poetry avoids pip clutter, handles deps cleanly.

```powershell
# Install Poetry (if not already installed in Windows)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -

# Add poetry to PATH for this session
$env:Path += ";$env:APPDATA\Python\Scripts"

# Check install
poetry --version

# Init new poetry project
poetry init --no-interaction --dependency fastapi --dependency "uvicorn[standard]" --dependency requests --dependency python-dotenv
```

This generates **`pyproject.toml`** with deps.

Activate environment:

```powershell
poetry shell
```

---

## 3. Create Boilerplate FastAPI App

Inside `src/` folder:

```powershell
mkdir src
cd src
New-Item main.py
```

**src/main.py**

```python
from fastapi import FastAPI

app = FastAPI(title="SIH Health Chatbot Backend")

@app.get("/ping")
async def ping():
    return {"status": "ok", "message": "Backend is running 🚀"}
```

---

## 4. Run Locally

```powershell
# From project root
uvicorn src.main:app --reload --port 8000
```

Test in browser:
👉 [http://127.0.0.1:8000/ping](http://127.0.0.1:8000/ping)
Should return:

```json
{"status":"ok","message":"Backend is running 🚀"}
```

---

## 5. Setup GitHub Repo

```powershell
# Create repo via GitHub CLI
gh repo create sih-health-chatbot-backend --public --source=. --remote=origin --push

# Add and commit code
git add .
git commit -m "Initial FastAPI boilerplate with /ping endpoint"
git push -u origin main
```

Now repo is live ✅

---

## 6. Add .gitignore (Python + Poetry + Docker)

Create `.gitignore` in root:

```
__pycache__/
*.pyc
.env
.venv
poetry.lock
dist/
build/
docker-compose.override.yml
```

Commit:

```powershell
git add .gitignore
git commit -m "Add .gitignore"
git push
```

---

## 7. Verification

* ✅ Repo exists on GitHub.
* ✅ FastAPI `/ping` endpoint works locally.
* ✅ Poetry manages dependencies cleanly.

---

# 🔄 Updates for Master Document

### Section 8 (Implementation Status)

* ✅ Environment prerequisites installed.
* ✅ Created GitHub repo `sih-health-chatbot-backend`.
* ✅ Initialized FastAPI app (`main.py` with `/ping`).
* ✅ Added `.gitignore`.
* ✅ Created GitHub repo `sih-health-chatbot-backend`.
* ✅ Initialized FastAPI app (`main.py` with `/ping` endpoint).
* ✅ Added `.gitignore`.
* ✅ Added backend project skeleton (routers, services, db, utils, tests, docker, ci).
* ✅ Setup pre-commit hooks (black, isort, flake8, mypy).
* ✅ Added first test case for `/ping`.
* 🚧 Next: Prepare Dockerfile (for FastAPI + Uvicorn).

### Section 9 (Next Action Items)

1. Prepare Dockerfile (for FastAPI + Uvicorn).
2. Configure GitHub Actions (CI pipeline).

---
