const $ = (selector) => document.querySelector(selector);
const primary = $("#primary-content");
const addPanel = $("#add-panel");
const reviewPanel = $("#review-panel");
const statusBox = $("#status");
const contentGrid = $(".content-grid");
let envelope = null;
let pendingOrientation = null;
let pendingWhatIf = null;
let pendingFogBank = null;
let whatIfSourceVersion = null;
let hasRendered = false;
let reviewReturn = "plan";
let inputContext = null;

const labels = {
  career: "Work",
  education: "Education",
  location: "Location",
  resume: "Your story",
};

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
  B: "Starting your transition plan · roughly 12–18 months out",
  C: "Building your plan · roughly 9–12 months out",
  D: "Finishing required steps · roughly 6–9 months out",
  E: "Taking time-sensitive steps · roughly 3–6 months out",
  F: "Final readiness · roughly 1–3 months out",
  G: "Final month · under 30 days",
  H: "Building stability after service",
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

function resetInputContext() {
  inputContext = null;
  const input = $("#input-text");
  if (input) input.placeholder = "For example: My timeline changed, or I want to explore something different.";
}

function setAddPanelCopy(kicker, title, description) {
  $("#add-kicker").textContent = kicker;
  $("#add-title").textContent = title;
  $("#add-description").textContent = description;
}

function resetAddPanelCopy() {
  setAddPanelCopy("Update your plan", "Something changed?", "Tell Military SLICES what’s different.");
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
  const raw = String(value ?? "");
  const exactLabels = {
    army: "Army",
    navy: "Navy",
    marine_corps: "Marine Corps",
    air_force: "Air Force",
    space_force: "Space Force",
    coast_guard: "Coast Guard",
    active_duty: "Active duty or full-time service",
    reserve: "Reserve",
    national_guard: "National Guard",
  };
  if (exactLabels[raw]) return exactLabels[raw];
  return raw
    .replace(/resolve the next material uncertainty/gi, "Choose what to test next")
    .replace(/used what you learned to retire this uncertainty/gi, "Your answer moved this plan forward")
    .replace(/recomputed the next question from the updated plan/gi, "Here’s the next thing worth figuring out")
    .replace(/it advances the current target inside the active service-aware path/gi, "This is the next answer that could change what you do")
    .replace(/\blatent\b/gi, "in the background")
    .replace(/\bcanonical\b/gi, "current")
    .replace(/\bgoverned\b/gi, "saved")
    .replace(/\bstale\b/gi, "ready for another look")
    .replace(/\bdependencies?\b/gi, "related choices")
    .replace(/\bexecution state\b/gi, "plan status")
    .replace(/\bauthority governor\b/gi, "your control")
    .replace(/\bresolver\b/gi, "system")
    .replace(/\bpath[- ]relevant\b/gi, "important to this plan")
    .replace(/\bmaterial(?:ly)?\b/gi, "enough to matter")
    .replace(/\bbounded\b/gi, "focused")
    .replace(/\bdeclared target\b/gi, "goal you chose")
    .replace(/\bactive target\b/gi, "current goal")
    .replace(/\bactive decision\b/gi, "current decision")
    .replace(/\bactive path\b/gi, "current plan")
    .replace(/\btransition window\b/gi, "transition timing")
    .replace(/\breconsidered\b/gi, "reviewed again")
    .replace(/\bre-orientation\b/gi, "plan update")
    .replace(/\bhypothetical\b/gi, "possible")
    .replace(/\bprovenance\b/gi, "source history")
    .replace(/\buncertaint(?:y|ies)\b/gi, "open question")
    .replace(/\bassumptions?\b/gi, "part of the plan")
    .replace(/\bprerequisites?\b/gi, "required steps")
    .replace(/\bfeasibility\b/gi, "whether it can work")
    .replace(/\bnomination\b/gi, "suggestion")
    .replace(/\bcandidates?\b/gi, "options")
    .replace(/initial saved state/gi, "Plan created");
}

