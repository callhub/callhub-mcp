#!/usr/bin/env python3
"""CallHub MCP Server."""

import sys
from pathlib import Path

import logging
logger = logging.getLogger("callhub")

# Add the bundled dependency directory to the import path. The MCPB bundle
# ships third-party dependencies under `lib/` alongside this file, so no
# runtime installation is ever required.
server_dir = Path(__file__).parent
lib_path = server_dir / "lib"
if lib_path.exists():
    sys.path.insert(0, str(lib_path))


"""
CallHub MCP Server - Main Module

This server provides tools for interacting with the CallHub API through Claude.

## Server Restart Guidelines

The CallHub MCP server must be restarted manually by the user after any code changes.
If you're using Claude or another AI assistant to modify this code:

1. The AI should NEVER assume a restart has occurred
2. The AI should ALWAYS pause after suggesting code changes
3. The AI should explicitly ask the user to restart the server
4. The AI should wait for confirmation before proceeding with testing

This is critical for ensuring code changes take effect before testing.
"""

# IMPORTANT: Server restart required after code changes!
# When implementing changes to this file or other modules:
# 1. Always pause after suggesting code changes
# 2. Ask the user to implement the changes and restart the server
# 3. Wait for explicit confirmation that the restart is complete
# 4. Only then proceed with testing the changes


import sys
import datetime
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from typing import Optional, List, Dict, Any, Union # Added Union here

# Import from tools_callhub for backwards compatibility
from tools_callhub import (
    list_accounts,
    add_callhub_account,
    update_callhub_account,
    delete_callhub_account,
    fetch_agents,
)

# Import directly from new module structure for new functions
from callhub.agents import (
    list_agents,
    get_agent,
    create_agent,
    get_live_agents
)

from callhub.teams import (
    list_teams,
    get_team,
    create_team,
    update_team,
    delete_team,
    get_team_agents,
    get_team_agent_details,
    add_agents_to_team,
    remove_agents_from_team,
    validate_team_exists
)

from callhub.contacts import (
    list_contacts,
    get_contact,
    create_contact,
    create_contacts_bulk,
    update_contact,
    delete_contact,
    get_contact_fields,
)

from callhub.users import (
    list_users,
    get_credit_usage,
)

from callhub.dnc import (
    create_dnc_contact,
    list_dnc_contacts,
    update_dnc_contact,
    delete_dnc_contact,
    create_dnc_list,
    list_dnc_lists,
    update_dnc_list,
    delete_dnc_list
)

from callhub.campaigns import (list_call_center_campaigns , update_call_center_campaign ,
                               create_call_center_campaign , exportCampaignData  ,
                               getCampaignStatsAdvanced , get_media_files   )

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
    auto_rent_sms_number
)

from callhub.vb_campaigns import (get_vb_campaign , create_vb_campaign_template ,
                                  create_voice_broadcast_campaign ,list_voice_broadcasts )

from callhub.sms_campaigns import (
    list_sms_campaigns,
    update_sms_campaign
)

from callhub.p2p_campaigns import (list_p2p_campaigns , update_p2p_campaign ,
                                   get_p2p_campaign_agents , add_agents_to_p2p_campaign , reassign_p2p_agents ,
                                   get_p2p_surveys , create_p2p_campaign)


from callhub.sms_broadcasts import (
    create_sms_broadcast,
    get_sms_broadcast,
    update_sms_broadcast
)


from callhub.agent_activation_manual import (
    generate_export_url,
    process_activation_csv
)

from callhub.csv_processor import (
    process_uploaded_csv,
    process_agent_activation_csv_from_file,
)
from callhub.phonebooks import (
    list_phonebooks,
    get_phonebook,
    create_phonebook,
    update_phonebook,
    delete_phonebook,
    add_contacts_to_phonebook,
    remove_contact_from_phonebook,
    get_phonebook_count,
    get_phonebook_contacts,
)

from callhub.tags import (
    list_tags,
    get_tag,
    create_tag,
    update_tag,
    delete_tag,
    add_tag_to_contact,
    remove_tag_from_contact,
)

from callhub.custom_fields import (
    list_custom_fields,
    get_custom_field,
    create_custom_field,
    update_custom_field,
    delete_custom_field,
    update_contact_custom_field,
)

from callhub.webhooks import (
    list_webhooks,
    get_webhook,
    create_webhook,
    delete_webhook,
)

from callhub.survey_templates import (
    list_survey_templates,
    get_survey_template,
    create_survey_template,
    update_survey_template,
    delete_survey_template,
)

from callhub.questions import (
    list_questions,
    get_question
)

from callhub.integration_fields import (
    list_integration_fields,
    get_integration_field
)

from callhub.urls import (
    get_shortened_url,
    list_shortened_urls
)

from callhub.api_utils import (
    getApiSchema
)

from callhub.utils import parse_input_fields
from callhub.relational_organizing import (
    create_relational_organizing_campaign,
    duplicate_relational_organizing_campaign,
    assign_agents_to_relational_organizing_campaign,
    update_relational_organizing_campaign,
    get_relational_organizing_campaign,
    update_relational_organizing_campaign_status,
)
from callhub.sms_broadcasts import duplicate_sms_broadcast
from callhub.p2p_campaigns import duplicate_p2p_campaign
from callhub.campaigns import add_agents_to_power_campaign, duplicate_power_campaign, export_power_campaign
from callhub.vb_campaigns import duplicate_vb_campaign
from callhub.sms_campaigns import export_sms_report


# Load .env (for CALLHUB_ACCOUNT, etc.)
load_dotenv()

# Initialize the MCP server
server = FastMCP(name="callhub-mcp-py")


@server.tool(name="listAccounts", description="List configured CallHub accounts.")
def list_accounts_tool() -> dict:
    try:
        return list_accounts({})
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="configureAccount", description="Add or update a CallHub account configuration. Use this to set up new accounts or modify existing ones. All fields (accountName, username, apiKey, baseUrl) are required.")
def configure_account_tool(accountName: str, username: str, apiKey: str, baseUrl: str) -> dict:
    try:
        # Check if account exists
        accounts = list_accounts({}).get("accounts", [])
        if accountName.lower() in [a.lower() for a in accounts]:
            # Update existing account
            return update_callhub_account({
                "accountName": accountName,
                "username": username,
                "apiKey": apiKey,
                "baseUrl": baseUrl
            })
        else:
            # Add new account
            return add_callhub_account({
                "accountName": accountName,
                "username": username,
                "apiKey": apiKey,
                "baseUrl": baseUrl
            })
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="deleteAccount", description="Delete a CallHub account configuration. This will remove the account from the .env file.")
def delete_account_tool(accountName: str) -> dict:
    try:
        return delete_callhub_account({"accountName": accountName})
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="listAgents", description="List all agents for the CallHub account. Accepts optional 'page' (number or full URL) and 'include_pending' (boolean) arguments. IMPORTANT: The 'include_pending' parameter only includes agents in certain states - it DOES NOT include newly created agents awaiting email verification. Those pending agents must be managed using the exportAgentActivationUrls workflow.")
def list_agents_tool(account: Optional[str] = None, page: Optional[Union[str, int]] = None, include_pending: Optional[bool] = False) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account

        # Pass the page argument if it's provided
        if page is not None:
            params["page"] = page

        # Pass the include_pending argument if it's True
        if include_pending:
            params["include_pending"] = True

        # Directly call the function from callhub.agents
        return list_agents(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="getAgent", description="Get details for a specific agent by ID.")
def get_agent_tool(account: Optional[str] = None, agentId: Optional[str] = None) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account
        if agentId:
            params["agentId"] = agentId
        return get_agent(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="createAgent", description="Create a new agent with required email, username, and team. Note: Only these three fields are supported. Team should be the team NAME. IMPORTANT: Newly created agents exist in a 'pending' state and will NOT be visible through the standard listAgents API even with include_pending=true. To manage pending agent activation, use exportAgentActivationUrls or getAgentActivationExportUrl followed by the activation functions workflow.")
