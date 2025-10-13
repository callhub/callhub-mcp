# File: src/callhub/users.py

import sys
from typing import Dict, Any
from datetime import datetime

from .client import McpApiClient

def list_users(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retrieve a list of all users in the CallHub account.
    
    Args:
        params (dict): Dictionary containing the following keys:
            - accountName (str, optional): The account name to use
    
    Returns:
        dict: A dictionary containing the API response with user data
    """
    client = McpApiClient(params.get("accountName"))
    return client.call("/v1/users/", "GET")

def get_credit_usage(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retrieve credit usage details for the CallHub account.
    
    Args:
        params (dict): Dictionary containing the following keys:
            - accountName (str, optional): The account name to use
            - start_date (str, optional): Start date in MM/DD/YYYY format
            - end_date (str, optional): End date in MM/DD/YYYY format
            - generate_csv (bool, optional): Whether to output in CSV (True) or JSON (False)
            - campaign_type (int, optional): Filter by campaign type (1=SMS, 3=Text2Join, 4=P2P, 5=CallCentre, 6=Voice)
    
    Returns:
        dict: A dictionary containing the API response with credit usage data
    """
    client = McpApiClient(params.get("accountName"))
    
    # Prepare the request payload
    payload = {}
    
    # Add parameters - start_date is required in mm/dd/yyyy format
    if params.get("start_date"):
        payload["start_date"] = params.get("start_date")
    else:
        # Default to current date if not provided
        from datetime import datetime
        today = datetime.now()
        payload["start_date"] = today.strftime("%m/%d/%Y")
    
    # Add end_date if provided (also in mm/dd/yyyy format)
    if params.get("end_date"):
        payload["end_date"] = params.get("end_date")
    
    # Campaign type is optional
    if params.get("campaign_type") is not None:
        payload["campaign_type"] = params.get("campaign_type")
        
    generate_csv = params.get("generate_csv", False)
    payload["generate_csv"] = generate_csv
    
    sys.stderr.write(f"[callhub] POST request to v2/credits_usage/\n")
    sys.stderr.write(f"[callhub] Payload: {payload}\n")
    result = client.call("/v2/credits_usage/", "POST", body=payload)

    if generate_csv and not result.get("isError"):
        csv_data = result.get("message", "")
        if not csv_data and result.get("content"):
            csv_data = result["content"][0].get("text", "")
        return {"format": "csv", "data": csv_data, "success": True}

    return result
