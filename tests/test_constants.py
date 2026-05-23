"""Tests for API endpoint constants."""
from callhub.constants import ENDPOINTS

def test_all_endpoints_are_strings():
    for attr in dir(ENDPOINTS):
        if attr.startswith('_'):
            continue
        value = getattr(ENDPOINTS, attr)
        assert isinstance(value, str), f"ENDPOINTS.{attr} should be str, got {type(value)}"

def test_all_endpoints_start_with_slash():
    for attr in dir(ENDPOINTS):
        if attr.startswith('_'):
            continue
        value = getattr(ENDPOINTS, attr)
        assert value.startswith('/'), f"ENDPOINTS.{attr} = '{value}' should start with /"

def test_v1_endpoints_exist():
    """Verify core v1 endpoints are defined."""
    required = ['AGENTS', 'CONTACTS_V1', 'TEAMS', 'WEBHOOKS', 'CALL_CENTER_CAMPAIGNS',
                 'VOICE_BROADCASTS', 'SMS_CAMPAIGNS', 'DNC_CONTACTS', 'DNC_LISTS',
                 'NUMBERS', 'PHONEBOOKS', 'TEMPLATES', 'USERS']
    for name in required:
        assert hasattr(ENDPOINTS, name), f"ENDPOINTS.{name} not defined"

def test_v2_endpoints_exist():
    """Verify core v2 endpoints are defined."""
    required = ['CREDITS_USAGE', 'TAGS', 'CONTACTS', 'SMS_BROADCAST',
                 'MEDIA_UPLOAD', 'AGENT_KEY', 'AGENT_STATUS', 'USER_DETAILS']
    for name in required:
        assert hasattr(ENDPOINTS, name), f"ENDPOINTS.{name} not defined"

def test_relational_campaign_uses_v_1():
    """Regression: relational campaign URL must use v_1 not v1."""
    assert '/v_1/' in ENDPOINTS.RELATIONAL_CAMPAIGN, \
        f"RELATIONAL_CAMPAIGN should use /v_1/ but got {ENDPOINTS.RELATIONAL_CAMPAIGN}"