def create_agent_tool(
    account: Optional[str] = None,
    email: Optional[str] = None,
    username: Optional[str] = None,
    team: Optional[str] = None
) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account
        if email:
            params["email"] = email
        if username:
            params["username"] = username
        if team:
            params["team"] = team

        # Validate that the team exists before creating the agent
        if team:
            team_validation = validate_team_exists(account, team)
            if not team_validation.get("exists"):
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": team_validation.get("message")},
                        {"type": "text", "text": "Use the createTeam tool to create this team first."}
                    ]
                }

        return create_agent(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}




@server.tool(name="getLiveAgents", description="Get a list of all agents currently connected to any campaign.")
def get_live_agents_tool(account: Optional[str] = None) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account
        return get_live_agents(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="listContacts", description="List contacts with pagination, filtering, or fetch all.")
def list_contacts_tool(
    account: Optional[str] = None,
    page: Optional[int] = None,
    pageSize: Optional[int] = None,
    filters: Optional[dict] = None,
    allPages: bool = False
) -> dict:
    try:
        params: dict = {"allPages": allPages}
        if account:
            params["accountName"] = account
        if page is not None:
            params["page"] = page
        if pageSize is not None:
            params["pageSize"] = pageSize
        if filters is not None:
            params["filters"] = filters
        return list_contacts(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="getContact", description="Retrieve a single contact by ID.")
def get_contact_tool(
    account: Optional[str] = None,
    contactId: Optional[str] = None
) -> dict:
    try:
        params: dict = {"contactId": contactId}
        if account:
            params["accountName"] = account
        return get_contact(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="createContact", description="Create a new contact. Pass contact details as URL-encoded string (e.g., 'contact=1234567890&first_name=John&last_name=Doe').")
def create_contact_tool(
    account: Optional[str] = None,
    contact_fields: str = None
) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account

        # Parse contact_fields using our improved parser
        if contact_fields:
            parsed_fields = parse_input_fields(contact_fields)
            params.update(parsed_fields)

        return create_contact(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="bulkCreateContacts", description="Create multiple contacts by uploading a CSV file or providing a CSV URL. Requires phonebook_id parameter. Optional country_choice ('file' or 'custom') and country_iso (when country_choice is 'custom'). Note: This API has a rate limit of 1 call per minute.")
