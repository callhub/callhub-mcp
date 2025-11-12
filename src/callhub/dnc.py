# File: src/callhub/dnc.py

from typing import Dict, Any
from .client import McpApiClient
from .constants import ENDPOINTS

def create_dnc_contact(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new DNC contact.
    
    Args:
        account (str, optional): The CallHub account name to use. Defaults to 'default'.
        dnc (str, required): URL of the DNC list that the phone number belongs to.
                             Format: 'https://api.callhub.io/v1/dnc_lists/{id}/'
        phone_number (str, required): Phone number of the contact in E.164 format.
        category (int, optional): 1 for call opt-out only, 2 for text opt-out only,
                                 3 for both call and text opt-out. Defaults to 3.
        
    Returns:
        dict: API response containing the created DNC contact information.
    """
    dnc = params.get("dnc")
    phone_number = params.get("phone_number")
    category = params.get("category", 3)

    if not dnc:
        return {"isError": True, "content": [{"text": "'dnc' is required."}]}
    if not phone_number:
        return {"isError": True, "content": [{"text": "'phone_number' is required."}]}

    client = McpApiClient(params.get("account"))
    data = {"dnc": dnc, "phone_number": phone_number, "category": category}
    return client.call(ENDPOINTS.DNC_CONTACTS, "POST", form_data=data)

def list_dnc_contacts(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retrieve a list of DNC contacts with optional pagination.
    
    Args:
        account (str, optional): The CallHub account name to use. Defaults to 'default'.
        page (int, optional): Page number for pagination. Defaults to 1.
        pageSize (int, optional): Number of items per page. Defaults to 10.
        allPages (bool, optional): If True, fetch all pages. Defaults to False.
        
    Returns:
        dict: API response containing DNC contacts with url, dnc, and phone_number fields.
    """
    client = McpApiClient(params.get("account"))
    all_pages = params.get("allPages", False)

    if not all_pages:
        query_params = {}
        if params.get("page"):
            query_params["page"] = params["page"]
        if params.get("pageSize"):
            query_params["page_size"] = params["pageSize"]
        return client.call(ENDPOINTS.DNC_CONTACTS, "GET", query=query_params)

    all_results = []
    current_page = 1
    while True:
        query_params = {"page": current_page}
        if params.get("pageSize"):
            query_params["page_size"] = params["pageSize"]
        
        result = client.call(ENDPOINTS.DNC_CONTACTS, "GET", query=query_params)
        if result.get("isError"):
            return result
        
        all_results.extend(result.get("results", []))
        if not result.get("next"):
            break
        current_page += 1
    
    return {"count": len(all_results), "results": all_results}

def update_dnc_contact(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update an existing DNC contact by ID.
    
    Args:
        account (str, optional): The CallHub account name to use. Defaults to 'default'.
        contactId (str, required): The ID of the DNC contact to update.
        dnc (str, required): URL of the DNC list that the contact belongs to.
                            Format: 'https://api.callhub.io/v1/dnc_lists/{id}/'
        phone_number (str, required): Phone number of the contact in E.164 format.
        
    Returns:
        dict: API response containing the updated DNC contact information.
        
    Note:
        Both 'dnc' and 'phone_number' fields are required by the CallHub API.
        Omitting either field will result in a 400 Bad Request error.
    """
    contact_id = params.get("contactId")
    dnc = params.get("dnc")
    phone_number = params.get("phone_number")

    if not contact_id:
        return {"isError": True, "content": [{"text": "'contactId' is required."}]}
    if not dnc:
        return {"isError": True, "content": [{"text": "'dnc' is required."}]}
    if not phone_number:
        return {"isError": True, "content": [{"text": "'phone_number' is required."}]}

    client = McpApiClient(params.get("account"))
    data = {"dnc": dnc, "phone_number": phone_number}
    return client.call(f"{ENDPOINTS.DNC_CONTACTS}{contact_id}/", "PUT", form_data=data)

def delete_dnc_contact(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Delete a DNC contact by ID.
    
    Args:
        account (str, optional): The CallHub account name to use. Defaults to 'default'.
        contactId (str, required): The ID of the DNC contact to delete.
        
    Returns:
        dict: API response indicating success or failure.
    """
    contact_id = params.get("contactId")
    if not contact_id:
        return {"isError": True, "content": [{"text": "'contactId' is required."}]}

    client = McpApiClient(params.get("account"))
    return client.call(f"{ENDPOINTS.DNC_CONTACTS}{contact_id}/", "DELETE")

def create_dnc_list(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new DNC list.
    
    Args:
        account (str, optional): The CallHub account name to use. Defaults to 'default'.
        name (str, required): Name of the DNC list to be created.
        
    Returns:
        dict: API response containing the created DNC list information.
    """
    name = params.get("name")
    if not name:
        return {"isError": True, "content": [{"text": "'name' is required."}]}

    client = McpApiClient(params.get("account"))
    data = {"name": name}
    return client.call(ENDPOINTS.DNC_LISTS, "POST", form_data=data)

def list_dnc_lists(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retrieve a list of DNC lists with optional pagination.
    
    Args:
        account (str, optional): The CallHub account name to use. Defaults to 'default'.
        page (int, optional): Page number for pagination. Defaults to 1.
        pageSize (int, optional): Number of items per page. Defaults to 10.
        allPages (bool, optional): If True, fetch all pages. Defaults to False.
        
    Returns:
        dict: API response containing DNC lists with url, owner, and name fields.
    """
    client = McpApiClient(params.get("account"))
    all_pages = params.get("allPages", False)

    if not all_pages:
        query_params = {}
        if params.get("page"):
            query_params["page"] = params["page"]
        if params.get("pageSize"):
            query_params["page_size"] = params["pageSize"]
        return client.call(ENDPOINTS.DNC_LISTS, "GET", query=query_params)

    all_results = []
    current_page = 1
    while True:
        query_params = {"page": current_page}
        if params.get("pageSize"):
            query_params["page_size"] = params["pageSize"]

        result = client.call(ENDPOINTS.DNC_LISTS, "GET", query=query_params)
        if result.get("isError"):
            return result
        
        all_results.extend(result.get("results", []))
        if not result.get("next"):
            break
        current_page += 1
    
    return {"count": len(all_results), "results": all_results}

def update_dnc_list(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update an existing DNC list by ID.
    
    Args:
        account (str, optional): The CallHub account name to use. Defaults to 'default'.
        listId (str, required): The ID of the DNC list to update.
        name (str, required): The new name for the DNC list.
        
    Returns:
        dict: API response containing the updated DNC list information.
    """
    list_id = params.get("listId")
    name = params.get("name")

    if not list_id:
        return {"isError": True, "content": [{"text": "'listId' is required."}]}
    if not name:
        return {"isError": True, "content": [{"text": "'name' is required."}]}

    client = McpApiClient(params.get("account"))
    data = {"name": name}
    return client.call(f"{ENDPOINTS.DNC_LISTS}{list_id}/", "PUT", form_data=data)

def delete_dnc_list(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Delete a DNC list by ID.
    
    Args:
        account (str, optional): The CallHub account name to use. Defaults to 'default'.
        listId (str, required): The ID of the DNC list to delete.
        
    Returns:
        dict: API response indicating success or failure.
    """
    list_id = params.get("listId")
    if not list_id:
        return {"isError": True, "content": [{"text": "'listId' is required."}]}

    client = McpApiClient(params.get("account"))
    return client.call(f"{ENDPOINTS.DNC_LISTS}{list_id}/", "DELETE")