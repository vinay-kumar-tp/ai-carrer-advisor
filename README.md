# AI Career Advisor — Complete Platform Architecture & Operating System

> An end-to-end, modular, AI-driven **Career Operating System** for students and early-career professionals. Integrates 14 core career modules, including interactive online coding practice, AI mock interviews, Big Five personality mapping, skill gap analysis, and ATS resume scoring.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.10+**
- **Node.js 18+** & `npm`
- *(Optional)* Docker & Docker Compose

### 2. Local Setup & Run

#### Backend (FastAPI + SQLite/PostgreSQL)
```bash
# Navigate to backend directory
cd backend

# Install python dependencies
pip install -r requirements.txt

# Seed database with initial coding problems, MCQs, jobs & demo accounts
python seed.py

# Launch FastAPI development server
uvicorn app.main:app --port 8000 --reload
```
*API Swagger Documentation will be available at: http://localhost:8000/docs*

#### Frontend (React + TypeScript + Vite)
```bash
# Navigate to frontend directory
cd frontend

# Install node packages
npm install

# Start Vite dev server
npm run dev
```
*Application UI will be available at: http://localhost:5173*

#### Quick Launcher (Windows)
Double-click `start.bat` in the root directory to launch both services simultaneously.

---

## 🔑 Pre-Seeded Credentials

| User Role | Email | Password | Access Level |
|-----------|-------|----------|--------------|
| **Demo Student** | `student@careeradvisor.ai` | `student12345` | Access to all 14 student modules, XP stats & history |
| **System Admin** | `admin@careeradvisor.ai` | `admin12345` | Student features + System Admin Panel & Metrics |

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend UI** | React 18 + TypeScript + Vite | Responsive, lightning-fast Single Page Application |
| **Design System** | Vanilla CSS (Cyber Dark Glassmorphism) | Custom glassmorphism aesthetic, dark mode, smooth transitions |
| **Backend API** | FastAPI (Python 3.13) | Asynchronous RESTful microservice API architecture |
| **Database** | SQLAlchemy 2.0 + SQLite / PostgreSQL | Dual-compatible relational ORM with JSON support |
| **Authentication** | JWT (JSON Web Tokens) + PBKDF2 SHA-256 | Secure stateless auth with access & refresh tokens |
| **Code Execution** | Subprocess Sandbox Engine | Multi-language auto-judge execution for Python & JS |
| **Vector DB** | ChromaDB Integration Ready | RAG-grounded career advising & semantic search |
| **Orchestration** | Docker & Docker Compose | Containerized service deployment (Postgres, Redis, Chroma, API, UI) |

---

## 📦 System Architecture & 14 Core Modules

```
ai-career-advisor/
├── backend/
│   ├── app/
│   │   ├── api/routers/        # Module endpoint handlers
│   │   │   ├── auth.py          # Register, Login, Refresh tokens
│   │   │   ├── profile.py       # My Profile & Skill proficiency
│   │   │   ├── jobs.py          # Job Board & Applications
│   │   │   ├── codequest.py     # Code Quest auto-judge engine
│   │   │   ├── aptitude.py      # Aptitude MCQ quiz engine
│   │   │   ├── personality.py   # Big Five OCEAN assessment
│   │   │   ├── documents.py     # Document vault & ATS resume parser
│   │   │   ├── interview.py     # Structured & Adaptive AI Interview Coach
│   │   │   ├── events.py        # Fairs & Technical Webinars
│   │   │   └── admin.py        # System analytics & User directory
│   │   ├── core/                # Config & PBKDF2 security
│   │   ├── db/                  # Session factory & SQLite/Postgres init
│   │   ├── models/              # 20+ ORM Database Models
│   │   └── schemas/             # Pydantic request/response validators
│   ├── seed.py                  # Initial data seeder
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/          # Sidebar, Navbar, ProtectedLayout
│   │   ├── context/             # AuthContext state management
│   │   ├── pages/               # 14 Full Module Pages
│   │   │   ├── Dashboard.tsx        # Module 1: Home Dashboard & XP Stats
│   │   │   ├── Profile.tsx          # Module 2: My Profile & Skills
│   │   │   ├── VideoResume.tsx      # Module 3: Video Resume Pitch
│   │   │   ├── CodeQuest.tsx        # Module 4: Code Quest Online Judge
│   │   │   ├── AptitudeQuest.tsx    # Module 5: Aptitude MCQ Quizzes
│   │   │   ├── PersonalityTest.tsx  # Module 6: Big Five OCEAN Test
│   │   │   ├── PositionAI.tsx       # Module 7: Skill Gap Analyzer
│   │   │   ├── Documents.tsx        # Module 8: Document Vault
│   │   │   ├── JobBoard.tsx         # Module 9: Job Board & Filter
│   │   │   ├── MyJobs.tsx           # Module 10: Application Tracker
│   │   │   ├── ResumeBuilder.tsx    # Module 11: AI Resume Builder & ATS
│   │   │   ├── Events.tsx           # Module 12: Events & Webinars
│   │   │   ├── InterviewCoach.tsx   # Module 13: AI Mock Interviewer
│   │   │   ├── Assessments.tsx      # Module 14: Career Readiness Score
│   │   │   └── AdminDashboard.tsx   # Admin Panel & User Metrics
│   │   ├── services/api.ts      # Axios API client layer
│   │   └── styles/index.css     # Cyber Dark Glassmorphism CSS system
├── docker-compose.yml
└── README.md
```

---

## 🎨 Key Features & Module Capabilities

1. **Home Dashboard:** Aggregates overall AI Job Readiness Score (82%), Level 2 Learner XP badges, day streaks, and quick launch modules.
2. **Code Quest:** Multi-language IDE environment (Python & JavaScript) with real-time automated test case execution, runtime execution logs, and competitive leaderboard rankings.
3. **AI Interview Coach:** Interactive mock interview simulator supporting both **Structured Mode** (preset rubrics) and **Adaptive AI Mode** (dynamic turn-by-turn follow-ups) with detailed scores for communication, technical depth, and confidence.
4. **Position AI:** Natural Language Skill-Gap Analyzer. Paste any target Job Description (JD) to extract missing skill vectors and recommended learning pathways.
5. **AI Resume Builder & ATS Scoring:** Formats resumes and calculates ATS compatibility percentages, keyword match breakdowns, and actionable formatting suggestions.
6. **Aptitude Quest:** Timed quantitative, logical reasoning, and verbal aptitude quizzes with instant per-topic score breakdown and XP awards.
7. **Big Five Personality Inventory:** 10-item OCEAN trait assessment calculating openness, conscientiousness, extraversion, agreeableness, and neuroticism scores.
8. **Document Vault:** Secure storage for resumes, certificates, and portfolio files.