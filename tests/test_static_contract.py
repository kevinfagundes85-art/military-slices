from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_cold_path_avoids_architecture_language() -> None:
    html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    visible = html.casefold()
    forbidden = (
        "human decision",
        "candidate resolution",
        "context_needed",
        "profile version",
        "firestore state",
        "epistemic",
    )
    for term in forbidden:
        assert term not in visible


def test_dynamic_backend_copy_is_projected_into_human_language() -> None:
    script = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    assert "function humanCopy" in script
    for replacement in (
        '.replace(/\\blatent\\b/gi, "in the background")',
        '.replace(/\\bcanonical\\b/gi, "current")',
        '.replace(/\\bgoverned\\b/gi, "saved")',
        '.replace(/\\bstale\\b/gi, "ready for another look")',
        '.replace(/\\bdependencies?\\b/gi, "related choices")',
        '.replace(/\\bexecution state\\b/gi, "plan status")',
        '.replace(/\\bresolver\\b/gi, "system")',
    ):
        assert replacement in script
    assert "humanCopy(gate.question)" in script
    assert "humanCopy(gate.why)" in script
    assert "humanCopy(lens.summary)" in script
    assert "humanCopy(feedback.headline)" in script


def test_rich_artifact_contract_cannot_regress_to_text_only() -> None:
    html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    assert ".pdf" in html
    assert ".docx" in html
    assert ".png" in html
    assert ".jpg" in html
    assert "5 MB max" in html
    assert "plain-text résumé" not in html
    assert ".md" not in html
    assert "100 KB" not in html


def test_file_selection_is_the_artifact_authorization_boundary() -> None:
    script = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    assert 'form.append("expected_version"' in script
    assert 'form.append("idempotency_key"' in script
    artifact_flow = script[script.index("async function uploadArtifact") :]
    assert 'api("/api/artifact"' in artifact_flow
    assert "showReview" not in artifact_flow
    assert "ready to review" not in artifact_flow
    assert "render(next, { showFeedback: true })" in artifact_flow
    assert 'announce("Saved.")' in artifact_flow


def test_mobile_targets_and_overflow_guards_exist() -> None:
    css = (ROOT / "static" / "styles.css").read_text(encoding="utf-8")
    assert "min-height: 46px" in css
    assert "min-width: 300px" in css
    assert "overflow-wrap: anywhere" in css
    assert "@media (max-width: 480px)" in css


def test_transition_path_is_bounded_instead_of_rendered_as_a_dashboard() -> None:
    html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    script = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    assert "Parts of your transition" not in html
    assert 'id="areas"' not in html
    assert 'id="current-target"' in html
    assert 'id="path-position"' in html
    assert "taskHorizon(state.active_tasks)" in script
    assert ".slice(0, 3)" in script


def test_firestore_dependency_pair_is_locked_to_the_hosted_known_good_versions() -> None:
    project = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert '"google-cloud-firestore==2.28.1"' in project
    assert '"google-api-core==2.34.0"' in project


def test_human_control_layer_stays_bounded_and_explicit() -> None:
    html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    script = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    css = (ROOT / "static" / "styles.css").read_text(encoding="utf-8")
    assert 'id="lens-nav"' in html
    assert 'id="open-history"' in html
    assert 'id="open-what-if"' in html
    assert "Looking without changing" in html
    assert "Hypothetical — nothing changes yet" in html
    assert "Test one possible move against what matters now" in html
    assert "home lab" in html
    assert 'api("/api/what-if"' in script
    assert 'api("/api/what-if/promote"' in script
    assert "Use this plan" in script
    assert "Keep my current plan" in script
    assert "Add this to my plan" in script
    assert ".lens-cloud { display: flex; flex-wrap: wrap" in css
    assert "Look at this another way" in html
    assert "Choose a relevant part of your plan" in html
    assert "/static/app.js?v=9" in html
    assert "/static/styles.css?v=7" in html


def test_temporal_impact_surface_is_natural_bounded_and_deterministic() -> None:
    html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    script = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    assert 'id="impact-panel"' in html
    assert "Because of your last decision" in html
    assert 'api("/api/revalidate"' in script
    assert "Worth checking" in script
    assert "Still planning to stay local?" not in html
    for forbidden in ("dependency invalidated", "TTL", "receipt refresh", "freshness class"):
        assert forbidden not in html


