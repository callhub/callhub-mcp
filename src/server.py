#!/usr/bin/env python3

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

import os
import sys
import json
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
    delete_agent,
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

from callhub.campaigns import (
    list_call_center_campaigns,
    update_call_center_campaign,
    delete_call_center_campaign,
    create_call_center_campaign,
)

from callhub.numbers import (
    list_rented_numbers,
    list_validated_numbers,
    rent_number,
)

from callhub.voice_broadcasts import (
    list_voice_broadcasts,
    update_voice_broadcast,
    delete_voice_broadcast
)

from callhub.sms_campaigns import (
    list_sms_campaigns,
    update_sms_campaign,
    delete_sms_campaign
)

from callhub.p2p_campaigns import (list_p2p_campaigns , update_p2p_campaign , delete_p2p_campaign ,
                                   get_p2p_campaign_agents , add_agents_to_p2p_campaign , reassign_p2p_agents ,
                                   get_p2p_surveys , create_p2p_campaign)

from callhub.sms_broadcasts import (
    list_sms_broadcasts,
    update_sms_broadcast,
    delete_sms_broadcast
)

from callhub.agent_activation import (
    export_agent_activation_urls
)

from callhub.agent_activation_manual import (
    generate_export_url,
    process_activation_csv
)

from callhub.csv_processor import (
    process_uploaded_csv,
    process_agent_activation_csv_from_file,
    find_file,
    smart_file_process
)

from callhub.browser_automation import (
    export_agent_activation_urls_browser,
    activate_agents_with_password,
    process_local_activation_csv,
    parse_activation_csv
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

# Import our new batch activation tools
from callhub.mcp_tools.batch_activation_tools import (
    process_uploaded_activation_csv,
    prepare_agent_activation,
    activate_agents_with_batch_password,
    get_activation_status,
    reset_activation_state
)

from callhub.utils import parse_input_fields

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


@server.tool(name="fetchAgents", description="Retrieve current agents via CallHub API. Optional 'account'.")
def fetch_agents_tool(account: Optional[str] = None) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account
        return fetch_agents(params)
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


@server.tool(name="deleteAgent", description="Delete an agent by ID.")
def delete_agent_tool(account: Optional[str] = None, agentId: Optional[str] = None) -> dict:
    try:
        params = {}
        if account:
            params["accountName"] = account
        if agentId:
            params["agentId"] = agentId
        return delete_agent(params)
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


@server.tool(name="createContactsBulk", description="Create multiple contacts by uploading a CSV file or providing a CSV URL. Requires phonebook_id parameter. Optional country_choice ('file' or 'custom') and country_iso (when country_choice is 'custom'). Note: This API has a rate limit of 1 call per minute.")
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


@server.tool(name="listPhonebooks", description="List phonebooks with optional pagination.")
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


@server.tool(name="getPhonebook", description="Retrieve a single phonebook by ID.")
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


@server.tool(name="createPhonebook", description="Create a new phonebook. Pass fields as URL-encoded string (e.g., 'name=MyPhonebook&description=Description').")
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


@server.tool(name="updatePhonebook", description="Update a phonebook. Pass fields as URL-encoded string (e.g., 'name=NewName&description=NewDesc').")
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


@server.tool(name="deletePhonebook", description="Delete a phonebook by ID.")
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


@server.tool(name="addContactsToPhonebook", description="Add (upsert) contacts into a phonebook.")
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

@server.tool(name="removeContactFromPhonebook", description="Remove a contact from a phonebook.")
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


@server.tool(name="getPhonebookCount", description="Get total contacts in a phonebook.")
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


@server.tool(name="getPhonebookContacts", description="Get contacts in a phonebook with pagination.")
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


@server.tool(name="addTagToContact", description="Add tags to a contact by specifying tag names.")
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


@server.tool(name="updateContactCustomField", description="Update a custom field value for a contact.")
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


@server.tool(name="updateCallCenterCampaign", description="Update a call center campaign's status. Valid values: 'pause', 'resume', 'stop', 'restart'.")
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


@server.tool(name="deleteCallCenterCampaign", description="Delete a call center campaign by ID.")
def delete_call_center_campaign_tool(
    account: Optional[str] = None,
    campaignId: str = None
) -> dict:
    try:
        # Validate required parameters
        if not campaignId:
            return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}

        params = {"campaignId": campaignId}
        if account:
            params["accountName"] = account

        return delete_call_center_campaign(params)
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


# Phone Number Management Tools

@server.tool(name="listRentedNumbers", description="List all rented calling numbers (caller IDs) for the account.")
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


