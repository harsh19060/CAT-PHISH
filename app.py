"""Streamlit user interface for the locally trained URL-only classifiers."""
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

from src.feature_extraction import FEATURE_NAMES
from src.prediction import analyze_url

st.set_page_config(page_title="Phishing URL Lab", page_icon="🛡️", layout="wide")
st.markdown("""
<style>
  .block-container {max-width: 1280px; padding-top: 2.1rem; padding-bottom: 3rem;}
  .hero {padding: 1.5rem 1.7rem; border-radius: 18px; color: white;
         background: linear-gradient(115deg,#102a43 0%,#155e75 58%,#0f766e 100%); margin-bottom: 1.2rem;}
  .hero h1 {font-size: 2.25rem; margin: 0 0 .35rem 0; color: white;}
  .hero p {font-size: 1.03rem; margin: 0; opacity: .92;}
  [data-testid="stMetric"] {background: #1b2029; border: 1px solid #343c49; padding: 1rem; border-radius: 14px;}
  [data-testid="stMetric"] label,
  [data-testid="stMetric"] [data-testid="stMetricLabel"] {color: #bac5d3 !important;}
  [data-testid="stMetric"] [data-testid="stMetricValue"] {color: #f4f7fb !important;}
  [data-testid="stMetric"] [data-testid="stMetricDelta"] {color: #b8c7d9 !important;}
  div[data-testid="stTabs"] button {font-weight: 650;}
</style>
<div class="hero"><h1>🛡️ Phishing URL Detection</h1>
<p>Explore four classic machine-learning classifiers, compare their measured results, and inspect a URL locally.</p></div>
""", unsafe_allow_html=True)
st.caption("Teaching demonstration · URL-only features · bounded HTTP status check before prediction")
MODEL_FILES = {
    "Logistic Regression": "logistic_regression.joblib",
    "K-Nearest Neighbors": "knearest_neighbors.joblib",
    "Decision Tree": "decision_tree.joblib",
    "Gaussian Naive Bayes": "gaussian_naive_bayes.joblib",
}
tab_check, tab_compare, tab_method = st.tabs(["🔎 Check a URL", "📊 Compare models", "ℹ️ How it works"])

with tab_check:
    left, right = st.columns([1.4, 1], gap="large")
    with left:
        model_name = st.selectbox("Classifier", list(MODEL_FILES), key="predict_model")
        url = st.text_input("URL to assess", placeholder="https://example.com/login")
        submitted = st.button("Analyze URL", type="primary", width="stretch")
    with right:
        st.markdown("#### What the model sees")
        st.write("Twenty-five numeric properties are calculated from the URL string. The app first checks whether a public host returns an HTTP response. Only then does it pass those numeric features to the selected model. It does not read the page body or follow redirects.")
        st.caption("Host structure, HTTPS, letters/digits, special characters, encoding, path, and query statistics")
    st.info("The URL is contacted for the status check. Avoid private links or URLs containing access tokens. A 404 means the server responded but that page was not found. If DNS lookup or the connection fails, automatic classification stops.")
    if submitted:
        st.session_state["url_analysis_state"] = None
        try:
            path = Path("models") / MODEL_FILES[model_name]
            if not path.exists():
                raise FileNotFoundError("Trained model missing. Run `python train.py` first.")
            model = joblib.load(path)
            st.session_state["url_analysis_state"] = {"analysis": analyze_url(url, model)}
        except (ValueError, FileNotFoundError, RuntimeError) as exc:
            st.session_state["url_analysis_state"] = {"error": str(exc), "kind": "warning"}
        except (ConnectionError, TimeoutError) as exc:
            st.session_state["url_analysis_state"] = {
                "error": f"Reachability check failed, so the URL was not sent to the model: {exc}",
                "kind": "error",
            }
        except Exception as exc:
            st.session_state["url_analysis_state"] = {
                "error": f"Prediction could not be completed: {exc}",
                "kind": "error",
            }

    output = st.session_state.get("url_analysis_state")
    if output:
        if "error" in output:
            if output["kind"] == "warning":
                st.warning(output["error"])
            else:
                st.error(output["error"])
        else:
            analysis = output["analysis"]
            status = analysis["status"]
            code = status["status_code"]
            if 200 <= code < 300:
                st.success(f"Server responded: HTTP {code} {status['reason']}")
            elif 300 <= code < 400:
                st.warning(f"Server responded with redirect: HTTP {code} {status['reason']}. The redirect was not followed.")
            else:
                st.warning(f"Server responded: HTTP {code} {status['reason']}. A 404 means this page was not found; it does not mean the whole site is offline or prove phishing.")
            if analysis["demo_homepage"]:
                raw_label = "Phishing" if analysis["classifier_prediction"] == 1 else "Legitimate"
                st.info(f"Exact-homepage demo rule matched {analysis['demo_homepage']}; showing Legitimate for this HTTP 2xx homepage. The raw classifier said {raw_label}. This narrow example rule does not vouch for other pages or prove a site is safe.")
            if analysis["prediction"] == 1:
                st.error("### Prediction: Phishing")
            else:
                st.success("### Prediction: Legitimate")
            probability = analysis["phishing_probability"]
            if probability is not None:
                st.metric("Raw classifier phishing score", f"{probability:.1%}")
                st.caption("This always shows the model's score for phishing. It is not calibrated certainty: URL-only features cannot capture a site's full behavior. KNN uses five neighbors, so its scores occur in 20-point steps; 100% means all five neighbors voted phishing, not that the URL is certainly malicious.")
            with st.expander("URL features supplied to the model"):
                st.dataframe(analysis["features"].T.rename(columns={0: "Value"}), width="stretch")
    st.warning("Predictions are estimates. Treat unknown links cautiously, even when marked legitimate.")

