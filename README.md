# LiveKit Salon Agent

Monorepo containing:
- Core backend service (FastAPI) and the salon voice agent code in `core-service`
- Supervisor dashboard (React) in `supervisor-dashboard`
- Postgres + Adminer via Docker Compose in the repo root

---

## Architecture

- **Core Service (`core-service`)**
  - FastAPI app exposes REST endpoints under `/api` for managing Help Requests and the Knowledge Base.
  - Uses SQLAlchemy with PostgreSQL (pgvector enabled) for storage.
  - Loads environment from the repo root `.env`.
  - Default server: `http://localhost:8000` with CORS allowed for `http://localhost:3000` (and `http://localhost:5173`).

- **Agent (`agent`)**
  - LiveKit Agents based voice assistant for a salon (named Beauty Palace).
  - Stack: Deepgram STT, OpenAI LLM, Cartesia TTS, Silero VAD, Multilingual turn detection, optional LiveKit noise cancellation.
  - Primary flow:
    - Uses `search_knowledge_base` tool to query the backend knowledge base.
    - On miss, creates a Help Request in the backend, logging a followup that in production would be sent as a text to the supervisor. Notifies the user the question has been escalated.
    - When an answer arrives, a text back to the cusomer is sumulate via logging, as well as a record in followups db.
    - The knowledge base is then updated, allowing the AI agent to get smarter.

- **Supervisor Dashboard (`supervisor-dashboard`)**
  - React UI for supervisors to view and resolve Help Requests and manage the Knowledge Base.
  - Supports cancellation of help requests, updating of knowledge base, and creating new Knowledge Base items without a help request.
  - Talks to the backend at `http://localhost:8000/api`.

- **Database + Adminer (Docker)**
  - `postgres` (pgvector-enabled), `expiry-job` and `adminer` containers are managed via `docker-compose.yml` at the repo root.
  - Database is initialized by SQL in `db/init` on first run.
  - Sidecar is deployed through docker for CRON job that updates expired help requests.
  - Design philosophy is based on the fact that almost all data (besides embeddings) are relational in nature, so a local SQL option was preferred (with a vector system for embeddings).

---

## Environment Variables

Copy `.env.example` from the repo root to `.env` and fill in values:

- Backend / Core
  - `DATABASE_URL` (required): e.g. `postgresql+psycopg2://POSTGRES_USER:POSTGRES_PASSWORD@localhost:DB_PORT/POSTGRES_DB`
  - `API_HOST` (default `0.0.0.0`)
  - `API_PORT` (default `8000`)
  - `CORS_ORIGINS` (default `http://localhost:3000,http://localhost:5173`)

- Docker / Postgres
  - `POSTGRES_USER`
  - `POSTGRES_PASSWORD`
  - `POSTGRES_DB`
  - `DB_PORT` (host port to bind Postgres; compose maps `${DB_PORT}:5432`)

- Agent / AI Providers
  - `OPENAI_API_KEY` (OpenAI)
  - `DEEPGRAM_API_KEY` (STT)
  - `CARTESIA_API_KEY` (TTS)
  - LiveKit:
    - `LIVEKIT_URL`
    - `LIVEKIT_API_KEY`
    - `LIVEKIT_API_SECRET`

Note: The backend and the agent both read `.env` from the repo root. Ensure `DATABASE_URL` is correct and reachable from your machine (and from inside the agent if running separately).

---

## Prerequisites

- Python 3.10+ (3.11 recommended)
- Node.js 18+ and npm
- Docker Desktop (or Docker Engine + docker compose plugin)

---

## Setup

1) Clone repository and create a virtual environment. For simplicity, create this in the root since both `/agent` and `/core-service` will use it:
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

2) Create and populate environment file at the repo root:
```bash
cp .env.example .env
# Edit .env and set DATABASE_URL, POSTGRES_*, OPENAI_API_KEY, DEEPGRAM_API_KEY, CARTESIA_API_KEY, etc.
```

3) Start database stack from the repo root. The database is needed for both the agent and the backend:
```bash
docker compose up -d
# Postgres: localhost:${DB_PORT}  |  Adminer: http://localhost:8080
```

4) Install dashboard dependencies:
```bash
cd supervisor-dashboard
npm install
cd ..
```

5) OptionalL install phone interface dependencies:
```bash
cd mobile
npm install
cd ..
```
---

## Running the apps

- Backend API (required for the dashboard):
```bash
cd core-service
source .venv/bin/activate    # if not already active
python main.py               # or: uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- Supervisor Dashboard (requires backend running):
```bash
cd supervisor-dashboard
npm run build
npm start
# Opens http://localhost:5173 and calls the API at http://localhost:8000/api
```

- Agent (requires Postgres + provider keys):
```bash
cd agent
source .venv/bin/activate
# defauly start method, requires the phone interface setup and running: 
python main.py start
# alternative option, will start the voice agent in your console, with logs for extra info:
python main.py console
```

- Mock phone call application (required for python -m agent start):
```bash
cd mobile
npm run build
npm start
# Opens http://localhost:3000 and connects with the voice agent
```

---

## Notes

- The dashboard has backup endpoints hardcoded to use `http://localhost:8000/api`. You can change backend host/port, update via env variables accordingly.
- Database schemas and triggers are created from `db/init` on first container start. To reset, use scripts in `db/scripts` or recreate the volume.
- Adminer is available at `http://localhost:8080` (server: `postgres`, credentials from your `.env`). 

## Design Notes

- One core-services folder stores functions to serve the backend and the few functions called by the voice agent. This is intentional to avoid duplicated code (in production, a seperate layer would be present in the agent folder containing the logic needed)

- Backend is intentionally loosely coupled to backend (read from same database, do not communicate directly)

- Supervisor dashboard is intentionally vaguely branded, to allow project to be applied to other topics if needed (ex: airline agent, hotel receptionist, etc.)

- Modular code is prioritized, allows for easy replacement/edits to logic when needed

- Database is designed for simplicity, while supporting expansion for a system that supports heavier traffic (ex: followups table to store pending/completed texts messages; one source of truth for stratified process) 
