from __future__ import annotations

import ast
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VISIBLE_KEYWORDS = {
    "clarification_question",
    "headline",
    "purpose",
    "question",
    "summary",
    "title",
    "why",
}
FORBIDDEN_VETERAN_COPY = {
    "active gate",
    "bounded",
    "canonical",
    "decision surface",
    "governed",
    "hypothetical",
    "latent",
    "materially",
    "path-relevant",
    "persistent helm input",
    "re-orientation",
    "resolver",
}


class _VisibleHtml(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.hidden_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self.hidden_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"}:
            self.hidden_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self.hidden_depth and data.strip():
            self.parts.append(data.strip())


def _syllables(word: str) -> int:
    cleaned = re.sub(r"[^a-z]", "", word.casefold())
    if not cleaned:
        return 0
    groups = len(re.findall(r"[aeiouy]+", cleaned))
    if cleaned.endswith("e") and not cleaned.endswith(("le", "ye")) and groups > 1:
        groups -= 1
    return max(groups, 1)


def _grade(text: str) -> float:
    words = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", text)
    sentences = re.findall(r"[.!?]+", text)
    syllables = sum(_syllables(word) for word in words)
    return 0.39 * (len(words) / max(len(sentences), 1)) + 11.8 * (syllables / max(len(words), 1)) - 15.59


def _keyword_literals(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    values: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.keyword) or node.arg not in VISIBLE_KEYWORDS:
            continue
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            values.append(node.value.value)
        elif isinstance(node.value, ast.JoinedStr):
            values.extend(
                item.value
                for item in node.value.values
                if isinstance(item, ast.Constant) and isinstance(item.value, str)
            )
    return values


def test_static_veteran_copy_uses_plain_language() -> None:
    parser = _VisibleHtml()
    parser.feed((ROOT / "static" / "index.html").read_text(encoding="utf-8"))
    visible = " ".join(parser.parts)
    lowered = visible.casefold()

    assert not sorted(term for term in FORBIDDEN_VETERAN_COPY if term in lowered)
    assert _grade(visible) <= 10.0


def test_generated_questions_and_explanations_use_plain_language() -> None:
    copy = []
    for relative in (
        "military_slices/acquisition.py",
        "military_slices/engine.py",
        "military_slices/temporal.py",
    ):
        copy.extend(_keyword_literals(ROOT / relative))

    combined = " ".join(copy)
    lowered = combined.casefold()
    assert not sorted(term for term in FORBIDDEN_VETERAN_COPY if term in lowered)
    assert _grade(combined) <= 10.0


def test_dynamic_interface_copy_does_not_expose_architecture_language() -> None:
    source = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
    visible_templates = source[source.index("function renderStartingVector") :]

    for phrase in (
        "active gate",
        "decision surface",
        "determine eligibility",
        "governed target",
        "path milestone",
        "persistent helm input",
        "proposed re-orientation",
        "use this re-orientation",
    ):
        assert phrase not in visible_templates.casefold()
    assert "They do not decide what you qualify for or take action for you" in source


def test_model_written_veteran_copy_has_the_same_reading_ceiling() -> None:
    prompt_source = (ROOT / "military_slices" / "agent_runtime.py").read_text(encoding="utf-8")
    assert prompt_source.count("tenth-grade reading level") >= 3
    assert "Use short sentences and common words" in prompt_source
