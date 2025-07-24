"""API utilities and schema functions for CallHub API."""
import sys
from typing import Dict, Optional

from .auth import get_account_config
from .utils import build_url, api_call, get_auth_headers


def getApiSchema(params: dict) -> dict:
    """Get the complete API schema documentation.
    
    Returns the OpenAPI/Swagger schema for the CallHub API,
    including all endpoints, parameters, and response formats.
    
    Args:
        params: Dictionary with:
            - accountName (optional): The account to use
        
    Returns:
        Dictionary with the complete API schema
    """
    account_name = params.get("accountName")
    _, api_key, base_url = get_account_config(account_name)
    
    headers = get_auth_headers(api_key)
    api_url = build_url(base_url, "api-schema/")
    
    return api_call("GET", api_url, headers)


def getApiVersion(params: dict) -> dict:
    """Get the current API version information.
    
    Args:
        params: Dictionary with:
            - accountName (optional): The account to use
        
    Returns:
        Dictionary with API version details
    """
    account_name = params.get("accountName")
    _, api_key, base_url = get_account_config(account_name)
    
    headers = get_auth_headers(api_key)
    api_url = build_url(base_url, "v1/version/")
    
    return api_call("GET", api_url, headers)


def getApiStatus(params: dict) -> dict:
    """Check the API status and health.
    
    Args:
        params: Dictionary with:
            - accountName (optional): The account to use
        
    Returns:
        Dictionary with API status information
    """
    account_name = params.get("accountName")
    _, api_key, base_url = get_account_config(account_name)
    
    headers = get_auth_headers(api_key)
    api_url = build_url(base_url, "v1/status/")
    
    return api_call("GET", api_url, headers)
