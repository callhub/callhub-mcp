#!/usr/bin/env python3

"""
CallHub Questions Management - API Integration

This module provides functions for managing questions (PDI/VAN) in CallHub.
"""

import json
import sys
from typing import Dict, Any, Optional

from .auth import get_account_config
from .utils import build_url, api_call, get_auth_headers


def list_questions(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    List all questions with optional type filtering.
    
    Args:
        params: Dictionary with optional keys:
            - accountName (str): The account name to use
            - type (str): Filter by question type (PDI_QUESTION, VAN_QUESTION)
            
    Returns:
        Dictionary with questions list or error information
    """
    account_name = params.get("accountName")
    account, api_key, base_url = get_account_config(account_name)
    
    # Build URL with optional type filter
    url = build_url(base_url, "/v1/questions/")
    
    # Add type parameter if specified
    question_type = params.get("type")
    if question_type and question_type in ["PDI_QUESTION", "VAN_QUESTION"]:
        url += f"?type={question_type}"
    
    headers = get_auth_headers(api_key)
    
    return api_call("GET", url, headers)


def get_question(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get details for a specific question by ID.
    
    Args:
        params: Dictionary with keys:
            - questionId (str): The question ID
            - accountName (str, optional): The account name to use
            
    Returns:
        Dictionary with question details or error information
    """
    account_name = params.get("accountName")
    question_id = params.get("questionId")
    
    if not question_id:
        return {
            "isError": True,
            "content": [{"type": "text", "text": "questionId is required"}]
        }
    
    account, api_key, base_url = get_account_config(account_name)
    url = build_url(base_url, "/v1/questions/{}/", question_id)
    headers = get_auth_headers(api_key)
    
    return api_call("GET", url, headers)
