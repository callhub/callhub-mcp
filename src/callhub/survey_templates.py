#!/usr/bin/env python3

"""
CallHub Survey Templates - API Integration

This module provides functions for managing survey templates in CallHub.
Based on Django REST framework serializers for PSurvey_template and PSection_template.
"""

from typing import Dict, Any

from .client import McpApiClient
from .constants import ENDPOINTS

def list_survey_templates(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    List all survey templates for the authenticated user.
    
    Args:
        params: Dictionary with optional 'accountName' key
        
    Returns:
        Dictionary with survey templates list or error information
    """
    client = McpApiClient(params.get("accountName"))
    return client.call(ENDPOINTS.TEMPLATES, "GET")

def get_survey_template(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get details for a specific survey template by ID.
    
    Args:
        params: Dictionary with 'templateId' and optional 'accountName' keys
        
    Returns:
        Dictionary with survey template details or error information
    """
    template_id = params.get("templateId")
    if not template_id:
        return {"isError": True, "content": [{"type": "text", "text": "templateId is required"}]}
    
    client = McpApiClient(params.get("accountName"))
    return client.call(f"{ENDPOINTS.TEMPLATES}{template_id}/", "GET")

def create_survey_template(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new survey template with questions.
    
    Args:
        params: Dictionary with survey template data including:
            - label: Survey template name
            - questions: List of question objects
            - accountName: Optional account name
            
    Returns:
        Dictionary with created survey template or error information
    """
    label = params.get("label")
    if not label:
        return {"isError": True, "content": [{"type": "text", "text": "label is required"}]}
    
    client = McpApiClient(params.get("accountName"))
    survey_data = {"label": label, "questions": params.get("questions", [])}
    return client.call(ENDPOINTS.TEMPLATES, "POST", body=survey_data)

def update_survey_template(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update an existing survey template.
    
    Args:
        params: Dictionary with survey template update data including:
            - templateId: Survey template ID
            - label: Updated survey template name (optional)
            - questions: Updated list of question objects (optional)
            - accountName: Optional account name
            
    Returns:
        Dictionary with updated survey template or error information
    """
    template_id = params.get("templateId")
    if not template_id:
        return {"isError": True, "content": [{"type": "text", "text": "templateId is required"}]}
    
    # Prepare update data (only include fields that are provided)
    update_data = {}
    if "label" in params:
        update_data["label"] = params["label"]
    if "questions" in params:
        update_data["questions"] = params["questions"]
    
    if not update_data:
        return {"isError": True, "content": [{"type": "text", "text": "No update data provided."}]}
    
    client = McpApiClient(params.get("accountName"))
    return client.call(f"{ENDPOINTS.TEMPLATES}{template_id}/", "PATCH", body=update_data)

def delete_survey_template(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Delete a survey template by ID.
    
    Args:
        params: Dictionary with 'templateId' and optional 'accountName' keys
        
    Returns:
        Dictionary with deletion result or error information
    """
    template_id = params.get("templateId")
    if not template_id:
        return {"isError": True, "content": [{"type": "text", "text": "templateId is required"}]}
    
    client = McpApiClient(params.get("accountName"))
    return client.call(f"{ENDPOINTS.TEMPLATES}{template_id}/", "DELETE")