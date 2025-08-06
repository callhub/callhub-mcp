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

from callhub.account_management import (add_account , update_account , delete_account)
from callhub.agents import (list_agents)
# Import from our new modules
from callhub.auth import (load_all_credentials)


# Import new activation tools from mcp_tools module

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





