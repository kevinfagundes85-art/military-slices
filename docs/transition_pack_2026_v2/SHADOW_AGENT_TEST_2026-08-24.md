# Military SLICES Path-Bounded Shadow-Agent Test — 24 August 2026

## Scope

This is an independent shadow-agent simulation of the research pack and HELM path-bounded contract. It is **not** an execution of the BHE/Gemini runtime. The test used the pack as the governing policy and fresh official service sources as external evidence.

The goal was to answer one question: **does the path constraint keep a capable agent working toward a bounded target instead of activating the entire transition universe?**

## Result

**PASS WITH CORRECTIONS.** The path constraint materially reduces activation breadth and keeps the user-visible workload to 1 primary gate and 1–3 tasks. The test exposed one architectural ambiguity and two service-freshness gaps, all corrected in v2 of the pack.

### Correction 1 — human objective vs. process milestone

The original pack used `target_state` for canonical path milestones such as `CAPSTONE_READY`. That can accidentally make process completion the objective. HELM needs two anchors:

- `human_anchor`: the user-declared outcome;
- `path_target_state`: the next bounded path milestone.

Tasks must map to both. If the human anchor is unknown, establishing it becomes the only active objective.

### Correction 2 — Coast Guard retirement early-start nuance

Current Coast Guard TAP guidance requires the transition process 365 days prior, while current PPC Separations guidance states members may begin one year before separation or two years before retirement. The v2 overlay now distinguishes the early retirement opportunity from the mandatory gate.

### Correction 3 — 2026 DAF SkillBridge volatility

DAF changed Air Force and Space Force SkillBridge maximum participation and approval authority effective 31 March 2026, with rank-dependent limits. The durable path should not hard-code those details; when SkillBridge becomes active, the resolver must query current DAF policy.

## Scenario results

### 1. Army — normal ETS, 17 months out, civilian employment direction unclear

**Human anchor:** establish a viable civilian-employment direction before required transition milestones.

**Active tasks:**
1. Begin Army TAP/self-assessment and IIC.
2. Complete/prepare Pre-Separation Counseling within the service timeline.
3. Establish broad employment direction sufficiently to choose the next track.

**Primary gate:** Which broad post-service direction should govern the next planning step: employment, education/training, entrepreneurship, continued service, or still undecided?

**Suppressed:** resume rewriting, benefits shopping, job listings, relocation, medical/claim details.

**Verdict:** PASS.

### 2. Navy — 10 months out, resume uploaded for a declared program-management role

**Human anchor:** make the resume submission-ready for the declared role.

**Active tasks:**
1. Translate grounded military evidence into civilian role evidence.
2. Identify role-relevant evidence gaps.
3. Produce/validate the resume against the declared target.

**Primary gate:** the single highest-value missing evidence item needed for the target resume.

**Suppressed:** unrelated cyber/intelligence job recommendations despite the resume containing those skills.

**Verdict:** PASS. This is the exact “resume uploaded → here are three jobs” failure the path constraint prevents.

### 3. Marine Corps — 13 months from EAS, education-first target

**Human anchor:** choose and prepare an education path for post-EAS transition.

**Active tasks:**
1. Complete/prepare TRS in the 14–12 month service window.
2. Define the education outcome enough to evaluate programs.
3. Establish the financial/timing baseline necessary for that route.

**Primary gate:** What post-service education outcome is the Marine pursuing?

**Suppressed:** immediate job search, unrelated resume recommendations, broad benefits catalog.

**Verdict:** PASS. Service terminology and sequence remain distinct without creating a separate architecture.

### 4. Air Force — 5 months out, SkillBridge is explicitly on path

**Human anchor:** determine whether an identified SkillBridge plan is executable before DOS.

**Active tasks:**
1. Validate current DAF SkillBridge eligibility/timing.
2. Resolve rank-dependent participation duration and approval authority from current policy.
3. Stage the approval path if feasible.

**Primary gate:** rank/grade if not already known, because 2026 DAF policy makes it outcome-controlling.

**Suppressed:** unrelated transition benefits and career recommendations.

**Verdict:** PASS after fresh-source lookup. This exposed the need to mark DAF SkillBridge as volatile.

### 5. Space Force — 5 months out, SkillBridge on path

**Human anchor:** same as Air Force scenario.

**Behavior:** shared DAF TAP infrastructure is reused, but the current USSF SkillBridge category/approval rules are queried and applied rather than inventing a separate transition bureaucracy.

**Verdict:** PASS.

### 6. Coast Guard — retiring 20 months out, education-first target

**Human anchor:** orient the retirement path toward post-service education.

**Active tasks:**
1. Begin early retirement transition planning under current Coast Guard/PPC guidance.
2. Establish education target and working retirement date.
3. Prepare for the mandatory 365-day TAP gate rather than activating late-stage tasks.

**Primary gate:** working retirement date if not already fixed.

**Suppressed:** 90-day Capstone actions, healthcare enrollment, DD-214 correction, final-out tasks.

**Verdict:** PASS after overlay correction.

### 7. Conflict — target requires relocation, family constraint blocks move

**Human anchor:** pursue the declared post-service role.

**State:** `CONFLICTED`, not `UNKNOWN`.

**Primary gate:** which constraint governs the active path: the role/location requirement or the no-move family constraint?

**Behavior:** one human authority gate; no new unrelated domains activated.

**Verdict:** PASS.

### 8. External dependency escape — defense employment target encounters ethics restriction

**Human anchor:** complete the active defense-employment path.

**Trigger:** grounded evidence indicates a post-government-employment restriction may apply to the specific target.

**Behavior:** HELM is allowed to cross the normal task boundary because the external dependency can block the active target. It should route the member to the appropriate ethics/legal authority and avoid providing legal adjudication itself. No unrelated legal topics activate.

**Verdict:** PASS.

## Overall finding

The checklist/path works best as a **constraint**, not as content. Under the tested contract, the agent consistently remained inside a 1–3 task horizon and did not promote merely relevant information into action.

The most important implementation invariant is now:

> **A task must be eligible on the current service/time path and materially advance the human anchor. Process relevance alone is insufficient.**

This is the control most likely to reduce the current front-end clutter without reducing backend capability.
