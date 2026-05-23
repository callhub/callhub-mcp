"""Tool wrappers for Team operations."""
from typing import Optional, List
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
)


def register(server):
    @server.tool(name="listTeams", description="List all teams in the CallHub account.")
    def list_teams_tool(account: Optional[str] = None) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            return list_teams(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getTeam", description="Get details for a specific team by ID.")
    def get_team_tool(account: Optional[str] = None, teamId: Optional[str] = None) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if teamId:
                params["teamId"] = teamId
            return get_team(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="createTeam", description="Create a new team.")
    def create_team_tool(account: Optional[str] = None, name: str = None) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if name:
                params["name"] = name
            return create_team(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="updateTeam", description="Update a team's name.")
    def update_team_tool(account: Optional[str] = None, teamId: str = None, name: str = None) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if teamId:
                params["teamId"] = teamId
            if name:
                params["name"] = name
            return update_team(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="deleteTeam", description="Delete a team by ID. All agents associated with the team will be unassigned.")
    def delete_team_tool(account: Optional[str] = None, teamId: str = None) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if teamId:
                params["teamId"] = teamId
            return delete_team(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getTeamAgents", description="Get a list of all agents assigned to a specific team.")
    def get_team_agents_tool(account: Optional[str] = None, teamId: str = None) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if teamId:
                params["teamId"] = teamId
            return get_team_agents(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getTeamAgentDetails", description="Get details for a specific agent in a team.")
    def get_team_agent_details_tool(account: Optional[str] = None, teamId: str = None, agentId: str = None) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if teamId:
                params["teamId"] = teamId
            if agentId:
                params["agentId"] = agentId
            return get_team_agent_details(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="addAgentsToTeam", description="Add one or more agents to a team.")
    def add_agents_to_team_tool(account: Optional[str] = None, teamId: str = None, agentIds: List[str] = None) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if teamId:
                params["teamId"] = teamId
            if agentIds:
                params["agentIds"] = agentIds # Should be a list of IDs
            return add_agents_to_team(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="removeAgentsFromTeam", description="Remove one or more agents from a team.")
    def remove_agents_from_team_tool(account: Optional[str] = None, teamId: str = None, agentIds: List[str] = None) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if teamId:
                params["teamId"] = teamId
            if agentIds:
                params["agentIds"] = agentIds # Should be a list of IDs
            return remove_agents_from_team(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}
