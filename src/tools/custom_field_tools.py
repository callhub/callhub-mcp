"""Tool wrappers for Custom Field operations."""
from typing import Optional, List, Any
from callhub.custom_fields import (
    list_custom_fields,
    get_custom_field,
    create_custom_field,
    update_custom_field,
    delete_custom_field,
    update_contact_custom_field,
)


def register(server):
    @server.tool(name="listCustomFields", description="List all custom fields with optional pagination.")
    def list_custom_fields_tool(
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
            return list_custom_fields(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getCustomField", description="Retrieve a single custom field by ID.")
    def get_custom_field_tool(
        account: Optional[str] = None,
        customFieldId: Optional[str] = None
    ) -> dict:
        try:
            params = {"customFieldId": customFieldId}
            if account:
                params["accountName"] = account
            return get_custom_field(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="createCustomField", description="Create a new custom field with name, type, and optional choices for Multi-choice type.")
    def create_custom_field_tool(
        account: Optional[str] = None,
        name: str = None,
        field_type: str = None,
        choices: Optional[List[str]] = None
    ) -> dict:
        try:
            params = {
                "name": name,
                "field_type": field_type
            }
            if account:
                params["accountName"] = account
            if choices and field_type == "Multi-choice":
                params["choices"] = choices

            return create_custom_field(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="updateCustomField", description="Update an existing custom field by ID.")
    def update_custom_field_tool(
        account: Optional[str] = None,
        customFieldId: str = None,
        name: Optional[str] = None,
        options: Optional[List[str]] = None
    ) -> dict:
        try:
            params = {"customFieldId": customFieldId}
            if account:
                params["accountName"] = account
            if name:
                params["name"] = name
            if options:
                params["options"] = options

            return update_custom_field(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="deleteCustomField", description="Delete a custom field by ID.")
    def delete_custom_field_tool(
        account: Optional[str] = None,
        customFieldId: str = None
    ) -> dict:
        try:
            params = {"customFieldId": customFieldId}
            if account:
                params["accountName"] = account

            return delete_custom_field(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="updateContactCustomField", description="Update a custom field value for a contact.")
    def update_contact_custom_field_tool(
        account: Optional[str] = None,
        contactId: str = None,
        customFieldId: str = None,
        value: Any = None
    ) -> dict:
        try:
            params = {
                "contactId": contactId,
                "customFieldId": customFieldId,
                "value": value
            }
            if account:
                params["accountName"] = account

            return update_contact_custom_field(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}
