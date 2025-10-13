# sms_broadcasts.py
"""
SMS Broadcast operations for CallHub API.
"""

import sys
from datetime import datetime, timedelta
from typing import Dict, Any

from .client import McpApiClient

def create_sms_broadcast(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new SMS broadcast campaign.

    Args:
        params: Dictionary containing the following keys:
            account (str, optional): The account name to use
            name (str): Campaign name
            text_message (str): SMS message content
            phonebook (list): List of phonebook IDs
            callerid (str): Caller ID/Sender ID
            callerid_choice (str, optional): Caller ID choice (defaults to "exists")
            startingdate (str, optional): Starting date in "YYYY-MM-DD HH:MM:SS" format
            expirationdate (str, optional): Expiration date in "YYYY-MM-DD HH:MM:SS" format
            daily_start_time (str, optional): Daily start time (e.g., "08:00")
            daily_stop_time (str, optional): Daily stop time (e.g., "21:00")
            opt_out_language (str, optional): Opt out language
            help_compliance_message (str, optional): Help compliance message
            monday (str, optional): Monday schedule ("on"/"off")
            tuesday (str, optional): Tuesday schedule ("on"/"off")
            wednesday (str, optional): Wednesday schedule ("on"/"off")
            thursday (str, optional): Thursday schedule ("on"/"off")
            friday (str, optional): Friday schedule ("on"/"off")
            saturday (str, optional): Saturday schedule ("on"/"off")
            sunday (str, optional): Sunday schedule ("on"/"off")
            description (str, optional): Campaign description
            timezone_choices (str, optional): Timezone choice (e.g., "America/Chicago")
            use_contact_tz (str, optional): Use contact timezone setting
            intervalretry (int, optional): Retry interval in minutes (default 5)
            maxretry (int, optional): Maximum retries (default 0)
            auto_replies (list, optional): List of auto-reply configurations
            base_short_url (list, optional): Base short URL configuration
            dont_text_dnc (bool, optional): Don't text DNC numbers (default false)
            dont_text_litigator (bool, optional): Don't text litigator numbers (default true)

    Returns:
        dict: API response containing the created campaign data
    """
    try:
        required_fields = ["name", "text_message", "phonebook", "callerid"]
        for key in required_fields:
            if not params.get(key):
                return {"isError": True, "content": [{"type": "text", "text": f"'{key}' is required."}]}

        client = McpApiClient(params.get("account"))

        data = {
            "name": params.get("name"),
            "text_message": params.get("text_message"),
            "phonebook": params.get("phonebook"),
            "callerid": params.get("callerid"),
            "callerid_choice": params.get("callerid_choice", "exists"),
            "opt_out_language": params.get("opt_out_language", ""),
            "intervalretry": params.get("intervalretry", 5),
            "maxretry": params.get("maxretry", 0),
            "dont_text_dnc": params.get("dont_text_dnc", False),
            "dont_text_litigator": params.get("dont_text_litigator", True),
            "daily_start_time": params.get("daily_start_time", "08:00"),
            "daily_stop_time": params.get("daily_stop_time", "21:00"),
            "monday": params.get("monday", "on"),
            "tuesday": params.get("tuesday", "on"),
            "wednesday": params.get("wednesday", "on"),
            "thursday": params.get("thursday", "on"),
            "friday": params.get("friday", "on"),
            "saturday": params.get("saturday", "on"),
            "sunday": params.get("sunday", "on"),
            "startingdate": params.get("startingdate", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "expirationdate": params.get("expirationdate", (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S"))
        }

        optional_fields = [
            "help_compliance_message", "description", "timezone_choices",
            "use_contact_tz", "auto_replies", "base_short_url", "country_iso",
            "sender_name", "senderid", "shortcode_keyword_id", "nb_contact_type",
            "nb_custom_field", "an_stag", "an_rtag", "nb_stag", "nb_rtag",
            "bb_stag", "bb_rtag", "civi_campaign", "civi_activity_type",
            "bsd_field_label", "bsd_field_value", "van_activistcodes",
            "van_activistcodes_recv", "sf_tag_sent", "sf_tag_recv", "email",
            "media_files", "tcr_usecase"
        ]
        for field in optional_fields:
            if field in params and params[field] is not None:
                data[field] = params[field]

        return client.call("/v2/sms_broadcast/create/", "POST", body=data)
    except Exception as e:
        sys.stderr.write(f"[callhub] Error creating SMS broadcast campaign: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def get_sms_broadcast(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get details of an SMS broadcast campaign.

    Args:
        params: Dictionary containing the following keys:
            account (str, optional): The account name to use
            campaignId (str): The ID of the campaign to retrieve

    Returns:
        dict: API response containing the campaign data
    """
    try:
        campaign_id = params.get("campaignId")
        if not campaign_id:
            return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}

        client = McpApiClient(params.get("account"))
        return client.call(f"v2/sms_broadcast/{campaign_id}/", "GET")
    except Exception as e:
        sys.stderr.write(f"[callhub] Error getting SMS broadcast campaign: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def update_sms_broadcast(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update an SMS broadcast campaign's status.
    
    Args:
        params: Dictionary containing the following keys:
            account (str, optional): The account name to use
            campaignId (str): The ID of the campaign to update
            status (str or int): The new status of the campaign. 
                String values: "start", "pause", "abort", "end"
                Numeric values: 1 (START), 2 (PAUSE), 3 (ABORT), 4 (END)
    
    Returns:
        dict: API response from the update operation
    """
    try:
        campaign_id = params.get("campaignId")
        if not campaign_id:
            return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}
        
        status = params.get("status")
        if status is None:
            return {"isError": True, "content": [{"type": "text", "text": "'status' is required."}]}
        
        status_mapping = {"start": 1, "pause": 2, "abort": 3, "end": 4}
        
        if isinstance(status, str) and status.lower() in status_mapping:
            status = status_mapping[status.lower()]
        elif isinstance(status, str) and status.isdigit():
            status = int(status)
        
        if not isinstance(status, int) or status < 1 or status > 4:
            return {
                "isError": True, 
                "content": [{"type": "text", "text": "Valid 'status' is required: start, pause, abort, end, or a valid numeric status (1-4)"}]
            }
        
        client = McpApiClient(params.get("account"))
        data = {"status": status}
        return client.call(f"v2/sms_broadcast/{campaign_id}/", "PATCH", body=data)
    except Exception as e:
        sys.stderr.write(f"[callhub] Error updating SMS broadcast campaign: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def duplicate_sms_broadcast(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Duplicate an SMS broadcast campaign.

    Args:
        params: Dictionary containing the following keys:
            account (str, optional): The account name to use
            campaignId (str): The ID of the campaign to duplicate

    Returns:
        dict: API response from the duplicate operation
    """
    try:
        campaign_id = params.get("campaignId")
        if not campaign_id:
            return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}

        client = McpApiClient(params.get("account"))
        return client.call(f"v2/sms_broadcast/{campaign_id}/duplicate/", "POST")
    except Exception as e:
        sys.stderr.write(f"[callhub] Error duplicating SMS broadcast campaign: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

