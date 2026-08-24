# Service Terminology Matrix — Military SLICES 2026

**Research date:** 2026-08-24  
**Authority preference:** current service headquarters/program pages > current DoD/department policy > current installation implementation pages > historical guides/anecdotal material.

This matrix exists so Military SLICES can speak the user's service language without creating six different products.

| Concept | Army | Navy | Marine Corps | Air Force | Space Force | Coast Guard |
|---|---|---|---|---|---|---|
| Member noun | Soldier | Sailor | Marine | Airman | Guardian | Coast Guard member / Coast Guardsman |
| Transition program | Army Transition Assistance Program (TAP) | Transition Assistance Program (TAP) | Transition Readiness Program (TRP) | Department of the Air Force TAP | Department of the Air Force TAP | Transition Assistance Program (TAP) |
| Core seminar label | Army Day + DoD/DoW TAP curriculum | TAP Core Curriculum / Transition Day | Transition Readiness Seminar (TRS) | TAP Core Curriculum / Transition Day | TAP Core Curriculum / Transition Day | TAP Core Curriculum; Coast Guard page uses **DHS Transition Day** |
| Initial assessment/counseling | Self-Assessment + Individualized Initial Counseling (IIC) | Initial Counseling (IC) / self-assessment | Individual Counseling / Individualized Initial Counseling (IC) | Initial Counseling | Initial Counseling | Self-assessment + Individual Initial Counseling |
| Pre-separation | Pre-Separation Counseling | Pre-Separation Counseling | Pre-Separation Counseling Workshop | Pre-Separation Brief | Pre-Separation Brief | Pre-Separation Counseling |
| Final readiness review | Capstone | CAPSTONE | Capstone Review + Commander's Verification / Capstone Interview | Capstone | Capstone | CAPSTONE |
| Career plan artifact | Individual Transition Plan (ITP) | Individual Transition Plan (ITP) | Individual Transition Plan (ITP) | Individual Transition Plan (ITP) | Individual Transition Plan (ITP) | Individual Transition Plan (ITP) |
| Readiness standard | Career Readiness Standards (CRS) | Career Readiness Standards (CRS) | Career Readiness Standards (CRS) | Career Readiness Standards (CRS) | Career Readiness Standards (CRS) | Career Readiness Standards (CRS) |
| Primary local office | TAP Center / Transition Center; Retirement Services Officer (RSO) for retirement | Fleet and Family Support Center (FFSC), Command Career Counselor (CCC), transition counselor | Transition Office / TRP staff; Unit Transition Coordinator (UTC); P&PD ecosystem | Military & Family Readiness Center (M&FRC) | Military & Family Readiness Center (M&FRC) | Transition/Relocation Manager (TRM) at HSWL Regional Practice; SPO or Command may support pre-separation |
| Common separation date term | ETS; REFRAD; retirement date | EAOS; resignation; retirement date | EAS; retirement date | Date of Separation (DOS); retirement | Date of Separation (DOS); retirement | separation / retirement date |
| Employment/career bridge program | Army Career Skills Program (CSP) and current DoW SkillBridge process; 2026 Army routes CSP/SB through IPPS-A | SkillBridge | SkillBridge | SkillBridge | SkillBridge | SkillBridge |
| Personnel/admin ecosystem examples | IPPS-A; Soldier Talent Profile; Transition Center | MyNavy HR; NSIPS; MyNavy Portal; NPPSC/TSC processes | IPAC; S-1; Career Planner; DMO/TMO | myFSS / personnel center processes; M&FRC | DAF personnel processes; M&FRC | SPO; PPC/PSC; Work-Life / HSWL |
| Service-specific occupation vocabulary | MOS | Rating / NEC / officer designator | MOS | AFSC | Space Force specialty / career field; use current DAF/USSF source language where available | Rating |

## Normalization rule for HELM

Internally, normalize to common concepts such as:

