"""
train_model.py — BugLens AI model training pipeline.

Trains one model per language (java, c, cpp, python).
Saves 3 files per language:
    model/{lang}_model.pkl
    model/{lang}_vectorizer.pkl
    model/{lang}_samples.pkl
"""

import os
import sys
import warnings
from typing import Any

import joblib
import numpy as np
import pandas as pd
import scipy.sparse as sp
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import FeatureUnion

warnings.filterwarnings("ignore")

LANGUAGES: list[str] = ["java", "c", "cpp", "python"]
DATA_PATH: str = os.path.join("data", "training_data.csv")
MODEL_DIR: str = "model"

# ── Vectorizer config (Critical Fix 1) ──────────────────────────────────────

def build_vectorizer() -> FeatureUnion:
    word_vectorizer = TfidfVectorizer(
        token_pattern=r"(?u)\b\w+\b",
        ngram_range=(1, 2),
        max_features=8000,
        sublinear_tf=True,
        lowercase=False,
    )
    char_vectorizer = TfidfVectorizer(
        analyzer="char",
        ngram_range=(2, 4),
        max_features=4000,
        sublinear_tf=True,
        lowercase=False,
    )
    return FeatureUnion([("word", word_vectorizer), ("char", char_vectorizer)])


# ── Classifier config (Critical Fix 2) ───────────────────────────────────────

def build_model() -> CalibratedClassifierCV:
    base_rf = RandomForestClassifier(
        n_estimators=300,
        max_depth=25,
        min_samples_split=5,
        class_weight="balanced",
        n_jobs=-1,
        random_state=42,
    )
    return CalibratedClassifierCV(base_rf, cv=5, method="isotonic")


# ── Sample store ──────────────────────────────────────────────────────────────

def build_sample_store(
    df_buggy: pd.DataFrame,
    vectorizer: FeatureUnion,
) -> dict[str, Any]:
    """Return a dict with metadata and vectorised sparse matrix for buggy rows."""
    metadata: dict[int, dict[str, Any]] = {}
    for idx, row in df_buggy.iterrows():
        metadata[int(idx)] = {
            "code": row["code"],
            "bug_type": row.get("bug_type", ""),
            "line_number": int(row.get("line_number", 0)),
            "description": row.get("description", ""),
            "fixed_code": row.get("fixed_code", ""),
        }

    feature_texts = (df_buggy["language"] + " " + df_buggy["code"]).tolist()
    vectors: sp.csr_matrix = vectorizer.transform(feature_texts)  # type: ignore[assignment]

    return {"metadata": metadata, "vectors": vectors}


# ── Fix validation ────────────────────────────────────────────────────────────

def validate_fixes(
    lang: str,
    df_lang: pd.DataFrame,
    vectorizer: FeatureUnion,
    model: CalibratedClassifierCV,
) -> None:
    """Predict fixed_code samples and report how many are classified as clean."""
    df_buggy = df_lang[df_lang["is_bug"] == 1].copy()
    fixed_texts = (lang + " " + df_buggy["fixed_code"].astype(str)).tolist()

    if not fixed_texts:
        print(f"  Fix validation [{lang}]: no fixed samples found.")
        return

    X_fixed = vectorizer.transform(fixed_texts)
    preds = model.predict(X_fixed)
    clean_count = int(np.sum(preds == 0))
    total = len(preds)
    pct = 100 * clean_count / total if total else 0

    print(f"  Fix validation [{lang}]: {clean_count}/{total} fixes correctly identified as clean ({pct:.1f}%)")
    if pct < 90:
        print(f"  WARNING: fix validation below 90% for {lang} ({pct:.1f}%).")


# ── Per-language training ─────────────────────────────────────────────────────