def test_cold_start_renders_intake_without_plan_machinery() -> None:
    html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    script = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    assert 'id="orientation-shell"' in html and 'aria-labelledby="transition-title" hidden' in html
    assert '<div class="content-grid" hidden>' in html
    assert 'id="add-context-top"' in html and 'type="button" hidden' in html
    assert "if (!state.starting_vector_complete && state.version === 0)" in script
    starting = script[script.index("function renderStartingVector") : script.index("function submitStartingVector")]
    assert "Who are you planning for?" in starting
    assert "Where is the service member in their timeline?" in starting
    assert "Military branch" in starting
    assert "Service category" in starting
    fresh = script[script.index("function renderColdFrontDoor") : script.index("function renderPrimary")]
    assert "You do not need to have your transition figured out." in fresh
    assert "Start with a document" in fresh
    assert "Start with an image" in fresh
    assert "Tell me what’s going on" in fresh
    assert "start-document.webp" in fresh
    assert "start-image.webp" in fresh
    assert "start-thought.webp" in fresh
    assert 'id="cold-input-form"' not in fresh
    assert "api(" not in fresh
    for premature in ("Path readiness", "decisions settled", "Loading your next step", "Because of your last decision"):
        assert premature not in fresh


def test_static_front_door_choices_are_local_and_accept_normal_artifacts() -> None:
    script = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    choice = script[script.index("function chooseColdEntry") : script.index("function renderColdFrontDoor")]
    front_door = script[script.index("function renderColdFrontDoor") : script.index("function renderPrimary")]
    text_entry = script[script.index("function renderColdTextEntry") : script.index("function chooseColdEntry")]
    assert "api(" not in choice
    assert "api(" not in front_door
    assert "api(" not in text_entry
    assert '".png,.jpg,.jpeg,image/png,image/jpeg"' in choice
    document_accept = (
        '".txt,.pdf,.docx,text/plain,application/pdf,'
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document"'
    )
    assert document_accept in choice
    assert "input.click()" in choice
    assert 'type="file" hidden aria-hidden="true" tabindex="-1"' in front_door
    bootstrap = script[script.rindex('$("#boot-shell").hidden = true;') :]
    assert bootstrap.index("renderColdFrontDoor();") < bootstrap.index("loadState();")


def test_front_door_photos_are_bounded_optimized_assets() -> None:
    css = (ROOT / "static" / "styles.css").read_text(encoding="utf-8")
    assert ".entry-card img { display: block; width: 100%; height: auto; aspect-ratio: 3 / 2" in css
    assets = ROOT / "static" / "images"
    for name in ("start-document.webp", "start-image.webp", "start-thought.webp"):
        path = assets / name
        assert path.exists()
        assert path.stat().st_size < 50_000


def test_pre_anchor_state_renders_the_backend_question_without_plan_scaffolding() -> None:
    script = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    assert "return state.version > 0 && Boolean(state.human_anchor)" in script
    assert "if (!state.starting_vector_complete && state.version === 0)" in script
    assert "if (!state.human_anchor && !state.original_intents.length)" in script
    assert '$("#orientation-shell").hidden = !started' in script
    assert '<h2 id="primary-title">${escapeHtml(humanCopy(gate.question))}</h2>' in script


def test_progressive_disclosure_and_feedback_are_state_earned() -> None:
    script = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    assert "function applyProgressiveDisclosure" in script
    assert '$("#orientation-shell").hidden = !started' in script
    assert '$(".control-nav").hidden = !started' in script
    assert '$(".context-column").hidden = !contextVisible' in script
    assert "hasRendered && next.state.version !== previousVersion" in script
    assert "renderChanged(visibleFeedback)" in script
    assert 'render(await api("/api/state"), { showFeedback: false })' in script


def test_fog_bank_is_persistent_human_control_not_an_automatic_mutation() -> None:
    html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    script = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    assert 'id="open-fog-bank"' in html
    assert "Something doesn’t fit" in html
    assert 'id="fog-bank-panel"' in html
    assert "Nothing changes unless you review and accept" in html
    assert 'api("/api/fog-bank"' in script
    assert 'api("/api/fog-bank/accept"' in script
    assert "Keep my current plan" in script
    assert "Use this re-orientation" in script
    assert "none gains authority merely because it may matter" in script


