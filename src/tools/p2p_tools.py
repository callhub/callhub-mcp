"""Tool wrappers for P2P Campaign operations."""
from typing import Optional, List
from callhub.p2p_campaigns import (
    list_p2p_campaigns,
    update_p2p_campaign,
    get_p2p_campaign_agents,
    add_agents_to_p2p_campaign,
    reassign_p2p_agents,
    get_p2p_surveys,
    create_p2p_campaign,
    duplicate_p2p_campaign,
    get_collective_texting_questions,
    get_collective_texting_saved_replies,
    get_p2p_campaign_schema,
)


def register(server):
    @server.tool(name="listP2pCampaigns", description="List all P2P campaigns with optional pagination.")
    def list_p2p_campaigns_tool(
        account: Optional[str] = None,
        page: Optional[int] = None,
        pageSize: Optional[int] = None
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if page is not None:
                params["page"] = page
            if pageSize is not None:
                params["pageSize"] = pageSize

            return list_p2p_campaigns(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="updateP2pCampaign", description="[Extended API] Update a P2P campaign's status. Valid values: 'start', 'pause', 'abort', 'end' or 1-4 numerically.")
    def update_p2p_campaign_tool(
        account: Optional[str] = None,
        campaignId: str = None,
        status: str = None # Kept as str, conversion in module
    ) -> dict:
        try:
            # Validate required parameters
            if not campaignId:
                return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}

            if not status: # Basic check, detailed validation in module
                return {
                    "isError": True,
                    "content": [{"type": "text", "text": "Valid 'status' is required: start, pause, abort, end, or 1-4 numerically"}]
                }

            params = {
                "campaignId": campaignId,
                "status": status
            }
            if account:
                params["accountName"] = account

            return update_p2p_campaign(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="createP2PCampaign", description="[Extended API] Create a new P2P campaign with a complex script structure.")
    def create_p2p_campaign_tool(
        account: Optional[str] = None,
        campaign_data: dict = None
    ) -> dict:
        try:
            # Validate required parameters
            if not campaign_data:
                return {"isError": True, "content": [{"type": "text", "text": "'campaign_data' is required."}]}

            params = {"campaign_data": campaign_data}
            if account:
                params["accountName"] = account

            return create_p2p_campaign(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="duplicateP2pCampaign", description="[Extended API] Duplicate a P2P campaign.")
    def duplicate_p2p_campaign_tool(
        account: Optional[str] = None, campaign_id: int = None
    ) -> dict:
        try:
            params = {"campaignId": campaign_id}
            if account:
                params["accountName"] = account
            return duplicate_p2p_campaign(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getP2pCampaignAgents", description="[Extended API] Get agents for a P2P campaign.")
    def get_p2p_campaign_agents_tool(
        account: Optional[str] = None,
        campaignId: str = None
    ) -> dict:
        try:
            if not campaignId:
                return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}

            params = {"campaignId": campaignId}
            if account:
                params["accountName"] = account

            return get_p2p_campaign_agents(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="addAgentsToP2pCampaign", description="[Extended API] Add agents to a P2P campaign.")
    def add_agents_to_p2p_campaign_tool(
        account: Optional[str] = None,
        campaignId: str = None,
        agentIds: List[str] = None
    ) -> dict:
        try:
            if not campaignId:
                return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}
            if not agentIds:
                return {"isError": True, "content": [{"type": "text", "text": "'agentIds' is required."}]}

            params = {"campaignId": campaignId, "agentIds": agentIds}
            if account:
                params["accountName"] = account

            return add_agents_to_p2p_campaign(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="reassignP2pAgents", description="[Extended API] Reassign agents in a P2P campaign.")
    def reassign_p2p_agents_tool(
        account: Optional[str] = None,
        campaignId: str = None,
        reassignData: dict = None
    ) -> dict:
        try:
            if not campaignId:
                return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}

            params = {"campaignId": campaignId, "reassignData": reassignData or {}}
            if account:
                params["accountName"] = account

            return reassign_p2p_agents(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getP2pSurveys", description="[Extended API] Get surveys for a P2P campaign.")
    def get_p2p_surveys_tool(
        account: Optional[str] = None,
        campaignId: Optional[str] = None
    ) -> dict:
        try:
            params = {}
            if campaignId:
                params["campaignId"] = campaignId
            if account:
                params["accountName"] = account

            return get_p2p_surveys(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getCollectiveTextingQuestions", description="Get questions for a Collective Texting (P2P) campaign.")
    def get_collective_texting_questions_tool(
        account: Optional[str] = None,
        campaign_id: str = None,
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if campaign_id:
                params["campaign_id"] = campaign_id
            return get_collective_texting_questions(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getCollectiveTextingSavedReplies", description="Get saved replies for a Collective Texting (P2P) campaign.")
    def get_collective_texting_saved_replies_tool(
        account: Optional[str] = None,
        campaign_id: str = None,
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if campaign_id:
                params["campaign_id"] = campaign_id
            return get_collective_texting_saved_replies(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getP2pCampaignSchema", description="Get the JSON schema for P2P campaign API resources.")
    def get_p2p_campaign_schema_tool(
        account: Optional[str] = None,
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            return get_p2p_campaign_schema(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}
