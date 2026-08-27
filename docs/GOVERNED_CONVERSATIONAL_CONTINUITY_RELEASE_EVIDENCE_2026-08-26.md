# Governed Conversational Continuity — Release Evidence

Date: 2026-08-26  
Source commits: `6959804`, `fa770cb`  
Candidate revision: `military-slices-00039-kiq`  
Candidate traffic: `0%`  
Candidate tag: `continuity-rc`  
Candidate URL: <https://continuity-rc---military-slices-ztvqlzospa-uw.a.run.app/?build=fa770cb>  
Production revision: `military-slices-00001-niw`  
Production traffic: `100%`

## Disposition

An accepted governed direction now invalidates the prior acquisition horizon, refreshes Path state, removes the resolved career-direction Gate, and creates one new human-authorized Gate for the first unresolved task derived from the accepted hypothesis. The conversational model receives only the newly computed bounded horizon and the governed change receipt; it can phrase an acknowledgment and consequence but cannot select the next Gate, change state, or persist anything.

The user first explores a direction without a write. The preview shows the proposed first experiment, the questions that experiment should answer, supporting evidence, and remaining uncertainty. Only the explicit `Use this as my working direction` action invokes the existing version-bound Governor-authorized decision path.

The accepted direction is projected as the current target. A reload omits the transient acknowledgment while preserving the recomputed question and accepted target, so continuity is experienced without replaying old conversational copy.

## Falsification coverage

- Founder direction: acceptance advances to the hypothesis-specific unresolved question and never defaults to job-description or employment-stabilization copy.
- Employment direction: acceptance continues toward role/evidence uncertainty when that evidence is relevant.
- Rich input: current employment and remote, schedule, and travel preferences are retained and not re-asked.
- Direction change: a reviewed Fog Bank reorientation clears the stale accepted hypothesis and its downstream Path question before recomputation.
- Multi-Gate response: collateral human statements remain explicit facts while each Gate retains independent Governor evaluation and persistence.
- Model containment: an out-of-horizon conversational proposal fails closed to deterministic language.
- Recursive refinement: a useful natural answer to a dynamic Path Gate is accepted through the normal bounded-acquisition and Governor path, retires only that Gate, and produces a distinct next Gate.
- Insufficient answer: a too-small answer remains a zero-write clarification.
- Explicit pre-existing targets retain their established `PATH_IDENTIFIED` semantics; the new exploration state applies only after a `career-direction` decision.

## Automated results

- Pytest: `217 passed`
- Ruff: passed for `military_slices` and `tests`
- strict Mypy: passed for 15 source files
- Bandit: passed
- dependency audit: no known vulnerabilities; the local package itself is not published on PyPI
- JavaScript syntax: passed
- `git diff --check`: passed

## Hosted Gemini/ADK transaction

A fresh synthetic profile used the hosted `gemini-3.7-flash` / Google ADK runtime at a 375px viewport:

1. Veteran/service member; Navy; active duty/full-time service; separated 1–5 years ago.
2. Reviewed input stated 20 years in military information operations, existing civilian cyber-engineer employment, a remote technology-company direction serving military members and spouses, predictable hours, little travel, and work from home.
3. Gemini proposed `Technology Venture Founder / Operator`, `Remote Technology Project / Product Lead`, and `Community / Veteran Support Program Operations Manager`.
4. Opening the founder direction created zero writes and exposed a bounded first experiment plus two questions derived from the actual hypothesis.
5. Accepting it produced: `What specific operational problem do military members or spouses identify as top priority?`
6. The conversational bridge acknowledged the governed decision and explained why that foreground question followed. No job-description, initial-employment, or employment-stabilization machinery appeared.
7. The ambient current target projected `Technology Venture Founder / Operator`.
8. A natural answer advanced to `Can customer discovery be managed within a predictable remote schedule?`, proving recursive refinement and use of the already governed schedule constraint.

Exact hosted assets: `app.js?v=13`, `styles.css?v=10`.

## Mobile and accessibility evidence

| Width | Horizontal overflow | Minimum visible interactive target |
| --- | --- | --- |
| 320px | No | 48px |
| 375px | No | 44px |
| 414px | No | 44px |

The newly reconstituted foreground heading receives focus. Browser diagnostic logs were empty throughout the hosted transaction. Cloud Logging contained zero entries at severity `WARNING` or higher for `military-slices-00039-kiq` after validation.

## Hosted identity and containment

- Health: `ok`
- Model: `gemini-3.7-flash`
- Agent framework: Google ADK
- Transition pack: `2026-08-24-v2-shadow-tested`
- Domain Pack hash: `026a1508a3a2e6eb16907b2e8fc29c4f333af5c5ab908e6029903b8cbcbf9f4c`
- Domain Pack status: `LEGACY_VALID`
- External effects: disabled
- Autonomous Probe: disabled
- Store: Firestore
- Runtime service account, resources, timeout, concurrency, secrets, and environment match the prior candidate

## Defects found and corrected during falsification

1. A question-shaped Path task was normalized with `?.` and then wrapped in a second question. Task punctuation is now preserved and regression-tested.
2. The legacy acquisition matcher rejected a useful answer when orientation could not independently rediscover the active question's Slice. An explicit human statement of meaningful length is now scoped to the active dynamic Path Gate while the existing Governor, version, ownership, and persistence boundaries remain unchanged.
3. The UI projected the broader `Find civilian work` anchor after a more specific direction was accepted. It now projects the accepted governed direction first.

No evidence required a canonical HELM amendment, new authority, new policy value, new datastore, external-effect authorization, or autonomous Probe authorization.

## Remaining human gates

- Physical Android touch, keyboard, focus, and real-device rendering.
- Founder comprehension and usefulness judgment for the acknowledgment, consequence, and next question.
- Cold-user validation across founder, employment, education, relocation, and mixed directions.
- Real second-account isolation on physical devices.
- Human confirmation that accepted-direction continuity feels natural after reload and later direction changes.

The candidate is not promoted. Production remains the immediate rollback target and the human acceptance Gate remains open.
