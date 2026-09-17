# Domain Model

## 1. Core distinction: Claim vs. Evidence vs. Requirement vs. Assessment

These four concepts are never conflated in the system:

| Concept     | Example                                               |
|-------------|--------------------------------------------------------|
| Claim       | "This person has experience with Python."             |
| Evidence    | GitHub repository `SyntheticData`, language: Python    |
| Requirement | "Python experience required" (extracted from a job)    |
| Assessment  | `Strong` — with an explanation referencing the evidence |

A **Claim** is never stored as a bare sentence. It only exists as the
human-readable surface of an `Assessment`, which is always backed by one or
more `Evidence` records, which are always backed by an `EvidenceSource`.

## 2. Entities

### CareerProfile (aggregate root)
Belongs to a `User`. Owns `Skill`, `Project`, `Experience`, `Education`,
`Certification` records.

### EvidenceSource (aggregate root, immutable once created)
```
id
source_type: resume | github | project | certificate | experience | manual | portfolio
label                # human-readable, e.g. "GitHub: SyntheticData"
uri                  # link or file reference, if applicable
raw_content_ref       # pointer to stored raw content (file, fetched README, etc.)
retrieved_at
last_verified_at
```
Immutable: if the source changes (e.g. repo updated), a new version /
re-verification event is recorded rather than mutating history silently.

### Evidence (join entity — NOT independent)
Connects a `CareerProfile` item (Skill/Project/Experience/etc.) to an
`EvidenceSource`.
```
id
subject_type: skill | project | experience | education | certification
subject_id
evidence_source_id
excerpt              # the specific part of the source that supports the subject
relevance_note        # short human/LLM-generated note on *why* this is relevant
```

### Skill / Project / Experience / Education / Certification
Standard profile entities, each `CareerProfile`-scoped. `Skill` in
particular is intentionally lightweight — its credibility comes entirely
from attached `Evidence`, not from being listed.

### Job (aggregate root, immutable original text)
```
id
title
company
raw_description       # preserved verbatim, never overwritten
source_url            # optional, if pasted from a page
created_at
```

### JobRequirement
Extracted from a `Job`, always traceable back to the source text.
```
id
job_id
text                  # normalized requirement, e.g. "Python"
requirement_type: required | preferred | responsibility | domain_signal | education | certification
source_span           # pointer/offset into raw_description this was extracted from
```

### RequirementEvidence (join entity)
Connects a `JobRequirement` to the `Evidence` candidates considered for it,
and carries the outcome.
```
id
job_requirement_id
evidence_ids: [Evidence.id]
assessment: strong | partial | weak | none | conflicting
explanation            # human-readable reasoning, generated but evidence-grounded
```

### Application (aggregate root)
```
id
career_profile_id
job_id
status
created_at
```

### ApplicationVersion (immutable snapshot)
```
id
application_id
version_number
selected_evidence_ids
selected_project_ids
generated_resume_ref
generated_cover_letter_ref
created_at
```

### ApplicationOutcome
```
id
application_id
outcome_type: no_response | rejected | interview | offer | withdrawn
recorded_at
notes
```

## 3. Relationships at a glance

```
CareerProfile
 ├── Skill ──┐
 ├── Project │
 ├── Experience ├──► Evidence ◄── EvidenceSource (provenance, immutable)
 ├── Education │
 └── Certification ┘

Job (immutable raw text)
 └── JobRequirement ──► RequirementEvidence ──► Evidence
                               │
                         Assessment + Explanation

Application ──► ApplicationVersion (immutable snapshots)
          └──► ApplicationOutcome
```

## 4. Assessment states

| State       | Meaning                                                        |
|-------------|------------------------------------------------------------------|
| Strong      | Multiple relevant, high-confidence evidence sources             |
| Partial     | Some relevant evidence, but limited depth or indirect            |
| Weak        | Tangential or low-confidence evidence only                       |
| None        | No reliable evidence found                                       |
| Conflicting | Evidence sources disagree (e.g. resume claims it, no repos show it) |

Assessments are never a single opaque numeric "match score" — the state
plus the explanation plus the linked evidence must always be inspectable
together.

## 5. What's intentionally NOT modeled yet

- Vector embeddings / semantic similarity tables (see architecture.md §6)
- Multi-tenant / team accounts
- Browser extension session state
- Job-board-specific scraping schemas (adapters come in Phase 9)
