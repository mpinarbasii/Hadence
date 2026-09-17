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

🚧 Early foundation stage (Phase 0 / Phase 1 of the roadmap — see
[`docs/architecture.md`](docs/architecture.md) and
[`docs/domain-model.md`](docs/domain-model.md)).

## Repository layout

```
hadence/
├── backend/     FastAPI + Pydantic service, layered by domain / application / infrastructure / api
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
cp ../.env.example ../.env   # fill in real values
pytest
ruff check .
uvicorn app.api.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Tech stack

| Layer      | Choice                                  |
|------------|------------------------------------------|
| Frontend   | Next.js, TypeScript, Tailwind CSS        |
| Backend    | Python, FastAPI, Pydantic                |
| Database   | PostgreSQL                               |
| LLM        | Provider-abstracted (OpenAI / Anthropic) |

See [`docs/architecture.md`](docs/architecture.md) for the reasoning behind
these choices and the layering rules that keep the domain model independent
of any specific framework or LLM vendor.

## Contributing / working agreement

This project follows a phased roadmap (Career Evidence Foundation → GitHub
Evidence Collector → Job Intelligence → Evidence Mapping → Application
Blueprint → Application Builder → Application Workspace → Diff/Analytics →
Browser Extension). Each phase should land as a coherent, tested slice —
see `docs/architecture.md` for the full plan.
