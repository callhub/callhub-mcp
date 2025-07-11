# p2p_campaigns.py
"""
P2P (Peer-to-Peer) Campaign operations for CallHub API.
P2P = Snowflake = Collective Texting in CallHub

FIXES APPLIED - July 2025 VB System Integration Testing:

1. SCRIPT STRUCTURE FIX:
   - Use template_id (integer) or script object
   - Optionally convert script objects to template_id from v1/templates
   - ✅ CORRECT "script": {"label": "...", "questions": [...]}
   - ✅ CORRECT: "template_id": 123

2. SSL CERTIFICATE HANDLING:
   - Local development (0.0.0.0): Use HTTP, disable SSL verification
   - Production: Use HTTPS with proper SSL certificates
   - Added automatic SSL detection based on URL

3. MINIMAL REQUIRED FIELDS:
   - name: Campaign name (required)
   - template_id: Survey template ID (required) 
   - phonebooks: List of phonebook IDs (required)
   - callerid_options: Caller ID configuration (required)
   - All other fields are optional - let API set defaults

4. ERROR HANDLING:
   - Specific handling for date format errors
   - SSL certificate error guidance
   - Authentication failure messages
   - Validation error parsing

5. DATE FORMAT REQUIREMENTS:
   - ✅ CORRECT: "2025-07-11 15:55:40+00:00"
   - ❌ WRONG: "2025-07-12 09:55:40+00:00" (some timezones cause issues)
   - RECOMMENDATION: Let API set default schedule for simplicity

WORKING EXAMPLE:
    campaign_data = {
        "name": "VB System P2P Campaign",
        "template_id": 3674114171558954642,  # INTEGER
        "phonebooks": ["1"],
        "callerid_options": {"numbers": ["12232017834"]}
    }

INTEGRATION NOTES:
- Use with VB modules: dialer_campaign, dialer_contact, survey, workflow
- Store campaign IDs in dialer_cdr for tracking
- Handle success/failure callbacks in workflow module
"""

import sys
from typing import Dict, List, Union, Optional, Any
import json # Added import for json

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
        account_name, api_key, base_url = get_account_config(params.get("account")) # Reverted to original signature
        
        # Build URL using Snowflake endpoint
        url = build_url(base_url, "v1/p2p_campaigns/")
        headers = get_auth_headers(api_key) # Reverted to original signature
        
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
        account_name, api_key, base_url = get_account_config(params.get("account")) # Reverted to original signature
        
        # Build URL using Snowflake endpoint
        url = build_url(base_url, "v1/p2p_campaigns/{}/", campaign_id)
        headers = get_auth_headers(api_key, "application/json") # Reverted to original signature
        
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
    
    FIXED VERSION - Based on VB System integration testing July 2025
    
    Key Fixes Applied:
    - Recommend template_id (integer) instead of script object structure
    - Handle SSL certificate issues for local development (0.0.0.0)
    - Support minimal required fields
    - Convert script object to template_id automatically
    - Better error handling with specific messages
    
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
    campaign_data = params.get("campaign_data", params) # Handle both nested and flat params
    
    # Extract and validate required parameters
    name = campaign_data.get("name")
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
    if not name:
        required_fields.append("name")
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
        "name": name,
        "template_id": template_id,  # KEY FIX: Use template_id, not script
        "phonebooks": phonebooks,
        "callerid_options": callerid_options
    }
    
    # Add optional fields only if provided (avoid validation errors)
    optional_fields = ['script','schedule', 'agent_settings', 'contact_options', 'recommended_replies', 'description']
    for field in optional_fields:
        if field in campaign_data and campaign_data[field] is not None:
            payload[field] = campaign_data[field]
    
    try:
        # Get account configuration
        account_name, api_key, base_url = get_account_config(params.get("account"))
        
        # Build URL using P2P campaigns endpoint
        url = build_url(base_url, "v1/p2p_campaigns/")
        headers = get_auth_headers(api_key, "application/json")
        
        # Log the payload being sent for debugging
        sys.stderr.write(f"[callhub] Creating P2P campaign: {name}\n")
        sys.stderr.write(f"[callhub] Template ID: {template_id}\n")
        sys.stderr.write(f"[callhub] Payload: {json.dumps(payload, indent=2)}\n")
        sys.stderr.write(f"[callhub] URL: {url}\n")
        
        # Make API call with SSL handling for local development
        response = api_call("POST", url, headers, json_data=payload)
        
        # Handle successful response
        if not response.get("isError") and "id" in response:
            sys.stderr.write(f"[callhub] ✅ P2P Campaign created successfully!\n")
            sys.stderr.write(f"[callhub] Campaign ID: {response.get('id')}\n")
            sys.stderr.write(f"[callhub] Campaign PK: {response.get('pk_str')}\n")
            
            # Add success indicators to response
            response["success"] = True
            response["campaign_id"] = response.get("id")
            response["campaign_pk"] = response.get("pk_str")
            response["message"] = f"P2P campaign '{name}' created successfully"
        
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
