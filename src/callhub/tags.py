# tags.py
"""
Tag management functions for CallHub API.
"""

import sys
import json
from typing import Dict, Any, List

from .client import McpApiClient

def list_tags(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    List all tags for the account.
    
    Args:
        params: Dictionary with:
            - accountName (optional): The account to use
            - page (optional): Page number for pagination
            - pageSize (optional): Number of results per page
            
    Returns:
        Dictionary with tag results
    """
    client = McpApiClient(params.get("accountName"))
    query = {}
    if params.get("page"):
        query["page"] = params["page"]
    if params.get("pageSize"):
        query["page_size"] = params["pageSize"]
    return client.call("/v1/tags/", "GET", query=query)

def get_tag(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retrieve a single tag by ID.
    
    Args:
        params: Dictionary with:
            - accountName (optional): The account to use
            - tagId: ID of the tag to retrieve
            
    Returns:
        Dictionary with tag details
    """
    tag_id = params.get("tagId")
    if not tag_id:
        return {"isError": True, "content": [{"type": "text", "text": "'tagId' is required."}]}

    client = McpApiClient(params.get("accountName"))
    return client.call(f"/v1/tags/{tag_id}/", "GET")

def create_tag(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new tag.
    
    Args:
        params: Dictionary with:
            - accountName (optional): The account to use
            - name: Name of the tag (required)
            
    Returns:
        Dictionary with created tag details
    """
    if "name" not in params:
        return {"isError": True, "content": [{"type": "text", "text": "'name' field is required."}]}

    sys.stderr.write(f"[callhub] Creating tag with params: {params}\n")
    client = McpApiClient(params.get("accountName"))
    request_data = {"tag": params["name"]}
    return client.call("/v2/tags/", "POST", body=request_data)

def update_tag(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update an existing tag by ID.
    
    Args:
        params: Dictionary with:
            - accountName (optional): The account to use
            - tagId: ID of the tag to update
            - name (optional): New name for the tag
            - description (optional): New description
            
    Returns:
        Dictionary with updated tag details
    """
    tag_id = params.get("tagId")
    if not tag_id:
        return {"isError": True, "content": [{"type": "text", "text": "'tagId' is required."}]}

    client = McpApiClient(params.get("accountName"))
    update_data = {}
    if "name" in params:
        update_data["name"] = params["name"]
    if "description" in params:
        update_data["description"] = params["description"]

    sys.stderr.write(f"[callhub] Updating tag {tag_id} with params: {update_data}\n")
    return client.call(f"/v1/tags/{tag_id}/", "PATCH", body=update_data)

def delete_tag(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Delete a tag by ID.
    
    Args:
        params: Dictionary with:
            - accountName (optional): The account to use
            - tagId: ID of the tag to delete
            
    Returns:
        Dictionary with deletion status
    """
    tag_id = params.get("tagId")
    if not tag_id:
        return {"isError": True, "content": [{"type": "text", "text": "'tagId' is required."}]}

    client = McpApiClient(params.get("accountName"))
    result = client.call(f"/v1/tags/{tag_id}/", "DELETE")
    
    if not result.get("isError"):
        return {"deleted": True, "tagId": tag_id}
    return result

def add_tag_to_contact(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add tag(s) to a contact.
    
    Args:
        params: Dictionary with:
            - accountName (optional): The account to use
            - contactId: ID of the contact
            - tagNames: List of tag names to add
            
    Returns:
        Dictionary with operation status
    """
    contact_id = params.get("contactId")
    tag_names = params.get("tagNames")
    
    if not contact_id:
        return {"isError": True, "content": [{"type": "text", "text": "'contactId' is required."}]}
    if not tag_names or not isinstance(tag_names, list):
        return {"isError": True, "content": [{"type": "text", "text": "'tagNames' must be a non-empty list."}]}

    client = McpApiClient(params.get("accountName"))
    
    contact_result = client.call(f"/v1/contacts/{contact_id}/", "GET")
    if contact_result.get("isError"):
        return contact_result
    
    phone_number = contact_result.get("contact")
    existing_tags = contact_result.get("tags", [])
    existing_tag_names = [tag["name"] for tag in existing_tags]
    
    if all(tag_name in existing_tag_names for tag_name in tag_names):
        return {"success": True, "message": f"All tags already exist on contact {contact_id}"}

    all_tag_names = set(existing_tag_names + tag_names)
    all_tag_ids = {str(tag["id"]) for tag in existing_tags}

    tags_result = list_tags({"accountName": params.get("accountName"), "pageSize": 1000})
    if tags_result.get("isError"):
        return tags_result

    available_tags = {tag["name"]: str(tag["id"]) for tag in tags_result.get("results", [])}

    for tag_name in all_tag_names:
        if tag_name not in available_tags:
            sys.stderr.write(f"[callhub] Tag '{tag_name}' not found, attempting to create it\n")
            create_result = create_tag({"accountName": params.get("accountName"), "name": tag_name})
            if create_result.get("isError"):
                return {"isError": True, "content": [{"type": "text", "text": f"Failed to create tag '{tag_name}'."}]}
            all_tag_ids.add(str(create_result["id"]))
        else:
            all_tag_ids.add(available_tags[tag_name])

    payload = {"tags": list(all_tag_ids)}
    sys.stderr.write(f"[callhub] Setting tags for contact {contact_id}\n")
    sys.stderr.write(f"[callhub] Request URL: v2/contacts/{contact_id}/taggings/\n")
    sys.stderr.write(f"[callhub] Request payload: {json.dumps(payload)}\n")
    result = client.call(f"/v2/contacts/{contact_id}/taggings/", "PATCH", body=payload)
    
    if not result.get("isError"):
        return {"success": True, "message": f"Tags successfully set for contact {contact_id}"}
    
    sys.stderr.write(f"[callhub] PATCH attempt failed, trying PUT to the contact endpoint\n")
    return result

def remove_tag_from_contact(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove a tag from a contact.
    
    Args:
        params: Dictionary with:
            - accountName (optional): The account to use
            - contactId: ID of the contact
            - tagId: ID of the tag to remove
            
    Returns:
        Dictionary with operation status
    """
    contact_id = params.get("contactId")
    tag_id = params.get("tagId")
    
    if not contact_id or not tag_id:
        return {"isError": True, "content": [{"type": "text", "text": "Both 'contactId' and 'tagId' are required."}]}

    sys.stderr.write(f"[callhub] Removing tag {tag_id} from contact {contact_id}\n")
    client = McpApiClient(params.get("accountName"))
    result = client.call(f"/v1/contacts/{contact_id}/tags/{tag_id}/", "DELETE")
    
    if not result.get("isError"):
        return {"success": True, "message": f"Tag {tag_id} removed from contact {contact_id}"}
    
    return result
