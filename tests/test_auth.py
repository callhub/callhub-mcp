"""Credential resolution tests (no network)."""
import importlib


def test_default_account_resolves(default_credentials):
    import callhub.auth as auth
    importlib.reload(auth)
    account, api_key, base_url = auth.get_account_config()
    assert account == "default"
    assert api_key == "test-key"
    assert base_url == "https://api-na1.callhub.io"


def test_client_instantiates(default_credentials):
    from callhub.client import McpApiClient
    client = McpApiClient()
    assert client.api_key == "test-key"
    assert client.base_url == "https://api-na1.callhub.io"


def test_build_url_strips_trailing_slash():
    from callhub.utils import build_url
    # A base URL pasted with a trailing slash must not double up.
    url = build_url("https://api-na1.callhub.io/", "/v1/contacts/")
    assert url == "https://api-na1.callhub.io/v1/contacts/"
