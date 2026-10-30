from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports'/'Phishing_URL_Detection_Project_Report.docx'
d=Document(); s=d.sections[0]
s.page_width=Inches(8.27); s.page_height=Inches(11.69)
s.top_margin=Inches(.62); s.bottom_margin=Inches(.58); s.left_margin=Inches(.68); s.right_margin=Inches(.68)
s.header_distance=Inches(.25); s.footer_distance=Inches(.25)
styles=d.styles
styles['Normal'].font.name='Aptos'; styles['Normal'].font.size=Pt(9.1); styles['Normal'].font.color.rgb=RGBColor(35,43,54)
styles['Normal'].paragraph_format.space_after=Pt(4); styles['Normal'].paragraph_format.line_spacing=1.04
for n,z in [('Title',25),('Heading 1',16),('Heading 2',11.5),('Heading 3',9.5)]:
 st=styles[n]; st.font.name='Aptos Display'; st.font.size=Pt(z); st.font.bold=True; st.font.color.rgb=RGBColor(0,0,0); st.paragraph_format.keep_with_next=True; st.paragraph_format.space_before=Pt(5); st.paragraph_format.space_after=Pt(4)
styles['Title'].paragraph_format.space_before=Pt(0)
try: ts=styles['Compact Table']
except KeyError: ts=styles.add_style('Compact Table',1)
ts.font.name='Aptos'; ts.font.size=Pt(7.6); ts.font.color.rgb=RGBColor(35,43,54); ts.paragraph_format.space_after=Pt(0); ts.paragraph_format.line_spacing=1.0
hp=s.header.paragraphs[0]; hp.text='PHISHING URL DETECTION  |  MACHINE LEARNING MINI-PROJECT'; hp.alignment=WD_ALIGN_PARAGRAPH.RIGHT
for r in hp.runs: r.font.size=Pt(7); r.font.color.rgb=RGBColor(90,101,114)
fp=s.footer.paragraphs[0]; fp.alignment=WD_ALIGN_PARAGRAPH.CENTER; rr=fp.add_run('Project report  •  '); rr.font.size=Pt(8); rr.font.color.rgb=RGBColor(90,101,114)
fld=OxmlElement('w:fldSimple'); fld.set(qn('w:instr'),'PAGE'); fp._p.append(fld)

def shade(c,color):
 sh=OxmlElement('w:shd'); sh.set(qn('w:fill'),color); c._tc.get_or_add_tcPr().append(sh)
def tbl(head,rows,widths=None,size=7.6):
 t=d.add_table(rows=1,cols=len(head)); t.alignment=WD_TABLE_ALIGNMENT.CENTER; t.autofit=False
 for j,x in enumerate(head):
  c=t.rows[0].cells[j]; c.text=''; p=c.paragraphs[0]; p.style='Compact Table'; r=p.add_run(str(x)); r.bold=True; r.font.size=Pt(size); r.font.color.rgb=RGBColor(255,255,255); shade(c,'16324F'); c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
 tr=t.rows[0]._tr.get_or_add_trPr(); rep=OxmlElement('w:tblHeader'); rep.set(qn('w:val'),'true'); tr.append(rep)
 for row in rows:
  cells=t.add_row().cells
  for j,x in enumerate(row):
   c=cells[j]; c.text=''; p=c.paragraphs[0]; p.style='Compact Table'; p.paragraph_format.keep_together=True; r=p.add_run(str(x)); r.font.size=Pt(size); c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
 if widths:
  for row in t.rows:
   for j,w in enumerate(widths): row.cells[j].width=Inches(w)
 d.add_paragraph().paragraph_format.space_after=Pt(0); return t
def p(text='',size=None,italic=False,align=None):
 q=d.add_paragraph(); q.paragraph_format.keep_together=True
 if align is not None:q.alignment=align
 r=q.add_run(text); r.italic=italic
 if size:r.font.size=Pt(size)
 return q
def h(text,level=1): d.add_heading(text,level)
def bullet(text):
 q=d.add_paragraph(style='List Bullet'); q.paragraph_format.left_indent=Inches(.2); q.paragraph_format.first_line_indent=Inches(-.12); q.paragraph_format.space_after=Pt(2); q.add_run(text)
def page(): d.add_page_break()
def fig(path,width):
 q=d.add_paragraph(); q.alignment=WD_ALIGN_PARAGRAPH.CENTER; q.paragraph_format.space_after=Pt(1); q.add_run().add_picture(str(path),width=Inches(width))
