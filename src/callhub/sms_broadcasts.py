# sms_broadcasts.py
"""
SMS Broadcast operations for CallHub API.
"""

import sys
from typing import Dict, List, Union, Optional, Any

from .utils import build_url, api_call, get_auth_headers
from .auth import get_account_config

def list_sms_broadcasts(params: Dict) -> Dict:
    """
    List all SMS broadcast campaigns with optional pagination.
    
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
        url = build_url(base_url, "v1/sms_broadcasts/")
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
        sys.stderr.write(f"[callhub] Error listing SMS broadcast campaigns: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def update_sms_broadcast(params: Dict) -> Dict:
    """
    Update an SMS broadcast campaign's status.
    
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
        url = build_url(base_url, "v1/sms_broadcasts/{}/", campaign_id)
        headers = get_auth_headers(api_key, "application/json")
        
        # Prepare data
        data = {"status": status}
        
        # Make API call
        return api_call("PATCH", url, headers, json_data=data)
        
    except Exception as e:
        sys.stderr.write(f"[callhub] Error updating SMS broadcast campaign: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def delete_sms_broadcast(params: Dict) -> Dict:
    """
    Delete an SMS broadcast campaign by ID.
    
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
        
        # Build URL and headers
        url = build_url(base_url, "v1/sms_broadcasts/{}/", campaign_id)
        headers = get_auth_headers(api_key)
        
        # Make API call
        return api_call("DELETE", url, headers)
        
    except Exception as e:
        sys.stderr.write(f"[callhub] Error deleting SMS broadcast campaign: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def create_sms_broadcast(params: Dict) -> Dict:
    """
    Create a new SMS broadcast campaign.

    Args:
        params: Dictionary containing the following keys:
            account (str, optional): The account name to use
            name (str): Name of the campaign
            phonebook_ids (list): List of phonebook IDs
            message (str): SMS message content
            sender_id (str): Sender ID
            schedule_date (str, optional): Scheduled date (ISO format)

    Returns:
        dict: API response containing the created campaign data
    """
    # Validate required parameters
    for key in ["name", "phonebook_ids", "message", "sender_id"]:
        if not params.get(key):
            return {"isError": True, "content": [{"type": "text", "text": f"'{key}' is required."}]}

    try:
        # Get account configuration
        account_name, api_key, base_url = get_account_config(params.get("account"))

        # Build URL and headers
        url = build_url(base_url, "v2/sms_broadcast/create/")
        headers = get_auth_headers(api_key, "application/json")

        # Prepare data
        data = {
            "name": params["name"],
            "phonebook_ids": params["phonebook_ids"],
            "message": params["message"],
            "sender_id": params["sender_id"]
        }
        if params.get("schedule_date"):
            data["schedule_date"] = params["schedule_date"]

        # Make API call
        return api_call("POST", url, headers, json_data=data)

    except Exception as e:
        sys.stderr.write(f"[callhub] Error creating SMS broadcast campaign: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}