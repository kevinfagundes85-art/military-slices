# Hackathon Compliance Ledger

Checked against the official All Things Agentic Hackathon rules on 2026-08-23.

Primary authority: <https://allthingsagentichackathon.devpost.com/rules>

State vocabulary: `YES`, `NO`, `PARTIAL`, `UNKNOWN`, `CONFLICTED`.

| Requirement | Evidence | State | Owner | Closure action |
|---|---|---:|---|---|
| Eligible adult, permitted location, internet access by Aug 3 | Official rules §3; founder attested they are not employed by a government agency | PARTIAL | Kevin | Final eligibility attestation remains human-only |
| Not a Contest Entity or household member | Official rules §3 | UNKNOWN | Kevin | Final eligibility attestation |
| Submission period | Aug 3, 2026 09:00 PT–Aug 31, 2026 17:00 PT, official rules §4 | YES | BHE | Preserve dated Git/deployment history |
| New project only | Fresh `military-slices` repository; no Veteran Slice code/schema/deployment reuse | YES | BHE | Maintain provenance and disclosure |
| One category | Collaborative Partner selected because the system guides, captures feedback, and adapts | YES | BHE | Select in Devpost draft |
| Team structure | Individual entry currently assumed | PARTIAL | Kevin | Confirm final entrant/team roster |
| Gemini 3.5+ | `gemini-3.7-flash` through Vertex AI | PARTIAL | BHE | Hosted call evidence required |
| Google agent framework | Google ADK agent and bounded tools | PARTIAL | BHE | Hosted execution evidence required |
| Google Cloud infrastructure | Cloud Run + Firestore | PARTIAL | BHE | Candidate deployment evidence required |
| Autonomous behavior beyond chat | Agent proposes structured state movement; machine-closeable timing/evidence work; adaptive decision interface | PARTIAL | BHE | Demo proof required |
| Functional/testable project | Public candidate planned at `militaryslices.com` | PARTIAL | BHE | Deploy, HTTPS, test |
| Free judge access | Anonymous first value with isolated signed session | PARTIAL | BHE | Hosted cold-browser validation |
| English | UI and submission materials are English | YES | BHE | Regression scan |
| Repository URL | GitHub/GitLab/Bitbucket URL required | UNKNOWN | Kevin/BHE | Create/publish repository or grant required private access |
| Private repo access | If private: invite `testing@devpost.com` and `cloudhackathons@google.com` | UNKNOWN | Kevin | Only if private repo chosen |
| README spin-up instructions | Root README includes local/deploy instructions | YES | BHE | Verify from clean environment |
| Architecture diagram | Mermaid diagram in README and architecture document | YES | BHE | Add rendered submission image |
| Hosted-project URL | Required if available; strongly encouraged | PARTIAL | BHE | Deploy candidate and map domain |
| Text description | Must include features, technologies, data sources, findings/learnings | PARTIAL | BHE | Complete Devpost draft |
| Demo video | Public YouTube/Vimeo, English, ≤4 minutes | UNKNOWN | Kevin | Human recording/upload gate |
| Cloud proof in demo | Show Cloud Run/Vertex/`.run.app` evidence | PARTIAL | BHE/Kevin | Prepare unedited demo sequence |
| Public demo behavior | Live agent action, database/state proof, no fake execution | PARTIAL | BHE | Hosted demo rehearsal |
| Third-party authorization/licenses | PyPI dependencies; public official occupational links; Apache-2.0 project | PARTIAL | BHE | Generate dependency/license inventory |
| AI-generated code disclosure | AI coding assistants explicitly permitted; disclose Codex assistance | YES | BHE | Include in Devpost draft |
| Prior-work disclosure | HELM methodology/lessons only; no prior proprietary code or data | YES | BHE | Include concise disclosure |
| Original ownership/IP | Fresh implementation; synthetic fixtures; no employer/government data | PARTIAL | Kevin/BHE | Final human ownership attestation |
| Demo content/IP | No third-party marks implying endorsement; public-source citations only | PARTIAL | BHE | Final screenshot/video review |
| Judging: innovation/utility 40% | Cross-domain transition decision loop and human-attention reduction | PARTIAL | BHE | Evidence in demo and submission |
| Judging: architecture 30% | Typed state, authority, concurrency, idempotency, bounded tools | PARTIAL | BHE | Tests and diagram |
| Judging: demo/readiness 30% | Public deployment, clean docs, unedited proof of action | PARTIAL | BHE/Kevin | Candidate validation and human video |
| Final Devpost submission | Binding legal attestation and irreversible submission | UNKNOWN | Kevin | Human-only final gate |

## Category decision

**Collaborative Partner** is the selected category. The product accepts messy input, asks one decision-relevant clarification, mutates a persistent governed plan, captures adjudication, and reconstitutes the next interaction around the individual. That directly matches the category language and its emphasis on transforming complex unstructured input rather than merely reading it.

## Fresh-build disclosure

Military SLICES was implemented in a new repository during the contest period. Pre-existing HELM methodology, product lessons, and experimental evidence informed design decisions. No Veteran Slice source code, routes, schemas, data, deployment, domain, or app identity were incorporated. Commodity open-source frameworks and Google services are used under their normal licenses and contest permissions.

