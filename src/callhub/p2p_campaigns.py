# p2p_campaigns.py
"""
P2P (Peer-to-Peer) Campaign operations for CallHub API.
P2P = Snowflake = Collective Texting in CallHub
"""

import sys
from typing import Dict, Any, List
import json

from .client import McpApiClient
from .constants import ENDPOINTS

def list_p2p_campaigns(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    List all P2P campaigns (Snowflake campaigns) with optional pagination.
    
    Args:
        params: Dictionary containing the following keys:
            account (str, optional): The account name to use
            page (int, optional): Page number for pagination
            pageSize (int, optional): Number of items per page
    
    Returns:
        dict: API response containing campaign data or error information
    """
    try:
        client = McpApiClient(params.get("account"))
        query_params = {}
        if params.get("page") is not None:
            query_params["page"] = params["page"]
        if params.get("pageSize") is not None:
            query_params["page_size"] = params["pageSize"]
        return client.call(ENDPOINTS.P2P_CAMPAIGNS, "GET", query=query_params)
    except Exception as e:
        sys.stderr.write(f"[callhub] Error listing P2P campaigns: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def update_p2p_campaign(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a P2P campaign's status using Snowflake endpoint.
    
    Args:
        params: Dictionary containing the following keys:
            account (str, optional): The account name to use
            campaignId (str): The ID of the campaign to update
            status (str or int): The new status of the campaign. 
                String values: "start", "pause", "abort", "end"
                Numeric values: 1 (START), 2 (PAUSE), 3 (ABORT), 4 (END)
    
    Returns:
        dict: API response from the update operation
    """
    # Validate required parameters
    campaign_id = params.get("campaignId")
    if not campaign_id:
        return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}
    
    status = params.get("status")
    if not status:
        return {"isError": True, "content": [{"type": "text", "text": "'status' is required."}]}

    try:
        client = McpApiClient(params.get("account"))
        return client.call(f"{ENDPOINTS.P2P_CAMPAIGN}{campaign_id}/", "PUT", body={"status": status})
    except Exception as e:
        sys.stderr.write(f"[callhub] Error updating P2P campaign: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def delete_p2p_campaign(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Delete a P2P campaign by ID using Snowflake endpoint.
    
    Args:
        params: Dictionary containing the following keys:
            account (str, optional): The account name to use
            campaignId (str): The ID of the campaign to delete
    
    Returns:
        dict: API response from the delete operation
    """
    # Validate required parameters
    campaign_id = params.get("campaignId")
    if not campaign_id:
        return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}
    
    try:
        client = McpApiClient(params.get("account"))
        return client.call(f"{ENDPOINTS.P2P_CAMPAIGN}{campaign_id}/", "DELETE")
    except Exception as e:
        sys.stderr.write(f"[callhub] Error deleting P2P campaign: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def get_p2p_campaign_agents(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get agents for a P2P campaign using Collective Texting endpoint.
    
    Args:
        params: Dictionary containing the following keys:
            account (str, optional): The account name to use
            campaignId (str): The ID of the campaign
    
    Returns:
        dict: API response containing agent data
    """
    campaign_id = params.get("campaignId")
    if not campaign_id:
        return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}
    
    try:
        client = McpApiClient(params.get("account"))
        return client.call(ENDPOINTS.COLLECTIVE_TEXTING_AGENTS.format(campaign_id=campaign_id), "GET")
    except Exception as e:
        sys.stderr.write(f"[callhub] Error getting P2P campaign agents: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def add_agents_to_p2p_campaign(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add agents to a P2P campaign using Collective Texting endpoint.
    
    Args:
        params: Dictionary containing the following keys:
            account (str, optional): The account name to use
            campaignId (str): The ID of the campaign
            agentIds (List[str]): List of agent IDs to add
    
    Returns:
        dict: API response from the add operation
    """
    campaign_id = params.get("campaignId")
    agent_ids = params.get("agentIds", [])
    
    if not campaign_id:
        return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}
    if not agent_ids:
        return {"isError": True, "content": [{"type": "text", "text": "'agentIds' is required."}]}
    
    try:
        client = McpApiClient(params.get("account"))
        data = {"agents": agent_ids}
        return client.call(ENDPOINTS.COLLECTIVE_TEXTING_AGENTS_ADD.format(campaign_id=campaign_id), "POST", body=data)
    except Exception as e:
        sys.stderr.write(f"[callhub] Error adding agents to P2P campaign: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def reassign_p2p_agents(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reassign agents in a P2P campaign using Collective Texting endpoint.
    
    Args:
        params: Dictionary containing the following keys:
            account (str, optional): The account name to use
            campaignId (str): The ID of the campaign
            reassignData (Dict): Reassignment configuration
    
    Returns:
        dict: API response from the reassign operation
    """
    campaign_id = params.get("campaignId")
    reassign_data = params.get("reassignData", {})
    
    if not campaign_id:
        return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}
    
    try:
        client = McpApiClient(params.get("account"))
        return client.call(ENDPOINTS.COLLECTIVE_TEXTING_AGENTS_REASSIGN.format(campaign_id=campaign_id), "POST", body=reassign_data)
    except Exception as e:
        sys.stderr.write(f"[callhub] Error reassigning P2P agents: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def create_p2p_campaign(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new P2P (Snowflake) campaign.
    Args:
        params: Dictionary containing campaign configuration data including:
            account (str, optional): The account name to use
            campaign_data (Dict): Campaign configuration containing:
                name (str): Campaign name (required)
                template_id (int): Survey template ID - USE THIS instead of script object
                phonebooks (List[str]): List of phonebook IDs (required)
                callerid_options (Dict): Caller ID configuration (required)
                schedule (Dict, optional): Campaign schedule
                agent_settings (Dict, optional): Agent configuration
                contact_options (Dict, optional): Contact handling options

    Returns:
        dict: API response containing created campaign data or error information

    Example Usage:
        params = {
            "account": "engineering+mocktest@callhub.io",
            "campaign_data": {
                "name": "VB System P2P Campaign",
                "template_id": 3674114171558954642,  # INTEGER, not script object
                "phonebooks": ["1"],
                "callerid_options": {"numbers": ["12232017834"]}
            }
        }
    """
    campaign_data = params.get("campaign_data", params)
    
    # Extract and validate required parameters
    callerid_options = campaign_data.get("callerid_options")
    phonebooks = campaign_data.get("phonebooks")
    template_id = campaign_data.get("template_id")
    script = campaign_data.get("script")
    
    # CRITICAL FIX: Handle script object conversion to template_id
    if script and not template_id:
        if isinstance(script, dict) and "id" in script:
            # Convert script object to template_id
            template_id = script["id"]
            sys.stderr.write(f"[callhub] Converted script object to template_id: {template_id}\n")
        elif isinstance(script, int):
            # Script was provided as integer, use as template_id
            template_id = script
            sys.stderr.write(f"[callhub] Using script integer as template_id: {template_id}\n")

    
    # Validate required fields (LESSON LEARNED FROM TESTING)
    required_fields = []
    if not callerid_options:
        required_fields.append("callerid_options")
    if not phonebooks:
        required_fields.append("phonebooks")
    
    if required_fields:
        return {
            "isError": True, 
            "content": [{"type": "text", "text": f"Missing required fields: {', '.join(required_fields)}"}]
        }
    
    # Validate template_id or script requirement
    if not template_id and not script:
        return {
            "isError": True,
            "content": [{"type": "text", "text": "Either 'template_id' or 'script' must be provided. Recommended: use template_id (integer)."}]
        }

    # Build minimal payload (LESSON: Start with minimal fields, let API set defaults)
    payload = {
        "phonebooks": phonebooks,
        "callerid_options": callerid_options
    }
    
    # CRITICAL FIX: Only include template_id OR script, never both, never None
    if template_id is not None:
        payload["template_id"] = template_id
    elif script is not None:
        payload["script"] = script
    
    # Add optional fields only if provided (avoid validation errors)
    optional_fields = ['name','schedule', 'agent_settings', 'contact_options', 'recommended_replies', 'description']
    for field in optional_fields:
        if field in campaign_data and campaign_data[field] is not None:
            payload[field] = campaign_data[field]
    
    try:
        client = McpApiClient(params.get("account"))
        # Log the payload being sent for debugging
        sys.stderr.write(f"[callhub] Template ID: {template_id}\n")
        sys.stderr.write(f"[callhub] Payload: {json.dumps(payload, indent=2)}\n")
        response = client.call(ENDPOINTS.P2P_CAMPAIGNS, "POST", body=payload)
        # Handle successful response
        if not response.get("isError") and "id" in response:
            sys.stderr.write(f"[callhub] ✅ P2P Campaign created successfully!\n")
            sys.stderr.write(f"[callhub] Campaign ID: {response.get('id')}\n")
            sys.stderr.write(f"[callhub] Campaign PK: {response.get('pk_str')}\n")
            
            # Add success indicators to response
            response["success"] = True
            response["campaign_id"] = response.get("id")
            response["campaign_pk"] = response.get("pk_str")
        
        return response
        
    except Exception as e:
        error_msg = str(e)
        sys.stderr.write(f"[callhub] Error creating P2P campaign: {error_msg}\n")
        
        # Provide helpful error messages based on common issues discovered during testing
        if "SSL" in error_msg.upper():
            return {
                "isError": True, 
                "content": [{
                    "type": "text", 
                    "text": f"SSL Error: {error_msg}. For local development with 0.0.0.0, use HTTP base URL instead of HTTPS."
                }]
            }
        elif "Connection" in error_msg:
            return {
                "isError": True, 
                "content": [{
                    "type": "text", 
                    "text": f"Connection Error: {error_msg}. Check if the base URL is accessible."
                }]
            }
        else:
            return {"isError": True, "content": [{"type": "text", "text": error_msg}]}

def get_p2p_surveys(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get surveys for a P2P campaign using Snowflake survey endpoint.
    
    Args:
        params: Dictionary containing the following keys:
            account (str, optional): The account name to use
            campaignId (str, optional): The ID of the campaign
    
    Returns:
        dict: API response containing survey data
    """
    try:
        client = McpApiClient(params.get("account"))
        campaign_id = params.get("campaignId")
        
        if campaign_id:
            url = f"{ENDPOINTS.P2P_CAMPAIGN_SURVEY_LIST}{campaign_id}/"
        else:
            url = ENDPOINTS.P2P_CAMPAIGN_SURVEY_LIST
        
        return client.call(url, "GET")
    except Exception as e:
        sys.stderr.write(f"[callhub] Error getting P2P surveys: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def duplicate_p2p_campaign(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Duplicate a P2P campaign.

    Args:
        params: Dictionary containing the following keys:
            account (str, optional): The account name to use
            campaignId (str): The ID of the campaign to duplicate

    Returns:
        dict: API response from the duplicate operation
    """
    campaign_id = params.get("campaignId")
    if not campaign_id:
        return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}

    try:
        client = McpApiClient(params.get("account"))
        return client.call(f"{ENDPOINTS.P2P_CAMPAIGNS}{campaign_id}/duplicate/", "POST")
    except Exception as e:
        sys.stderr.write(f"[callhub] Error duplicating P2P campaign: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}
