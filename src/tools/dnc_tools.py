"""Tool wrappers for DNC (Do Not Call) operations."""
from typing import Optional, List, Dict, Any
from callhub.dnc import (
    create_dnc_contact,
    list_dnc_contacts,
    update_dnc_contact,
    delete_dnc_contact,
    create_dnc_list,
    list_dnc_lists,
    update_dnc_list,
    delete_dnc_list,
    add_contacts_to_suppression_list,
)


def register(server):
    @server.tool(name="createDncContact", description="Create a new DNC contact with the specified phone number.")
    def create_dnc_contact_tool(
        account: Optional[str] = None,
        dnc: str = None, # This is the DNC list URL
        phone_number: str = None,
        category: int = 3
    ) -> dict:
        """Create a new DNC contact.

        Args:
            account: The CallHub account name to use. Defaults to 'default'.
            dnc: URL of the DNC list that the phone number belongs to. Format: 'https://api.callhub.io/v1/dnc_lists/{id}/'
            phone_number: Phone number of the contact in E.164 format.
            category: 1 for call opt-out only, 2 for text opt-out only, 3 for both call and text opt-out. Defaults to 3.
        """
        try:
            params = {}
            if account: params["accountName"] = account
            if dnc: params["dnc"] = dnc
            if phone_number: params["phone_number"] = phone_number
            if category is not None: params["category"] = category
            return create_dnc_contact(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="listDncContacts", description="List contacts in the DNC (Do Not Call) list with optional pagination.")
    def list_dnc_contacts_tool(
        account: Optional[str] = None,
        page: Optional[int] = None,
        pageSize: Optional[int] = None,
        allPages: bool = False
    ) -> dict:
        try:
            params = {}
            if account: params["accountName"] = account
            if page is not None: params["page"] = page
            if pageSize is not None: params["pageSize"] = pageSize
            params["allPages"] = allPages
            return list_dnc_contacts(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="updateDncContact", description="Update an existing DNC contact by ID.")
    def update_dnc_contact_tool(
        account: Optional[str] = None,
        contactId: str = None, # DNC Contact ID (this is the 'id' or 'url' from listDncContacts)
        dnc: Optional[str] = None, # DNC List URL
        phone_number: Optional[str] = None # Phone number
    ) -> dict:
        try:
            params = {}
            if account: params["accountName"] = account
            if contactId: params["contactId"] = contactId
            if dnc: params["dnc"] = dnc
            if phone_number: params["phone_number"] = phone_number
            return update_dnc_contact(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="deleteDncContact", description="Delete a DNC contact by ID.")
    def delete_dnc_contact_tool(
        account: Optional[str] = None,
        contactId: str = None # DNC Contact ID
    ) -> dict:
        try:
            params = {}
            if account: params["accountName"] = account
            if contactId: params["contactId"] = contactId
            return delete_dnc_contact(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="createDncList", description="Create a new DNC list.")
    def create_dnc_list_tool(
        account: Optional[str] = None,
        name: str = None
    ) -> dict:
        try:
            params = {}
            if account: params["accountName"] = account
            if name: params["name"] = name
            return create_dnc_list(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="listDncLists", description="List all DNC lists with optional pagination.")
    def list_dnc_lists_tool(
        account: Optional[str] = None,
        page: Optional[int] = None,
        pageSize: Optional[int] = None,
        allPages: bool = False
    ) -> dict:
        try:
            params = {}
            if account: params["accountName"] = account
            if page is not None: params["page"] = page
            if pageSize is not None: params["pageSize"] = pageSize
            if allPages: params["allPages"] = allPages
            return list_dnc_lists(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="updateDncList", description="Update an existing DNC list by ID.")
    def update_dnc_list_tool(
        account: Optional[str] = None,
        listId: str = None, # DNC List ID
        name: str = None
    ) -> dict:
        try:
            params = {}
            if account: params["accountName"] = account
            if listId: params["listId"] = listId
            if name: params["name"] = name
            return update_dnc_list(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="deleteDncList", description="Delete a DNC list by ID.")
    def delete_dnc_list_tool(
        account: Optional[str] = None,
        listId: str = None # DNC List ID
    ) -> dict:
        try:
            params = {}
            if account: params["accountName"] = account
            if listId: params["listId"] = listId
            return delete_dnc_list(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="addContactsToSuppressionList", description="Add contacts to a suppression list. Each contact should have 'phone_number' and 'mobile_number' keys. Returns 207 Multi-Status.")
    def add_contacts_to_suppression_list_tool(
        account: Optional[str] = None,
        list_id: str = None,
        contacts: List[Dict[str, Any]] = None,
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if list_id:
                params["list_id"] = list_id
            if contacts is not None:
                params["contacts"] = contacts
            return add_contacts_to_suppression_list(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}
