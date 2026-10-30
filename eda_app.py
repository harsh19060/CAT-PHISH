"""Classroom walkthrough of the PhiUSIIL dataset and URL-only preprocessing.

Run from the project root with:
    .venv\\Scripts\\python.exe -m streamlit run eda_app.py
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st
from sklearn.model_selection import train_test_split

from src.data_loader import load_source_data
from src.feature_extraction import FEATURE_NAMES, extract_url_features
from src.model_training import build_models


st.set_page_config(page_title="Phishing URL EDA", page_icon="📊", layout="wide")
st.markdown("""
<style>
  .block-container {max-width: 1380px; padding-top: 1.8rem; padding-bottom: 3rem;}
  .hero {padding: 1.45rem 1.7rem; border-radius: 18px; color: white;
         background: linear-gradient(115deg,#102a43 0%,#155e75 58%,#0f766e 100%); margin-bottom: 1rem;}
  .hero h1 {font-size: 2.1rem; margin: 0 0 .35rem 0; color: white;}
  .hero p {font-size: 1rem; margin: 0; opacity: .92;}
  [data-testid="stMetric"] {background: #1b2029; border: 1px solid #343c49; padding: 1rem; border-radius: 14px;}
  [data-testid="stMetric"] label, [data-testid="stMetric"] [data-testid="stMetricLabel"] {color: #bac5d3 !important;}
  [data-testid="stMetric"] [data-testid="stMetricValue"] {color: #f4f7fb !important;}
</style>
<div class="hero"><h1>📊 Explore the dataset and preprocessing</h1>
<p>A guided, reproducible look at the real UCI data and the exact URL-only inputs used by the classifiers.</p></div>
""", unsafe_allow_html=True)
st.caption("Classroom presentation mode · UCI dataset 967 · URL strings are analyzed locally")


@st.cache_data(show_spinner="Fetching and preparing the official UCI dataset…")
def get_eda_data():
    """Fetch once per Streamlit cache and calculate features through shared code."""
    source, targets, data_source = load_source_data()
    if "URL" not in source or targets.shape[1] < 1:
        raise ValueError("The fetched UCI dataset is missing its expected URL or target column.")
    original = pd.to_numeric(targets.iloc[:, 0], errors="raise")
    if set(original.dropna().unique()) != {0, 1}:
        raise ValueError("Expected UCI target labels 0 and 1.")
    # UCI label 0 means phishing; the project convention makes phishing positive.
    y = (original == 0).astype("int8").rename("target_phishing")
    features = pd.DataFrame(
        [extract_url_features(url, as_frame=False) for url in source["URL"]],
        columns=FEATURE_NAMES,
        index=source.index,
    )
    combined = pd.concat([source, targets], axis=1)
    mismatch_counts = {
        col: int((pd.to_numeric(source[col], errors="coerce") != features[col]).sum())
        for col in FEATURE_NAMES if col in source.columns
    }
    url_labels = pd.DataFrame({"URL": source["URL"], "original_label": original})
    url_groups = url_labels.groupby("URL", dropna=False)["original_label"].agg(["size", "nunique"])
    audit = {
        "data_source": data_source,
        "rows": len(source),
        "input_columns": source.shape[1],
        "missing_cells": int(combined.isna().sum().sum()),
        "duplicate_full_rows": int(combined.duplicated().sum()),
        "repeated_url_groups": int((url_groups["size"] > 1).sum()),
        "conflicting_label_url_groups": int((url_groups["nunique"] > 1).sum()),
        "original_label_counts": original.value_counts().sort_index().to_dict(),
        "project_label_counts": y.value_counts().sort_index().to_dict(),
        "mismatches_vs_stored_url_features": mismatch_counts,
    }
    return source, original, features, y, audit


try:
    source, original_y, X, y, audit = get_eda_data()
except Exception as exc:
    st.error(f"Could not load the official UCI data: {exc}")
    st.info("Check network access to the UCI repository, then reload this page. No alternate dataset is used.")
    st.stop()


overview, cleaning, features_tab, preprocessing = st.tabs([
    "1 · Dataset overview", "2 · Inspect & clean", "3 · URL-only features", "4 · Split & scale"
])

with overview:
    st.markdown("### What is in the dataset?")
    st.write("Each row represents a URL and corresponding webpage record. The source has URL fields plus webpage-derived fields; this project uses only values that can be calculated from the URL string.")
    st.caption(f"Loaded from: {audit['data_source']}")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Records", f"{audit['rows']:,}")
    m2.metric("Source input columns", str(audit["input_columns"]))
    m3.metric("Missing cells", f"{audit['missing_cells']:,}")
    m4.metric("Exact duplicate rows", f"{audit['duplicate_full_rows']:,}")
    c1, c2 = st.columns([1, 1.2], gap="large")
    with c1:
        st.markdown("#### Original target labels")
        original_counts = pd.Series(audit["original_label_counts"], name="URLs")
        original_counts.index = ["0 · Phishing", "1 · Legitimate"]
        st.bar_chart(original_counts, y_label="Records", color="#2dd4bf")
        st.caption("Official mapping: 0 = phishing; 1 = legitimate.")
    with c2:
        st.markdown("#### Source fields and data types")
        dtype_table = pd.DataFrame({"Column": source.columns, "Data type": source.dtypes.astype(str).values})
        st.dataframe(dtype_table, hide_index=True, height=390, width="stretch")
    st.markdown("#### First five source records")
    st.dataframe(pd.concat([source.head(5), original_y.rename("Original target")], axis=1),
                 hide_index=True, width="stretch")

with cleaning:
    st.markdown("### What was checked, and what was changed?")
    st.write("The data loader checks missing values, exact duplicate full rows, target labels, numeric feature validity, repeated URL strings, and repeated URLs with conflicting labels. It does not remove rows just because URLs repeat.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Repeated URL groups", f"{audit['repeated_url_groups']:,}")
    c2.metric("Repeated URLs with conflicting labels", f"{audit['conflicting_label_url_groups']:,}")
    c3.metric("Rows removed", "0")
    st.markdown("#### Target mapping used by this project")
    st.code("Original UCI label 0  →  project target 1 (Phishing)\nOriginal UCI label 1  →  project target 0 (Legitimate)", language="text")
    st.dataframe(pd.DataFrame({
        "Meaning": ["Legitimate", "Phishing"],
        "Original UCI label": [1, 0],
        "Project target (positive class = phishing)": [0, 1],
        "Records": [audit["original_label_counts"].get(1, 0), audit["original_label_counts"].get(0, 0)],
    }), hide_index=True, width="stretch")

with features_tab:
    st.markdown("### Features the URL-only app can calculate")
    descriptions = {
        "URLLength": "Character count of the supplied URL string.",
        "DomainLength": "Character count of the parsed hostname.",
        "IsDomainIP": "1 when the hostname parses as an IP address; otherwise 0.",
        "TLDLength": "Character count of the hostname's last dot-separated label; 0 for an IP.",
        "NoOfSubDomain": "Hostname label count before the final two labels, with a minimum of 0.",
        "IsHTTPS": "1 when the URL uses HTTPS; a URL entered without a scheme is treated as HTTPS.",
        "NoOfLettersInURL": "Count of alphabetic characters in the normalized URL string.",
        "NoOfDigitsInURL": "Count of numeric digits in the normalized URL string.",
        "NoOfAtSymbols": "Count of @ characters in the normalized URL string.",
        "HasPercentEncoding": "1 when a percent sign is followed by two hexadecimal digits, such as %2F.",
        "LetterRatioInURL": "Alphabetic-character count divided by normalized URL length.",
        "DigitRatioInURL": "Digit count divided by normalized URL length.",
        "NoOfEqualsInURL": "Count of = characters in the normalized URL string.",
        "NoOfQuestionMarksInURL": "Count of ? characters in the normalized URL string.",
        "NoOfAmpersandsInURL": "Count of & characters in the normalized URL string.",
        "NoOfDotsInURL": "Count of periods across the entire normalized URL string.",
        "NoOfHyphensInURL": "Count of hyphens across the entire normalized URL string.",
        "NoOfSlashesInURL": "Count of forward slashes, including the two in the scheme separator.",
        "NoOfNonAlphanumericCharsInURL": "Count of characters outside ASCII letters and digits.",
        "NonAlphanumericRatioInURL": "Non-alphanumeric character count divided by normalized URL length.",
        "PathLength": "Character count of the parsed path, excluding query and fragment.",
        "QueryLength": "Character count of the parsed query, excluding ? and fragment.",
        "QueryParameterCount": "0 when no query exists; otherwise ampersand count in the query plus one.",
        "NoOfPercentEncodings": "Count of valid percent-encoded triplets such as %2F.",
        "PercentEncodedRatioInURL": "Percent-encoded triplet count divided by normalized URL length.",
    }
    st.dataframe(pd.DataFrame({"Feature": FEATURE_NAMES,
                               "Calculation": [descriptions[name] for name in FEATURE_NAMES]}),
                 hide_index=True, width="stretch")
    st.markdown("#### Why these features were selected")
    rationale = {
        "URLLength": "Captures how long the complete URL string is; unusually long URLs can hide paths or parameters. It is directly computable without opening the site.",
        "DomainLength": "Captures the size of the hostname itself, separate from the path and query string.",
        "IsDomainIP": "Flags URLs that use a numeric IP address as the host instead of a conventional domain name.",
        "TLDLength": "Captures the length of the final hostname label (for example, 'com' has length 3).",
        "NoOfSubDomain": "Captures hostname complexity by counting labels before the final two hostname labels.",
        "IsHTTPS": "Records whether the URL uses HTTPS. Encryption does not prove a site is legitimate, but scheme use can be informative alongside other signals.",
        "NoOfLettersInURL": "Measures alphabetic characters across the full URL, capturing differences in URL composition.",
        "NoOfDigitsInURL": "Counts digits across the URL; unusually digit-heavy links can be a useful structural signal.",
        "NoOfAtSymbols": "Counts @ symbols, which can be used to make a URL's apparent destination confusing.",
        "HasPercentEncoding": "Flags percent-encoded byte sequences such as %2F, which can obscure URL text.",
        "LetterRatioInURL": "Separates alphabetic density from raw length so different-sized URLs can be compared.",
        "DigitRatioInURL": "Measures how much of the URL is numeric, normalized for URL length.",
        "NoOfEqualsInURL": "Counts assignment-like delimiters commonly used in query strings.",
        "NoOfQuestionMarksInURL": "Counts query delimiters; repeated or misplaced delimiters can change URL parsing.",
        "NoOfAmpersandsInURL": "Counts separators often used between query parameters.",
        "NoOfDotsInURL": "Measures dot usage across host and path/query text, complementing hostname-only subdomain count.",
        "NoOfHyphensInURL": "Measures hyphen use, which can appear in long or deceptive hostname and path strings.",
        "NoOfSlashesInURL": "Measures path and scheme separator structure across the full URL.",
        "NoOfNonAlphanumericCharsInURL": "Captures punctuation density using one explicit, reproducible character rule.",
        "NonAlphanumericRatioInURL": "Normalizes punctuation count by total length to distinguish density from size.",
        "PathLength": "Measures path complexity separately from hostname and query text.",
        "QueryLength": "Measures query complexity separately from hostname and path.",
        "QueryParameterCount": "Captures the number of query segments separated by ampersands.",
        "NoOfPercentEncodings": "Counts encoded byte triplets rather than only recording whether any were found.",
        "PercentEncodedRatioInURL": "Normalizes encoded-triplet count by total URL length.",
    }
    st.dataframe(pd.DataFrame({"Feature": FEATURE_NAMES,
                               "Reason for including it": [rationale[name] for name in FEATURE_NAMES]}),
                 hide_index=True, width="stretch")
    st.caption("All 25 features are calculated from the URL string using the same definitions during training and prediction. Several extra counts are project-defined and may differ from similarly named UCI fields. Page content and external reputation statistics are excluded because a raw URL alone cannot supply them.")
    st.markdown("#### Correlation with the phishing target")
    correlation_data = X.copy()
    correlation_data["target_phishing"] = y
    correlation = correlation_data.corr(method="pearson")
    target_correlations = correlation["target_phishing"].drop("target_phishing")
    ranked_correlations = pd.DataFrame({
        "Feature": target_correlations.index,
        "Correlation with phishing target": target_correlations.values,
        "Absolute correlation": target_correlations.abs().values,
    }).sort_values("Absolute correlation", ascending=False)
    st.dataframe(ranked_correlations.style.format({
        "Correlation with phishing target": "{:+.3f}", "Absolute correlation": "{:.3f}"
    }), hide_index=True, width="stretch")
    corr_fig, corr_ax = plt.subplots(figsize=(14, 12))
    sns.heatmap(correlation, annot=True, fmt=".2f", cmap="coolwarm", center=0,
                vmin=-1, vmax=1, square=True, linewidths=.5, ax=corr_ax,
                annot_kws={"size": 6},
                cbar_kws={"label": "Pearson correlation"})
    corr_ax.set_title("URL-only features and target (1 = phishing)")
    corr_fig.tight_layout()
    st.pyplot(corr_fig, width="stretch")
    plt.close(corr_fig)
    strongest = ranked_correlations.iloc[0]
    st.caption(f"Largest absolute linear correlation in this run: {strongest['Feature']} ({strongest['Correlation with phishing target']:+.3f}). Correlation is association, not causation; it is univariate and may miss nonlinear effects or interactions. Model importance is not the same as correlation.")
    st.markdown("#### Actual feature distributions by class")
    plot_columns = 4
    plot_rows = (len(FEATURE_NAMES) + plot_columns - 1) // plot_columns
    fig, axes = plt.subplots(plot_rows, plot_columns, figsize=(15, 2.8 * plot_rows))
    axes = axes.flat
    for ax, name in zip(axes, FEATURE_NAMES):
        ax.hist([X.loc[y == 0, name], X.loc[y == 1, name]], bins=30,
                label=["Legitimate", "Phishing"], color=["#38bdf8", "#fb7185"], alpha=.78)
        ax.set_title(name)
        ax.set_ylabel("Records")
        ax.legend(fontsize=8)
        ax.grid(axis="y", alpha=.18)
    for ax in list(axes)[len(FEATURE_NAMES):]:
        ax.axis("off")
    fig.tight_layout()
    st.pyplot(fig, width="stretch")
    plt.close(fig)
    st.markdown("#### URL-derived sample used for training")
    sample = X.head(10).copy()
    sample.insert(0, "URL", source.loc[sample.index, "URL"])
    sample["Target: 1=phishing"] = y.loc[sample.index]
    st.dataframe(sample, hide_index=True, width="stretch")
    mismatch = audit["mismatches_vs_stored_url_features"]
    if mismatch:
        st.warning("The extractor recalculates these values from the raw URL. In this run, mismatches versus the stored UCI columns were: "
                   + ", ".join(f"{name}: {count:,}" for name, count in mismatch.items())
                   + ". Models and UI both use the recalculated values; this does not reproduce the stored URLLength values exactly.")
    st.caption("Webpage-only features are excluded. This EDA page never contacts dataset URLs; the separate prediction app makes a bounded status request only when you submit a URL.")

with preprocessing:
    st.markdown("### Split first; learn scaling from training data only")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=.20, random_state=42, stratify=y
    )
    c1, c2 = st.columns(2)
    c1.metric("Training records", f"{len(X_train):,}")
    c2.metric("Held-out test records", f"{len(X_test):,}")
    proportions = pd.DataFrame({
        "Train": y_train.value_counts(normalize=True).sort_index(),
        "Test": y_test.value_counts(normalize=True).sort_index(),
    })
    proportions.index = ["Legitimate (0)", "Phishing (1)"]
    st.markdown("#### Stratification preserves class proportions")
    st.dataframe(proportions.style.format("{:.1%}"), width="stretch")
    st.markdown("#### Scaling demonstration: Logistic Regression / KNN")
    st.write("The same median imputer and StandardScaler used in the model pipelines are fitted on training rows only. The held-out test rows are transformed using those already-fitted training statistics.")
    pipeline = build_models()["Logistic Regression"]
    imputer = pipeline.named_steps["imputer"]
    scaler = pipeline.named_steps["scaler"]
    train_imputed = imputer.fit_transform(X_train)
    test_imputed = imputer.transform(X_test)
    train_scaled = pd.DataFrame(scaler.fit_transform(train_imputed), columns=FEATURE_NAMES, index=X_train.index)
    test_scaled = pd.DataFrame(scaler.transform(test_imputed), columns=FEATURE_NAMES, index=X_test.index)
    st.markdown("**First five training rows: raw derived values → scaled values**")
    preview_index = X_train.index[:5]
    raw_preview = X_train.loc[preview_index].add_prefix("Raw · ")
    scaled_preview = train_scaled.loc[preview_index].add_prefix("Scaled · ")
    st.dataframe(pd.concat([raw_preview, scaled_preview], axis=1).reset_index(drop=True),
                 hide_index=True, width="stretch")
    st.markdown("**First five test rows after applying the training-fitted scaler**")
    st.dataframe(test_scaled.head().reset_index(drop=True), hide_index=True, width="stretch")
    st.info("Decision Tree and Gaussian Naive Bayes use median imputation but do not use feature scaling. In this dataset there are no missing cells, so imputation leaves the numeric values unchanged.")
    st.caption("The displayed split uses the project's exact settings: test_size=0.20, random_state=42, stratify=y.")