def create_contacts_bulk_tool(
    account: Optional[str] = None,
    phonebook_id: Optional[str] = None,  # Added phonebook_id parameter
    csv_file_path: Optional[str] = None,
    csv_url: Optional[str] = None,
    mapping: Optional[Dict[str, int]] = None,
    country_choice: Optional[str] = None,  # Added country_choice parameter
    country_iso: Optional[str] = None      # Added country_iso parameter
) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account

        # Add the phonebook_id parameter
        if phonebook_id:
            params["phonebook_id"] = phonebook_id

        # Add country parameters
        if country_choice:
            params["country_choice"] = country_choice

        if country_iso:
            params["country_iso"] = country_iso

        if csv_file_path:
            params["csv_file_path"] = csv_file_path

        if csv_url:
            params["csv_url"] = csv_url

        if mapping:
            params["mapping"] = mapping

        result = create_contacts_bulk(params)

        # Handle rate limiting with a user-friendly message
        if "isRateLimited" in result:
            retry_after = result.get("retryAfter", 60)
            message = result.get("message", f"The bulk create contacts API is currently rate limited. Please try again in {retry_after} seconds.")

            return {
                "isError": True,
                "content": [
                    {"type": "text", "text": message},
                    {"type": "text", "text": f"The API can only be called once per minute. Current wait time: {retry_after} seconds."}
                ]
            }

        return result
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="updateContact", description="Update a contact by phone number. Pass fields as URL-encoded string (e.g., 'contact=12015550123&mobile=12015550124'). Note: May create a new contact if multiple contacts have the same phone number.")
def update_contact_tool(
    account: Optional[str] = None,
    update_fields: str = None
) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account

        # Parse update_fields using our improved parser
        if update_fields:
            parsed_fields = parse_input_fields(update_fields)
            params.update(parsed_fields)

        # Ensure we have the contact phone number
        if "contact" not in params:
            return {"isError": True, "content": [{"type": "text", "text": "The 'contact' field (phone number) is required to identify which contact to update."}]}

        return update_contact(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

@server.tool(name="deleteContact", description="Delete a contact by ID.")
def delete_contact_tool(
    account: Optional[str] = None,
    contactId: Optional[str] = None
) -> dict:
    try:
        params = {"contactId": contactId}
        if account:
            params["accountName"] = account
        return delete_contact(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="getContactFields", description="List all available contact fields for this account.")
def get_contact_fields_tool(
    account: Optional[str] = None
) -> dict:
    try:
        params: dict = {}
        if account:
            params["accountName"] = account
        return get_contact_fields(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="listContactLists", description="List phonebooks with optional pagination.")
def list_phonebooks_tool(
    account: Optional[str] = None,
    page: Optional[int] = None,
    pageSize: Optional[int] = None
) -> dict:
    try:
        params: dict = {}
        if account:
            params["accountName"] = account
        if page is not None:
            params["page"] = page
        if pageSize is not None:
            params["pageSize"] = pageSize
        return list_phonebooks(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="getContactList", description="Retrieve a single phonebook by ID.")
def get_phonebook_tool(
    account: Optional[str] = None,
    phonebookId: Optional[str] = None
) -> dict:
    try:
        params = {"phonebookId": phonebookId}
        if account:
            params["accountName"] = account
        return get_phonebook(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="createContactList", description="Create a new phonebook. Pass fields as URL-encoded string (e.g., 'name=MyPhonebook&description=Description').")
def create_phonebook_tool(
    account: Optional[str] = None,
    phonebook_fields: str = None
) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account

        # Parse phonebook_fields using our improved parser
        if phonebook_fields:
            parsed_fields = parse_input_fields(phonebook_fields)
            params.update(parsed_fields)

        return create_phonebook(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="updateContactList", description="Update a phonebook. Pass fields as URL-encoded string (e.g., 'name=NewName&description=NewDesc').")
def update_phonebook_tool(
    account: Optional[str] = None,
    phonebookId: Optional[str] = None,
    update_fields: str = None
) -> dict:
    try:
        params = {"phonebookId": phonebookId}
        if account:
            params["accountName"] = account

        # Parse update_fields using our improved parser
        if update_fields:
            parsed_fields = parse_input_fields(update_fields)
            params.update(parsed_fields)

        return update_phonebook(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="deleteContactList", description="Delete a phonebook by ID.")
def delete_phonebook_tool(
    account: Optional[str] = None,
    phonebookId: Optional[str] = None
) -> dict:
    try:
        params = {"phonebookId": phonebookId}
        if account:
            params["accountName"] = account
        return delete_phonebook(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="addContactsToContactList", description="Add (upsert) contacts into a phonebook.")
def add_contacts_to_phonebook_tool(
    account: str | None = None,
    phonebookId: str | None = None,
    contactIds: list = None
) -> dict:
    try:
        # Validate required parameters
        if not phonebookId:
            return {"isError": True, "content": [{"type": "text", "text": "phonebookId is required"}]}
        if not contactIds:
            return {"isError": True, "content": [{"type": "text", "text": "contactIds is required"}]}

        # Ensure contactIds is a list
        if not isinstance(contactIds, list):
            return {"isError": True, "content": [{"type": "text", "text": "contactIds must be a list"}]}

        # Convert all contactIds to strings (API requirement)
        contact_ids_str = [str(cid) for cid in contactIds]

        params = {
            "phonebookId": phonebookId,
            "contactIds": contact_ids_str
        }

        if account:
            params["accountName"] = account

        return add_contacts_to_phonebook(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

@server.tool(name="removeContactsFromContactList", description="Remove a contact from a phonebook.")
def remove_contact_from_phonebook_tool(
    account: Optional[str] = None,
    phonebookId: Optional[str] = None,
    contactId: Optional[str] = None
) -> dict:
    try:
        params = {"phonebookId": phonebookId, "contactId": contactId}
        if account:
            params["accountName"] = account
        return remove_contact_from_phonebook(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="getContactListCount", description="Get total contacts in a phonebook.")
def get_phonebook_count_tool(
    account: Optional[str] = None,
    phonebookId: Optional[str] = None
) -> dict:
    try:
        params = {"phonebookId": phonebookId}
        if account:
            params["accountName"] = account
        return get_phonebook_count(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="getContactListContacts", description="Get contacts in a phonebook with pagination.")
def get_phonebook_contacts_tool(
    account: Optional[str] = None,
    phonebookId: Optional[str] = None,
    page: Optional[int] = None,
    pageSize: Optional[int] = None,
    allPages: bool = False
) -> dict:
    try:
        params = {
            "phonebookId": phonebookId,
            "allPages": allPages
        }
        if account:
            params["accountName"] = account
        if page is not None:
            params["page"] = page
        if pageSize is not None:
            params["pageSize"] = pageSize

        return get_phonebook_contacts(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


# Tag Management Tools

@server.tool(name="listTags", description="List all tags with optional pagination.")
def list_tags_tool(
    account: Optional[str] = None,
    page: Optional[int] = None,
    pageSize: Optional[int] = None
) -> dict:
    try:
        params: dict = {}
        if account:
            params["accountName"] = account
        if page is not None:
            params["page"] = page
        if pageSize is not None:
            params["pageSize"] = pageSize
        return list_tags(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="getTag", description="Retrieve a single tag by ID.")
def get_tag_tool(
    account: Optional[str] = None,
    tagId: Optional[str] = None
) -> dict:
    try:
        params = {"tagId": tagId}
        if account:
            params["accountName"] = account
        return get_tag(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="createTag", description="Create a new tag.")
def create_tag_tool(
    account: Optional[str] = None,
    name: str = None
) -> dict:
    try:
        params = {"name": name}
        if account:
            params["accountName"] = account

        return create_tag(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="updateTag", description="Update an existing tag by ID.")
def update_tag_tool(
    account: Optional[str] = None,
    tagId: str = None,
    name: Optional[str] = None,
    description: Optional[str] = None
) -> dict:
    try:
        params = {"tagId": tagId}
        if account:
            params["accountName"] = account
        if name:
            params["name"] = name
        if description:
            params["description"] = description

        return update_tag(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="deleteTag", description="Delete a tag by ID.")
def delete_tag_tool(
    account: Optional[str] = None,
    tagId: str = None
) -> dict:
    try:
        params = {"tagId": tagId}
        if account:
            params["accountName"] = account

        return delete_tag(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="addTagsToContact", description="Add tags to a contact by specifying tag names.")
def add_tag_to_contact_tool(
    account: Optional[str] = None,
    contactId: str = None,
    tagNames: List[str] = None
) -> dict:
    try:
        params = {
            "contactId": contactId,
            "tagNames": tagNames
        }
        if account:
            params["accountName"] = account

        return add_tag_to_contact(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="removeTagFromContact", description="Remove a tag from a contact.")
def remove_tag_from_contact_tool(
    account: Optional[str] = None,
    contactId: str = None,
    tagId: str = None
) -> dict:
    try:
        params = {
            "contactId": contactId,
            "tagId": tagId
        }
        if account:
            params["accountName"] = account

        return remove_tag_from_contact(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


# Custom Fields Tools

@server.tool(name="listCustomFields", description="List all custom fields with optional pagination.")
def list_custom_fields_tool(
    account: Optional[str] = None,
    page: Optional[int] = None,
    pageSize: Optional[int] = None
) -> dict:
    try:
        params: dict = {}
        if account:
            params["accountName"] = account
        if page is not None:
            params["page"] = page
        if pageSize is not None:
            params["pageSize"] = pageSize
        return list_custom_fields(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="getCustomField", description="Retrieve a single custom field by ID.")
def get_custom_field_tool(
    account: Optional[str] = None,
    customFieldId: Optional[str] = None
) -> dict:
    try:
        params = {"customFieldId": customFieldId}
        if account:
            params["accountName"] = account
        return get_custom_field(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="createCustomField", description="Create a new custom field with name, type, and optional choices for Multi-choice type.")
def create_custom_field_tool(
    account: Optional[str] = None,
    name: str = None,
    field_type: str = None,
    choices: Optional[List[str]] = None
) -> dict:
    try:
        params = {
            "name": name,
            "field_type": field_type
        }
        if account:
            params["accountName"] = account
        if choices and field_type == "Multi-choice":
            params["choices"] = choices

        return create_custom_field(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="updateCustomField", description="Update an existing custom field by ID.")
def update_custom_field_tool(
    account: Optional[str] = None,
    customFieldId: str = None,
    name: Optional[str] = None,
    options: Optional[List[str]] = None
) -> dict:
    try:
        params = {"customFieldId": customFieldId}
        if account:
            params["accountName"] = account
        if name:
            params["name"] = name
        if options:
            params["options"] = options

        return update_custom_field(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="deleteCustomField", description="Delete a custom field by ID.")
def delete_custom_field_tool(
    account: Optional[str] = None,
    customFieldId: str = None
) -> dict:
    try:
        params = {"customFieldId": customFieldId}
        if account:
            params["accountName"] = account

        return delete_custom_field(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="setContactCustomField", description="Update a custom field value for a contact.")
def update_contact_custom_field_tool(
    account: Optional[str] = None,
    contactId: str = None,
    customFieldId: str = None,
    value: Any = None
) -> dict:
    try:
        params = {
            "contactId": contactId,
            "customFieldId": customFieldId,
            "value": value
        }
        if account:
            params["accountName"] = account

        return update_contact_custom_field(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


# Webhook Management Tools

@server.tool(name="listWebhooks", description="List all webhooks with optional pagination.")
def list_webhooks_tool(
    account: Optional[str] = None,
    page: Optional[int] = None,
    pageSize: Optional[int] = None
) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account
        if page is not None:
            params["page"] = page
        if pageSize is not None:
            params["pageSize"] = pageSize

        return list_webhooks(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="getWebhook", description="Retrieve a single webhook by ID.")
def get_webhook_tool(
    account: Optional[str] = None,
    webhookId: str = None
) -> dict:
    try:
        params = {"webhookId": webhookId}
        if account:
            params["accountName"] = account

        return get_webhook(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="createWebhook", description="Create a new webhook. Valid event types: 'vb.transfer', 'sb.reply', 'cc.notes', or 'agent.activation'.")
def create_webhook_tool(
    account: Optional[str] = None,
    event_name: str = None,
    target_url: str = None
) -> dict:
    try:
        # Validate required parameters
        if not event_name:
            return {"isError": True, "content": [{"type": "text", "text": "'event_name' is required."}]}
        if not target_url:
            return {"isError": True, "content": [{"type": "text", "text": "'target_url' is required."}]}

        # Validate event type
        valid_events = ['vb.transfer', 'sb.reply', 'cc.notes', 'agent.activation']
        if event_name not in valid_events:
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"'event_name' must be one of: {', '.join(valid_events)}"}]
            }

        params = {
            "event_name": event_name,
            "target_url": target_url
        }
        if account:
            params["accountName"] = account

        return create_webhook(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="deleteWebhook", description="Delete a webhook by ID.")
def delete_webhook_tool(
    account: Optional[str] = None,
    webhookId: str = None
) -> dict:
    try:
        # Validate required parameters
        if not webhookId:
            return {"isError": True, "content": [{"type": "text", "text": "'webhookId' is required."}]}

        params = {"webhookId": webhookId}
        if account:
            params["accountName"] = account

        return delete_webhook(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


# Call Center Campaign Management Tools

@server.tool(name="listCallCenterCampaigns", description="List all call center campaigns with optional pagination.")
def list_call_center_campaigns_tool(
    account: Optional[str] = None,
    page: Optional[int] = None,
    pageSize: Optional[int] = None
) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account
        if page is not None:
            params["page"] = page
        if pageSize is not None:
            params["pageSize"] = pageSize

        return list_call_center_campaigns(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="updateCallCenterCampaignStatus", description="Update a call center campaign's status. Valid values: 'pause', 'resume', 'stop', 'restart'.")
def update_call_center_campaign_tool(
    account: Optional[str] = None,
    campaignId: str = None,
    status: str = None
) -> dict:
    try:
        # Validate required parameters
        if not campaignId:
            return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}

        if not status or status not in ["pause", "resume", "stop", "restart"]:
            return {
                "isError": True,
                "content": [{"type": "text", "text": "Valid 'status' is required: pause, resume, stop, or restart"}]
            }

        params = {
            "campaignId": campaignId,
            "status": status
        }
        if account:
            params["accountName"] = account

        return update_call_center_campaign(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}




@server.tool(name="createCallCenterCampaign", description="Create a new call center campaign with a complex script structure.")
def create_call_center_campaign_tool(
    account: Optional[str] = None,
    campaign_data: dict = None
) -> dict:
    try:
        # Validate required parameters
        if not campaign_data:
            return {"isError": True, "content": [{"type": "text", "text": "'campaign_data' is required."}]}

        params = {"campaign_data": campaign_data}
        if account:
            params["accountName"] = account

        return create_call_center_campaign(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="duplicateCallCenterCampaign", description="Duplicates a PowerCampaign with specified parameters.")
def duplicate_power_campaign_tool(
    campaign_id: int,
    phonebook_ids: List[int],
    assign_all_agents: bool,
    account: Optional[str] = None,
    target_account: Optional[str] = None,
    name: Optional[str] = None,
    callerid: Optional[Dict] = None,
    callerid_block: Optional[Dict] = None,
    textid: Optional[Dict] = None,
    dialin: Optional[Dict] = None
) -> dict:
    try:
        params = {
            "campaign_id": campaign_id,
            "phonebook_ids": phonebook_ids,
            "assign_all_agents": assign_all_agents,
        }
        if account:
            params["accountName"] = account
        if target_account:
            params["target_account"] = target_account
        if name:
            params["name"] = name
        if callerid:
            params["callerid"] = callerid
        if callerid_block:
            params["callerid_block"] = callerid_block
        if textid:
            params["textid"] = textid
        if dialin:
            params["dialin"] = dialin

        # This function is expected to be in callhub/utils.py
        return duplicate_power_campaign(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

@server.tool(name="exportCampaignData", description="Export campaign data in specified format.")
def export_campaign_data_tool(
    account: Optional[str] = None,
    campaignId: str = None,
    format: str = "csv"
) -> dict:
    try:
        if not campaignId:
            return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}

        params = {"campaignId": campaignId, "format": format}
        if account:
            params["accountName"] = account

        return exportCampaignData(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

@server.tool(name="getCampaignStatsAdvanced", description="Get enhanced campaign statistics.")
def get_campaign_stats_advanced_tool(
    account: Optional[str] = None,
    campaignId: str = None,
    includeDetails: bool = True
) -> dict:
    try:
        if not campaignId:
            return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}

        params = {"campaignId": campaignId, "includeDetails": includeDetails}
        if account:
            params["accountName"] = account

        return getCampaignStatsAdvanced(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="listMedia", description="Retrieve a list of media files (audio, images, videos) uploaded to CallHub. Supports pagination.")
def get_media_files_tool(
    account: Optional[str] = None,
    page: Optional[int] = None,
    pageSize: Optional[int] = None,
    file_type: Optional[str] = None, # 'audio', 'image', 'video'
    search: Optional[str] = None # Search by file name
) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account
        if page is not None:
            params["page"] = page
        if pageSize is not None:
            params["pageSize"] = pageSize
        if file_type:
            params["file_type"] = file_type
        if search:
            params["search"] = search

        # Assuming a function `list_media_files` exists in `callhub.media`
        return get_media_files(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


# Phone Number Management Tools

@server.tool(name="listRentedCallingNumbers", description="List all rented calling numbers (caller IDs) for the account.")
def list_rented_numbers_tool(
    account: Optional[str] = None
) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account

        return list_rented_numbers(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


# Voice Broadcasting Campaign Management Tools

@server.tool(name="listVoiceBroadcastCampaigns", description="List all voice broadcast campaigns with optional pagination.")
def list_voice_broadcast_campaigns_tool(
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

        return list_voice_broadcasts(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="getVoiceBroadcastCampaign", description="Get a voice broadcast campaign by ID.")
def get_vb_campaign_tool(
    account: Optional[str] = None,
    campaignId: str = None
) -> dict:
    try:
        if not campaignId:
            return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}
        params = {"campaignId": campaignId}
        if account:
            params["accountName"] = account
        return get_vb_campaign(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="createVoiceBroadcastCampaign", description="Create a new voice broadcast campaign.")
def create_vb_campaign_tool(
    account: Optional[str] = None,
    campaign_data: dict = None
) -> dict:
    try:
        if not campaign_data:
            return {"isError": True, "content": [{"type": "text", "text": "'campaign_data' is required."}]}
        params = campaign_data.copy()
        if account:
            params["accountName"] = account
        return create_voice_broadcast_campaign(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="createVoiceBroadcastTemplate", description="Create a new voice broadcast campaign template.")
def create_vb_campaign_template_tool(
    account: Optional[str] = None,
    template_data: dict = None
) -> dict:
    try:
        if not template_data:
            return {"isError": True, "content": [{"type": "text", "text": "'template_data' is required."}]}
        params = {"template_data": template_data}
        if account:
            params["accountName"] = account
        return create_vb_campaign_template(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="listValidatedNumbers", description="List all validated personal phone numbers that can be used as caller IDs.")
def list_validated_numbers_tool(
    account: Optional[str] = None
) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account

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
    setup_fee: Optional[bool] = None
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

        return rent_number(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


# SMS Campaign Management Tools

@server.tool(name="listTextBroadcasts", description="List all SMS campaigns with optional pagination.")
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


@server.tool(name="updateSmsCampaignStatus", description="Update an SMS campaign's status. Valid values: 'start', 'pause', 'abort', 'end' or 1-4 numerically.")
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



# P2P Campaign Management Tools

@server.tool(name="listP2pCampaigns", description="List all P2P campaigns with optional pagination.")
def list_p2p_campaigns_tool(
    account: Optional[str] = None,
    page: Optional[int] = None,
    pageSize: Optional[int] = None
) -> dict:
    try:
        params = {}
        if account:
            params["account"] = account
        if page is not None:
            params["page"] = page
        if pageSize is not None:
            params["pageSize"] = pageSize

        return list_p2p_campaigns(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="updateP2pCampaignStatus", description="Update a P2P campaign's status. Valid values: 'start', 'pause', 'abort', 'end' or 1-4 numerically.")
def update_p2p_campaign_tool(
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

        return update_p2p_campaign(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}





@server.tool(name="listP2pCampaignAgents", description="Get agents for a P2P campaign.")
def get_p2p_campaign_agents_tool(
    account: Optional[str] = None,
    campaignId: str = None
) -> dict:
    try:
        if not campaignId:
            return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}

        params = {"campaignId": campaignId}
        if account:
            params["account"] = account

        return get_p2p_campaign_agents(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="addAgentsToP2pCampaign", description="Add agents to a P2P campaign.")
def add_agents_to_p2p_campaign_tool(
    account: Optional[str] = None,
    campaignId: str = None,
    agentIds: List[str] = None
) -> dict:
    try:
        if not campaignId:
            return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}
        if not agentIds:
            return {"isError": True, "content": [{"type": "text", "text": "'agentIds' is required."}]}

        params = {"campaignId": campaignId, "agentIds": agentIds}
        if account:
            params["account"] = account

        return add_agents_to_p2p_campaign(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="reassignP2pAgents", description="Reassign agents in a P2P campaign.")
def reassign_p2p_agents_tool(
    account: Optional[str] = None,
    campaignId: str = None,
    reassignData: dict = None
) -> dict:
    try:
        if not campaignId:
            return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}

        params = {"campaignId": campaignId, "reassignData": reassignData or {}}
        if account:
            params["account"] = account

        return reassign_p2p_agents(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="listP2pSurveys", description="Get surveys for a P2P campaign.")
def get_p2p_surveys_tool(
    account: Optional[str] = None,
    campaignId: Optional[str] = None
) -> dict:
    try:
        params = {}
        if campaignId:
            params["campaignId"] = campaignId
        if account:
            params["account"] = account

        return get_p2p_surveys(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}




@server.tool(name="createTextBroadcast", description="Create a new SMS broadcast campaign.")
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


@server.tool(name="getTextBroadcast", description="Get details of an SMS broadcast campaign.")
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


@server.tool(name="updateTextBroadcastStatus", description="Update an SMS broadcast campaign's status. Valid values: 'start', 'pause', 'abort', 'end' or 1-4 numerically.")
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

@server.tool(name="createP2pCampaign", description="Create a new P2P campaign with a complex script structure.")
def create_p2p_campaign_tool(
    account: Optional[str] = None,
    campaign_data: dict = None
) -> dict:
    try:
        # Validate required parameters
        if not campaign_data:
            return {"isError": True, "content": [{"type": "text", "text": "'campaign_data' is required."}]}

        params = {"campaign_data": campaign_data}
        if account:
            params["accountName"] = account

        return create_p2p_campaign(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


# User and Credit Usage Tools

@server.tool(name="getUsers", description="Retrieve a list of all users in the CallHub account.")
def get_users_tool(
    account: Optional[str] = None
) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account

        return list_users(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="getCreditUsage", description="Retrieve credit usage details for the CallHub account.")
def get_credit_usage_tool(
    account: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    generate_csv: Optional[bool] = False,
    campaign_type: Optional[int] = None
) -> dict:
    """Campaign Type Mapping: SMS Broadcast=1, Text2Join=3, P2P=4, Call Centre=5, Voice Broadcast=6"""
    try:
        params = {}
        if account:
            params["accountName"] = account
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if generate_csv is not None: # Pass boolean directly
            params["generate_csv"] = generate_csv
        if campaign_type is not None:
            params["campaign_type"] = campaign_type

        return get_credit_usage(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


# DNC Contact Management Tools

@server.tool(name="addToDnc", description="Create a new DNC contact with the specified phone number.")
def create_dnc_contact_tool(
    account: Optional[str] = None,
    dnc: str = None, # This is the DNC list URL
    phone_number: str = None,
    category: int = 3
) -> dict:
    """Create a new DNC contact.

    Args:
        account: The CallHub account name to use. Defaults to 'default'.
        dnc: URL of the DNC list that the phone number belongs to. Format: 'https://api.callhub.io/v1/dnc_lists/{id}/'
        phone_number: Phone number of the contact in E.164 format.
        category: 1 for call opt-out only, 2 for text opt-out only, 3 for both call and text opt-out. Defaults to 3.
    """
    try:
        # Parameters are passed directly to the imported function
        return create_dnc_contact({"account": account, "dnc": dnc, "phone_number": phone_number, "category": category})
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="listDncContacts", description="List contacts in the DNC (Do Not Call) list with optional pagination.")
def list_dnc_contacts_tool(
    account: Optional[str] = None,
    page: Optional[int] = None,
    pageSize: Optional[int] = None,
    allPages: bool = False
) -> dict:
    try:
        # Parameters are passed directly to the imported function
        return list_dnc_contacts({"account": account, "page": page, "pageSize": pageSize, "allPages": allPages})
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="updateDncContact", description="Update an existing DNC contact by ID.")
def update_dnc_contact_tool(
    account: Optional[str] = None,
    contactId: str = None, # DNC Contact ID (this is the 'id' or 'url' from listDncContacts)
    dnc: Optional[str] = None, # DNC List URL
    phone_number: Optional[str] = None # Phone number
) -> dict:
    try:
        # Parameters are passed directly to the imported function
        return update_dnc_contact({"account": account, "contactId": contactId, "dnc": dnc, "phone_number": phone_number})
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="removeFromDnc", description="Delete a DNC contact by ID.")
def delete_dnc_contact_tool(
    account: Optional[str] = None,
    contactId: str = None # DNC Contact ID
) -> dict:
    try:
        # Parameters are passed directly to the imported function
        return delete_dnc_contact({"account": account, "contactId": contactId})
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


# Team Management Tools

@server.tool(name="listTeams", description="List all teams in the CallHub account.")
def list_teams_tool(account: Optional[str] = None) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account
        return list_teams(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="getTeam", description="Get details for a specific team by ID.")
def get_team_tool(account: Optional[str] = None, teamId: Optional[str] = None) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account
        if teamId:
            params["teamId"] = teamId
        return get_team(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="createTeam", description="Create a new team.")
def create_team_tool(account: Optional[str] = None, name: str = None) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account
        if name:
            params["name"] = name
        return create_team(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="updateTeam", description="Update a team's name.")
def update_team_tool(account: Optional[str] = None, teamId: str = None, name: str = None) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account
        if teamId:
            params["teamId"] = teamId
        if name:
            params["name"] = name
        return update_team(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="deleteTeam", description="Delete a team by ID. All agents associated with the team will be unassigned.")
def delete_team_tool(account: Optional[str] = None, teamId: str = None) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account
        if teamId:
            params["teamId"] = teamId
        return delete_team(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="getTeamAgents", description="Get a list of all agents assigned to a specific team.")
def get_team_agents_tool(account: Optional[str] = None, teamId: str = None) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account
        if teamId:
            params["teamId"] = teamId
        return get_team_agents(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="getTeamAgentDetails", description="Get details for a specific agent in a team.")
def get_team_agent_details_tool(account: Optional[str] = None, teamId: str = None, agentId: str = None) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account
        if teamId:
            params["teamId"] = teamId
        if agentId:
            params["agentId"] = agentId
        return get_team_agent_details(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="addAgentsToTeam", description="Add one or more agents to a team.")
def add_agents_to_team_tool(account: Optional[str] = None, teamId: str = None, agentIds: List[str] = None) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account
        if teamId:
            params["teamId"] = teamId
        if agentIds:
            params["agentIds"] = agentIds # Should be a list of IDs
        return add_agents_to_team(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="removeAgentsFromTeam", description="Remove one or more agents from a team.")
def remove_agents_from_team_tool(account: Optional[str] = None, teamId: str = None, agentIds: List[str] = None) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account
        if teamId:
            params["teamId"] = teamId
        if agentIds:
            params["agentIds"] = agentIds # Should be a list of IDs
        return remove_agents_from_team(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


# DNC List Management Tools

@server.tool(name="createDncList", description="Create a new DNC list.")
def create_dnc_list_tool(
    account: Optional[str] = None,
    name: str = None
) -> dict:
    try:
        # Parameters are passed directly to the imported function
        return create_dnc_list({"account": account, "name": name})
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="listDncLists", description="List all DNC lists with optional pagination.")
def list_dnc_lists_tool(
    account: Optional[str] = None,
    page: Optional[int] = None,
    pageSize: Optional[int] = None,
    allPages: bool = False
) -> dict:
    try:
        # Parameters are passed directly to the imported function
        return list_dnc_lists({"account": account, "page": page, "pageSize": pageSize, "allPages": allPages})
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="createRelationalCampaign", description="Create a new relational organizing campaign.")
def create_relational_campaign_tool(
    account: Optional[str] = None,
    name: str = None,
    brief: str = None,
    phonebook_ids: list = None,
    user_tag_ids: list = None,
    default_outreach_medium: int = None,
    agent_assignment_choice: int = None,
    team_ids: list = None,
    starting_date: str = None,
    end_date: str = None,
    timezone: str = None,
    survey_id: int = None,
) -> dict:
    try:
        params = {
            "name": name,
            "brief": brief,
            "phonebook_ids": phonebook_ids,
            "user_tag_ids": user_tag_ids,
            "default_outreach_medium": default_outreach_medium,
            "agent_assignment_choice": agent_assignment_choice,
            "team_ids": team_ids,
            "starting_date": starting_date,
            "end_date": end_date,
            "timezone": timezone,
            "survey_id": survey_id,
        }
        if account:
            params["accountName"] = account
        return create_relational_organizing_campaign(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="duplicateRelationalCampaign", description="Duplicate a relational organizing campaign.")
def duplicate_relational_campaign_tool(
    account: Optional[str] = None, campaign_id: int = None
) -> dict:
    try:
        params = {"campaign_id": campaign_id}
        if account:
            params["accountName"] = account
        return duplicate_relational_organizing_campaign(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(
    name="assignRelationalCampaignAgents",
    description="Assign or remove agents to/from a relational organizing campaign.",
)
def assign_agents_to_relational_campaign_tool(
    account: Optional[str] = None, campaign_id: int = None, agent_ids_to_assign: list = None, agent_ids_to_remove: list = None
) -> dict:
    try:
        params = {"campaign_id": campaign_id, "agent_ids_to_assign": agent_ids_to_assign, "agent_ids_to_remove": agent_ids_to_remove}
        if account:
            params["accountName"] = account
        return assign_agents_to_relational_organizing_campaign(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}



@server.tool(name="duplicateTextBroadcast", description="Duplicate an SMS broadcast campaign.")
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


@server.tool(name="duplicateP2pCampaign", description="Duplicate a P2P campaign.")
def duplicate_p2p_campaign_tool(
    account: Optional[str] = None, campaign_id: int = None
) -> dict:
    try:
        params = {"campaignId": campaign_id}
        if account:
            params["accountName"] = account
        return duplicate_p2p_campaign(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="addAgentsToCallCenterCampaign", description="Add agents to a power campaign.")
def add_agents_to_power_campaign_tool(
    account: Optional[str] = None, campaign_id: int = None, agent_ids: list = None
) -> dict:
    try:
        params = {"campaignId": campaign_id, "agentIds": agent_ids}
        if account:
            params["accountName"] = account
        return add_agents_to_power_campaign(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="duplicateVoiceBroadcastCampaign", description="Duplicate a voice broadcast campaign.")
def duplicate_vb_campaign_tool(
    account: Optional[str] = None, campaign_id: int = None
) -> dict:
    try:
        params = {"campaignId": campaign_id}
        if account:
            params["accountName"] = account
        return duplicate_vb_campaign(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="updateRelationalCampaign", description="Update a relational organizing campaign.")
def update_relational_campaign_tool(
    account: Optional[str] = None,
    campaign_id: int = None,
    name: str = None,
    brief: str = None,
    phonebook_ids: list = None,
    user_tag_ids: list = None,
    default_outreach_medium: int = None,
    agent_assignment_choice: int = None,
    team_ids: list = None,
    starting_date: str = None,
    end_date: str = None,
    timezone: str = None,
    survey_id: int = None,
) -> dict:
    try:
        params = {
            "campaign_id": campaign_id,
            "name": name,
            "brief": brief,
            "phonebook_ids": phonebook_ids,
            "user_tag_ids": user_tag_ids,
            "default_outreach_medium": default_outreach_medium,
            "agent_assignment_choice": agent_assignment_choice,
            "team_ids": team_ids,
            "starting_date": starting_date,
            "end_date": end_date,
            "timezone": timezone,
            "survey_id": survey_id,
        }
        if account:
            params["accountName"] = account
        return update_relational_organizing_campaign(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="getRelationalCampaign", description="Get a relational organizing campaign.")
def get_relational_campaign_tool(
    account: Optional[str] = None, campaign_id: int = None
) -> dict:
    try:
        params = {"campaign_id": campaign_id}
        if account:
            params["accountName"] = account
        return get_relational_organizing_campaign(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="updateRelationalCampaignStatus", description="Update the status of a relational organizing campaign.")
def update_relational_campaign_status_tool(
    account: Optional[str] = None, campaign_id: int = None, status: str = None
) -> dict:
    try:
        params = {"campaign_id": campaign_id, "status": status}
        if account:
            params["accountName"] = account
        return update_relational_organizing_campaign_status(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="exportTextBroadcastReport", description="Export an SMS report for a campaign.")


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








@server.tool(name="exportCallCenterCampaign", description="Export a power campaign.")


def export_power_campaign_tool(


    account: Optional[str] = None, campaign_id: int = None


) -> dict:


    try:


        params = {"campaignId": campaign_id}


        if account:


            params["accountName"] = account


        return export_power_campaign(params)


    except Exception as e:


        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}@server.tool(name="updateDncList", description="Update an existing DNC list by ID.")
def update_dnc_list_tool(
    account: Optional[str] = None,
    listId: str = None, # DNC List ID
    name: str = None
) -> dict:
    try:
        # Parameters are passed directly to the imported function
        return update_dnc_list({"account": account, "listId": listId, "name": name})
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="deleteDncList", description="Delete a DNC list by ID.")
def delete_dnc_list_tool(
    account: Optional[str] = None,
    listId: str = None # DNC List ID
) -> dict:
    try:
        # Parameters are passed directly to the imported function
        return delete_dnc_list({"account": account, "listId": listId})
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="exportAgentActivationUrls", description="Export pending agent activation URLs. IMPORTANT: This requires browser session authentication rather than API key. There is NO way to access pending agent data through direct API calls. The user must download the CSV file from the URL provided.")
def export_agent_activation_urls_tool(account: Optional[str] = None) -> dict:
    """Generate a direct URL for exporting agent activation data.

    This tool provides a direct link to the agent activation export page in the CallHub web interface.
    The user will need to manually:
    1. Click the provided link
    2. Log in to CallHub if necessary
    3. Click the 'Export Pending Activations' button
    4. Download the CSV file
    5. Upload the CSV back to this conversation for processing

    Args:
        account: Optional account name to use (defaults to 'default')

    Returns:
        Dict with the export URL and instructions
    """
    try:
        # Generate export URL using the manual approach (no browser automation)
        return generate_export_url(account)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="getAgentActivationExportUrl", description="Get a direct URL for exporting agent activation data manually. IMPORTANT: There is NO way to access pending agent data through direct API calls. The user must manually download the CSV file from this URL. STOP and wait after displaying this URL before proceeding.")
