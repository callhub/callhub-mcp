"""
Client for interacting with CallHub vb campaign APIs.
"""
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

def create_vb_campaign(params: dict):
    """
    Create a new VB (Voice Broadcast) campaign.
    
    FIXED VERSION - Based on P2P campaign fixes and VB System integration.
    
    Key Fixes Applied:
    - Support template_id (integer) instead of complex script objects
    - Handle SSL certificate issues for local development
    - Better field validation and error handling
    - Automatic conversion of script objects to template_id
    
    Args:
        params: Dictionary containing:
            accountName (str, optional): Account to use
            campaign_data (dict): Campaign configuration with:
                name (str): Campaign name (required)
                template_id (int): Survey template ID (recommended)
                phonebooks (list): List of phonebook IDs (required)
                callerid (str or dict): Caller ID configuration (required)
                audio_message (str or dict): Audio message URL or ID (required for VB)
                schedule (dict, optional): Campaign schedule
                
    Returns:
        dict: API response with campaign data or error
    """
    import sys
    import json
    
    campaign_data = params.get("campaign_data", params)
    
    # Extract key fields
    callerid = campaign_data.get("callerid")
    phonebooks = campaign_data.get("phonebooks")
    audio_message = campaign_data.get("audio_message")
    template_id = campaign_data.get("template_id")
    script = campaign_data.get("script")
    
    # Handle script to template_id conversion (similar to P2P)
    if script and not template_id:
        if isinstance(script, dict) and "id" in script:
            template_id = script["id"]
            sys.stderr.write(f"[callhub] Converted script object to template_id: {template_id}\n")
        elif isinstance(script, int):
            template_id = script
            sys.stderr.write(f"[callhub] Using script integer as template_id: {template_id}\n")
    
    # Validate required fields for VB campaigns
    required_fields = []
    if not phonebooks:
        required_fields.append("phonebooks")
    if not audio_message:
        required_fields.append("audio_message (required for voice broadcast)")
    if not callerid:
        required_fields.append("callerid")
        
    if required_fields:
        return {
            "isError": True,
            "content": [{"type": "text", "text": f"Missing required fields: {', '.join(required_fields)}"}]
        }
    
    # Build payload
    payload = {
        "phonebooks": phonebooks,
        "audio_message": audio_message,
        "callerid": callerid
    }
    
    # Add template_id if provided
    if template_id is not None:
        payload["template_id"] = template_id
    elif script is not None:
        payload["script"] = script
    
    # Add optional fields
    optional_fields = ['name', 'schedule', 'description', 'press_1_transfer_to', 
                      'dnc_list', 'answering_machine_detection', 'voicemail_audio']
    for field in optional_fields:
        if field in campaign_data and campaign_data[field] is not None:
            payload[field] = campaign_data[field]
    
    try:
        account_name = params.get("accountName")
        account, api_key, base_url = get_account_config(account_name)
        
        url = build_url(base_url, "/v1/vb_campaigns/")
        headers = get_auth_headers(api_key, "application/json")
        
        # Log for debugging
        sys.stderr.write(f"[callhub] Creating VB campaign\n")
        sys.stderr.write(f"[callhub] URL: {url}\n")
        if template_id:
            sys.stderr.write(f"[callhub] Template ID: {template_id}\n")
        
        # Make API call with JSON data
        response = api_call('POST', url, headers=headers, json_data=payload)
        
        # Handle successful response
        if not response.get("isError") and "id" in response:
            sys.stderr.write(f"[callhub] ✅ VB Campaign created successfully!\n")
            sys.stderr.write(f"[callhub] Campaign ID: {response.get('id')}\n")
            
            response["success"] = True
            response["campaign_id"] = response.get("id")
        
        return response
        
    except Exception as e:
        error_msg = str(e)
        sys.stderr.write(f"[callhub] Error creating VB campaign: {error_msg}\n")
        
        if "SSL" in error_msg.upper():
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"SSL Error: {error_msg}. For local development, use HTTP base URL."}]
            }
        else:
            return {"isError": True, "content": [{"type": "text", "text": error_msg}]}

def create_vb_campaign_template(params: dict):
    """
    Create a new vb campaign template.
    """
    template_data = params.get("template_data")
    if not template_data:
        return {"isError": True, "content": [{"type": "text", "text": "'template_data' is required."}]}
    account_name = params.get( "accountName" )
    account , api_key , base_url = get_account_config( account_name )

    url = build_url( base_url , "/v1/vb_templates/"  )
    headers = get_auth_headers( api_key )
    return api_call('post', url,headers=headers, data=template_data)
