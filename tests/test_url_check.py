"""Offline tests for URL status-check validation and bounded request behavior."""
import socket
import unittest
from unittest.mock import MagicMock, patch

from src.url_check import check_url_reachability


class UrlCheckTests(unittest.TestCase):
    def test_private_ip_is_blocked_without_network_request(self):
        with self.assertRaisesRegex(ValueError, "public internet hosts"):
            check_url_reachability("http://127.0.0.1/")

    def test_non_http_scheme_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "HTTP or HTTPS"):
            check_url_reachability("ftp://example.com/file")

    def test_get_is_streamed_and_redirect_is_not_followed(self):
        dns_record = (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))
        response = MagicMock(status_code=302, reason="Found", headers={"Location": "https://other.example/"})
        with patch("src.url_check.socket.getaddrinfo", return_value=[dns_record]), \
             patch("src.url_check.requests.get", return_value=response) as get_request:
            result = check_url_reachability("https://example.com/path")
        self.assertEqual(result["status_code"], 302)
        self.assertEqual(result["redirect_location"], "https://other.example/")
        get_request.assert_called_once()
        self.assertTrue(get_request.call_args.kwargs["stream"])
        self.assertFalse(get_request.call_args.kwargs["allow_redirects"])
        response.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