- `member_type`
- `service`
- `component`
- `transition_date`
- `separation_type`
- `current_timeline_window`
- `current_task`
- `current_gate`
- `service_term_display`

Externally, render service-specific language.

Example:

```text
canonical concept: transition_date
Army display: ETS / retirement date / REFRAD date as applicable
Navy display: EAOS / resignation / retirement date as applicable
Marine display: EAS / retirement date
DAF display: DOS / retirement date
USCG display: separation / retirement date
```

Do **not** force users to learn another service's acronyms.

## Common federal baseline

Across the services, the current common transition structure is broadly:

1. self-assessment / initial counseling;
2. pre-separation counseling;
3. core transition curriculum;
4. optional/required two-day tracks based on need/tier;
5. Career Readiness Standards / ITP work;
6. Capstone no later than 90 days before transition.

The current DoD instruction is DoDI 1332.35, Change 1 dated 29 July 2025. Current service pages generally require initiation no later than 365 days before separation/retirement for covered members, with earlier recommended windows depending on service and retirement status.

## Service-specific differences that matter to the product

### Army

- Retiring Soldiers can begin TAP as early as 24 months; normal separations as early as 18 months; required start is no later than 365 days.
- Army's recommended sequence includes IIC/self-assessment, pre-separation counseling, Army Day, DOL employment content, VA content, and Capstone.
- Army career-transition execution now includes a 2026 change routing Career Skills Program and SkillBridge requests through IPPS-A.
- Army retirement has a large official Soldier for Life ecosystem and current 2026 retirement planning guide/checklists.

### Navy

- MyNavy HR TAP page was verified 29 July 2026.
- Uses Initial Counseling, Pre-Separation Counseling, TAP Core Curriculum, track selection, CRS, and CAPSTONE.
- Navy-facing product language should recognize EAOS, rating/NEC/designator, FFSC, CCC, NSIPS/MyNavy HR, and Fleet Reserve/retirement processes.
- Navy official current sources supersede stale details in the user-provided 2023 retirement guide.

### Marine Corps

- Transition Readiness Program (TRP), not merely generic TAP, is the service-facing program identity.
- Current TECOM implementation language uses Individual Counseling at roughly 24–18 months before EAS, Pre-Separation Counseling Workshop at 24–18 months, TRS at 14–12 months, followed by Capstone Review and Commander's Verification.
- Product language should recognize EAS, TRS, TRP, UTC, IPAC, Career Planner, and DMO/TMO.

### Air Force

- Uses DAF TAP through the Military & Family Readiness Center.
- 2026 command fact sheet recommends initiation 18–24 months before separation/retirement and mandates no later than 365 days.
- Capstone should occur no earlier than 12 months and no later than 90 days before transition in the 2026 fact sheet.

### Space Force

- Uses the Department of the Air Force transition/readiness infrastructure.
- M&FRC resources explicitly support Airmen **and Guardians**.
- Use Guardian as the member noun, but do not invent a parallel Space Force-specific TAP workflow where DAF owns the common process.

### Coast Guard

- Current Coast Guard TAP page says eligible members begin the transition process 365 days before separation/retirement.
- Coast Guard uses **DHS Transition Day** on its current TAP page, not the DoD label used by the military departments.
- Local support language includes Transition/Relocation Manager (TRM), Health, Safety and Work-Life Regional Practice (HSWL RP), SPO, and Command.
- Coast Guard Sea Legs maintains a Departing the Service Checklist.
- Older Coast Guard toolkit text contains legacy timing language around ~180 days; treat the current TAP page plus governing current policy as the preferred authority where they conflict.

## Component/status warning

Do not assume `active duty = all users`.

Guard and Reserve applicability can depend on:

- Title 10 vs Title 32 status;
- continuous active-duty duration;
- retirement type (regular vs non-regular);
- mobilization/demobilization context;
- service-specific implementation.

Therefore `component/status` is an early path discriminator when it materially changes mandatory tasks. It should not become a giant intake section unless needed to resolve the current path.