with tab_compare:
    results_path = Path("results/model_comparison.csv")
    if results_path.exists():
        results = pd.read_csv(results_path)
        expected = {"model", "accuracy", "phishing_precision", "phishing_recall", "phishing_f1", "roc_auc"}
        if not expected.issubset(results.columns):
            st.error("The saved evaluation file is incomplete. Run `python train.py` to regenerate it.")
        else:
            sort_by = st.selectbox("Rank models by", ["phishing_recall", "phishing_f1", "roc_auc", "accuracy"],
                                   format_func=lambda c: {"phishing_recall":"Phishing recall (recommended)",
                                                          "phishing_f1":"Phishing F1", "roc_auc":"ROC-AUC",
                                                          "accuracy":"Accuracy"}[c])
            ranked = results.sort_values(sort_by, ascending=False).reset_index(drop=True)
            winner = ranked.iloc[0]
            st.success(f"Top by {sort_by.replace('_', ' ')}: **{winner['model']}** — {winner[sort_by]:.1%}")
            metric_cols = st.columns(4)
            metric_labels = [("accuracy", "Accuracy"), ("phishing_precision", "Phishing precision"),
                             ("phishing_recall", "Phishing recall"), ("phishing_f1", "Phishing F1")]
            for col, (field, label) in zip(metric_cols, metric_labels):
                col.metric(label, f"{winner[field]:.1%}", help="Top model under the selected ranking metric")
            st.markdown("#### Scorecard")
            display = ranked.rename(columns={"model":"Model", "accuracy":"Accuracy",
                "phishing_precision":"Phishing precision", "phishing_recall":"Phishing recall",
                "phishing_f1":"Phishing F1", "roc_auc":"ROC-AUC"})
            st.dataframe(display.style.format({c:"{:.1%}" for c in display.columns if c != "Model"})
                         .highlight_max(subset=["Accuracy", "Phishing precision", "Phishing recall", "Phishing F1", "ROC-AUC"], color="#174b35"),
                         hide_index=True, width="stretch")
            st.markdown("#### Compare every metric")
            chart_path = Path("results/metric_comparison.png")
            if chart_path.exists():
                st.image(str(chart_path), caption="Grouped metric scores for all four models (0 to 1 scale)", width="stretch")
            else:
                st.info("Metric chart not found. Run `python train.py` to regenerate the evaluation figures.")
            st.caption("Higher recall catches more phishing URLs but can increase false alarms. Metrics are measured on the same held-out test set.")
            image_cols = st.columns(2)
            for col, filename, caption in [
                (image_cols[0], "confusion_matrices.png", "Confusion matrices (positive class: phishing)"),
                (image_cols[1], "roc_curves.png", "ROC curves; area is shown in the scorecard")]:
                path = Path("results") / filename
                if path.exists(): col.image(str(path), caption=caption, width="stretch")
    else:
        st.info("No measured results are saved yet. Run `python train.py` to download the official dataset, train all four classifiers, and generate comparison charts.")

with tab_method:
    st.markdown("#### Twenty-five URL-only features")
    st.write("The feature set covers URL and hostname structure, HTTPS, letters and digits, special characters, percent encoding, path length, and query-string structure. Training and prediction use the same extractor and fixed feature order. No webpage content is used.")
    st.warning("Demo exception: exact Google.com and Amazon.com homepage URLs with HTTP 2xx receive a Legitimate display override because these hosts are not distinguishable from each other using the numeric URL features. The raw model result is shown separately. This exception does not cover paths, queries, subdomains, other hosts, or prove safety.")
    st.markdown("#### Model guide")
    st.markdown("""
    | Classifier | Basic idea | Practical trade-off |
    |---|---|---|
    | Logistic Regression | Fits a linear decision boundary | Fast baseline; can miss nonlinear patterns |
    | K-Nearest Neighbors | Votes among nearby training examples | Intuitive; distance and prediction cost matter |
    | Decision Tree | Learns feature-threshold rules | Explainable; can overfit |
    | Gaussian Naive Bayes | Combines class probabilities | Fast; assumes features are conditionally independent |
    """)
    st.markdown("#### Limitations")
    st.write("The app cannot inspect page content, follow redirects, assess domain reputation, or query current threat feeds. It performs DNS resolution only to check public-host reachability. The test scores describe this dataset split, not future attacks. Model scores are not calibrated guarantees of safety.")
