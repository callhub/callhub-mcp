# sms_campaigns.py
"""
SMS Campaign operations for CallHub API.
"""

import sys
from typing import Dict, List, Union, Optional, Any

from .utils import build_url, api_call, get_auth_headers
from .auth import get_account_config

def list_sms_campaigns(params: Dict) -> Dict:
    """
    List all SMS campaigns with optional pagination.
    
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
        
        # Build URL and headers
        url = build_url(base_url, "v1/sms_campaigns/")
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
        sys.stderr.write(f"[callhub] Error listing SMS campaigns: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def update_sms_campaign(params: Dict) -> Dict:
    """
    Update an SMS campaign's status.
    
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
        
        # Build URL and headers
        url = build_url(base_url, "v1/sms_campaigns/{}/", campaign_id)
        headers = get_auth_headers(api_key, "application/json")
        
        # Prepare data
        data = {"status": status}
        
        # Make API call
        return api_call("PUT", url, headers, json_data=data)
        
    except Exception as e:
        sys.stderr.write(f"[callhub] Error updating SMS campaign: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def export_sms_report(client: CallHubClient, campaign_id: int):
    """
    Export an SMS report for a campaign.
    """
    return client.get(f"v1/sms_campaign/sms_report/export/?campaign_id={campaign_id}")