function humanQuestion(value) {
  const question = humanCopy(value);
  const legacyPrefix = "What evidence would confirm or change this assumption:";
  if (!question.toLowerCase().startsWith(legacyPrefix.toLowerCase())) return question;
  const gap = question.slice(legacyPrefix.length).trim().replace(/\?$/, "");
  const known = {
    "A specific user problem worth owning": "Which veteran problem do you want to take on first?",
    "Evidence that a small useful solution changes something for that user": "What could you test with one veteran to see whether your idea actually helps?",
    "Civilian job-title calibration": "Which civilian job title best matches the work you want?",
    "Evidence matched to a real posting": "Which real job posting would help you test this direction?",
    "Civilian data-tool evidence": "What work sample would show a civilian team how you use data tools?",
    "Portfolio examples without protected information": "What could you put in a portfolio without using protected information?",
  };
  return known[gap] || `What would give you a real answer about ${gap.charAt(0).toLowerCase()}${gap.slice(1)}?`;
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
    ? `<div class="processing-dialog">
        <span class="helm-wheel" aria-hidden="true"><span>HELM</span></span>
        <strong class="processing-message">${escapeHtml(message)}</strong>
        <span class="processing-support">Keeping your plan together while this finishes.</span>
      </div>`
    : "";
  document.body.classList.toggle("processing-open", Boolean(message));
  $("#primary-content").setAttribute("aria-busy", message ? "true" : "false");
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
  addPanel.hidden = true;
  $(".context-column").hidden = !contextVisible;
  contentGrid.hidden = false;
  contentGrid.classList.toggle("fresh-start", !started);
  document.body.dataset.planState = started ? executionMode(next.state).toLowerCase() : "fresh";
  document.body.classList.toggle("dashboard-active", started);
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
  renderHelmFocus(next.state, next.active_gate);
  renderLenses(next.state, next.lenses);
  renderPrimary(next, showFeedback);
  primary.scrollTop = 0;
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

function renderHelmFocus(state, gate) {
  const mode = executionMode(state);
  const caughtUp = !gate && !(state.active_tasks || []).length;
  const acceptedDirection = (state.career_hypotheses || []).find((item) => item.status === "accepted");
  const needsLearningDecision = Boolean(
    caughtUp && acceptedDirection && directionAwaitingNextMove(state, acceptedDirection),
  );
  const hasActiveDirectionTest = Boolean(caughtUp && acceptedDirection && !needsLearningDecision);
  const scope = (gate?.affected_slices || []).map((slice) => labels[slice] || humanCopy(slice));
  $("#focus-state").textContent = mode === "PARALYZED"
    ? "Needs attention"
    : (mode === "COMPLETE"
      ? "Complete"
      : (needsLearningDecision ? "Next move" : (hasActiveDirectionTest ? "In the field" : (caughtUp ? "Caught up" : "On course"))));
  $("#focus-now").textContent = gate
    ? humanCopy(gate.title)
    : (mode === "COMPLETE"
      ? "No decision is waiting."
      : (needsLearningDecision
        ? "Decide what to do with what you learned."
        : (hasActiveDirectionTest ? "Run the test shown here, then add what happened." : "Your current plan is caught up.")));
  $("#focus-why").textContent = gate
    ? humanCopy(gate.why)
    : (mode === "COMPLETE"
      ? "This goal has been closed."
      : (needsLearningDecision
        ? "A real result should shape the next test—or the direction."
        : (hasActiveDirectionTest ? "The next useful input is evidence from the real world." : "Nothing needs your decision right now.")));
  $("#focus-scope").textContent = scope.length
    ? scope.join(" · ")
    : ((needsLearningDecision || hasActiveDirectionTest) ? "Work · Your story" : "No additional plan area is active.");
  renderPlanningRoute(state, gate);
}

function renderPlanningRoute(state, gate) {
  const decisions = state.decisions || [];
  const facts = state.facts || [];
  const acceptedDirection = (state.career_hypotheses || []).some((item) => item.status === "accepted");
  const gateId = gate?.id || "";
  const hasDecision = (id) => decisions.some((decision) => decision.gate_id === id);
  const hasDecisionPrefix = (prefix) => decisions.some((decision) => decision.gate_id?.startsWith(prefix));
  const hasSliceFact = (slice) => facts.some((fact) => (fact.affected_slices || []).includes(slice));
  const intent = (state.original_intents || []).join(" ").toLowerCase();
  const obstacle = (label, cleared, active, known) => ({
    label,
    state: active ? "active" : (cleared ? "cleared" : (known ? "ahead" : "unmapped")),
  });
  const obstacles = [
    obstacle("Set the timing", Boolean(state.transition_date || state.transition_month), gateId === "planned-transition-date", true),
    obstacle("Choose a direction", acceptedDirection, gateId === "career-direction", Boolean(state.career_target || state.career_hypotheses?.length || intent.match(/job|career|work/))),
    obstacle("Test it in real life", hasDecisionPrefix("path-task_") && !gateId.startsWith("path-task_"), gateId.startsWith("path-task_"), acceptedDirection),
    obstacle("Line up training", hasDecision("education-outcome"), gateId === "education-outcome", hasSliceFact("education") || /school|training|degree|certificate|education/.test(intent)),
    obstacle("Protect location needs", hasDecision("location-priority"), gateId === "location-priority", hasSliceFact("location") || /move|relocat|location|remote/.test(intent)),
    obstacle("Prepare your story", hasDecision("resume-target-role"), gateId === "resume-target-role", hasSliceFact("resume") || /resume|résumé|profile|application/.test(intent)),
  ];
  const labelsByState = { cleared: "Cleared", active: "Now", ahead: "Ahead", unmapped: "To map" };
  $("#planning-obstacles").innerHTML = obstacles.map((item) => `
    <li data-route-state="${item.state}">
      <span class="route-marker" aria-hidden="true">${item.state === "cleared" ? "✓" : ""}</span>
      <span class="route-label">${escapeHtml(item.label)}</span>
      <small>${labelsByState[item.state]}</small>
    </li>
  `).join("");
  $("#metric-active").textContent = String(obstacles.filter((item) => item.state === "cleared").length);
  $("#metric-latent").textContent = String(obstacles.filter((item) => item.state === "active").length);
  $("#metric-tasks").textContent = String(obstacles.filter((item) => item.state === "ahead" || item.state === "unmapped").length);
  const cleared = obstacles.filter((item) => item.state === "cleared").length;
  $("#planning-route-summary").textContent = `${cleared} of ${obstacles.length} cleared · see the full route`;
}

function buildLensTopics(state, lenses) {
  if (state.version === 0) {
    return [];
  }
  const facts = (state.facts || []).filter((fact) => fact.status !== "stale");
  const knownText = facts.map((fact) => fact.statement).join(" ").toLowerCase();
  const byId = new Map();
  lenses.forEach((lens) => {
    const relevantFacts = lens.name === "location"
      ? lens.facts.filter((fact) => !(/\b(remote|hybrid)\b/i.test(fact) && !/\b(relocat|move|location|commute|city|state|local|near)\b/i.test(fact)))
      : lens.facts;
    const meaningful = Boolean(
      lens.may_have_changed
      || lens.path_relevant
      || relevantFacts.length
      || lens.open_gates
      || lens.conflicted_gates
    );
    if (!meaningful) return;
    const score = (lens.may_have_changed ? 120 : 0) + (lens.path_relevant ? 80 : 30) + Math.min(lens.fact_count, 6) * 4;
    byId.set(lens.name, {
      id: lens.name,
      label: lens.label,
      slice: lens.name,
      summary: humanCopy(lens.summary),
      facts: relevantFacts.slice(-2),
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
        ? `A detail you supplied about ${rule.label === "PCS and moving" ? rule.label : rule.label.toLowerCase()} may affect this choice.`
        : `${rule.label} may affect the decision in front of you.`,
      facts: relevantFacts.slice(-2).map((fact) => fact.statement),
      score: 65 + Math.min(relevantFacts.length, 4) * 5,
      mayHaveChanged: false,
    });
  });
  return [...byId.values()]
    .sort((left, right) => right.score - left.score || left.label.localeCompare(right.label))
    .slice(0, 6);
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
      ? `<button id="update-lens-topic" class="button button-secondary" type="button">Add context about ${escapeHtml(topic.label.toLowerCase())}</button>`
      : "");
  preview.innerHTML = `
    <button id="dismiss-lens-preview" class="preview-close" type="button" aria-label="Dismiss preview">×</button>
    <div class="section-kicker">Another way to look at the current choice</div>
    <h3>${escapeHtml(topic.label)}</h3>
    ${topic.mayHaveChanged ? '<div class="impact-note">A recent decision may make this worth checking.</div>' : ""}
    <p>${escapeHtml(topic.summary)}</p>
    ${factMarkup}
    <p class="trust-note">No changes have been made.</p>
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
  $("#lens-cloud-shell").hidden = true;
  $("#open-lenses").hidden = !topics.length;
  $("#open-lenses").setAttribute("aria-expanded", "false");
  $("#lens-preview").hidden = true;
  nav.innerHTML = topics.map((topic, index) => `
    <button class="lens-button" data-lens="${escapeHtml(topic.id)}" data-weight="${index < 2 ? "3" : (index < 5 ? "2" : "1")}" data-impact="${Boolean(topic.mayHaveChanged)}" type="button" aria-expanded="false">
      <span>${escapeHtml(topic.label)}</span>
      <small>${topic.mayHaveChanged ? "Worth checking" : (topic.facts?.length ? "Context available" : "May change this choice")}</small>
    </button>
  `).join("");
  nav.querySelectorAll(".lens-button").forEach((button) => {
    const topic = topics.find((item) => item.id === button.dataset.lens);
    button.addEventListener("click", () => showLensPreview(topic, button));
  });
}

function openLensCloud() {
  const shell = $("#lens-cloud-shell");
  if (!$("#lens-nav").children.length) return;
  shell.hidden = false;
  $("#open-lenses").setAttribute("aria-expanded", "true");
  shell.scrollIntoView({ behavior: "smooth", block: "start" });
  $("#lens-cloud-title").setAttribute("tabindex", "-1");
  $("#lens-cloud-title").focus({ preventScroll: true });
}

function closeLensCloud() {
  $("#lens-cloud-shell").hidden = true;
  $("#open-lenses").setAttribute("aria-expanded", "false");
  $("#open-lenses").focus();
}

function renderTimeline(state) {
  const order = ["TODAY", "PREPARE", "SEPARATE", "TRANSITION", "STABILIZE"];
  const activeIndex = Math.max(0, order.indexOf(state.stage));
  document.querySelectorAll(".timeline-step").forEach((step, index) => {
    step.classList.toggle("active", index <= activeIndex);
  });
}

function renderPath(state) {
  const acceptedDirection = state.career_hypotheses?.find((item) => item.status === "accepted")?.title;
  $("#current-target").textContent = acceptedDirection
    || state.career_target
    || state.human_anchor
    || "Choose what matters first.";
  const timing = windowLabels[state.current_timeline_window];
  if (state.current_timeline_window === "PATH_IDENTITY") {
    $("#path-position").textContent = "Timing details will be added only when they affect the plan.";
  } else {
    $("#path-position").textContent = timing || "Current transition timing";
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

function renderStartingVector() {
  primary.innerHTML = `
    <div class="section-kicker">First, tell us where you are</div>
    <h2 id="primary-title">Let’s start with where you are now.</h2>
    <p class="gate-copy">Four quick answers help us show the right next step.</p>
    <form id="starting-vector-form" class="gate-form">
      <fieldset>
        <legend>Who are you planning for?</legend>
        <div class="choice-grid">
          <label class="choice-option"><input type="radio" name="operating-role" value="veteran_service_member" required><span>Veteran or service member</span></label>
          <label class="choice-option"><input type="radio" name="operating-role" value="spouse_partner"><span>Spouse or partner</span></label>
          <label class="choice-option"><input type="radio" name="operating-role" value="counselor_supporter"><span>Counselor or supporter</span></label>
        </div>
      </fieldset>
      <label for="starting-timeline">Where is the service member now?</label>
      <select id="starting-timeline" required>
        <option value="">Choose one</option>
        <option value="currently_serving">Currently serving, with no planned departure in the next year</option>
        <option value="leaving_within_12_months">Leaving within about 12 months</option>
        <option value="separated_within_last_year">Separated within the last year</option>
        <option value="separated_1_to_5_years">Separated 1–5 years ago</option>
        <option value="separated_more_than_5_years">Separated more than 5 years ago</option>
      </select>
      <div id="starting-month-wrap" hidden>
        <label id="starting-month-label" for="starting-month">Expected transition month</label>
        <input id="starting-month" type="month" autocomplete="off">
        <p class="trust-note">Month and year are enough.</p>
      </div>
      <label for="starting-service">Military branch</label>
      <select id="starting-service" required>
        <option value="">Choose one</option>
        ${Object.entries(serviceLabels).map(([value, label]) => `<option value="${value}">${label}</option>`).join("")}
      </select>
      <label for="starting-component">Service status</label>
      <select id="starting-component" required>
        <option value="">Choose one</option>
        <option value="active_duty">Active duty or full-time service</option>
        <option value="reserve">Reserve</option>
        <option value="national_guard">National Guard</option>
      </select>
      <button class="button button-primary" type="submit">Continue</button>
    </form>
    <p class="trust-note">These answers help choose your next question. They do not decide what you qualify for or take action for you.</p>
  `;
  $("#starting-vector-form").addEventListener("submit", submitStartingVector);
  $("#starting-timeline").addEventListener("change", (event) => {
    const needsMonth = ["currently_serving", "leaving_within_12_months", "separated_within_last_year"].includes(event.target.value);
    $("#starting-month-wrap").hidden = !needsMonth;
    $("#starting-month").required = needsMonth;
    $("#starting-month-label").textContent = event.target.value.startsWith("separated")
      ? "Last month in uniform"
      : "Expected transition month";
  });
}

async function submitStartingVector(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const operatingRole = form.querySelector('input[name="operating-role"]:checked')?.value;
  const lifecyclePosition = $("#starting-timeline").value;
  const service = $("#starting-service").value;
  const component = $("#starting-component").value;
  const transitionMonth = $("#starting-month").value || null;
  if (!operatingRole || !lifecyclePosition || !service || !component) {
    showInlineGuidance(primary, "Choose one answer for each starting question.");
    return;
  }
  const button = event.submitter;
  button.disabled = true;
  try {
    const next = await api("/api/starting-vector", {
      method: "POST",
      body: JSON.stringify({
        operating_role: operatingRole,
        lifecycle_position: lifecyclePosition,
        service,
        component,
        transition_month: transitionMonth,
        expected_version: envelope.state.version,
        idempotency_key: idempotencyKey(),
      }),
    });
    render(next, { showFeedback: false });
    focusPrimary();
  } catch (error) {
    if (error.status === 409) await loadState();
    showInlineGuidance(primary, error.message);
  } finally {
    button.disabled = false;
  }
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
      <h2 id="primary-title">You don’t need the whole plan yet.</h2>
      <p class="gate-copy">Start with a file, a screenshot, or a few words. We’ll help you find one next step.</p>
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
    <p class="trust-note front-door-trust">Nothing is saved yet. You will review anything we find before it changes your plan.</p>
  `;
  primary.querySelectorAll(".entry-choice").forEach((button) => {
    button.addEventListener("click", () => chooseColdEntry(button.dataset.entry));
  });
  $("#cold-artifact-file").addEventListener("change", uploadArtifact);
}

