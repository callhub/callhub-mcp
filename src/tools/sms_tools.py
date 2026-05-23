"""Tool wrappers for SMS Campaign and Broadcast operations."""
from typing import Optional
from callhub.sms_campaigns import (
    list_sms_campaigns,
    update_sms_campaign,
    delete_sms_campaign,
    export_sms_report,
)
from callhub.sms_broadcasts import (
    create_sms_broadcast,
    get_sms_broadcast,
    update_sms_broadcast,
    duplicate_sms_broadcast,
)


def register(server):
    @server.tool(name="listSmsCampaigns", description="List all SMS campaigns with optional pagination.")
    def list_sms_campaigns_tool(
        account: Optional[str] = None,
        page: Optional[int] = None,
        pageSize: Optional[int] = None
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account # Corrected from params["account"] to params["accountName"]
            if page is not None:
                params["page"] = page
            if pageSize is not None:
                params["pageSize"] = pageSize

            return list_sms_campaigns(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="updateSmsCampaign", description="Update an SMS campaign's status. Valid values: 'start', 'pause', 'abort', 'end' or 1-4 numerically.")
    def update_sms_campaign_tool(
        account: Optional[str] = None,
        campaignId: str = None,
        status: str = None # Kept as str, conversion in module
    ) -> dict:
        try:
            # Validate required parameters
            if not campaignId:
                return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}

            if not status: # Basic check, detailed validation in module
                return {
                    "isError": True,
                    "content": [{"type": "text", "text": "Valid 'status' is required: start, pause, abort, end, or 1-4 numerically"}]
                }

            params = {
                "campaignId": campaignId,
                "status": status
            }
            if account:
                params["accountName"] = account # Corrected from params["account"] to params["accountName"]

            return update_sms_campaign(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="deleteSmsCampaign", description="Delete an SMS campaign by ID.")
    def delete_sms_campaign_tool(
        account: Optional[str] = None,
        campaignId: str = None
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if campaignId:
                params["campaignId"] = campaignId
            return delete_sms_campaign(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="createSmsBroadcast", description="Create a new SMS broadcast campaign.")
    def create_sms_broadcast_tool(
        account: Optional[str] = None,
        name: str = None,
        text_message: str = None,
        phonebook: list = None,
        callerid: str = None,
        callerid_choice: Optional[str] = "exists",
        description: Optional[str] = None,
        startingdate: Optional[str] = None,
        expirationdate: Optional[str] = None,
        daily_start_time: Optional[str] = None,
        daily_stop_time: Optional[str] = None,
        opt_out_language: Optional[str] = "",
        help_compliance_message: Optional[str] = "",
        monday: Optional[str] = None,
        tuesday: Optional[str] = None,
        wednesday: Optional[str] = None,
        thursday: Optional[str] = None,
        friday: Optional[str] = None,
        saturday: Optional[str] = None,
        sunday: Optional[str] = None,
        timezone_choices: Optional[str] = None,
        use_contact_tz: Optional[str] = "campaign_timezone",
        intervalretry: Optional[int] = 5,
        maxretry: Optional[int] = 0,
        auto_replies: Optional[list] = None,
        base_short_url: Optional[list] = None,
        dont_text_dnc: Optional[bool] = False,
        dont_text_litigator: Optional[bool] = True
    ) -> dict:
        try:
            # Validate required parameters
            if not name:
                return {"isError": True, "content": [{"type": "text", "text": "'name' is required."}]}
            if not text_message:
                return {"isError": True, "content": [{"type": "text", "text": "'text_message' is required."}]}
            if not phonebook:
                return {"isError": True, "content": [{"type": "text", "text": "'phonebook' is required."}]}
            if not callerid:
                return {"isError": True, "content": [{"type": "text", "text": "'callerid' is required."}]}

            params = {
                "name": name,
                "text_message": text_message,
                "phonebook": phonebook,
                "callerid": callerid,
                "callerid_choice": callerid_choice,
                "opt_out_language": opt_out_language,
                "help_compliance_message": help_compliance_message,
                "use_contact_tz": use_contact_tz,
                "intervalretry": intervalretry,
                "maxretry": maxretry,
                "dont_text_dnc": dont_text_dnc,
                "dont_text_litigator": dont_text_litigator
            }

            # Add optional parameters if provided
            if account:
                params["account"] = account
            if description:
                params["description"] = description
            if startingdate:
                params["startingdate"] = startingdate
            if expirationdate:
                params["expirationdate"] = expirationdate
            if daily_start_time:
                params["daily_start_time"] = daily_start_time
            if daily_stop_time:
                params["daily_stop_time"] = daily_stop_time
            if timezone_choices:
                params["timezone_choices"] = timezone_choices
            if auto_replies:
                params["auto_replies"] = auto_replies
            if base_short_url:
                params["base_short_url"] = base_short_url

            # Add weekday scheduling parameters
            weekdays = {"monday": monday, "tuesday": tuesday, "wednesday": wednesday,
                       "thursday": thursday, "friday": friday, "saturday": saturday, "sunday": sunday}
            for day, value in weekdays.items():
                if value:
                    params[day] = value

            return create_sms_broadcast(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getSmsBroadcast", description="[Extended API] Get details of an SMS broadcast campaign.")
    def get_sms_broadcast_tool(
        account: Optional[str] = None,
        campaignId: str = None
    ) -> dict:
        try:
            # Validate required parameters
            if not campaignId:
                return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}

            params = {
                "campaignId": campaignId
            }
            if account:
                params["account"] = account

            return get_sms_broadcast(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="updateSmsBroadcast", description="[Extended API] Update an SMS broadcast campaign's status. Valid values: 'start', 'pause', 'abort', 'end' or 1-4 numerically.")
    def update_sms_broadcast_tool(
        account: Optional[str] = None,
        campaignId: str = None,
        status: str = None # Kept as str, conversion in module
    ) -> dict:
        try:
            # Validate required parameters
            if not campaignId:
                return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}

            if not status: # Basic check, detailed validation in module
                return {
                    "isError": True,
                    "content": [{"type": "text", "text": "Valid 'status' is required: start, pause, abort, end, or 1-4 numerically"}]
                }

            params = {
                "campaignId": campaignId,
                "status": status
            }
            if account:
                params["account"] = account

            return update_sms_broadcast(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="duplicateSmsBroadcast", description="Duplicate an SMS broadcast campaign.")
    def duplicate_sms_broadcast_tool(
        account: Optional[str] = None, campaign_id: int = None
    ) -> dict:
        try:
            params = {"campaignId": campaign_id}
            if account:
                params["accountName"] = account
            return duplicate_sms_broadcast(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="exportSmsReport", description="[Extended API] Export an SMS report for a campaign.")
    def export_sms_report_tool(
        account: Optional[str] = None, campaign_id: int = None
    ) -> dict:
        try:
            params = {"campaign_id": campaign_id}
            if account:
                params["accountName"] = account
            return export_sms_report(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}
