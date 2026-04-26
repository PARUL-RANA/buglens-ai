"""
app.py — BugLens AI Flask REST API.

API CONTRACT (from .cursorrules):
    POST /analyze  { code, language } -> full analysis response
    GET  /health   -> { status, models_loaded, sample_counts }
    GET  /languages -> { languages }
    POST /feedback  { code, language, was_correct } -> 200 OK
"""

import ast
import logging
import os
import re
import time
from typing import Any, Optional

import joblib
import numpy as np
from flask import Flask, g, jsonify, request, send_from_directory
from flask_cors import CORS
from sklearn.metrics.pairwise import cosine_similarity

from model.complexity import compute_complexity

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = Flask(__name__, static_folder="static")

# ── CORS — restrict /analyze to localhost only ──────────────────────────────
CORS(app, resources={r"/analyze": {"origins": [
    "http://localhost:5000",
    "http://127.0.0.1:5000",
]}})

LANGUAGES: list[str] = ["java", "c", "cpp", "python"]
MAX_CODE_LEN: int = 10_000

# ── Confidence threshold — uncertain zone ────────────────────────────────────
CLEAN_CONFIDENCE_THRESHOLD: float = 0.65

# Pattern-based precheck matches use a high confidence to skip ML.
PATTERN_MATCH_CONFIDENCE: float = 0.95

# ---------------------------------------------------------------------------
# Request logging setup
# ---------------------------------------------------------------------------
_LOG_DIR = "logs"
os.makedirs(_LOG_DIR, exist_ok=True)

_request_logger = logging.getLogger("buglens.requests")
_request_logger.setLevel(logging.INFO)
_request_logger.propagate = False

_fh = logging.FileHandler(os.path.join(_LOG_DIR, "requests.log"), mode="a", encoding="utf-8")
_fh.setFormatter(logging.Formatter("%(message)s"))
_request_logger.addHandler(_fh)


@app.before_request
def _start_timer() -> None:
    g.start_time = time.time()


@app.after_request
def _log_analyze_request(response: Any) -> Any:
    if request.path == "/analyze" and request.method == "POST":
        elapsed_ms = round((time.time() - g.start_time) * 1000, 1)
        payload: dict[str, Any] = request.get_json(silent=True) or {}
        code: str = payload.get("code", "")
        language: str = payload.get("language", "")

        result: dict[str, Any] = {}
        try:
            result = response.get_json() or {}
        except Exception:
            pass

        _request_logger.info(
            "%s | lang=%-6s | code_len=%5d | is_bug=%-5s | confidence=%.4f | response_ms=%7.1f",
            time.strftime("%Y-%m-%dT%H:%M:%S"),
            language or "?",
            len(code),
            str(result.get("is_bug", "?")).lower(),
            result.get("confidence", 0.0),
            elapsed_ms,
        )
    return response

# ---------------------------------------------------------------------------
# Model loading at startup
# ---------------------------------------------------------------------------
models: dict[str, Any] = {}
vectorizers: dict[str, Any] = {}
sample_lookups: dict[str, Any] = {}

for _lang in LANGUAGES:
    models[_lang] = joblib.load(f"model/{_lang}_model.pkl")
    vectorizers[_lang] = joblib.load(f"model/{_lang}_vectorizer.pkl")
    sample_lookups[_lang] = joblib.load(f"model/{_lang}_samples.pkl")

print(f"[BugLens] Models loaded for: {LANGUAGES}")

# ---------------------------------------------------------------------------
# Model health check on startup
# ---------------------------------------------------------------------------
_HEALTH_SNIPPETS: dict[str, str] = {
    "java":   "public class T { public static void main(String[] a) { int x = 1; } }",
    "c":      "#include <stdio.h>\nint main() { int x = 1; return 0; }",
    "cpp":    "#include <iostream>\nint main() { int x = 1; return 0; }",
    "python": "def add(a, b):\n    return a + b\nresult = add(1, 2)",
}

