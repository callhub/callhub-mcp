"""Tool wrappers for User and Credit operations."""
from typing import Optional
from callhub.users import (
    list_users,
    get_credit_usage,
    share_credits,
    get_user_details,
)
from callhub.agents import (
    get_agent_key,
    get_agent_status,
)


def register(server):
    @server.tool(name="getUsers", description="Retrieve a list of all users in the CallHub account.")
    def get_users_tool(
        account: Optional[str] = None
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account

            return list_users(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getCreditUsage", description="Retrieve credit usage details for the CallHub account.")
    def get_credit_usage_tool(
        account: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        generate_csv: Optional[bool] = False,
        campaign_type: Optional[int] = None
    ) -> dict:
        """Campaign Type Mapping: SMS Broadcast=1, Text2Join=3, P2P=4, Call Centre=5, Voice Broadcast=6"""
        try:
            params = {}
            if account:
                params["accountName"] = account
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date
            if generate_csv is not None: # Pass boolean directly
                params["generate_csv"] = generate_csv
            if campaign_type is not None:
                params["campaign_type"] = campaign_type

            return get_credit_usage(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getUserDetails", description="Get details of the currently authenticated user.")
    def get_user_details_tool(
        account: Optional[str] = None,
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            return get_user_details(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="shareCredits", description="Share credits from an enterprise account to a subaccount.")
    def share_credits_tool(
        account: Optional[str] = None,
        subaccount: str = None,
        transfer_amount: int = None,
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if subaccount:
                params["subaccount"] = subaccount
            if transfer_amount is not None:
                params["transfer_amount"] = transfer_amount
            return share_credits(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getAgentKey", description="Get an auth token (agent key) for an agent by username and password.")
    def get_agent_key_tool(
        account: Optional[str] = None,
        username: str = None,
        password: str = None,
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if username:
                params["username"] = username
            if password:
                params["password"] = password
            return get_agent_key(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getAgentStatus", description="Get the current status of agents in the CallHub account.")
    def get_agent_status_tool(
        account: Optional[str] = None,
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            return get_agent_status(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}
