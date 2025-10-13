# teams.py
"""
Team management functions for CallHub API.
"""

import sys
from typing import Dict, Any, Optional
from .client import McpApiClient

def list_teams(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    List all teams in the CallHub account.
    
    Args:
        params (dict): Dictionary containing:
            - accountName (optional): The CallHub account name to use
    
    Returns:
        Dict: Response from the API with team list
    """
    client = McpApiClient(params.get("accountName"))
    return client.call("/v1/teams/", "GET")

def get_team(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get details for a specific team by ID.
    
    Args:
        params (dict): Dictionary containing:
            - accountName (optional): The CallHub account name to use
            - teamId (required): The ID of the team to retrieve
    
    Returns:
        Dict: Response from the API with team details
    """
    team_id = params.get("teamId")
    
    if not team_id:
        return {"isError": True, "content": [{"type": "text", "text": "'teamId' is required"}]}
    
    client = McpApiClient(params.get("accountName"))
    return client.call(f"/v1/teams/{team_id}/", "GET")

def create_team(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new team.
    
    Args:
        params (dict): Dictionary containing:
            - accountName (optional): The CallHub account name to use
            - name (required): Name of the team to create
    
    Returns:
        Dict: Response from the API with the created team details
    """
    name = params.get("name")
    
    # Validate required fields
    if not name:
        return {"isError": True, "content": [{"type": "text", "text": "Team 'name' is required"}]}
    
    client = McpApiClient(params.get("accountName"))
    payload = {"name": name}
    return client.call("/v1/teams/", "POST", body=payload)

def update_team(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a team's name by ID.
    
    Args:
        params (dict): Dictionary containing:
            - accountName (optional): The CallHub account name to use
            - teamId (required): The ID of the team to update
            - name (required): New name for the team
    
    Returns:
        Dict: Response from the API with the updated team details
    """
    team_id = params.get("teamId")
    name = params.get("name")
    
    # Validate required fields
    if not team_id:
        return {"isError": True, "content": [{"type": "text", "text": "'teamId' is required"}]}
    
    if not name:
        return {"isError": True, "content": [{"type": "text", "text": "Team 'name' is required"}]}
    
    client = McpApiClient(params.get("accountName"))
    payload = {"name": name}
    return client.call(f"/v1/teams/{team_id}/", "PUT", body=payload)

def delete_team(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Delete a team by ID.
    
    Args:
        params (dict): Dictionary containing:
            - accountName (optional): The CallHub account name to use
            - teamId (required): The ID of the team to delete
    
    Returns:
        Dict: Response indicating success or failure
        
    Notes:
        This endpoint will unassign all agents associated with the team.
    """
    account_name = params.get("accountName")
    team_id = params.get("teamId")
    
    if not team_id:
        return {"isError": True, "content": [{"type": "text", "text": "'teamId' is required"}]}
    
    client = McpApiClient(account_name)
    
    agents_response = get_team_agents({"accountName": account_name, "teamId": team_id})
    agent_count = 0
    if not agents_response.get("isError"):
        agent_count = len(agents_response.get("results", []))
        # If the team has agents, provide a warning but proceed with deletion
        if agent_count > 0:
            sys.stderr.write(f"[callhub] Warning: Team {team_id} has {agent_count} agents that will be unassigned\n")

    delete_response = client.call(f"/v1/teams/{team_id}/", "DELETE")
    
    # If deletion was successful and there were agents, add warning to response
    if not delete_response.get("isError") and agent_count > 0:
        if "content" not in delete_response:
            delete_response["content"] = []
        delete_response["content"].append({
            "type": "text", 
            "text": f"Warning: {agent_count} agents have been unassigned from this team"
        })
    
    return delete_response

def get_team_agents(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get a list of all agents assigned to a specific team.
    
    Args:
        params (dict): Dictionary containing:
            - accountName (optional): The CallHub account name to use
            - teamId (required): The ID of the team
    
    Returns:
        Dict: Response from the API with the list of agents in the team
    """
    team_id = params.get("teamId")
    
    if not team_id:
        return {"isError": True, "content": [{"type": "text", "text": "'teamId' is required"}]}
    
    client = McpApiClient(params.get("accountName"))
    return client.call(f"/v1/teams/{team_id}/agents/", "GET")

def get_team_agent_details(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get details for a specific agent in a team.
    
    Args:
        params (dict): Dictionary containing:
            - accountName (optional): The CallHub account name to use
            - teamId (required): The ID of the team
            - agentId (required): The ID of the agent
    
    Returns:
        Dict: Response from the API with the agent details
    """
    team_id = params.get("teamId")
    agent_id = params.get("agentId")
    
    # Validate required fields
    if not team_id:
        return {"isError": True, "content": [{"type": "text", "text": "'teamId' is required"}]}
    if not agent_id:
        return {"isError": True, "content": [{"type": "text", "text": "'agentId' is required"}]}
    
    client = McpApiClient(params.get("accountName"))
    return client.call(f"/v1/teams/{team_id}/agents/{agent_id}/", "GET")

def add_agents_to_team(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add one or more agents to a team.
    
    Args:
        params (dict): Dictionary containing:
            - accountName (optional): The CallHub account name to use
            - teamId (required): The ID of the team
            - agentIds (required): List of agent IDs to add to the team
    
    Returns:
        Dict: Response indicating success or failure
    """
    team_id = params.get("teamId")
    agent_ids = params.get("agentIds")
    
    # Validate required fields
    if not team_id:
        return {"isError": True, "content": [{"type": "text", "text": "'teamId' is required"}]}
    if not agent_ids or not isinstance(agent_ids, list) or len(agent_ids) == 0:
        return {"isError": True, "content": [{"type": "text", "text": "'agentIds' must be a non-empty list of agent IDs"}]}
    
    client = McpApiClient(params.get("accountName"))
    payload = {"agents": [int(agent_id) for agent_id in agent_ids]}
    return client.call(f"/v1/teams/{team_id}/agents/", "POST", body=payload)

def remove_agents_from_team(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove one or more agents from a team.
    
    Args:
        params (dict): Dictionary containing:
            - accountName (optional): The CallHub account name to use
            - teamId (required): The ID of the team
            - agentIds (required): List of agent IDs to remove from the team
    
    Returns:
        Dict: Response indicating success or failure
    """
    team_id = params.get("teamId")
    agent_ids = params.get("agentIds")
    
    # Validate required fields
    if not team_id:
        return {"isError": True, "content": [{"type": "text", "text": "'teamId' is required"}]}
    if not agent_ids or not isinstance(agent_ids, list) or len(agent_ids) == 0:
        return {"isError": True, "content": [{"type": "text", "text": "'agentIds' must be a non-empty list of agent IDs"}]}
    
    client = McpApiClient(params.get("accountName"))
    payload = {"agents": [int(agent_id) for agent_id in agent_ids]}
    return client.call(f"/v1/teams/{team_id}/agents/", "DELETE", body=payload)

# Team validation helper function (for agent creation validation)
def validate_team_exists(account_name: Optional[str], team_input: str) -> Dict[str, Any]:
    """
    Validate that a team exists by name or ID before creating an agent.
    
    Args:
        account_name: The CallHub account name to use
        team_input: Name or ID of the team to validate
        
    Returns:
        Dict: Response indicating whether the team exists
    """
    # First, get all teams
    teams_response = list_teams({"accountName": account_name})
    
    # Check if the API call failed
    if teams_response.get("isError"):
        return teams_response
    
    # Extract team objects from the response
    teams = teams_response.get("results", [])
    
    # Check if team_input is numeric (likely an ID)
    is_id_format = team_input.isdigit() # or (team_input.startswith("2") or team_input.startswith("3")) # Original logic
    
    # Look for a team with a matching name or ID
    for team in teams:
        # Check for team ID match
        if is_id_format and (str(team.get("id")) == team_input): # or team.get("pk_str") == team_input): # Original logic
            return {
                "exists": True,
                "teamId": team.get("id"),
                "team": team
            }
        # Check for team name match
        elif not is_id_format and team.get("name") == team_input:
            return {
                "exists": True,
                "teamId": team.get("id"),
                "team": team
            }
    
    # If no team was found with that name or ID
    if is_id_format:
        return {
            "exists": False,
            "message": f"Team with ID '{team_input}' does not exist. Please create a team first or use an existing team ID."
        }
    else:
        return {
            "exists": False,
            "message": f"Team with name '{team_input}' does not exist. Please create it first or use an existing team."
        }
