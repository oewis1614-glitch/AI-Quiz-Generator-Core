"""
cleaner.py
----------
Post-processing utilities for Mistral model output.

Two main functions:
  - clean_question_output()   : strips artifacts from generated questions
  - validate_question()       : checks structural correctness per type
  - validate_difficulty_match(): checks question length vs difficulty
"""

import re


# ── Question cleaner ──────────────────────────────────────────────────────────

def clean_question_output(text: str, q_type: str) -> str:
    """
    Strips prompt leftovers, LaTeX, base64 images, leaked answers,
    and extra commentary from raw model output.

    Stops at the first complete question (D option) to prevent
    double-question output.
    """
    # Remove prompt artifact
    if "[/INST]" in text:
        text = text.split("[/INST]")[-1].strip()

    # Remove LaTeX math
    text = re.sub(r"\\\[.*?\\\]", "", text, flags=re.DOTALL)
    text = re.sub(r"\$\$.*?\$\$", "", text, flags=re.DOTALL)
    text = re.sub(r"\$.*?\$", "", text)
    text = re.sub(r"\\begin\{.*?\}.*?\\end\{.*?\}", "", text, flags=re.DOTALL)
    text = re.sub(r"\\[a-zA-Z]+\{[^}]*\}", "", text)
    text = re.sub(r"\\[a-zA-Z]+", "", text)
    text = re.sub(r"\[\\.*?\]", "", text)

    # Remove base64 / markdown image blobs
    text = re.sub(r"!\[.*?\]\(data:image/[^)]+\)", "", text)
    text = re.sub(r"data:image/[a-zA-Z]+;base64,[A-Za-z0-9+/=\s]+", "", text)
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)

    FORBIDDEN_STARTS = [
        "correct answer", "answer:", "explanation", "commentary",
        "model answer", "key point", "example question", "note:",
        "reference", "please ", "choose ", "select ",
        "[answer", "[blank", "you stop", "stop here",
        "---", "===", "***",
        "based on the given", "based on the provided",
        "create an", "generate a", "write a",
        "you are", "as an", "i will",
    ]

    QUESTION_LABELS = {
        "multiple-choice": ["question:"],
        "true-false":      ["statement:"],
        "short-answer":    ["question:", "q:"],
        "case-study":      ["case:", "question:"],
        "image-based":     ["figure reference:", "question:"],
    }
    q_labels = QUESTION_LABELS.get(q_type, ["question:"])

    result = []
    found_label = False
    found_d = False

    for line in text.splitlines():
        stripped = line.strip()
        if found_d:
            break
        if not stripped:
            if result and result[-1] != "":
                result.append("")
            continue

        lower = stripped.lower()

        if any(lower.startswith(fb) for fb in FORBIDDEN_STARTS):
            continue
        if re.match(r"^\[.*\]$", stripped):
            continue
        if "base64" in lower or "data:image" in lower:
            continue
        if q_type == "true-false" and re.match(r"^[AB][.)]\s*(true|false)", lower):
            continue

        is_option_line = bool(re.match(r"^[A-D][).]\s", stripped))
        if is_option_line:
            if q_type in ("multiple-choice", "case-study", "image-based"):
                result.append(stripped)
                if re.match(r"^D[).]\s", stripped):
                    found_d = True
            continue

        is_label = q_labels and any(lower.startswith(lbl) for lbl in q_labels)

        if not found_label and q_type == "short-answer" and len(stripped.split()) >= 4:
            if not is_option_line:
                found_label = True
                result.append("Question: " + stripped)
                continue

        if is_label:
            found_label = True
            result.append(stripped)
            continue

        if found_label or q_type == "image-based":
            result.append(stripped)

    while result and result[0] == "":
        result.pop(0)
    while result and result[-1] == "":
        result.pop()

    return "\n".join(result).strip()


def clean_content_for_correction(content: str) -> str:
    """Minimal cleaning for question content sent to the corrector."""
    if "[/INST]" in content:
        content = content.split("[/INST]")[-1].strip()
    if "[INST]" in content:
        content = content.split("[INST]")[0].strip()
    content = re.sub(r"!\[.*?\]\(data:image/[^)]+\)", "", content)
    content = re.sub(r"data:image/[a-zA-Z]+;base64,[A-Za-z0-9+/=\s]+", "", content)
    content = re.sub(r"!\[.*?\]\(.*?\)", "", content)
    content = re.sub(r"\\\[.*?\\\]", "", content, flags=re.DOTALL)
    content = re.sub(r"\\begin\{.*?\}.*?\\end\{.*?\}", "", content, flags=re.DOTALL)
    lines = [l for l in content.splitlines()
             if not l.strip().lower().startswith("figure reference")]
    return "\n".join(lines).strip()


# ── Validators ────────────────────────────────────────────────────────────────

def validate_question(text: str, q_type: str) -> tuple[bool, str]:
    """Returns (is_valid, reason)."""
    if len(text.split()) < 8:
        return False, "output too short"

    if q_type == "image-based":
        if not re.search(r"(?i)question\s*:", text):
            return False, "missing Question label"
        if not (re.search(r"(?m)^A[).]\s", text) and re.search(r"(?m)^B[).]\s", text)):
            return False, "missing A/B options"
        return True, "ok"

    if not re.search(r"(?i)(question|case|statement|image description)\s*:", text):
        return False, "missing question/statement label"

    if q_type in ("multiple-choice", "case-study"):
        if not (re.search(r"(?m)^A[).]\s", text) and re.search(r"(?m)^B[).]\s", text)):
            return False, "missing A/B options"

    if q_type == "true-false":
        if not re.search(r"(?i)statement\s*:", text):
            return False, "missing Statement label"
        if re.search(r"(?m)^[A-D][).]\s", text):
            return False, "true-false has MCQ options"

    return True, "ok"


def validate_difficulty_match(text: str, difficulty: str) -> tuple[bool, str]:
    """Returns (is_valid, reason)."""
    word_count = len(text.split())
    if difficulty == "advanced" and word_count < 30:
        return False, f"Advanced question too short ({word_count} words)"
    if difficulty == "beginner" and word_count > 200:
        return False, f"Beginner question suspiciously long ({word_count} words)"
    return True, "ok"
