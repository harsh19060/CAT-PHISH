"""Tests for the reachability-before-inference sequence and score meaning."""
import unittest
from unittest.mock import Mock

from src.prediction import analyze_url


class PredictionFlowTests(unittest.TestCase):
    def test_http_404_is_a_response_and_still_reaches_model(self):
        model = Mock()
        model.predict.return_value = [1]
        model.predict_proba.return_value = [[0.97, 0.03]]
        model.classes_ = [0, 1]
        checker = Mock(return_value={"status_code": 404, "reason": "Not Found"})

        result = analyze_url("https://example.com/missing", model, reachability_checker=checker)

        checker.assert_called_once_with("https://example.com/missing")
        model.predict.assert_called_once()
        self.assertEqual(result["status"]["status_code"], 404)
        self.assertEqual(result["prediction"], 1)
        self.assertAlmostEqual(result["phishing_probability"], 0.03)

    def test_connection_failure_stops_before_model_inference(self):
        model = Mock()
        checker = Mock(side_effect=ConnectionError("unreachable"))

        with self.assertRaisesRegex(ConnectionError, "unreachable"):
            analyze_url("https://example.com/login", model, reachability_checker=checker)

        model.predict.assert_not_called()
        model.predict_proba.assert_not_called()

    def test_phishing_probability_is_read_by_class_label_not_column_position(self):
        model = Mock()
        model.predict.return_value = [0]
        model.predict_proba.return_value = [[0.22, 0.78]]
        model.classes_ = [1, 0]

        result = analyze_url(
            "https://example.com/", model,
            reachability_checker=Mock(return_value={"status_code": 200, "reason": "OK"}),
        )

        self.assertEqual(result["prediction"], 0)
        self.assertAlmostEqual(result["phishing_probability"], 0.22)

    def test_exact_known_homepage_gets_transparent_demo_override(self):
        model = Mock()
        model.predict.return_value = [1]
        model.predict_proba.return_value = [[0.01, 0.99]]
        model.classes_ = [0, 1]
        result = analyze_url(
            "https://www.google.com/", model,
            reachability_checker=Mock(return_value={"status_code": 200, "reason": "OK"}),
        )
        self.assertEqual(result["classifier_prediction"], 1)
        self.assertEqual(result["prediction"], 0)
        self.assertEqual(result["demo_homepage"], "www.google.com")

    def test_known_brand_paths_and_lookalike_hosts_are_not_overridden(self):
        model = Mock()
        model.predict.return_value = [1]
        model.predict_proba.return_value = [[0.01, 0.99]]
        model.classes_ = [0, 1]
        checker = Mock(return_value={"status_code": 200, "reason": "OK"})
        for url in ["https://www.google.com/url?q=elsewhere", "https://www.google.com.evil.test/"]:
            with self.subTest(url=url):
                result = analyze_url(url, model, reachability_checker=checker)
                self.assertEqual(result["prediction"], 1)
                self.assertIsNone(result["demo_homepage"])


if __name__ == "__main__":
    unittest.main()
