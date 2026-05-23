"""Tool wrappers for Phone Number operations."""
from typing import Optional, List
from callhub.numbers import (
    list_rented_numbers,
    list_validated_numbers,
    rent_number,
    get_area_codes,
    get_number_rent_rates,
    get_auto_unrent_settings,
    update_auto_unrent_settings,
    revalidate_numbers,
    list_sms_only_numbers,
    list_combined_sms_numbers,
    auto_rent_sms_number,
)


def register(server):
    @server.tool(name="listRentedNumbers", description="List all rented calling numbers (caller IDs) for the account. Supports pagination and filtering.")
    def list_rented_numbers_tool(
        account: Optional[str] = None,
        page_size: Optional[int] = None,
        page: Optional[int] = None,
        countries: Optional[str] = None,
        order_by: Optional[str] = None,
        order_direction: Optional[str] = None
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if page_size is not None:
                params["page_size"] = page_size
            if page is not None:
                params["page"] = page
            if countries:
                params["countries"] = countries
            if order_by:
                params["order_by"] = order_by
            if order_direction:
                params["order_direction"] = order_direction

            return list_rented_numbers(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="listValidatedNumbers", description="List all validated personal phone numbers that can be used as caller IDs. Supports pagination.")
    def list_validated_numbers_tool(
        account: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if page is not None:
                params["page"] = page
            if page_size is not None:
                params["page_size"] = page_size

            return list_validated_numbers(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="rentNumber", description="Rent a new phone number to use as a caller ID. Requires country_iso (e.g., 'US') parameter. Optional phone_number_prefix for specifying area code.")
    def rent_number_tool(
        account: Optional[str] = None,
        country_iso: str = None,
        country_code: Optional[str] = None,
        phone_number_prefix: Optional[str] = None,
        area_code: Optional[str] = None,
        prefix: Optional[str] = None,
        setup_fee: Optional[bool] = None,
        campaign_type: Optional[str] = None
    ) -> dict:
        try:
            # Validate required parameters
            if not country_iso and not country_code:
                return {"isError": True, "content": [{"type": "text", "text": "Either 'country_iso' or 'country_code' is required."}]}

            params = {}
            if account:
                params["accountName"] = account
            if country_iso:
                params["country_iso"] = country_iso
            if country_code: #This parameter is deprecated in favor of country_iso but supported for now
                params["country_code"] = country_code
            if phone_number_prefix:
                params["phone_number_prefix"] = phone_number_prefix
            if area_code: #This parameter is deprecated in favor of phone_number_prefix but supported for now
                params["area_code"] = area_code
            if prefix:
                params["prefix"] = prefix
            if setup_fee is not None:
                params["setup_fee"] = setup_fee
            if campaign_type:
                params["campaign_type"] = campaign_type

            return rent_number(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getAreaCodes", description="[Extended API] Get area codes for a specific country.")
    def get_area_codes_tool(
        account: Optional[str] = None,
        country_iso: str = None
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if country_iso:
                params["country_iso"] = country_iso

            return get_area_codes(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getNumberRentRates", description="[Extended API] Get number rent rates for a specific country.")
    def get_number_rent_rates_tool(
        account: Optional[str] = None,
        country_iso: str = None
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if country_iso:
                params["country_iso"] = country_iso

            return get_number_rent_rates(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getAutoUnrentSettings", description="[Extended API] Get auto-unrent settings.")
    def get_auto_unrent_settings_tool(
        account: Optional[str] = None
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account

            return get_auto_unrent_settings(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="updateAutoUnrentSettings", description="[Extended API] Update auto-unrent settings.")
    def update_auto_unrent_settings_tool(
        account: Optional[str] = None,
        auto_unrent_enabled: Optional[bool] = None,
        threshold_days: Optional[int] = None,
        numbers_to_exclude: Optional[List[str]] = None,
        email_reminders_enabled: Optional[bool] = None
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if auto_unrent_enabled is not None:
                params["auto_unrent_enabled"] = auto_unrent_enabled
            if threshold_days is not None:
                params["threshold_days"] = threshold_days
            if numbers_to_exclude is not None:
                params["numbers_to_exclude"] = numbers_to_exclude
            if email_reminders_enabled is not None:
                params["email_reminders_enabled"] = email_reminders_enabled

            return update_auto_unrent_settings(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="revalidateNumbers", description="[Extended API] Revalidate phone numbers.")
    def revalidate_numbers_tool(
        account: Optional[str] = None
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account

            return revalidate_numbers(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="listSmsOnlyNumbers", description="[Extended API] List SMS-only rented numbers.")
    def list_sms_only_numbers_tool(
        account: Optional[str] = None
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account

            return list_sms_only_numbers(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="listCombinedSmsNumbers", description="[Extended API] List combined validated and rented SMS numbers.")
    def list_combined_sms_numbers_tool(
        account: Optional[str] = None
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account

            return list_combined_sms_numbers(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="autoRentSmsNumber", description="[Extended API] Auto-rent SMS number.")
    def auto_rent_sms_number_tool(
        account: Optional[str] = None,
        country_iso: str = None,
        feature: Optional[str] = None
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if country_iso:
                params["country_iso"] = country_iso
            if feature:
                params["feature"] = feature

            return auto_rent_sms_number(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}
