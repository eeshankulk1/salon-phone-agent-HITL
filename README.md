# Frontdesk Assessment

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

- **Agent (`core-service/agent`)**
  - LiveKit Agents based voice assistant for the salon.
  - Stack: Deepgram STT, OpenAI LLM, Cartesia TTS, Silero VAD, Multilingual turn detection, optional LiveKit noise cancellation.
  - Primary flow:
    - Uses `search_knowledge_base` tool to query the backend knowledge base.
    - On miss, creates a Help Request in the backend, then waits for a supervisor response by subscribing to a Postgres `LISTEN/NOTIFY` channel (`help_request_updates`).
    - When an answer arrives, a text back to the cusomer is sumulate via logging.
    - The knowledge base is then updated, allowing the AI agent to get smarter.

- **Supervisor Dashboard (`supervisor-dashboard`)**
  - React UI for supervisors to view and resolve Help Requests and manage the Knowledge Base.
  - Talks to the backend at `http://localhost:8000/api`.

- **Database + Adminer (Docker)**
  - `postgres` (pgvector-enabled) and `adminer` containers are managed via `docker-compose.yml` at the repo root.
  - Database is initialized by SQL in `db/init` on first run.
  - Design philosophy is based on the fact that almost all data (besides embeddings) are relational in nature, so a local SQL option was preferred.

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
  - LiveKit (if connecting to a LiveKit server):
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

1) Clone repository and create a virtual environment for the backend:
```bash
cd core-service
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

2) Create and populate environment file at the repo root:
```bash
cd ..
cp .env.example .env
# Edit .env and set DATABASE_URL, POSTGRES_*, OPENAI_API_KEY, DEEPGRAM_API_KEY, CARTESIA_API_KEY, etc.
```

3) Start database stack from the repo root:
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
npm start
# Opens http://localhost:3000 and calls the API at http://localhost:8000/api
```

- Agent (requires Postgres + provider keys):
```bash
cd core-service
source .venv/bin/activate
python -m agent.agent         # preferred
# also supported in some environments:
python -m agent.agent console
```

---

## Useful Endpoints

- Health check: `GET http://localhost:8000/healthz`
- Help Requests:
  - `GET /api/help-requests/` with optional `?status=pending|in_progress|resolved`
  - `GET /api/help-requests/{id}`
  - `POST /api/help-requests/` (create)
  - `POST /api/help-requests/{id}/resolve` (resolve and create KB entry)
- Knowledge Base:
  - `GET /api/knowledge-base/` with optional `?q=...`
  - `GET /api/knowledge-base/{id}`
  - `POST /api/knowledge-base` (create)
  - `PUT /api/knowledge-base/{id}` (update)
  - `DELETE /api/knowledge-base/{id}` (delete)

---

## Notes

- The dashboard is hardcoded to use `http://localhost:8000/api`. If you change backend host/port, update `supervisor-dashboard/src/services/index.ts` accordingly.
- Database schemas and triggers are created from `db/init` on first container start. To reset, use scripts in `db/scripts` or recreate the volume.
- Adminer is available at `http://localhost:8080` (server: `postgres`, credentials from your `.env`). 