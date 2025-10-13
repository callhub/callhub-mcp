# !/usr/bin/env python3
"""
McpApiClient - A simple, reusable API client for CallHub MCP
Uses named endpoints for clean, maintainable API calls.
"""

from typing import Dict , Any , Optional



class McpApiClient :
    """
    Simple API client with named endpoints.
    Eliminates redundancy while keeping a clean, readable interface.
    """

    def __init__ (self , account_name: Optional[ str ] = None) :
        """
        Initialize the API client with account configuration.

        Args:
            account_name: Optional account name for multi-tenant support
        """
        from .auth import get_account_config
        self.account , self.api_key , self.base_url = get_account_config( account_name )

    def call (self , url ,method,*url_params,
            body: Optional[ Dict[ str , Any ] ] = None , query: Optional[ Dict[ str , Any ] ] = None, form_data: Optional[Dict[str, Any]] = None ) -> Dict[ str , Any ] :
        """
        Make an API call to a named endpoint.

        Args:
            url: Endpoint Url
            method: HTTP method (GET, POST, PATCH, DELETE)
            body: JSON body for POST/PATCH requests
            query: Query parameters for GET requests
            form_data: Form data for POST requests (used instead of body if provided)
            url_params: Positional arguments to be formatted into the URL

        Returns:
            API response dictionary
        """
        from .utils import build_url , api_call , get_auth_headers

        # Get headers
        headers = get_auth_headers( self.api_key )
        url = build_url( self.base_url , url ,*url_params)
        if method == "GET" :
            return api_call( method , url , headers , params = query )
        elif method in [ "POST" , "PUT" , "PATCH" ] :
            if body is not None :
                return api_call( method , url , headers , json_data = body )
            elif form_data is not None:
                headers = get_auth_headers(self.api_key, "application/x-www-form-urlencoded")
                return api_call( method, url, headers, data=form_data)
            else :
                return api_call( method , url , headers )
        elif method == "DELETE" :
            return api_call( method , url , headers, json_data=body )
        else :
            return {
                "isError" : True , "content" : [ { "type" : "text" , "text" : f"Unsupported method: {method}" } ]
            }


