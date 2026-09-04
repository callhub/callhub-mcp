"""Regressions for the retry path in callhub.utils: a throttled request must wait
the delay the server asked for, cap that delay, and tell the caller about it."""
import pathlib
import sys

import pytest
import requests

SRC = pathlib.Path(__file__).resolve().parent.parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from callhub import utils  # noqa: E402

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


def test_retry_after_is_bounded_by_max_backoff(slept):
    with pytest.raises(requests.exceptions.HTTPError):
        utils.retry_with_backoff(
            _always_throttled({"Retry-After": "3600"}),
            max_retries=1, initial_backoff=0.1, max_backoff=5,
        )
    assert slept == [5]


def test_backoff_is_used_when_the_server_sends_no_retry_after(slept):
    with pytest.raises(requests.exceptions.HTTPError):
        utils.retry_with_backoff(
            _always_throttled({}),
            max_retries=2, initial_backoff=1, backoff_factor=2, max_backoff=60,
        )
    assert len(slept) == 2
    assert 0.8 <= slept[0] <= 1.2
    assert 1.6 <= slept[1] <= 2.4


def test_throttled_call_reports_the_retry_delay(monkeypatch, slept):
    monkeypatch.setattr(
        requests, "request",
        lambda **kwargs: _response(429, {"Retry-After": "60"}, b'{"detail": "Request was throttled."}'),
    )
    result = utils.api_call("GET", URL, {}, max_retries=1)
    assert result["isError"] is True
    text = result["content"][0]["text"]
    assert "Rate limit exceeded (429)" in text
    assert "60" in text


def test_connection_error_is_retried_and_reported(monkeypatch, slept):
    def refuse(**kwargs):
        raise requests.exceptions.ConnectionError("connection refused")

    monkeypatch.setattr(requests, "request", refuse)
    result = utils.api_call("GET", URL, {}, max_retries=1)
    assert result["isError"] is True
    assert "connection refused" in result["content"][0]["text"]
    assert len(slept) == 1
