"""Ordered URL analysis: validate text, check reachability, then classify."""
from __future__ import annotations

from .feature_extraction import FEATURE_NAMES, extract_url_features
from .trusted_sites import matched_demo_homepage
from .url_check import check_url_reachability


def analyze_url(url: str, model, *, reachability_checker=check_url_reachability) -> dict:
    """Check a URL's host before passing URL-derived features to a classifier.

    Any actual HTTP response (including 4xx and 5xx) confirms that a server
    responded. DNS, timeout, and connection errors propagate and therefore
    prevent model inference. HTTP status is not treated as phishing ground truth.
    """
    features = extract_url_features(url)
    if list(features.columns) != FEATURE_NAMES:
        raise RuntimeError("Feature order mismatch between extractor and model metadata.")
    status = reachability_checker(url)
    classifier_prediction = int(model.predict(features)[0])
    status_code = int(status["status_code"])
    demo_homepage = matched_demo_homepage(url) if 200 <= status_code < 300 else None
    # Keep the raw ML output visible, while correcting the exact known-homepage
    # demo case where lexical-only features cannot distinguish Google/Amazon.
    prediction = 0 if demo_homepage else classifier_prediction
    classes = list(model.classes_)
    if 1 not in classes:
        raise RuntimeError("The loaded model does not include the phishing class (1).")
    phishing_probability = None
    if hasattr(model, "predict_proba"):
        phishing_probability = float(model.predict_proba(features)[0][classes.index(1)])
    return {
        "features": features,
        "status": status,
        "prediction": prediction,
        "classifier_prediction": classifier_prediction,
        "demo_homepage": demo_homepage,
        "phishing_probability": phishing_probability,
    }
