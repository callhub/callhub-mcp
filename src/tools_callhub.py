# File: src/tools_callhub.py

"""
CallHub API Tools for Claude

This module contains tools for interacting with the CallHub API through Claude.

## Server Restart Guidelines

The CallHub MCP server must be restarted manually by the user after any code changes.
If you're using Claude or another AI assistant to modify this code:

1. The AI should NEVER assume a restart has occurred
2. The AI should ALWAYS pause after suggesting code changes
3. The AI should explicitly ask the user to restart the server
4. The AI should wait for confirmation before proceeding with testing

This is critical for ensuring code changes take effect before testing.

## Agent Activation Workflow

When new agents are created via the API, they exist in a 'pending' state and must verify their email before becoming active. These pending agents are:
- NOT visible through the standard listAgents API (even with include_pending=true)
- NOT manageable through direct API calls
- Only accessible through the activation exports workflow

To activate pending agents:
1. Use exportAgentActivationUrls or getAgentActivationExportUrl to obtain the export URL
2. User downloads the activation CSV file from the CallHub UI
3. Process the CSV using processAgentActivationCsv or related functions
4. Activate agents using activateAgentsWithPassword or activateAgentsWithBatchPassword

IMPORTANT: NEVER create new test agents to check activation status - this workflow is specifically designed because pending agents are not accessible through direct API calls.
"""

# IMPORTANT: DO NOT attempt to restart the server on your own.
# You MUST ask the user to restart the server after making code changes
# and wait for their confirmation before proceeding with testing.
# ALWAYS STOP between writing code changes and testing those changes.

import os
import json
import requests
import sys
import urllib.parse
from typing import Dict, List, Union, Optional, Any

# Import from our new modules
from callhub.auth import (
    load_all_credentials,
    save_credentials,
    get_account_config
)

from callhub.account_management import (
    add_account,
    update_account,
    delete_account
)

from callhub.utils import (
    build_url,
    parse_input_fields,
    api_call,
    get_auth_headers
)

from callhub.agents import (
    list_agents,
    get_agent,
    create_agent,
    delete_agent,
    get_live_agents
)

from callhub.teams import (
    list_teams,
    get_team,
    create_team,
    update_team,
    delete_team,
    get_team_agents,
    get_team_agent_details,
    add_agents_to_team,
    remove_agents_from_team,
    validate_team_exists
)

from callhub.users import (
    list_users,
    get_credit_usage
)

from callhub.dnc import (
    create_dnc_contact,
    list_dnc_contacts,
    update_dnc_contact,
    delete_dnc_contact,
    create_dnc_list,
    list_dnc_lists,
    update_dnc_list,
    delete_dnc_list
)

from callhub.contacts import (
    list_contacts,
    get_contact,
    create_contact,
    create_contacts_bulk,
    update_contact,
    delete_contact,
    get_contact_fields,
    find_duplicate_contacts
)

from callhub.phonebooks import (
    list_phonebooks,
    get_phonebook,
    create_phonebook,
    update_phonebook,
    delete_phonebook,
    add_contacts_to_phonebook,
    remove_contact_from_phonebook,
    get_phonebook_count,
    get_phonebook_contacts
)

from callhub.webhooks import (
    list_webhooks,
    get_webhook,
    create_webhook,
    delete_webhook
)

from callhub.campaigns import (
    list_call_center_campaigns,
    update_call_center_campaign,
    delete_call_center_campaign,
    create_call_center_campaign
)

from callhub.numbers import (
    list_rented_numbers,
    list_validated_numbers,
    rent_number
)

from callhub.voice_broadcasts import (
    list_voice_broadcasts,
    update_voice_broadcast,
    delete_voice_broadcast
)

from callhub.sms_campaigns import (
    list_sms_campaigns,
    update_sms_campaign,
    delete_sms_campaign
)

from callhub.p2p_campaigns import (
    list_p2p_campaigns,
    update_p2p_campaign,
    delete_p2p_campaign,
    create_p2p_campaign,
    get_p2p_campaign_agents,
    add_agents_to_p2p_campaign,
    reassign_p2p_agents,
    get_p2p_surveys
)