for _lang, _snippet in _HEALTH_SNIPPETS.items():
    try:
        _feature = f"{_lang} {_snippet}"
        _vec = vectorizers[_lang].transform([_feature])
        _pred = models[_lang].predict(_vec)[0]
        _proba = models[_lang].predict_proba(_vec)[0]
        print(f"[BugLens] Health check [{_lang}]: pred={_pred}, conf={max(_proba):.4f} — OK")
    except Exception as _exc:
        print(f"[BugLens] WARNING: Health check [{_lang}] FAILED: {_exc}")

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def clean_response(code: str, language: str, confidence: float = 1.0) -> Any:
    """Return a JSON response indicating clean (bug-free) code."""
    complexity = compute_complexity(code)
    return jsonify({
        "is_bug": False,
        "confidence": round(confidence, 4),
        "bug_type": "clean",
        "line_number": 0,
        "description": "No bugs detected. Code looks correct.",
        "fixed_code": code,
        "complexity_score": complexity["complexity_score"],
        "quality_grade": complexity["quality_grade"],
        "language": language,
    })


def uncertain_response(code: str, language: str, confidence: float) -> Any:
    """Return a JSON response when the model is not confident enough to call a bug."""
    complexity = compute_complexity(code)
    return jsonify({
        "is_bug": False,
        "confidence": round(confidence, 4),
        "bug_type": "uncertain",
        "line_number": 0,
        "description": "The model is not confident. Code may be clean.",
        "fixed_code": code,
        "complexity_score": complexity["complexity_score"],
        "quality_grade": complexity["quality_grade"],
        "language": language,
    })


def buggy_response(
    code: str,
    language: str,
    confidence: float,
    bug_type: str,
    line_number: int,
    description: str,
    fixed_code: str,
) -> Any:
    """Return a JSON response describing a detected bug."""
    complexity = compute_complexity(code)
    return jsonify({
        "is_bug": True,
        "confidence": round(confidence, 4),
        "bug_type": bug_type,
        "line_number": line_number,
        "description": description,
        "fixed_code": fixed_code,
        "complexity_score": complexity["complexity_score"],
        "quality_grade": complexity["quality_grade"],
        "language": language,
    })


def _nearest_sample_by_bug_type(
    language: str,
    X_input: Any,
    want_bug: str,
) -> Optional[dict[str, Any]]:
    """Pick the training sample of `want_bug` most similar to the input (TF-IDF space)."""
    metadata: dict[int, dict[str, Any]] = sample_lookups[language]["metadata"]
    buggy_vectors = sample_lookups[language]["vectors"]
    meta_keys: list[int] = list(metadata.keys())
    want = want_bug.lower()
    indices: list[int] = [
        i for i, k in enumerate(meta_keys)
        if str(metadata[k].get("bug_type", "")).lower() == want
    ]
    if not indices:
        return None
    sub = buggy_vectors[indices]
    sims = cosine_similarity(X_input, sub)[0]
    best_i = int(np.argmax(sims))
    best_key = meta_keys[indices[best_i]]
    return dict(metadata[best_key])


