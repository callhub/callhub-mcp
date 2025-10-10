
from callhub.client import CallHubClient

def create_relational_organizing_campaign(client: CallHubClient, name: str, brief: str, phonebook_ids: list, user_tag_ids: list, default_outreach_medium: int, agent_assignment_choice: int, team_ids: list, starting_date: str, end_date: str, timezone: str, survey_id: int):
    """
    Create a new relational organizing campaign.
    """
    data = {
        "name": name,
        "brief": brief,
        "phonebooks": phonebook_ids,
        "user_tags": user_tag_ids,
        "default_outreach_medium": default_outreach_medium,
        "agent_assignment_choice": agent_assignment_choice,
        "team": team_ids,
        "startingdate": starting_date,
        "end_date": end_date,
        "timezone": timezone,
        "survey": survey_id,
    }
    return client.post("v1/relational-campaign/", data=data)

def duplicate_relational_organizing_campaign(client: CallHubClient, campaign_id: int):
    """
    Duplicate a relational organizing campaign.
    """
    return client.post(f"v1/relational-campaign/{campaign_id}/duplicate/")

def assign_agents_to_relational_organizing_campaign(client: CallHubClient, campaign_id: int, agent_ids_to_assign: list, agent_ids_to_remove: list):
    """
    Assign or remove agents to/from a relational organizing campaign.
    """
    data = {
        "agent_ids_to_assign": agent_ids_to_assign,
        "agent_ids_to_remove": agent_ids_to_remove,
    }
    return client.put(f"v1/relational-campaign/{campaign_id}/agents/", data=data)

def update_relational_organizing_campaign(client: CallHubClient, campaign_id: int, name: str, brief: str, phonebook_ids: list, user_tag_ids: list, default_outreach_medium: int, agent_assignment_choice: int, team_ids: list, starting_date: str, end_date: str, timezone: str, survey_id: int):
    """
    Update a relational organizing campaign.
    """
    data = {
        "name": name,
        "brief": brief,
        "phonebooks": phonebook_ids,
        "user_tags": user_tag_ids,
        "default_outreach_medium": default_outreach_medium,
        "agent_assignment_choice": agent_assignment_choice,
        "team": team_ids,
        "startingdate": starting_date,
        "end_date": end_date,
        "timezone": timezone,
        "survey": survey_id,
    }
    return client.put(f"v1/relational-campaign/{campaign_id}/", data=data)

def get_relational_organizing_campaign(client: CallHubClient, campaign_id: int):
    """
    Get a relational organizing campaign.
    """
    return client.get(f"v1/relational-campaign/{campaign_id}/")

def update_relational_organizing_campaign_status(client: CallHubClient, campaign_id: int, status: str):
    """
    Update the status of a relational organizing campaign.
    """
    data = {
        "status": status,
    }
    return client.post(f"v1/relational-campaign/{campaign_id}/update-status/", data=data)