def cap(text):
 q=d.add_paragraph(); q.alignment=WD_ALIGN_PARAGRAPH.CENTER; q.paragraph_format.space_after=Pt(3); r=q.add_run(text); r.italic=True; r.font.size=Pt(8); r.font.color.rgb=RGBColor(80,90,102)

# 1 Cover and abstract
q=d.add_paragraph(); q.paragraph_format.space_before=Pt(28); q.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=q.add_run('PHISHING URL DETECTION'); r.bold=True; r.font.name='Aptos Display'; r.font.size=Pt(25)
p('A Comparative Machine Learning Mini-Project',14,align=WD_ALIGN_PARAGRAPH.CENTER)
p('Formal project report for demonstration and viva assessment',10,align=WD_ALIGN_PARAGRAPH.CENTER)
p('Dataset: UCI PhiUSIIL (Dataset 967)  |  Models: Logistic Regression, K-Nearest Neighbors, Decision Tree, Gaussian Naive Bayes',8,align=WD_ALIGN_PARAGRAPH.CENTER)
h('Abstract',1)
p('This project implements a URL-string phishing classifier and browser-based teaching interface. It uses a local PhiUSIIL CSV with 235,795 records and 54 original columns, derives 25 numeric URL features from each raw URL, and compares four scikit-learn classifiers using one stratified 80/20 split (random state 42). The Decision Tree achieved the highest measured phishing recall (99.13%) and F1 score (99.51%) on that holdout; K-Nearest Neighbors was close. The application checks public-host reachability before inference and reports HTTP status separately from the model input. It does not fetch page content or pass status to the classifier. These scores describe a random split from one dataset, not proven future or cross-source performance. The audit also found that URL-derived values differ from same-named stored PhiUSIIL values for many rows, so this is a project-defined URL-only experiment rather than a direct replication of the original feature benchmark.')
h('Project snapshot',2)
tbl(['Item','Implemented project'],[
('Problem','Binary URL-only classification: phishing=1, legitimate=0.'),('Training data','Local PhiUSIIL CSV; 235,795 rows; 54 columns; no missing values and no exact duplicate full rows.'),('Model input','Fixed ordered vector of 25 numeric properties computed from URL text; no webpage content, DNS reputation, or WHOIS fields.'),('Evaluation','Stratified 80/20 holdout, random_state=42; accuracy, phishing precision/recall/F1, ROC-AUC and confusion matrices.'),('Best measured model','Decision Tree by a small margin: 99.58% accuracy, 99.13% phishing recall, 99.51% phishing F1 and 99.74% ROC-AUC.')],[1.35,5.55],7.5)
p('Interpretation: a reproducible educational comparison of four classical models, not an operational anti-phishing service or a claim of state-of-the-art performance.',8,italic=True)

# 2 Introduction
page(); h('1. Introduction',1); h('1.1 Background and problem statement',2)
p('Phishing URLs direct users to deceptive destinations designed to imitate trusted services or collect credentials and payment information. A URL contains visible structural signals, including host labels, path and query text, character composition, encoding and protocol. These signals can be measured without downloading a page. They provide a lightweight first-pass representation, but do not reveal page content, ownership, reputation or intent.')
p('The task is to estimate from the literal URL string whether it resembles phishing or legitimate examples in the training corpus. The constraint keeps feature extraction fast and avoids fetching the page for model inference. A separate bounded network request reports whether the public host responds; reachability is not a learned feature.')
h('1.2 Aim and objectives',2)
for x in ['Inspect and document the PhiUSIIL data, including dimensions, types, missingness, duplicate rows and labels.','Construct a transparent 25-feature URL-only representation used consistently at training and inference.','Train and compare four standard classifiers on a common stratified test partition.','Present metrics and diagnostics in a Streamlit interface, with EDA visuals for classroom explanation.','Explain performance limits, URL reachability and the distinction between a raw classifier result and an explicit demonstration rule.']: bullet(x)
h('1.3 Scope and contribution',2)
p('The contribution is an inspectable teaching workflow: local CSV loading, data audit, feature derivation, preprocessing pipelines, model comparison, saved artifacts and browser UI. The code does not implement URL character embeddings, transformers, XGBoost, web-page inspection, blacklist lookup or temporal testing. Those methods are literature context, not features of this project.')
h('1.4 Research questions',2)
p('RQ1: How do the four models compare on the held-out PhiUSIIL subset after URL-only feature extraction? RQ2: Why are the feature groups relevant to URL structure and what do they omit? RQ3: How does the interface distinguish reachability from phishing classification?')
h('1.5 Report organization',2)
p('Section 2 compares recent studies. Sections 3–5 describe methodology, preparation and feature rationale. Section 6 reports model metrics. Section 7 documents UI behavior and deployment. Section 8 discusses limitations and conclusions.')

