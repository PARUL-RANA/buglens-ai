"""
model/complexity.py — Code complexity and quality analysis for BugLens AI.

compute_complexity(code) returns a structured dict used by the /analyze route.
"""

import re


# Control-flow keywords counted across all languages
_CONTROL_FLOW_PATTERN: re.Pattern[str] = re.compile(
    r"\b(if|else|elif|for|while|switch|try|catch|except|case)\b"
)

# Nesting chars / keywords that increase depth
_OPEN_BRACE: re.Pattern[str] = re.compile(r"\{")
_PYTHON_BLOCK: re.Pattern[str] = re.compile(
    r"^\s*(def |class |if |elif |else:|for |while |try:|except|with )",
    re.MULTILINE,
)


def _count_max_nesting(code: str) -> int:
    """Return the maximum brace-nesting depth seen in *code*.

    For Python (no braces) falls back to counting leading-indent levels.
    """
    # Brace-based languages
    if "{" in code:
        depth = 0
        max_depth = 0
        for ch in code:
            if ch == "{":
                depth += 1
                max_depth = max(max_depth, depth)
            elif ch == "}":
                depth = max(0, depth - 1)
        return max_depth

    # Python / indent-based: approximate via indentation levels
    max_indent = 0
    for line in code.splitlines():
        stripped = line.lstrip()
        if not stripped:
            continue
        indent = len(line) - len(stripped)
        level = indent // 4  # assume 4-space indentation
        max_indent = max(max_indent, level)
    return max_indent


def _to_score(raw: int) -> int:
    """Clamp a raw complexity integer to the 1-10 range."""
    return max(1, min(10, raw))


def compute_complexity(code: str) -> dict[str, object]:
    """Analyse *code* and return a complexity breakdown dict.

    Returns
    -------
    dict with keys:
        complexity_score  : int  1-10
        quality_grade     : str  A/B/C/D/F
        line_count        : int
        max_nesting       : int
        control_flow_count: int
    """
    lines = code.splitlines()
    line_count: int = len(lines)

    control_flow_count: int = len(_CONTROL_FLOW_PATTERN.findall(code))
    max_nesting: int = _count_max_nesting(code)

    # Raw score: weight nesting more heavily than keyword count
    raw_score: int = 1 + max_nesting + (control_flow_count // 3)
    complexity_score: int = _to_score(raw_score)

    grade_map: list[tuple[int, str]] = [
        (3, "A"),
        (5, "B"),
        (7, "C"),
        (9, "D"),
    ]
    quality_grade: str = "F"
    for threshold, letter in grade_map:
        if complexity_score <= threshold:
            quality_grade = letter
            break

    return {
        "complexity_score": complexity_score,
        "quality_grade": quality_grade,
        "line_count": line_count,
        "max_nesting": max_nesting,
        "control_flow_count": control_flow_count,
    }
