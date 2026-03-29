"""Tests for RateLimiter."""

from config import RateLimitConfig
from scrapers.base import RateLimiter


class TestRateLimiter:
    def test_first_request_no_wait(self, mocker):
        sleep_mock = mocker.patch("time.sleep")
        rate_limiter = RateLimiter(RateLimitConfig(min_delay=1.0))
        rate_limiter.wait("example.com")
        sleep_mock.assert_not_called()

    def test_subsequent_request_waits_correct_duration(self, mocker):
        mocker.patch("random.uniform", return_value=0.0)
        sleep_mock = mocker.patch("time.sleep")
        mocker.patch("time.time", side_effect=[100.0, 100.0, 100.0, 101.0])
        rate_limiter = RateLimiter(RateLimitConfig(min_delay=1.0, jitter=0.0))
        rate_limiter.wait("example.com")
        rate_limiter.wait("example.com")
        sleep_mock.assert_called_once_with(1.0)

    def test_wait_time_with_jitter(self, mocker):
        mocker.patch("random.uniform", return_value=0.25)
        sleep_mock = mocker.patch("time.sleep")
        mocker.patch("time.time", side_effect=[100.0, 100.0, 100.0, 100.5])
        rate_limiter = RateLimiter(RateLimitConfig(min_delay=1.0, jitter=0.5))
        rate_limiter.wait("example.com")
        rate_limiter.wait("example.com")
        sleep_mock.assert_called_once()
        wait_time = sleep_mock.call_args[0][0]
        assert 1.0 <= wait_time <= 1.5

    def test_jitter_bounds_minimum(self, mocker):
        mocker.patch("random.uniform", return_value=0.0)
        sleep_mock = mocker.patch("time.sleep")
        mocker.patch("time.time", side_effect=[100.0, 100.0, 100.0, 100.0])
        rate_limiter = RateLimiter(RateLimitConfig(min_delay=2.0, jitter=1.0))
        rate_limiter.wait("example.com")
        rate_limiter.wait("example.com")
        sleep_mock.assert_called_once_with(2.0)

    def test_jitter_bounds_maximum(self, mocker):
        mocker.patch("random.uniform", return_value=1.0)
        sleep_mock = mocker.patch("time.sleep")
        mocker.patch("time.time", side_effect=[100.0, 100.0, 100.0, 100.0])
        rate_limiter = RateLimiter(RateLimitConfig(min_delay=2.0, jitter=1.0))
        rate_limiter.wait("example.com")
        rate_limiter.wait("example.com")
        sleep_mock.assert_called_once_with(3.0)

    def test_multiple_domains_independent(self, mocker):
        sleep_mock = mocker.patch("time.sleep")
        rate_limiter = RateLimiter(RateLimitConfig(min_delay=1.0, jitter=0.0))
        rate_limiter.wait("example.com")
        rate_limiter.wait("other.com")
        sleep_mock.assert_not_called()

    def test_record_request_updates_timing(self, mocker):
        sleep_mock = mocker.patch("time.sleep")
        mocker.patch("time.time", side_effect=[100.0, 101.0, 101.0])
        rate_limiter = RateLimiter(RateLimitConfig(min_delay=1.0, jitter=0.0))
        rate_limiter.record_request("example.com")
        rate_limiter.wait("example.com")
        sleep_mock.assert_not_called()

    def test_default_config_values(self, mocker):
        mocker.patch("random.uniform", return_value=0.0)
        sleep_mock = mocker.patch("time.sleep")
        mocker.patch("time.time", side_effect=[100.0, 100.0, 100.0, 100.0])
        rate_limiter = RateLimiter()
        rate_limiter.wait("example.com")
        rate_limiter.wait("example.com")
        sleep_mock.assert_called_once()
        wait_time = sleep_mock.call_args[0][0]
        default_min_delay = 2.0
        assert wait_time == default_min_delay
