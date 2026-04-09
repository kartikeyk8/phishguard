# PhishGuard — Adaptive Phishing Awareness Training Platform

A full-stack cybersecurity training platform with adaptive quizzes across Email, SMS, URL, and Voice phishing scenarios.

---

## Project Structure

```
phishing-platform/
│
├── backend/                  ← FastAPI Python backend
│   ├── main.py               ← App entry point, CORS, router registration
│   ├── config.py             ← Loads .env variables
│   ├── database.py           ← MongoDB connection + collection refs
│   ├── models/
│   │   ├── user.py           ← Pydantic user schemas
│   │   ├── question.py       ← Pydantic question schema
│   │   └── quiz.py           ← Quiz submission / result schemas
│   ├── routes/
│   │   ├── auth.py           ← POST /register, POST /login, GET /me
│   │   ├── quiz.py           ← GET /questions/{difficulty}, POST /submit
│   │   ├── report.py         ← GET /generate, GET /download (PDF)
│   │   └── analytics.py      ← GET /me (behavioral analytics)
│   ├── services/
│   │   ├── auth_service.py   ← Password hashing, JWT, user CRUD
│   │   ├── quiz_service.py   ← Adaptive scoring, level advancement
│   │   ├── analytics_service.py ← Pandas/NumPy behavioral analysis
│   │   └── report_service.py ← Report generation + ReportLab PDF
│   └── utils/
│       └── dependencies.py   ← FastAPI JWT auth dependency
│
├── frontend/                 ← Static HTML/CSS/JS frontend
│   ├── index.html            ← Login / Register page
│   ├── pages/
│   │   ├── dashboard.html    ← User dashboard (score, modules, analytics)
│   │   ├── quiz.html         ← Adaptive quiz interface
│   │   └── report.html       ← Awareness report page
│   ├── css/
│   │   ├── main.css          ← Global design system (dark theme)
│   │   └── dashboard.css     ← Dashboard-specific styles
│   └── js/
│       ├── auth.js           ← JWT helpers, apiFetch, auth guard
│       ├── dashboard.js      ← Dashboard data loading
│       ├── quiz.js           ← Quiz engine (timer, scoring, transitions)
│       └── report.js         ← Report rendering + PDF download
│
├── data/
│   └── seed_questions.py     ← MongoDB seed script (16 questions, all levels)
│
├── .env                      ← Environment variables (do not commit)
├── requirements.txt          ← Python dependencies
├── run.py                    ← One-command server startup
└── README.md
```

---

## Prerequisites

- Python 3.10+
- MongoDB running locally on port 27017 (or set `MONGO_URI` in `.env`)
- Git

---

## Setup Instructions

### 1. Clone and enter the project

```bash
git clone <your-repo-url>
cd phishing-platform
```

### 2. Create a virtual environment

```bash
python -m venv venv

# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Edit `.env` (already created) — set a strong JWT secret for production:

```
MONGO_URI=mongodb://localhost:27017
DB_NAME=phishing_platform
JWT_SECRET=replace-with-a-very-long-random-string
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
```

### 5. Seed the database

```bash
python -m data.seed_questions
```

You should see: `✅ Seeded 16 phishing questions into MongoDB.`

### 6. Start the server

```bash
python run.py
```

Server starts at: **http://localhost:8000**

### 7. Open the app

Visit: **http://localhost:8000/static/index.html**

---

## API Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register` | — | Register new user |
| POST | `/api/auth/login` | — | Login, receive JWT |
| GET | `/api/auth/me` | ✓ | Get current user profile |
| GET | `/api/quiz/questions/{difficulty}` | ✓ | Fetch quiz questions |
| POST | `/api/quiz/submit` | ✓ | Submit answers, get scored result |
| GET | `/api/analytics/me` | ✓ | Get behavioral analytics |
| GET | `/api/report/generate` | ✓ | Generate JSON awareness report |
| GET | `/api/report/download` | ✓ | Download PDF awareness report |

Interactive API docs: **http://localhost:8000/docs**

---

## Adaptive Quiz Logic

```
Beginner Quiz  ──► Score ≥ 70% ──► Intermediate Quiz
                        │
                      < 70% ──► Retry Beginner

Intermediate   ──► Score ≥ 70% ──► Advanced Quiz
                        │
                      < 70% ──► Retry Intermediate

Advanced       ──► Score ≥ 70% ──► Generate Awareness Report
                        │
                      < 70% ──► Retry Advanced
```

**Scoring:** Correct answer = +10 pts | Incorrect = −5 pts

---

## Scoring System

| Action | Points |
|--------|--------|
| Correct answer | +10 |
| Incorrect answer | −5 |
| Pass threshold | ≥ 70% accuracy |

---

## MongoDB Collections

| Collection | Key Fields |
|---|---|
| `users` | name, email, password (bcrypt), score, level |
| `phishing_questions` | type, difficulty, content, options, correct_answer, explanation |
| `quiz_results` | user_id, question_id, user_answer, correct, time_taken, score |
| `awareness_reports` | user_id, overall_score, accuracy_by_type, weakest_category, recommendations |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Database | MongoDB + PyMongo |
| Analytics | Pandas + NumPy |
| PDF Reports | ReportLab |
| Frontend | HTML5 + CSS3 + ES Modules (vanilla JS) |

---

## Development Notes

- The frontend uses native ES Modules — no build step needed.
- All API calls include `Authorization: Bearer <token>` headers via `auth.js`.
- The quiz strips `correct_answer` from questions before sending to the client.
- Behavioral analytics are computed on-the-fly with Pandas from stored `quiz_results`.
