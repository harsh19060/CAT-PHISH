import unittest

from src.feature_extraction import FEATURE_NAMES, extract_url_features


class FeatureExtractionTests(unittest.TestCase):
  def test_features_have_fixed_names_and_order(self):
    frame = extract_url_features("https://login.shop.example.com/path?a=1")
    self.assertEqual(list(frame.columns), FEATURE_NAMES)
    self.assertEqual(frame.iloc[0]["IsDomainIP"], 0)
    self.assertEqual(frame.iloc[0]["NoOfSubDomain"], 2)
    self.assertEqual(frame.iloc[0]["IsHTTPS"], 1)
    self.assertEqual(frame.iloc[0]["NoOfDigitsInURL"], 1)
    self.assertEqual(frame.iloc[0]["NoOfAtSymbols"], 0)
    self.assertEqual(frame.iloc[0]["HasPercentEncoding"], 0)
    self.assertEqual(frame.iloc[0]["NoOfQuestionMarksInURL"], 1)
    self.assertEqual(frame.iloc[0]["NoOfEqualsInURL"], 1)
    self.assertEqual(frame.iloc[0]["QueryParameterCount"], 1)

  def test_bare_hostname_defaults_to_https_for_model_features(self):
    bare = extract_url_features("example.com/login").iloc[0]
    explicit = extract_url_features("https://example.com/login").iloc[0]
    self.assertEqual(bare["IsHTTPS"], 1)
    self.assertEqual(bare["URLLength"], explicit["URLLength"])
    self.assertEqual(bare["NoOfLettersInURL"], explicit["NoOfLettersInURL"])

  def test_url_character_features_are_counted(self):
    row = extract_url_features("https://a.example.com/a%2Fb?x=12&y=@").iloc[0]
    self.assertEqual(row["NoOfDigitsInURL"], 3)
    self.assertEqual(row["NoOfAtSymbols"], 1)
    self.assertEqual(row["HasPercentEncoding"], 1)
    self.assertEqual(row["NoOfPercentEncodings"], 1)
    self.assertEqual(row["QueryLength"], len("x=12&y=@"))

  def test_compact_and_dataframe_outputs_match(self):
    url = "https://shop.example.com/path"
    self.assertEqual(extract_url_features(url, as_frame=False),
                     extract_url_features(url).iloc[0].tolist())

  def test_ip_host_is_detected_without_fake_subdomains(self):
    row = extract_url_features("http://192.0.2.1/login").iloc[0]
    self.assertEqual(row["IsDomainIP"], 1)
    self.assertEqual(row["NoOfSubDomain"], 0)

  def test_invalid_urls_raise_value_error(self):
    for value in ["", "   ", "not-a-url", "https://bad host/path",
                  "https://example.com:bad", "ftp://example.com", "https://example..com"]:
      with self.subTest(value=value), self.assertRaises(ValueError):
        extract_url_features(value)


if __name__ == "__main__":
  unittest.main()
