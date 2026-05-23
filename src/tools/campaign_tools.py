"""Tool wrappers for Call Center Campaign operations."""
from typing import Optional, List, Dict
from callhub.campaigns import (
    list_call_center_campaigns,
    update_call_center_campaign,
    create_call_center_campaign,
    delete_call_center_campaign,
    duplicate_power_campaign,
    add_agents_to_power_campaign,
    export_power_campaign,
    exportCampaignData,
    getCampaignStatsAdvanced,
    get_export_job_result,
)


def register(server):
    @server.tool(name="listCallCenterCampaigns", description="List all call center campaigns with optional pagination.")
    def list_call_center_campaigns_tool(
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

            return list_call_center_campaigns(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="updateCallCenterCampaign", description="Update a call center campaign. Status is required; name is optional. Valid status values: 'pause', 'resume', 'stop', 'restart'.")
    def update_call_center_campaign_tool(
        account: Optional[str] = None,
        campaignId: str = None,
        status: str = None,
        name: Optional[str] = None
    ) -> dict:
        try:
            # Validate required parameters
            if not campaignId:
                return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}

            if not status or status not in ["pause", "resume", "stop", "restart"]:
                return {
                    "isError": True,
                    "content": [{"type": "text", "text": "Valid 'status' is required: pause, resume, stop, or restart"}]
                }

            params = {
                "campaignId": campaignId,
                "status": status
            }
            if account:
                params["accountName"] = account
            if name:
                params["name"] = name

            return update_call_center_campaign(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="createCallCenterCampaign", description="[Extended API] Create a new call center campaign with a complex script structure.")
    def create_call_center_campaign_tool(
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

            return create_call_center_campaign(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="deleteCallCenterCampaign", description="Delete a call center campaign by ID.")
    def delete_call_center_campaign_tool(
        account: Optional[str] = None,
        campaignId: str = None
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if campaignId:
                params["campaignId"] = campaignId
            return delete_call_center_campaign(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="duplicatePowerCampaign", description="[Extended API] Duplicates a PowerCampaign with specified parameters.")
    def duplicate_power_campaign_tool(
        campaign_id: int,
        phonebook_ids: List[int],
        assign_all_agents: bool,
        account: Optional[str] = None,
        target_account: Optional[str] = None,
        name: Optional[str] = None,
        callerid: Optional[Dict] = None,
        callerid_block: Optional[Dict] = None,
        textid: Optional[Dict] = None,
        dialin: Optional[Dict] = None
    ) -> dict:
        try:
            params = {
                "campaign_id": campaign_id,
                "phonebook_ids": phonebook_ids,
                "assign_all_agents": assign_all_agents,
            }
            if account:
                params["accountName"] = account
            if target_account:
                params["target_account"] = target_account
            if name:
                params["name"] = name
            if callerid:
                params["callerid"] = callerid
            if callerid_block:
                params["callerid_block"] = callerid_block
            if textid:
                params["textid"] = textid
            if dialin:
                params["dialin"] = dialin

            # This function is expected to be in callhub/utils.py
            return duplicate_power_campaign(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="addAgentsToPowerCampaign", description="[Extended API] Add agents to a power campaign.")
    def add_agents_to_power_campaign_tool(
        account: Optional[str] = None, campaign_id: int = None, agent_ids: list = None
    ) -> dict:
        try:
            params = {"campaignId": campaign_id, "agentIds": agent_ids}
            if account:
                params["accountName"] = account
            return add_agents_to_power_campaign(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="exportPowerCampaign", description="[Extended API] Export a power campaign.")
    def export_power_campaign_tool(
        account: Optional[str] = None, campaign_id: int = None
    ) -> dict:
        try:
            params = {"campaignId": campaign_id}
            if account:
                params["accountName"] = account
            return export_power_campaign(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="exportCampaignData", description="[Extended API] Export campaign data in specified format.")
    def export_campaign_data_tool(
        account: Optional[str] = None,
        campaignId: str = None,
        format: str = "csv"
    ) -> dict:
        try:
            if not campaignId:
                return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}

            params = {"campaignId": campaignId, "format": format}
            if account:
                params["accountName"] = account

            return exportCampaignData(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getCampaignStatsAdvanced", description="[Extended API] Get enhanced campaign statistics.")
    def get_campaign_stats_advanced_tool(
        account: Optional[str] = None,
        campaignId: str = None,
        includeDetails: bool = True
    ) -> dict:
        try:
            if not campaignId:
                return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}

            params = {"campaignId": campaignId, "includeDetails": includeDetails}
            if account:
                params["accountName"] = account

            return getCampaignStatsAdvanced(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getExportJobResult", description="Get the result of an export job by job ID. Use this after initiating an export to retrieve the exported data.")
    def get_export_job_result_tool(
        account: Optional[str] = None,
        job_id: str = None,
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if job_id:
                params["job_id"] = job_id
            return get_export_job_result(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}
