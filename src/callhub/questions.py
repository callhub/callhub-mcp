#!/usr/bin/env python3

"""
CallHub Questions Management - API Integration

This module provides functions for managing questions (PDI/VAN) in CallHub.
"""

from typing import Dict, Any

from .client import McpApiClient
from .constants import ENDPOINTS

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
    client = McpApiClient(params.get("accountName"))
    query_params = {}

    # Add type parameter if specified
    question_type = params.get("type")
    if question_type and question_type in ["PDI_QUESTION", "VAN_QUESTION"]:
        query_params["type"] = question_type
    
    return client.call(ENDPOINTS.QUESTIONS, "GET", query=query_params)

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
    question_id = params.get("questionId")
    if not question_id:
        return {
            "isError": True,
            "content": [{"type": "text", "text": "questionId is required"}]
        }
    
    client = McpApiClient(params.get("accountName"))
    return client.call(f"{ENDPOINTS.QUESTIONS}{question_id}/", "GET")