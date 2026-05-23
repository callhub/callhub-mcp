"""Tool wrappers for Voice Broadcast Campaign operations."""
from typing import Optional
from callhub.vb_campaigns import (
    get_vb_campaign,
    create_vb_campaign_template,
    create_voice_broadcast_campaign,
    list_voice_broadcasts,
    delete_voice_broadcast_campaign,
    update_voice_broadcast_campaign,
    duplicate_vb_campaign,
)


def register(server):
    @server.tool(name="listVoiceBroadcastCampaigns", description="List all voice broadcast campaigns with optional pagination.")
    def list_voice_broadcast_campaigns_tool(
        account: Optional[str] = None,
        page: Optional[int] = None,
        pageSize: Optional[int] = None
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account # Corrected from params["account"] to params["accountName"]
            if page is not None:
                params["page"] = page
            if pageSize is not None:
                params["pageSize"] = pageSize

            return list_voice_broadcasts(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getVbCampaign", description="Get a voice broadcast campaign by ID.")
    def get_vb_campaign_tool(
        account: Optional[str] = None,
        campaignId: str = None
    ) -> dict:
        try:
            if not campaignId:
                return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}
            params = {"campaignId": campaignId}
            if account:
                params["accountName"] = account
            return get_vb_campaign(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="createVbCampaign", description="Create a new voice broadcast campaign.")
    def create_vb_campaign_tool(
        account: Optional[str] = None,
        campaign_data: dict = None
    ) -> dict:
        try:
            if not campaign_data:
                return {"isError": True, "content": [{"type": "text", "text": "'campaign_data' is required."}]}
            params = campaign_data.copy()
            if account:
                params["accountName"] = account
            return create_voice_broadcast_campaign(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="createVbCampaignTemplate", description="Create a new voice broadcast campaign template.")
    def create_vb_campaign_template_tool(
        account: Optional[str] = None,
        template_data: dict = None
    ) -> dict:
        try:
            if not template_data:
                return {"isError": True, "content": [{"type": "text", "text": "'template_data' is required."}]}
            params = {"template_data": template_data}
            if account:
                params["accountName"] = account
            return create_vb_campaign_template(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="duplicateVbCampaign", description="Duplicate a voice broadcast campaign.")
    def duplicate_vb_campaign_tool(
        account: Optional[str] = None, campaign_id: int = None
    ) -> dict:
        try:
            params = {"campaignId": campaign_id}
            if account:
                params["accountName"] = account
            return duplicate_vb_campaign(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="deleteVoiceBroadcastCampaign", description="Delete a voice broadcast campaign by ID.")
    def delete_voice_broadcast_campaign_tool(
        account: Optional[str] = None,
        campaignId: str = None
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if campaignId:
                params["campaignId"] = campaignId
            return delete_voice_broadcast_campaign(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="updateVoiceBroadcastCampaign", description="Update a voice broadcast campaign. Supports updating name, status, and frequency (calls per minute).")
    def update_voice_broadcast_campaign_tool(
        account: Optional[str] = None,
        campaignId: str = None,
        name: Optional[str] = None,
        status: Optional[int] = None,
        frequency: Optional[int] = None,
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if campaignId:
                params["campaignId"] = campaignId
            if name is not None:
                params["name"] = name
            if status is not None:
                params["status"] = status
            if frequency is not None:
                params["frequency"] = frequency
            return update_voice_broadcast_campaign(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}
