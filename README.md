# 📖 SIH Health Chatbot Backend

AI-Driven **Public Health Chatbot** for disease awareness, preventive healthcare, vaccination schedules, and outbreak alerts. Built as part of **SIH 2025 (Problem ID: 25049)** for Govt. of Odisha (Electronics & IT Dept.).

<div align="left">

[![CI](https://github.com/UTTAM-VAGHASIA/sih-health-chatbot-backend/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/UTTAM-VAGHASIA/sih-health-chatbot-backend/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116-green)
![License](https://img.shields.io/github/license/UTTAM-VAGHASIA/sih-health-chatbot-backend)
![Lines Of Code](https://tokei.rs/b1/github/UTTAM-VAGHASIA/sih-health-chatbot-backend?category=code)
![Last commit](https://img.shields.io/github/last-commit/UTTAM-VAGHASIA/sih-health-chatbot-backend)
![Commit activity](https://img.shields.io/github/commit-activity/m/UTTAM-VAGHASIA/sih-health-chatbot-backend)
![Open issues](https://img.shields.io/github/issues/UTTAM-VAGHASIA/sih-health-chatbot-backend)
![Open PRs](https://img.shields.io/github/issues-pr/UTTAM-VAGHASIA/sih-health-chatbot-backend)
![Stars](https://img.shields.io/github/stars/UTTAM-VAGHASIA/sih-health-chatbot-backend)
![Forks](https://img.shields.io/github/forks/UTTAM-VAGHASIA/sih-health-chatbot-backend)

<!-- Code quality & tooling -->
![Code style: black](https://img.shields.io/badge/code%20style-black-000000)
![Imports: isort](https://img.shields.io/badge/imports-isort-ef8336)
![Lint: flake8](https://img.shields.io/badge/lint-flake8-007EC6)
![Types: mypy](https://img.shields.io/badge/types-mypy-2A6DB2)
![Tests: pytest](https://img.shields.io/badge/tests-pytest-0A9EDC)
![Docker](https://img.shields.io/badge/docker-ready-2496ED)

</div>

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
├── src/                      # Source code
│   ├── main.py              # FastAPI entrypoint
│   ├── routers/             # API endpoints
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
│   └── config.py            # Configuration
│
├── scripts/                 # Automation scripts
│   ├── start-app.bat        # Windows startup
│   └── start-app.sh         # Linux/macOS startup
│
├── tests/                   # Unit/integration tests
├── docker/                  # Docker configuration
│   └── Dockerfile
├── pyproject.toml           # Poetry dependencies
├── requirements.txt         # Pip dependencies
├── docker-compose.yml       # Docker Compose setup
└── README.md
```

---

## ⚙️ Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/UTTAM-VAGHASIA/sih-health-chatbot-backend.git
cd sih-health-chatbot-backend
```

### 2. Setup Python Environment (Poetry)

```bash
poetry install
# To create env and activate it
poetry env activate

# If the above command does not activate it, then use the following command to activate venv
.\.venv\Scripts\activate
```

### 3. Run FastAPI Backend

```bash
uvicorn src.main:app --reload --port 8000
```

Check health endpoint: [http://127.0.0.1:8000/ping](http://127.0.0.1:8000/ping)

### 4. Run with Docker

#### Option A: Docker Compose with Cloudflare Tunnel (Recommended)

**Windows:**
```bash
scripts\start-app.bat
```

**Linux/macOS:**
```bash
chmod +x scripts/start-app.sh
./scripts/start-app.sh
```

**Manual:**
```bash
docker-compose up --build
```

**What happens:**
- ✅ **Docker containers start** (backend + cloudflared tunnel)
- ✅ **Cloudflare creates** temporary URL (e.g., `https://abc123.trycloudflare.com`)
- ✅ **Your webhook URL** will be: `https://abc123.trycloudflare.com/webhook/whatsapp`

#### Option B: Docker without tunnel (Local only)

```bash
docker build -t sih-chatbot-backend .
docker run -p 8000:8000 sih-chatbot-backend
```

**Note:** Option B only works locally. For WhatsApp webhooks, use Option A with Cloudflare tunnel.

---

## 📱 WhatsApp Integration

### Manual Webhook Setup

1. **Start your application** using one of the methods above
2. **Get your tunnel URL** from the cloudflared logs (look for `https://xxxxx.trycloudflare.com`)
3. **Go to [Meta Developer Console](https://developers.facebook.com/)**
4. **Navigate to your WhatsApp Business App**
5. **Go to WhatsApp > Configuration**
6. **Update webhook URL** to: `https://your-tunnel-url.trycloudflare.com/webhook/whatsapp`
7. **Set verify token** to: `sih-health-chatbot-secret`

### Webhook Endpoints

- **POST** `/webhook/whatsapp` - WhatsApp message webhook
- **GET** `/webhook/whatsapp` - WhatsApp webhook verification

---

## 🔧 Development

### Local Development (without Docker)

```bash
# Install dependencies
poetry install
poetry shell

# Run FastAPI backend
uvicorn src.main:app --reload --port 8000
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_main.py
```

---

## 🚀 Deployment

### Docker Deployment

```bash
# Start application
docker-compose up --build -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Considerations

1. **Use environment variables** for all configuration
2. **Set up proper monitoring** and logging
3. **Configure health checks** for your containers
4. **Use persistent storage** for databases
5. **Set up SSL certificates** if using custom domains

---

## 📚 Documentation

- [IMPLEMENTATION.md](IMPLEMENTATION.md) - Implementation details
- [FULL_ROADMAP.md](FULL_ROADMAP.md) - Complete project roadmap

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a Pull Request

---

## License

Licensed under the [MIT License](./LICENSE) © 2025.

---

## Creators [🔝](#sih-health-chatbot-backend)

| Author | Collaborator |
| :---: | :---: |
| [<img src="https://github.com/UTTAM-VAGHASIA.png?size=115" width=115><br><sub>@UTTAM-VAGHASIA</sub>](https://github.com/UTTAM-VAGHASIA) | [<img src="https://github.com/purify010622.png?size=115" width=115><br><sub>@Sarthak Yerpude</sub>](https://github.com/purify010622) |

## Thanks to all contributors ❤

<a href="https://github.com/UTTAM-VAGHASIA/sih-health-chatbot-backend/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=UTTAM-VAGHASIA/sih-health-chatbot-backend" />
</a>

---