def get_agent_activation_export_url_tool(account: Optional[str] = None) -> dict:
    """Generate a direct URL for exporting agent activation data.

    IMPORTANT: Do NOT use this tool proactively or for testing purposes unless specifically
    requested by the user. Only use when the user explicitly asks to export activation URLs
    or wants to perform a full agent workflow (like "add agents from this CSV and activate them").

    Args:
        account: Optional account name to use (defaults to 'default')

    Returns:
        Dict with the export URL and instructions
    """
    try:
        return generate_export_url(account)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="processAgentActivationCsv", description="Process an agent activation CSV file uploaded by the user. IMPORTANT: This function must be used with the CSV downloaded from the CallHub UI. Do NOT attempt to create test agents to demonstrate activation - always use this workflow.")
def process_agent_activation_csv_tool(csv_content: str) -> dict:
    """Process a CSV file containing agent activation URLs.

    IMPORTANT: Do NOT use this tool proactively or for testing purposes. Only use when:
    1. The user has explicitly uploaded a CSV file with agent activation URLs
    2. The user has explicitly requested to process activation URLs
    3. The user wants to complete an agent workflow like bulk activation with a specific password
       (e.g., "add the agents listed in this CSV and activate them with password 'CH2025'")

    Args:
        csv_content: Raw CSV content as a string

    Returns:
        Dict with the parsed activation data
    """
    try:
        return process_activation_csv(csv_content)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="processUploadedActivationCsv", description="IMPORTANT: When a user uploads a CSV file, Claude CANNOT read its contents directly. This tool takes the filename from the upload and searches for the actual file in the user's local system (Downloads, Desktop, etc.)")
