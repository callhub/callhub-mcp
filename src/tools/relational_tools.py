"""Tool wrappers for Relational Organizing Campaign operations."""
from typing import Optional
from callhub.relational_organizing import (
    create_relational_organizing_campaign,
    duplicate_relational_organizing_campaign,
    assign_agents_to_relational_organizing_campaign,
    update_relational_organizing_campaign,
    get_relational_organizing_campaign,
    update_relational_organizing_campaign_status,
)


def register(server):
    @server.tool(name="createRelationalCampaign", description="Create a new relational organizing campaign.")
    def create_relational_campaign_tool(
        account: Optional[str] = None,
        name: str = None,
        brief: str = None,
        phonebook_ids: list = None,
        user_tag_ids: list = None,
        default_outreach_medium: int = None,
        agent_assignment_choice: int = None,
        team_ids: list = None,
        starting_date: str = None,
        end_date: str = None,
        timezone: str = None,
        survey_id: int = None,
    ) -> dict:
        try:
            params = {
                "name": name,
                "brief": brief,
                "phonebook_ids": phonebook_ids,
                "user_tag_ids": user_tag_ids,
                "default_outreach_medium": default_outreach_medium,
                "agent_assignment_choice": agent_assignment_choice,
                "team_ids": team_ids,
                "starting_date": starting_date,
                "end_date": end_date,
                "timezone": timezone,
                "survey_id": survey_id,
            }
            if account:
                params["accountName"] = account
            return create_relational_organizing_campaign(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="duplicateRelationalCampaign", description="[Extended API] Duplicate a relational organizing campaign.")
    def duplicate_relational_campaign_tool(
        account: Optional[str] = None, campaign_id: int = None
    ) -> dict:
        try:
            params = {"campaign_id": campaign_id}
            if account:
                params["accountName"] = account
            return duplicate_relational_organizing_campaign(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(
        name="assignAgentsToRelationalCampaign",
        description="[Extended API] Assign or remove agents to/from a relational organizing campaign.",
    )
    def assign_agents_to_relational_campaign_tool(
        account: Optional[str] = None, campaign_id: int = None, agent_ids_to_assign: list = None, agent_ids_to_remove: list = None
    ) -> dict:
        try:
            params = {"campaign_id": campaign_id, "agent_ids_to_assign": agent_ids_to_assign, "agent_ids_to_remove": agent_ids_to_remove}
            if account:
                params["accountName"] = account
            return assign_agents_to_relational_organizing_campaign(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="updateRelationalCampaign", description="Update a relational organizing campaign.")
    def update_relational_campaign_tool(
        account: Optional[str] = None,
        campaign_id: int = None,
        name: str = None,
        brief: str = None,
        phonebook_ids: list = None,
        user_tag_ids: list = None,
        default_outreach_medium: int = None,
        agent_assignment_choice: int = None,
        team_ids: list = None,
        starting_date: str = None,
        end_date: str = None,
        timezone: str = None,
        survey_id: int = None,
    ) -> dict:
        try:
            params = {
                "campaign_id": campaign_id,
                "name": name,
                "brief": brief,
                "phonebook_ids": phonebook_ids,
                "user_tag_ids": user_tag_ids,
                "default_outreach_medium": default_outreach_medium,
                "agent_assignment_choice": agent_assignment_choice,
                "team_ids": team_ids,
                "starting_date": starting_date,
                "end_date": end_date,
                "timezone": timezone,
                "survey_id": survey_id,
            }
            if account:
                params["accountName"] = account
            return update_relational_organizing_campaign(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getRelationalCampaign", description="Get a relational organizing campaign.")
    def get_relational_campaign_tool(
        account: Optional[str] = None, campaign_id: int = None
    ) -> dict:
        try:
            params = {"campaign_id": campaign_id}
            if account:
                params["accountName"] = account
            return get_relational_organizing_campaign(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="updateRelationalCampaignStatus", description="[Extended API] Update the status of a relational organizing campaign.")
    def update_relational_campaign_status_tool(
        account: Optional[str] = None, campaign_id: int = None, status: str = None
    ) -> dict:
        try:
            params = {"campaign_id": campaign_id, "status": status}
            if account:
                params["accountName"] = account
            return update_relational_organizing_campaign_status(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}
