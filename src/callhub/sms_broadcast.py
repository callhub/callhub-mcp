# sms_broadcast.py
"""
SMSBroadcast class for CallHub API operations.
"""

import sys
from typing import Dict, List, Union, Optional, Any

from .utils import build_url, api_call, get_auth_headers
from .auth import get_account_config

class SMSBroadcast:
    """
    SMSBroadcast class for managing CallHub SMS broadcast campaigns.
    
    This class provides methods for interacting with CallHub SMS broadcast APIs,
    including listing, updating, and deleting SMS broadcast campaigns.
    """
    
    def __init__(self, account_name: Optional[str] = None):
        """
        Initialize the SMSBroadcast class.
        
        Args:
            account_name (str, optional): The account name to use for API calls
        """
        self.account_name = account_name
        self._api_key = None
        self._base_url = None
        self._initialize_config()
    
    def _initialize_config(self):
        """Initialize the API configuration from the account settings."""
        try:
            self.account_name, self._api_key, self._base_url = get_account_config(self.account_name)
        except Exception as e:
            sys.stderr.write(f"[callhub] Error initializing SMSBroadcast: {str(e)}\n")
            raise
    
    def list_sms_broadcasts(self, page: Optional[int] = None, page_size: Optional[int] = None) -> Dict:
        """
        List all SMS broadcast campaigns with optional pagination.
        
        Args:
            page (int, optional): Page number for pagination
            page_size (int, optional): Number of items per page
        
        Returns:
            dict: API response containing campaign data or error information
        """
        try:
            # Build URL and headers
            url = build_url(self._base_url, "v1/sms_broadcasts/")
            headers = get_auth_headers(self._api_key)
            
            # Prepare query parameters
            query_params = {}
            if page is not None:
                query_params["page"] = page
            if page_size is not None:
                query_params["page_size"] = page_size
            
            # Make API call
            return api_call("GET", url, headers, params=query_params)
            
        except Exception as e:
            sys.stderr.write(f"[callhub] Error listing SMS broadcast campaigns: {str(e)}\n")
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}
    
    def update_sms_broadcast(self, campaign_id: str, status: Union[str, int]) -> Dict:
        """
        Update an SMS broadcast campaign's status.
        
        Args:
            campaign_id (str): The ID of the campaign to update
            status (str or int): The new status of the campaign. 
                String values: "start", "pause", "abort", "end"
                Numeric values: 1 (START), 2 (PAUSE), 3 (ABORT), 4 (END)
        
        Returns:
            dict: API response from the update operation
        """
        # Validate required parameters
        if not campaign_id:
            return {"isError": True, "content": [{"type": "text", "text": "'campaign_id' is required."}]}
        
        if status is None:
            return {"isError": True, "content": [{"type": "text", "text": "'status' is required."}]}
        
        # Map string status to numeric status if needed
        status_mapping = {
            "start": 1,
            "pause": 2,
            "abort": 3,
            "end": 4
        }
        
        # If a string status was provided, convert it to numeric
        if isinstance(status, str) and status.lower() in status_mapping:
            status = status_mapping[status.lower()]
        # If a numeric status as string was provided, convert to int
        elif isinstance(status, str) and status.isdigit():
            status = int(status)
        # Check if status is valid now
        if not isinstance(status, int) or status < 1 or status > 4:
            return {
                "isError": True, 
                "content": [{"type": "text", "text": "Valid 'status' is required: start, pause, abort, end, or a valid numeric status (1-4)"}]
            }
        
        try:
            # Build URL and headers
            url = build_url(self._base_url, "v1/sms_broadcasts/{}/", campaign_id)
            headers = get_auth_headers(self._api_key, "application/json")
            
            # Prepare data
            data = {"status": status}
            
            # Make API call
            return api_call("PATCH", url, headers, json_data=data)
            
        except Exception as e:
            sys.stderr.write(f"[callhub] Error updating SMS broadcast campaign: {str(e)}\n")
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}
    
    def delete_sms_broadcast(self, campaign_id: str) -> Dict:
        """
        Delete an SMS broadcast campaign by ID.
        
        Args:
            campaign_id (str): The ID of the campaign to delete
        
        Returns:
            dict: API response from the delete operation
        """
        # Validate required parameters
        if not campaign_id:
            return {"isError": True, "content": [{"type": "text", "text": "'campaign_id' is required."}]}
        
        try:
            # Build URL and headers
            url = build_url(self._base_url, "v1/sms_broadcasts/{}/", campaign_id)
            headers = get_auth_headers(self._api_key)
            
            # Make API call
            return api_call("DELETE", url, headers)
            
        except Exception as e:
            sys.stderr.write(f"[callhub] Error deleting SMS broadcast campaign: {str(e)}\n")
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}
    
    def create_sms_broadcast(self, name: str, phonebook_ids: List[str], message: str, 
                            sender_id: str, schedule_date: Optional[str] = None) -> Dict:
        """
        Create a new SMS broadcast campaign.
        
        Args:
            name (str): Name of the campaign
            phonebook_ids (list): List of phonebook IDs to include in the campaign
            message (str): The SMS message content
            sender_id (str): ID of the sender to use for the campaign
            schedule_date (str, optional): Date to schedule the campaign (ISO format)
        
        Returns:
            dict: API response containing the created campaign data
        """
        # Validate required parameters
        if not name:
            return {"isError": True, "content": [{"type": "text", "text": "'name' is required."}]}
        
        if not phonebook_ids:
            return {"isError": True, "content": [{"type": "text", "text": "'phonebook_ids' is required."}]}
        
        if not message:
            return {"isError": True, "content": [{"type": "text", "text": "'message' is required."}]}
        
        if not sender_id:
            return {"isError": True, "content": [{"type": "text", "text": "'sender_id' is required."}]}
        
        try:
            # Build URL and headers
            url = build_url(self._base_url, "v1/sms_broadcasts/")
            headers = get_auth_headers(self._api_key, "application/json")
            
            # Prepare data
            data = {
                "name": name,
                "phonebook_ids": phonebook_ids,
                "message": message,
                "sender_id": sender_id
            }
            
            if schedule_date:
                data["schedule_date"] = schedule_date
            
            # Make API call
            return api_call("POST", url, headers, json_data=data)
            
        except Exception as e:
            sys.stderr.write(f"[callhub] Error creating SMS broadcast campaign: {str(e)}\n")
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}