function itemList(items, emptyCopy) {
  const values = (items || []).filter(Boolean);
  if (!values.length) return `<p>${escapeHtml(emptyCopy)}</p>`;
  return `<ul>${values.map((item) => `<li>${escapeHtml(humanCopy(item))}</li>`).join("")}</ul>`;
}

function openDirectionLearning(item) {
  openAdd(false);
  setAddPanelCopy(
    "Test the direction",
    "Add what you learned",
    "Tell us what happened and what changed your view.",
  );
  inputContext = { kind: "direction-learning", title: item.title };
  const input = $("#input-text");
  input.value = "";
  input.placeholder = `What did you learn while testing ${item.title}? A sentence is enough.`;
  input.focus();
}

function openDirectionNextTest(item) {
  openAdd(false);
  setAddPanelCopy(
    "Keep moving",
    "Plan the next small test",
    "Turn what you learned into one concrete next test.",
  );
  inputContext = { kind: "direction-next-test", title: item.title };
  const input = $("#input-text");
  input.value = "";
  input.placeholder = `What is the next small test for ${item.title}? Say what you will try and what result you will watch for.`;
  input.focus();
}

function changeWorkingDirection(item) {
  openFogBank();
  $("#fog-bank-title").textContent = "What direction fits better now?";
  $("#fog-bank-text").value = `I want to explore a different direction instead of ${item.title}. `;
  showInlineGuidance($("#fog-bank-panel"), "Add the direction you want to explore, then review the change.");
  $("#fog-bank-text").focus();
}

function directionDecisionValues(state) {
  return (state.decisions || [])
    .filter((decision) => decision.gate_id?.startsWith("path-task_"))
    .map((decision) => humanCopy(decision.value))
    .filter(Boolean)
    .slice(-4);
}

function directionLearningValues(state, item) {
  const prefix = `While testing the ${item.title} work direction, I learned:`.toLowerCase();
  return (state.original_intents || [])
    .filter((value) => value.toLowerCase().startsWith(prefix))
    .map((value) => value.slice(prefix.length).trim())
    .filter(Boolean)
    .slice(-3);
}

function directionNextTestValues(state, item) {
  const prefix = `For my next test of the ${item.title} work direction:`.toLowerCase();
  return (state.original_intents || [])
    .filter((value) => value.toLowerCase().startsWith(prefix))
    .map((value) => value.slice(prefix.length).trim())
    .filter(Boolean);
}

