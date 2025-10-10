# agents.py
"""
Agent management functions for CallHub API.
"""

import json
import sys
from typing import Dict, List, Union, Optional, Any

from .auth import get_account_config
from .utils import build_url, api_call, get_auth_headers, parse_input_fields

def list_agents(params: Dict) -> Dict:
    """
    List all agents for the CallHub account.
    
    Args:
        params (dict): Dictionary containing:
            - accountName (optional): The CallHub account name to use
            - include_pending (optional): Include pending agents (default: False)
            - page (optional): Page number for pagination, or full URL from 'next' field
    
    Returns:
        Dict: Response from the API with agent list
    """
    account_name = params.get("accountName")
    include_pending = params.get("include_pending", False)
    page = params.get("page")
    
    # Debug log for pagination
    sys.stderr.write(f"[callhub] list_agents called with page parameter: {page}\n")
    
    account, api_key, base_url = get_account_config(account_name)
    
    # Check if page is a full URL (from 'next' field)
    if page and isinstance(page, str) and page.startswith(("http://", "https://")):
        url = page
        sys.stderr.write(f"[callhub] Using provided full URL for pagination: {url}\n")
        # When using full URL, make sure we don't also send page as a query parameter
        query_params = {}
        # But still include include_pending if requested
        if include_pending:
            query_params["include_pending"] = "true"
    else:
        url = build_url(base_url, "/v1/agents/")
        sys.stderr.write(f"[callhub] Using built URL: {url}\n")
        
        # Try to add parameters to include pending agents if requested
        query_params = {}
        if include_pending:
            query_params["include_pending"] = "true"
        
        # Add page parameter only if it's a number
        if page and isinstance(page, (int, str)) and not page.startswith(("http://", "https://")):
            try:
                query_params["page"] = str(int(page))  # Convert to int then back to str to validate
                sys.stderr.write(f"[callhub] Added page parameter to query: {query_params['page']}\n")
            except (ValueError, TypeError):
                sys.stderr.write(f"[callhub] Invalid page parameter, ignoring: {page}\n")
    
    headers = get_auth_headers(api_key)
    sys.stderr.write(f"[callhub] Making request with params: {query_params}\n")
    
    response = api_call("GET", url, headers, params=query_params)
    
    # Debug log for response pagination
    if "next" in response:
        sys.stderr.write(f"[callhub] Response includes next URL: {response['next']}\n")
    else:
        sys.stderr.write("[callhub] Response does not include next URL\n")
    
    return response

def get_agent(params: Dict) -> Dict:
    """
    Get details for a specific agent by ID.
    
    Args:
        params (dict): Dictionary containing:
            - accountName (optional): The CallHub account name to use
            - agentId (required): The ID of the agent to retrieve
    
    Returns:
        Dict: Response from the API with agent details
    """
    account_name = params.get("accountName")
    agent_id = params.get("agentId")
    
    if not agent_id:
        return {"isError": True, "content": [{"type": "text", "text": "'agentId' is required"}]}
    
    account, api_key, base_url = get_account_config(account_name)
    
    url = build_url(base_url, "/v1/agents/{}/", agent_id)
    headers = get_auth_headers(api_key)
    
    return api_call("GET", url, headers)

def create_agent(params: Dict) -> Dict:
    """
    Create a new agent.
    
    Args:
        params (dict): Dictionary containing:
            - accountName (optional): The CallHub account name to use
            - email (required): Email address for the agent
            - username (required): Username for the agent
            - team (required): Team NAME (not ID) for the agent's team
            
    Notes:
        - The agent will receive a verification email
        - Once they verify their account, an owner is assigned and they can make calls
        - Agents set their own password through the verification process
        - IMPORTANT: Only send username, email, and team - other fields will cause an error
        - IMPORTANT: The 'team' parameter must be the team NAME (as a string), not the ID
    
    Returns:
        Dict: Response from the API with the created agent details
    """
    account_name = params.get("accountName")
    email = params.get("email")
    username = params.get("username")
    team = params.get("team")
    
    # Validate required fields
    required_fields = {"email": email, "username": username, "team": team}
    missing_fields = [field for field, value in required_fields.items() if not value]
    
    if missing_fields:
        return {
            "isError": True, 
            "content": [{"type": "text", "text": f"Missing required fields: {', '.join(missing_fields)}"}]
        }
    
    account, api_key, base_url = get_account_config(account_name)
    
    url = build_url(base_url, "/v1/agents/")
    headers = get_auth_headers(api_key)
    
    # If team looks like an ID, convert it to a team name
    if team and (str(team).isdigit() or (str(team).startswith("2") or str(team).startswith("3"))):
        try:
            # If team is an ID, convert to name
            from .teams import list_teams
            teams_response = list_teams({"accountName": account_name})
            if not teams_response.get("isError"):
                teams = teams_response.get("results", [])
                team_id = str(team)  # Store the ID for comparison
                for t in teams:
                    if str(t.get("id")) == team_id or t.get("pk_str") == team_id:
                        # Use the name instead of the ID
                        team = t.get("name")
                        sys.stderr.write(f"[callhub] Converted team ID {team_id} to name '{team}'\n")
                        break
        except Exception as e:
            sys.stderr.write(f"[callhub] Error converting team ID to name: {str(e)}\n")
    
    # ONLY include required fields - the API rejects requests with additional fields
    payload = {
        "username": username,
        "email": email,
        "team": team
    }
    
    # Print the payload for debugging
    sys.stderr.write(f"[callhub] Creating agent with payload: {payload}\n")
    
    return api_call("POST", url, headers, json_data=payload)

def get_live_agents(params: Dict) -> Dict:
    """
    Get a list of all agents currently connected to any campaign.
    
    Args:
        params (dict): Dictionary containing:
            - accountName (optional): The CallHub account name to use
    
    Returns:
        Dict: Response from the API with the list of connected agents
    """
    account_name = params.get("accountName")
    account, api_key, base_url = get_account_config(account_name)
    
    url = build_url(base_url, "/v2/campaign/agent/live/")
    headers = get_auth_headers(api_key)
    
    return api_call("GET", url, headers)
