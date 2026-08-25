# Military SLICES

**U.S. Military and Coast Guard Career Transition Planning Assistant**

Military SLICES turns incomplete transition context into one persistent, governed plan. It connects career, education, location, and résumé decisions; lets a bounded Gemini agent close machine-resolvable work; and asks the service member only for the next decision that genuinely requires them.

The installed transition runtime is `2026-08-24-v2-shadow-tested`. It separates the human objective from the next service-aware milestone and keeps the visible task horizon to one gate and no more than three tasks.

This is a fresh competition implementation created during the All Things Agentic Hackathon submission period. It does not contain Veteran Slice code, routes, schemas, deployments, or data.

## What it proves

- Typed human input becomes reviewable orientation before it becomes state.
- Deliberately selecting an artifact authorizes one bounded update; the user is not asked to authorize the same résumé twice.
- An artifact may contribute governed evidence without manufacturing the human's objective. If its desired use is unknown, the next interaction asks one routing question and keeps unrelated recommendations latent.
- Every visible task must support both the human objective and the next path milestone; relevance alone does not grant execution authority.
- Current-path readiness counts only decisions material to the declared target; it is not a master transition checklist.
- Career, Education, Location, and Your Story can be inspected without activating work or invoking Gemini.
- Historical versions are read-only. What-If branches remain signed, ephemeral hypotheses until the human explicitly promotes one.
- Temporal revalidation marks only mapped downstream assumptions, uses bounded receipt patches, and makes zero Gemini calls for freshness detection.
- Confirmed facts retain human authority and provenance.
- One shared decision can update several transition areas.
- Typed uncertainty preserves `UNKNOWN`, `PARTIAL`, and `CONFLICTED` instead of manufacturing certainty.
- Google ADK with Gemini 3.7 Flash proposes bounded career hypotheses and uses deterministic tools.
- Firestore persists one canonical state with optimistic concurrency and idempotency.
- Cloud Run hosts the public candidate.
- The next interaction is selected by the highest-value unresolved decision.

## Architecture

The submission-ready architecture diagram is available as
[`output/pdf/military-slices-architecture.pdf`](output/pdf/military-slices-architecture.pdf).

```mermaid
flowchart LR
    H[Service member] --> UI[Adaptive web interface]
    UI -->|typed input| O[Stateless orientation]
    O --> R[Human review and confirmation]
    R --> API[FastAPI on Cloud Run]
    UI -->|deliberately selected artifact| X[Safe ephemeral extraction]
    X --> API
    API --> G[Governed state transition]
    G --> ADK[Google ADK agent]
    ADK --> GEM[Gemini 3.7 Flash on Vertex AI]
    ADK --> T[Bounded deterministic tools]
    G --> FS[(Firestore canonical state)]
    FS --> P[Path-bounded projection: one gate and one to three tasks]
    P --> UI
```

The state persists. The decision determines the interface.

![Military SLICES architecture](docs/architecture.svg)

## Local setup

Prerequisites: Python 3.11+, a Google Cloud project, and Application Default Credentials for live Gemini/Firestore use.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn military_slices.app:app --reload --port 8080
```

For a deterministic local run without cloud writes, keep:

```text
MILITARY_SLICES_STORE=memory
MILITARY_SLICES_AGENT=deterministic
```

Open `http://127.0.0.1:8080`.

## Tests

```bash
pytest
ruff check .
mypy military_slices
bandit -r military_slices
pip-audit
```

## Deploy to Cloud Run

```bash
gcloud run deploy military-slices \
  --source . \
  --region us-west1 \
  --service-account military-slices-runtime@YOUR_PROJECT.iam.gserviceaccount.com \
  --allow-unauthenticated \
  --set-env-vars MILITARY_SLICES_ENV=production,MILITARY_SLICES_STORE=firestore,MILITARY_SLICES_COOKIE_SECURE=true,MILITARY_SLICES_AGENT=adk,GOOGLE_GENAI_USE_VERTEXAI=true,GOOGLE_CLOUD_PROJECT=YOUR_PROJECT,GOOGLE_CLOUD_LOCATION=global,MILITARY_SLICES_MODEL=gemini-3.7-flash \
  --set-secrets MILITARY_SLICES_SESSION_SECRET=military-slices-session-secret:latest
```

Grant the runtime service account Firestore User, Vertex AI User, and Secret Manager Secret Accessor for the named secret.

## Data and authority boundary

- Unconfirmed typed orientation is not written.
- Deliberately selecting a supported artifact is the authorization to use it for the current plan update; no redundant confirmation follows.
- Raw uploaded bytes are ephemeral and are never written to Firestore.
- The full extracted artifact is not persisted; only decision-relevant statements survive deterministic orientation.
- The durable cross-service path and source manifest live in `military_slices/data/`; volatile program rules are not treated as timeless truth and must be refreshed from an authoritative source when they become path-critical.
- Model output is a proposal, never self-authenticating truth.
- Durable state contains conclusions, provenance, decisions, and minimal feedback—not hidden model reasoning.
- Lenses inspect canonical state; History inspects prior canonical state; What-If creates hypothetical state. Only explicit governed promotion changes canonical truth.
- This product provides transition planning, not legal, medical, financial, clearance, benefits, or employment guarantees.

## Competition technology

- Gemini 3.7 Flash through Vertex AI
- Google Agent Development Kit (ADK)
- Cloud Run
- Firestore

See [docs/HACKATHON_COMPLIANCE.md](docs/HACKATHON_COMPLIANCE.md), [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/RELEASE_EVIDENCE_2026-08-23.md](docs/RELEASE_EVIDENCE_2026-08-23.md), and [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md).

## License

Apache-2.0. Third-party packages retain their respective licenses.
