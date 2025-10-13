from typing import Dict, Any
from .client import McpApiClient

def create_relational_organizing_campaign(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new relational organizing campaign.
    """
    client = McpApiClient(params.get("accountName"))
    # All params are passed as the body
    return client.call("v1/relational-campaign/", "POST", body=params)

def duplicate_relational_organizing_campaign(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Duplicate a relational organizing campaign.
    """
    campaign_id = params.get("campaign_id")
    if not campaign_id:
        return {"isError": True, "content": [{"type": "text", "text": "'campaign_id' is required."}]}
    client = McpApiClient(params.get("accountName"))
    return client.call(f"v1/relational-campaign/{campaign_id}/duplicate/", "POST")

def assign_agents_to_relational_organizing_campaign(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Assign or remove agents to/from a relational organizing campaign.
    """
    campaign_id = params.get("campaign_id")
    if not campaign_id:
        return {"isError": True, "content": [{"type": "text", "text": "'campaign_id' is required."}]}
    
    data = {
        "agent_ids_to_assign": params.get("agent_ids_to_assign", []),
        "agent_ids_to_remove": params.get("agent_ids_to_remove", []),
    }
    client = McpApiClient(params.get("accountName"))
    return client.call(f"v1/relational-campaign/{campaign_id}/agents/", "PUT", body=data)

def update_relational_organizing_campaign(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a relational organizing campaign.
    """
    campaign_id = params.get("campaign_id")
    if not campaign_id:
        return {"isError": True, "content": [{"type": "text", "text": "'campaign_id' is required."}]}
    
    client = McpApiClient(params.get("accountName"))
    # All other params are passed as the body
    return client.call(f"v1/relational-campaign/{campaign_id}/", "PUT", body=params)

def get_relational_organizing_campaign(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get a relational organizing campaign.
    """
    campaign_id = params.get("campaign_id")
    if not campaign_id:
        return {"isError": True, "content": [{"type": "text", "text": "'campaign_id' is required."}]}
    
    client = McpApiClient(params.get("accountName"))
    return client.call(f"v1/relational-campaign/{campaign_id}/", "GET")

def update_relational_organizing_campaign_status(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update the status of a relational organizing campaign.
    """
    campaign_id = params.get("campaign_id")
    status = params.get("status")
    if not campaign_id:
        return {"isError": True, "content": [{"type": "text", "text": "'campaign_id' is required."}]}
    if not status:
        return {"isError": True, "content": [{"type": "text", "text": "'status' is required."}]}

    data = {"status": status}
    client = McpApiClient(params.get("accountName"))
    return client.call(f"v1/relational-campaign/{campaign_id}/update-status/", "POST", body=data)