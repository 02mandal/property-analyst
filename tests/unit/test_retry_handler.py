"""Tests for RetryHandler."""

import pytest

from config import RetryConfig
from scrapers.base import RetryHandler


class TestRetryHandlerBackoffDelay:
    def test_first_attempt_base_delay(self):
        handler = RetryHandler(RetryConfig(base_delay=2.0, jitter=0.0))
        delay = handler.backoff_delay(0)
        assert delay == 2.0

    def test_exponential_backoff(self):
        handler = RetryHandler(RetryConfig(base_delay=2.0, exponential_base=2.0, jitter=0.0))
        assert handler.backoff_delay(0) == 2.0
        assert handler.backoff_delay(1) == 4.0
        assert handler.backoff_delay(2) == 8.0
        assert handler.backoff_delay(3) == 16.0

    def test_max_delay_cap(self):
        handler = RetryHandler(RetryConfig(base_delay=2.0, max_delay=10.0, jitter=0.0))
        assert handler.backoff_delay(0) == 2.0
        assert handler.backoff_delay(1) == 4.0
        assert handler.backoff_delay(2) == 8.0
        assert handler.backoff_delay(3) == 10.0
        assert handler.backoff_delay(4) == 10.0

    def test_jitter_bounds_minimum(self, mocker):
        mocker.patch("random.uniform", return_value=0.0)
        handler = RetryHandler(RetryConfig(base_delay=2.0, jitter=1.0))
        delay = handler.backoff_delay(0)
        assert delay == 2.0

    def test_jitter_bounds_maximum(self, mocker):
        mocker.patch("random.uniform", return_value=1.0)
        handler = RetryHandler(RetryConfig(base_delay=2.0, jitter=1.0))
        delay = handler.backoff_delay(0)
        assert delay == 3.0

    def test_jitter_with_exponential_backoff(self, mocker):
        mocker.patch("random.uniform", return_value=0.5)
        handler = RetryHandler(RetryConfig(base_delay=2.0, exponential_base=2.0, jitter=1.0))
        delay = handler.backoff_delay(1)
        assert delay == 4.5

    def test_default_config_values(self):
        handler = RetryHandler()
        delay_0 = handler.backoff_delay(0)
        assert delay_0 >= 2.0
        assert delay_0 <= 2.5


class TestRetryHandlerIsRetryable:
    def test_rate_limit_retryable(self):
        handler = RetryHandler()
        assert handler.is_retryable(429) is True

    @pytest.mark.parametrize(
        "status_code",
        [500, 502, 503, 504],
        ids=["500", "502", "503", "504"],
    )
    def test_server_errors_retryable(self, status_code):
        handler = RetryHandler()
        assert handler.is_retryable(status_code) is True

    def test_success_not_retryable(self):
        handler = RetryHandler()
        assert handler.is_retryable(200) is False

    def test_client_error_not_retryable(self):
        handler = RetryHandler()
        assert handler.is_retryable(400) is False

    def test_not_found_not_retryable(self):
        handler = RetryHandler()
        assert handler.is_retryable(404) is False
