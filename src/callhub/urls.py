"""Shortened URL management functions for CallHub API."""
from typing import Dict, Any

from .client import McpApiClient


def get_shortened_url(params: Dict[str, Any]) -> Dict[str, Any]:
    """Get details of a shortened URL by its short code.

    Args:
        params: Dictionary with:
            - accountName (optional): The account to use
            - shortCode: The short code of the URL to retrieve

    Returns:
        Dictionary with shortened URL details
    """
    short_code = params.get("shortCode")
    if not short_code:
        return {"isError": True, "content": [{"type": "text", "text": "'shortCode' is required."}]}

    client = McpApiClient(params.get("accountName"))
    return client.call(f"/v2/shortened-urls/{short_code}/", "GET")


def list_shortened_urls(params: Dict[str, Any]) -> Dict[str, Any]:
    """List all shortened URLs with optional pagination.
    
    Args:
        params: Dictionary with:
            - accountName (optional): The account to use
            - page (optional): Page number for pagination
            - pageSize (optional): Number of items per page

    Returns:
        Dictionary with list of shortened URLs
    """
    client = McpApiClient(params.get("accountName"))
    query = {}
    if params.get("page"):
        query["page"] = params["page"]
    if params.get("pageSize"):
        query["page_size"] = params["pageSize"]
    
    return client.call("v2/shortened-urls/", "GET", query=query)