def train_language(lang: str, df: pd.DataFrame) -> dict[str, Any]:
    """Train, evaluate, save, and return a result summary dict."""
    print(f"\n{'='*60}")
    print(f"  Training language: {lang.upper()}")
    print(f"{'='*60}")

    df_lang = df[df["language"] == lang].copy()
    if len(df_lang) < 10:
        print(f"  Too few samples ({len(df_lang)}). Skipping.")
        return {}

    # Critical Fix 3 — prefix every sample with its language token
    X_text: pd.Series = df_lang["language"] + " " + df_lang["code"]
    y: pd.Series = df_lang["is_bug"].astype(int)

    X_train_text, X_test_text, y_train, y_test = train_test_split(
        X_text, y, test_size=0.2, random_state=42, stratify=y
    )

    vectorizer = build_vectorizer()
    model = build_model()

    X_train = vectorizer.fit_transform(X_train_text)
    X_test = vectorizer.transform(X_test_text)

    model.fit(X_train, y_train)

    # ── Evaluation ────────────────────────────────────────────────────────────
    train_acc = float(np.mean(model.predict(X_train) == y_train.to_numpy()))
    test_preds = model.predict(X_test)
    test_acc = float(np.mean(test_preds == y_test.to_numpy()))

    print(f"\n  Training accuracy : {train_acc:.4f}")
    print(f"  Test accuracy     : {test_acc:.4f}")
    print("\n  Classification report:")
    print(classification_report(y_test, test_preds, target_names=["clean", "bug"], zero_division=0))
    print("  Confusion matrix:")
    cm = confusion_matrix(y_test, test_preds)
    print(f"    TN={cm[0,0]}  FP={cm[0,1]}")
    print(f"    FN={cm[1,0]}  TP={cm[1,1]}")

    # ── Fix validation ─────────────────────────────────────────────────────────
    validate_fixes(lang, df_lang, vectorizer, model)

    # ── Persist ───────────────────────────────────────────────────────────────
    os.makedirs(MODEL_DIR, exist_ok=True)
    model_path = os.path.join(MODEL_DIR, f"{lang}_model.pkl")
    vec_path = os.path.join(MODEL_DIR, f"{lang}_vectorizer.pkl")
    samples_path = os.path.join(MODEL_DIR, f"{lang}_samples.pkl")

    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vec_path)

    df_buggy = df_lang[df_lang["is_bug"] == 1].copy()
    sample_store = build_sample_store(df_buggy, vectorizer)
    joblib.dump(sample_store, samples_path)

    print(f"\n  Saved: {model_path}")
    print(f"  Saved: {vec_path}")
    print(f"  Saved: {samples_path}")

    return {
        "language": lang,
        "total_samples": len(df_lang),
        "train_samples": len(y_train),
        "test_samples": len(y_test),
        "train_acc": train_acc,
        "test_acc": test_acc,
    }


# ── Main entry point ──────────────────────────────────────────────────────────

def main() -> None:
    if not os.path.exists(DATA_PATH):
        print(f"[ERROR] Data file not found: {DATA_PATH}")
        print("Run  python generate_data.py  first.")
        sys.exit(1)

    print(f"Loading dataset from {DATA_PATH} ...")
    df = pd.read_csv(DATA_PATH)
    df["code"] = df["code"].fillna("").astype(str)
    df["fixed_code"] = df["fixed_code"].fillna("").astype(str)
    df["language"] = df["language"].astype(str)
    df["is_bug"] = df["is_bug"].astype(int)

    print(f"  Total rows : {len(df)}")
    print(f"  Buggy rows : {int(df['is_bug'].sum())}")
    print(f"  Clean rows : {int((df['is_bug'] == 0).sum())}")
    print(f"  Languages  : {df['language'].value_counts().to_dict()}")

    results: list[dict[str, Any]] = []
    for lang in LANGUAGES:
        result = train_language(lang, df)
        if result:
            results.append(result)

    # ── Summary table ─────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("  FINAL SUMMARY")
    print(f"{'='*60}")
    header = f"{'Lang':<8} {'Total':>7} {'Train':>7} {'Test':>6} {'TrainAcc':>10} {'TestAcc':>9}"
    print(header)
    print("-" * len(header))
    for r in results:
        print(
            f"{r['language']:<8} {r['total_samples']:>7} {r['train_samples']:>7} "
            f"{r['test_samples']:>6} {r['train_acc']:>10.4f} {r['test_acc']:>9.4f}"
        )
    print(f"\nAll models saved to '{MODEL_DIR}/'.")


if __name__ == "__main__":
    main()