def process_uploaded_activation_csv_tool(file_path: str) -> dict:
    """
    IMPORTANT: Claude CANNOT read the content of uploaded files.

    When a user uploads a CSV file to the conversation:
    1. Claude can only see the filename but NOT the content
    2. This tool uses that filename to search for the actual file in standard locations
       (Downloads folder, Desktop, Documents, etc.)
    3. The CSV is processed from the local file system, NOT from the upload

    Args:
        file_path: Name or path of the CSV file

    Returns:
        Dict with parsed activation data from the LOCAL file (not directly from the upload)
    """
    try:
        return process_agent_activation_csv_from_file(file_path)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="processUploadedCsv", description="IMPORTANT: When a user uploads a CSV file, Claude CANNOT read its contents directly. This tool takes the filename from the upload and searches for the actual file in the user's local system (Downloads, Desktop, etc.)")
def process_uploaded_csv_tool(file_path: str) -> dict:
    """
    IMPORTANT: Claude CANNOT read the content of uploaded files.

    When a user uploads a CSV file to the conversation:
    1. Claude can only see the filename but NOT the content
    2. This tool uses that filename to search for the actual file in standard locations
       (Downloads folder, Desktop, Documents, etc.)
    3. The CSV is processed from the local file system, NOT from the upload

    Args:
        file_path: Name or path of the CSV file

    Returns:
        Dict with parsed CSV data from the LOCAL file (not directly from the upload)
    """
    try:
        return process_uploaded_csv(file_path)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


