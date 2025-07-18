#!/usr/bin/env python3

"""
CallHub Integration Fields Management - API Integration

This module provides functions for managing integration custom fields in CallHub.
"""

import json
import sys
from typing import Dict, Any, Optional

from .auth import get_account_config
from .utils import build_url, api_call, get_auth_headers


def list_integration_fields(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    List all integration fields.
    
    Args:
        params: Dictionary with optional keys:
            - accountName (str): The account name to use
            
    Returns:
        Dictionary with integration fields list or error information
    """
    account_name = params.get("accountName")
    account, api_key, base_url = get_account_config(account_name)
    
    url = build_url(base_url, "/v1/integration_fields/")
    headers = get_auth_headers(api_key)
    
    return api_call("GET", url, headers)


def get_integration_field(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get details for a specific integration field by ID.
    
    Args:
        params: Dictionary with keys:
            - fieldId (str): The integration field ID
            - accountName (str, optional): The account name to use
            
    Returns:
        Dictionary with integration field details or error information
    """
    account_name = params.get("accountName")
    field_id = params.get("fieldId")
    
    if not field_id:
        return {
            "isError": True,
            "content": [{"type": "text", "text": "fieldId is required"}]
        }
    
    account, api_key, base_url = get_account_config(account_name)
    url = build_url(base_url, "/v1/integration_fields/{}/", field_id)
    headers = get_auth_headers(api_key)
    
    return api_call("GET", url, headers)
