"""
Client for interacting with CallHub vb campaign APIs.
"""
import sys
from typing import Dict, Any

from .client import McpApiClient
from .constants import ENDPOINTS

def get_vb_campaign(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get a single vb campaign.
    """
    campaign_id = params.get("campaignId")
    if not campaign_id:
        return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}
    
    client = McpApiClient(params.get("accountName"))
    return client.call(f"{ENDPOINTS.VB_CAMPAIGN}{campaign_id}/", "GET")

def create_voice_broadcast_campaign(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new voice broadcast campaign.

    Args:
        params: Dictionary containing the following keys:
            account (str, optional): The account name to use
            phonebooks (List[int]): List of phonebook IDs
            callerid_options (Dict): Caller ID options
            contact_options (Dict): Contact options
            template_id (str): Template ID
            schedule (Dict): Schedule options

    Returns:
        dict: API response containing campaign data or error information
    """
    try:
        client = McpApiClient(params.get("accountName"))
        data = {
            "phonebooks": params.get("phonebooks"),
            "callerid_options": params.get("callerid_options"),
            "contact_options": params.get("contact_options"),
            "template_id": params.get("template_id"),
            "schedule": params.get("schedule"),
        }
        return client.call(ENDPOINTS.VB_CAMPAIGN, "POST", body=data)
    except Exception as e:
        sys.stderr.write(f"[callhub] Error creating voice broadcast campaign: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def create_vb_campaign_template(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new voice broadcast campaign template.

    Args:
        params: Dictionary containing the following keys:
            account (str, optional): The account name to use
            label (str): The name of the template.
            live_message (Dict): The message to be played to a live person.
            transfers (List[Dict]): A list of transfer options.
            dnc_option (Dict): The DNC (Do Not Call) option.

    Returns:
        dict: API response containing template data or error information
    """
    try:
        client = McpApiClient(params.get("accountName"))
        data = {
            "label": params.get("label"),
            "live_message": params.get("live_message"),
            "transfers": params.get("transfers"),
            "dnc_option": params.get("dnc_option"),
        }
        return client.call(ENDPOINTS.VB_TEMPLATES, "POST", body=data)
    except Exception as e:
        sys.stderr.write(f"[callhub] Error creating VB campaign template: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def list_voice_broadcasts(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    List all voice broadcast campaigns with optional pagination.

    Args:
        params: Dictionary containing the following keys:
            account (str, optional): The account name to use
            page (int, optional): Page number for pagination
            pageSize (int, optional): Number of items per page

    Returns:
        dict: API response containing campaign data or error information
    """
    try:
        client = McpApiClient(params.get("accountName"))
        query_params = {}
        if params.get("page") is not None:
            query_params["page"] = params["page"]
        if params.get("pageSize") is not None:
            query_params["page_size"] = params["pageSize"]
        return client.call(ENDPOINTS.VOICE_BROADCASTS, "GET", query=query_params)
    except Exception as e:
        sys.stderr.write(f"[callhub] Error listing voice broadcast campaigns: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def duplicate_vb_campaign(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Duplicate a voice broadcast campaign.

    Args:
        params: Dictionary containing the following keys:
            account (str, optional): The account name to use
            campaignId (str): The ID of the campaign to duplicate

    Returns:
        dict: API response from the duplicate operation
    """
    try:
        campaign_id = params.get("campaignId")
        if not campaign_id:
            return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}

        client = McpApiClient(params.get("account"))
        return client.call(f"{ENDPOINTS.VB_CAMPAIGN}{campaign_id}/duplicate/", "POST")
    except Exception as e:
        sys.stderr.write(f"[callhub] Error duplicating voice broadcast campaign: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def list_vb_templates(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    List all voice broadcast campaign templates.

    Args:
        params: Dictionary containing:
            accountName (str, optional): Account name to use
            page (int, optional): Page number for pagination
            pageSize (int, optional): Items per page

    Returns:
        dict: API response with template list
    """
    try:
        client = McpApiClient(params.get("accountName"))
        query_params = {}
        if params.get("page"):
            query_params["page"] = params["page"]
        if params.get("pageSize"):
            query_params["page_size"] = params["pageSize"]
        return client.call(ENDPOINTS.VB_TEMPLATES, "GET", query=query_params)
    except Exception as e:
        sys.stderr.write(f"[callhub] Error listing VB templates: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def get_vb_campaign_defaults(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get minimal working structure with defaults for VB campaign creation.

    Returns:
        dict: Default campaign structure ready for creation
    """
    return {
        "isError": False,
        "content": [{
            "type": "text",
            "text": "Minimal VB campaign structure with defaults"
        }],
        "defaults": {
            "phonebooks": [],  # Required: array of phonebook IDs (int)
            "template_id": "",  # Required: template ID as string
            "callerid_options": {
                "callerid": ""  # Required: validated caller ID
            },
            "schedule": {
                "monday": True,
                "tuesday": True,
                "wednesday": True,
                "thursday": True,
                "friday": True,
                "saturday": True,
                "sunday": True
            },
            "contact_options": {
                "use_contact_tz": False  # Use campaign timezone by default
            }
        }
    }

def validate_vb_campaign_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate VB campaign parameters before creation.

    Args:
        params: Campaign parameters to validate

    Returns:
        dict: Validation result with errors if any
    """
    errors = []
    
    # Check required fields
    if not params.get("phonebooks") or not isinstance(params["phonebooks"], list):
        errors.append("phonebooks: Required array of phonebook IDs")
    
    if not params.get("template_id"):
        errors.append("template_id: Required string field")
    
    if not params.get("callerid_options") or not params["callerid_options"].get("callerid"):
        errors.append("callerid_options.callerid: Required validated number")
    
    # Check optional but recommended fields
    if not params.get("schedule"):
        errors.append("schedule: Recommended (weekday booleans)")
    
    if errors:
        return {
            "isError": True,
            "content": [{"type": "text", "text": "Validation failed:\n" + "\n".join(errors)}],
            "valid": False,
            "errors": errors
        }
    
    return {
        "isError": False,
        "content": [{"type": "text", "text": "Validation passed"}],
        "valid": True,
        "errors": []
    }