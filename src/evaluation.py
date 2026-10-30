"""Evaluation, saved metrics, and plots for a shared held-out test set."""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             roc_auc_score, confusion_matrix, ConfusionMatrixDisplay,
                             roc_curve, auc)


def evaluate_models(models, X_test, y_test, output_dir="results"):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    scores_by_model = {}
    figure, axes = plt.subplots(2, 2, figsize=(11, 9))
    for (name, model), ax in zip(models.items(), axes.flat):
        # Chunk predictions to keep KNN's held-out distance matrix memory bounded.
        predictions = []
        probabilities = []
        for start in range(0, len(X_test), 5000):
            batch = X_test.iloc[start:start + 5000]
            predictions.extend(model.predict(batch))
            probabilities.extend(model.predict_proba(batch)[:, list(model.classes_).index(1)])
        pred = pd.Series(predictions, index=y_test.index)
        row = {"model": name,
               "accuracy": accuracy_score(y_test, pred),
               "phishing_precision": precision_score(y_test, pred, pos_label=1, zero_division=0),
               "phishing_recall": recall_score(y_test, pred, pos_label=1, zero_division=0),
               "phishing_f1": f1_score(y_test, pred, pos_label=1, zero_division=0)}
        scores = probabilities
        scores_by_model[name] = scores
        row["roc_auc"] = roc_auc_score(y_test, scores)
        rows.append(row)
        ConfusionMatrixDisplay(confusion_matrix(y_test, pred, labels=[0, 1]),
                               display_labels=["Legitimate", "Phishing"]).plot(ax=ax, colorbar=False)
        ax.set_title(name)
    figure.tight_layout()
    figure.savefig(out / "confusion_matrices.png", dpi=160)
    plt.close(figure)
    results = pd.DataFrame(rows)
    results.to_csv(out / "model_comparison.csv", index=False)
    metrics = ["accuracy", "phishing_precision", "phishing_recall", "phishing_f1"]
    results.set_index("model")[metrics].plot(kind="bar", ylim=(0, 1), figsize=(10, 5))
    plt.ylabel("Score"); plt.title("Four-model comparison (phishing is positive class)")
    plt.xticks(rotation=15, ha="right"); plt.tight_layout()
    plt.savefig(out / "metric_comparison.png", dpi=160); plt.close()
    fig, ax = plt.subplots(figsize=(7, 6))
    for name in models:
        fpr, tpr, _ = roc_curve(y_test, scores_by_model[name], pos_label=1)
        ax.plot(fpr, tpr, label=f"{name} (AUC={auc(fpr, tpr):.3f})")
    ax.plot([0, 1], [0, 1], linestyle="--", color="gray", linewidth=1, label="Chance")
    ax.set_xlabel("False positive rate")
    ax.set_ylabel("True positive rate")
    ax.legend(loc="lower right", fontsize=8)
    ax.set_title("ROC curves (phishing is positive class)"); fig.tight_layout()
    fig.savefig(out / "roc_curves.png", dpi=160); plt.close(fig)
    return results
