"""Tool wrappers for Tag operations."""
from typing import Optional, List
from callhub.tags import (
    list_tags,
    get_tag,
    create_tag,
    update_tag,
    delete_tag,
    add_tag_to_contact,
    remove_tag_from_contact,
)


def register(server):
    @server.tool(name="listTags", description="List all tags with optional pagination.")
    def list_tags_tool(
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
            return list_tags(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getTag", description="Retrieve a single tag by ID.")
    def get_tag_tool(
        account: Optional[str] = None,
        tagId: Optional[str] = None
    ) -> dict:
        try:
            params = {"tagId": tagId}
            if account:
                params["accountName"] = account
            return get_tag(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="createTag", description="Create a new tag.")
    def create_tag_tool(
        account: Optional[str] = None,
        name: str = None
    ) -> dict:
        try:
            params = {"name": name}
            if account:
                params["accountName"] = account

            return create_tag(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="updateTag", description="Update an existing tag by ID.")
    def update_tag_tool(
        account: Optional[str] = None,
        tagId: str = None,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> dict:
        try:
            params = {"tagId": tagId}
            if account:
                params["accountName"] = account
            if name:
                params["name"] = name
            if description:
                params["description"] = description

            return update_tag(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="deleteTag", description="Delete a tag by ID.")
    def delete_tag_tool(
        account: Optional[str] = None,
        tagId: str = None
    ) -> dict:
        try:
            params = {"tagId": tagId}
            if account:
                params["accountName"] = account

            return delete_tag(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="addTagToContact", description="Add tags to a contact by specifying tag names.")
    def add_tag_to_contact_tool(
        account: Optional[str] = None,
        contactId: str = None,
        tagNames: List[str] = None
    ) -> dict:
        try:
            params = {
                "contactId": contactId,
                "tagNames": tagNames
            }
            if account:
                params["accountName"] = account

            return add_tag_to_contact(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="removeTagFromContact", description="Remove a tag from a contact.")
    def remove_tag_from_contact_tool(
        account: Optional[str] = None,
        contactId: str = None,
        tagId: str = None
    ) -> dict:
        try:
            params = {
                "contactId": contactId,
                "tagId": tagId
            }
            if account:
                params["accountName"] = account

            return remove_tag_from_contact(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}