# 3 literature comparison
page(); h('2. Literature Review',1)
p('Recent work explores engineered lexical signals, HTML and derived features, neural URL representations, transformer embeddings and domain adaptation. These studies are compared by method, evidence and relevance. Their scores are context only: dataset, labeling policy, feature pipeline, date and split differ, so the values cannot be directly ranked against this project.')
tbl(['Study and approach','Contribution reported','Comparison with this project'],[
('Kustiawan & Ghauth (2025), IEEE Access [1]','Compares URL, HTML and derived feature sets across ML models, focusing on feature modality.','Supports explicit URL-only scope; page-informed and URL-only tasks are distinct. Current project does not reproduce this study.'),
('Linh & Hung (2025), Data in Brief [2]','Provides 111,660 benign/phishing URLs with 22 engineered lexical and structural features, including lengths, ratios, entropy and HTTPS.','Shows continued use of transparent numeric URL features. The project’s 25 definitions are its own schema.'),
('Rao et al. (2025), Scientific Reports [3]','Phish-Jam combines handcrafted URL properties, LSTM and transformer representations in a mobile super learner; reports 98.93% accuracy and 99.07% F1 on its study data.','Shows advanced fusion and mobile deployment. The project instead compares four classical baselines; scores are not directly comparable.'),
('Sruthi & Naik (2025), Knowledge-Based Systems [4]','Uses a Siamese network with shared LSTM subnetworks to learn URL-sequence similarity; includes AI-generated phishing in evaluation.','Motivates testing novel patterns. Current project has no sequence encoder or generated/adversarial test set.'),
('Rashid et al. (2024), Computer Networks [5]','Tests URL classifiers across three datasets and uses unsupervised domain adaptation; reports average cross-dataset F1 improvement of 0.06.','Motivates caution about random-split metrics. Cross-source and temporal generalization remain untested here.')],[1.47,2.75,2.68],7.15)
h('2.1 Synthesis and research gap',2)
p('URL-only handcrafted features are lightweight and explainable but discard semantic context and site behavior. Neural encoders learn character/token patterns at greater computational cost. HTML-informed methods can use page signals but require retrieval and raise operational risks. Domain adaptation research shows that strong within-dataset performance may not transfer to a new feed or period.')
p('This work addresses a classroom objective, not a research novelty gap: compare four classical models on one shared feature pipeline and expose results interactively. It should not be called state of the art. No common public holdout was used to compare this project with the studies above.')

# 4 methodology
page(); h('3. Methodology',1); h('3.1 End-to-end pipeline',2)
tbl(['Stage','Implementation and output'],[
('1. Load and audit','Read local PhiUSIIL CSV; verify schema, dimensions, types, missingness, exact duplicates, labels and source-feature mismatches.'),('2. Prepare','Derive 25 values from raw URL; map source 0 (phishing) to project target 1 and source 1 (legitimate) to target 0.'),('3. Split','train_test_split with test_size=.20, random_state=42 and stratify=y; common test rows for each model.'),('4. Fit','Fit imputation/scaling within scikit-learn pipelines on training partition only; train and save four model artifacts.'),('5. Evaluate','Compute accuracy, phishing precision/recall/F1 and ROC-AUC; save comparison CSV, ROC and confusion-matrix figures.'),('6. Infer','Check public-host reachability with a bounded request; if an HTTP response is returned, extract URL features and invoke selected model.')],[1.3,5.6],7.6)
h('3.2 Model comparison',2)
tbl(['Classifier','Decision principle','Purpose and assumption'],[
('Logistic Regression','Fits a linear weighted boundary to numeric features.','Linear baseline; scaling supports optimization.'),('K-Nearest Neighbors (k=5)','Majority vote among five nearest training vectors.','Local similarity baseline; Euclidean distance requires scaling; score steps of 20 points.'),('Decision Tree (depth 12)','Recursively partitions feature ranges into decision regions.','Models nonlinear thresholds and interactions; depth constraint limits complexity.'),('Gaussian Naive Bayes','Combines class-conditional Gaussian likelihoods under conditional independence.','Fast probabilistic baseline; independence and distribution assumptions may be imperfect.')],[1.5,2.7,2.7],7.5)
h('3.3 Performance measures',2)
p('Phishing is positive. Accuracy=(TP+TN)/(TP+TN+FP+FN); precision=TP/(TP+FP); recall=TP/(TP+FN); F1=2·precision·recall/(precision+recall). ROC-AUC summarizes ranking across thresholds. A false negative is missed phishing; a false positive is a false alarm. Recall is important for attack coverage, while precision captures alert quality. These are point estimates on one holdout; no confidence intervals or repeated-seed results were computed.')

