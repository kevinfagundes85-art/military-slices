# Hackathon Compliance Ledger

Checked against the official All Things Agentic Hackathon rules on 2026-08-28.

Primary authority: <https://allthingsagentichackathon.devpost.com/rules>

State vocabulary: `YES`, `NO`, `PARTIAL`, `UNKNOWN`, `CONFLICTED`.

| Requirement | Evidence | State | Owner | Closure action |
|---|---|---:|---|---|
| Eligible adult, permitted location, internet access by Aug 3 | Official rules §3 | PARTIAL | Kevin | Make final eligibility attestation |
| Not a Contest Entity/household member; no government-agency employment conflict | Official rules §3 | UNKNOWN | Kevin | Make final eligibility and conflict attestation |
| Submission deadline | Aug 31, 2026 at 5:00 PM PT, official rules §4 | YES | Kevin | Submit before deadline |
| New project only | Fresh repository; prior methodology disclosed; no Veteran Slice implementation reused | YES | BHE | Preserve provenance |
| One category | Collaborative Partner | YES | Kevin | Select in Devpost |
| Team structure | Individual entry currently assumed | PARTIAL | Kevin | Confirm entrant/team roster |
| Gemini 3.5+ | `gemini-3.7-flash` through Vertex AI | YES | BHE | Show runtime proof |
| Google agent framework | Google ADK bounded agent runtime | YES | BHE | Show in demo and repository |
| Google Cloud infrastructure | Cloud Run revision `military-slices-00047-doz`; Firestore canonical state | YES | BHE | Preserve evidence |
| Beyond a standard chat loop | Structured plan mutation, persistent state, bounded tools, re-entry, and changed-reality handling | YES | BHE | Demonstrate live |
| Functional/testable project | Public HTTPS tagged candidate validated on desktop and Android-width viewport | YES | BHE | Keep tag live through judging |
| Free judge access | Anonymous isolated session requires no paid account or credentials | YES | BHE | Recheck before submission |
| English | App and materials are English | YES | BHE | Final visual review |
| Repository URL | GitHub/GitLab/Bitbucket URL required | UNKNOWN | Kevin | Publish repository or choose private access |
| Private repository access | If private, grant `testing@devpost.com` and `cloudhackathons@google.com` | UNKNOWN | Kevin | Apply only if private |
| README spin-up instructions | Root README includes local and cloud setup | YES | BHE | Final link check |
| Architecture diagram | README and architecture artifact | YES | BHE | Export a clear image for submission |
| Hosted-project URL | Public zero-traffic tagged Cloud Run candidate | YES | BHE | Use candidate URL; custom domain optional |
| Text description | Features, stack, sources, findings, and learnings drafted | YES | BHE | Human review and paste |
| Demo video | Public YouTube/Vimeo, English, no longer than four minutes | UNKNOWN | Kevin | Record and upload at Human Gate |
| Cloud proof in video | Script includes `.run.app`, Cloud Run, Firestore, and Vertex proof | YES | BHE/Kevin | Capture in unedited recording |
| Third-party authorization/licenses | PyPI dependencies and public official evidence sources | PARTIAL | BHE/Kevin | Preserve dependency/license inventory and attest |
| AI-generated code disclosure | Codex assistance explicitly disclosed | YES | BHE | Keep disclosure |
| Prior-work disclosure | HELM methodology/lessons disclosed; no prior implementation reused | YES | BHE | Keep disclosure |
| Original ownership/IP | Fresh implementation and synthetic fixtures | PARTIAL | Kevin | Final ownership attestation |
| Demo content/IP | Synthetic inputs and no unauthorized biography or endorsement claims | YES | BHE/Kevin | Final recording review |
| Innovation & operational utility (40%) | Connected plan, messy input, persistent mutation, human-attention reduction | YES | BHE | Make action visible in demo |
| Architectural discipline & stack (30%) | Typed state, bounded agent/tooling, authority separation, Firestore, failure-safe fallback | YES | BHE | Show diagram and logs |
| Demo & production readiness (30%) | Hosted candidate and script ready; video remains open | PARTIAL | Kevin | Record and upload video |
| Final Devpost submission | Binding legal attestation and irreversible submission | UNKNOWN | Kevin | Human-only final gate |

## Category decision

**Collaborative Partner** is selected. The system ingests messy input, asks bounded clarifying questions, mutates a persistent plan, captures feedback, and adapts to the user's changing intent. This aligns directly with the category definition in the official rules.

## Fresh-build disclosure

Military SLICES was implemented in a new repository during the contest period. Pre-existing HELM methodology, product lessons, and experimental evidence informed design decisions. No Veteran Slice source code, routes, schemas, data, deployment, domain, or app identity were incorporated. Commodity open-source frameworks and Google services are used under their normal licenses and contest permissions.

## Remaining Human Gates

1. Confirm eligibility, conflict, ownership, and final entrant/team roster.
2. Choose public repository or grant the required reviewers access to a private repository.
3. Record and publicly upload the no-longer-than-four-minute English demo.
4. Review the final Devpost entry and perform the irreversible submission.
