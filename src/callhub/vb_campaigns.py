"""
Client for interacting with CallHub vb campaign APIs.
"""
import sys
from typing import Dict, Any

from .auth import get_account_config
from .utils import api_call , build_url , get_auth_headers


def get_vb_campaign(params: dict):
    """
    Get a single vb campaign.
    """
    campaign_id = params.get("campaignId")
    if not campaign_id:
        return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}
    account_name = params.get( "accountName" )
    account , api_key , base_url = get_account_config( account_name )

    url = build_url( base_url , "/v1/vb_campaigns/{}" , campaign_id )
    headers = get_auth_headers( api_key )
    return api_call('get', url, params=params,headers=headers)

def create_voice_broadcast_campaign(params: Dict[str, Any]) -> Dict:
    """
    Create a new voice broadcast campaign.

    Args:
        params: Dictionary containing the following keys:
            account (str, optional): The account name to use
            phonebooks (List[int]): List of phonebook IDs
            callerid_options (Dict): Caller ID options
            contact_options (Dict): Contact options
            template_id (str): Template ID
            schedule (Dict): Schedule options

    Returns:
        dict: API response containing campaign data or error information
    """
    try:
        # Get account configuration
        account_name = params.get( "accountName" )
        account_name, api_key, base_url = get_account_config(account_name)

        # Build URL and headers
        url = build_url(base_url, "v1/vb_campaigns/")
        headers = get_auth_headers(api_key)
        headers["Content-Type"] = "application/json"

        # Prepare data payload
        data = {
            "phonebooks": params.get("phonebooks"),
            "callerid_options": params.get("callerid_options"),
            "contact_options": params.get("contact_options"),
            "template_id": params.get("template_id"),
            "schedule": params.get("schedule"),
        }

        # Make API call
        return api_call("POST", url, headers, json_data=data)

    except Exception as e:
        sys.stderr.write(f"[callhub] Error creating voice broadcast campaign: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


def create_vb_campaign_template(params: Dict[str, Any]) -> Dict:
    """
    Create a new voice broadcast campaign template.

    Args:
        params: Dictionary containing the following keys:
            account (str, optional): The account name to use
            label (str): The name of the template.
            live_message (Dict): The message to be played to a live person.
            transfers (List[Dict]): A list of transfer options.
            dnc_option (Dict): The DNC (Do Not Call) option.

    Returns:
        dict: API response containing template data or error information
    """
    try:
        # Get account configuration
        account_name, api_key, base_url = get_account_config(params.get("accountName"))

        # Build URL and headers
        url = build_url(base_url, "/v1/vb_templates/")
        headers = get_auth_headers(api_key)
        headers["Content-Type"] = "application/json"

        # Prepare data payload
        data = {
            "label": params.get("label"),
            "live_message": params.get("live_message"),
            "transfers": params.get("transfers"),
            "dnc_option": params.get("dnc_option"),
        }

        # Make API call
        return api_call("POST", url, headers, json_data=data)

    except Exception as e:
        import sys
        sys.stderr.write(f"[callhub] Error creating VB campaign template: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


def list_voice_broadcasts (params: Dict) -> Dict :
    """
    List all voice broadcast campaigns with optional pagination.

    Args:
        params: Dictionary containing the following keys:
            account (str, optional): The account name to use
            page (int, optional): Page number for pagination
            pageSize (int, optional): Number of items per page

    Returns:
        dict: API response containing campaign data or error information
    """
    try :
        # Get account configuration
        account_name , api_key , base_url = get_account_config( params.get( "accountName" ) )

        # Build URL and headers
        url = build_url( base_url , "v1/voice_broadcasts/" )
        headers = get_auth_headers( api_key )

        # Prepare query parameters
        query_params = { }
        if params.get( "page" ) is not None :
            query_params[ "page" ] = params[ "page" ]
        if params.get( "pageSize" ) is not None :
            query_params[ "page_size" ] = params[ "pageSize" ]

        # Make API call
        return api_call( "GET" , url , headers , params = query_params )

    except Exception as e :
        sys.stderr.write( f"[callhub] Error listing voice broadcast campaigns: {str( e )}\n" )
        return { "isError" : True , "content" : [ { "type" : "text" , "text" : str( e ) } ] }