const $ = (selector) => document.querySelector(selector);
const primary = $("#primary-content");
const addPanel = $("#add-panel");
const reviewPanel = $("#review-panel");
const statusBox = $("#status");
const contentGrid = $(".content-grid");
let envelope = null;
let pendingOrientation = null;

const labels = {
  career: "Work",
  education: "Education",
  location: "Location",
  resume: "Your story",
};

function idempotencyKey() {
  return crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`;
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    credentials: "same-origin",
    headers: options.body instanceof FormData ? {} : { "Content-Type": "application/json" },
    ...options,
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
  renderAreas(next.state.projections);
  renderPrimary(next);
  renderWhy(next.active_gate);
  renderChanged(next.what_changed);
  renderHistory(next.state);
}

function renderTimeline(state) {
  const order = ["TODAY", "PREPARE", "SEPARATE", "TRANSITION", "STABILIZE"];
  const activeIndex = Math.max(0, order.indexOf(state.stage));
  document.querySelectorAll(".timeline-step").forEach((step, index) => {
    step.classList.toggle("active", index <= activeIndex);
  });
}

function renderAreas(projections) {
  $("#areas").innerHTML = projections.map((item) => `
    <div class="area" data-status="${escapeHtml(item.status)}">
      <strong>${escapeHtml(item.label)}</strong>
      <span>${escapeHtml(item.summary)}</span>
    </div>
  `).join("");
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
  if (file.size > 5 * 1024 * 1024) {
    announce("That file is larger than the 5 MB limit.", true);
    event.target.value = "";
    return;
  }
  const form = new FormData();
  form.append("file", file);
  $("#file-status").textContent = `Reading ${file.name}…`;
  try {
    const result = await api("/api/artifact", { method: "POST", body: form });
    $("#input-text").value = result.text;
    $("#file-status").textContent = `${result.filename} · ready to review`;
    $("#input-text").focus();
    announce("The file was converted to editable text. Review it before continuing.");
  } catch (error) {
    $("#file-status").textContent = "PDF, DOCX, TXT, PNG, or JPG · 5 MB max";
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

loadState();
