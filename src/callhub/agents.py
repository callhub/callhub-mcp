# agents.py
"""
Agent management functions for CallHub API.
"""

import sys
from typing import Dict, Any
from .client import McpApiClient
from .constants import ENDPOINTS

def list_agents(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    List all agents for the CallHub account.
    
    Args:
        params (dict): Dictionary containing:
            - accountName (optional): The CallHub account name to use
            - include_pending (optional): Include pending agents (default: False)
            - page (optional): Page number for pagination
    
    Returns:
        Dict: Response from the API with agent list
    """
    client = McpApiClient(params.get("accountName"))
    
    query_params = {}
    if params.get("include_pending"):
        query_params["include_pending"] = "true"
    
    page = params.get("page")
    if page:
        # Debug log for pagination
        sys.stderr.write(f"[callhub] list_agents called with page parameter: {page}\n")
        query_params["page"] = page
        
    return client.call(ENDPOINTS.AGENTS, "GET", query=query_params)

def get_agent(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get details for a specific agent by ID.
    
    Args:
        params (dict): Dictionary containing:
            - accountName (optional): The CallHub account name to use
            - agentId (required): The ID of the agent to retrieve
    
    Returns:
        Dict: Response from the API with agent details
    """
    agent_id = params.get("agentId")
    
    if not agent_id:
        return {"isError": True, "content": [{"type": "text", "text": "'agentId' is required"}]}
    
    client = McpApiClient(params.get("accountName"))
    return client.call(f"{ENDPOINTS.AGENTS}{agent_id}/", "GET")

def create_agent(params: Dict[str, Any]) -> Dict[str, Any]:
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
    
    client = McpApiClient(account_name)
    
    # If team looks like an ID, convert it to a team name
    if team and str(team).isdigit():
        from .teams import list_teams
        try:
            # If team is an ID, convert to name
            teams_response = list_teams({"accountName": account_name})
            if not teams_response.get("isError"):
                teams = teams_response.get("results", [])
                team_id_str = str(team)
                for t in teams:
                    if str(t.get("id")) == team_id_str:
                        # Use the name instead of the ID
                        team = t.get("name")
                        sys.stderr.write(f"[callhub] Converted team ID {team_id_str} to name '{team}'\n")
                        break
        except Exception as e:
            sys.stderr.write(f"[callhub] Error converting team ID to name: {str(e)}\n")
            pass

    # ONLY include required fields - the API rejects requests with additional fields
    payload = {
        "username": username,
        "email": email,
        "team": team
    }
    
    # Print the payload for debugging
    sys.stderr.write(f"[callhub] Creating agent with payload: {payload}\n")
    return client.call(ENDPOINTS.AGENTS, "POST", body=payload)

def get_live_agents(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get a list of all agents currently connected to any campaign.
    
    Args:
        params (dict): Dictionary containing:
            - accountName (optional): The CallHub account name to use
    
    Returns:
        Dict: Response from the API with the list of connected agents
    """
    client = McpApiClient(params.get("accountName"))
    return client.call(ENDPOINTS.CAMPAIGN_AGENT_LIVE, "GET")