@server.tool(name="updateVoiceBroadcastCampaign", description="Update a voice broadcast campaign's status. Valid values: 'start', 'pause', 'abort', 'end' or 1-4 numerically.")
def update_voice_broadcast_campaign_tool(
    account: Optional[str] = None,
    campaignId: str = None,
    status: str = None # Kept as str to match other update_campaign tools, conversion happens in the module
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

        return update_voice_broadcast(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="deleteVoiceBroadcastCampaign", description="Delete a voice broadcast campaign by ID.")
def delete_voice_broadcast_campaign_tool(
    account: Optional[str] = None,
    campaignId: str = None
) -> dict:
    try:
        # Validate required parameters
        if not campaignId:
            return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}

        params = {"campaignId": campaignId}
        if account:
            params["accountName"] = account # Corrected from params["account"] to params["accountName"]

        return delete_voice_broadcast(params)
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
        # Validate required parameters
        if not campaignId:
            return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}

        params = {"campaignId": campaignId}
        if account:
            params["accountName"] = account # Corrected from params["account"] to params["accountName"]

        return delete_sms_campaign(params)
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


@server.tool(name="updateP2pCampaign", description="Update a P2P campaign's status. Valid values: 'start', 'pause', 'abort', 'end' or 1-4 numerically.")
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


@server.tool(name="deleteP2pCampaign", description="Delete a P2P campaign by ID.")
def delete_p2p_campaign_tool(
    account: Optional[str] = None,
    campaignId: str = None
) -> dict:
    try:
        # Validate required parameters
        if not campaignId:
            return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}

        params = {"campaignId": campaignId}
        if account:
            params["account"] = account

        return delete_p2p_campaign(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}



@server.tool(name="getP2pCampaignAgents", description="Get agents for a P2P campaign.")
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


@server.tool(name="getP2pSurveys", description="Get surveys for a P2P campaign.")
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


# SMS Broadcast Management Tools

@server.tool(name="listSmsBroadcasts", description="List all SMS broadcast campaigns with optional pagination.")
def list_sms_broadcasts_tool(
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

        return list_sms_broadcasts(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="updateSmsBroadcast", description="Update an SMS broadcast campaign's status. Valid values: 'start', 'pause', 'abort', 'end' or 1-4 numerically.")
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

@server.tool(name="createP2PCampaign", description="Create a new P2P campaign with a complex script structure.")
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

        return create_p2p_campaign(params)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

@server.tool(name="deleteSmsBroadcast", description="Delete an SMS broadcast campaign by ID.")
def delete_sms_broadcast_tool(
    account: Optional[str] = None,
    campaignId: str = None
) -> dict:
    try:
        # Validate required parameters
        if not campaignId:
            return {"isError": True, "content": [{"type": "text", "text": "'campaignId' is required."}]}

        params = {"campaignId": campaignId}
        if account:
            params["accountName"] = account

        return delete_sms_broadcast(params)
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

@server.tool(name="createDncContact", description="Create a new DNC contact with the specified phone number.")
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
        return create_dnc_contact(account=account, dnc=dnc, phone_number=phone_number, category=category)
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
        return list_dnc_contacts(account=account, page=page, pageSize=pageSize, allPages=allPages)
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
        return update_dnc_contact(account=account, contactId=contactId, dnc=dnc, phone_number=phone_number)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="deleteDncContact", description="Delete a DNC contact by ID.")
def delete_dnc_contact_tool(
    account: Optional[str] = None,
    contactId: str = None # DNC Contact ID
) -> dict:
    try:
        # Parameters are passed directly to the imported function
        return delete_dnc_contact(account=account, contactId=contactId)
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
        return create_dnc_list(account=account, name=name)
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
        return list_dnc_lists(account=account, page=page, pageSize=pageSize, allPages=allPages)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="updateDncList", description="Update an existing DNC list by ID.")
def update_dnc_list_tool(
    account: Optional[str] = None,
    listId: str = None, # DNC List ID
    name: str = None
) -> dict:
    try:
        # Parameters are passed directly to the imported function
        return update_dnc_list(account=account, listId=listId, name=name)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="deleteDncList", description="Delete a DNC list by ID.")
def delete_dnc_list_tool(
    account: Optional[str] = None,
    listId: str = None # DNC List ID
) -> dict:
    try:
        # Parameters are passed directly to the imported function
        return delete_dnc_list(account=account, listId=listId)
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