# 5 Data preparation
page(); h('4. Data Cleaning and Preprocessing',1); h('4.1 Dataset profile',2)
p('The local file data/PhiUSIIL_Phishing_URL_Dataset.csv corresponds to UCI dataset 967. The audit reports 235,795 records and 54 original columns, containing raw URLs, lexical values, page observations and other context. Source labels are 0=phishing (100,945 records) and 1=legitimate (134,850 records), approximately 42.8% and 57.2%.')
tbl(['Audit check','Observed result','Treatment / meaning'],[
('Missing values','0','No source-data imputation needed.'),('Exact duplicate full rows','0','No full-row duplicate removal performed.'),('Source labels','0 phishing: 100,945; 1 legitimate: 134,850','Mapped to project convention 1=phishing, 0=legitimate.'),('Input columns','54','Only URL string is used for inference; page-derived and external fields are excluded.'),('Invalid URL-only rows','0 dropped in recorded run','Extraction errors instead of assigning arbitrary values or labels.')],[1.45,2.0,3.45],7.55)
h('4.2 Why not use all 54 columns?',2)
p('The table includes HTML line counts, page title, forms, scripts, redirects and external references. Such fields cannot be calculated from the string alone without retrieving the page or consulting a service. Training with them while the UI has only a URL would create a training–inference mismatch. The project derives a constrained subset from the raw URL and uses the same extractor in both phases.')
h('4.3 Cleaning, target coding and leakage control',2)
p('Preparation is audit-led: verify schema and types; measure nulls and exact duplicate rows; parse URL; derive numeric features; and remap labels. The recorded audit found no missing values, exact duplicates or unusable URL rows, so it did not drop records for these reasons. Stratification preserves approximate class proportions. Learned transforms fit only on training data through model pipelines, avoiding use of test statistics during fitting.')
h('4.4 Source-feature alignment caveat',2)
p('Five features have names associated with PhiUSIIL columns, but this project recomputes them from the URL. The audit reports mismatches: URLLength 187,151 rows; DomainLength 36; IsDomainIP 30; TLDLength 625; NoOfSubDomain 616. In particular, project URLLength does not reproduce the stored value for most rows. Training and inference remain internally consistent with the project extractor, but this is not an exact reimplementation of the source fields. The subdomain rule is a last-two-label approximation and may not follow public suffix boundaries such as co.uk.')

