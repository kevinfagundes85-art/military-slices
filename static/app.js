const $ = (selector) => document.querySelector(selector);
const primary = $("#primary-content");
const addPanel = $("#add-panel");
const reviewPanel = $("#review-panel");
const statusBox = $("#status");
const contentGrid = $(".content-grid");
let envelope = null;
let pendingOrientation = null;
let pendingWhatIf = null;
let whatIfSourceVersion = null;
let hasRendered = false;
let reviewReturn = "plan";

const labels = {
  career: "Work",
  education: "Education",
  location: "Location",
  resume: "Your story",
};

const starterLensTopics = [
  { id: "career", label: "Work", slice: "career", summary: "Explore civilian work, career direction, and the conditions that make work fit." },
  { id: "education", label: "Education", slice: "education", summary: "Explore school, training, credentials, and what they should make possible." },
  { id: "location", label: "Location", slice: "location", summary: "Explore where you may live, commute, or relocate and what the choice needs to respect." },
  { id: "family", label: "Family and household", slice: "location", summary: "Explore household needs that may shape timing, location, work, or education." },
  { id: "resume", label: "Résumé", slice: "resume", summary: "Explore how your experience could support a specific civilian role or use." },
  { id: "timing", label: "Timing", slice: "location", summary: "Explore the dates, deadlines, moves, and transitions that could change what comes first." },
  { id: "training", label: "Training", slice: "education", summary: "Explore certifications, licenses, and focused training without assuming another degree is required." },
  { id: "work-needs", label: "Work needs", slice: "career", summary: "Explore schedule, travel, commute, pace, environment, and flexibility without explaining why you need them." },
];

const contextualLensRules = [
  { id: "family", label: "Family and household", slice: "location", terms: ["spouse", "family", "household", "child", "caregiver"] },
  { id: "pcs", label: "PCS and moving", slice: "location", terms: ["pcs", "move", "moving", "relocat"] },
  { id: "timing", label: "Timing", slice: "location", terms: ["date", "month", "year", "before", "deadline", "separate", "retire"] },
  { id: "training", label: "Training", slice: "education", terms: ["training", "certif", "credential", "license", "degree", "school"] },
  { id: "pay", label: "Pay and income", slice: "career", terms: ["salary", "pay", "income", "compensation"] },
  { id: "clearance", label: "Clearance", slice: "career", terms: ["clearance", "classified", "security eligibility"] },
  { id: "work-needs", label: "Work needs", slice: "career", terms: ["shift", "schedule", "travel", "remote", "hybrid", "commute", "pace"] },
];

const serviceLabels = {
  army: "Army",
  navy: "Navy",
  marine_corps: "Marine Corps",
  air_force: "Air Force",
  space_force: "Space Force",
  coast_guard: "Coast Guard",
};

const windowLabels = {
  PATH_IDENTITY: "Establishing the next useful starting point",
  A: "Early preparation · roughly 18–24+ months out",
  B: "Transition path activation · roughly 12–18 months out",
  C: "Preparation baseline · roughly 9–12 months out",
  D: "Closing route prerequisites · roughly 6–9 months out",
  E: "Time-sensitive execution · roughly 3–6 months out",
  F: "Final readiness · roughly 1–3 months out",
  G: "Final-out window · under 30 days",
  H: "Post-service stabilization",
};

