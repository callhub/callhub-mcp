#!/usr/bin/env python3

"""
CallHub Integration Fields Management - API Integration

This module provides functions for managing integration custom fields in CallHub.
"""

from typing import Dict, Any

from .client import McpApiClient

def list_integration_fields(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    List all integration fields.
    
    Args:
        params: Dictionary with optional keys:
            - accountName (str): The account name to use
            
    Returns:
        Dictionary with integration fields list or error information
    """
    client = McpApiClient(params.get("accountName"))
    return client.call("/v1/integration_fields/", "GET")

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
    field_id = params.get("fieldId")
    if not field_id:
        return {
            "isError": True,
            "content": [{"type": "text", "text": "fieldId is required"}]
        }
    
    client = McpApiClient(params.get("accountName"))
    return client.call(f"/v1/integration_fields/{field_id}/", "GET")