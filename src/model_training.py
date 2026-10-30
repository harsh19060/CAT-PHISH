"""Training pipelines for the four required scikit-learn classifiers."""
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB


def build_models():
    """Create exactly four model pipelines; learned transforms fit on train only."""
    scaled = lambda estimator: Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("classifier", estimator),
    ])
    unscaled = lambda estimator: Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("classifier", estimator),
    ])
    return {
        "Logistic Regression": scaled(LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)),
        # A KD-tree is efficient for this five-dimensional numeric feature space.
        "K-Nearest Neighbors": scaled(KNeighborsClassifier(n_neighbors=5, algorithm="kd_tree", leaf_size=40, n_jobs=-1)),
        "Decision Tree": unscaled(DecisionTreeClassifier(max_depth=12, class_weight="balanced", random_state=42)),
        "Gaussian Naive Bayes": unscaled(GaussianNB()),
    }