from callhub.browser_automation import (
    export_agent_activation_urls_browser,
    activate_agents_with_password,
    parse_activation_csv,
    process_local_activation_csv
)

# Import new activation tools from mcp_tools module
from callhub.mcp_tools.batch_activation_tools import (
    prepare_agent_activation,
    activate_agents_with_batch_password,
    get_activation_status,
    reset_activation_state
)

# Re-export functions to maintain backwards compatibility
# This ensures server.py doesn't break

def list_accounts(params: dict = None) -> dict:
    """Return all account keys from the credentials file."""
    creds = load_all_credentials()
    return {"accounts": list(creds.keys())}

def add_callhub_account(params: dict) -> dict:
    """Add a new CallHub account to the .env file.
    
    Required parameters:
    - accountName: Name of the account to add
    - username: CallHub username (typically an email address)
    - apiKey: API key for the account
    - baseUrl: Base URL for the CallHub instance
    """
    account_name = params.get("accountName")
    username = params.get("username")
    api_key = params.get("apiKey")
    base_url = params.get("baseUrl")
    
    if not account_name or not username or not api_key or not base_url:
        return {
            "isError": True,
            "content": [{"type": "text", "text": "All credential fields are required: 'accountName', 'username', 'apiKey', and 'baseUrl'."}]
        }
    
    result = add_account(account_name, username, api_key, base_url)
    
    if not result.get("success"):
        return {
            "isError": True,
            "content": [{"type": "text", "text": result.get("message")}]
        }
    
    return result

def update_callhub_account(params: dict) -> dict:
    """Update an existing CallHub account in the .env file.
    
    Required parameters:
    - accountName: Name of the account to update
    
    Optional parameters:
    - username: New username/email
    - apiKey: New API key
    - baseUrl: New base URL
    """
    account_name = params.get("accountName")
    username = params.get("username")
    api_key = params.get("apiKey")
    base_url = params.get("baseUrl")
    
    if not account_name:
        return {
            "isError": True,
            "content": [{"type": "text", "text": "'accountName' is required."}]
        }
    
    if not username and not api_key and not base_url:
        return {
            "isError": True,
            "content": [{"type": "text", "text": "At least one of 'username', 'apiKey', or 'baseUrl' must be provided."}]
        }
    
    result = update_account(account_name, username, api_key, base_url)
    
    if not result.get("success"):
        return {
            "isError": True,
            "content": [{"type": "text", "text": result.get("message")}]
        }
    
    return result

def delete_callhub_account(params: dict) -> dict:
    """Delete a CallHub account from the .env file.
    
    Required parameters:
    - accountName: Name of the account to delete
    """
    account_name = params.get("accountName")
    
    if not account_name:
        return {
            "isError": True,
            "content": [{"type": "text", "text": "'accountName' is required."}]
        }
    
    result = delete_account(account_name)
    
    if not result.get("success"):
        return {
            "isError": True,
            "content": [{"type": "text", "text": result.get("message")}]
        }
    
    return result

def fetch_agents(params: dict) -> dict:
    """Retrieve agents (v1) via the CallHub API."""
    # Updated to use the new module
    return list_agents(params)


# Call Center Campaign Functions
def listCallCenterCampaigns(params: dict) -> dict:
    """List all call center campaigns with optional pagination."""
    return list_call_center_campaigns(params)

def updateCallCenterCampaign(params: dict) -> dict:
    """Update a call center campaign's status."""
    return update_call_center_campaign(params)

def deleteCallCenterCampaign(params: dict) -> dict:
    """Delete a call center campaign by ID."""
    return delete_call_center_campaign(params)

def createCallCenterCampaign(params: dict) -> dict:
    """Create a new call center campaign.
    
    See the campaigns.py module for detailed documentation on the required structure
    and example of the campaign_data parameter.
    """
    return create_call_center_campaign(params)


# Phone Number Management Functions
def listRentedNumbers(params: dict) -> dict:
    """List all rented calling numbers (caller IDs) for the account."""
    return list_rented_numbers(params)

def listValidatedNumbers(params: dict) -> dict:
    """List all validated personal phone numbers that can be used as caller IDs."""
    return list_validated_numbers(params)

def rentNumber(params: dict) -> dict:
    """Rent a new phone number to use as a caller ID."""
    return rent_number(params)


