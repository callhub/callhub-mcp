# numbers.py
"""
Phone number management operations for CallHub API.
"""

import sys
from typing import Dict, List, Union, Optional, Any

from .utils import build_url, api_call, get_auth_headers
from .auth import get_account_config

def list_rented_numbers(params: Dict) -> Dict:
    """
    List all rented calling numbers (caller IDs) for the account.
    
    Args:
        params: Dictionary containing the following keys:
            accountName (str, optional): The account name to use
    
    Returns:
        dict: API response containing rented number data or error information
    """
    try:
        # Get account configuration
        account_name, api_key, base_url = get_account_config(params.get("accountName"))
        
        # Build URL and headers
        url = build_url(base_url, "v1/numbers/rented_calling_numbers/")
        headers = get_auth_headers(api_key)
        
        # Make API call
        return api_call("GET", url, headers)
        
    except Exception as e:
        sys.stderr.write(f"[callhub] Error listing rented numbers: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def list_validated_numbers(params: Dict) -> Dict:
    """
    List all validated personal phone numbers that can be used as caller IDs.
    
    Args:
        params: Dictionary containing the following keys:
            accountName (str, optional): The account name to use
    
    Returns:
        dict: API response containing validated number data or error information
    """
    try:
        # Get account configuration
        account_name, api_key, base_url = get_account_config(params.get("accountName"))
        
        # Build URL and headers
        url = build_url(base_url, "v1/numbers/validated_numbers/")
        headers = get_auth_headers(api_key)
        
        # Make API call
        return api_call("GET", url, headers)
        
    except Exception as e:
        sys.stderr.write(f"[callhub] Error listing validated numbers: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def rent_number(params: Dict) -> Dict:
    """
    Rent a new phone number to use as a caller ID.
    
    Args:
        params: Dictionary containing the following keys:
            accountName (str, optional): The account name to use
            country_iso (str): The country ISO code for the number (e.g., "US")
            country_code (str): Alternative way to specify country (legacy parameter)
            phone_number_prefix (str, optional): The area code for the number
            area_code (str, optional): Alternative way to specify area code (legacy parameter)
            prefix (str, optional): The prefix for the number
            setup_fee (bool, optional): Whether to pay setup fee (default: True)
    
    Returns:
        dict: API response containing the newly rented number or error information
    """
    try:
        # Get account configuration
        account_name, api_key, base_url = get_account_config(params.get("accountName"))
        
        # Required parameter validation
        country_iso = params.get("country_iso") or params.get("country_code")
        if not country_iso:
            return {"isError": True, "content": [{"type": "text", "text": "Either 'country_iso' or 'country_code' is required."}]}
        
        # Build URL and headers
        url = build_url(base_url, "v1/numbers/rent/")
        headers = get_auth_headers(api_key, "application/json")
        
        # Prepare data
        data = {"country_iso": country_iso}
        
        # Add optional parameters
        if params.get("area_code") or params.get("phone_number_prefix"):
            data["phone_number_prefix"] = params.get("area_code") or params.get("phone_number_prefix")
        if params.get("prefix"):
            data["prefix"] = params["prefix"]
        if "setup_fee" in params:
            data["setup_fee"] = params["setup_fee"]
        
        # Make API call
        return api_call("POST", url, headers, json_data=data)
        
    except Exception as e:
        sys.stderr.write(f"[callhub] Error renting number: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


def get_area_codes(params: Dict) -> Dict:
    """
    Get area codes for a specific country.
    
    Args:
        params: Dictionary containing the following keys:
            accountName (str, optional): The account name to use
            country_iso (str): The country ISO code (e.g., "US")
    
    Returns:
        dict: API response containing area codes or error information
    """
    try:
        account_name, api_key, base_url = get_account_config(params.get("accountName"))
        
        country_iso = params.get("country_iso")
        if not country_iso:
            return {"isError": True, "content": [{"type": "text", "text": "country_iso is required"}]}
        
        url = build_url(base_url, f"v2/get_area_code/?country_iso={country_iso}")
        headers = get_auth_headers(api_key)
        
        return api_call("GET", url, headers)
        
    except Exception as e:
        sys.stderr.write(f"[callhub] Error getting area codes: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


def get_number_rent_rates(params: Dict) -> Dict:
    """
    Get number rent rates for a specific country.
    
    Args:
        params: Dictionary containing the following keys:
            accountName (str, optional): The account name to use
            country_iso (str): The country ISO code (e.g., "US")
    
    Returns:
        dict: API response containing rent rates or error information
    """
    try:
        account_name, api_key, base_url = get_account_config(params.get("accountName"))
        
        country_iso = params.get("country_iso")
        if not country_iso:
            return {"isError": True, "content": [{"type": "text", "text": "country_iso is required"}]}
        
        url = build_url(base_url, f"v1/number_rent_rates/?country_iso={country_iso}")
        headers = get_auth_headers(api_key)
        
        return api_call("GET", url, headers)
        
    except Exception as e:
        sys.stderr.write(f"[callhub] Error getting rent rates: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


def get_auto_unrent_settings(params: Dict) -> Dict:
    """
    Get auto-unrent settings.
    
    Args:
        params: Dictionary containing the following keys:
            accountName (str, optional): The account name to use
    
    Returns:
        dict: API response containing auto-unrent settings or error information
    """
    try:
        account_name, api_key, base_url = get_account_config(params.get("accountName"))
        
        url = build_url(base_url, "v2/auto_unrent/settings/")
        headers = get_auth_headers(api_key)
        
        return api_call("GET", url, headers)
        
    except Exception as e:
        sys.stderr.write(f"[callhub] Error getting auto-unrent settings: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


def update_auto_unrent_settings(params: Dict) -> Dict:
    """
    Update auto-unrent settings.
    
    Args:
        params: Dictionary containing the following keys:
            accountName (str, optional): The account name to use
            auto_unrent_enabled (bool): Enable/disable auto-unrent
            threshold_days (int): Days threshold for auto-unrent
            numbers_to_exclude (list): List of number IDs to exclude
            email_reminders_enabled (bool): Enable/disable email reminders
    
    Returns:
        dict: API response containing updated settings or error information
    """
    try:
        account_name, api_key, base_url = get_account_config(params.get("accountName"))
        
        url = build_url(base_url, "v2/auto_unrent/settings/")
        headers = get_auth_headers(api_key, "application/json")
        
        data = {}
        if "auto_unrent_enabled" in params:
            data["auto_unrent_enabled"] = params["auto_unrent_enabled"]
        if "threshold_days" in params:
            data["threshold_days"] = params["threshold_days"]
        if "numbers_to_exclude" in params:
            data["numbers_to_exclude"] = params["numbers_to_exclude"]
        if "email_reminders_enabled" in params:
            data["email_reminders_enabled"] = params["email_reminders_enabled"]
        
        return api_call("POST", url, headers, json_data=data)
        
    except Exception as e:
        sys.stderr.write(f"[callhub] Error updating auto-unrent settings: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


def revalidate_numbers(params: Dict) -> Dict:
    """
    Revalidate phone numbers.
    
    Args:
        params: Dictionary containing the following keys:
            accountName (str, optional): The account name to use
    
    Returns:
        dict: API response containing revalidation results or error information
    """
    try:
        account_name, api_key, base_url = get_account_config(params.get("accountName"))
        
        url = build_url(base_url, "v1/revalidate_numbers/")
        headers = get_auth_headers(api_key, "application/json")
        
        return api_call("POST", url, headers)
        
    except Exception as e:
        sys.stderr.write(f"[callhub] Error revalidating numbers: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


def list_sms_only_numbers(params: Dict) -> Dict:
    """
    List SMS-only rented numbers.
    
    Args:
        params: Dictionary containing the following keys:
            accountName (str, optional): The account name to use
    
    Returns:
        dict: API response containing SMS-only numbers or error information
    """
    try:
        account_name, api_key, base_url = get_account_config(params.get("accountName"))
        
        url = build_url(base_url, "v2/sms_number/show_rented_number/")
        headers = get_auth_headers(api_key)
        
        return api_call("GET", url, headers)
        
    except Exception as e:
        sys.stderr.write(f"[callhub] Error listing SMS-only numbers: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


def list_combined_sms_numbers(params: Dict) -> Dict:
    """
    List combined validated and rented SMS numbers.
    
    Args:
        params: Dictionary containing the following keys:
            accountName (str, optional): The account name to use
    
    Returns:
        dict: API response containing combined SMS numbers or error information
    """
    try:
        account_name, api_key, base_url = get_account_config(params.get("accountName"))
        
        url = build_url(base_url, "v2/validated_and_rented_numbers/")
        headers = get_auth_headers(api_key)
        
        return api_call("GET", url, headers)
        
    except Exception as e:
        sys.stderr.write(f"[callhub] Error listing combined SMS numbers: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


def auto_rent_sms_number(params: Dict) -> Dict:
    """
    Auto-rent SMS number.
    
    Args:
        params: Dictionary containing the following keys:
            accountName (str, optional): The account name to use
            country_iso (str): The country ISO code (e.g., "US")
            feature (str): The feature type (default: "sms")
    
    Returns:
        dict: API response containing rented SMS number or error information
    """
    try:
        account_name, api_key, base_url = get_account_config(params.get("accountName"))
        
        country_iso = params.get("country_iso")
        if not country_iso:
            return {"isError": True, "content": [{"type": "text", "text": "country_iso is required"}]}
        
        url = build_url(base_url, "v2/sms_number/sms_rent_number/")
        headers = get_auth_headers(api_key, "application/json")
        
        data = {
            "country_iso": country_iso,
            "feature": params.get("feature", "sms")
        }
        
        return api_call("POST", url, headers, json_data=data)
        
    except Exception as e:
        sys.stderr.write(f"[callhub] Error auto-renting SMS number: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}
