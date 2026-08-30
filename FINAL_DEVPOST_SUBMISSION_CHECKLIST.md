# Final Devpost Submission Checklist

Complete these actions in order. Every item is classified **HUMAN ACTION**. There is currently no engineering **BLOCKER**.

Overall submission readiness: **READY**  
Current gate classification: **HUMAN ACTION**

## 1. Publish the final repository commit — HUMAN ACTION

From the local `military-slices` repository:

```powershell
git status --short
git push origin main
git rev-parse HEAD
```

Expected before push: `git status --short` prints nothing.

After the push, open:

https://github.com/kevinfagundes85-art/military-slices

Confirm all three facts:

- repository visibility says **Public**;
- the latest commit equals the commit reported at the end of this preparation pass;
- the README begins **Military SLICES** and includes **Watch the final demo**.

If the push is rejected, stop and resolve GitHub authentication or branch protection. Do not submit an outdated repository.

## 2. Verify the final presentation — HUMAN ACTION

Open a signed-out/private browser window and play:

https://youtu.be/EwAtrtrIUiI

Confirm:

- no login or permission request blocks playback;
- title is **Military SLICES — Powered by HELM | Hackathon Demo**;
- the presentation plays through the end;
- audio is understandable and the image remains legible.

Do not replace or regenerate the video.

## 3. Open the Devpost submission form — HUMAN ACTION

Select the **Collaborative Partner** category.

Use [docs/DEVPOST_SUBMISSION_COPY.md](docs/DEVPOST_SUBMISSION_COPY.md) as the only narrative source. Paste its fields in this order:

1. Project title
2. Tagline
3. Inspiration / problem
4. What it does
5. How it works
6. How we built it
7. Technologies used
8. Challenges
9. Accomplishments
10. What we learned
11. What is next
12. Required disclosures, wherever Devpost provides an additional-details or disclosures field

Use these URLs exactly:

- Hosted project: `https://hackathon-rc---military-slices-ztvqlzospa-uw.a.run.app/`
- Source repository: `https://github.com/kevinfagundes85-art/military-slices`
- Demo video: `https://youtu.be/EwAtrtrIUiI`

Do not add unsupported claims or personal employment history.

## 4. Upload judge media — HUMAN ACTION

Upload these images in this exact order:

1. `docs/screenshots/01-front-door.png` — entry experience
2. `docs/screenshots/02-human-review.png` — review before plan write
3. `docs/screenshots/03-direction-choice.png` — bounded direction alternatives
4. `docs/screenshots/04-bundled-decisions.png` — related decisions answered together
5. `docs/screenshots/05-real-world-test.png` — direction becomes an outside-the-app action
6. `docs/screenshots/06-plan-updated-from-evidence.png` — evidence changes the relevant plan
7. `docs/screenshots/07-complete-plan-and-export.png` — complete dated plan and export
8. `docs/screenshots/08-helm-architecture.png` — judge-readable HELM architecture

Use `01-front-door.png` as the cover image unless Devpost's crop makes its title unreadable; in that case use `07-complete-plan-and-export.png`. Do not reorder the remaining images.

## 5. Complete entrant-controlled declarations — HUMAN ACTION

Read and answer the Devpost declarations yourself. Confirm only facts you personally know, including:

- entrant and team eligibility;
- team roster and participant identities;
- ownership and authority to submit;
- third-party software, service, media, and license disclosures;
- competition-period/new-project declaration;
- agreement to the official rules and Devpost terms;
- any employer, conflict, sanctions, residency, age, or tax declarations shown by the form.

Do not infer an answer from repository text. If any declaration cannot be answered confidently, stop before submission and resolve it.

## 6. Run the final preview — HUMAN ACTION

Before submitting, verify the rendered Devpost preview:

- title and tagline are correct;
- category is **Collaborative Partner**;
- hosted application opens without credentials;
- GitHub opens publicly and displays the final preparation commit;
- YouTube opens and plays;
- all eight images are legible and ordered correctly;
- Markdown, lists, punctuation, and links rendered correctly;
- no private data, prohibited employment history, debug surfaces, or placeholder text appears;
- limitations and required disclosures are present;
- no field contains internal gate labels, placeholder markers, or unfinished instructions.

## 7. Submit — HUMAN ACTION

Confirm the deadline shown by Devpost still permits submission. Then perform the irreversible final submission.

After submission, save the confirmation page or confirmation email and record the submitted Devpost URL.

Final status before these actions: **HUMAN ACTION**.