# 6 features first set
page(); h('5. Feature Engineering and Rationale',1)
p('Selection prioritized deployability and interpretable URL structure, not a formal statistical feature-selection algorithm. Every feature can be calculated from a URL string without page HTML or external reputation. The set spans host structure, protocol, character composition, encoding, separators, path and query. It is a practical teaching subset, not evidence that these 25 are uniquely optimal or superior to all source columns.')
tbl(['Feature','Project definition','Reason and caveat'],[
('1 URLLength','Character count of normalized URL string.','Long strings provide space for deceptive paths and parameters; convention-sensitive.'),('2 DomainLength','Length of parsed hostname, excluding trailing dot.','Long hostnames may be suspicious; legitimate naming varies.'),('3 IsDomainIP','1 if hostname parses as IP; else 0.','Numeric host can conceal identity; IP hosting is not inherently malicious.'),('4 TLDLength','Length of final hostname label.','Simple structural signal, not TLD reputation.'),('5 NoOfSubDomain','Labels before final two hostname labels.','Nested labels may obscure apparent identity; suffix boundary approximated.'),('6 IsHTTPS','1 for HTTPS scheme; else 0.','Protocol context only; HTTPS is not evidence of trust.'),('7 NoOfLettersInURL','Alphabetic-character count.','Captures URL text volume.'),('8 NoOfDigitsInURL','Numeric-character count.','Numbers can appear in random names and legitimate URLs.'),('9 NoOfAtSymbols','Count of @ characters.','Can contribute to authority confusion or obfuscation.'),('10 HasPercentEncoding','1 if one or more valid %HH sequences occur.','Captures transformation of visible URL characters.'),('11 LetterRatioInURL','Letters divided by URL length.','Normalizes text density by total length.'),('12 DigitRatioInURL','Digits divided by URL length.','Normalizes numeric density.'),('13 NoOfEqualsInURL','Count of = characters.','Measures key/value syntax; common in legitimate queries too.')],[1.52,2.25,3.13],7.15)
p('These fields are “better” for this app only in the operational sense that they are calculable consistently from a URL. Predictive superiority requires an independent representative test. EDA correlation measures association, not causation or feature-selection proof.',8,italic=True)
fig(ROOT/'reports'/'feature_target_correlation.png',5.2)
cap('Figure 1. Pearson correlation matrix for the 25 extracted features and target (1 = phishing), computed on the full cleaned dataset. IsHTTPS has the largest absolute target correlation (r = +0.613); this is association, not causal importance.')

# 7 features remainder
page(); h('5. Feature Engineering and Rationale (continued)',1)
tbl(['Feature','Project definition','Reason and caveat'],[
('14 NoOfQuestionMarksInURL','Count of ? characters.','Marks query boundary; repetitions may indicate unusual formatting.'),('15 NoOfAmpersandsInURL','Count of & characters.','Approximates query separator frequency.'),('16 NoOfDotsInURL','Count periods across URL.','Captures hostname/path segmentation.'),('17 NoOfHyphensInURL','Count hyphens.','Can split deceptive or unusually long labels.'),('18 NoOfSlashesInURL','Count forward slashes.','Reflects path depth and URL structure.'),('19 NoOfNonAlphanumericCharsInURL','Count outside ASCII letters and digits.','Measures punctuation/delimiter density.'),('20 NonAlphanumericRatioInURL','Non-alphanumeric count divided by URL length.','Normalizes symbol density.'),('21 PathLength','Length of parsed path component.','Long paths may contain nested directories or lures.'),('22 QueryLength','Length of parsed query component.','Long queries can carry tracking or deceptive text.'),('23 QueryParameterCount','0 without query; otherwise ampersand count+1.','Simple estimate; encoded separators are not decoded.'),('24 NoOfPercentEncodings','Count valid %HH escapes.','Measures encoding intensity, beyond presence.'),('25 PercentEncodedRatioInURL','Escape count divided by URL length.','Normalizes encoded-token density.')],[1.7,2.2,3.0],7.15)
h('5.1 Rationale for the complete feature set',2)
p('Host features characterize apparent domain construction; protocol and IP flags capture basic authority properties; character counts and ratios describe lexical composition; punctuation and percent encoding capture obfuscation or segmentation; path/query values distinguish a homepage from a deeply parameterized address. Raw counts retain scale while ratios partly normalize for URL length. One deterministic extractor and fixed feature order serve training and inference.')
h('5.2 What URL features cannot establish',2)
p('The vector cannot establish domain ownership, brand impersonation, page credential collection, DNS resolution, domain age or threat-feed reputation. Distinct URLs can have identical vectors. During development, Google and Amazon homepage URLs produced identical feature vectors and all raw classifiers marked them phishing. This is a concrete information-loss example. The app’s narrow exact-homepage demonstration rule and its limitations are documented in Section 7; its output is not a model finding.')