# New Batch Activation Tools

# Survey Template Management Tools

@server.tool(name="listSurveyTemplates", description="List all survey templates for the authenticated user.")
def list_survey_templates_tool(
    account: Optional[str] = None
) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account
        return list_survey_templates(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="getSurveyTemplate", description="Get details for a specific survey template by ID.")
def get_survey_template_tool(
    account: Optional[str] = None,
    templateId: Optional[str] = None
) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account
        if templateId:
            params["templateId"] = templateId
        return get_survey_template(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="createSurveyTemplate", description="Create a new survey template with questions. Pass questions as a list of dictionaries with 'type', 'question', and optional 'question_name', 'is_initial_message' fields.")
def create_survey_template_tool(
    account: Optional[str] = None,
    label: str = None,
    questions: List[Dict[str, Any]] = None
) -> dict:
    try:
        if not label:
            return {"isError": True, "content": [{"type": "text", "text": "label is required"}]}
        
        params = {
            "label": label,
            "questions": questions or []
        }
        if account:
            params["accountName"] = account
        
        return create_survey_template(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="updateSurveyTemplate", description="Update an existing survey template.")
def update_survey_template_tool(
    account: Optional[str] = None,
    templateId: str = None,
    label: Optional[str] = None,
    questions: Optional[List[Dict[str, Any]]] = None
) -> dict:
    try:
        if not templateId:
            return {"isError": True, "content": [{"type": "text", "text": "templateId is required"}]}
        
        params = {"templateId": templateId}
        if account:
            params["accountName"] = account
        if label:
            params["label"] = label
        if questions:
            params["questions"] = questions
        
        return update_survey_template(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="deleteSurveyTemplate", description="Delete a survey template by ID.")
