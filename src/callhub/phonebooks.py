# phonebooks.py
"""
Phonebook management functions for CallHub API.
"""

import sys
from typing import Dict, Any, List

from .client import McpApiClient

def list_phonebooks(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    List phonebooks with optional pagination.
    
    Args:
        params: Dictionary with:
            - accountName (optional): The account to use
            - page (optional): Page number for pagination
            - pageSize (optional): Number of results per page
            
    Returns:
        Dictionary with phonebook results
    """
    client = McpApiClient(params.get("accountName"))
    query = {}
    if params.get("page"):
        query["page"] = params["page"]
    if params.get("pageSize"):
        query["page_size"] = params["pageSize"]
    return client.call("/v1/phonebooks/", "GET", query=query)

def get_phonebook(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retrieve a single phonebook by ID.
    
    Args:
        params: Dictionary with:
            - accountName (optional): The account to use
            - phonebookId: ID of the phonebook to retrieve
            
    Returns:
        Dictionary with phonebook details
    """
    pb_id = params.get("phonebookId")
    if not pb_id:
        return {"isError": True, "content": [{"type": "text", "text": "'phonebookId' is required."}]}

    client = McpApiClient(params.get("accountName"))
    return client.call(f"/v1/phonebooks/{pb_id}/", "GET")

def create_phonebook(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new phonebook.
    
    Args:
        params: Dictionary with:
            - accountName (optional): The account to use
            - name: Name of the phonebook (required)
            - description (optional): Description of the phonebook
            
    Returns:
        Dictionary with created phonebook details
    """
    if "name" not in params:
        return {"isError": True, "content": [{"type": "text", "text": "'name' field is required."}]}

    sys.stderr.write(f"[callhub] Creating phonebook with params: {params}\n")
    client = McpApiClient(params.pop("accountName", None))
    return client.call("/v1/phonebooks/", "POST", form_data=params)

def update_phonebook(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update an existing phonebook by ID.
    
    Args:
        params: Dictionary with:
            - accountName (optional): The account to use
            - phonebookId: ID of the phonebook to update
            - name (optional): New name for the phonebook
            - description (optional): New description for the phonebook
            
    Returns:
        Dictionary with updated phonebook details
    """
    pb_id = params.pop("phonebookId", None)
    if not pb_id:
        return {"isError": True, "content": [{"type": "text", "text": "'phonebookId' is required."}]}

    sys.stderr.write(f"[callhub] Updating phonebook {pb_id} with params: {params}\n")
    client = McpApiClient(params.pop("accountName", None))
    return client.call(f"/v1/phonebooks/{pb_id}/", "PATCH", form_data=params)

def delete_phonebook(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Delete a phonebook by ID.
    
    Args:
        params: Dictionary with:
            - accountName (optional): The account to use
            - phonebookId: ID of the phonebook to delete
            
    Returns:
        Dictionary with deletion status
    """
    pb_id = params.get("phonebookId")
    if not pb_id:
        return {"isError": True, "content": [{"type": "text", "text": "'phonebookId' is required."}]}

    client = McpApiClient(params.get("accountName"))
    result = client.call(f"/v1/phonebooks/{pb_id}/", "DELETE")
    
    if not result.get("isError"):
        return {"deleted": True, "phonebookId": pb_id}
    return result

def add_contacts_to_phonebook(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add existing contacts to a phonebook.
    
    Args:
        params: Dictionary with:
            - accountName (optional): The account to use
            - phonebookId: ID of the phonebook
            - contactIds: List of contact IDs to add
            
    Returns:
        Dictionary with operation status
    """
    pb_id = params.get("phonebookId")
    contact_ids = params.get("contactIds")
    if not pb_id or contact_ids is None:
        return {"isError": True, "content": [{"type": "text", "text": "Both 'phonebookId' and 'contactIds' are required."}]}

    contact_ids_str = [str(cid) for cid in contact_ids]
    sys.stderr.write(f"[callhub] Adding contacts {contact_ids_str} to phonebook {pb_id}\n")

    client = McpApiClient(params.get("accountName"))
    body = {"contact_ids": contact_ids_str}
    return client.call(f"/v1/phonebooks/{pb_id}/contacts/", "POST", body=body)

def remove_contact_from_phonebook(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove a contact from a phonebook.
    
    Args:
        params: Dictionary with:
            - accountName (optional): The account to use
            - phonebookId: ID of the phonebook
            - contactId: ID of the contact to remove
            
    Returns:
        Dictionary with operation status
    """
    pb_id = params.get("phonebookId")
    cid = params.get("contactId")
    if not pb_id or not cid:
        return {"isError": True, "content": [{"type": "text", "text": "Both 'phonebookId' and 'contactId' are required."}]}

    client = McpApiClient(params.get("accountName"))
    body = {"contact_ids": [str(cid)]}
    result = client.call(f"/v1/phonebooks/{pb_id}/contacts/", "DELETE", body=body)
    
    if not result.get("isError"):
        try:
            # Get the phonebook count before and after
            count_before = get_phonebook_count({"accountName": params.get("accountName"), "phonebookId": pb_id})

            # Verify contact was removed by searching for it in the phonebook
            # (This would require additional code to check specific contacts in a phonebook)
            return {"removed": True, "phonebookId": pb_id, "contactId": cid}
        except Exception as e:
            sys.stderr.write(f"[callhub] Warning: Unable to verify contact removal: {str(e)}\n")
            return {"removed": True, "phonebookId": pb_id, "contactId": cid}
    
    return result

def get_phonebook_count(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get the total number of contacts in a phonebook.
    
    Args:
        params: Dictionary with:
            - accountName (optional): The account to use
            - phonebookId: ID of the phonebook to count
            
    Returns:
        Dictionary with contact counts
    """
    pb_id = params.get("phonebookId")
    if not pb_id:
        return {"isError": True, "content": [{"type": "text", "text": "'phonebookId' is required."}]}

    client = McpApiClient(params.get("accountName"))
    return client.call(f"/v1/phonebooks/{pb_id}/numbers_count/", "GET")

def get_phonebook_contacts(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get contacts in a specific phonebook with pagination.
    
    Args:
        params: Dictionary with:
            - accountName (optional): The account to use
            - phonebookId: ID of the phonebook
            - page (optional): Page number
            - pageSize (optional): Results per page
            - allPages (optional): If True, fetch all pages
            
    Returns:
        Dictionary with contacts in the phonebook
    """
    pb_id = params.get("phonebookId")
    if not pb_id:
        return {"isError": True, "content": [{"type": "text", "text": "'phonebookId' is required."}]}

    client = McpApiClient(params.get("accountName"))
    all_pages = params.get("allPages", False)

    if not all_pages:
        query = {}
        if params.get("page"):
            query["page"] = params["page"]
        if params.get("pageSize"):
            query["page_size"] = params["pageSize"]
        return client.call(f"/v1/phonebooks/{pb_id}/contacts/", "GET", query=query)

    results = []
    page = 1
    while True:
        query = {"page": page}
        if params.get("pageSize"):
            query["page_size"] = params["pageSize"]
        
        result = client.call(f"/v1/phonebooks/{pb_id}/contacts/", "GET", query=query)
        if result.get("isError"):
            return result
        
        results.extend(result.get("results", []))
        if not result.get("next"):
            break
        page += 1
            
    return {"results": results}
