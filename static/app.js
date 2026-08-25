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

const labels = {
  career: "Work",
  education: "Education",
  location: "Location",
  resume: "Your story",
};

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
      const error = new Error(detail);
      error.status = response.status;
      throw error;
    }
    return response.json();
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error("This took too long. Your plan was not left spinning; reload to check the current state.");
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

function escapeHtml(value) {
  const element = document.createElement("div");
  element.textContent = value ?? "";
  return element.innerHTML;
}

function render(next) {
  envelope = next;
  primary.setAttribute("aria-busy", "false");
  renderTimeline(next.state);
  renderPath(next.state);
  renderProgress(next.progress);
  renderLenses(next.lenses);
  renderPrimary(next);
  renderWhy(next.active_gate);
  renderChanged(next.what_changed);
  renderHistory(next.state);
}

function renderProgress(progress) {
  $("#readiness-count").textContent = `${progress.closed} / ${progress.total} decisions settled`;
  $("#readiness-marks").innerHTML = progress.items.map((item) => (
    `<span class="readiness-mark" data-state="${escapeHtml(item.state)}" title="${escapeHtml(item.label)}"></span>`
  )).join("");
}

function showLensPreview(lens, trigger) {
  const preview = $("#lens-preview");
  document.querySelectorAll(".lens-button").forEach((button) => {
    button.setAttribute("aria-expanded", String(button === trigger));
  });
  preview.innerHTML = `
    <button id="dismiss-lens-preview" class="preview-close" type="button" aria-label="Dismiss preview">×</button>
    <strong>${escapeHtml(lens.label)}</strong>
    <div class="lens-counts">${lens.fact_count} relevant facts · ${lens.closed_gates} settled · ${lens.open_gates} open</div>
    <p>${escapeHtml(lens.summary)}</p>
    ${lens.latent_dependencies ? `<p class="latent-note">${lens.latent_dependencies} known details remain in the background.</p>` : ""}
    <button id="open-lens-detail" class="button button-secondary" type="button">Open ${escapeHtml(lens.label)}</button>
  `;
  preview.hidden = false;
  $("#dismiss-lens-preview").addEventListener("click", () => {
    preview.hidden = true;
    trigger.setAttribute("aria-expanded", "false");
    trigger.focus();
  });
  $("#open-lens-detail").addEventListener("click", () => openLensDetail(lens));
}

