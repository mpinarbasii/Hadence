# Hadence

**Your career, backed by evidence.**

Hadence is an **Application Intelligence Workspace** — a system that builds a
persistent, structured representation of a person's professional evidence
(the *Career Evidence Graph*), then uses that evidence to understand job
postings and construct truthful, well-targeted applications.

Hadence is deliberately **not**:

- a CV/ATS keyword scorer
- a generic "ChatGPT wrapper" for resumes
- a job-board scraper

## Core principle

> **Evidence > keywords. Truthful representation > optimization tricks.**

Hadence never invents experience because a job description asks for it. If
there is no reliable evidence for a skill, the system says so explicitly.

## Status

🚧 Early foundation stage — Career Evidence Foundation with PostgreSQL
persistence is being implemented. See [`docs/architecture.md`](docs/architecture.md)
and [`docs/domain-model.md`](docs/domain-model.md).

## Repository layout

```
hadence/
├── backend/     FastAPI service, layered by domain / application / infrastructure / api
├── frontend/    Next.js + TypeScript + Tailwind CSS
└── docs/        Architecture and domain-model documentation
```

## Local development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp ../.env.example ../.env
alembic upgrade head
pytest
ruff check .

To run the optional Postgres integration test suite, set `TEST_DATABASE_URL`
to a separate test database (for example the `hadence_test` database) and
run `pytest tests/test_postgres_repository.py`.


uvicorn app.api.main:app --reload
```

On Windows PowerShell, activate with:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks scripts in the current session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Tech stack

| Layer      | Choice |
|------------|--------|
| Frontend   | Next.js, TypeScript, Tailwind CSS |
| Backend    | Python, FastAPI, Pydantic |
| Database   | PostgreSQL, SQLAlchemy, Alembic |
| LLM        | Provider-abstracted (OpenAI / Anthropic) |

## First persistent workflow

The first real vertical slice is:

```text
Profile
  ↓
Skill / Project / Experience
  ↓
EvidenceSource
  ↓
Evidence
  ↓
PostgreSQL
```

The next phases build GitHub evidence collection, Job Intelligence, Evidence
Mapping, Application Blueprint, Application Builder, Application Workspace,
Diff/Analytics, and the browser extension on top of this foundation.
