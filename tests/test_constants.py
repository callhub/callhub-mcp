"""Sanity checks on the endpoint constants."""
from callhub.constants import ENDPOINTS


def _endpoint_items():
    return [
        (name, value)
        for name, value in vars(ENDPOINTS).items()
        if not name.startswith("_") and isinstance(value, str)
    ]


def test_endpoints_are_non_empty_strings():
    items = _endpoint_items()
    assert items, "ENDPOINTS should define endpoint strings"
    for name, value in items:
        assert value, f"{name} is empty"


def test_endpoints_start_with_slash():
    for name, value in _endpoint_items():
        assert value.startswith("/"), f"{name} should start with '/': {value!r}"


def test_relational_endpoint_uses_v_1():
    # CallHub's relational (external email service) path is v_1, not v1.
    assert ENDPOINTS.RELATIONAL_CAMPAIGN == "/email/v_1/relational-campaign/"
