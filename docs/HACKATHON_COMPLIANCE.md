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
| Gemini 3.5+ | Hosted `gemini-3.7-flash` execution through Vertex AI; release-candidate logs record two model turns | YES | BHE | Preserve release evidence |
| Google agent framework | Hosted Google ADK agent used four bounded tool calls in the release-candidate proof | YES | BHE | Preserve release evidence |
| Google Cloud infrastructure | Cloud Run revision `military-slices-00006-yes`; Firestore collection `military_slices_profiles` | YES | BHE | Preserve release evidence |
| Autonomous behavior beyond chat | Agent proposes structured state movement, calls bounded tools, and reconstitutes the next decision | YES | BHE | Show in demo |
| Functional/testable project | Zero-traffic HTTPS release candidate is operational; canonical domain is intentionally unmapped | PARTIAL | BHE/Kevin | Human release/domain gate |
| Free judge access | Anonymous first value with isolated signed sessions passed hosted cold-browser checks | YES | BHE | Confirm after domain cutover |
| English | UI and submission materials are English | YES | BHE | Regression scan |
| Repository URL | GitHub/GitLab/Bitbucket URL required | UNKNOWN | Kevin/BHE | Create/publish repository or grant required private access |
| Private repo access | If private: invite `testing@devpost.com` and `cloudhackathons@google.com` | UNKNOWN | Kevin | Only if private repo chosen |
| README spin-up instructions | Root README includes local/deploy instructions | YES | BHE | Verify from clean environment |
| Architecture diagram | Mermaid diagram in README and architecture document | YES | BHE | Add rendered submission image |
| Hosted-project URL | Release candidate exists; `militaryslices.com` is purchased but not mapped | PARTIAL | BHE/Kevin | Human release/domain gate |
| Text description | Draft includes features, technologies, data sources, findings, and learnings | YES | BHE | Paste/review in Devpost |
| Demo video | Public YouTube/Vimeo, English, ≤4 minutes | UNKNOWN | Kevin | Human recording/upload gate |
| Cloud proof in demo | Exact Cloud Run, Vertex, model/tool, and Firestore evidence is captured | YES | BHE/Kevin | Show in unedited recording |
| Public demo behavior | Hosted agent action, Firestore continuity, rejection, and reload were exercised | YES | BHE | Repeat after domain cutover |
| Third-party authorization/licenses | PyPI dependencies; public official occupational links; Apache-2.0 project | PARTIAL | BHE | Generate dependency/license inventory |
| AI-generated code disclosure | AI coding assistants explicitly permitted; disclose Codex assistance | YES | BHE | Include in Devpost draft |
| Prior-work disclosure | HELM methodology/lessons only; no prior proprietary code or data | YES | BHE | Include concise disclosure |
| Original ownership/IP | Fresh implementation; synthetic fixtures; no employer/government data | PARTIAL | Kevin/BHE | Final human ownership attestation |
| Demo content/IP | No third-party marks implying endorsement; public-source citations only | PARTIAL | BHE | Final screenshot/video review |
| Judging: innovation/utility 40% | Cross-domain transition decision loop and human-attention reduction | PARTIAL | BHE | Evidence in demo and submission |
| Judging: architecture 30% | Typed state, authority, concurrency, HTTP idempotency, bounded tools, and diagram | YES | BHE | Present clearly |
| Judging: demo/readiness 30% | Green zero-traffic candidate and clean docs; video/domain remain human gates | PARTIAL | BHE/Kevin | Domain, rehearsal, video |
| Final Devpost submission | Binding legal attestation and irreversible submission | UNKNOWN | Kevin | Human-only final gate |

## Category decision

**Collaborative Partner** is the selected category. The product accepts messy input, asks one decision-relevant clarification, mutates a persistent governed plan, captures adjudication, and reconstitutes the next interaction around the individual. That directly matches the category language and its emphasis on transforming complex unstructured input rather than merely reading it.

## Fresh-build disclosure

Military SLICES was implemented in a new repository during the contest period. Pre-existing HELM methodology, product lessons, and experimental evidence informed design decisions. No Veteran Slice source code, routes, schemas, data, deployment, domain, or app identity were incorporated. Commodity open-source frameworks and Google services are used under their normal licenses and contest permissions.
