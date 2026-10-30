"""Verify that a downloaded official-style CSV is consumed by the pipeline."""
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.data_loader import load_dataset, load_source_data
from src.feature_extraction import SOURCE_FEATURE_NAMES, extract_url_features


class LocalCsvLoadingTests(unittest.TestCase):
    def test_local_csv_is_used_and_target_is_remapped(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=root) as temp_dir:
            csv_path = Path(temp_dir) / "official.csv"
            urls = ["https://example.com/login", "http://bad.example.net/a"]
            records = []
            for index, (url, original_label) in enumerate(zip(urls, [0, 1])):
                feature_values = extract_url_features(url, as_frame=False)
                records.append({"FILENAME": f"sample-{index}", "URL": url,
                                **dict(zip(SOURCE_FEATURE_NAMES, feature_values[:len(SOURCE_FEATURE_NAMES)])),
                                "label": original_label})
            pd.DataFrame(records).to_csv(csv_path, index=False)

            X, original_y, source_name = load_source_data(csv_path)
            self.assertEqual(source_name, f"local CSV: {csv_path}")
            self.assertNotIn("FILENAME", X.columns)
            self.assertEqual(list(original_y.iloc[:, 0]), [0, 1])

            extracted, target, audit = load_dataset(csv_path)
            from src.feature_extraction import FEATURE_NAMES
            self.assertEqual(list(extracted.columns), FEATURE_NAMES)
            self.assertEqual(list(target), [1, 0])  # Project convention: 1=phishing.
            self.assertEqual(audit["rows"], 2)
            self.assertEqual(audit["data_source"], source_name)


if __name__ == "__main__":
    unittest.main()
