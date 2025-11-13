"""API utilities and schema functions for CallHub API."""
import sys
from typing import Dict, Optional

from .auth import get_account_config
from .utils import build_url, api_call, get_auth_headers


def getApiSchema(params: dict) -> dict:
    """Get the API schema documentation for a specific resource.
    
    Returns the schema for a CallHub API resource,
    including all endpoints, parameters, and response formats.
    
    Args:
        params: Dictionary with:
            - accountName (optional): The account to use
            - resource (optional): The resource to get schema for (e.g., 'p2p_campaigns')
                                  If not provided, tries global api-schema endpoint
        
    Returns:
        Dictionary with the API schema
    """
    account_name = params.get("accountName")
    _, api_key, base_url = get_account_config(account_name)
    
    headers = get_auth_headers(api_key)
    
    # Check if a specific resource is requested
    resource = params.get("resource")
    if not resource:
        raise ValueError("Resource parameter is required to get API schema.")
    # Resource-specific schema endpoint (e.g., /v1/p2p_campaigns/api-schema)
    api_url = build_url(base_url, f"v1/{resource}/api-schema")
    
    return api_call("GET", api_url, headers)

