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
  addPanel.hidden = !started;
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
  const scope = (gate?.affected_slices || []).map((slice) => labels[slice] || humanCopy(slice));
  const heldBack = Number(state.latent_fact_count || 0);
  const activeFacts = (state.facts || []).filter((fact) => fact.status !== "stale").length;
  $("#focus-state").textContent = mode === "PARALYZED" ? "Needs attention" : (mode === "COMPLETE" ? "Complete" : "Active");
  $("#focus-now").textContent = gate ? humanCopy(gate.title) : (mode === "COMPLETE" ? "No decision is waiting." : "Your current plan is caught up.");
  $("#focus-scope").textContent = scope.length ? scope.join(" · ") : "No additional plan area is active.";
  $("#focus-background").textContent = heldBack
    ? `${heldBack} ${heldBack === 1 ? "detail stays" : "details stay"} in the background until needed.`
    : "Other details stay available without being pulled into this decision.";
  $("#metric-active").textContent = String(activeFacts);
  $("#metric-latent").textContent = String(heldBack);
  $("#metric-tasks").textContent = String((state.active_tasks || []).length);
}

function bindFocusCarousel() {
  const track = $("#focus-carousel");
  const previous = $("#focus-previous");
  const next = $("#focus-next");
  const position = $("#focus-position");
  if (!track || !previous || !next || !position) return;
  const total = track.children.length;
  let activeIndex = 0;
  let scrollTimer;
  const reflect = () => {
    position.textContent = `Focus ${activeIndex + 1} of ${total}`;
    previous.disabled = activeIndex === 0;
    next.disabled = activeIndex === total - 1;
  };
  const update = (index) => {
    activeIndex = Math.max(0, Math.min(total - 1, index));
    track.scrollTo({ left: track.clientWidth * activeIndex, behavior: "smooth" });
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
  reflect();
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
  const input = $("#input-text");
  input.value = "";
  input.placeholder = `What did you learn while testing ${item.title}? A sentence is enough.`;
  input.focus();
}

function renderAcceptedExploration(item) {
  primary.innerHTML = `
    <div class="section-kicker">Explore the direction</div>
    <h2 id="primary-title">Start by testing ${escapeHtml(item.title)}.</h2>
    <p class="gate-copy">You’re not locked in. The next move is to try one thing in the real world and see what you learn.</p>
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
        <h3>What you already bring</h3>
        ${itemList(item.capability_matches, "No fit is being assumed yet.")}
      </section>
      <section>
        <h3>What you still need to find out</h3>
        ${itemList(item.possible_gaps, "You still need a real-world answer here.")}
      </section>
      <p class="evidence-note">What this is based on: ${escapeHtml(humanCopy((item.evidence || []).join(" · ")))}</p>
    </article>
    <button id="add-direction-learning" class="button button-primary" type="button">Add what I learn</button>
  `;
  $("#add-direction-learning").addEventListener("click", () => openDirectionLearning(item));
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
      renderAcceptedExploration(accepted);
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
        <span id="direction-position" class="carousel-position" aria-live="polite">Direction 1 of ${hypotheses.length}</span>
        <div class="carousel-controls" aria-label="Browse directions">
          <button id="direction-previous" class="carousel-button" type="button" aria-label="Previous direction">←</button>
          <button id="direction-next" class="carousel-button" type="button" aria-label="Next direction">→</button>
        </div>
      </div>
      <div id="direction-carousel" class="hypothesis-grid" tabindex="0">${hypotheses.map((item, index) => `
      <article class="hypothesis" aria-label="Direction ${index + 1} of ${hypotheses.length}">
        <h3>${escapeHtml(item.title)}</h3>
        <p>${escapeHtml(humanCopy(item.rationale))}</p>
        <p><strong>What may already fit</strong><br>${escapeHtml(humanCopy(item.capability_matches.join(" · ")))}</p>
        <p><strong>What to check</strong><br>${escapeHtml(humanCopy(item.possible_gaps.join(" · ")))}</p>
        <div class="evidence-note">Based on ${escapeHtml(humanCopy(item.evidence.join(" · ")))}</div>
        <div class="hypothesis-actions">
          <button class="button button-secondary hypothesis-explore" data-id="${escapeHtml(item.id)}" type="button">Explore this direction</button>
          <button class="button button-quiet hypothesis-choice" data-value="reject:${escapeHtml(item.title)}" type="button">Not for me</button>
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
  document.querySelectorAll(".hypothesis-choice").forEach((button) => {
    button.addEventListener("click", () => submitDecision({ preventDefault() {}, currentTarget: button }));
  });
  document.querySelectorAll(".hypothesis-explore").forEach((button) => {
    button.addEventListener("click", () => renderHypothesisExploration(button.dataset.id));
  });
  if (gate.surface === "compare" && hypotheses.length) {
    bindDirectionCarousel(hypotheses.length);
  }
}

function bindDirectionCarousel(total) {
  const track = $("#direction-carousel");
  const previous = $("#direction-previous");
  const next = $("#direction-next");
  const position = $("#direction-position");
  if (!track || !previous || !next || !position) return;

  let activeIndex = 0;
  let scrollTimer;
  const reflect = () => {
    position.textContent = `Direction ${activeIndex + 1} of ${total}`;
    previous.disabled = activeIndex === 0;
    next.disabled = activeIndex === total - 1;
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
  [addPanel, reviewPanel, $("#lens-panel"), $("#history-panel"), $("#what-if-panel"), $("#fog-bank-panel")].forEach((item) => {
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

function restoreWorkspace(returnTo = null) {
  document.body.classList.remove("inspection-open");
  contentGrid.hidden = false;
  const started = planHasStarted(envelope.state);
  $("#orientation-shell").hidden = !started;
  $(".control-nav").hidden = !started;
  addPanel.hidden = !started;
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
    let lastAnchor = null;
    history.entries.slice().reverse().forEach((entry) => {
      const anchor = entry.human_anchor?.trim();
      if (!anchor || anchor === lastAnchor) return;
      meaningful.push(entry);
      lastAnchor = anchor;
    });
    if (meaningful.length < 2) {
      $("#history-list").innerHTML = "<p>No earlier direction change has been recorded yet.</p>";
      return;
    }
    $("#history-list").innerHTML = meaningful.slice(0, 4).map((entry) => `
      <button class="history-version" data-version="${entry.version}" type="button">
        <strong>${entry.current ? "Current plan" : "Earlier plan"}</strong>
        <span>${escapeHtml(humanCopy(entry.human_anchor))}</span>
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
  result.hidden = false;
  if (proposal.status === "clarification_needed") {
    result.innerHTML = `
      <div class="attention-note">
        <h3>One more detail</h3>
        <p>${escapeHtml(proposal.clarification_question)}</p>
        <p class="trust-note">Your current plan has not changed.</p>
      </div>
    `;
    $("#fog-bank-text").focus();
    return;
  }
  $("#fog-bank-form").hidden = true;
  result.innerHTML = `
    <div class="attention-note"><strong>Nothing has changed yet.</strong> ${escapeHtml(proposal.summary)}</div>
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
  reviewPanel.hidden = true;
  addPanel.hidden = false;
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
  $("#input-text").value = "";
  $("#artifact-file").value = "";
  $("#file-status").textContent = "PDF, DOCX, TXT, PNG, or JPG · 5 MB max";
  addPanel.querySelector(".inline-guidance")?.remove();
  $("#input-text").focus();
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
  await requestOrientation(text, event.submitter);
}

function isPlanChangeRequest(text) {
  const normalized = text.toLowerCase().replace(/[^a-z0-9\s]/g, " ").replace(/\s+/g, " ").trim();
  const plan = "(?:my|the)?\\s*(?:career|transition|current)?\\s*plans?";
  const directChange = new RegExp(`\\b(?:change|update|fix|redo|revise|edit)\\s+${plan}\\b`);
  const makeChange = new RegExp(`\\bmake\\s+changes?\\s+to\\s+${plan}\\b`);
  return directChange.test(normalized) || makeChange.test(normalized);
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
    if (reviewReturn === "add") $("#input-text").value = "";
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
    restoreWorkspace($("#input-text"));
    $("#input-text").focus();
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
bindFocusCarousel();

$("#boot-shell").hidden = true;
contentGrid.hidden = false;
contentGrid.classList.add("fresh-start");
primary.setAttribute("aria-busy", "true");
renderColdFrontDoor();
loadState();
