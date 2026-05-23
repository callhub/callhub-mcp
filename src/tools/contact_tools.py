"""Tool wrappers for Contact operations."""
from typing import Optional, Dict
from callhub.contacts import (
    list_contacts,
    get_contact,
    create_contact,
    create_contacts_bulk,
    update_contact,
    delete_contact,
    get_contact_fields,
)
from callhub.utils import parse_input_fields


def register(server):
    @server.tool(name="listContacts", description="List contacts with pagination, filtering, or fetch all.")
    def list_contacts_tool(
        account: Optional[str] = None,
        page: Optional[int] = None,
        pageSize: Optional[int] = None,
        filters: Optional[dict] = None,
        allPages: bool = False
    ) -> dict:
        try:
            params: dict = {"allPages": allPages}
            if account:
                params["accountName"] = account
            if page is not None:
                params["page"] = page
            if pageSize is not None:
                params["pageSize"] = pageSize
            if filters is not None:
                params["filters"] = filters
            return list_contacts(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getContact", description="Retrieve a single contact by ID.")
    def get_contact_tool(
        account: Optional[str] = None,
        contactId: Optional[str] = None
    ) -> dict:
        try:
            params: dict = {"contactId": contactId}
            if account:
                params["accountName"] = account
            return get_contact(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="createContact", description="Create a new contact. Pass contact details as URL-encoded string (e.g., 'contact=1234567890&first_name=John&last_name=Doe').")
    def create_contact_tool(
        account: Optional[str] = None,
        contact_fields: str = None
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account

            # Parse contact_fields using our improved parser
            if contact_fields:
                parsed_fields = parse_input_fields(contact_fields)
                params.update(parsed_fields)

            return create_contact(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="createContactsBulk", description="Create multiple contacts by uploading a CSV file or providing a CSV URL. Requires phonebook_id parameter. Optional country_choice ('file' or 'custom') and country_iso (when country_choice is 'custom'). Note: This API has a rate limit of 1 call per minute.")
    def create_contacts_bulk_tool(
        account: Optional[str] = None,
        phonebook_id: Optional[str] = None,  # Added phonebook_id parameter
        csv_file_path: Optional[str] = None,
        csv_url: Optional[str] = None,
        mapping: Optional[Dict[str, int]] = None,
        country_choice: Optional[str] = None,  # Added country_choice parameter
        country_iso: Optional[str] = None      # Added country_iso parameter
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account

            # Add the phonebook_id parameter
            if phonebook_id:
                params["phonebook_id"] = phonebook_id

            # Add country parameters
            if country_choice:
                params["country_choice"] = country_choice

            if country_iso:
                params["country_iso"] = country_iso

            if csv_file_path:
                params["csv_file_path"] = csv_file_path

            if csv_url:
                params["csv_url"] = csv_url

            if mapping:
                params["mapping"] = mapping

            result = create_contacts_bulk(params)

            # Handle rate limiting with a user-friendly message
            if "isRateLimited" in result:
                retry_after = result.get("retryAfter", 60)
                message = result.get("message", f"The bulk create contacts API is currently rate limited. Please try again in {retry_after} seconds.")

                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": message},
                        {"type": "text", "text": f"The API can only be called once per minute. Current wait time: {retry_after} seconds."}
                    ]
                }

            return result
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="updateContact", description="Update a contact by phone number. Pass fields as URL-encoded string (e.g., 'contact=12015550123&mobile=12015550124'). Note: May create a new contact if multiple contacts have the same phone number.")
    def update_contact_tool(
        account: Optional[str] = None,
        update_fields: str = None
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account

            # Parse update_fields using our improved parser
            if update_fields:
                parsed_fields = parse_input_fields(update_fields)
                params.update(parsed_fields)

            # Ensure we have the contact phone number
            if "contact" not in params:
                return {"isError": True, "content": [{"type": "text", "text": "The 'contact' field (phone number) is required to identify which contact to update."}]}

            return update_contact(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="deleteContact", description="Delete a contact by ID.")
    def delete_contact_tool(
        account: Optional[str] = None,
        contactId: Optional[str] = None
    ) -> dict:
        try:
            params = {"contactId": contactId}
            if account:
                params["accountName"] = account
            return delete_contact(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getContactFields", description="List all available contact fields for this account.")
    def get_contact_fields_tool(
        account: Optional[str] = None
    ) -> dict:
        try:
            params: dict = {}
            if account:
                params["accountName"] = account
            return get_contact_fields(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}