function directionAwaitingNextMove(state, item) {
  const learningPrefix = `While testing the ${item.title} work direction, I learned:`.toLowerCase();
  const nextTestPrefix = `For my next test of the ${item.title} work direction:`.toLowerCase();
  const latestCycleEntry = [...(state.original_intents || [])]
    .reverse()
    .find((value) => {
      const normalized = value.toLowerCase();
      return normalized.startsWith(learningPrefix) || normalized.startsWith(nextTestPrefix);
    });
  return Boolean(latestCycleEntry?.toLowerCase().startsWith(learningPrefix));
}

function renderAcceptedExploration(item, state) {
  const decisions = directionDecisionValues(state);
  const learnings = directionLearningValues(state, item);
  const nextTestValues = directionNextTestValues(state, item);
  const experiment = nextTestValues.at(-1)
    || (decisions.length >= 3 ? decisions.at(-1) : humanCopy(item.first_experiment || item.next_step));
  const recordedDecisions = decisions.length >= 3 ? decisions.slice(0, -1) : decisions;
  if (directionAwaitingNextMove(state, item)) {
    primary.innerHTML = `
      <div class="section-kicker">Use what you learned</div>
      <h2 id="primary-title">What do you want to do next?</h2>
      <p class="gate-copy">You tested this direction and learned something real. Use that result now instead of leaving it buried in the plan.</p>
      <section class="learning-next-move">
        <span>YOUR LATEST RESULT</span>
        <strong>${escapeHtml(learnings.at(-1) || "A test result was recorded.")}</strong>
        <p>Choose whether to run a sharper test or reconsider the direction.</p>
        <div class="direction-actions next-move-actions">
          <button id="plan-next-direction-test" class="button button-primary" type="button">Plan the next small test</button>
          <button id="change-working-direction" class="button button-secondary" type="button">Change direction</button>
        </div>
      </section>
      <details class="working-record-details">
        <summary>Review the working direction</summary>
        <p><strong>${escapeHtml(item.title)}</strong></p>
        <p>Previous test: ${escapeHtml(experiment)}</p>
      </details>
    `;
    $("#plan-next-direction-test").addEventListener("click", () => openDirectionNextTest(item));
    $("#change-working-direction").addEventListener("click", () => changeWorkingDirection(item));
    return;
  }
  const nextTests = learnings.length
    ? ["Use the findings to decide whether to strengthen, change, or stop this direction. If you continue, define the next small test."]
    : (decisions.length >= 3
      ? ["Run the experiment you described, then add the result—especially anything that changed your trust in this direction."]
      : item.possible_gaps);
  primary.innerHTML = `
    <div class="section-kicker">Explore the direction</div>
    <h2 id="primary-title">Your working direction: ${escapeHtml(item.title)}</h2>
    <p class="gate-copy">This is the live decision record—not a permanent commitment. Add evidence whenever the real world changes your view.</p>
    <article class="direction-exploration">
      <section>
        <h3>What you’re testing</h3>
        <p>${escapeHtml(experiment)}</p>
      </section>
      <section class="decision-record">
        <h3>Decisions you made</h3>
        ${itemList(recordedDecisions, "No test decision has been recorded yet.")}
      </section>
      <section class="learning-record">
        <h3>What you learned</h3>
        ${itemList(learnings, "No test result has been added yet.")}
      </section>
      <section>
        <h3>What to test next</h3>
        ${itemList(nextTests, "What would have to be true for this direction to be worth continuing?")}
      </section>
      <section>
        <h3>What you already bring</h3>
        ${itemList(item.capability_matches, "No fit is being assumed yet.")}
      </section>
      <p class="evidence-note">What this is based on: ${escapeHtml(humanCopy((item.evidence || []).join(" · ")))}</p>
    </article>
    <button id="add-direction-learning" class="button button-primary" type="button">Add a test result</button>
  `;
  $("#add-direction-learning").addEventListener("click", () => openDirectionLearning(item));
}

function remainingDirectionTasks(state) {
  const decisions = state.decisions || [];
  const accepted = (state.career_hypotheses || []).find((item) => item.status === "accepted");
  if (!accepted) return [];
  let directionIndex = -1;
  decisions.forEach((decision, index) => {
    if (decision.gate_id === "career-direction" && decision.value?.startsWith("Explore: ")) directionIndex = index;
  });
  const completed = decisions
    .slice(directionIndex + 1)
    .filter((decision) => decision.gate_id?.startsWith("path-task_"))
    .length;
  const declaredTasks = [
    ...(accepted.questions_to_test || []).map((question) => ({
      title: question,
      reason: "This answer defines what the real-world test must resolve.",
    })),
    {
      title: accepted.first_experiment,
      reason: "This answer turns the direction into a bounded first action and a result you can evaluate.",
    },
  ];
  return declaredTasks.slice(completed);
}

function directionTaskQuestion(task) {
  const title = humanCopy(task.title || "").trim();
  return title || "Describe the next real-world check.";
}

function renderDecisionBundle(state, gate, tasks) {
  primary.innerHTML = `
    <div class="section-kicker">Make the whole test plan</div>
    <h2 id="primary-title">Answer the known questions together.</h2>
    <p class="gate-copy">These answers belong together. Review all of them once; we’ll save each one in the right place without making you step through three screens.</p>
    <form id="decision-bundle-form" class="gate-form decision-bundle">
      ${tasks.map((task, index) => `
        <section>
          <label for="bundle-answer-${index}"><strong>${index + 1}. ${escapeHtml(directionTaskQuestion(task))}</strong></label>
          <p>${escapeHtml(humanCopy(task.reason || "This answer shapes the next test."))}</p>
          <textarea id="bundle-answer-${index}" data-bundle-answer rows="3" maxlength="2000" required placeholder="A direct answer is enough."></textarea>
        </section>
      `).join("")}
      <button class="button button-primary" type="submit">Use these decisions</button>
      <p class="trust-note">Each answer keeps its own approval and record. This screen only removes unnecessary repetition.</p>
    </form>
    ${taskHorizon(tasks, true)}
  `;
  $("#decision-bundle-form").addEventListener("submit", submitDecisionBundle);
  $("#bundle-answer-0").focus();
}

async function submitDecisionBundle(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const answers = [...form.querySelectorAll("[data-bundle-answer]")].map((input) => input.value.trim());
  if (answers.some((answer) => !answer)) {
    showInlineGuidance(primary, "Answer each question before using this test plan.");
    return;
  }
  const button = event.submitter;
  button.disabled = true;
  button.textContent = "Saving the test plan…";
  let next = envelope;
  try {
    for (const answer of answers) {
      const currentGate = next.active_gate;
      if (!currentGate?.id?.startsWith("path-task_")) {
        throw new Error("The plan changed before every answer could be applied. The saved decisions remain visible.");
      }
      next = await api("/api/decision", {
        method: "POST",
        body: JSON.stringify({
          gate_id: currentGate.id,
          value: answer,
          expected_version: next.state.version,
          idempotency_key: idempotencyKey(),
        }),
      });
    }
    render(next, { showFeedback: true });
    focusPrimary();
    announce("Test plan saved.");
  } catch (error) {
    if (error.status === 409) await loadState();
    showInlineGuidance(primary, error.message);
  } finally {
    button.disabled = false;
    button.textContent = "Use these decisions";
  }
}

