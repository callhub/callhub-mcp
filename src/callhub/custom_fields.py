# custom_fields.py
"""
Custom fields management functions for CallHub API.
"""

import sys
import json
from typing import Dict, Any

from .client import McpApiClient
from .constants import ENDPOINTS

def list_custom_fields(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    List all custom fields for the account.
    
    Args:
        params: Dictionary with:
            - accountName (optional): The account to use
            - page (optional): Page number for pagination
            - pageSize (optional): Number of results per page
            
    Returns:
        Dictionary with custom field results
    """
    client = McpApiClient(params.get("accountName"))
    query = {}
    if params.get("page"):
        query["page"] = params["page"]
    if params.get("pageSize"):
        query["page_size"] = params["pageSize"]

    result = client.call(ENDPOINTS.CUSTOM_FIELDS, "GET", query=query)
    
    if result.get("isError"):
        return result

    # Handle non-standard concatenated JSON response
    if "results" not in result and "message" in result:
        try:
            # Split the string by "}{", then fix each item to be valid JSON
            parts = result["message"].split("}{")
            json_objects = []
            for i, part in enumerate(parts):
                # Add closing brace to all except last part
                if i < len(parts) - 1 and not part.endswith("}"):
                    part += "}"
                # Add opening brace to all except first part
                if i > 0 and not part.startswith("{"):
                    part = "{" + part
                # Try to parse as JSON
                try:
                    obj = json.loads(part)
                    json_objects.append(obj)
                except json.JSONDecodeError as e:
                    sys.stderr.write(f"[callhub] Failed to parse JSON part: {part}: {e}\n")

            # Return a standard format with results array
            return {"count": len(json_objects), "results": json_objects}
        except Exception as e:
            sys.stderr.write(f"[callhub] Error processing custom fields response: {str(e)}\n")
            # Return original response on error
            return {"isError": True, "content": [{"type": "text", "text": f"Failed to parse response: {str(e)}"}]}
    
    # If not a string or parsing failed, return the original result
    return result

def get_custom_field(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retrieve a single custom field by ID or by name and type.

    Args:
        params: Dictionary with:
            - accountName (optional): The account to use
            - customFieldId: ID of the custom field to retrieve
            - name (alternative): Name of the custom field
            - field_type (if using name): Type of field (1: "Text", 2: "Number", 3: "Boolean", 4: "Multi-choice")

    Returns:
        Dictionary with custom field details
    """
    client = McpApiClient(params.get("accountName"))
    field_id = params.get("customFieldId")
    name = params.get("name")
    field_type = params.get("field_type")
    
    if not field_id and not (name and field_type):
        return {"isError": True, "content": [{"type": "text", "text": "Either 'customFieldId' or both 'name' and 'field_type' are required."}]}

    if field_id:
        return client.call(f"{ENDPOINTS.CUSTOM_FIELDS}{field_id}/", "GET")
    else:
        query_params = {"name": name, "field_type": field_type}
        return client.call(ENDPOINTS.CUSTOM_FIELDS, "GET", query=query_params)

def create_custom_field(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new custom field.
    
    Args:
        params: Dictionary with:
            - accountName (optional): The account to use
            - name: Name of the custom field (required)
            - field_type: Type of the field (required, e.g., "Text", "Number", "Boolean", "Multi-choice")
            - choices: For "Multi-choice" type, a list of options (optional)
            
    Returns:
        Dictionary with created custom field details
    """
    # Ensure required fields are provided
    if "name" not in params:
        return {"isError": True, "content": [{"type": "text", "text": "'name' field is required."}]}
    if "field_type" not in params:
        return {"isError": True, "content": [{"type": "text", "text": "'field_type' is required."}]}

    client = McpApiClient(params.get("accountName"))
    request_data = {"name": params["name"], "field_type": params["field_type"]}
    
    # Add choice array for Multi-choice type fields
    if params["field_type"] == "Multi-choice" and "choices" in params:
        request_data["choice"] = params["choices"]

    # Debug output to help troubleshoot
    sys.stderr.write(f"[callhub] Creating custom field with params: {request_data}\n")
    return client.call(ENDPOINTS.CUSTOM_FIELDS, "POST", body=request_data)

def update_custom_field(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update an existing custom field by ID.
    
    Args:
        params: Dictionary with:
            - accountName (optional): The account to use
            - customFieldId: ID of the custom field to update
            - name (optional): New name for the custom field
            - options (optional): For "select" type, a list of options
            
    Returns:
        Dictionary with updated custom field details
    """
    field_id = params.get("customFieldId")
    if not field_id:
        return {"isError": True, "content": [{"type": "text", "text": "'customFieldId' is required."}]}

    client = McpApiClient(params.get("accountName"))
    update_data = {}
    if "name" in params:
        update_data["name"] = params["name"]
    if "options" in params:
        update_data["options"] = params["options"]

    # Debug output to help troubleshoot
    sys.stderr.write(f"[callhub] Updating custom field {field_id} with params: {update_data}\n")
    return client.call(f"{ENDPOINTS.CUSTOM_FIELDS}{field_id}/", "PUT", body=update_data)

def delete_custom_field(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Delete a custom field by ID.
    
    Args:
        params: Dictionary with:
            - accountName (optional): The account to use
            - customFieldId: ID of the custom field to delete
            
    Returns:
        Dictionary with deletion status
    """
    field_id = params.get("customFieldId")
    if not field_id:
        return {"isError": True, "content": [{"type": "text", "text": "'customFieldId' is required."}]}

    client = McpApiClient(params.get("accountName"))
    result = client.call(f"{ENDPOINTS.CUSTOM_FIELDS}{field_id}/", "DELETE")
    
    if not result.get("isError"):
        return {"deleted": True, "customFieldId": field_id}
    return result

def get_custom_field_info(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get custom field information by filtering all custom fields.
    .

    Args:
        account_name (str): The account to use
        custom_field_id (str): ID of the custom field to retrieve

    Returns:
        dict: The custom field information or error response
    """
    custom_field_id = params.get("customFieldId")
    if not custom_field_id:
        return {"isError": True, "content": [{"type": "text", "text": "'customFieldId' is required."}]}

    list_params = {"accountName": params.get("accountName")}
    # Call the list_custom_fields endpoint
    result = list_custom_fields(list_params)
    
    if result.get("isError"):
        return result
    
    # Handle string response (concatenated JSON objects)
    if isinstance(result, str):
        sys.stderr.write(f"[callhub] Got a string response: {result[:100]}...\n")
        try:
            # Split the string by "}{"
            parts = result.split("}{")
            sys.stderr.write(f"[callhub] Split into {len(parts)} parts\n")
            
            for i, part in enumerate(parts):
                # Add closing brace to all except last part
                if i < len(parts) - 1 and not part.endswith("}"):
                    part += "}"
                # Add opening brace to all except first part
                if i > 0 and not part.startswith("{"):
                    part = "{" + part
                    
                sys.stderr.write(f"[callhub] Processing part {i+1}/{len(parts)}: {part[:50]}...\n")
                    
                # Try to parse as JSON
                try:
                    field_obj = json.loads(part)
                    sys.stderr.write(f"[callhub] Parsed JSON: id={field_obj.get('id')}\n")
                    if str(field_obj.get("id")) == str(custom_field_id):
                        sys.stderr.write(f"[callhub] Found matching field!\n")
                        return field_obj
                except json.JSONDecodeError as e:
                    sys.stderr.write(f"[callhub] JSON decode error: {str(e)}\n")
                    continue
            
            sys.stderr.write(f"[callhub] No matching field found\n")
        except Exception as e:
            sys.stderr.write(f"[callhub] Error parsing custom fields: {str(e)}\n")
            return {"isError": True, "content": [{"type": "text", "text": f"Error processing custom fields: {str(e)}"}]}
    
    for field in result.get("results", []):
        if str(field.get("id")) == str(custom_field_id):
            return field
    
    return {"isError": True, "content": [{"type": "text", "text": f"Custom field with ID {custom_field_id} not found"}]}

def update_contact_custom_field(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a custom field value for a specific contact.
    
    Args:
        params: Dictionary with:
            - accountName (optional): The account to use
            - contactId: ID of the contact
            - customFieldId: ID of the custom field
            - value: New value for the custom field
            
    Returns:
        Dictionary with operation status
    """
    contact_id = params.get("contactId")
    field_id = params.get("customFieldId")
    value = params.get("value")
    
    if not contact_id or not field_id:
        return {"isError": True, "content": [{"type": "text", "text": "Both 'contactId' and 'customFieldId' are required."}]}
    # Value can be None to clear the field, but must be provided as a parameter
    if "value" not in params:
        return {"isError": True, "content": [{"type": "text", "text": "'value' parameter is required."}]}

    client = McpApiClient(params.get("accountName"))

    # First, get the contact to get the current data and the field name
    contact_result = client.call(f"{ENDPOINTS.CONTACTS_V1}{contact_id}/", "GET")
    if contact_result.get("isError"):
        return contact_result
        
    field_info_params = {"accountName": params.get("accountName"), "customFieldId": field_id}
    # Use our new helper function instead of direct getCustomField
    custom_field = get_custom_field_info(field_info_params)
    if custom_field.get("isError"):
        return custom_field
    
    # Extract the field name
    field_name = custom_field.get("name")
    if not field_name:
        return {"isError": True, "content": [{"type": "text", "text": f"Custom field with ID {field_id} has no name"}]}

    # Now we have the field name, update the contact
    # Start with the basic required field - contact phone number
    # Add the custom field value
    update_data = {"contact": contact_result.get("contact"), field_name: value}
    
    # Debug output
    sys.stderr.write(f"[callhub] Updating contact {contact_id} with custom field '{field_name}' = {value}\n")
    sys.stderr.write(f"[callhub] Request URL: v1/contacts/{contact_id}/\n")
    sys.stderr.write(f"[callhub] Request payload: {update_data}\n")

    # Make the API call to update the contact
    result = client.call(f"{ENDPOINTS.CONTACTS_V1}{contact_id}/", "PUT", body=update_data)

    # If successful, standardize the response
    if not result.get("isError"):
        return {
            "success": True,
            "message": f"Custom field '{field_name}' updated for contact {contact_id}",
            "contactId": contact_id,
            "customFieldId": field_id,
            "value": value
        }
    
    # If failed, return the error
    return result
