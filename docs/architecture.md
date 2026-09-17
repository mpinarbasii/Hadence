# Architecture

## 1. Goals

Hadence's architecture is optimized for:

1. Correct domain modeling (evidence, claims, requirements, and
   assessments are distinct concepts — see `domain-model.md`)
2. Clear separation of concerns
3. Testability
4. Extendability (new evidence sources, new LLM providers, new job-source
   adapters should be addable without touching the domain layer)
5. Explicit data provenance
6. Avoiding premature complexity (no microservices, no event bus, no
   vector DB until there's a concrete requirement for one)

## 2. High-level layout

```
backend/app/
├── domain/            # Entities, value objects, domain services.
│                       # No FastAPI, no SQLAlchemy, no LLM SDKs here.
├── application/        # Use cases / orchestration. Talks to domain +
│                       # infrastructure via interfaces (ports).
├── infrastructure/
│   ├── db/             # SQLAlchemy models, repositories (implements
│   │                    # domain repository interfaces)
│   └── llm/             # LLMProvider interface + OpenAIProvider /
│                        # AnthropicProvider implementations
└── api/                # FastAPI routers, request/response schemas
                         # (Pydantic), dependency wiring
```

**Dependency rule:** `domain` depends on nothing else in this codebase.
`application` depends on `domain` only, through interfaces. `infrastructure`
implements those interfaces. `api` wires everything together and is the only
layer that knows about HTTP.

This means: swapping OpenAI for Anthropic, or Postgres for a different
database, should never require changes to `domain/` or `application/`.

## 3. Why this stack

- **FastAPI + Pydantic**: async-friendly, strong typing/validation that maps
  cleanly onto the domain model, good OpenAPI generation for the eventual
  frontend/extension consumers.
- **PostgreSQL**: relational data (evidence graph, job requirements,
  applications) is fundamentally relational. No vector search is introduced
  until a concrete semantic-search requirement exists (see §6).
- **Next.js + TypeScript + Tailwind**: server components for
  data-heavy views (evidence graph, job requirement breakdown), client
  components for interactive editing.

## 4. LLM provider abstraction

```
domain/ports/llm_provider.py      # Protocol/ABC: LLMProvider
infrastructure/llm/openai_provider.py
infrastructure/llm/anthropic_provider.py
```

The `application` layer depends only on the `LLMProvider` interface (e.g. a
method like `extract_job_structure(raw_text: str) -> JobStructure`). LLMs are
used for **interpretation** (extracting structure from unstructured text,
evaluating evidence relevance, drafting explanations) — never for
deterministic operations like DB filtering, GitHub API calls, or validation,
which stay as plain code.

## 5. Data provenance

Every evidence record must be traceable to an `EvidenceSource` with a
`source_type` (resume, github, project, certificate, experience, manual,
portfolio), and must be able to answer:

- Where did this come from?
- What exactly supports it?
- When was it last verified?
- Can the user inspect the source?

See `domain-model.md` §"EvidenceSource" for the schema.

## 6. Explicitly deferred (do not build yet)

- Microservices / service mesh
- Distributed event bus
- Vector database / embeddings search — only once semantic matching between
  free-text job requirements and evidence becomes a real bottleneck for
  keyword/LLM-based matching
- Multi-agent orchestration frameworks
- Browser extension backend (Phase 9)

## 7. Testing strategy

- `domain/`: pure unit tests, no mocking needed (no I/O).
- `application/`: unit tests with fake/in-memory implementations of the
  repository and LLM provider interfaces.
- `infrastructure/db/`: integration tests against a real (test) Postgres
  instance or `sqlite`-backed test DB for speed, migration tests via
  Alembic.
- `api/`: FastAPI `TestClient` request/response tests.
- `frontend/`: component tests + a small number of end-to-end flows.

## 8. Roadmap phases (see root README for full detail)

0. Repository & architecture foundation (this document)
1. Career Evidence Foundation — profile, skills, projects, experience,
   education, certifications, evidence sources, with real relationships
2. GitHub Evidence Collector
3. Job Intelligence (structured extraction from pasted job descriptions)
4. Evidence Mapping (requirement → evidence → assessment → explanation)
5. Application Blueprint
6. Application Builder
7. Application Workspace (tracking)
8. Application Diff & Analytics
9. Browser Extension