@server.tool(name="activateAgentsWithPassword", description="Automate activation of agents using their activation URLs and a common password. IMPORTANT: This function must be used with activation data from the CSV downloaded from the CallHub UI export. Never attempt to generate this data manually.")
def activate_agents_with_password_tool(activation_data: List[Dict] = None, password: str = None, account: Optional[str] = None) -> dict:
    """Automate activation of agents by visiting each agent's activation URL and setting a common password.

    This tool uses headless browser automation to visit each agent's activation URL and set
    the provided password, completing the activation process without manual intervention.

    Args:
        activation_data: List of activation data entries, each with at least 'url' field
        password: Password to set for all activating agents (must be at least 8 characters)
                 If not provided, defaults to "CallHub" + current year (e.g., CallHub2025)
        account: Optional account name to use (defaults to 'default')

    Returns:
        Dict with results of activation attempts
    """
    try:
        if not activation_data:
            return {
                "isError": True,
                "content": [{"type": "text", "text": "activation_data is required - must provide a list of agent activation data"}]
            }

        # If no password provided, use the default scheme: CallHub + current year
        if not password:
            current_year = datetime.datetime.now().year
            password = f"CallHub{current_year}"
            sys.stderr.write(f"[callhub] Using default password scheme: {password}\n")

        # Check password length - CallHub requires at least 8 characters
        if len(password) < 8:
            return {
                "isError": True,
                "content": [
                    {"type": "text", "text": f"Password '{password}' is too short. CallHub requires passwords to be at least 8 characters long."},
                    {"type": "text", "text": "Please provide a longer password that meets the minimum requirements."}
                ]
            }

        return activate_agents_with_password(activation_data, password, account)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="processLocalActivationCsv", description="Process a local CSV file containing agent activation URLs. IMPORTANT: When a user uploads a CSV, Claude can only see the filename but cannot read its contents. This tool searches for the file by name in the user's local system (Downloads, Desktop, etc.) and processes the actual local file.")
def process_local_activation_csv_tool(file_path: str) -> dict:
    """
    Process a local CSV file containing agent activation URLs.

    IMPORTANT WORKFLOW:
    1. When a user uploads a CSV file to the conversation, Claude can only see the filename
       but CANNOT access the content of the uploaded file
    2. This tool uses the filename to search for the actual file on the user's local system
       (Downloads folder, Desktop, Documents, etc.)
    3. The actual CSV content is read and processed from the local file system, not from
       the uploaded file

    Args:
        file_path: Name or path of the CSV file containing agent activations

    Returns:
        Dict with the parsed activation data from the LOCAL file (not the uploaded file)
    """
    try:
        return process_local_activation_csv(file_path)
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

@server.tool(name="activateAgentsWithBatchPassword", description="Activate agents in batches with real-time progress updates. Supports large CSV files and provides resumability.")
def activate_agents_with_batch_password_tool(
    account: str,
    password: str,
    activation_data: List[Dict],
    batch_size: int = 10
) -> dict:
    """
    Activate a large number of agents in batches with progress updates and resumability.
    This tool is designed to handle hundreds of agent activations while providing:
    1. Real-time progress updates during processing
    2. Batch processing to avoid overwhelming the server
    3. Resumability if the process is interrupted or the context window is exceeded

    Args:
        account: CallHub account name
        password: Password to set for all agents (must be at least 8 characters)
        activation_data: List of activation data entries
        batch_size: Number of agents to process in each batch

    Returns:
        Dict with activation results and progress information
    """
    try:
        return activate_agents_with_batch_password(
            account=account,
            password=password,
            activation_data=activation_data,
            batch_size=batch_size
        )
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="getActivationStatus", description="Get the current status of an in-progress or completed agent activation job.")
def get_activation_status_tool(account: str = None) -> dict:
    """
    Get the current status of an agent activation job.

    Use this tool to check:
    1. If an activation job is currently in progress
    2. How many agents have been activated so far
    3. When the last update occurred

    This is useful when activation was interrupted and you need to resume,
    or when dealing with a large number of agents being activated.

    Args:
        account: CallHub account name

    Returns:
        Dict with current status information
    """
    try:
        return get_activation_status(account)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="resetActivationState", description="Reset the progress tracking state for agent activation (for troubleshooting or restarting).")
def reset_activation_state_tool(account: str = None) -> dict:
    """
    Reset the progress tracking state for agent activation.

    Use this tool if:
    1. You want to restart an activation process from the beginning
    2. You're having issues with a previous activation job
    3. You want to clear saved state from a completed job

    Args:
        account: CallHub account name

    Returns:
        Dict with reset result
    """
    try:
        return reset_activation_state(account)
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


@server.tool(name="prepareAgentActivation", description="Prepare for agent activation by setting up logs and showing instructions. IMPORTANT: Always call this first before activating agents.")
def prepare_agent_activation_tool(
    account: str,
    password: str,
    activation_data: List[Dict],
    batch_size: int = 10
) -> dict:
    """
    Prepare for agent activation by setting up the log file and showing instructions.
    This MUST be called BEFORE actually activating agents to ensure the user knows
    where to look for progress updates.

    Args:
        account: CallHub account name
        password: Password to set for all agents (must be at least 8 characters)
        activation_data: List of activation data entries
        batch_size: Number of agents to process in each batch

    Returns:
        Dict with log file path and instructions
    """
    try:
        return prepare_agent_activation(
            account=account,
            password=password,
            activation_data=activation_data,
            batch_size=batch_size
        )
    except Exception as e:
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}


# openTerminalWithLogs function removed for security reasons


if __name__ == "__main__":
    server.run()