def test_execution_state_projection_is_human_facing() -> None:
    script = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    assert 'if (mode === "COMPLETE")' in script
    assert "You’ve completed this goal." in script
    assert 'mode === "PARALYZED"' in script
    assert "These choices cannot both guide the next step" in script
    for forbidden_copy in (">PARALYZED<", ">ACTIVE<", ">COMPLETE<"):
        assert forbidden_copy not in script


def test_trust_boundary_copy_distinguishes_text_and_artifact_authority() -> None:
    html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    script = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    combined = html + script
    assert "Nothing is saved until you confirm" not in combined
    assert "Reviewing this does not change your plan" in html
    assert "Choosing a file lets Military SLICES use relevant details" in combined
    assert 'api("/api/artifact"' in script


def test_insufficient_orientation_requires_clarification_before_any_write() -> None:
    script = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    assert "const needsClarification = !result.sufficient" in script
    assert "One question before this can shape your plan." in script
    assert "Check this clarification" in script
    assert "!pendingOrientation.sufficient" in script
    assert 'id="review-text-label"' in html
    assert 'id="review-trust"' in html


def test_lens_preview_and_what_if_keep_observe_separate_from_commit() -> None:
    script = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    preview = script[script.index("function showLensPreview") : script.index("function renderLenses")]
    assert "Another way to look at the current choice" in preview
    assert "api(" not in preview
    assert "No changes have been made." in preview
    assert "openTopicUpdate(topic)" in preview
    assert 'mode === "ACTIVE"' in preview
    assert "This remains hypothetical until you choose" in script
    assert "Keep my current plan" in script
    assert "Use this plan" in script


def test_lens_cloud_is_deterministic_bounded_and_non_mutating_until_explicit_action() -> None:
    script = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    build = script[script.index("function buildLensTopics") : script.index("function openTopicUpdate")]
    preview = script[script.index("function showLensPreview") : script.index("function renderLenses")]
    render = script[script.index("function renderLenses") : script.index("function renderTimeline")]
    assert "const starterLensTopics" not in script
    assert "if (state.version === 0)" in build
    assert "return [];" in build
    assert "const meaningful = Boolean(" in build
    assert ".slice(0, 6)" in build
    assert 'lens.name === "location"' in build
    assert "Math.random" not in build
    assert 'rule.label === "PCS and moving"' in build
    assert "touches pcs and moving" not in script
    assert "api(" not in build
    assert "api(" not in preview
    assert "api(" not in render
    assert 'role="listitem"' not in render
    assert "const factMarkup = topic.facts?.length" in preview
    assert '$("#lens-cloud-shell").hidden = true' in render
    assert '$("#open-lenses").hidden = !topics.length' in render
    assert 'id="open-lenses"' in html
    assert "Look at this another way" in html


def test_lens_cloud_is_secondary_and_empty_domain_surfaces_are_not_padded() -> None:
    html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    script = (ROOT / "static" / "app.js").read_text(encoding="utf-8")

    assert 'id="lens-cloud-shell"' in html and "hidden" in html
    assert "openLensCloud" in script
    assert "closeLensCloud" in script
    assert "Back to what matters now" in html
    assert "Nothing here currently blocks the active path" not in script
    assert "Look without changing" not in script


def test_loading_preserves_stable_content_and_never_exposes_processing_steps() -> None:
    html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    script = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    assert 'id="processing-status"' in html
    assert "Working through this…" in script
    assert "setProcessing" in script
    for forbidden in ("calling model", "running resolver", "writing firestore", "recomputing gates"):
        assert forbidden not in (html + script).casefold()


def test_success_updates_are_announced_without_a_competing_visual_toast() -> None:
    html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    styles = (ROOT / "static" / "styles.css").read_text(encoding="utf-8")
    assert 'id="status" class="status" role="status" aria-live="polite"' in html
    assert ".status.visible { opacity: 1" not in styles
    assert ".status.visible.error { opacity: 1" in styles


def test_governed_changes_and_required_actions_never_depend_on_toasts() -> None:
    script = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    assert "function transitionAnnouncement" not in script
    assert 'announce("Saved.")' in script
    assert 'announce("No changes saved.")' in script
    assert 'showInlineGuidance(primary, "Add your decision first.")' in script
    assert 'showInlineGuidance(reviewPanel, "Checking your correction' in script
    for forbidden_toast in (
        "Your plan updated and the next decision is ready.",
        "Decision saved. Your next step changed.",
        "Your document updated the plan and changed what comes next.",
        "Goal complete. No new task was created.",
    ):
        assert forbidden_toast not in script
