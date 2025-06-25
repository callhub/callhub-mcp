# p2p_campaigns.py
"""
P2P (Peer-to-Peer) Campaign operations for CallHub API.
P2P = Snowflake = Collective Texting in CallHub
"""

import sys
from typing import Dict, List, Union, Optional, Any

from .utils import build_url, api_call, get_auth_headers
from .auth import get_account_config

def list_p2p_campaigns(params: Dict) -> Dict:
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
        # Get account configuration
        account_name, api_key, base_url = get_account_config(params.get("account"))
        
        # Build URL using Snowflake endpoint
        url = build_url(base_url, "v1/sms_campaigns/?campaign_type=4")
        headers = get_auth_headers(api_key)
        
        # Prepare query parameters
        query_params = {}
        if params.get("page") is not None:
            query_params["page"] = params["page"]
        if params.get("pageSize") is not None:
            query_params["page_size"] = params["pageSize"]
        
        # Make API call
        return api_call("GET", url, headers, params=query_params)
        
    except Exception as e:
        sys.stderr.write(f"[callhub] Error listing P2P campaigns: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def update_p2p_campaign(params: Dict) -> Dict:
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
    if status is None:
        return {"isError": True, "content": [{"type": "text", "text": "'status' is required."}]}
    
    # Map string status to numeric status if needed
    status_mapping = {
        "start": 1,
        "pause": 2,
        "abort": 3,
        "end": 4
    }
    
    # If a string status was provided, convert it to numeric
    if isinstance(status, str) and status.lower() in status_mapping:
        status = status_mapping[status.lower()]
    # If a numeric status as string was provided, convert to int
    elif isinstance(status, str) and status.isdigit():
        status = int(status)
    # Check if status is valid now
    if not isinstance(status, int) or status < 1 or status > 4:
        return {
            "isError": True, 
            "content": [{"type": "text", "text": "Valid 'status' is required: start, pause, abort, end, or a valid numeric status (1-4)"}]
        }
    
    try:
        # Get account configuration
        account_name, api_key, base_url = get_account_config(params.get("account"))
        
        # Build URL using Snowflake endpoint
        url = build_url(base_url, "v2/sms_campaign/snowflake/{}/", campaign_id)
        headers = get_auth_headers(api_key, "application/json")
        
        # Prepare data
        data = {"status": status}
        
        # Make API call
        return api_call("PUT", url, headers, json_data=data)
        
    except Exception as e:
        sys.stderr.write(f"[callhub] Error updating P2P campaign: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def delete_p2p_campaign(params: Dict) -> Dict:
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
        # Get account configuration
        account_name, api_key, base_url = get_account_config(params.get("account"))
        
        # Build URL using Snowflake endpoint
        url = build_url(base_url, "v2/sms_campaign/snowflake/{}/", campaign_id)
        headers = get_auth_headers(api_key)
        
        # Make API call
        return api_call("DELETE", url, headers)
        
    except Exception as e:
        sys.stderr.write(f"[callhub] Error deleting P2P campaign: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def get_p2p_campaign_agents(params: Dict) -> Dict:
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
        account_name, api_key, base_url = get_account_config(params.get("account"))
        url = build_url(base_url, "v2/collective_texting/{}/agents/", campaign_id)
        headers = get_auth_headers(api_key)
        
        return api_call("GET", url, headers)
        
    except Exception as e:
        sys.stderr.write(f"[callhub] Error getting P2P campaign agents: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def add_agents_to_p2p_campaign(params: Dict) -> Dict:
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
        account_name, api_key, base_url = get_account_config(params.get("account"))
        url = build_url(base_url, "v2/collective_texting/{}/agents/add/", campaign_id)
        headers = get_auth_headers(api_key, "application/json")
        
        data = {"agents_data": {len(agent_ids): agent_ids}}
        
        return api_call("POST", url, headers, json_data=data)
        
    except Exception as e:
        sys.stderr.write(f"[callhub] Error adding agents to P2P campaign: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def reassign_p2p_agents(params: Dict) -> Dict:
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
        account_name, api_key, base_url = get_account_config(params.get("account"))
        url = build_url(base_url, "v2/collective_texting/{}/agents/reassign/", campaign_id)
        headers = get_auth_headers(api_key, "application/json")
        
        return api_call("POST", url, headers, json_data=reassign_data)
        
    except Exception as e:
        sys.stderr.write(f"[callhub] Error reassigning P2P agents: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def create_p2p_campaign(params: Dict) -> Dict:
    """
    Create a new P2P (Snowflake) campaign.
    
    Args:
        params: Dictionary containing the following keys:
            account (str, optional): The account name to use
            campaign_data (Dict): Campaign configuration data including:
                - name (str): Campaign name
                - phonebook (List[str]): List of phonebook URLs
                - message (str): Campaign message
                - other campaign-specific settings
    
    Returns:
        dict: API response containing created campaign data or error information
    """
    campaign_data = params.get("campaign_data")
    if not campaign_data:
        return {"isError": True, "content": [{"type": "text", "text": "'campaign_data' is required."}]}
    
    try:
        # Get account configuration
        account_name, api_key, base_url = get_account_config(params.get("account"))
        
        # Build URL using Snowflake endpoint
        url = build_url(base_url, "v2/sms_campaign/snowflake/")
        headers = get_auth_headers(api_key, "application/json")
        
        # Make API call
        return api_call("POST", url, headers, json_data=campaign_data)
        
    except Exception as e:
        sys.stderr.write(f"[callhub] Error creating P2P campaign: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def get_p2p_surveys(params: Dict) -> Dict:
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
        account_name, api_key, base_url = get_account_config(params.get("account"))
        
        campaign_id = params.get("campaignId")
        if campaign_id:
            url = build_url(base_url, "v2/sms_campaign/snowflake/survey-list/{}/", campaign_id)
        else:
            url = build_url(base_url, "v2/sms_campaign/snowflake/survey-list/")
        
        headers = get_auth_headers(api_key)
        
        return api_call("GET", url, headers)
        
    except Exception as e:
        sys.stderr.write(f"[callhub] Error getting P2P surveys: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}
