"""Tests for domain function interfaces."""
import inspect
import sys
import os

# Ensure src is on path (conftest.py does this but be explicit for direct runs)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from callhub import agents, contacts, teams, dnc, campaigns, numbers
from callhub import vb_campaigns, sms_campaigns, sms_broadcasts, p2p_campaigns
from callhub import phonebooks, tags, custom_fields, webhooks, users
from callhub import survey_templates, questions, integration_fields, urls
from callhub import relational_organizing

# All domain modules and their expected functions
DOMAIN_MODULES = {
    agents: ['list_agents', 'get_agent', 'create_agent', 'get_live_agents',
             'get_agent_key', 'get_agent_status'],
    contacts: ['list_contacts', 'get_contact', 'create_contact', 'create_contacts_bulk',
               'update_contact', 'delete_contact', 'get_contact_fields'],
    teams: ['list_teams', 'get_team', 'create_team', 'update_team', 'delete_team',
            'get_team_agents', 'get_team_agent_details', 'add_agents_to_team', 'remove_agents_from_team'],
    dnc: ['create_dnc_contact', 'list_dnc_contacts', 'update_dnc_contact', 'delete_dnc_contact',
          'create_dnc_list', 'list_dnc_lists', 'update_dnc_list', 'delete_dnc_list',
          'add_contacts_to_suppression_list'],
    campaigns: ['list_call_center_campaigns', 'update_call_center_campaign',
                'create_call_center_campaign', 'delete_call_center_campaign',
                'upload_media_file', 'get_export_job_result'],
    numbers: ['list_rented_numbers', 'list_validated_numbers', 'rent_number'],
    vb_campaigns: ['list_voice_broadcasts', 'get_vb_campaign', 'create_voice_broadcast_campaign',
                   'delete_voice_broadcast_campaign', 'update_voice_broadcast_campaign'],
    sms_campaigns: ['list_sms_campaigns', 'update_sms_campaign', 'delete_sms_campaign'],
    sms_broadcasts: ['create_sms_broadcast', 'get_sms_broadcast', 'update_sms_broadcast',
                     'duplicate_sms_broadcast'],
    users: ['list_users', 'get_credit_usage', 'get_user_details', 'share_credits'],
    webhooks: ['list_webhooks', 'get_webhook', 'create_webhook', 'delete_webhook'],
}


def test_all_domain_functions_exist():
    """Verify all expected domain functions are defined."""
    for module, functions in DOMAIN_MODULES.items():
        for func_name in functions:
            assert hasattr(module, func_name), \
                f"{module.__name__}.{func_name} not found"


def test_domain_functions_accept_params_dict():
    """All domain functions should accept a single params dict argument."""
    for module, functions in DOMAIN_MODULES.items():
        for func_name in functions:
            func = getattr(module, func_name)
            sig = inspect.signature(func)
            params = list(sig.parameters.keys())
            assert len(params) == 1, \
                f"{module.__name__}.{func_name} should accept 1 param (params dict), got {len(params)}: {params}"
            assert params[0] == 'params', \
                f"{module.__name__}.{func_name} param should be named 'params', got '{params[0]}'"


def test_domain_functions_return_error_on_missing_required():
    """Domain functions should return isError when required params are missing."""
    # Test a few representative functions with empty params
    test_cases = [
        (dnc.create_dnc_contact, {}),
        (dnc.update_dnc_contact, {}),
        (dnc.delete_dnc_contact, {}),
        (contacts.create_contact, {}),
        (teams.create_team, {}),
    ]
    for func, params in test_cases:
        result = func(params)
        assert result.get('isError') is True, \
            f"{func.__name__}({params}) should return isError=True for missing required params"