# Voice Broadcast Campaign Functions
def listVoiceBroadcastCampaigns(params: dict) -> dict:
    """List all voice broadcast campaigns with optional pagination."""
    return list_voice_broadcasts(params)

def updateVoiceBroadcastCampaign(params: dict) -> dict:
    """Update a voice broadcast campaign's status.
    
    Valid status values are: "start", "pause", "abort", "end" or 1-4 numerically.
    """
    return update_voice_broadcast(params)

def deleteVoiceBroadcastCampaign(params: dict) -> dict:
    """Delete a voice broadcast campaign by ID."""
    return delete_voice_broadcast(params)


# SMS Campaign Functions
def listSmsCampaigns(params: dict) -> dict:
    """List all SMS campaigns with optional pagination."""
    return list_sms_campaigns(params)

def updateSmsCampaign(params: dict) -> dict:
    """Update an SMS campaign's status.
    
    Valid status values are: "start", "pause", "abort", "end" or 1-4 numerically.
    """
    return update_sms_campaign(params)

def deleteSmsCampaign(params: dict) -> dict:
    """Delete an SMS campaign by ID."""
    return delete_sms_campaign(params)


# P2P Campaign Functions
def listP2pCampaigns(params: dict) -> dict:
    """List all P2P campaigns with optional pagination."""
    return list_p2p_campaigns(params)

def updateP2pCampaign(params: dict) -> dict:
    """Update a P2P campaign's status.
    
    Valid status values are: "start", "pause", "abort", "end" or 1-4 numerically.
    """
    return update_p2p_campaign(params)

def deleteP2pCampaign(params: dict) -> dict:
    """Delete a P2P campaign by ID."""
    return delete_p2p_campaign(params)

def createP2pCampaign(params: dict) -> dict:
    """Create a new P2P (Snowflake) campaign.
    
    Required parameters:
    - campaign_data: Dictionary containing campaign configuration
    """
    return create_p2p_campaign(params)

def getP2pCampaignAgents(params: dict) -> dict:
    """Get agents for a P2P campaign."""
    return get_p2p_campaign_agents(params)

def addAgentsToP2pCampaign(params: dict) -> dict:
    """Add agents to a P2P campaign."""
    return add_agents_to_p2p_campaign(params)

def reassignP2pAgents(params: dict) -> dict:
    """Reassign agents in a P2P campaign."""
    return reassign_p2p_agents(params)

def getP2pSurveys(params: dict) -> dict:
    """Get surveys for a P2P campaign."""
    return get_p2p_surveys(params)


# User and Credit Usage Functions
def getUsers(params: dict) -> dict:
    """Retrieve a list of all users in the CallHub account."""
    return list_users(params)

def getCreditUsage(params: dict) -> dict:
    """Retrieve credit usage details for the CallHub account."""
    return get_credit_usage(params)


# Team Management Functions
def listTeams(params: dict) -> dict:
    """List all teams in the CallHub account."""
    return list_teams(params)

def getTeam(params: dict) -> dict:
    """Get details for a specific team by ID."""
    return get_team(params)

def createTeam(params: dict) -> dict:
    """Create a new team.
    
    Required parameters:
    - name: Name of the team to create
    """
    return create_team(params)

def updateTeam(params: dict) -> dict:
    """Update a team's name by ID.
    
    Required parameters:
    - teamId: The ID of the team to update
    - name: New name for the team
    """
    return update_team(params)

def deleteTeam(params: dict) -> dict:
    """Delete a team by ID.
    
    Required parameters:
    - teamId: The ID of the team to delete
    
    Notes:
    - All agents associated with the team will be unassigned
    """
    return delete_team(params)

def getTeamAgents(params: dict) -> dict:
    """Get a list of all agents assigned to a specific team.
    
    Required parameters:
    - teamId: The ID of the team
    """
    return get_team_agents(params)

def getTeamAgentDetails(params: dict) -> dict:
    """Get details for a specific agent in a team.
    
    Required parameters:
    - teamId: The ID of the team
    - agentId: The ID of the agent
    """
    return get_team_agent_details(params)