function idempotencyKey() {
  return crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`;
}

function humanError(message, status = 0) {
  if (status === 409) return "Your plan changed somewhere else. The newest version is loaded; try this choice again.";
  if (status === 429) return "Too many updates arrived at once. Wait a moment, then try again.";
  if (status === 413) return "That file is larger than the 5 MB limit.";
  if (/provider|gemini|firestore|resolver|model route|stack trace|internal server/i.test(message || "")) {
    return "We couldn’t finish this step. Your earlier plan is unchanged, so you can safely try again.";
  }
  return message || "Something went wrong. Your earlier plan is unchanged; try again.";
}

async function api(path, options = {}) {
  const { timeoutMs = 25000, ...requestOptions } = options;
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(path, {
      credentials: "same-origin",
      headers: requestOptions.body instanceof FormData ? {} : { "Content-Type": "application/json" },
      ...requestOptions,
      signal: controller.signal,
    });
    if (!response.ok) {
      let detail = "Something went wrong. Please try again.";
      try {
        const payload = await response.json();
        detail = payload.detail || detail;
      } catch (_) {}
      const error = new Error(humanError(detail, response.status));
      error.status = response.status;
      throw error;
    }
    return response.json();
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error("This took too long. Your plan was not left spinning; reload to check the current state.");
    }
    if (error instanceof TypeError) {
      throw new Error("The connection was interrupted. Your earlier plan is unchanged; check your connection and try again.");
    }
    throw error;
  } finally {
    window.clearTimeout(timeout);
  }
}

function announce(message, error = false) {
  statusBox.textContent = message;
  statusBox.classList.toggle("error", error);
  statusBox.classList.add("visible");
  window.clearTimeout(announce.timeout);
  announce.timeout = window.setTimeout(() => statusBox.classList.remove("visible"), 5000);
}

function clearAnnouncement() {
  window.clearTimeout(announce.timeout);
  statusBox.classList.remove("visible", "error");
  statusBox.textContent = "";
}

function showInlineGuidance(root, message) {
  root.querySelector(".inline-guidance")?.remove();
  const guidance = document.createElement("p");
  guidance.className = "inline-guidance";
  guidance.setAttribute("role", "alert");
  guidance.setAttribute("tabindex", "-1");
  guidance.textContent = message;
  root.appendChild(guidance);
  guidance.focus({ preventScroll: true });
}

function escapeHtml(value) {
  const element = document.createElement("div");
  element.textContent = value ?? "";
  return element.innerHTML;
}

function humanCopy(value) {
  return String(value ?? "")
    .replace(/\blatent\b/gi, "in the background")
    .replace(/\bcanonical\b/gi, "current")
    .replace(/\bgoverned\b/gi, "saved")
    .replace(/\bstale\b/gi, "ready for another look")
    .replace(/\bdependencies?\b/gi, "related choices")
    .replace(/\bexecution state\b/gi, "plan status")
    .replace(/\bauthority governor\b/gi, "your control")
    .replace(/\bresolver\b/gi, "system")
    .replace(/initial saved state/gi, "Plan created");
}

function whatIfCopy(value) {
  const copy = humanCopy(value)
    .replace(/^Path milestone:/i, "Current step:")
    .replace(/^Active gate:/i, "Current question:");
  if (/^Current question:\s*none$/i.test(copy)) return "No question is waiting.";
  return copy.replace(/^Current step:\s*([A-Z0-9_]+)$/i, (_, step) => (
    `Current step: ${step.toLowerCase().replaceAll("_", " ")}.`
  ));
}

function planHasStarted(state) {
  return state.version > 0 && Boolean(state.human_anchor);
}

function executionMode(state) {
  return state.execution?.state || "ACTIVE";
}

function setProcessing(message = "", button = null) {
  const indicator = $("#processing-status");
  indicator.hidden = !message;
  indicator.innerHTML = message
    ? `<span class="processing-dot" aria-hidden="true"></span><span>${escapeHtml(message)}</span>`
    : "";
  if (button) button.disabled = Boolean(message);
}

function focusPrimary() {
  const heading = $("#primary-title");
  heading?.setAttribute("tabindex", "-1");
  heading?.focus({ preventScroll: true });
}

function applyProgressiveDisclosure(next, showFeedback) {
  const started = planHasStarted(next.state);
  const contextVisible = started && Boolean(next.impact || (showFeedback && next.what_changed));
  $("#boot-shell").hidden = true;
  $("#orientation-shell").hidden = !started;
  $("#add-context-top").hidden = !started;
  $(".control-nav").hidden = !started;
  $(".context-column").hidden = !contextVisible;
  contentGrid.hidden = false;
  contentGrid.classList.toggle("fresh-start", !started);
  document.body.dataset.planState = started ? executionMode(next.state).toLowerCase() : "fresh";
}

function render(next, options = {}) {
  const previousVersion = envelope?.state?.version;
  const showFeedback = options.showFeedback ?? (hasRendered && next.state.version !== previousVersion);
  envelope = next;
  primary.setAttribute("aria-busy", "false");
  applyProgressiveDisclosure(next, showFeedback);
  renderTimeline(next.state);
  renderPath(next.state);
  renderProgress(next.progress, next.state, next.active_gate);
  renderLenses(next.state, next.lenses);
  renderPrimary(next);
  renderImpact(next.impact);
  const visibleFeedback = executionMode(next.state) === "COMPLETE" ? null : (showFeedback ? next.what_changed : null);
  renderChanged(visibleFeedback);
  $(".context-column").hidden = !planHasStarted(next.state) || (!next.impact && !visibleFeedback);
  hasRendered = true;
}

function renderProgress(_progress, state, gate) {
  const readiness = $("#readiness");
  readiness.hidden = true;
  if (executionMode(state) === "COMPLETE") {
    $("#readiness-count").textContent = "This goal is complete.";
  } else if (executionMode(state) === "PARALYZED") {
    $("#readiness-count").textContent = "One choice needs your attention.";
  } else {
    $("#readiness-count").textContent = gate ? `Next: ${gate.question}` : "No immediate choice is waiting.";
  }
  $("#readiness-marks").innerHTML = "";
}

function buildLensTopics(state, lenses) {
  if (state.version === 0) {
    return starterLensTopics.map((topic, index) => ({ ...topic, score: 80 - index, facts: [], fresh: true }));
  }
  const facts = (state.facts || []).filter((fact) => fact.status !== "stale");
  const knownText = facts.map((fact) => fact.statement).join(" ").toLowerCase();
  const byId = new Map();
  lenses.forEach((lens) => {
    const score = (lens.may_have_changed ? 120 : 0) + (lens.path_relevant ? 80 : 30) + Math.min(lens.fact_count, 6) * 4;
    byId.set(lens.name, {
      id: lens.name,
      label: lens.label,
      slice: lens.name,
      summary: humanCopy(lens.summary),
      facts: lens.facts.slice(-2),
      score,
      mayHaveChanged: lens.may_have_changed,
    });
  });
  contextualLensRules.forEach((rule) => {
    const matched = rule.terms.some((term) => knownText.includes(term));
    const explicitTiming = rule.id === "timing" && Boolean(state.transition_date || state.pcs_relocation_date);
    if (!matched && !explicitTiming) return;
    const relevantFacts = facts.filter((fact) => rule.terms.some((term) => fact.statement.toLowerCase().includes(term)));
    byId.set(rule.id, {
      ...rule,
      summary: relevantFacts.length
        ? `Information you supplied touches ${rule.label === "PCS and moving" ? rule.label : rule.label.toLowerCase()}. Looking here does not change your plan.`
        : `${rule.label} may affect timing or another choice already in view. Looking here does not change your plan.`,
      facts: relevantFacts.slice(-2).map((fact) => fact.statement),
      score: 65 + Math.min(relevantFacts.length, 4) * 5,
      mayHaveChanged: false,
    });
  });
  starterLensTopics.forEach((topic, index) => {
    if (byId.size >= 6 || byId.has(topic.id)) return;
    byId.set(topic.id, { ...topic, score: 20 - index, facts: [] });
  });
  return [...byId.values()]
    .sort((left, right) => right.score - left.score || left.label.localeCompare(right.label))
    .slice(0, 10);
}

function openTopicUpdate(topic) {
  if (envelope.state.version === 0) {
    renderColdTextEntry(topic);
    return;
  }
  openAdd(false);
  $("#input-text").value = "";
  $("#input-text").placeholder = `What changed about ${topic.label.toLowerCase()}? A sentence is enough.`;
  $("#input-text").focus();
}

function showLensPreview(topic, trigger) {
  const preview = $("#lens-preview");
  document.querySelectorAll(".lens-button").forEach((button) => {
    button.setAttribute("aria-expanded", String(button === trigger));
  });
  const mode = executionMode(envelope.state);
  const matchingImpact = envelope.impact?.affected_slice === topic.slice ? envelope.impact : null;
  const canBeginUpdate = mode === "ACTIVE";
  const factMarkup = topic.facts?.length
    ? `<ul class="lens-facts">${topic.facts.map((fact) => `<li>${escapeHtml(humanCopy(fact))}</li>`).join("")}</ul>`
    : "";
  const actionMarkup = matchingImpact
    ? `<div id="lens-impact-actions">${impactControls(matchingImpact)}</div>`
    : (canBeginUpdate
      ? `<button id="update-lens-topic" class="button button-secondary" type="button">${topic.fresh ? "Start with this" : "Update this"}</button>`
      : "");
  preview.innerHTML = `
    <button id="dismiss-lens-preview" class="preview-close" type="button" aria-label="Dismiss preview">×</button>
    <div class="section-kicker">Preview only — nothing changed</div>
    <h3>${escapeHtml(topic.label)}</h3>
    ${topic.mayHaveChanged ? '<div class="impact-note">A recent decision may make this worth checking.</div>' : ""}
    <p>${escapeHtml(topic.summary)}</p>
    ${factMarkup}
    <p class="trust-note">Closing this preview returns you to the same plan and question.</p>
    ${actionMarkup}
  `;
  preview.hidden = false;
  preview.scrollIntoView({ behavior: "smooth", block: "nearest" });
  $("#dismiss-lens-preview").addEventListener("click", () => {
    preview.hidden = true;
    trigger.setAttribute("aria-expanded", "false");
    trigger.focus();
  });
  if (matchingImpact) {
    wireImpact($("#lens-impact-actions"), matchingImpact);
  } else {
    $("#update-lens-topic")?.addEventListener("click", () => openTopicUpdate(topic));
  }
}

function renderLenses(state, lenses) {
  const topics = buildLensTopics(state, lenses);
  const nav = $("#lens-nav");
  $("#lens-cloud-shell").hidden = !topics.length;
  $("#lens-preview").hidden = true;
  nav.innerHTML = topics.map((topic, index) => `
    <button class="lens-button" data-lens="${escapeHtml(topic.id)}" data-weight="${index < 2 ? "3" : (index < 5 ? "2" : "1")}" data-impact="${Boolean(topic.mayHaveChanged)}" type="button" aria-expanded="false">
      <span>${escapeHtml(topic.label)}</span>
      <small>${topic.mayHaveChanged ? "Worth checking" : "Look without changing"}</small>
    </button>
  `).join("");
  nav.querySelectorAll(".lens-button").forEach((button) => {
    const topic = topics.find((item) => item.id === button.dataset.lens);
    button.addEventListener("click", () => showLensPreview(topic, button));
  });
}

function renderTimeline(state) {
  const order = ["TODAY", "PREPARE", "SEPARATE", "TRANSITION", "STABILIZE"];
  const activeIndex = Math.max(0, order.indexOf(state.stage));
  document.querySelectorAll(".timeline-step").forEach((step, index) => {
    step.classList.toggle("active", index <= activeIndex);
  });
}

function renderPath(state) {
  $("#current-target").textContent = state.human_anchor || "Choose what matters first.";
  const service = serviceLabels[state.service];
  const timing = windowLabels[state.current_timeline_window];
  if (!service && state.current_timeline_window === "PATH_IDENTITY") {
    $("#path-position").textContent = "Timing details will be added only when they affect the plan.";
  } else {
    $("#path-position").textContent = [service, timing].filter(Boolean).join(" · ") || "Current transition timing";
  }
}

function taskHorizon(tasks, expanded = false) {
  if (!tasks?.length) return "";
  return `
    <details class="task-horizon" ${expanded ? "open" : ""}>
      <summary>What this choice is working toward</summary>
      <ol>${tasks.slice(0, 3).map((task) => `<li>${escapeHtml(humanCopy(task.title))}</li>`).join("")}</ol>
    </details>
  `;
}

function renderColdTextEntry(topic = null) {
  primary.innerHTML = `
    <button id="back-to-front-door" class="button button-quiet back-to-front" type="button">← Choose another way to start</button>
    <div class="section-kicker">Start with a thought</div>
    <h2 id="primary-title">${topic ? `What’s going on with ${escapeHtml(topic.label.toLowerCase())}?` : "What’s going on?"}</h2>
    <p class="gate-copy">A sentence is enough. You do not need to organize it first.</p>
    <form id="cold-input-form" class="gate-form">
      <label for="cold-input-text">Tell Military SLICES what you are trying to figure out</label>
      <textarea id="cold-input-text" maxlength="12000" rows="5" placeholder="For example: I leave the Coast Guard next spring. I need steady work near Tacoma, but I don’t know what civilian roles fit my experience."></textarea>
      <button class="button button-primary" type="submit">See what matters first</button>
    </form>
    <p class="trust-note">Nothing changes until you review what the system heard and choose to use it in your plan.</p>
  `;
  $("#cold-input-form").addEventListener("submit", orientColdInput);
  $("#back-to-front-door").addEventListener("click", renderColdFrontDoor);
  $("#cold-input-text").focus({ preventScroll: true });
}

function chooseColdEntry(kind) {
  if (kind === "thought") {
    renderColdTextEntry();
    return;
  }
  const input = $("#cold-artifact-file");
  input.accept = kind === "image"
    ? ".png,.jpg,.jpeg,image/png,image/jpeg"
    : ".txt,.pdf,.docx,text/plain,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document";
  input.click();
}

function renderColdFrontDoor() {
  primary.innerHTML = `
    <div class="front-door-copy">
      <div class="section-kicker">Start with what you have</div>
      <h2 id="primary-title">You do not need to have your transition figured out.</h2>
      <p class="gate-copy">Bring a document, a screenshot, or one unpolished thought. Military SLICES will help identify one useful next step.</p>
    </div>
    <div class="entry-story" role="list" aria-label="Choose how to start">
      <article class="entry-card" role="listitem">
        <img src="/static/images/start-document.webp" alt="A woman reviewing documents beside her laptop at a kitchen table" width="960" height="640">
        <div class="entry-card-copy">
          <h3>I have a document</h3>
          <p>Résumé, orders, or another file you already use.</p>
          <button class="button button-secondary entry-choice" data-entry="document" type="button">Start with a document</button>
        </div>
      </article>
      <article class="entry-card" role="listitem">
        <img src="/static/images/start-image.webp" alt="A man comparing a phone screenshot with information on his laptop" width="960" height="640">
        <div class="entry-card-copy">
          <h3>I have a screenshot</h3>
          <p>A job post, profile, orders, or anything useful in an image.</p>
          <button class="button button-secondary entry-choice" data-entry="image" type="button">Start with an image</button>
        </div>
      </article>
      <article class="entry-card" role="listitem">
        <img src="/static/images/start-thought.webp" alt="A military-connected couple talking through a move and career decision at home" width="960" height="640">
        <div class="entry-card-copy">
          <h3>I just want to explain</h3>
          <p>Say what is happening in your own words. It can be messy.</p>
          <button class="button button-primary entry-choice" data-entry="thought" type="button">Tell me what’s going on</button>
        </div>
      </article>
    </div>
    <input id="cold-artifact-file" type="file" hidden aria-hidden="true" tabindex="-1">
    <p class="trust-note front-door-trust">Looking around does not change a plan. Choosing a file or writing a thought only starts the existing review process.</p>
  `;
  primary.querySelectorAll(".entry-choice").forEach((button) => {
    button.addEventListener("click", () => chooseColdEntry(button.dataset.entry));
  });
  $("#cold-artifact-file").addEventListener("change", uploadArtifact);
}

function renderPrimary(next) {
  const state = next.state;
  const gate = next.active_gate;
  const mode = executionMode(state);
  if (state.version === 0) {
    renderColdFrontDoor();
    return;
  }
  if (mode === "COMPLETE") {
    primary.innerHTML = `
      <div class="completion-mark" aria-hidden="true">✓</div>
      <h2 id="primary-title">You’ve completed this goal.</h2>
      <p class="gate-copy">There is no unfinished task waiting here. Your plan remains available if something changes.</p>
      <button id="add-after-complete" class="button button-quiet" type="button">Add an update</button>
    `;
    $("#add-after-complete").addEventListener("click", () => openAdd(false));
    return;
  }
  if (!gate) {
    const accepted = state.career_hypotheses.find((item) => item.status === "accepted");
    const hasTasks = Boolean(state.active_tasks?.length);
    primary.innerHTML = `
      <h2 id="primary-title">${accepted ? `Keep testing ${escapeHtml(accepted.title)}.` : (hasTasks ? "Your next steps are ready." : "Your plan is caught up for now.")}</h2>
      <p class="gate-copy">${accepted ? `Your experience suggests a credible direction. The remaining gaps are hypotheses until you compare them with a real job description.` : (hasTasks ? "Work through these steps in the order that fits your timing. Add an update when something changes." : "Add something whenever your timing, priorities, work preferences, education, or location changes.")}</p>
      ${taskHorizon(state.active_tasks, true)}
      <button id="add-more" class="button ${hasTasks ? "button-quiet" : "button-primary"}" type="button">${accepted ? "Add a job description or update" : "Add an update"}</button>
    `;
    $("#add-more").addEventListener("click", () => openAdd(false));
    return;
  }
  const hypotheses = state.career_hypotheses.filter((item) => item.status === "candidate");
  let control = "";
  if (gate.surface === "date") {
    control = `<label for="gate-value">Expected date</label><input id="gate-value" type="date" min="${new Date().toISOString().slice(0, 10)}">`;
  } else if ((gate.surface === "choice" || gate.surface === "conflict") && gate.options.length) {
    control = `<div class="choice-grid">${gate.options.map((option, index) => `
      <label class="choice-option"><input type="radio" name="gate-choice" value="${escapeHtml(option)}" ${index === 0 ? "checked" : ""}><span>${escapeHtml(humanCopy(option))}</span></label>
    `).join("")}</div>`;
  } else if (gate.surface === "compare" && hypotheses.length) {
    control = `<div class="hypothesis-grid">${hypotheses.map((item) => `
      <article class="hypothesis">
        <h3>${escapeHtml(item.title)}</h3>
        <p>${escapeHtml(humanCopy(item.rationale))}</p>
        <p><strong>What may already fit</strong><br>${escapeHtml(humanCopy(item.capability_matches.join(" · ")))}</p>
        <p><strong>What to verify</strong><br>${escapeHtml(humanCopy(item.possible_gaps.join(" · ")))}</p>
        <div class="evidence-note">Explore with ${escapeHtml(humanCopy(item.evidence.join(" · ")))}</div>
        <div class="hypothesis-actions">
          <button class="button button-secondary hypothesis-choice" data-value="explore:${escapeHtml(item.title)}" type="button">Test this direction</button>
          <button class="button button-quiet hypothesis-choice" data-value="reject:${escapeHtml(item.title)}" type="button">Not for me</button>
        </div>
      </article>
    `).join("")}</div>`;
  } else {
    control = `<label for="gate-value">Your answer</label><textarea id="gate-value" rows="4" placeholder="A sentence is enough."></textarea>`;
  }
  primary.innerHTML = `
    ${mode === "PARALYZED" ? '<div class="attention-note">These choices cannot both guide the next step. Your answer below will clear the conflict.</div>' : ""}
    <h2 id="primary-title">${escapeHtml(humanCopy(gate.question))}</h2>
    <p class="gate-copy">${escapeHtml(humanCopy(gate.why))}</p>
    <form id="gate-form" class="gate-form">
      ${control}
      ${gate.surface === "compare" && hypotheses.length ? "" : '<button class="button button-primary" type="submit">Use this decision</button>'}
    </form>
    ${taskHorizon(state.active_tasks)}
  `;
  const form = $("#gate-form");
  form.addEventListener("submit", submitDecision);
  document.querySelectorAll(".hypothesis-choice").forEach((button) => {
    button.addEventListener("click", () => submitDecision({ preventDefault() {}, currentTarget: button }));
  });
}

function impactUpdateMarkup(impact) {
  if (impact.update_options?.length) {
    return `<div class="impact-update" hidden>${impact.update_options.map((option) => (
      `<button class="button button-secondary impact-option" data-value="${escapeHtml(option)}" type="button">${escapeHtml(option)}</button>`
    )).join("")}</div>`;
  }
  return `<div class="impact-update" hidden>
    <label for="impact-value">What changed?</label>
    <textarea id="impact-value" rows="3" placeholder="A sentence is enough."></textarea>
    <button class="button button-primary impact-save" type="button">Use this update</button>
  </div>`;
}

function impactControls(impact) {
  return `
    <div class="button-row align-start impact-buttons">
      <button class="button button-primary impact-confirm" type="button">${escapeHtml(impact.confirm_label)}</button>
      <button class="button button-quiet impact-update-open" type="button">${escapeHtml(impact.update_label)}</button>
      ${impact.blocking ? "" : '<button class="button button-quiet impact-dismiss" type="button">Not now</button>'}
    </div>
    ${impactUpdateMarkup(impact)}
  `;
}

function wireImpact(root, impact) {
  root.querySelector(".impact-confirm").addEventListener("click", () => submitRevalidation(impact, "confirm"));
  root.querySelector(".impact-update-open").addEventListener("click", () => {
    const update = root.querySelector(".impact-update");
    update.hidden = false;
    update.querySelector("button, textarea")?.focus();
  });
  root.querySelector(".impact-dismiss")?.addEventListener("click", () => submitRevalidation(impact, "dismiss"));
  root.querySelectorAll(".impact-option").forEach((button) => {
    button.addEventListener("click", () => submitRevalidation(impact, "update", button.dataset.value));
  });
  root.querySelector(".impact-save")?.addEventListener("click", () => {
    const value = root.querySelector("#impact-value")?.value?.trim();
    if (!value) {
      showInlineGuidance(root, "Add the update first.");
      return;
    }
    submitRevalidation(impact, "update", value);
  });
}

function renderImpact(impact) {
  const panel = $("#impact-panel");
  if (!impact) {
    panel.hidden = true;
    return;
  }
  if (impact.blocking) {
    panel.hidden = true;
    primary.innerHTML = `
      ${taskHorizon(envelope.state.active_tasks)}
      <h2 id="primary-title">${escapeHtml(humanCopy(impact.question))}</h2>
      <p class="gate-copy">${escapeHtml(humanCopy(impact.message))}</p>
      <div id="blocking-impact-actions">${impactControls(impact)}</div>
    `;
    wireImpact($("#blocking-impact-actions"), impact);
    return;
  }
  panel.hidden = false;
  $("#impact-message").textContent = humanCopy(impact.message);
  $("#impact-question").textContent = humanCopy(impact.question);
  $("#impact-actions").innerHTML = impactControls(impact);
  wireImpact($("#impact-actions"), impact);
}

async function submitRevalidation(impact, action, value = null) {
  document.querySelectorAll(".impact-card button, #blocking-impact-actions button").forEach((button) => {
    button.disabled = true;
  });
  setProcessing("Updating only the part of your plan affected by this choice…");
  try {
    const next = await api("/api/revalidate", {
      method: "POST",
      body: JSON.stringify({
        impact_id: impact.id,
        action,
        value,
        expected_version: envelope.state.version,
        idempotency_key: idempotencyKey(),
      }),
    });
    render(next, { showFeedback: true });
    $("#primary").scrollIntoView({ behavior: "smooth", block: "start" });
    focusPrimary();
    announce(action === "dismiss" ? "No changes saved." : "Saved.");
  } catch (error) {
    if (error.status === 409) await loadState();
    announce(error.message, true);
    document.querySelectorAll(".impact-card button, #blocking-impact-actions button").forEach((button) => {
      button.disabled = false;
    });
  } finally {
    setProcessing();
  }
}

function renderChanged(feedback) {
  const panel = $("#changed-panel");
  if (!feedback) {
    panel.hidden = true;
    return;
  }
  panel.hidden = false;
  $("#changed-title").textContent = humanCopy(feedback.headline);
  $("#changed-list").innerHTML = feedback.consequences.map((item) => `<li>${escapeHtml(humanCopy(item))}</li>`).join("");
}

function showInspection(panel) {
  clearAnnouncement();
  [addPanel, reviewPanel, $("#lens-panel"), $("#history-panel"), $("#what-if-panel")].forEach((item) => {
    item.hidden = item !== panel;
  });
  contentGrid.hidden = true;
  $(".control-nav").hidden = true;
  $("#orientation-shell").hidden = true;
  document.body.classList.add("inspection-open");
  panel.hidden = false;
  panel.scrollIntoView({ behavior: "smooth", block: "start" });
  const heading = panel.querySelector("h2");
  heading?.setAttribute("tabindex", "-1");
  heading?.focus({ preventScroll: true });
}

function closeInspection(panel, returnTo) {
  panel.hidden = true;
  document.body.classList.remove("inspection-open");
  contentGrid.hidden = false;
  $("#orientation-shell").hidden = !planHasStarted(envelope.state);
  $(".control-nav").hidden = !planHasStarted(envelope.state);
  returnTo?.focus();
}

function openLensDetail(lens) {
  const panel = $("#lens-panel");
  $("#lens-title").textContent = lens.label;
  $("#lens-detail").innerHTML = `
    <p class="trust-note">You are reviewing this part of your plan. Nothing changes until you deliberately add or choose something.</p>
    <p>${escapeHtml(humanCopy(lens.summary))}</p>
    ${lens.facts.length ? `<h3>Relevant details</h3><ul>${lens.facts.map((item) => `<li>${escapeHtml(humanCopy(item))}</li>`).join("")}</ul>` : "<p>No additional details are needed here right now.</p>"}
    ${lens.decisions.length ? `<h3>Choices you made</h3><ul>${lens.decisions.map((item) => `<li>${escapeHtml(humanCopy(item))}</li>`).join("")}</ul>` : ""}
  `;
  showInspection(panel);
}

async function openHistory() {
  const panel = $("#history-panel");
  showInspection(panel);
  $("#history-list").innerHTML = "<p>Loading earlier plans…</p>";
  $("#history-detail").hidden = true;
  try {
    const history = await api("/api/history");
    $("#history-list").innerHTML = history.entries.slice().reverse().map((entry) => `
      <button class="history-version" data-version="${entry.version}" type="button">
        <strong>${entry.current ? "Current plan" : "Earlier plan"}</strong>
        <span>${escapeHtml(humanCopy(entry.human_anchor || "No target declared"))}</span>
        <small>${escapeHtml(humanCopy(entry.change_summary))}</small>
      </button>
    `).join("");
    document.querySelectorAll(".history-version").forEach((button) => {
      button.addEventListener("click", () => inspectHistoryVersion(Number(button.dataset.version)));
    });
  } catch (error) {
    $("#history-list").innerHTML = `<p>${escapeHtml(error.message)}</p>`;
  }
}

async function inspectHistoryVersion(version) {
  try {
    const result = await api(`/api/history/${version}`);
    const entry = result.entry;
    const detail = $("#history-detail");
    detail.hidden = false;
    detail.innerHTML = `
      <div class="history-snapshot">
        <div class="section-kicker">Read-only earlier plan</div>
        <h3>${escapeHtml(humanCopy(entry.human_anchor || "No target was declared"))}</h3>
        <p>${entry.open_gates.length ? `Still unresolved then: ${escapeHtml(humanCopy(entry.open_gates.join(" · ")))}` : "Nothing unresolved was recorded."}</p>
        <p>${entry.closed_decisions.length ? `Choices then: ${escapeHtml(humanCopy(entry.closed_decisions.join(" · ")))}` : "No choice was recorded yet."}</p>
        <p class="trust-note">Your current plan has not changed.</p>
        <button id="what-if-from-history" class="button button-secondary" type="button">What if from here?</button>
      </div>
    `;
    $("#what-if-from-history").addEventListener("click", () => {
      whatIfSourceVersion = version;
      openWhatIf();
    });
  } catch (error) {
    announce(error.message, true);
  }
}

function openWhatIf() {
  pendingWhatIf = null;
  const panel = $("#what-if-panel");
  $("#what-if-result").hidden = true;
  $("#what-if-form").hidden = false;
  $("#what-if-text").value = "";
  showInspection(panel);
  $("#what-if-text").focus();
}

async function createWhatIf(event) {
  event.preventDefault();
  const text = $("#what-if-text").value.trim();
  if (!text) {
    showInlineGuidance($("#what-if-panel"), "Add one change to explore.");
    return;
  }
  const button = event.submitter;
  button.disabled = true;
  try {
    pendingWhatIf = await api("/api/what-if", {
      method: "POST",
      body: JSON.stringify({ text, source_version: whatIfSourceVersion }),
    });
    renderWhatIf(pendingWhatIf);
  } catch (error) {
    announce(error.message, true);
  } finally {
    button.disabled = false;
  }
}

function renderWhatIf(branch) {
  $("#what-if-form").hidden = true;
  const result = $("#what-if-result");
  result.hidden = false;
  result.innerHTML = `
    <div class="comparison-grid">
      <section><div class="section-kicker">Current</div><ul>${branch.current_summary.map((item) => `<li>${escapeHtml(whatIfCopy(item))}</li>`).join("")}</ul></section>
      <section><div class="section-kicker">Hypothetical</div><ul>${branch.hypothetical_summary.map((item) => `<li>${escapeHtml(whatIfCopy(item))}</li>`).join("")}</ul></section>
    </div>
    ${branch.conflicts.length ? `<div class="conflict-note"><strong>Conflict to resolve</strong><ul>${branch.conflicts.map((item) => `<li>${escapeHtml(whatIfCopy(item))}</li>`).join("")}</ul></div>` : ""}
    <h3>If you use this plan</h3>
    <ul>${branch.consequences.map((item) => `<li>${escapeHtml(whatIfCopy(item))}</li>`).join("")}</ul>
    <p class="trust-note">This remains hypothetical until you choose “Use this plan.”</p>
    <div class="button-row">
      <button id="discard-what-if" class="button button-quiet" type="button">Keep my current plan</button>
      <button id="promote-what-if" class="button button-primary" type="button">Use this plan</button>
    </div>
  `;
  $("#discard-what-if").addEventListener("click", () => {
    pendingWhatIf = null;
    whatIfSourceVersion = null;
    closeInspection($("#what-if-panel"), $("#open-what-if"));
    announce("No changes saved.");
  });
  $("#promote-what-if").addEventListener("click", promoteWhatIf);
}

async function promoteWhatIf() {
  if (!pendingWhatIf) return;
  const button = $("#promote-what-if");
  button.disabled = true;
  try {
    const next = await api("/api/what-if/promote", {
      method: "POST",
      body: JSON.stringify({
        token: pendingWhatIf.token,
        expected_version: envelope.state.version,
        idempotency_key: idempotencyKey(),
      }),
    });
    pendingWhatIf = null;
    whatIfSourceVersion = null;
    $("#what-if-panel").hidden = true;
    contentGrid.hidden = false;
    document.body.classList.remove("inspection-open");
    render(next, { showFeedback: true });
    focusPrimary();
    announce("Saved.");
  } catch (error) {
    if (error.status === 409) await loadState();
    announce(error.message, true);
    button.disabled = false;
  }
}

function openAdd(fileFirst) {
  reviewReturn = "add";
  reviewPanel.hidden = true;
  contentGrid.hidden = true;
  addPanel.hidden = false;
  addPanel.scrollIntoView({ behavior: "smooth", block: "start" });
  if (fileFirst) {
    $("#artifact-file").click();
  } else {
    $("#input-text").focus();
  }
}

function closeAdd() {
  addPanel.hidden = true;
  contentGrid.hidden = false;
  $("#add-context-top").focus();
}

async function orientInput(event) {
  event.preventDefault();
  const text = $("#input-text").value.trim();
  if (!text) {
    showInlineGuidance($("#add-panel"), "Add a sentence or choose a file first.");
    $("#input-text").focus();
    return;
  }
  reviewReturn = "add";
  await requestOrientation(text, event.submitter);
}

async function orientColdInput(event) {
  event.preventDefault();
  const text = $("#cold-input-text").value.trim();
  if (!text) {
    showInlineGuidance(primary, "Add a sentence first.");
    $("#cold-input-text").focus();
    return;
  }
  reviewReturn = "cold";
  await requestOrientation(text, event.submitter);
}

async function requestOrientation(text, submit) {
  if (submit) {
    submit.disabled = true;
    submit.textContent = "Working through this…";
  }
  try {
    pendingOrientation = await api("/api/orient", { method: "POST", body: JSON.stringify({ text }) });
    showReview(pendingOrientation);
  } catch (error) {
    announce(error.message, true);
  } finally {
    if (submit) {
      submit.disabled = false;
      submit.textContent = "Continue";
    }
  }
}

function showReview(result) {
  $("#review-summary").textContent = result.summary;
  $("#review-statements").innerHTML = result.statements.map((item) => `<li>${escapeHtml(item.text)}</li>`).join("") || "<li>We need one clarification before this can shape your plan.</li>";
  $("#review-text").value = result.reviewed_input;
  showInspection(reviewPanel);
}

async function confirmReview() {
  if (!pendingOrientation || !envelope) return;
  const reviewedInput = $("#review-text").value.trim();
  if (reviewedInput !== pendingOrientation.reviewed_input) {
    showInlineGuidance(reviewPanel, "Checking your correction before it shapes the plan…");
    try {
      pendingOrientation = await api("/api/orient", { method: "POST", body: JSON.stringify({ text: reviewedInput }) });
      showReview(pendingOrientation);
    } catch (error) {
      announce(error.message, true);
    }
    return;
  }
  const button = $("#confirm-review");
  button.disabled = true;
  button.textContent = "Updating your plan…";
  try {
    const next = await api("/api/confirm", {
      method: "POST",
      body: JSON.stringify({
        token: pendingOrientation.token,
        reviewed_input: reviewedInput,
        expected_version: envelope.state.version,
        idempotency_key: idempotencyKey(),
      }),
    });
    reviewPanel.hidden = true;
    contentGrid.hidden = false;
    document.body.classList.remove("inspection-open");
    pendingOrientation = null;
    render(next, { showFeedback: true });
    $("#primary").scrollIntoView({ behavior: "smooth", block: "start" });
    focusPrimary();
    announce("Saved.");
  } catch (error) {
    if (error.status === 409) await loadState();
    announce(error.message, true);
  } finally {
    button.disabled = false;
    button.textContent = "Use this in my plan";
  }
}

async function submitDecision(event) {
  event.preventDefault();
  const gate = envelope?.active_gate;
  if (!gate) return;
  let value = event.currentTarget?.dataset?.value || "";
  if (!value && (gate.surface === "choice" || gate.surface === "conflict")) {
    value = document.querySelector('input[name="gate-choice"]:checked')?.value || "";
  }
  if (!value) value = $("#gate-value")?.value?.trim() || "";
  if (!value) {
    showInlineGuidance(primary, "Add your decision first.");
    return;
  }
  const buttons = document.querySelectorAll("#gate-form button");
  buttons.forEach((button) => { button.disabled = true; });
  setProcessing("Working through this…");
  try {
    const next = await api("/api/decision", {
      method: "POST",
      body: JSON.stringify({
        gate_id: gate.id,
        value,
        expected_version: envelope.state.version,
        idempotency_key: idempotencyKey(),
      }),
    });
    render(next, { showFeedback: true });
    focusPrimary();
    announce("Saved.");
  } catch (error) {
    if (error.status === 409) await loadState();
    showInlineGuidance(primary, error.message);
  } finally {
    buttons.forEach((button) => { button.disabled = false; });
    setProcessing();
  }
}

async function uploadArtifact(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  if (!envelope) {
    showInlineGuidance(primary, "Your plan is still loading. Try the file again in a moment.");
    event.target.value = "";
    return;
  }
  if (file.size > 5 * 1024 * 1024) {
    showInlineGuidance(
      event.target.id === "cold-artifact-file" ? primary : $("#add-panel"),
      "That file is larger than the 5 MB limit.",
    );
    event.target.value = "";
    return;
  }
  const form = new FormData();
  form.append("file", file);
  form.append("expected_version", String(envelope.state.version));
  form.append("idempotency_key", idempotencyKey());
  const fileStatus = event.target.id === "cold-artifact-file" ? null : $("#file-status");
  if (fileStatus) fileStatus.textContent = `Using ${file.name} to update your plan…`;
  setProcessing("Reading the relevant details and updating this step…");
  try {
    const next = await api("/api/artifact", { method: "POST", body: form });
    addPanel.hidden = true;
    reviewPanel.hidden = true;
    contentGrid.hidden = false;
    document.body.classList.remove("inspection-open");
    render(next, { showFeedback: true });
    $("#primary").scrollIntoView({ behavior: "smooth", block: "start" });
    focusPrimary();
    announce("Saved.");
  } catch (error) {
    if (fileStatus) fileStatus.textContent = "PDF, DOCX, TXT, PNG, or JPG · 5 MB max";
    if (error.status === 409) await loadState();
    showInlineGuidance(event.target.id === "cold-artifact-file" ? primary : $("#add-panel"), error.message);
  } finally {
    setProcessing();
    event.target.value = "";
  }
}

async function loadState() {
  try {
    render(await api("/api/state"), { showFeedback: false });
  } catch (error) {
    primary.innerHTML = `<h2 id="primary-title">We couldn’t load your plan.</h2><p>${escapeHtml(error.message)}</p><button id="retry" class="button button-primary">Try again</button>`;
    $("#retry").addEventListener("click", loadState);
  }
}

$("#add-context-top").addEventListener("click", () => openAdd(false));
$("#close-add").addEventListener("click", closeAdd);
$("#input-form").addEventListener("submit", orientInput);
$("#artifact-file").addEventListener("change", uploadArtifact);
$("#cancel-review").addEventListener("click", () => {
  reviewPanel.hidden = true;
  document.body.classList.remove("inspection-open");
  if (reviewReturn === "add") {
    addPanel.hidden = false;
    $("#input-text").focus();
  } else {
    contentGrid.hidden = false;
    $("#orientation-shell").hidden = !planHasStarted(envelope.state);
    $(".control-nav").hidden = !planHasStarted(envelope.state);
    $("#cold-input-text")?.focus();
  }
});
$("#confirm-review").addEventListener("click", confirmReview);
$("#open-history").addEventListener("click", openHistory);
$("#open-what-if").addEventListener("click", () => {
  whatIfSourceVersion = null;
  openWhatIf();
});
$("#close-lens").addEventListener("click", () => closeInspection($("#lens-panel"), $("#lens-nav .lens-button")));
$("#close-history").addEventListener("click", () => closeInspection($("#history-panel"), $("#open-history")));
$("#close-what-if").addEventListener("click", () => {
  pendingWhatIf = null;
  whatIfSourceVersion = null;
  closeInspection($("#what-if-panel"), $("#open-what-if"));
});
$("#what-if-form").addEventListener("submit", createWhatIf);

$("#boot-shell").hidden = true;
contentGrid.hidden = false;
contentGrid.classList.add("fresh-start");
primary.setAttribute("aria-busy", "true");
renderColdFrontDoor();
loadState();
