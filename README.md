<div align="center">

# 🎯 AI Career Advisor

### An end-to-end, AI-powered Career Operating System for students and early-career professionals.

Practice coding, run AI mock interviews, map your Big Five personality, analyze skill gaps against real job descriptions, score your resume for ATS, and track your career readiness — all in one modular platform.

<p>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" />
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white" />
  <img alt="React" src="https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black" />
  <img alt="TypeScript" src="https://img.shields.io/badge/TypeScript-6-3178C6?logo=typescript&logoColor=white" />
  <img alt="Vite" src="https://img.shields.io/badge/Vite-8-646CFF?logo=vite&logoColor=white" />
  <img alt="SQLAlchemy" src="https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white" />
  <img alt="Docker" src="https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white" />
</p>

</div>

---

## ✨ Overview

**AI Career Advisor** brings the full job-preparation journey under one roof. Instead of juggling a coding
site, a personality quiz, a resume checker, and an interview simulator, students get a single, gamified
platform that tracks their growth with XP, levels, and streaks.

The platform is **AI-optional by design**: connect an LLM provider (OpenRouter or Google Gemini) to unlock
adaptive interviews and richer feedback, or run it fully offline — every AI feature gracefully falls back to
deterministic local heuristics so demos never break.

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** (project pins **3.12** via `runtime.txt`)
- **Node.js 18+** and `npm`
- *(Optional)* Docker & Docker Compose

### 1. Backend — FastAPI + SQLite/PostgreSQL

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# (Optional) configure environment — the app runs without this,
# but copy the template if you want to set an AI key or a secret.
cp .env.example .env

# Seed demo accounts, coding problems, MCQs, jobs & events
python seed.py

# Launch the API (Swagger docs at http://localhost:8000/docs)
uvicorn app.main:app --port 8000 --reload
```

### 2. Frontend — React + TypeScript + Vite

```bash
cd frontend

npm install
npm run dev     # UI at http://localhost:5173
```

### 3. One-Click Launch (Windows)

Double-click **`start.bat`** in the project root to boot both services in separate terminals.

---

## 🔑 Demo Credentials

Seeded automatically by `python seed.py`:

| Role | Email | Password | Access |
|------|-------|----------|--------|
| 👨‍🎓 **Student** | `student@careeradvisor.ai` | `student12345` | All student modules, XP, history & a fully populated demo profile |
| 🛡️ **Admin** | `admin@careeradvisor.ai` | `admin12345` | Everything above + Admin Panel & platform metrics |

---

## 🤖 Enabling AI (Optional)

Every AI feature works without a key by falling back to local logic. To enable live LLM responses, set **one**
of the following in `backend/.env`:

```bash
# Option A — OpenRouter (takes precedence if both are set)
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=meta-llama/llama-3.3-70b-instruct

# Option B — Google Gemini
GEMINI_API_KEY=...
```

The AI layer is a lightweight async `httpx` client that auto-selects the provider, strips model quirks (code
fences, "thinking" tokens), and returns `None` on any failure so callers stay resilient. A live diagnostic is
exposed at `GET /api/health/ai`.

---

## 🛠️ Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| **Frontend** | React 19 · TypeScript · Vite | Fast SPA with client-side routing (`react-router-dom`) |
| **Design** | Vanilla CSS (dark glassmorphism) | Custom theme system with light/dark support |
| **Backend** | FastAPI · Python 3.12 | Async REST API |
| **ORM / DB** | SQLAlchemy 2.0 (async) · SQLite / PostgreSQL | `aiosqlite` locally, `asyncpg` in production |
| **Migrations** | Alembic | Schema versioning |
| **Auth** | JWT (python-jose) · PBKDF2 password hashing | Stateless access tokens |
| **AI** | OpenRouter **or** Gemini via `httpx` | Auto-fallback to local heuristics |
| **Docs / Resume** | `pypdf` · `python-docx` · `reportlab` | Parsing & PDF generation for ATS scoring |
| **Orchestration** | Docker Compose | Postgres · Redis · ChromaDB · API · UI |

---

## 🧩 Core Modules

| # | Module | What it does |
|---|--------|--------------|
| 1 | **Dashboard** | Aggregates readiness score, XP, level, streaks & quick links |
| 2 | **Profile** | Rich profile — education, work, projects, certifications, awards & benchmarks |
| 3 | **Code Quest** | Multi-language auto-judge (Python & JavaScript) with test cases & leaderboard |
| 4 | **Aptitude Quest** | Timed quant, logical & verbal MCQ quizzes with per-topic breakdown |
| 5 | **Personality Test** | Big Five (OCEAN) inventory — BFI-44 & IPIP-120 frameworks |
| 6 | **Position AI** | Paste a job description to surface missing skills & learning paths |
| 7 | **Documents** | Secure vault for resumes, certificates & portfolio files |
| 8 | **Job Board** | Browse & filter listings by skills, location & type |
| 9 | **My Jobs** | Track and manage your applications |
| 10 | **Resume Builder** | Generate resumes & compute ATS compatibility scores |
| 11 | **Events** | Career fairs & technical webinars |
| 12 | **Interview Coach** | Structured + adaptive AI mock interviews with scored feedback |
| 13 | **Assessments** | Overall career-readiness scoring |
| 14 | **Admin Panel** | User directory & platform analytics |

---

## 📁 Project Structure

```
ai-carrer-advisor/
├── backend/
│   ├── app/
│   │   ├── ai/                  # LLM client (OpenRouter / Gemini + fallbacks)
│   │   ├── api/routers/         # auth, profile, jobs, codequest, aptitude,
│   │   │                        # personality, documents, interview, events,
│   │   │                        # position_ai, notifications, admin
│   │   ├── content/             # Seed content: codequest, aptitude, personality banks
│   │   ├── core/                # Config & security (JWT, PBKDF2)
│   │   ├── db/                  # Async session factory & DB init
│   │   ├── models/              # SQLAlchemy ORM models
│   │   └── schemas/             # Pydantic request/response models
│   ├── alembic/                 # Database migrations
│   ├── tests/                   # Backend tests
│   ├── seed*.py                 # Data seeders (problems, jobs, events, aptitude)
│   ├── requirements.txt
│   └── runtime.txt              # Pinned Python version
├── frontend/
│   └── src/
│       ├── components/          # Layout, Sidebar, Navbar, ProtectedLayout
│       ├── context/             # Auth & Theme providers
│       ├── pages/               # One folder/page per module
│       ├── services/            # Axios API client
│       └── styles/              # Glassmorphism CSS system
├── docker-compose.yml           # Postgres · Redis · ChromaDB · API · UI
├── render.yaml                  # Render.com deployment config
├── start.bat                    # Windows one-click launcher
└── README.md
```

---

## 🐳 Running with Docker

```bash
docker compose up --build
```

This spins up Postgres, Redis, ChromaDB, the FastAPI backend, and the Vite frontend. The backend is published
on port **8080**, the UI on **5173**.

---

## 🧪 Testing

```bash
cd backend
pytest
```

---

## 🔒 Security Notes

- Set a strong `SECRET_KEY` and `DEBUG=False` before any deployment — in non-debug mode the app refuses to
  start without a secret, and the API docs are disabled.
- `.env`, local databases (`*.db`) and uploads are git-ignored. Never commit real credentials.
- Passwords are hashed with PBKDF2; sessions use stateless JWTs.

---

## 📄 License

This project is provided as-is for educational and demonstration purposes.