def addAgentsToTeam(params: dict) -> dict:
    """Add one or more agents to a team.
    
    Required parameters:
    - teamId: The ID of the team
    - agentIds: List of agent IDs to add to the team
    """
    return add_agents_to_team(params)

def removeAgentsFromTeam(params: dict) -> dict:
    """Remove one or more agents from a team.
    
    Required parameters:
    - teamId: The ID of the team
    - agentIds: List of agent IDs to remove from the team
    """
    return remove_agents_from_team(params)


# CSV Processing Functions
def processAgentActivationCsv(params: dict) -> dict:
    """Process an agent activation CSV file provided as a string.
    
    IMPORTANT: This is different from processing uploaded files. Claude cannot read
    uploaded file contents directly. This function takes actual CSV content as a string.
    
    Args:
        csv_content: CSV content as a string
        
    Returns:
        Dict with parsed activation data
    """
    csv_content = params.get("csv_content")
    
    if not csv_content:
        return {
            "isError": True,
            "content": [{"type": "text", "text": "No CSV content provided"}]
        }
    
    return parse_activation_csv(csv_content)

def processUploadedActivationCsv(params: dict) -> dict:
    """Process an agent activation CSV file based on filename from an uploaded file.
    
    IMPORTANT: When a user uploads a CSV file to the conversation, Claude can only see the filename
    but CANNOT access the content. This function searches for the file on the user's local system
    and processes the local file.
    
    Args:
        file_path: Name of the CSV file to look for in local system
        
    Returns:
        Dict with parsed activation data from the LOCAL file
    """
    file_path = params.get("file_path")
    
    if not file_path:
        return {
            "isError": True,
            "content": [{"type": "text", "text": "No file path provided"}]
        }
    
    # Check if the file exists
    if not os.path.isfile(file_path):
        return {
            "isError": True,
            "content": [{"type": "text", "text": f"File not found: {file_path}. Please make sure the file exists."}]
        }
    
    try:
        # Read the CSV file
        with open(file_path, 'r', encoding='utf-8') as f:
            csv_content = f.read()
        
        # Parse the CSV content
        return parse_activation_csv(csv_content)
    except Exception as e:
        return {
            "isError": True,
            "content": [{"type": "text", "text": f"Error reading or parsing CSV file: {str(e)}"}]
        }

def processUploadedCsv(params: dict) -> dict:
    """Process any CSV file based on filename from an uploaded file.
    
    IMPORTANT: When a user uploads a CSV file to the conversation, Claude can only see the filename
    but CANNOT access the content. This function searches for the file on the user's local system
    and processes the local file.
    
    Args:
        file_path: Name of the CSV file to look for in local system
        
    Returns:
        Dict with parsed CSV data from the LOCAL file
    """
    file_path = params.get("file_path")
    
    if not file_path:
        return {
            "isError": True,
            "content": [{"type": "text", "text": "No file path provided"}]
        }
    
    # Check if the file exists
    if not os.path.isfile(file_path):
        return {
            "isError": True,
            "content": [{"type": "text", "text": f"File not found: {file_path}. Please make sure the file exists."}]
        }
    
    try:
        # Read the CSV file
        with open(file_path, 'r', encoding='utf-8') as f:
            csv_content = f.read()
        
        # Parse the CSV with csv module
        import csv
        from io import StringIO
        
        reader = csv.reader(StringIO(csv_content))
        headers = next(reader, [])
        rows = list(reader)
        
        return {
            "success": True,
            "headers": headers,
            "row_count": len(rows),
            "preview": rows[:10],  # First 10 rows for preview
            "raw_csv": csv_content
        }
    except Exception as e:
        return {
            "isError": True,
            "content": [{"type": "text", "text": f"Error reading or parsing CSV file: {str(e)}"}]
        }

