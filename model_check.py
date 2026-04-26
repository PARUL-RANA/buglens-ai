"""
model_check.py — BugLens AI standalone model validation script.

Loads all 12 .pkl files and runs 2 test predictions per language
(1 buggy, 1 clean), printing PASS/FAIL for each.

Usage:
    python model_check.py
"""

import sys
from typing import Any

import joblib
import numpy as np

LANGUAGES: list[str] = ["java", "c", "cpp", "python"]

# ---------------------------------------------------------------------------
# Test cases: (label, code, expect_is_bug)
# ---------------------------------------------------------------------------
TEST_CASES: dict[str, list[tuple[str, str, bool]]] = {
    "java": [
        (
            "buggy  — unclosed brace",
            (
                "public class ConfigLoader {\n"
                "    public void display() {\n"
                "        int result = 0;\n"
                "        while (result < 4) {\n"
                "            result++;\n"
                "        // missing closing brace for while\n"
                "        System.out.println(result);\n"
                "    }\n"
                "}"
            ),
            True,
        ),
        (
            "clean  — try-with-resources",
            (
                "import java.io.FileInputStream;\n"
                "import java.io.IOException;\n"
                "public class Resolver {\n"
                "    public void dispatch() throws IOException {\n"
                "        try (FileInputStream frame = new FileInputStream(\"data.txt\")) {\n"
                "            int b = frame.read();\n"
                "            System.out.println(b);\n"
                "        }\n"
                "    }\n"
                "}"
            ),
            False,
        ),
    ],
    "c": [
        (
            "buggy  — missing return value",
            (
                "#include <stdio.h>\n"
                "\n"
                "int append(int entry) {\n"
                "    int x = entry * 10;\n"
                "    int y = x + 1;\n"
                "}"
            ),
            True,
        ),
        (
            "clean  — conditional return",
            (
                "#include <stdio.h>\n"
                "\n"
                "int calculate(int source) {\n"
                "    if (source > 11) {\n"
                "        return 1;\n"
                "    }\n"
                "    return 0;\n"
                "}"
            ),
            False,
        ),
    ],
    "cpp": [
        (
            "buggy  — missing include for cout",
            (
                "void decompress(int target) {\n"
                "    if (target >= 0) std::cout << target << std::endl;\n"
                "    else std::cerr << \"negative\" << std::endl;\n"
                "}"
            ),
            True,
        ),
        (
            "clean  — string output with includes",
            (
                "#include <iostream>\n"
                "#include <string>\n"
                "\n"
                "void serialize() {\n"
                "    std::string descriptor = \"hello\";\n"
                "    std::cout << descriptor << std::endl;\n"
                "}"
            ),
            False,
        ),
    ],
    "python": [
        (
            "buggy  — indentation error",
            "def foo():\nreturn 42",
            True,
        ),
        (
            "clean  — fibonacci",
            "def fib(n):\n    if n <= 1:\n        return n\n    return fib(n-1) + fib(n-2)",
            False,
        ),
    ],
}

# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def load_artifacts(lang: str) -> tuple[Any, Any] | None:
    """Load (model, vectorizer) for *lang*; return None on failure."""
    model_path = f"model/{lang}_model.pkl"
    vec_path = f"model/{lang}_vectorizer.pkl"
    try:
        model = joblib.load(model_path)
        vectorizer = joblib.load(vec_path)
        return model, vectorizer
    except FileNotFoundError as exc:
        print(f"  [LOAD ERROR] {exc}")
        return None


def run_checks() -> int:
    """Run all checks; return number of failures."""
    total = 0
    failures = 0

    print("=" * 60)
    print("  BugLens AI - Model Check")
    print("=" * 60)

    for lang in LANGUAGES:
        print(f"\n  Language: {lang.upper()}")
        print(f"  {'-'*50}")

        artifacts = load_artifacts(lang)
        if artifacts is None:
            for label, _, _ in TEST_CASES[lang]:
                print(f"    [{lang}] {label:<42}  FAIL  (model not loaded)")
                failures += 1
                total += 1
            continue

        model, vectorizer = artifacts

        for label, code, expect_bug in TEST_CASES[lang]:
            total += 1
            try:
                feature = f"{lang} {code}"
                X = vectorizer.transform([feature])
                pred: int = int(model.predict(X)[0])
                proba: np.ndarray = model.predict_proba(X)[0]
                predicted_bug = pred == 1
                confidence = float(proba[1] if predicted_bug else proba[0])

                if predicted_bug == expect_bug:
                    status = "PASS"
                else:
                    status = "FAIL"
                    failures += 1

                expected_str = "bug  " if expect_bug else "clean"
                predicted_str = "bug  " if predicted_bug else "clean"
                print(
                    f"    [{lang}] {label:<42}  {status}"
                    f"  (expected={expected_str} got={predicted_str} conf={confidence:.3f})"
                )
            except Exception as exc:
                print(f"    [{lang}] {label:<42}  FAIL  (exception: {exc})")
                failures += 1

    print(f"\n{'='*60}")
    passed = total - failures
    print(f"  Results: {passed}/{total} passed", end="")
    if failures == 0:
        print("  — ALL PASS")
    else:
        print(f"  — {failures} FAILED")
    print("=" * 60)

    return failures


if __name__ == "__main__":
    sys.exit(run_checks())