function renderHypothesisExploration(itemId) {
  const item = envelope?.state?.career_hypotheses?.find((candidate) => candidate.id === itemId);
  if (!item || !envelope.active_gate || envelope.active_gate.id !== "career-direction") {
    renderPrimary(envelope);
    focusPrimary();
    return;
  }
  primary.innerHTML = `
    <div class="section-kicker">Explore before deciding — nothing changed yet</div>
    <h2 id="primary-title">${escapeHtml(item.title)}</h2>
    <p class="gate-copy">${escapeHtml(humanCopy(item.rationale))}</p>
    <article class="direction-exploration">
      <section>
        <h3>A useful first experiment</h3>
        <p>${escapeHtml(humanCopy(item.first_experiment || item.next_step))}</p>
      </section>
      <section>
        <h3>Questions this test should answer</h3>
        ${itemList(item.questions_to_test, "What would have to be true for this direction to be worth continuing?")}
      </section>
      <section>
        <h3>Why it may fit</h3>
        ${itemList(item.capability_matches, "No fit is being assumed yet.")}
      </section>
      <section>
        <h3>What to check</h3>
        ${itemList(item.possible_gaps, "You still need a real-world answer here.")}
      </section>
      <p class="evidence-note">What this is based on: ${escapeHtml(humanCopy((item.evidence || []).join(" · ")))}</p>
    </article>
    <form id="gate-form" class="gate-form">
      <button id="accept-direction" class="button button-primary" data-value="explore:${escapeHtml(item.title)}" type="button">Use this as my working direction</button>
      <button id="back-to-directions" class="button button-quiet" type="button">Back to the other directions</button>
    </form>
    <p class="trust-note">Exploring this page did not save or change your plan.</p>
  `;
  $("#accept-direction").addEventListener("click", (event) => submitDecision({ preventDefault() {}, currentTarget: event.currentTarget }));
  $("#back-to-directions").addEventListener("click", () => {
    renderPrimary(envelope);
    focusPrimary();
  });
  focusPrimary();
}

function conversationLead(horizon, visible) {
  if (!visible || !horizon?.acknowledgment) return "";
  return `
    <div class="conversation-lead">
      <p class="conversation-ack">${escapeHtml(humanCopy(horizon.acknowledgment))}</p>
      ${horizon.consequence ? `<p>${escapeHtml(humanCopy(horizon.consequence))}</p>` : ""}
    </div>
  `;
}

function renderPrimary(next, showConversationLead = false) {
  const state = next.state;
  const gate = next.active_gate;
  const acquisition = next.acquisition_horizon;
  const mode = executionMode(state);
  if (!state.starting_vector_complete && state.version === 0) {
    renderStartingVector();
    return;
  }
  if (!state.human_anchor && !state.original_intents.length) {
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
    if (accepted) {
      renderAcceptedExploration(accepted, state);
      return;
    }
    const hasTasks = Boolean(state.active_tasks?.length);
    primary.innerHTML = `
      <h2 id="primary-title">${hasTasks ? "Your next steps are ready." : "Your plan is caught up for now."}</h2>
      <p class="gate-copy">${hasTasks ? "Work through these steps in the order that fits your timing. Add an update when something changes." : "Add something whenever your timing, priorities, work preferences, education, or location changes."}</p>
      ${taskHorizon(state.active_tasks, true)}
      <button id="add-more" class="button ${hasTasks ? "button-quiet" : "button-primary"}" type="button">Add an update</button>
    `;
    $("#add-more").addEventListener("click", () => openAdd(false));
    return;
  }
  const directionTasks = remainingDirectionTasks(state);
  if (gate.id.startsWith("path-task_") && directionTasks.length > 1) {
    renderDecisionBundle(state, gate, directionTasks);
    return;
  }
  const hypotheses = state.career_hypotheses.filter((item) => item.status === "candidate");
  let control = "";
  if (gate.surface === "date") {
    control = `<label for="gate-value">Expected date</label><input id="gate-value" type="date" min="${new Date().toISOString().slice(0, 10)}">`;
  } else if ((gate.surface === "choice" || gate.surface === "conflict") && gate.options.length) {
    control = `<div class="choice-grid">${gate.options.map((option) => `
      <label class="choice-option"><input type="radio" name="gate-choice" value="${escapeHtml(option)}"><span>${escapeHtml(humanCopy(option))}</span></label>
    `).join("")}</div>
    ${gate.surface === "choice" ? `
      <details class="natural-answer">
        <summary>Tell me in your own words</summary>
        <label for="gate-natural-value">What are you picturing?</label>
        <textarea id="gate-natural-value" rows="4" maxlength="4000" placeholder="Say it naturally. Relevant details can carry forward to the next step."></textarea>
      </details>
    ` : ""}`;
  } else if (gate.surface === "compare" && hypotheses.length) {
    control = `
      <div class="carousel-heading">
        <div>
          <span id="direction-position" class="carousel-position" aria-live="polite">${hypotheses.length} directions to consider</span>
          <p class="direction-instruction">These are alternatives, not steps. Explore the one that feels most useful.</p>
        </div>
        <div class="carousel-controls" aria-label="Browse directions">
          <button id="direction-previous" class="carousel-button direction-nav-button" type="button" aria-label="Previous direction">← Previous</button>
          <button id="direction-next" class="carousel-button direction-nav-button" type="button" aria-label="Next direction">Next →</button>
        </div>
      </div>
      <div id="direction-actions" class="direction-actions" aria-live="polite">
        <button id="choose-current-direction" class="button button-primary" data-value="explore:${escapeHtml(hypotheses[0].title)}" type="button">Explore this direction</button>
        <button id="detail-current-direction" class="button button-secondary" data-id="${escapeHtml(hypotheses[0].id)}" type="button">See test details</button>
        <button id="skip-current-direction" class="button button-quiet" data-value="reject:${escapeHtml(hypotheses[0].title)}" type="button">Skip this option</button>
      </div>
      <div id="direction-carousel" class="hypothesis-grid" tabindex="0">${hypotheses.map((item, index) => `
      <article class="hypothesis" aria-label="Direction ${index + 1} of ${hypotheses.length}">
        <h3>${escapeHtml(item.title)}</h3>
        <div class="hypothesis-details">
          <p>${escapeHtml(humanCopy(item.rationale))}</p>
          <p><strong>Why it may fit</strong><br>${escapeHtml(humanCopy(item.capability_matches.slice(0, 2).join(" · ")))}</p>
          <p><strong>What we’d need to check</strong><br>${escapeHtml(humanCopy(item.possible_gaps.slice(0, 1).join(" · ")))}</p>
        </div>
      </article>
    `).join("")}</div>`;
  } else {
    control = `<label for="gate-value">Your answer</label><textarea id="gate-value" rows="4" placeholder="A sentence is enough."></textarea>`;
  }
  const primaryAction = gate.id === "career-direction" && gate.surface === "text"
    ? "Turn this into directions"
    : "Use this decision";
  primary.innerHTML = `
    ${mode === "PARALYZED" ? '<div class="attention-note">These choices cannot both guide the next step. Your answer below will clear the conflict.</div>' : ""}
    ${conversationLead(acquisition, showConversationLead)}
    <h2 id="primary-title">${escapeHtml(humanQuestion(acquisition?.prompt || gate.question))}</h2>
    <p class="gate-copy">${escapeHtml(humanCopy(gate.why))}</p>
    <form id="gate-form" class="gate-form">
      ${control}
      ${gate.surface === "compare" && hypotheses.length ? "" : `<button class="button button-primary" type="submit">${primaryAction}</button>`}
    </form>
    ${taskHorizon(state.active_tasks)}
  `;
  const form = $("#gate-form");
  form.addEventListener("submit", submitDecision);
  if (gate.surface === "compare" && hypotheses.length) {
    $("#choose-current-direction").addEventListener("click", (event) => submitDecision({ preventDefault() {}, currentTarget: event.currentTarget }));
    $("#skip-current-direction").addEventListener("click", (event) => submitDecision({ preventDefault() {}, currentTarget: event.currentTarget }));
    $("#detail-current-direction").addEventListener("click", (event) => renderHypothesisExploration(event.currentTarget.dataset.id));
    bindDirectionCarousel(hypotheses);
  }
}

