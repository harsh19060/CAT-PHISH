"""Reproducible end-to-end training script. Run from the repository root."""
import json
from pathlib import Path

import joblib
from sklearn.model_selection import train_test_split

from src.data_loader import load_dataset
from src.evaluation import evaluate_models
from src.feature_extraction import FEATURE_NAMES
from src.model_training import build_models


def main():
    models_dir = Path("models"); models_dir.mkdir(exist_ok=True)
    results_dir = Path("results"); results_dir.mkdir(exist_ok=True)
    X, y, audit = load_dataset()
    print(f"Rows: {audit['rows']}; original input columns: {audit['feature_columns']}")
    print("First five derived URL-only training rows:")
    print(X.head().to_string(index=False))
    print("First five source rows for selected-column inspection:")
    print(audit["first_five_source_rows"])
    print("Columns:", audit["column_names"])
    print("Original labels (0=phishing, 1=legitimate):", audit["original_target_distribution"])
    print("Missing:", audit["missing_values"], "exact duplicate full rows:", audit["duplicate_full_rows"])
    print("URL-only feature order:", FEATURE_NAMES)
    mismatches = audit["source_vs_url_calculation_mismatches"]
    if any(mismatches.values()):
        print("Source-feature comparison (mismatches by column):", mismatches)
        if mismatches.get("URLLength", 0):
            print("Note: training uses the literal URLLength computed by the shared extractor; ")
            print("it does not substitute the dataset's stored URLLength values.")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y)
    models = build_models()
    for model in models.values():
        model.fit(X_train, y_train)
    metrics = evaluate_models(models, X_test, y_test, results_dir)
    for name, model in models.items():
        safe_name = name.lower().replace(" ", "_").replace("-", "")
        joblib.dump(model, models_dir / f"{safe_name}.joblib")
    best = metrics.sort_values(["phishing_recall", "phishing_f1"], ascending=False).iloc[0]["model"]
    (models_dir / "model_metadata.json").write_text(json.dumps({
        "feature_names": FEATURE_NAMES, "target": "1=phishing, 0=legitimate",
        "best_model_by_phishing_recall_then_f1": best,
        "dataset": "UCI PhiUSIIL dataset 967", "random_state": 42, "test_size": 0.2,
    }, indent=2), encoding="utf-8")
    (results_dir / "data_audit.json").write_text(json.dumps(audit, indent=2, default=str), encoding="utf-8")
    print(metrics.to_string(index=False)); print(f"Best by phishing recall then F1: {best}")


if __name__ == "__main__":
    main()
