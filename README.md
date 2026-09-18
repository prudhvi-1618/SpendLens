# SpendLens — Gmail Spend Intelligence

## What it does
SpendLens is an intelligent personal finance tracker that automatically connects to your Gmail and identifies your spending habits. It uses Google's Gemini AI to extract structured financial transactions from your inbox, classifying purchases, detecting anomalies, and identifying recurring subscriptions. The platform offers a beautiful, responsive dashboard to help you gain complete control over your finances with zero manual data entry.

## Architecture
```mermaid
graph TD
    Gmail("Gmail API")
    FastAPI("FastAPI (Backend)")
    DB[("PostgreSQL")]
    Agent("LangGraph Agent<br>& Spend Profiler")
    Gemini("Gemini AI")
    UI("React UI<br>(Dashboard)")

    FastAPI -- "OAuth 2.0 (ReadOnly)" --> Gmail
    Gmail --> FastAPI
    FastAPI --> DB
    FastAPI --> Agent
    Agent -- "AI Extraction" --> Gemini
    Gemini --> Agent
    Agent --> UI
```

## Tech stack table
| Layer | Technology |
|---|---|
| **Backend** | FastAPI, Python 3.11 |
| **Frontend** | React 18, Vite, Tailwind CSS, Recharts |
| **AI / Agent** | Google Gemini (1.5-flash), LangGraph, LangChain |
| **Database** | PostgreSQL, SQLAlchemy 2.0, Alembic |
| **Auth** | Google OAuth 2.0 (gmail.readonly) |

## Local setup
```bash
# 1. Clone the repository and enter the directory
git clone <repository_url>
cd SpendLens

# 2. Setup the backend
cd backend
cp .env.example .env
# Edit .env and fill in your GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GEMINI_API_KEY, and SECRET_KEY
docker-compose up -d
python -m venv venv
source venv/bin/activate  # Or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload

# 3. Setup the frontend
cd ../frontend
npm install
npm run dev
```

## Environment variables
| Variable | Description | Example Value |
|---|---|---|
| `GOOGLE_CLIENT_ID` | OAuth Client ID from Google Cloud Console | `123-abc.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | OAuth Client Secret | `GOCSPX-xyz123` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://postgres:postgres@localhost:5432/spendlens` |
| `FRONTEND_URL` | URL of the frontend application for CORS | `http://localhost:5173` |
| `SECRET_KEY` | 32 url-safe base64-encoded bytes for Fernet token encryption | `a_32_byte_base64_encoded_string=` |
| `GEMINI_API_KEY` | API Key for Google Gemini | `AIzaSy...` |
| `VITE_API_URL` | Base URL of the backend API | `http://localhost:8000` |

## AI components
- **LangGraph**: Orchestrates the extraction pipeline into a state graph consisting of steps: fetch unprocessed emails, run AI extraction in batches, validate and store structured JSON, and perform anomaly detection.
- **Gemini**: Handles the heavy lifting of reading unstructured email bodies and outputting structured JSON with fields like merchant, amount, category, and date. Also generates the brief insight summary on the dashboard.
- **LangChain**: Used specifically for the spend profiler chain, pulling aggregate data from PostgreSQL and piping it into a prompt template for Gemini to summarize.
- **Anomaly Detection**: Pure Python logic applied after extraction that flags transactions based on a 90-day rolling average (e.g., amount spikes, completely new expensive merchants, or subscription lapses).

## Key design decisions
- **Token Encryption**: OAuth tokens are symmetrically encrypted at rest in PostgreSQL using a Fernet key derived from `SECRET_KEY`.
- **Confidence Threshold**: Transactions with a Gemini confidence score below `0.72` are ignored to prevent pollution of the user's ledger with false positives.
- **`gmail.readonly` Scope Only**: The application requests absolute minimum permissions to ensure user trust; it cannot send, delete, or modify emails.
- **Email Drill-down**: Anomalies and transactions store the original `gmail_message_id`, enabling deep-links directly back into the user's Gmail inbox for verification.
- **90-Day Rolling Window**: The spend profiler and anomaly detection systems only baseline off the last 90 days to ensure insights are highly relevant and resilient to stale historic data.
