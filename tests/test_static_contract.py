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
    assert "Your document updated the plan" in artifact_flow


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
