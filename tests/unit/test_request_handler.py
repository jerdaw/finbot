"""Tests for request_handler and retry_config.

Tests RetryConfig initialization, RequestHandler creation, session management,
error handling, and unsupported request types.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from finbot.utils.request_utils.request_handler import RequestHandler
from finbot.utils.request_utils.retry_config import RetryConfig


class TestRetryConfig:
    """Tests for RetryConfig."""

    def test_default_values(self):
        config = RetryConfig()
        assert config.retry_count == 3
        assert config.backoff_factor == 0.3
        assert config.status_forcelist == (429, 500, 502, 503, 504)

    def test_custom_values(self):
        config = RetryConfig(retry_count=5, backoff_factor=1.0, status_forcelist=(500, 502))
        assert config.retry_count == 5
        assert config.backoff_factor == 1.0
        assert config.status_forcelist == (500, 502)

    def test_apply_to_session(self):
        config = RetryConfig()
        session = requests.Session()
        config.apply_to_session(session)
        # Check that adapters are mounted for both http and https
        assert "https://" in session.adapters
        assert "http://" in session.adapters

    def test_apply_to_session_retry_strategy(self):
        config = RetryConfig(retry_count=5)
        session = requests.Session()
        config.apply_to_session(session)
        adapter = session.get_adapter("https://example.com")
        assert adapter.max_retries.total == 5


class TestRequestHandler:
    """Tests for RequestHandler."""

    def test_init_default_retry(self):
        handler = RequestHandler()
        assert hasattr(handler, "session")
        assert isinstance(handler.session, requests.Session)

    def test_init_custom_retry(self):
        config = RetryConfig(retry_count=5)
        handler = RequestHandler(retry_config=config)
        assert isinstance(handler.session, requests.Session)

    def test_context_manager(self):
        with RequestHandler() as handler:
            assert isinstance(handler, RequestHandler)
            assert isinstance(handler.session, requests.Session)
        # After exiting, session should be closed (no error on close)

    def test_unsupported_request_type_raises(self):
        handler = RequestHandler()
        with pytest.raises(NotImplementedError, match="not supported"):
            handler.make_request("https://example.com", request_type="INVALID")

    @patch.object(requests.Session, "request")
    def test_make_request_get(self, mock_request):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        handler = RequestHandler()
        response = handler.make_request("https://example.com", request_type="GET")
        assert response.ok
        mock_request.assert_called_once()

    @patch.object(requests.Session, "request")
    def test_make_json_request(self, mock_request):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.headers = {"Content-Type": "application/json; charset=utf-8"}
        mock_response.json.return_value = {"key": "value"}
        mock_request.return_value = mock_response

        handler = RequestHandler()
        result = handler.make_json_request("https://api.example.com/data")
        assert result == {"key": "value"}

    @patch.object(requests.Session, "request")
    def test_make_json_request_non_json_raises(self, mock_request):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.headers = {"Content-Type": "text/html"}
        mock_request.return_value = mock_response

        handler = RequestHandler()
        with pytest.raises(ValueError, match="not in JSON format"):
            handler.make_json_request("https://example.com")

    @patch.object(requests.Session, "request")
    def test_make_text_request(self, mock_request):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.headers = {"Content-Type": "text/plain"}
        mock_response.text = "Hello, World!"
        mock_request.return_value = mock_response

        handler = RequestHandler()
        result = handler.make_text_request("https://example.com/text")
        assert result == "Hello, World!"

    @patch.object(requests.Session, "request")
    def test_make_text_request_non_text_still_returns(self, mock_request):
        """Non text/plain content should still be returned (with warning)."""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.text = "<html>page</html>"
        mock_request.return_value = mock_response

        handler = RequestHandler()
        result = handler.make_text_request("https://example.com")
        assert result == "<html>page</html>"

    @patch.object(requests.Session, "request")
    def test_failed_request_raises(self, mock_request):
        mock_request.side_effect = requests.RequestException("Connection failed")

        handler = RequestHandler()
        with pytest.raises(requests.RequestException):
            handler.make_request("https://example.com")

    @patch.object(requests.Session, "request")
    def test_http_error_status_raises(self, mock_request):
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.reason = "Internal Server Error"
        mock_response.raise_for_status.side_effect = requests.HTTPError("500")
        mock_request.return_value = mock_response

        handler = RequestHandler()
        with pytest.raises(requests.HTTPError):
            handler.make_request("https://example.com")

    def test_save_response_json(self, tmp_path):
        handler = RequestHandler()
        save_options = {"save_dir": str(tmp_path), "file_name": "test.json.zst"}
        handler.save_response(save_options, {"key": "value"})
        # File should be saved (zstd compressed)
        saved_files = list(tmp_path.iterdir())
        assert len(saved_files) == 1

    def test_save_response_text(self, tmp_path):
        handler = RequestHandler()
        save_options = {"save_dir": str(tmp_path), "file_name": "test.txt.zst"}
        handler.save_response(save_options, "some text content")
        saved_files = list(tmp_path.iterdir())
        assert len(saved_files) == 1

    def test_save_response_no_save_dir(self):
        """Without save_dir, nothing should be saved."""
        handler = RequestHandler()
        handler.save_response({}, {"key": "value"})  # Should not raise

    @pytest.mark.parametrize("method", ["GET", "POST", "PUT", "DELETE", "PATCH"])
    @patch.object(requests.Session, "request")
    def test_all_supported_methods(self, mock_request, method):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_request.return_value = mock_response

        handler = RequestHandler()
        response = handler.make_request("https://example.com", request_type=method)
        assert response.ok