function bindDirectionCarousel(hypotheses) {
  const total = hypotheses.length;
  const track = $("#direction-carousel");
  const previous = $("#direction-previous");
  const next = $("#direction-next");
  const position = $("#direction-position");
  if (!track || !previous || !next || !position) return;

  let activeIndex = 0;
  let scrollTimer;
  const reflect = () => {
    const current = hypotheses[activeIndex];
    position.textContent = `${total} directions to consider`;
    previous.disabled = activeIndex === 0;
    next.disabled = activeIndex === total - 1;
    $("#choose-current-direction").textContent = "Explore this direction";
    $("#choose-current-direction").dataset.value = `explore:${current.title}`;
    $("#detail-current-direction").dataset.id = current.id;
    $("#skip-current-direction").dataset.value = `reject:${current.title}`;
  };
  const update = (index, behavior = "smooth") => {
    activeIndex = Math.max(0, Math.min(total - 1, index));
    track.scrollTo({ left: track.clientWidth * activeIndex, behavior });
    reflect();
  };

  previous.addEventListener("click", () => update(activeIndex - 1));
  next.addEventListener("click", () => update(activeIndex + 1));
  track.addEventListener("scroll", () => {
    clearTimeout(scrollTimer);
    scrollTimer = setTimeout(() => {
      if (!track.clientWidth) return;
      activeIndex = Math.max(0, Math.min(total - 1, Math.round(track.scrollLeft / track.clientWidth)));
      reflect();
    }, 100);
  }, { passive: true });
  update(0, "auto");
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
  panel.innerHTML = `
    <details class="deferred-impact">
      <summary>Related check for later</summary>
      <p>${escapeHtml(humanCopy(impact.message))}</p>
      <h2>${escapeHtml(humanCopy(impact.question))}</h2>
      <div class="deferred-impact-actions">${impactControls(impact)}</div>
    </details>
  `;
  wireImpact(panel.querySelector(".deferred-impact-actions"), impact);
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
  $("#changed-list").innerHTML = feedback.consequences.slice(0, 2).map((item) => `<li>${escapeHtml(humanCopy(item))}</li>`).join("");
}

function showInspection(panel) {
  clearAnnouncement();
  [addPanel, reviewPanel, $("#lens-panel"), $("#history-panel"), $("#what-if-panel"), $("#fog-bank-panel")].forEach((item) => {
    item.hidden = item !== panel;
  });
  contentGrid.hidden = true;
  $(".control-nav").hidden = true;
  $("#orientation-shell").hidden = true;
  document.body.classList.add("inspection-open");
  document.body.classList.remove("input-open");
  panel.hidden = false;
  panel.scrollIntoView({ behavior: "smooth", block: "start" });
  const heading = panel.querySelector("h2");
  heading?.setAttribute("tabindex", "-1");
  heading?.focus({ preventScroll: true });
}

function restoreWorkspace(returnTo = null) {
  document.body.classList.remove("inspection-open");
  contentGrid.hidden = false;
  const started = planHasStarted(envelope.state);
  $("#orientation-shell").hidden = !started;
  $(".control-nav").hidden = !started;
  addPanel.hidden = true;
  returnTo?.focus();
}

