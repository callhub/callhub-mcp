"""Tests for authentication and client configuration."""
from callhub.auth import get_account_config
from callhub.client import McpApiClient

def test_default_account_resolves():
    """Default account should resolve using env vars set in conftest."""
    # conftest.py sets CALLHUB_DEFAULT_API_KEY which maps to account 'default'
    account, api_key, base_url = get_account_config('default')
    assert account == 'default'
    assert api_key is not None
    assert base_url is not None

def test_client_instantiates():
    """McpApiClient should instantiate without errors."""
    client = McpApiClient(None)
    assert client is not None
