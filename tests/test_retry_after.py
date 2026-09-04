"""Retry-path regressions for callhub.utils.

requests.Response.__bool__ returns .ok, so `if e.response:` is falsy for exactly
the 4xx/5xx responses the retry/error code was written to handle. These tests
pin the corrected behavior: honor Retry-After, stop retrying (rather than
retry while still throttled) when the requested delay exceeds our max wait, and
report a quota-neutral 429 message that names the delay.
"""
import pytest
import requests

from callhub import utils

URL = "https://api.callhub.io/v1/contacts/"


def _response(status, headers=None, body=b""):
    resp = requests.Response()
    resp.status_code = status
    resp.reason = "Too Many Requests" if status == 429 else "Error"
    resp.url = URL
    resp.headers.update(headers or {})
    resp._content = body
    return resp


def _always_throttled(headers):
    def call():
        raise requests.exceptions.HTTPError(response=_response(429, headers))
    return call


@pytest.fixture
def slept(monkeypatch):
    """Record the delays the retry loop asks for instead of waiting them out."""
    delays = []
    monkeypatch.setattr(utils.time, "sleep", delays.append)
    return delays


def test_retry_after_header_sets_the_delay(slept):
    with pytest.raises(requests.exceptions.HTTPError):
        utils.retry_with_backoff(
            _always_throttled({"Retry-After": "7"}),
            max_retries=2, initial_backoff=0.1, backoff_factor=2, max_backoff=60,
        )
    assert slept == [7.0, 7.0]


def test_long_retry_after_stops_retrying(slept):
    # A Retry-After beyond max_backoff must NOT be truncated-and-retried into
    # another 429; the loop stops immediately and lets the caller surface it.
    with pytest.raises(requests.exceptions.HTTPError):
        utils.retry_with_backoff(
            _always_throttled({"Retry-After": "3600"}),
            max_retries=3, initial_backoff=0.1, max_backoff=60,
        )
    assert slept == []


def test_backoff_when_no_retry_after(slept):
    with pytest.raises(requests.exceptions.HTTPError):
        utils.retry_with_backoff(
            _always_throttled({}),
            max_retries=2, initial_backoff=1, backoff_factor=2, max_backoff=60,
        )
    assert len(slept) == 2
    assert 0.8 <= slept[0] <= 1.2
    assert 1.6 <= slept[1] <= 2.4


def test_throttled_call_reports_delay_quota_neutral(monkeypatch, slept):
    monkeypatch.setattr(
        requests, "request",
        lambda **kwargs: _response(429, {"Retry-After": "3600"}, b'{"detail": "Request was throttled."}'),
    )
    result = utils.api_call("GET", URL, {}, max_retries=1)
    assert result["isError"] is True
    text = result["content"][0]["text"]
    assert "Rate limit exceeded (429)" in text
    assert "3600" in text
    # The shared 429 path handles per-day-limited endpoints too, so it must not
    # assert a per-minute quota.
    assert "per minute" not in text.lower()


def test_connection_error_is_reported_not_crashed(monkeypatch, slept):
    # A ConnectionError has no .response at all; the error path must handle that
    # (the `e.response is not None` guards) and report it rather than raise.
    def refuse(**kwargs):
        raise requests.exceptions.ConnectionError("connection refused")
    monkeypatch.setattr(requests, "request", refuse)
    result = utils.api_call("GET", URL, {}, max_retries=1)
    assert result["isError"] is True