def delete_survey_template_tool(
    account: Optional[str] = None,
    templateId: str = None
) -> dict:
    try:
        if not templateId:
            return {"isError": True, "content": [{"type": "text", "text": "templateId is required"}]}
        
        params = {"templateId": templateId}
        if account:
            params["accountName"] = account
        
        return delete_survey_template(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


# Questions Management Tools

@server.tool(name="listQuestions", description="List all questions with optional type filtering (PDI_QUESTION, VAN_QUESTION).")
def list_questions_tool(
    account: Optional[str] = None,
    type: Optional[str] = None
) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account
        if type:
            params["type"] = type
        
        return list_questions(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="getQuestion", description="Get details for a specific question by ID.")
def get_question_tool(
    account: Optional[str] = None,
    questionId: Optional[str] = None
) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account
        if questionId:
            params["questionId"] = questionId
        
        return get_question(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


# Integration Fields Management Tools

@server.tool(name="listIntegrationFields", description="List all integration fields.")
def list_integration_fields_tool(
    account: Optional[str] = None
) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account
        
        return list_integration_fields(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="getIntegrationField", description="Get details for a specific integration field by ID.")
def get_integration_field_tool(
    account: Optional[str] = None,
    fieldId: Optional[str] = None
) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account
        if fieldId:
            params["fieldId"] = fieldId
        
        return get_integration_field(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


# Extended Number Management Tools

@server.tool(name="getAreaCodes", description="Get area codes for a specific country.")
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


@server.tool(name="getNumberRentRates", description="Get number rent rates for a specific country.")
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


@server.tool(name="getAutoUnrentSettings", description="Get auto-unrent settings.")
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


@server.tool(name="updateAutoUnrentSettings", description="Update auto-unrent settings.")
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


@server.tool(name="revalidateNumber", description="Revalidate phone numbers.")
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


@server.tool(name="listSmsOnlyNumbers", description="List SMS-only rented numbers.")
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


@server.tool(name="listCombinedSmsNumbers", description="List combined validated and rented SMS numbers.")
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


@server.tool(name="autoRentSmsNumber", description="Auto-rent SMS number.")
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


# openTerminalWithLogs function removed for security reasons


# Shortened URL Management Tools



@server.tool(name="getShortenedUrlStats", description="Get details of a shortened URL by its short code.")
def get_shortened_url_tool(
    account: Optional[str] = None,
    shortCode: Optional[str] = None
) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account
        if shortCode:
            params["shortCode"] = shortCode
        
        return get_shortened_url(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="listShortenedUrls", description="List all shortened URLs with optional pagination.")
def list_shortened_urls_tool(
    account: Optional[str] = None,
    page: Optional[int] = None,
    pageSize: Optional[int] = None
) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account
        if page is not None:
            params["page"] = page
        if pageSize is not None:
            params["pageSize"] = pageSize
        
        return list_shortened_urls(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


# API Schema and Utilities Tools

@server.tool(name="getApiSchema", description="Get the complete API schema documentation.")
def get_api_schema_tool(
    account: Optional[str] = None
) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account
        
        return getApiSchema(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}



# ---------------------------------------------------------------------------
# Additional tools (completeness + parity with the CallHub API)
# ---------------------------------------------------------------------------
from callhub.contacts import search_contacts, add_contact_notes
from callhub.campaigns import (
    get_call_center_campaign,
    delete_call_center_campaign,
    get_export_job_status,
)
from callhub.p2p_campaigns import get_p2p_campaign
from callhub.vb_campaigns import list_voice_broadcast_templates
from callhub.numbers import list_numbers_needing_revalidation
from callhub.dnc import add_to_suppression_list


@server.tool(name="searchContacts", description="Search contacts by phone number, name, or email. Use this to find a specific contact instead of paging through listContacts. Rate limit: 1 search per second.")
def search_contacts_tool(query: str, account: Optional[str] = None, page: Optional[Union[str, int]] = None) -> dict:
    try:
        params = {"query": query}
        if account:
            params["accountName"] = account
        if page is not None:
            params["page"] = page
        return search_contacts(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="addContactNotes", description="Save a note on a contact. Appends the note to the contact record.")
def add_contact_notes_tool(contactId: str, notes: str, account: Optional[str] = None) -> dict:
    try:
        params = {"contactId": contactId, "notes": notes}
        if account:
            params["accountName"] = account
        return add_contact_notes(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="getCallCenterCampaign", description="Get a single call center (power) campaign by ID.")
def get_call_center_campaign_tool(campaignId: str, account: Optional[str] = None) -> dict:
    try:
        params = {"campaignId": campaignId}
        if account:
            params["accountName"] = account
        return get_call_center_campaign(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="deleteCallCenterCampaign", description="Delete a call center (power) campaign by ID. This is permanent.")
def delete_call_center_campaign_tool(campaignId: str, account: Optional[str] = None) -> dict:
    try:
        params = {"campaignId": campaignId}
        if account:
            params["accountName"] = account
        return delete_call_center_campaign(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="getExportJobStatus", description="Poll an export job by its job_id (returned by export tools). When complete, the response includes the CSV download URL.")
def get_export_job_status_tool(jobId: str, account: Optional[str] = None) -> dict:
    try:
        params = {"jobId": jobId}
        if account:
            params["accountName"] = account
        return get_export_job_status(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="getP2pCampaign", description="Get a single P2P campaign by ID.")
def get_p2p_campaign_tool(campaignId: str, account: Optional[str] = None) -> dict:
    try:
        params = {"campaignId": campaignId}
        if account:
            params["accountName"] = account
        return get_p2p_campaign(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="listVoiceBroadcastTemplates", description="List voice broadcast templates.")
def list_voice_broadcast_templates_tool(account: Optional[str] = None, page: Optional[Union[str, int]] = None) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account
        if page is not None:
            params["page"] = page
        return list_voice_broadcast_templates(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="listNumbersNeedingRevalidation", description="List phone numbers that need revalidation.")
def list_numbers_needing_revalidation_tool(account: Optional[str] = None) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account
        return list_numbers_needing_revalidation(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="addToSuppressionList", description="Bulk-add numbers to a suppression list (a Call Center feature, distinct from DNC). records = [{'phone_number': ..., 'mobile_number': ...}, ...], max 10 per call.")
def add_to_suppression_list_tool(listId: str, records: List[Dict], account: Optional[str] = None) -> dict:
    try:
        params = {"listId": listId, "records": records}
        if account:
            params["accountName"] = account
        return add_to_suppression_list(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


from callhub.vb_campaigns import (
    delete_voice_broadcast_campaign,
    update_voice_broadcast_campaign,
)
from callhub.sms_campaigns import delete_sms_campaign
from callhub.users import share_credits
from callhub.campaigns import upload_media_file


@server.tool(name="deleteVoiceBroadcastCampaign", description="Delete a voice broadcast campaign by ID. This is permanent.")
def delete_voice_broadcast_campaign_tool(campaignId: str, account: Optional[str] = None) -> dict:
    try:
        params = {"campaignId": campaignId}
        if account:
            params["accountName"] = account
        return delete_voice_broadcast_campaign(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="updateVoiceBroadcastCampaign", description="Update a voice broadcast campaign by ID. Optional: name, status (int), frequency (calls per minute).")
def update_voice_broadcast_campaign_tool(campaignId: str, account: Optional[str] = None, name: Optional[str] = None, status: Optional[int] = None, frequency: Optional[int] = None) -> dict:
    try:
        params = {"campaignId": campaignId}
        if account:
            params["accountName"] = account
        if name is not None:
            params["name"] = name
        if status is not None:
            params["status"] = status
        if frequency is not None:
            params["frequency"] = frequency
        return update_voice_broadcast_campaign(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="deleteTextBroadcast", description="Delete an SMS/text broadcast campaign by ID. This is permanent.")
def delete_text_broadcast_tool(campaignId: str, account: Optional[str] = None) -> dict:
    try:
        params = {"campaignId": campaignId}
        if account:
            params["account"] = account
        return delete_sms_campaign(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="uploadMediaFile", description="Upload a local media file (audio/image/video/GIF) to the CallHub media library. Provide file_path (a local path), optional name and generate_gif.")
def upload_media_file_tool(file_path: str, account: Optional[str] = None, name: Optional[str] = None, generate_gif: Optional[bool] = None) -> dict:
    try:
        params = {"file_path": file_path}
        if account:
            params["accountName"] = account
        if name is not None:
            params["name"] = name
        if generate_gif is not None:
            params["generate_gif"] = generate_gif
        return upload_media_file(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="shareCredits", description="Share credits from an enterprise account to a subaccount. Requires subaccount (username) and transfer_amount (integer).")
def share_credits_tool(subaccount: str, transfer_amount: int, account: Optional[str] = None) -> dict:
    try:
        params = {"subaccount": subaccount, "transfer_amount": transfer_amount}
        if account:
            params["accountName"] = account
        return share_credits(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


# ---------------------------------------------------------------------------
# Backward-compatible tool aliases
#
# Tools were renamed to the canonical CallHub vocabulary (e.g. "phonebook" ->
# "contact list", "Vb" -> "VoiceBroadcast"). To avoid breaking existing saved
# flows that still call the old names, every old name resolves transparently to
# its canonical tool. Aliases are intentionally NOT listed in list_tools(), so
# the tool catalogue stays clean; they only resolve when invoked.
# ---------------------------------------------------------------------------
TOOL_ALIASES = {
    # Phonebook -> ContactList
    "createPhonebook": "createContactList",
    "getPhonebook": "getContactList",
    "updatePhonebook": "updateContactList",
    "deletePhonebook": "deleteContactList",
    "listPhonebooks": "listContactLists",
    "addContactsToPhonebook": "addContactsToContactList",
    "removeContactFromPhonebook": "removeContactsFromContactList",
    "getPhonebookContacts": "getContactListContacts",
    "getPhonebookCount": "getContactListCount",
    # Voice Broadcast
    "createVbCampaign": "createVoiceBroadcastCampaign",
    "getVbCampaign": "getVoiceBroadcastCampaign",
    "duplicateVbCampaign": "duplicateVoiceBroadcastCampaign",
    "createVbCampaignTemplate": "createVoiceBroadcastTemplate",
    # Text Broadcast
    "createSmsBroadcast": "createTextBroadcast",
    "getSmsBroadcast": "getTextBroadcast",
    "duplicateSmsBroadcast": "duplicateTextBroadcast",
    "updateSmsBroadcast": "updateTextBroadcastStatus",
    "listSmsCampaigns": "listTextBroadcasts",
    "exportSmsReport": "exportTextBroadcastReport",
    "updateSmsCampaign": "updateSmsCampaignStatus",
    # Call Center (Power -> CallCenter)
    "addAgentsToPowerCampaign": "addAgentsToCallCenterCampaign",
    "duplicatePowerCampaign": "duplicateCallCenterCampaign",
    "exportPowerCampaign": "exportCallCenterCampaign",
    "updateCallCenterCampaign": "updateCallCenterCampaignStatus",
    # P2P
    "createP2PCampaign": "createP2pCampaign",
    "getP2pCampaignAgents": "listP2pCampaignAgents",
    "updateP2pCampaign": "updateP2pCampaignStatus",
    "getP2pSurveys": "listP2pSurveys",
    # Relational
    "assignAgentsToRelationalCampaign": "assignRelationalCampaignAgents",
    # Contacts / Tags / Custom fields
    "createContactsBulk": "bulkCreateContacts",
    "addTagToContact": "addTagsToContact",
    "updateContactCustomField": "setContactCustomField",
    # Misc verb cleanups
    "getMediaFiles": "listMedia",
    "listRentedNumbers": "listRentedCallingNumbers",
    "revalidateNumbers": "revalidateNumber",
    "getShortenedUrl": "getShortenedUrlStats",
    "createDncContact": "addToDnc",
    "deleteDncContact": "removeFromDnc",
    # Consolidated duplicate (fetch_agents was a thin wrapper around list_agents)
    "fetchAgents": "listAgents",
}


def _install_tool_aliases(mcp_server, aliases):
    """Wrap the tool manager's call_tool so old tool names resolve to canonical
    ones without appearing in the tool listing."""
    tool_manager = mcp_server._tool_manager
    original_call_tool = tool_manager.call_tool

    async def call_tool_with_aliases(name, arguments, *args, **kwargs):
        canonical = aliases.get(name, name)
        return await original_call_tool(canonical, arguments, *args, **kwargs)

    tool_manager.call_tool = call_tool_with_aliases


_install_tool_aliases(server, TOOL_ALIASES)


if __name__ == "__main__":
    server.run()