def _pattern_bugs_precheck(
    code: str,
    language: str,
    X_input: Any,
) -> Optional[Any]:
    """
    Fast pattern rules before ML. Returns a Flask response if a rule fires, else None.
    fixed_code and metadata come from the nearest same bug_type in sample_lookups.
    """
    print(f"[PRECHECK] first 200 chars of code: {code[:200]}")
    print(f"[PRECHECK] has_new={'new ' in code}, has_delete={'delete' in code}")
    has_null: bool = bool(re.search(r"(?<![=])=\s*null", code))
    has_method: bool = any(
        x in code for x in (".length()", ".toUpperCase()", ".toString()")
    )
    has_while: bool = bool(re.search(r"while\s*\(\s*true\s*\)", code))
    has_break: bool = "break" in code
    has_strcpy: bool = "strcpy" in code
    has_new: bool = "new " in code
    code_no_comments = '\n'.join(
        line for line in code.split('\n')
        if not line.strip().startswith('//')
    )
    has_delete: bool = bool(re.search(r'\bdelete\b\s+\w', code_no_comments))

    print(
        f"[PATTERN] java null_pointer check: has_null={has_null}, has_method={has_method}"
    )
    print(
        f"[PATTERN] java infinite_loop check: has_while={has_while}, has_break={has_break}"
    )
    print(f"[PATTERN] c buffer_overflow check: has_strcpy={has_strcpy}")
    print(f"[PATTERN] cpp memory_leak check: has_new={has_new}, has_delete={has_delete}")

    has_py_bad_len_index: bool = "[len(" in code
    has_py_str_int_add: bool = bool(
        re.search(r'["\'].*?["\'\s]*\+\s*\d', code)
        or re.search(r"\d\s*\+\s*[\"']", code)
    )
    has_py_while_true: bool = bool(re.search(r"while\s+True\s*:", code))
    print(
        f"[PATTERN] python index_out_of_range check: has_bad_len_index={has_py_bad_len_index}"
    )
    print(
        f"[PATTERN] python type_error check: has_str_int_add={has_py_str_int_add}"
    )
    print(
        f"[PATTERN] python infinite_loop check: has_while_true={has_py_while_true}, "
        f"has_break={has_break}"
    )

    want_bug: Optional[str] = None

    if language == "java":
        if re.search(r"(?<![=])=\s*null", code) and any(
            x in code for x in (".length()", ".toUpperCase()", ".toString()")
        ):
            want_bug = "null_pointer"
        elif re.search(r"while\s*\(\s*true\s*\)", code) and "break" not in code:
            want_bug = "infinite_loop"

    elif language == "c" and "strcpy" in code:
        if re.search(r"\bchar\s+\w+\s*\[[^\]]+\]", code):
            want_bug = "buffer_overflow"

    elif language == "cpp":
        if has_new and not has_delete:
            want_bug = "memory_leak"

    elif language == "python":
        if has_py_bad_len_index:
            want_bug = "index_out_of_range"
        elif has_py_str_int_add:
            want_bug = "type_error"
        elif has_py_while_true and not has_break:
            want_bug = "infinite_loop"

    if not want_bug:
        return None

    best = _nearest_sample_by_bug_type(language, X_input, want_bug)
    if not best:
        return buggy_response(
            code=code,
            language=language,
            confidence=PATTERN_MATCH_CONFIDENCE,
            bug_type=want_bug,
            line_number=1,
            description=f"Pattern match: {want_bug}.",
            fixed_code=code,
        )
    return buggy_response(
        code=code,
        language=language,
        confidence=PATTERN_MATCH_CONFIDENCE,
        bug_type=best.get("bug_type", want_bug),
        line_number=int(best.get("line_number", 1)),
        description=str(best.get("description", f"Pattern match: {want_bug}.")),
        fixed_code=str(best.get("fixed_code", code)),
    )

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index() -> Any:
    return send_from_directory("static", "index.html")


@app.route("/health", methods=["GET"])
def health() -> Any:
    sample_counts = {
        lang: len(sample_lookups[lang]["metadata"])
        for lang in LANGUAGES
    }
    return jsonify({
        "status": "ok",
        "models_loaded": True,
        "sample_counts": sample_counts,
    })


@app.route("/languages", methods=["GET"])
def languages() -> Any:
    return jsonify({"languages": LANGUAGES})


