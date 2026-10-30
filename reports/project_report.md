# Phishing URL Detection Using Machine Learning

## Abstract

This mini-project builds a reproducible URL-string classifier using the UCI PhiUSIIL dataset and four conventional scikit-learn models. The dataset mixes lexical URL fields with webpage-related fields. The app uses 25 explicitly defined URL-only features, all calculated by one shared function. The official data contains 235,795 instances, 54 input features and no missing values; the original labels are 0 phishing and 1 legitimate. This code remaps the positive class to 1 for phishing.

## Introduction, problem and objectives

Phishing uses deceptive messages and destinations to trick people into revealing credentials or other information. The lab problem is binary classification from URL structure. Objectives are to inspect and prepare the official dataset, compare four fixed classifiers with a common test set, and demonstrate predictions in a browser without reading a user-supplied page body.

## Literature review

The studies below provide context, not direct performance targets. Their datasets, feature definitions, time periods and splits differ, so their published scores are not comparable with this experiment. Metadata and findings are summarized from publisher or scholarly records; full text was not available for every item.

| Study | Method and data | Reported finding / relevance | Limitation for this lab |
|---|---|---|---|
| Prasad & Chandra (2024), “PhiUSIIL: A diverse security profile empowered phishing URL detection framework based on similarity index and incremental learning,” *Computers & Security*, DOI [10.1016/j.cose.2023.103545](https://doi.org/10.1016/j.cose.2023.103545) | Introduces the PhiUSIIL UCI dataset; URL and webpage-derived features | Primary source dataset for this project | Mixed feature types mean a raw URL app cannot reproduce the full feature space |
| R. et al. (2022), “Phishing URL Detection: A Real-Case Scenario Through Login URLs,” *IEEE Access* 10, 42949–42960, DOI [10.1109/ACCESS.2022.3168681](https://doi.org/10.1109/ACCESS.2022.3168681) | PILU-90K (60K legitimate, 30K phishing); handcrafted lexical features, character n-gram TF-IDF + Logistic Regression, and CNN | Reports 96.50% accuracy for TF-IDF + LR on its login-URL dataset and highlights temporal drift and legitimate login false positives | Different data and text representation; scores cannot be transferred to PhiUSIIL |
| Hasane Ahammad et al. (2022), “Phishing URL detection using machine learning methods,” *Advances in Engineering Software* 173, 103288, DOI [10.1016/j.advengsoft.2022.103288](https://doi.org/10.1016/j.advengsoft.2022.103288) | Evaluates ML and DL methods on 66,506 malicious URL records | Supports comparative URL feature modeling | Broader malicious URL task and distinct data/setup |
| Rashid et al. (2024), “Phishing URL detection generalisation using Unsupervised Domain Adaptation,” *Computer Networks* 245, 110398, DOI [10.1016/j.comnet.2024.110398](https://doi.org/10.1016/j.comnet.2024.110398) | Studies cross-dataset generalization and unsupervised domain adaptation | Warns that random within-dataset splits can overstate performance on future or shifted data | Domain adaptation is outside this basic fixed-split lab |
| Ghalechyan et al. (2024), “Phishing URL detection with neural networks: an empirical study,” *Scientific Reports* 14, 25134, DOI [10.1038/s41598-024-74725-6](https://doi.org/10.1038/s41598-024-74725-6) | Empirical neural-network study | Shows current work also explores neural approaches | Neural models are outside this syllabus comparison |
| Jishnu & Arthi (2024), “Real-time phishing URL detection framework using knowledge distilled ELECTRA,” *Automatika* 65(4), 1621–1639, DOI [10.1080/00051144.2024.2415797](https://doi.org/10.1080/00051144.2024.2415797) | Distilled ELECTRA and browser extension on 450,176 URLs | Publisher record reports 99.74% accuracy and 99.43% F1 on their data | Deep model and different corpus; not a state-of-the-art claim for this project |

Recent studies include deep learning, contextual URL representations, time-aware evaluation and cross-dataset transfer. This mini-project intentionally compares four classical classifiers for clarity, not as a claim of newest state of the art. A random stratified split measures in-sample-distribution generalization; it does not assess temporal drift.

## Dataset and cleaning

UCI PhiUSIIL is dataset 967, donated in 2024 and licensed CC BY 4.0. The repository reports 134,850 legitimate and 100,945 phishing rows (235,795 total), 54 features and no missing values. `src/data_loader.py` fetches it with `ucimlrepo`. It audits dimensions, names, types, missing values, exact duplicate full rows and original label distribution. It does not delete duplicate URLs or rows. If raw URL-derived values are unusable, extraction raises an error rather than assigning an arbitrary class.

The official labels are 0 = phishing, 1 = legitimate. For every model and metric the project defines target 1 = phishing, 0 = legitimate. The 25 URL-only features are URLLength, DomainLength, IsDomainIP, TLDLength, NoOfSubDomain, IsHTTPS, NoOfLettersInURL, NoOfDigitsInURL, NoOfAtSymbols, HasPercentEncoding, LetterRatioInURL, DigitRatioInURL, NoOfEqualsInURL, NoOfQuestionMarksInURL, NoOfAmpersandsInURL, NoOfDotsInURL, NoOfHyphensInURL, NoOfSlashesInURL, NoOfNonAlphanumericCharsInURL, NonAlphanumericRatioInURL, PathLength, QueryLength, QueryParameterCount, NoOfPercentEncodings, and PercentEncodedRatioInURL. The last 20 fields are calculated with explicit project definitions; several are not exact reproductions of similarly named UCI fields. Webpage metadata and external statistics are excluded because prediction receives only a URL string. Domain length is calculated from parsed hostname; subdomain count is the number of hostname labels before the final two. This is a simple educational approximation and may differ for public suffixes such as co.uk. The run audit compares the five core features to their similarly named UCI columns. In the executed run, mismatches were URLLength 187,151/235,795, DomainLength 36, IsDomainIP 30, TLDLength 625, and NoOfSubDomain 616. Training and prediction use the same extractor, but the base URLLength definition does not numerically reproduce most stored UCI values.

## Methodology and experiment

The shared workflow is `URL → extract 25 lexical features → 80/20 stratified split → four model pipelines → common held-out evaluation → saved artifacts → Streamlit`. Random state is 42. Any learned imputer/scaler fits inside the training pipeline only. Logistic Regression and KNN use standard scaling; Decision Tree and Gaussian Naive Bayes use imputation without scaling. The required models are Logistic Regression, KNN (5 neighbors), depth-limited Decision Tree (max depth 12), and Gaussian Naive Bayes.

Accuracy is the share of all correct classifications. Phishing precision is TP/(TP+FP), recall is TP/(TP+FN), and F1 is the harmonic mean of phishing precision and recall. ROC-AUC summarizes the ranking across thresholds. The confusion matrix uses rows for true labels and columns for predictions with order legitimate, phishing. Phishing recall matters because false negatives are missed attacks; increasing recall may also increase false alarms (lower precision). The selection rule favors phishing recall, then F1, but application users may inspect all four models.

## Results and discussion

The completed run created `results/model_comparison.csv`, `metric_comparison.png`, `confusion_matrices.png`, `roc_curves.png`, and `data_audit.json`. All four models use the same stratified 80/20 split. Results are actual measured scores on that held-out set; the mismatch caveat above limits comparison with stored UCI features.

| Model | Accuracy | Phishing precision | Phishing recall | Phishing F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Logistic Regression | 99.33% | 99.91% | 98.52% | 99.21% | 99.58% |
| K-Nearest Neighbors | 99.53% | 99.80% | 99.11% | 99.45% | 99.66% |
| Decision Tree | 99.57% | 99.86% | 99.13% | 99.49% | 99.74% |
| Gaussian Naive Bayes | 99.18% | 99.58% | 98.49% | 99.03% | 99.69% |

The Decision Tree had the highest accuracy, phishing precision, phishing recall, F1, and ROC-AUC by small margins on this split. KNN was close behind. These scores are not evidence of performance on new campaigns; URLs from related sources may occur in both partitions, and the feature definition mismatch should be investigated before presenting this as a fully validated benchmark.

Compared with the preceding 10-feature version on the same split, the 25-feature version raised accuracy/recall from 97.46% / 94.90% to 99.33% / 98.52% for Logistic Regression, 99.29% / 98.89% to 99.53% / 99.11% for KNN, 98.94% / 97.95% to 99.57% / 99.13% for Decision Tree, and 91.25% / 80.55% to 99.18% / 98.49% for Gaussian Naive Bayes. These are within-dataset random-split results; the URL strings are not independent observations in time or source, so this increase should be treated as a promising classroom comparison rather than proof of real-world accuracy.

![Model metric comparison](../results/metric_comparison.png)

![Confusion matrices](../results/confusion_matrices.png)

![ROC curves](../results/roc_curves.png)

## UI and deployment

`app.py` is a responsive Streamlit browser interface. It loads saved models, does not retrain on each request, and calls the same feature function as training. Before inference it performs one bounded HTTP request to a public host, with a short timeout, no redirects, and no page-body read. DNS, timeout, or connection failures stop inference. Any HTTP response, including 404, is shown separately and allows classification; 404 means the host answered but the requested path was not found. The model receives 25 numeric URL-string features, never the status code or page. Since the URL-only vectors for Google and Amazon homepages were identical and all classifiers returned false positives, a narrow exact-homepage demo rule displays these four hostnames as legitimate after an HTTP 2xx response: `google.com`, `www.google.com`, `amazon.com`, and `www.amazon.com`. The app shows the raw classifier prediction and score separately. The rule does not cover paths, queries, redirects, subdomains, or site safety generally. Model scores are uncalibrated and can reach 100%; they are not certainty estimates. Avoid URLs containing private tokens or credentials. Create a venv, install `requirements.txt`, run `python train.py`, then `streamlit run app.py`. For a public deployment, review the server-side URL check and deployment network restrictions; no deployment is claimed here.

## Limitations, future work and conclusion

Even 25 lexical features cannot represent page content, domain age, DNS/WHOIS reputation, certificates, redirects or threat feeds. The exact-homepage demo rule is a manually configured exception, not evidence from the classifier. The improved scores are measured on one random split from this dataset and do not establish future or cross-dataset performance; URL sources may share patterns across train and test. Model scores are not proof of safety. Future work could test a time-based or cross-dataset split, calibrate scores, add carefully validated reputation/page signals, and measure error costs while preserving privacy. The project demonstrates the full classical ML workflow with a constrained, explainable URL-only UI and four specified models.

## References

1. Prasad, A. & Chandra, S. (2024). PhiUSIIL Phishing URL (Website) [Dataset]. UCI Machine Learning Repository. https://doi.org/10.1016/j.cose.2023.103545.
2. “Phishing URL Detection: A Real-Case Scenario Through Login URLs.” IEEE Access (2022). https://doi.org/10.1109/ACCESS.2022.3168681.
3. Hasane Ahammad, S. K. et al. (2022). Phishing URL detection using machine learning methods. Advances in Engineering Software, 173, 103288. https://doi.org/10.1016/j.advengsoft.2022.103288.
4. Rashid, F. et al. (2024). Phishing URL detection generalisation using Unsupervised Domain Adaptation. Computer Networks, 245, 110398. https://doi.org/10.1016/j.comnet.2024.110398.
5. Ghalechyan, H. et al. (2024). Phishing URL detection with neural networks: an empirical study. Scientific Reports, 14, 25134. https://doi.org/10.1038/s41598-024-74725-6.
6. Jishnu, K. S. & Arthi, B. (2024). Real-time phishing URL detection framework using knowledge distilled ELECTRA. Automatika, 65(4), 1621–1639. https://doi.org/10.1080/00051144.2024.2415797.
