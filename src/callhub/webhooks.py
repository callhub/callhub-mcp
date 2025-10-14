# webhooks.py
"""
Webhook operations for CallHub API.
"""

import sys
from typing import Dict, Any

from .client import McpApiClient
from .constants import ENDPOINTS

def list_webhooks(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    List all webhooks with optional pagination.
    
    Args:
        params: Dictionary containing the following keys:
            accountName (str, optional): The account name to use
            page (int, optional): Page number for pagination
            pageSize (int, optional): Number of items per page
    
    Returns:
        dict: API response containing webhook data or error information
    """
    try:
        client = McpApiClient(params.get("accountName"))
        query_params = {}
        if params.get("page") is not None:
            query_params["page"] = params["page"]
        if params.get("pageSize") is not None:
            query_params["page_size"] = params["pageSize"]
        return client.call(ENDPOINTS.WEBHOOKS, "GET", query=query_params)
    except Exception as e:
        sys.stderr.write(f"[callhub] Error listing webhooks: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def get_webhook(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retrieve a single webhook by ID. Since the API doesn't have a dedicated endpoint
    for retrieving a single webhook, this function gets all webhooks and filters them.
    
    Args:
        params: Dictionary containing the following keys:
            accountName (str, optional): The account name to use
            webhookId (str): The ID of the webhook to retrieve
    
    Returns:
        dict: API response containing webhook data or error information
    """
    try:
        webhook_id = params.get("webhookId")
        if not webhook_id:
            return {"isError": True, "content": [{"type": "text", "text": "'webhookId' is required."}]}

        list_params = {"accountName": params.get("accountName")}
        all_webhooks_response = list_webhooks(list_params)
        
        # Check if there was an error getting all webhooks
        if "isError" in all_webhooks_response:
            return all_webhooks_response
        
        # Extract the webhooks from the response
        all_webhooks = all_webhooks_response.get("results", [])
        
        # Find the webhook with the matching ID
        for webhook in all_webhooks:
            if str(webhook.get("id")) == str(webhook_id):
                return {"result": webhook, "status": "success"}
        
        # If no webhook found with that ID
        return {
            "isError": True, 
            "content": [{"type": "text", "text": f"No webhook found with ID '{webhook_id}'"}]
        }
        
    except Exception as e:
        sys.stderr.write(f"[callhub] Error getting webhook: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def create_webhook(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new webhook.
    
    Args:
        params: Dictionary containing the following keys:
            accountName (str, optional): The account name to use
            event (str): The event type to listen for (e.g., 'vb.transfer', 'sb.reply', 'cc.notes', 'agent.activation')
            target (str): The URL that will receive webhook events
    
    Returns:
        dict: API response containing the created webhook data or error information
    """
    try:
        event = params.get("event_name") or params.get("event")
        target = params.get("target_url") or params.get("target")
        
        if not event:
            return {"isError": True, "content": [{"type": "text", "text": "'event' is required."}]}
        if not target:
            return {"isError": True, "content": [{"type": "text", "text": "'target' is required."}]}
        
        valid_events = ['vb.transfer', 'sb.reply', 'cc.notes', 'agent.activation']
        if event not in valid_events:
            return {"isError": True, "content": [{"type": "text", "text": f"'event' must be one of: {', '.join(valid_events)}"}]}
        
        client = McpApiClient(params.get("accountName"))
        data = {"event": event, "target": target}
        return client.call(ENDPOINTS.WEBHOOKS, "POST", form_data=data)
    except Exception as e:
        sys.stderr.write(f"[callhub] Error creating webhook: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def delete_webhook(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Delete a webhook by ID.
    
    Args:
        params: Dictionary containing the following keys:
            accountName (str, optional): The account name to use
            webhookId (str): The ID of the webhook to delete
    
    Returns:
        dict: API response or error information
    """
    try:
        webhook_id = params.get("webhookId")
        if not webhook_id:
            return {"isError": True, "content": [{"type": "text", "text": "'webhookId' is required."}]}
        
        client = McpApiClient(params.get("accountName"))
        return client.call(f"{ENDPOINTS.WEBHOOKS}{webhook_id}/", "DELETE")
    except Exception as e:
        sys.stderr.write(f"[callhub] Error deleting webhook: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