# 8 results chart
page(); h('6. Results and Performance Analytics',1); h('6.1 Held-out performance',2)
p('The recorded run uses a stratified 80/20 split (random_state=42); the same held-out rows were used for all models. Phishing is the positive class. Scores below are rounded from results/model_comparison.csv.')
tbl(['Model','Accuracy','Phish precision','Phish recall','Phish F1','ROC-AUC'],[
('Logistic Regression','99.33%','99.91%','98.52%','99.21%','99.58%'),('K-Nearest Neighbors','99.53%','99.80%','99.11%','99.45%','99.66%'),('Decision Tree','99.58%','99.88%','99.13%','99.51%','99.74%'),('Gaussian Naive Bayes','99.18%','99.58%','98.49%','99.03%','99.69%')],[1.42,.9,1.15,1.0,.85,.85],7.2)
h('6.2 Discussion of model comparison',2)
p('Decision Tree ranks first on each listed metric by a small margin in this split: accuracy 99.58%, phishing precision 99.88%, recall 99.13%, F1 99.51%, and ROC-AUC 99.74%. KNN is close, with 99.53% accuracy and 99.11% recall. Logistic Regression and Gaussian Naive Bayes have slightly lower recall. The gaps are not established as statistically significant; no confidence intervals or repeated-seed analysis was conducted.')
p('A recall of 99.13% means approximately 0.87% of positive phishing records in this test partition were missed at the evaluated threshold. Precision describes the correctness of flagged phishing records on this partition. Neither rate estimates internet-wide performance; both depend on corpus, label quality, sampling and threshold.')
fig(ROOT/'results'/'metric_comparison.png',6.45); cap('Figure 2. Metric comparison on the common held-out test partition.')
h('6.3 Context versus recent research',2)
p('Recent studies use richer signals, sequence encoders, transformers and ensembles, often on different corpora and splits. The literature scores are not a common leaderboard. This project compares only its four implemented models; the literature review explains methodological differences rather than presenting incomparable published metrics as direct competitors.')

# 9 diagnostics and UI
page(); h('6. Results and UI Deployment',1); h('6.4 Error and threshold diagnostics',2)
im=d.add_table(rows=1,cols=2); im.alignment=WD_TABLE_ALIGNMENT.CENTER; im.autofit=False
for c,path in zip(im.rows[0].cells,[ROOT/'results'/'confusion_matrices.png',ROOT/'results'/'roc_curves.png']):
 c.width=Inches(3.28); c.paragraphs[0].alignment=WD_ALIGN_PARAGRAPH.CENTER; c.paragraphs[0].add_run().add_picture(str(path),width=Inches(3.2))
cap('Figure 3. Confusion matrices (left) and ROC curves (right), generated from the same test set.')
p('Confusion matrices show counts of correct classifications, false alarms and missed phishing at each default threshold. ROC curves summarize the trade-off between true-positive and false-positive rates as threshold varies. ROC-AUC describes ranking, but neither selects an operational threshold nor establishes cost-sensitive performance.')
h('7. User Interface Development and Deployment',1); h('7.1 Interface and cross-platform access',2)
p('app.py is a Streamlit browser interface with URL-check, model-comparison and model-method views. eda_app.py supports dataset inspection, feature explanations and correlation visualization. Users open the local app in a standard browser. Windows, macOS, Linux and mobile browsers can access the same web interface where network and firewall settings allow. This is cross-platform browser accessibility, not a native mobile package or a public cloud deployment.')
h('7.2 URL validation and classifier handoff',2)
p('The checker validates syntax, blocks private/local IP targets, and sends one bounded streamed request with redirects disabled and no page-body read. An HTTP response means a server responded, not that the link is safe or that the requested page exists: HTTP 404 means the host answered but that path was not found. DNS, timeout or connection failure stops inference. When an HTTP response arrives, the model receives only the 25 URL-derived values; status code is shown separately and is not a feature.')
p('A manual teaching exception covers only exact google.com, www.google.com, amazon.com and www.amazon.com homepage URLs with HTTP 2xx. Their URL-only vectors were identical and raw models returned phishing. The app displays a legitimate result for these specific examples while showing the raw prediction and score. It does not cover paths, queries, subdomains or lookalikes and does not prove safety. In a viva, describe this as an explicit interface rule, not an ML result.')
h('7.3 Code quality and verification',2)
p('The repository separates data loading, feature extraction, training, evaluation, reachability checks and prediction under src/. Saved artifacts include trained models, metadata, score CSV, audit JSON and figures. The 16 passing unit tests cover feature order and parsing, model fit/predict/reload, local CSV target remapping, HTTP status behavior, redirects, private-IP blocking, class-probability mapping and the homepage exception. Compilation succeeded and saved model checks confirmed 25 inputs for all four estimators.')