@app.route("/analyze", methods=["POST"])
def analyze() -> Any:
    payload = request.get_json(silent=True) or {}
    code: str = payload.get("code", "")
    language: str = payload.get("language", "").lower()

    print(f"[DEBUG] language={language}")
    print(f"[DEBUG] code preview={code[:100]}")
    print(f"[DEBUG] pattern precheck running...")

    # ── Validation ────────────────────────────────────────────────────────────
    if not code:
        return jsonify({"error": "Code cannot be empty"}), 400
    if language not in LANGUAGES:
        return jsonify({"error": "Unsupported language"}), 400
    if len(code) > MAX_CODE_LEN:
        return jsonify({"error": "Code too long (max 10000 chars)"}), 400

    feature: str = f"{language} {code}"
    X_input = vectorizers[language].transform([feature])

    # ── Pattern precheck (before ML) ─────────────────────────────────────────
    pre = _pattern_bugs_precheck(code, language, X_input)
    if pre is not None:
        return pre

    # ── Fingerprint check — exact match against known fixed_code values ───────
    metadata: dict[int, dict[str, Any]] = sample_lookups[language]["metadata"]
    all_fixes: list[str] = [s["fixed_code"].strip() for s in metadata.values()]
    code_stripped = code.strip()

    if code_stripped in all_fixes:
        return clean_response(code, language)

    # ── Fingerprint check — cosine similarity against vectorised fixed codes ──
    fix_texts: list[str] = [f"{language} {s['fixed_code']}" for s in metadata.values()]
    if fix_texts:
        X_fixes = vectorizers[language].transform(fix_texts)
        fix_sims = cosine_similarity(X_input, X_fixes)[0]
        if float(fix_sims.max()) > 0.97:
            return clean_response(code, language)

    # ── Prediction ────────────────────────────────────────────────────────────
    pred: int = int(models[language].predict(X_input)[0])
    proba: np.ndarray = models[language].predict_proba(X_input)[0]

    # proba[0] = P(clean), proba[1] = P(bug)
    bug_confidence: float = float(proba[1])
    confidence: float

    # ── Model says clean — trust it immediately ───────────────────────────────
    if pred == 0:
        confidence = float(proba[0])
        print(f"[ML] pred={pred}, confidence={confidence}, bug_type=clean")
        return clean_response(code, language, float(proba[0]))

    # ── Find best matching buggy sample to determine the claimed bug type ─────
    buggy_vectors = sample_lookups[language]["vectors"]
    sample_sims = cosine_similarity(X_input, buggy_vectors)[0]
    best_pos: int = int(np.argmax(sample_sims))

    meta_keys: list[int] = list(metadata.keys())
    best_sample: dict[str, Any] = metadata[meta_keys[best_pos]]
    bug_type: str = best_sample.get("bug_type", "Unknown Bug")

    # ── Per-category confidence thresholds ────────────────────────────────────
    # Syntax bugs (missing_semicolon, indentation_error, …) produce far more
    # false positives than semantic bugs.  Require stronger confidence before
    # reporting them; use a lighter threshold for semantic/runtime bugs.
    _SYNTAX_BUG_TYPES = {
        "indentation_error", "syntax_error", "missing_colon",
        "missing_semicolon", "unclosed_brace", "unclosed_bracket",
    }
    is_syntax_bug = bug_type.lower() in _SYNTAX_BUG_TYPES
    if is_syntax_bug:
        min_bug_confidence: float = 0.85
    elif language == "java" and bug_type.lower() == "null_pointer":
        min_bug_confidence = 0.45
    elif language == "python":
        min_bug_confidence = 0.40
    else:
        min_bug_confidence = 0.55

    if bug_confidence < min_bug_confidence:
        confidence = bug_confidence
        print(f"[ML] pred={pred}, confidence={confidence}, bug_type={bug_type}")
        return clean_response(code, language, float(proba[0]))

    # ── Confidence threshold — uncertain zone ─────────────────────────────────
    # When the model predicts a bug but confidence falls below the global
    # threshold, report uncertain rather than a definitive bug detection.
    if bug_confidence < CLEAN_CONFIDENCE_THRESHOLD:
        confidence = bug_confidence
        print(f"[ML] pred={pred}, confidence={confidence}, bug_type={bug_type}")
        return uncertain_response(code, language, bug_confidence)

    # ── Python AST safety net for syntax bugs ─────────────────────────────────
    # ast.parse succeeds on any syntactically valid Python file; a real
    # indentation / syntax bug would raise SyntaxError here.
    if language == "python" and is_syntax_bug:
        try:
            ast.parse(code)
            confidence = bug_confidence
            print(f"[ML] pred={pred}, confidence={confidence}, bug_type={bug_type}")
            return clean_response(code, language, float(proba[0]))
        except SyntaxError:
            pass

    confidence = bug_confidence
    print(f"[ML] pred={pred}, confidence={confidence}, bug_type={bug_type}")
    return buggy_response(
        code=code,
        language=language,
        confidence=bug_confidence,
        bug_type=bug_type,
        line_number=int(best_sample.get("line_number", 1)),
        description=best_sample.get("description", "A bug was detected."),
        fixed_code=best_sample.get("fixed_code", code),
    )


@app.route("/feedback", methods=["POST"])
def feedback() -> Any:
    payload = request.get_json(silent=True) or {}
    code: str = payload.get("code", "")
    language: str = payload.get("language", "")
    was_correct: bool = bool(payload.get("was_correct", False))
    print(f"[feedback] lang={language} correct={was_correct} code_len={len(code)}")
    return jsonify({"status": "ok"}), 200

# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(e: Any) -> Any:
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(Exception)
def handle_exception(e: Exception) -> Any:
    app.logger.error("Unhandled error: %s", str(e), exc_info=True)
    return jsonify({"error": "Internal server error", "detail": str(e)}), 500

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=False, port=5000, host="0.0.0.0")
