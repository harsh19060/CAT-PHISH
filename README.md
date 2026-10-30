# Phishing URL Detection Using Machine Learning

Beginner-friendly lab comparing exactly four classifiers on the official UCI PhiUSIIL dataset. UCI maps original label `0` to phishing and `1` to legitimate; this project remaps to `1 = phishing`, `0 = legitimate` throughout evaluation and prediction.

## Setup (Windows PowerShell, macOS, Linux)

```bash
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python train.py
streamlit run app.py
```

Training uses `ucimlrepo.fetch_ucirepo(id=967)`. An internet connection is needed the first time. Dataset is 54.2 MB on UCI and is not committed. The UCI record is CC BY 4.0; cite Prasad and Chandra (2024). If fetch fails, verify access to UCI, then retry the same `python train.py`; do not substitute a different dataset.

If you download the official CSV manually, save it as `data/PhiUSIIL_Phishing_URL_Dataset.csv`. Training and the EDA page will use this local file automatically; otherwise they fetch dataset 967 with `ucimlrepo`. The `data/` folder is git-ignored, so the CSV will not be committed.

## Feature consistency

Training and the prediction app call `src.feature_extraction.extract_url_features` to calculate 25 numeric features from the URL: URL/domain structure, HTTPS, letters/digits, special-character counts, percent encoding, path length, and query structure. The fixed names and definitions are in `src/feature_extraction.py`; several are project-defined lexical features, not exact reproductions of similarly named UCI fields. Before prediction, `app.py` makes one bounded HTTP request to public hosts. It does not follow redirects or read page content. Any HTTP response, including 404 or 500, proceeds to classification: a 404 means the server answered but the requested page was not found. DNS, timeout, and connection failures stop automatic classification. The model never receives page contents or the HTTP status as features. The demo also has a narrow exact-homepage display override for `google.com`, `www.google.com`, `amazon.com`, and `www.amazon.com` after an HTTP 2xx response; it shows the raw classifier result separately. This exception covers only the homepage without path/query/fragment and does not make those sites or their other pages inherently safe. Do not submit private links or URLs containing access tokens. This remains a classroom demo; review the URL-check behavior before exposing it as a public service.

## Models

Logistic Regression and KNN use training-only imputation/scaling pipelines. Decision Tree (depth capped at 12) and Gaussian Naive Bayes use training-only imputation without scaling. `train.py` makes one 80/20 stratified split with random state 42. It saves four models, measured metrics, an audit, and plots. Winner selection prioritizes phishing recall, then phishing F1; recall captures how many phishing cases were caught, while precision reflects false alarms.

## Run tests and deployment

```bash
python -m unittest discover -s tests -v
```

## Classroom EDA walkthrough

Run the separate interactive data exploration and preprocessing presentation:

```bash
.venv/Scripts/python.exe -m streamlit run eda_app.py
```

On Windows Command Prompt, use backslashes: `.venv\Scripts\python.exe -m streamlit run eda_app.py`. This page fetches the same official UCI dataset and shows real class counts, data-quality checks, URL-feature distributions, source-feature mismatches, the project's label remapping, and a stratified train/test split with training-only scaling previews. It uses the same shared feature extractor as `train.py` and `app.py`.

For GitHub, initialize a repository, review `.gitignore`, and push the source. Do not add the dataset, model binaries, credentials, or personal paths. Streamlit Community Cloud can deploy from the GitHub repository with `app.py` as entrypoint, but generated model artifacts are ignored; therefore configure a build step that runs `python train.py` before `streamlit run app.py`, or provide generated model files through an approved artifact mechanism. The official dataset fetch requires network access and may make cold-start deployment slow; test within the hosting resource limits. No deployment is claimed by this repository.

## Repository checklist

| Assessment evidence | Files |
|---|---|
| Cleaning, inspection, split | `src/data_loader.py`, `train.py`, `results/data_audit.json` (generated) |
| Four classifiers and analytics | `src/model_training.py`, `src/evaluation.py`, generated `results/` |
| UI and cross-platform browser access | `app.py` |
| Code, report, GitHub, viva | `src/`, `README.md`, `reports/project_report.md`, `viva_questions.md` |

## Model notes

- **Logistic Regression:** learns a linear boundary; interpretable baseline, but may miss complex interactions.
- **KNN:** votes among nearby scaled examples; intuitive, but prediction can be slow and distance depends on scaling.
- **Decision Tree:** learns feature-based rules; easy to explain, but can overfit (depth is limited here).
- **Gaussian Naive Bayes:** combines class probabilities assuming conditional feature independence; fast, though the assumption is simplistic.

Read `reports/project_report.md` and `viva_questions.md` for the academic discussion.