# Agent Management Functions
def listAgents(params: dict) -> dict:
    """List all agents for the CallHub account.
    
    Optional parameters:
    - account: The CallHub account name to use (default: 'default')
    - include_pending: Set to true to include pending agents (default: false)
    - page: Can be either a page number or a full 'next' URL from previous response
    
    IMPORTANT: The 'include_pending' parameter only includes agents in certain states - it DOES NOT 
    include newly created agents awaiting email verification. Those pending agents must be managed 
    using the exportAgentActivationUrls workflow.
    
    Note about pagination:
    The CallHub API returns paginated results with a 'next' field containing the URL
    for the next page of results. To retrieve all agents, you'll need to:
    1. Make an initial call to listAgents()
    2. If the 'next' field is present, make another call with page=next_url
    3. Repeat until 'next' is null
    
    Example:
    ```
    all_agents = []
    response = listAgents({"account": "my_account"})
    all_agents.extend(response["results"])
    
    while response.get("next"):
        response = listAgents({"account": "my_account", "page": response["next"]})
        all_agents.extend(response["results"])
    ```
    """
    # Support both account and accountName parameters for backward compatibility
    account = params.get("account")
    if not account:
        account = params.get("accountName")
    
    # Build the parameters to pass to list_agents
    agent_params = {
        "accountName": account,
        "include_pending": params.get("include_pending", False),
        "page": params.get("page")
    }
    
    return list_agents(agent_params)

def getAgent(params: dict) -> dict:
    """Get details for a specific agent by ID."""
    return get_agent(params)

def createAgent(params: dict) -> dict:
    """Create a new agent.
    
    Required fields:
    - email: Email address for the agent
    - username: Username for the agent
    - team: Team NAME for the agent's team (string name, not ID)
    
    IMPORTANT: Only these three fields are supported. Including additional fields
    like first_name or last_name will cause the API to reject the request.
    
    If you provide a team ID instead of name, the system will attempt to look up
    the corresponding team name, but it's better to provide the name directly.
    
    IMPORTANT: Newly created agents exist in a 'pending' state and will NOT be visible through 
    the standard listAgents API even with include_pending=true. To manage pending agent activation, 
    use exportAgentActivationUrls or getAgentActivationExportUrl followed by the activation functions workflow.
    
    The agent will receive a verification email. Once they verify their account,
    they will be assigned an owner and can make calls. Agents set their own
    password through the verification process.
    """
    return create_agent(params)

def deleteAgent(params: dict) -> dict:
    """Delete an agent by ID."""
    return delete_agent(params)

def getLiveAgents(params: dict) -> dict:
    """Get a list of all agents currently connected to any campaign."""
    return get_live_agents(params)


# DNC (Do Not Call) Contact Functions
def createDncContact(params: dict) -> dict:
    """Create a new DNC contact with the specified phone number.
    
    Args:
        account (str, optional): The CallHub account name to use. Defaults to 'default'.
        dnc (str, required): URL of the DNC list that the phone number belongs to.
                             Format: 'https://api.callhub.io/v1/dnc_lists/{id}/'
        phone_number (str, required): Phone number of the contact in E.164 format.
        category (int, optional): 1 for call opt-out only, 2 for text opt-out only,
                                 3 for both call and text opt-out. Defaults to 3.
    """
    return create_dnc_contact(**params)

def listDncContacts(params: dict) -> dict:
    """Retrieve a list of DNC contacts with optional pagination."""
    return list_dnc_contacts(**params)

def updateDncContact(params: dict) -> dict:
    """Update an existing DNC contact by ID.
    
    Args:
        account (str, optional): The CallHub account name to use. Defaults to 'default'.
        contactId (str, required): The ID of the DNC contact to update.
        dnc (str, required): URL of the DNC list that the contact belongs to.
                           Format: 'https://api.callhub.io/v1/dnc_lists/{id}/'
        phone_number (str, required): Phone number of the contact in E.164 format.
        
    Note:
        Both 'dnc' and 'phone_number' fields are required by the CallHub API.
    """
    return update_dnc_contact(**params)

def deleteDncContact(params: dict) -> dict:
    """Delete a DNC contact by ID."""
    return delete_dnc_contact(**params)


# DNC (Do Not Call) List Functions
def createDncList(params: dict) -> dict:
    """Create a new DNC list."""
    return create_dnc_list(**params)

def listDncLists(params: dict) -> dict:
    """Retrieve a list of DNC lists with optional pagination."""
    return list_dnc_lists(**params)

def updateDncList(params: dict) -> dict:
    """Update an existing DNC list by ID."""
    return update_dnc_list(**params)

def deleteDncList(params: dict) -> dict:
    """Delete a DNC list by ID."""
    return delete_dnc_list(**params)