# 10 conclusion and refs
page(); h('8. Discussion, Limitations and Conclusion',1); h('8.1 Limitations and validity',2)
for x in ['Random splitting can place related URL patterns or sources in both partitions; it does not test future campaigns or cross-dataset transfer.','Project URL-derived features differ from same-named source fields, especially URLLength. High scores are specific to the project extractor and split; alignment and independent evaluation are needed before stronger claims.','Numeric URL features discard host identity and semantics. Google/Amazon false positives show a feature collision. The exact-homepage exception is a transparent UI rule, not classifier performance.','Reachability is not trustworthiness. DNS failure can be temporary; HTTP 404 still indicates a responding host. The bounded check contacts the submitted public URL but reads no page body.','No external benchmark, temporal split, repeated-seed uncertainty analysis, probability calibration, adversarial evaluation or public deployment is claimed.']: bullet(x)
h('8.2 Conclusion and next steps',2)
p('The project demonstrates a complete classical workflow from dataset auditing and URL feature engineering through four-model evaluation and an accessible browser interface. Decision Tree is the leading baseline by small margins on the recorded stratified holdout; KNN is nearly equivalent. These observations justify a within-project comparison, not universal accuracy claims. The next priority is a leakage-aware temporal or cross-source test with explicitly aligned feature definitions. Further work should add repeated splits or confidence intervals, calibrate probabilities, select a threshold based on missed-attack and false-alarm costs, and assess carefully validated features beyond URL shape.')
h('Assessment coverage',2)
tbl(['Assessment area','Evidence in this report and project','Submission note'],[
('Data cleaning and splitting (3 marks)','CSV quality audit, label remapping, fixed URL feature generation, stratified holdout and documented mismatch checks.','Metrics use the same reproducible test split.'),
('Model comparison and analytics (4 marks)','Four classifiers; shared metrics table; metric comparison, ROC and confusion-matrix figures.','Classical baselines are not presented as state of the art.'),
('UI and cross-platform access (4 marks)','Streamlit URL checker, comparison screen and EDA page accessible through a browser.','Local browser deployment is implemented; no public hosting is claimed.'),
('Code, GitHub, report and submission (4 marks)','Modular source, requirements, tests, generated model/results artifacts and this report.','The workspace is not currently a Git repository and has no GitHub remote; create/push the submission repository before claiming that component.')],[1.45,3.35,2.05],7.15)
h('References',1)
refs=[
'[1] Y. A. Kustiawan and K. I. Ghauth, “Evaluating the Impact of Feature Engineering in Phishing URL Detection: A Comparative Study of URL, HTML, and Derived Features,” IEEE Access, vol. 13, pp. 126756–126768, 2025. doi:10.1109/ACCESS.2025.3579223.',
'[2] D. M. Linh and T. C. Hung, “A Feature-Engineered Dataset of Benign and Phishing URLs for Machine Learning and Large Language Models Evaluation,” Data in Brief, vol. 63, art. 112162, 2025. doi:10.1016/j.dib.2025.112162.',
'[3] R. S. Rao, C. Kondaiah, A. R. Pais, and B. Lee, “A hybrid super learner ensemble for phishing detection on mobile devices,” Scientific Reports, vol. 15, art. 16839, 2025. doi:10.1038/s41598-025-02009-8.',
'[4] K. Sruthi and S. Manohar Naik, “A novel framework for effective phishing URL detection using an LSTM-based siamese network,” Knowledge-Based Systems, vol. 329, art. 114271, 2025. doi:10.1016/j.knosys.2025.114271.',
'[5] F. Rashid, B. Doyle, S. C. Han, and S. Seneviratne, “Phishing URL detection generalisation using Unsupervised Domain Adaptation,” Computer Networks, vol. 245, art. 110398, 2024. doi:10.1016/j.comnet.2024.110398.',
'[6] A. Prasad and S. Chandra, “PhiUSIIL Phishing URL (Website) Dataset,” UCI Machine Learning Repository, dataset 967, 2024. doi:10.1016/j.cose.2023.103545.',
'[7] Project evidence: app.py, eda_app.py, train.py, src/, results/model_comparison.csv, results/data_audit.json and models/model_metadata.json.'
]
for x in refs:
 q=d.add_paragraph(); q.paragraph_format.left_indent=Inches(.18); q.paragraph_format.first_line_indent=Inches(-.18); q.paragraph_format.space_after=Pt(2); q.paragraph_format.line_spacing=1.0; r=q.add_run(x); r.font.name='Aptos'; r.font.size=Pt(7.2)
d.core_properties.title='Phishing URL Detection A Comparative Machine Learning Mini Project'; d.core_properties.subject='Project report for viva and assessment'; d.core_properties.author=''
d.save(OUT); print(OUT)
