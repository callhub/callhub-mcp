"""Tool wrappers for Phonebook operations."""
from typing import Optional
from callhub.phonebooks import (
    list_phonebooks,
    get_phonebook,
    create_phonebook,
    update_phonebook,
    delete_phonebook,
    add_contacts_to_phonebook,
    remove_contact_from_phonebook,
    get_phonebook_count,
    get_phonebook_contacts,
)
from callhub.utils import parse_input_fields


def register(server):
    @server.tool(name="listPhonebooks", description="List phonebooks with optional pagination.")
    def list_phonebooks_tool(
        account: Optional[str] = None,
        page: Optional[int] = None,
        pageSize: Optional[int] = None
    ) -> dict:
        try:
            params: dict = {}
            if account:
                params["accountName"] = account
            if page is not None:
                params["page"] = page
            if pageSize is not None:
                params["pageSize"] = pageSize
            return list_phonebooks(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getPhonebook", description="Retrieve a single phonebook by ID.")
    def get_phonebook_tool(
        account: Optional[str] = None,
        phonebookId: Optional[str] = None
    ) -> dict:
        try:
            params = {"phonebookId": phonebookId}
            if account:
                params["accountName"] = account
            return get_phonebook(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="createPhonebook", description="Create a new phonebook. Pass fields as URL-encoded string (e.g., 'name=MyPhonebook&description=Description').")
    def create_phonebook_tool(
        account: Optional[str] = None,
        phonebook_fields: str = None
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account

            # Parse phonebook_fields using our improved parser
            if phonebook_fields:
                parsed_fields = parse_input_fields(phonebook_fields)
                params.update(parsed_fields)

            return create_phonebook(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="updatePhonebook", description="Update a phonebook. Pass fields as URL-encoded string (e.g., 'name=NewName&description=NewDesc').")
    def update_phonebook_tool(
        account: Optional[str] = None,
        phonebookId: Optional[str] = None,
        update_fields: str = None
    ) -> dict:
        try:
            params = {"phonebookId": phonebookId}
            if account:
                params["accountName"] = account

            # Parse update_fields using our improved parser
            if update_fields:
                parsed_fields = parse_input_fields(update_fields)
                params.update(parsed_fields)

            return update_phonebook(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="deletePhonebook", description="Delete a phonebook by ID.")
    def delete_phonebook_tool(
        account: Optional[str] = None,
        phonebookId: Optional[str] = None
    ) -> dict:
        try:
            params = {"phonebookId": phonebookId}
            if account:
                params["accountName"] = account
            return delete_phonebook(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="addContactsToPhonebook", description="Add (upsert) contacts into a phonebook.")
    def add_contacts_to_phonebook_tool(
        account: str | None = None,
        phonebookId: str | None = None,
        contactIds: list = None
    ) -> dict:
        try:
            # Validate required parameters
            if not phonebookId:
                return {"isError": True, "content": [{"type": "text", "text": "phonebookId is required"}]}
            if not contactIds:
                return {"isError": True, "content": [{"type": "text", "text": "contactIds is required"}]}

            # Ensure contactIds is a list
            if not isinstance(contactIds, list):
                return {"isError": True, "content": [{"type": "text", "text": "contactIds must be a list"}]}

            # Convert all contactIds to strings (API requirement)
            contact_ids_str = [str(cid) for cid in contactIds]

            params = {
                "phonebookId": phonebookId,
                "contactIds": contact_ids_str
            }

            if account:
                params["accountName"] = account

            return add_contacts_to_phonebook(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="removeContactFromPhonebook", description="Remove a contact from a phonebook.")
    def remove_contact_from_phonebook_tool(
        account: Optional[str] = None,
        phonebookId: Optional[str] = None,
        contactId: Optional[str] = None
    ) -> dict:
        try:
            params = {"phonebookId": phonebookId, "contactId": contactId}
            if account:
                params["accountName"] = account
            return remove_contact_from_phonebook(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getPhonebookCount", description="Get total contacts in a phonebook.")
    def get_phonebook_count_tool(
        account: Optional[str] = None,
        phonebookId: Optional[str] = None
    ) -> dict:
        try:
            params = {"phonebookId": phonebookId}
            if account:
                params["accountName"] = account
            return get_phonebook_count(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getPhonebookContacts", description="Get contacts in a phonebook with pagination.")
    def get_phonebook_contacts_tool(
        account: Optional[str] = None,
        phonebookId: Optional[str] = None,
        page: Optional[int] = None,
        pageSize: Optional[int] = None,
        allPages: bool = False
    ) -> dict:
        try:
            params = {
                "phonebookId": phonebookId,
                "allPages": allPages
            }
            if account:
                params["accountName"] = account
            if page is not None:
                params["page"] = page
            if pageSize is not None:
                params["pageSize"] = pageSize

            return get_phonebook_contacts(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}
