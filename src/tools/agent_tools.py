"""Tool wrappers for Agent operations."""
from typing import Optional, Union
from tools_callhub import fetch_agents
from callhub.agents import (
    list_agents,
    get_agent,
    create_agent,
    get_live_agents,
)
from callhub.teams import validate_team_exists


def register(server):
    @server.tool(name="fetchAgents", description="Retrieve current agents via CallHub API. Optional 'account'.")
    def fetch_agents_tool(account: Optional[str] = None) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            return fetch_agents(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="listAgents", description="List all agents for the CallHub account. Accepts optional 'page' (number or full URL) and 'include_pending' (boolean) arguments. IMPORTANT: The 'include_pending' parameter only includes agents in certain states - it DOES NOT include newly created agents awaiting email verification. Those pending agents must be managed using the exportAgentActivationUrls workflow.")
    def list_agents_tool(account: Optional[str] = None, page: Optional[Union[str, int]] = None, include_pending: Optional[bool] = False) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account

            # Pass the page argument if it's provided
            if page is not None:
                params["page"] = page

            # Pass the include_pending argument if it's True
            if include_pending:
                params["include_pending"] = True

            # Directly call the function from callhub.agents
            return list_agents(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getAgent", description="Get details for a specific agent by ID.")
    def get_agent_tool(account: Optional[str] = None, agentId: Optional[str] = None) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if agentId:
                params["agentId"] = agentId
            return get_agent(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="createAgent", description="Create a new agent with required email, username, and team. Note: Only these three fields are supported. Team should be the team NAME. IMPORTANT: Newly created agents exist in a 'pending' state and will NOT be visible through the standard listAgents API even with include_pending=true. To manage pending agent activation, use exportAgentActivationUrls or getAgentActivationExportUrl followed by the activation functions workflow.")
    def create_agent_tool(
        account: Optional[str] = None,
        email: Optional[str] = None,
        username: Optional[str] = None,
        team: Optional[str] = None
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if email:
                params["email"] = email
            if username:
                params["username"] = username
            if team:
                params["team"] = team

            # Validate that the team exists before creating the agent
            if team:
                team_validation = validate_team_exists(account, team)
                if not team_validation.get("exists"):
                    return {
                        "isError": True,
                        "content": [
                            {"type": "text", "text": team_validation.get("message")},
                            {"type": "text", "text": "Use the createTeam tool to create this team first."}
                        ]
                    }

            return create_agent(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getLiveAgents", description="[Extended API] Get a list of all agents currently connected to any campaign.")
    def get_live_agents_tool(account: Optional[str] = None) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            return get_live_agents(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}