function renderLenses(lenses) {
  const nav = $("#lens-nav");
  nav.innerHTML = lenses.map((lens) => `
    <button class="lens-button" data-lens="${escapeHtml(lens.name)}" type="button" aria-expanded="false">
      <span>${escapeHtml(lens.label)}</span>
      <small>${lens.path_relevant ? "Supports now" : "Look only"}</small>
    </button>
  `).join("");
  nav.querySelectorAll(".lens-button").forEach((button) => {
    const lens = lenses.find((item) => item.name === button.dataset.lens);
    button.addEventListener("mouseenter", () => showLensPreview(lens, button));
    button.addEventListener("focus", () => showLensPreview(lens, button));
    button.addEventListener("click", () => showLensPreview(lens, button));
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
  const service = serviceLabels[state.service] || "Service details only when needed";
  const timing = windowLabels[state.current_timeline_window] || "Current transition window";
  $("#path-position").textContent = `${service} · ${timing}`;
}

function taskHorizon(tasks) {
  if (!tasks?.length) return "";
  return `
    <div class="task-horizon" aria-label="Current tasks">
      <span>Working toward</span>
      <ol>${tasks.slice(0, 3).map((task) => `<li>${escapeHtml(task.title)}</li>`).join("")}</ol>
    </div>
  `;
}

function renderPrimary(next) {
  const state = next.state;
  const gate = next.active_gate;
  if (state.version === 0) {
    primary.innerHTML = `
      <h2 id="primary-title">Start with what you have.</h2>
      <p class="gate-copy">Tell us what is changing, what you know, or what you are unsure about. You do not need to understand the system or complete an intake form first.</p>
      <div class="button-row align-start">
        <button id="start-text" class="button button-primary" type="button">Tell me something</button>
        <button id="start-file" class="button button-secondary" type="button">Add a résumé or screenshot</button>
      </div>
    `;
    $("#start-text").addEventListener("click", () => openAdd(false));
    $("#start-file").addEventListener("click", () => openAdd(true));
    return;
  }
  if (!gate) {
    const accepted = state.career_hypotheses.find((item) => item.status === "accepted");
    primary.innerHTML = `
      ${taskHorizon(state.active_tasks)}
      <h2 id="primary-title">${accepted ? `Keep testing ${escapeHtml(accepted.title)}.` : "Your plan is caught up for now."}</h2>
      <p class="gate-copy">${accepted ? `Your experience suggests a credible direction. The remaining gaps are hypotheses until you compare them with a real job description.` : "Add something whenever your timing, priorities, work preferences, education, or location changes."}</p>
      <button id="add-more" class="button button-primary" type="button">${accepted ? "Add a job description or update" : "Add something"}</button>
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
      <label class="choice-option"><input type="radio" name="gate-choice" value="${escapeHtml(option)}" ${index === 0 ? "checked" : ""}><span>${escapeHtml(option)}</span></label>
    `).join("")}</div>`;
  } else if (gate.surface === "compare" && hypotheses.length) {
    control = `<div class="hypothesis-grid">${hypotheses.map((item) => `
      <article class="hypothesis">
        <h3>${escapeHtml(item.title)}</h3>
        <p>${escapeHtml(item.rationale)}</p>
        <p><strong>What may already fit</strong><br>${escapeHtml(item.capability_matches.join(" · "))}</p>
        <p><strong>What to verify</strong><br>${escapeHtml(item.possible_gaps.join(" · "))}</p>
        <div class="evidence-note">Explore with ${escapeHtml(item.evidence.join(" · "))}</div>
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
    ${taskHorizon(state.active_tasks)}
    <h2 id="primary-title">${escapeHtml(gate.question)}</h2>
    <p class="gate-copy">${escapeHtml(gate.why)}</p>
    <form id="gate-form" class="gate-form">
      ${control}
      ${gate.surface === "compare" && hypotheses.length ? "" : '<button class="button button-primary" type="submit">Use this decision</button>'}
    </form>
  `;
  const form = $("#gate-form");
  form.addEventListener("submit", submitDecision);
  document.querySelectorAll(".hypothesis-choice").forEach((button) => {
    button.addEventListener("click", () => submitDecision({ preventDefault() {}, currentTarget: button }));
  });
}

function renderWhy(gate) {
  const panel = $("#why-panel");
  if (!gate) {
    panel.hidden = true;
    return;
  }
  panel.hidden = false;
  $("#why-copy").textContent = gate.why;
  $("#affected-areas").innerHTML = gate.affected_slices.map((name) => `<span class="affected-area">${escapeHtml(labels[name])}</span>`).join("");
}

function renderChanged(feedback) {
  const panel = $("#changed-panel");
  if (!feedback) {
    panel.hidden = true;
    return;
  }
  panel.hidden = false;
  $("#changed-title").textContent = feedback.headline;
  $("#changed-list").innerHTML = feedback.consequences.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
}

function renderHistory(state) {
  const intents = state.original_intents.slice(-5).reverse();
  const decisions = state.decisions.slice(-5).reverse();
  if (!intents.length && !decisions.length) {
    $("#history-content").textContent = "Nothing has been saved yet.";
    return;
  }
  $("#history-content").innerHTML = `
    ${intents.map((item) => `<div class="history-item">${escapeHtml(item)}</div>`).join("")}
    ${decisions.map((item) => `<div class="history-item"><strong>Decision:</strong> ${escapeHtml(item.value)}</div>`).join("")}
  `;
}

function showInspection(panel) {
  [addPanel, reviewPanel, $("#lens-panel"), $("#history-panel"), $("#what-if-panel")].forEach((item) => {
    item.hidden = item !== panel;
  });
  contentGrid.hidden = true;
  panel.hidden = false;
  panel.scrollIntoView({ behavior: "smooth", block: "start" });
  panel.querySelector("h2")?.focus?.();
}

function closeInspection(panel, returnTo) {
  panel.hidden = true;
  contentGrid.hidden = false;
  returnTo?.focus();
}

function openLensDetail(lens) {
  const panel = $("#lens-panel");
  $("#lens-title").textContent = lens.label;
  $("#lens-detail").innerHTML = `
    <p>${escapeHtml(lens.summary)}</p>
    <dl class="lens-metrics">
      <div><dt>Relevant facts</dt><dd>${lens.fact_count}</dd></div>
      <div><dt>Settled decisions</dt><dd>${lens.closed_gates}</dd></div>
      <div><dt>Open here</dt><dd>${lens.open_gates}</dd></div>
    </dl>
    ${lens.facts.length ? `<h3>Known</h3><ul>${lens.facts.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>` : "<p>No governed facts are needed here yet.</p>"}
    ${lens.decisions.length ? `<h3>Prior decisions</h3><ul>${lens.decisions.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>` : ""}
    ${lens.latent_dependencies ? `<h3>In the background</h3><p>${lens.latent_dependencies} known details remain latent because they do not advance the current target.</p>` : ""}
    <p class="trust-note">Looking here did not change your target, gates, tasks, or plan version.</p>
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
        <strong>${entry.current ? "Current" : "Earlier"} · version ${entry.version}</strong>
        <span>${escapeHtml(entry.human_anchor || "No target declared")}</span>
        <small>${escapeHtml(entry.change_summary)}</small>
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
        <div class="section-kicker">Read-only version ${entry.version}</div>
        <h3>${escapeHtml(entry.human_anchor || "No target was declared")}</h3>
        <p>${entry.open_gates.length ? `Open then: ${escapeHtml(entry.open_gates.join(" · "))}` : "No open gate was recorded."}</p>
        <p>${entry.closed_decisions.length ? `Decisions then: ${escapeHtml(entry.closed_decisions.join(" · "))}` : "No decision was recorded yet."}</p>
        <p class="trust-note">Your current plan remains version ${envelope.state.version}.</p>
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
    announce("Add one change to explore.", true);
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
      <section><div class="section-kicker">Current</div><ul>${branch.current_summary.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul></section>
      <section><div class="section-kicker">Hypothetical</div><ul>${branch.hypothetical_summary.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul></section>
    </div>
    ${branch.conflicts.length ? `<div class="conflict-note"><strong>Conflict to resolve</strong><ul>${branch.conflicts.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul></div>` : ""}
    <h3>If you use this plan</h3>
    <ul>${branch.consequences.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
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
    announce("Hypothetical discarded. Your current plan did not change.");
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
    render(next);
    $("#main").focus();
    announce("You made the explored change part of your current plan.");
  } catch (error) {
    if (error.status === 409) await loadState();
    announce(error.message, true);
    button.disabled = false;
  }
}

function openAdd(fileFirst) {
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
    announce("Add a sentence or choose a file first.", true);
    $("#input-text").focus();
    return;
  }
  const submit = event.submitter;
  if (submit) submit.disabled = true;
  try {
    pendingOrientation = await api("/api/orient", { method: "POST", body: JSON.stringify({ text }) });
    showReview(pendingOrientation);
  } catch (error) {
    announce(error.message, true);
  } finally {
    if (submit) submit.disabled = false;
  }
}

function showReview(result) {
  addPanel.hidden = true;
  contentGrid.hidden = true;
  reviewPanel.hidden = false;
  $("#review-summary").textContent = result.summary;
  $("#review-statements").innerHTML = result.statements.map((item) => `<li>${escapeHtml(item.text)}</li>`).join("") || "<li>We need one clarification before this can shape your plan.</li>";
  $("#review-text").value = result.reviewed_input;
  reviewPanel.scrollIntoView({ behavior: "smooth", block: "start" });
  $("#review-title").focus?.();
}

async function confirmReview() {
  if (!pendingOrientation || !envelope) return;
  const reviewedInput = $("#review-text").value.trim();
  if (reviewedInput !== pendingOrientation.reviewed_input) {
    announce("Rechecking your correction before it shapes the plan.");
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
    pendingOrientation = null;
    render(next);
    $("#primary").scrollIntoView({ behavior: "smooth", block: "start" });
    $("#main").focus();
    announce(next.agent_run?.fallback ? "Your plan updated. Live research was unavailable, so the safe fallback kept you moving." : "Your plan updated and the next decision is ready.");
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
    announce("Add your decision first.", true);
    return;
  }
  const buttons = document.querySelectorAll("#gate-form button");
  buttons.forEach((button) => { button.disabled = true; });
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
    render(next);
    $("#main").focus();
    announce("Decision saved. Your next step changed.");
  } catch (error) {
    if (error.status === 409) await loadState();
    announce(error.message, true);
  } finally {
    buttons.forEach((button) => { button.disabled = false; });
  }
}

async function uploadArtifact(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  if (!envelope) {
    announce("Your plan is still loading. Try the file again in a moment.", true);
    event.target.value = "";
    return;
  }
  if (file.size > 5 * 1024 * 1024) {
    announce("That file is larger than the 5 MB limit.", true);
    event.target.value = "";
    return;
  }
  const form = new FormData();
  form.append("file", file);
  form.append("expected_version", String(envelope.state.version));
  form.append("idempotency_key", idempotencyKey());
  $("#file-status").textContent = `Using ${file.name} to update your plan…`;
  try {
    const next = await api("/api/artifact", { method: "POST", body: form });
    addPanel.hidden = true;
    contentGrid.hidden = false;
    render(next);
    $("#primary").scrollIntoView({ behavior: "smooth", block: "start" });
    $("#main").focus();
    announce(next.agent_run?.fallback ? "Your document updated the plan using the safe fallback." : "Your document updated the plan and changed what comes next.");
  } catch (error) {
    $("#file-status").textContent = "PDF, DOCX, TXT, PNG, or JPG · 5 MB max";
    if (error.status === 409) await loadState();
    announce(error.message, true);
  } finally {
    event.target.value = "";
  }
}

async function loadState() {
  try {
    render(await api("/api/state"));
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
  addPanel.hidden = false;
  $("#input-text").focus();
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

loadState();
