"""Shortened URL management functions for CallHub API."""
import sys
from typing import Dict, Optional

from .auth import get_account_config
from .utils import build_url, api_call, get_auth_headers



def getShortenedUrl(params: dict) -> dict:
    """Get details of a shortened URL by its short code.
    
    Args:
        params: Dictionary with:
            - accountName (optional): The account to use
            - shortCode: The short code of the URL to retrieve
        
    Returns:
        Dictionary with shortened URL details
    """
    account_name = params.get("accountName")
    _, api_key, base_url = get_account_config(account_name)
    
    short_code = params.get("shortCode")
    if not short_code:
        raise ValueError("'shortCode' is required.")
    
    headers = get_auth_headers(api_key)
    api_url = build_url(base_url, "v2/shortened-urls/{}/", short_code)

    return api_call("GET", api_url, headers)


def listShortenedUrls(params: dict) -> dict:
    """List all shortened URLs with optional pagination.
    
    Args:
        params: Dictionary with:
            - accountName (optional): The account to use
            - page (optional): Page number for pagination
            - pageSize (optional): Number of items per page
        
    Returns:
        Dictionary with list of shortened URLs
    """
    account_name = params.get("accountName")
    _, api_key, base_url = get_account_config(account_name)
    
    headers = get_auth_headers(api_key)
    query = {}
    if params.get("page"):
        query["page"] = params["page"]
    if params.get("pageSize"):
        query["page_size"] = params["pageSize"]
    
    api_url = build_url(base_url, "v2/shortened-urls/")
    return api_call("GET", api_url, headers, params=query)
