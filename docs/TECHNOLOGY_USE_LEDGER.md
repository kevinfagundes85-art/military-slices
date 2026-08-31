# Technology-Use Ledger

This ledger distinguishes code used by the running candidate from validation tools and future work.

| Technology or source | Exact implemented use | Strongest implementation evidence | Status |
|---|---|---|---|
| Gemini 3.7 Flash | Produces typed career hypotheses and bounded language bridges only when the active flow permits a model call. | `military_slices/agent_runtime.py:201-276`, `:413-489`, `:508-573`, `:603-667` | Implemented and used by the deployed ADK configuration |
| Vertex AI | Provider route for Gemini, configured with project, location, and model environment values. Image extraction also uses the configured Vertex model in the deployed candidate. | `.env.example`; `military_slices/agent_runtime.py:211`; `military_slices/artifacts.py:191-193` | Implemented |
| Google Agent Development Kit | Creates the bounded agents, in-memory run sessions, structured output schemas, deterministic tools, and `max_llm_calls` constraints around Gemini. | `military_slices/agent_runtime.py:414-473`, `:508-573`, `:603-667` | Implemented |
| Cloud Run | Hosts the public container containing FastAPI, the static interface, and the HELM runtime. No existing production service or traffic was migrated to this release candidate. | `Dockerfile`; `MILITARY_SLICES_HOSTED_RELEASE_CANDIDATE_REPORT_2026-08-28.md`; public `.run.app` URL | Implemented and deployed release candidate |
| Firestore | Persists one canonical plan per anonymous session, preserves prior versions in a subcollection, and transactionally enforces expected-version writes. It stores state; it does not host the application. | `military_slices/store.py:85-153` | Implemented and used by deployed configuration |
| Signed anonymous session | A signed cookie binds a browser session to its plan. This provides prototype session continuity, not production user authentication. | `military_slices/security.py:53-66`; `military_slices/app.py:86`, `:917-929` | Implemented |
| FastAPI | Defines the web/API routes, cookies, uploads, history, What-If, plan projection, and export responses. | `military_slices/app.py:95-1142` | Implemented |
| Pydantic | Enforces strict schemas for state, Gates, proposals, governor decisions, receipts, and transition-plan output. | `military_slices/models.py`; `military_slices/agent_runtime.py:18-64`; `military_slices/plan.py:14-55` | Implemented |
| HTML/CSS/JavaScript | Renders the responsive input-first experience, review-before-write surface, command post, history, What-If, full plan, and export controls. | `static/index.html`; `static/app.js`; `static/styles.css` | Implemented |
| PyPDF + PDFium | Extracts text from PDFs and renders scanned PDF pages for bounded image extraction. | `military_slices/artifacts.py`; dependencies in `pyproject.toml` | Implemented |
| python-docx | Extracts text from deliberately selected DOCX artifacts. | `military_slices/artifacts.py`; dependency in `pyproject.toml` | Implemented |
| Pillow | Validates and processes supported PNG/JPEG inputs before bounded extraction. | `military_slices/artifacts.py`; dependency in `pyproject.toml` | Implemented |
| O*NET Online | Provides public occupational codes and exploration references for proposed directions. It does not establish qualification. | `military_slices/agent_runtime.py:76-117` | Implemented public evidence source |
| U.S. Bureau of Labor Statistics Occupational Outlook Handbook | Provides a public occupational exploration reference. It does not establish qualification or hiring likelihood. | `military_slices/agent_runtime.py:108-114` | Implemented public evidence source |
| Docker | Builds the non-root Python 3.12 application container used by Cloud Run. | `Dockerfile` | Implemented |
| Secret Manager | Deployment configuration references the runtime session secret without placing it in source. | README Cloud Run guidance and hosted release evidence | Implemented deployment control; secret value is not in repository |
| Pytest | Covers product, governance, artifact, plan/export, mobile projection, persistence, and adversarial regressions. | `tests/`; final validation report | Validation only |
| Ruff, Mypy, Bandit, pip-audit | Linting, strict type analysis, static security checks, and dependency vulnerability checks. | `pyproject.toml`; final validation report | Validation only |
| HELM Probe | Bounded discovery concept; autonomous execution is disabled because the cumulative governed budget/authority contract is not activated in this prototype. | `military_slices/governance.py:306-307`; `tests/test_helm_governance_contract.py:365-370`; architecture diagram | Deliberately disabled, not claimed as a running feature |
| External operational actions | No job applications, messages, benefit filings, or other outside effects are dispatched. | `military_slices/governance.py:302-303`; `tests/test_helm_governance_contract.py:181-183` | Deliberately disabled |
