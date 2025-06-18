# campaigns.py
"""
Call Center Campaign operations for CallHub API.
"""

import sys
import json
from typing import Dict, List, Union, Optional, Any

from .utils import build_url, api_call, get_auth_headers, parse_input_fields
from .auth import get_account_config

def list_call_center_campaigns(params: Dict) -> Dict:
    """
    List all call center campaigns with optional pagination.
    
    Args:
        params: Dictionary containing the following keys:
            accountName (str, optional): The account name to use
            page (int, optional): Page number for pagination
            pageSize (int, optional): Number of items per page
    
    Returns:
        dict: API response containing campaign data or error information
    """
    try:
        # Get account configuration
        account_name, api_key, base_url = get_account_config(params.get("accountName"))
        
        # Build URL and headers
        url = build_url(base_url, "v1/callcenter_campaigns/")
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
        sys.stderr.write(f"[callhub] Error listing call center campaigns: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def update_call_center_campaign(params: Dict) -> Dict:
    """
    Update a call center campaign's status.
    
    Args:
        params: Dictionary containing the following keys:
            accountName (str, optional): The account name to use
            campaignId (str): The ID of the campaign to update
            status (str): The new status of the campaign. Valid values: 
                         "pause", "resume", "stop", "restart"
    
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
    
    # Map string status to numeric status if needed
    status_mapping = {
        "pause": 4,
        "resume": 2,
        "stop": 5,
        "restart": 2
    }
    
    # If a string status was provided, convert it to numeric
    if isinstance(status, str) and status.lower() in status_mapping:
        status = status_mapping[status.lower()]
    # If a numeric status as string was provided, convert to int
    elif isinstance(status, str) and status.isdigit():
        status = int(status)
    # Check if status is valid now
    if not isinstance(status, int):
        return {
            "isError": True, 
            "content": [{"type": "text", "text": "Valid 'status' is required: pause, resume, stop, restart, or a valid numeric status"}]
        }
    
    try:
        # Get account configuration
        account_name, api_key, base_url = get_account_config(params.get("accountName"))
        
        # Build URL and headers
        url = build_url(base_url, "v1/callcenter_campaigns/{}/", campaign_id)
        headers = get_auth_headers(api_key, "application/json")
        
        # Prepare data
        data = {"status": status}
        
        # Make API call
        return api_call("PATCH", url, headers, json_data=data)
        
    except Exception as e:
        sys.stderr.write(f"[callhub] Error updating call center campaign: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def delete_call_center_campaign(params: Dict) -> Dict:
    """
    Delete a call center campaign by ID.
    
    Args:
        params: Dictionary containing the following keys:
            accountName (str, optional): The account name to use
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
        account_name, api_key, base_url = get_account_config(params.get("accountName"))
        
        # Build URL and headers
        url = build_url(base_url, "v1/callcenter_campaigns/{}/", campaign_id)
        headers = get_auth_headers(api_key)
        
        # Make API call
        return api_call("DELETE", url, headers)
        
    except Exception as e:
        sys.stderr.write(f"[callhub] Error deleting call center campaign: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def create_call_center_campaign(params: Dict) -> Dict:
    """
    Create a new call center campaign using the Power Campaign API.
    
    This function handles the complex structure needed to create a call center campaign 
    in CallHub, including the script with screens, questions, and responses.
    
    Args:
        params: Dictionary containing the campaign configuration:
            accountName (str, optional): The account name to use
            campaign_data (dict): The complete campaign configuration including:
                Required fields:
                - name (str): Name of the campaign
                - phonebook_ids (list): List of phonebook IDs to use
                - callerid (str): Caller ID to display
                - script (list): Array of script elements with different types
                
                Optional fields:
                - recording (bool): Whether to record calls (default: False)
                - assign_all_agents (bool): Assign all agents to campaign (default: False)
                - call_dispositions (list): List of disposition names
                - monday, tuesday, etc. (bool): Days the campaign is operational
                - startingdate (str): Start date in 'YYYY-MM-DD HH:MM:SS' format
                - expirationdate (str): End date in 'YYYY-MM-DD HH:MM:SS' format
                - daily_start_time (str): Daily start time in 'HH:MM' format (default: '08:00')
                - daily_end_time (str): Daily end time in 'HH:MM' format (default: '21:00')
                - timezone (str): Name of campaign timezone
    
    Returns:
        dict: API response with details of the created campaign or error information
    
    Script Structure Example:
    ```python
    campaign_data = {
        "name": "Time to change rally",
        "phonebook_ids": ["12345", "67890"],
        "callerid": "15551234567",
        "script": [
            {
                "type": "12",
                "script_text": "Hi {first_name} my name is {agent_name}. I'm a volunteer with the Clean Energy Society. We are organizing a 'Time to change' rally. Do you have a minute to talk?"
            },
            {
                "type": "1",
                "question": "Will you attend the rally?",
                "choices": [
                    {"answer": "Yes"},
                    {"answer": "No"},
                    {"answer": "Maybe"}
                ]
            },
            {
                "type": "3", 
                "question": "Can you bring a few friends along? If yes, how many?"
            }
        ],
        "monday": True,
        "tuesday": True,
        "friday": True,
        "startingdate": "2025-05-15 12:00:00",
        "expirationdate": "2025-06-15 12:00:00",
        "daily_start_time": "08:00",
        "daily_end_time": "21:00",
        "timezone": "America/Phoenix",
        "use_contact_timezone": False,
        "block_cellphone": True,
        "block_litigators": True,
        "recording": True,
        "notes_required": True,
        "assign_all_agents": True,
        "call_dispositions": ["Will Attend", "Maybe", "Not Interested", "Call Back", "Wrong Number"]
    }
    ```
    """
    # Extract campaign data
    campaign_data = params.get("campaign_data")
    if not campaign_data:
        return {"isError": True, "content": [{"type": "text", "text": "'campaign_data' is required."}]}
    
    # Allow passing as a JSON string
    if isinstance(campaign_data, str):
        try:
            campaign_data = json.loads(campaign_data)
        except json.JSONDecodeError as e:
            return {"isError": True, "content": [{"type": "text", "text": f"Invalid JSON in campaign_data: {str(e)}"}]}
    
    # Validate required fields
    required_fields = ["name", "phonebook_ids", "callerid", "script"]
    missing_fields = [field for field in required_fields if field not in campaign_data]
    if missing_fields:
        return {
            "isError": True, 
            "content": [{"type": "text", "text": f"Missing required fields: {', '.join(missing_fields)}"}]
        }
    
    # Validate and normalize script structure
    script = campaign_data.get("script", [])
    if not isinstance(script, list) or len(script) == 0:
        return {
            "isError": True,
            "content": [{"type": "text", "text": "Script must be a non-empty array of script elements"}]
        }
    
    # Normalize script structure based on Django API expectations
    normalized_script = []
    for i, element in enumerate(script):
        if not isinstance(element, dict):
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"Script element at index {i} must be an object/dictionary"}]
            }
        
        # Convert string type to integer if needed
        element_type = element.get("type")
        if isinstance(element_type, str):
            try:
                element_type = int(element_type)
            except ValueError:
                return {
                    "isError": True,
                    "content": [{"type": "text", "text": f"Script element at index {i} has invalid type: {element_type}"}]
                }
        
        if element_type is None:
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"Script element at index {i} missing 'type' field"}]
            }
        
        # Create normalized element
        normalized_element = {
            "type": element_type
        }
        
        # Handle script text (type 12)
        if element_type == 12:
            script_text = element.get("script_text") or element.get("content") or element.get("question")
            if not script_text:
                return {
                    "isError": True,
                    "content": [{"type": "text", "text": f"Script element at index {i} with type 12 must have 'script_text', 'content', or 'question'"}]
                }
            normalized_element["script_text"] = script_text
        
        # Handle questions (type 1, 3, etc.)
        elif element_type in [1, 3]:
            question = element.get("question") or element.get("content")
            if not question:
                return {
                    "isError": True,
                    "content": [{"type": "text", "text": f"Script element at index {i} with type {element_type} must have 'question' or 'content'"}]
                }
            normalized_element["question"] = question
            
            # Handle choices for multi-choice questions (type 1)
            if element_type == 1:
                choices = element.get("choices", [])
                if not isinstance(choices, list) or len(choices) == 0:
                    return {
                        "isError": True,
                        "content": [{"type": "text", "text": f"Script element at index {i} with type 1 must have non-empty 'choices' array"}]
                    }
                normalized_element["choices"] = choices
        
        # Add any other fields as-is
        for key, value in element.items():
            if key not in ["type", "script_text", "question", "content", "choices"]:
                normalized_element[key] = value
        
        normalized_script.append(normalized_element)
    
    # Update the campaign data with normalized script
    campaign_data["script"] = normalized_script
    
    try:
        # Get account configuration
        account_name, api_key, base_url = get_account_config(params.get("accountName"))
        
        # Build URL and headers for power campaign creation
        url = build_url(base_url, "v1/power_campaign/create/")
        headers = get_auth_headers(api_key, "application/json")
        
        # Make API call
        return api_call("POST", url, headers, json_data=campaign_data)
        
    except Exception as e:
        sys.stderr.write(f"[callhub] Error creating call center campaign: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}
