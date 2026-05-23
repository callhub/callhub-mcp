"""Tool wrappers for Webhook operations."""
from typing import Optional
from callhub.webhooks import (
    list_webhooks,
    get_webhook,
    create_webhook,
    delete_webhook,
)


def register(server):
    @server.tool(name="listWebhooks", description="List all webhooks with optional pagination.")
    def list_webhooks_tool(
        account: Optional[str] = None,
        page: Optional[int] = None,
        pageSize: Optional[int] = None
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if page is not None:
                params["page"] = page
            if pageSize is not None:
                params["pageSize"] = pageSize

            return list_webhooks(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getWebhook", description="Retrieve a single webhook by ID.")
    def get_webhook_tool(
        account: Optional[str] = None,
        webhookId: str = None
    ) -> dict:
        try:
            params = {"webhookId": webhookId}
            if account:
                params["accountName"] = account

            return get_webhook(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="createWebhook", description="Create a new webhook. Provide an event type string (e.g. 'vb.transfer', 'sb.reply', 'cc.notes', 'agent.activation') and a target URL.")
    def create_webhook_tool(
        account: Optional[str] = None,
        event_name: str = None,
        target_url: str = None
    ) -> dict:
        try:
            # Validate required parameters
            if not event_name:
                return {"isError": True, "content": [{"type": "text", "text": "'event_name' is required."}]}
            if not target_url:
                return {"isError": True, "content": [{"type": "text", "text": "'target_url' is required."}]}

            params = {
                "event_name": event_name,
                "target_url": target_url
            }
            if account:
                params["accountName"] = account

            return create_webhook(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="deleteWebhook", description="Delete a webhook by ID.")
    def delete_webhook_tool(
        account: Optional[str] = None,
        webhookId: str = None
    ) -> dict:
        try:
            # Validate required parameters
            if not webhookId:
                return {"isError": True, "content": [{"type": "text", "text": "'webhookId' is required."}]}

            params = {"webhookId": webhookId}
            if account:
                params["accountName"] = account

            return delete_webhook(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}