function closeInspection(panel, returnTo) {
  panel.hidden = true;
  restoreWorkspace(returnTo);
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
    const meaningful = [];
    let lastFingerprint = null;
    history.entries.slice().reverse().forEach((entry) => {
      const anchor = entry.human_anchor?.trim();
      const latestDecision = entry.closed_decisions.at(-1) || "";
      const fingerprint = `${anchor || ""}\u001f${latestDecision}`;
      if (!anchor || fingerprint === lastFingerprint) return;
      meaningful.push(entry);
      lastFingerprint = fingerprint;
    });
    if (!meaningful.length) {
      $("#history-list").innerHTML = "<p>No governed decision has been recorded yet.</p>";
      return;
    }
    $("#history-list").innerHTML = meaningful.slice(0, 8).map((entry) => `
      <button class="history-version" data-version="${entry.version}" type="button">
        <strong>${entry.current ? "Current plan" : "Earlier plan"}</strong>
        <span>${escapeHtml(humanCopy(entry.human_anchor))}</span>
        <small>${escapeHtml(humanCopy(entry.closed_decisions.at(-1) || entry.change_summary))}</small>
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
        <div class="section-kicker">Earlier plan — view only</div>
        <h3>${escapeHtml(humanCopy(entry.human_anchor || "No target was declared"))}</h3>
        <p>${entry.open_gates.length ? `Still unanswered then: ${escapeHtml(humanCopy(entry.open_gates.join(" · ")))}` : "No unanswered question was recorded."}</p>
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
      <section><div class="section-kicker">Possible plan</div><ul>${branch.hypothetical_summary.map((item) => `<li>${escapeHtml(whatIfCopy(item))}</li>`).join("")}</ul></section>
    </div>
    ${branch.conflicts.length ? `<div class="conflict-note"><strong>Conflict to resolve</strong><ul>${branch.conflicts.map((item) => `<li>${escapeHtml(whatIfCopy(item))}</li>`).join("")}</ul></div>` : ""}
    <h3>${branch.modification_kind === "target_experiment" ? "If you add this possibility" : "If you use this plan"}</h3>
    <ul>${branch.consequences.map((item) => `<li>${escapeHtml(whatIfCopy(item))}</li>`).join("")}</ul>
    <p class="trust-note">Nothing changes until you choose “${branch.modification_kind === "target_experiment" ? "Add this to my plan" : "Use this plan"}.”</p>
    <div class="button-row">
      <button id="discard-what-if" class="button button-quiet" type="button">Keep my current plan</button>
      <button id="promote-what-if" class="button button-primary" type="button">${branch.modification_kind === "target_experiment" ? "Add this to my plan" : "Use this plan"}</button>
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

function openFogBank() {
  pendingFogBank = null;
  $("#fog-bank-title").textContent = "What are we missing?";
  $("#fog-bank-form").hidden = false;
  $("#fog-bank-result").hidden = true;
  $("#fog-bank-text").value = "";
  showInspection($("#fog-bank-panel"));
  $("#fog-bank-text").focus();
}

async function examineFogBank(event) {
  event.preventDefault();
  const text = $("#fog-bank-text").value.trim();
  if (!text) {
    showInlineGuidance($("#fog-bank-panel"), "Describe what the current plan is missing or getting wrong.");
    return;
  }
  const button = event.submitter;
  button.disabled = true;
  try {
    pendingFogBank = await api("/api/fog-bank", {
      method: "POST",
      body: JSON.stringify({ text, source_version: envelope.state.version }),
    });
    renderFogBank(pendingFogBank);
  } catch (error) {
    if (error.status === 409) await loadState();
    showInlineGuidance($("#fog-bank-panel"), error.message);
  } finally {
    button.disabled = false;
  }
}

function renderFogBank(proposal) {
  const result = $("#fog-bank-result");
  $("#fog-bank-panel").querySelector(".inline-guidance")?.remove();
  result.hidden = false;
  if (proposal.status === "clarification_needed") {
    result.innerHTML = `
      <div class="guidance-note">
        <h3>One more detail</h3>
        <p>${escapeHtml(proposal.clarification_question)}</p>
        <p><strong>Add your answer to the box above, then choose “Review this plan change” again.</strong></p>
        <p class="trust-note">Your current plan has not changed.</p>
      </div>
    `;
    $("#fog-bank-text").focus();
    return;
  }
  $("#fog-bank-form").hidden = true;
  result.innerHTML = `
    <div class="guidance-note"><strong>Nothing has changed yet.</strong> ${escapeHtml(proposal.summary)}</div>
    ${proposal.conflicts.length ? `<h3>What no longer fits</h3><ul>${proposal.conflicts.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>` : ""}
    <h3>Suggested plan update</h3>
    <ul>${proposal.changes.map((change) => `<li><strong>${escapeHtml(change.reason)}</strong><br><span>${escapeHtml(humanCopy(change.current_value || "Not set"))} → ${escapeHtml(humanCopy(change.proposed_value || "Remove from the active plan"))}</span></li>`).join("")}</ul>
    <p class="trust-note">Other parts of your plan may need another look. Nothing changes unless you approve it.</p>
    <div class="button-row">
      <button id="cancel-fog-bank" class="button button-quiet" type="button">Keep my current plan</button>
      <button id="accept-fog-bank" class="button button-primary" type="button">Use this update</button>
    </div>
  `;
  $("#cancel-fog-bank").addEventListener("click", () => {
    pendingFogBank = null;
    closeInspection($("#fog-bank-panel"), $("#open-fog-bank"));
  });
  $("#accept-fog-bank").addEventListener("click", acceptFogBank);
}

async function acceptFogBank() {
  if (!pendingFogBank?.token) return;
  const button = $("#accept-fog-bank");
  button.disabled = true;
  try {
    const next = await api("/api/fog-bank/accept", {
      method: "POST",
      body: JSON.stringify({
        token: pendingFogBank.token,
        expected_version: envelope.state.version,
        idempotency_key: idempotencyKey(),
      }),
    });
    pendingFogBank = null;
    resetInputContext();
    $("#input-text").value = "";
    $("#fog-bank-panel").hidden = true;
    document.body.classList.remove("inspection-open");
    contentGrid.hidden = false;
    render(next, { showFeedback: true });
    focusPrimary();
    announce("Saved.");
  } catch (error) {
    if (error.status === 409) await loadState();
    showInlineGuidance($("#fog-bank-panel"), error.message);
    button.disabled = false;
  }
}

function openAdd(fileFirst) {
  reviewReturn = "add";
  resetInputContext();
  resetAddPanelCopy();
  reviewPanel.hidden = true;
  addPanel.hidden = false;
  document.body.classList.add("input-open");
  addPanel.classList.remove("input-attention");
  void addPanel.offsetWidth;
  addPanel.classList.add("input-attention");
  addPanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
  if (fileFirst) {
    $("#artifact-file").click();
  } else {
    $("#input-text").focus();
  }
}

function closeAdd() {
  resetInputContext();
  resetAddPanelCopy();
  $("#input-text").value = "";
  $("#artifact-file").value = "";
  $("#file-status").textContent = "PDF, DOCX, TXT, PNG, or JPG · 5 MB max";
  addPanel.querySelector(".inline-guidance")?.remove();
  addPanel.hidden = true;
  document.body.classList.remove("input-open");
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
  if (isPlanChangeRequest(text)) {
    openFogBank();
    $("#fog-bank-title").textContent = "What do you want to change?";
    $("#fog-bank-text").value = text;
    showInlineGuidance($("#fog-bank-panel"), "Your words are ready below. Add any detail you want, then review the change.");
    $("#fog-bank-text").focus();
    return;
  }
  reviewReturn = "add";
  const orientedText = inputContext?.kind === "direction-learning"
    ? `While testing the ${inputContext.title} work direction, I learned: ${text}`
    : (inputContext?.kind === "direction-next-test"
      ? `For my next test of the ${inputContext.title} work direction: ${text}`
      : text);
  await requestOrientation(orientedText, event.submitter);
}

function isPlanChangeRequest(text) {
  const normalized = text.toLowerCase().replace(/[^a-z0-9\s]/g, " ").replace(/\s+/g, " ").trim();
  const plan = "(?:my|the)?\\s*(?:career|transition|current)?\\s*plans?";
  const directChange = new RegExp(`\\b(?:change|update|fix|redo|revise|edit)\\s+${plan}\\b`);
  const makeChange = new RegExp(`\\bmake\\s+changes?\\s+to\\s+${plan}\\b`);
  const hasWorkingDirection = (envelope?.state?.career_hypotheses || []).some((item) => item.status === "accepted");
  const declaresNewDirection = /\b(?:i\s+)?(?:now\s+)?want\s+to\s+(?:build|become|work\s+as|focus\s+on|pursue|explore)\b/.test(normalized);
  return directChange.test(normalized) || makeChange.test(normalized) || (hasWorkingDirection && declaresNewDirection);
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
  const originalLabel = submit?.textContent;
  if (submit) {
    submit.disabled = true;
    submit.textContent = "Reviewing this…";
  }
  try {
    pendingOrientation = await api("/api/orient", { method: "POST", body: JSON.stringify({ text }) });
    showReview(pendingOrientation);
  } catch (error) {
    announce(error.message, true);
  } finally {
    if (submit) {
      submit.disabled = false;
      submit.textContent = originalLabel || "Review update";
    }
  }
}

function showReview(result) {
  const needsClarification = !result.sufficient;
  const isUnrelated = needsClarification
    && (result.affected_slices || []).length === 0
    && envelope?.state?.starting_vector_complete;
  $("#review-text-label").hidden = Boolean(isUnrelated);
  $("#review-text").hidden = Boolean(isUnrelated);
  $("#confirm-review").hidden = Boolean(isUnrelated);
  $("#cancel-review").textContent = isUnrelated ? "Back to my plan" : "Go back";
  if (isUnrelated) {
    $("#review-title").textContent = "This doesn’t change your plan.";
    $("#review-summary").textContent = "We kept your current plan as-is because this detail is not connected to a decision you are working on.";
    $("#review-statements").innerHTML = result.statements.map((item) => `<li>${escapeHtml(item.text)}</li>`).join("");
    $("#review-trust").textContent = "Nothing was saved, and you do not need to explain it further.";
    $("#review-text").value = result.reviewed_input;
    showInspection(reviewPanel);
    return;
  }
  $("#review-title").textContent = needsClarification
    ? "One question before this can shape your plan."
    : "Check this before it shapes your plan.";
  $("#review-summary").textContent = needsClarification
    ? (result.clarification_question || "What decision would you most like help with first?")
    : result.summary;
  $("#review-statements").innerHTML = result.statements.map((item) => `<li>${escapeHtml(item.text)}</li>`).join("") || "<li>We need one clarification before this can shape your plan.</li>";
  $("#review-text-label").textContent = needsClarification
    ? "Add your answer to the words you already shared"
    : "Correct anything that is off";
  $("#review-trust").textContent = needsClarification
    ? "Your words are kept. Nothing is saved until your answer gives the plan a clear starting point."
    : "Nothing changes until you choose “Use this in my plan.” AI suggestions are never saved as facts on their own.";
  $("#confirm-review").textContent = needsClarification ? "Check this clarification" : "Use this in my plan";
  $("#review-text").value = result.reviewed_input;
  showInspection(reviewPanel);
}

async function confirmReview() {
  if (!pendingOrientation || !envelope) return;
  const reviewedInput = $("#review-text").value.trim();
  if (!pendingOrientation.sufficient && reviewedInput === pendingOrientation.reviewed_input) {
    showInlineGuidance(reviewPanel, "Add one detail that answers the question above.");
    $("#review-text").focus();
    return;
  }
  if (!pendingOrientation.sufficient || reviewedInput !== pendingOrientation.reviewed_input) {
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
    if (reviewReturn === "add") {
      $("#input-text").value = "";
      resetInputContext();
    }
    render(next, { showFeedback: true });
    $("#primary").scrollIntoView({ behavior: "smooth", block: "start" });
    focusPrimary();
    announce("Saved.");
  } catch (error) {
    if (error.status === 409) {
      await reloadKeepingDraft(reviewedInput, "dock");
    } else {
      announce(error.message, true);
    }
  } finally {
    button.disabled = false;
    button.textContent = pendingOrientation?.sufficient ? "Use this in my plan" : "Check this clarification";
  }
}

async function submitDecision(event) {
  event.preventDefault();
  const gate = envelope?.active_gate;
  if (!gate) return;
  let value = event.currentTarget?.dataset?.value || "";
  const naturalValue = $("#gate-natural-value")?.value?.trim() || "";
  if (!value && naturalValue) {
    await submitAcquisition(gate, naturalValue);
    return;
  }
  if (!value && (gate.surface === "choice" || gate.surface === "conflict")) {
    value = document.querySelector('input[name="gate-choice"]:checked')?.value || "";
  }
  if (!value) value = $("#gate-value")?.value?.trim() || "";
  if (!value) {
    showInlineGuidance(primary, "Add your decision first.");
    return;
  }
  if (gate.id === "career-direction" && gate.surface === "text") {
    reviewReturn = "plan";
    await requestOrientation(value, event.submitter);
    return;
  }
  if (gate.surface === "text") {
    await submitAcquisition(gate, value);
    return;
  }
  const buttons = document.querySelectorAll("#gate-form button");
  buttons.forEach((button) => { button.disabled = true; });
  setProcessing("Working through what you shared…");
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
    if (error.status === 409) {
      await reloadKeepingDraft(value, "gate");
    } else {
      showInlineGuidance(primary, error.message);
    }
  } finally {
    buttons.forEach((button) => { button.disabled = false; });
    setProcessing();
  }
}

async function submitAcquisition(gate, text) {
  const buttons = document.querySelectorAll("#gate-form button");
  buttons.forEach((button) => { button.disabled = true; });
  setProcessing("Working through what you shared…");
  try {
    const result = await api("/api/acquire", {
      method: "POST",
      body: JSON.stringify({
        gate_id: gate.id,
        text,
        expected_version: envelope.state.version,
        idempotency_key: idempotencyKey(),
      }),
    });
    if (result.status === "clarification_needed") {
      showInlineGuidance(primary, result.message);
      const input = $("#gate-natural-value") || $("#gate-value");
      if (input) {
        input.value = result.carry_forward || text;
        input.focus();
      }
      buttons.forEach((button) => { button.disabled = false; });
      return;
    }
    render(result.envelope, { showFeedback: true });
    focusPrimary();
    announce("Saved.");
  } catch (error) {
    if (error.status === 409) {
      await reloadKeepingDraft(text, "gate");
    } else {
      showInlineGuidance(primary, error.message);
    }
    buttons.forEach((button) => { button.disabled = false; });
  } finally {
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

async function reloadKeepingDraft(draft, destination = "dock") {
  await loadState();
  restoreWorkspace();
  const input = destination === "gate"
    ? ($("#gate-natural-value") || $("#gate-value"))
    : $("#input-text");
  if (input) {
    input.value = draft;
    input.focus();
  }
  showInlineGuidance(
    destination === "gate" ? primary : addPanel,
    "Your plan advanced while you were writing. The newest decision is loaded and your draft is preserved for review.",
  );
}

$("#add-context-top").addEventListener("click", () => openAdd(false));
$("#close-add").addEventListener("click", closeAdd);
$("#input-form").addEventListener("submit", orientInput);
$("#artifact-file").addEventListener("change", uploadArtifact);
$("#cancel-review").addEventListener("click", () => {
  reviewPanel.hidden = true;
  if (reviewReturn === "add") {
    restoreWorkspace();
    openAdd(false);
  } else {
    restoreWorkspace($("#gate-value") || $("#cold-input-text"));
  }
});
$("#confirm-review").addEventListener("click", confirmReview);
$("#open-history").addEventListener("click", openHistory);
$("#open-lenses").addEventListener("click", openLensCloud);
$("#close-lens-cloud").addEventListener("click", closeLensCloud);
$("#open-what-if").addEventListener("click", () => {
  whatIfSourceVersion = null;
  openWhatIf();
});
$("#open-fog-bank").addEventListener("click", openFogBank);
$("#close-lens").addEventListener("click", () => closeInspection($("#lens-panel"), $("#lens-nav .lens-button")));
$("#close-history").addEventListener("click", () => closeInspection($("#history-panel"), $("#open-history")));
$("#close-what-if").addEventListener("click", () => {
  pendingWhatIf = null;
  whatIfSourceVersion = null;
  closeInspection($("#what-if-panel"), $("#open-what-if"));
});
$("#close-fog-bank").addEventListener("click", () => {
  pendingFogBank = null;
  closeInspection($("#fog-bank-panel"), $("#open-fog-bank"));
});
$("#what-if-form").addEventListener("submit", createWhatIf);
$("#fog-bank-form").addEventListener("submit", examineFogBank);
$("#open-planning-route").addEventListener("click", () => $("#planning-route-dialog").showModal());
$("#close-planning-route").addEventListener("click", () => $("#planning-route-dialog").close());
$("#planning-route-dialog").addEventListener("click", (event) => {
  if (event.target === $("#planning-route-dialog")) $("#planning-route-dialog").close();
});
$("#boot-shell").hidden = true;
contentGrid.hidden = false;
contentGrid.classList.add("fresh-start");
primary.setAttribute("aria-busy", "true");
renderColdFrontDoor();
loadState();
