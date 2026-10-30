"""Download and inspect the official UCI PhiUSIIL dataset."""
from __future__ import annotations

import pandas as pd
from ucimlrepo import fetch_ucirepo
from pathlib import Path

from .feature_extraction import extract_url_features, FEATURE_NAMES, SOURCE_FEATURE_NAMES


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV_PATH = PROJECT_ROOT / "data" / "PhiUSIIL_Phishing_URL_Dataset.csv"


def load_source_data(csv_path=DEFAULT_CSV_PATH):
    """Load the local official CSV when present; otherwise fetch UCI dataset 967."""
    csv_path = Path(csv_path)
    if csv_path.exists():
        frame = pd.read_csv(csv_path)
        target_matches = [column for column in frame.columns if str(column).strip().lower() == "label"]
        if len(target_matches) != 1:
            raise ValueError(
                f"Expected exactly one 'label' target column in {csv_path}; "
                f"found {target_matches}. Check that this is the official UCI CSV."
            )
        target_name = target_matches[0]
        y = frame[[target_name]].copy()
        # FILENAME is marked as an identifier/other field by UCI, not a predictor.
        X = frame.drop(columns=[target_name] + [c for c in frame.columns if str(c).strip().upper() == "FILENAME"]).copy()
        return X, y, f"local CSV: {csv_path}"

    dataset = fetch_ucirepo(id=967)
    return dataset.data.features.copy(), dataset.data.targets.copy(), "UCI ucimlrepo API (dataset 967)"


def load_dataset(csv_path=DEFAULT_CSV_PATH):
    """Load official data and return URL-only features, phishing target, and audit."""
    X, y, data_source = load_source_data(csv_path)
    if "URL" not in X:
        raise ValueError("The official dataset did not contain the expected URL column.")
    missing_selected = set(SOURCE_FEATURE_NAMES) - set(X.columns)
    if missing_selected:
        raise ValueError(f"Official dataset is missing selected URL feature columns: {sorted(missing_selected)}")
    target_name = y.columns[0]
    original_y = pd.to_numeric(y[target_name], errors="raise")
    observed = set(original_y.dropna().unique())
    if observed != {0, 1}:
        raise ValueError(f"Expected official target labels 0 and 1; found {observed}.")
    # UCI defines 0 as phishing and 1 as legitimate. Keep this project convention.
    phishing_y = (original_y == 0).astype("int8")
    # Avoid constructing one pandas DataFrame per row: this dataset has over 200k URLs.
    derived_rows = [extract_url_features(url, as_frame=False) for url in X["URL"]]
    derived = pd.DataFrame(derived_rows, columns=FEATURE_NAMES, index=X.index)
    consistency = {}
    for feature in SOURCE_FEATURE_NAMES:
        source = pd.to_numeric(X[feature], errors="coerce")
        calculated = pd.to_numeric(derived[feature], errors="coerce")
        consistency[feature] = int((source != calculated).sum())
    audit = {
        "rows": len(X), "feature_columns": X.shape[1],
        "data_source": data_source,
        "column_names": list(X.columns), "dtypes": X.dtypes.astype(str).to_dict(),
        "missing_values": int(X.isna().sum().sum() + y.isna().sum().sum()),
        "duplicate_full_rows": int(pd.concat([X, y], axis=1).duplicated().sum()),
        "original_target_distribution": original_y.value_counts().sort_index().to_dict(),
        "source_vs_url_calculation_mismatches": consistency,
        "first_five_source_rows": X[["URL", *SOURCE_FEATURE_NAMES]].head().to_dict(orient="records"),
        "url_only_invalid_rows_dropped": 0,
    }
    if derived.isna().any().any() or not derived.apply(lambda c: pd.to_numeric(c, errors="coerce").notna().all()).all():
        raise ValueError("URL-derived training features contain invalid values.")
    return derived, phishing_y, audit
