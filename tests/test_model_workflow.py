"""Small dependency-level smoke test for all training pipelines and model saving."""
import tempfile
import unittest
import importlib.util
from pathlib import Path

import pandas as pd

from src.feature_extraction import FEATURE_NAMES


SKLEARN_AVAILABLE = bool(importlib.util.find_spec("sklearn") and importlib.util.find_spec("joblib"))


@unittest.skipUnless(SKLEARN_AVAILABLE, "Install requirements.txt to run model fit/save/reload integration test")
class ModelWorkflowTests(unittest.TestCase):
    def test_all_four_models_fit_predict_and_reload(self):
        import joblib
        from src.model_training import build_models

        # Balanced, deterministic toy data checks artifact plumbing, not model quality.
        rows = []
        labels = []
        for i in range(80):
            phishing = i % 2
            base = [25 + i, 10 + (i % 6), phishing, 2 + (i % 4), i % 3]
            extra = [(i + j) % 7 for j in range(len(FEATURE_NAMES) - len(base))]
            rows.append(base + extra)
            labels.append(phishing)
        X = pd.DataFrame(rows, columns=FEATURE_NAMES)
        y = pd.Series(labels)
        sample = X.iloc[[0, 1, 2]]
        # Keep temporary artifacts inside the repository so Windows sandboxed
        # environments with restricted system TEMP directories can run the test.
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as temp_dir:
            for name, model in build_models().items():
                with self.subTest(model=name):
                    model.fit(X, y)
                    expected = model.predict(sample)
                    path = Path(temp_dir) / f"{name}.joblib"
                    joblib.dump(model, path)
                    loaded = joblib.load(path)
                    self.assertEqual(list(loaded.predict(sample)), list(expected))
                    self.assertEqual(loaded.predict_proba(sample).shape, (3, 2))


if __name__ == "__main__":
    unittest.main()
