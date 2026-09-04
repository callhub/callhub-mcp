# CallHub MCP — API Reference

This MCP server exposes the CallHub REST API as a set of tools that any MCP
client (an AI assistant, or any other MCP-compatible caller) can invoke.
Each tool wraps one CallHub HTTP endpoint (occasionally two, chained), and a
few tools are purely local — they manage the server's own account
configuration or parse a locally uploaded file rather than calling the API.

This document is generated directly from the source:

- `src/server.py` — every tool is registered with `@server.tool(name="...")`
  and delegates to a module function.
- `src/callhub/*.py` — each module function calls `client.call(ENDPOINT,
  METHOD, ...)` (or, for a few upload/verification paths, `requests`
  directly) against the endpoint constants defined in `src/callhub/constants.py`.

**Access column key**

- **Public** — the endpoint is part of CallHub's published API
  (developer.callhub.io).
- **Extended** — the endpoint is internal/undocumented; it is not published
  and may change or disappear without notice.
- **Local** — the tool does not call the CallHub API at all (account
  configuration, CSV/file parsing, or a static schema dump).

Tool count: **136** registered tools, plus **39** backward-compatible
aliases (old names that silently resolve to a canonical tool — see below).

---

## Accounts & Utilities

| Tool | Method | Endpoint | Access | Purpose |
|---|---|---|---|---|
| `listAccounts` | — | *(reads local `.env` credentials)* | Local | List configured CallHub account names. |
| `configureAccount` | GET (verify) | `/v1/users/` | Local | Add/update an account in `.env`; verifies credentials with a GET before saving. |
| `deleteAccount` | — | *(edits local `.env`)* | Local | Remove an account configuration. |
| `getApiSchema` | — | *(static in-code schema)* | Local | Return the server's bundled API schema documentation. |
| `getUsers` | GET | `/v1/users/` | Public | List all users in the account. |
| `getCreditUsage` | POST | `/v2/credits_usage/` | Public | Retrieve credit usage details. |
| `shareCredits` | POST | `/enterprise-account/share-credits/` | Extended | Share credits from an enterprise account to a subaccount. |

## Contacts

| Tool | Method | Endpoint | Access | Purpose |
|---|---|---|---|---|
| `listContacts` | GET | `/v1/contacts/` | Public | List contacts with pagination/filtering. |
| `getContact` | GET | `/v1/contacts/{id}/` | Public | Retrieve a single contact. |
| `createContact` | POST | `/v1/contacts/` | Public | Create a contact. |
| `bulkCreateContacts` | POST | `/v1/contacts/bulk_create/` | Public | Bulk-create contacts from a CSV file/URL (rate-limited to 1/min). |
| `updateContact` | POST | `/v1/contacts/` | Public | Update a contact, matched by phone number. |
| `deleteContact` | DELETE | `/v1/contacts/{id}/` | Public | Delete a contact. |
| `getContactFields` | GET | `/v1/contacts/fields/` | Public | List available contact fields. |
| `searchContacts` | GET | `/v1/contacts/` (query) | Public | Search contacts by phone/name/email (rate-limited to 1/sec). |
| `addContactNotes` | POST | `/v2/contact-notes/{contact_id}` | Extended | Append a note to a contact record. |
| `setContactCustomField` | GET then PUT | `/v1/contacts/{id}/` | Public | Set a custom field value on a contact (reads contact, then writes it back). |

## Contact Lists (Phonebooks)

A "contact list" in these tools is the same object the CallHub API calls a
**phonebook**.

| Tool | Method | Endpoint | Access | Purpose |
|---|---|---|---|---|
| `listContactLists` | GET | `/v1/phonebooks/` | Public | List phonebooks. |
| `getContactList` | GET | `/v1/phonebooks/{id}/` | Public | Retrieve a single phonebook. |
| `createContactList` | POST | `/v1/phonebooks/` | Public | Create a phonebook. |
| `updateContactList` | PATCH | `/v1/phonebooks/{id}/` | Public | Update a phonebook. |
| `deleteContactList` | DELETE | `/v1/phonebooks/{id}/` | Public | Delete a phonebook. |
| `addContactsToContactList` | POST | `/v1/phonebooks/{id}/contacts/` | Public | Add/upsert contacts into a phonebook. |
| `removeContactsFromContactList` | DELETE | `/v1/phonebooks/{id}/contacts/` | Public | Remove a contact from a phonebook. |
| `getContactListCount` | GET | `/v1/phonebooks/{id}/numbers_count/` | Public | Get total contacts in a phonebook. |
| `getContactListContacts` | GET | `/v1/phonebooks/{id}/contacts/` | Public | List contacts in a phonebook (paginated). |

## Tags

| Tool | Method | Endpoint | Access | Purpose |
|---|---|---|---|---|
| `listTags` | GET | `/v1/tags/` | Public | List tags. |
| `getTag` | GET | `/v1/tags/{id}/` | Public | Retrieve a single tag. |
| `createTag` | POST | `/v2/tags/` | Public | Create a tag. |
| `updateTag` | PATCH | `/v1/tags/{id}/` | Public | Update a tag. |
| `deleteTag` | DELETE | `/v1/tags/{id}/` | Public | Delete a tag. |
| `addTagsToContact` | GET then PATCH | `/v1/contacts/{id}/`, `/v2/contacts/{contact_id}/taggings/` | Public | Add tags to a contact by name (looks up the contact, then patches its taggings). |
| `removeTagFromContact` | DELETE | `/v1/contacts/{id}/tags/{tag_id}/` | Public | Remove a tag from a contact. |

## Custom Fields

| Tool | Method | Endpoint | Access | Purpose |
|---|---|---|---|---|
| `listCustomFields` | GET | `/v1/custom_fields/` | Public | List custom fields. |
| `getCustomField` | GET | `/v1/custom_fields/{id}/` (or list+filter) | Public | Retrieve a single custom field. |
| `createCustomField` | POST | `/v1/custom_fields/` | Public | Create a custom field (with choices for Multi-choice type). |
| `updateCustomField` | PUT | `/v1/custom_fields/{id}/` | Public | Update a custom field. |
| `deleteCustomField` | DELETE | `/v1/custom_fields/{id}/` | Public | Delete a custom field. |

## Agents & Teams

| Tool | Method | Endpoint | Access | Purpose |
|---|---|---|---|---|
| `listAgents` | GET | `/v1/agents/` | Public | List agents. |
| `getAgent` | GET | `/v1/agents/{id}/` | Public | Get a single agent. |
| `createAgent` | POST | `/v1/agents/` | Public | Create an agent (validates team existence first, locally). |
| `getLiveAgents` | GET | `/v2/campaign/agent/live/` | Extended | List agents currently connected to any campaign. |
| `listTeams` | GET | `/v1/teams/` | Public | List teams. |
| `getTeam` | GET | `/v1/teams/{id}/` | Public | Get a single team. |
| `createTeam` | POST | `/v1/teams/` | Public | Create a team. |
| `updateTeam` | PUT | `/v1/teams/{id}/` | Public | Update a team's name. |
| `deleteTeam` | DELETE | `/v1/teams/{id}/` | Public | Delete a team. |
| `getTeamAgents` | GET | `/v1/teams/{id}/agents/` | Public | List agents on a team. |
| `getTeamAgentDetails` | GET | `/v1/teams/{id}/agents/{agent_id}/` | Public | Get one agent's detail within a team. |
| `addAgentsToTeam` | PUT | `/v1/teams/{id}/agents/` | Public | Add agents to a team. |
| `removeAgentsFromTeam` | DELETE | `/v1/teams/{id}/agents/` | Public | Remove agents from a team. |

## Call Center Campaigns

"Call center campaign" and "power campaign" refer to the same feature;
`/v1/callcenter_campaigns/` is the public, documented resource, while
`/v1/power_campaign/*` is an internal endpoint family used for creation,
duplication, agent assignment, and export.

| Tool | Method | Endpoint | Access | Purpose |
|---|---|---|---|---|
| `listCallCenterCampaigns` | GET | `/v1/callcenter_campaigns/` | Public | List call center campaigns. |
| `getCallCenterCampaign` | GET | `/v1/callcenter_campaigns/{id}/` | Public | Get a single call center campaign. |
| `updateCallCenterCampaignStatus` | PATCH | `/v1/callcenter_campaigns/{id}/` | Public | Pause/resume/stop/restart a campaign. |
| `deleteCallCenterCampaign` | DELETE | `/v1/callcenter_campaigns/{id}/` | Public | Permanently delete a campaign. |
| `createCallCenterCampaign` | POST | `/v1/power_campaign/create/` | Extended | Create a call center campaign with full script structure. |
| `duplicateCallCenterCampaign` | POST | `/v1/power_campaign/duplicate/` | Extended | Duplicate a call center campaign. |
| `addAgentsToCallCenterCampaign` | POST | `/v1/power_campaign/{id}/agents/add/` | Extended | Add agents to a campaign. |
| `exportCallCenterCampaign` | GET | `/v1/power_campaign/{id}/export/` | Extended | Export a call center campaign. |
| `exportCampaignData` | GET | `/v1/campaigns/{id}/export` | Extended | Export generic campaign data in the requested format. |
| `getCampaignStatsAdvanced` | GET | `/v1/campaigns/{id}/stats` | Extended | Get enhanced campaign statistics. |

## Voice Broadcast

| Tool | Method | Endpoint | Access | Purpose |
|---|---|---|---|---|
| `listVoiceBroadcastCampaigns` | GET | `/v1/voice_broadcasts/` | Public | List voice broadcast campaigns. |
| `getVoiceBroadcastCampaign` | GET | `/v1/vb_campaign/{id}/` | Public | Get a voice broadcast campaign. |
| `createVoiceBroadcastCampaign` | POST | `/v1/vb_campaign/` | Public | Create a voice broadcast campaign. |
| `duplicateVoiceBroadcastCampaign` | POST | `/v1/vb_campaign/{id}/duplicate/` | Public | Duplicate a voice broadcast campaign. |
| `deleteVoiceBroadcastCampaign` | DELETE | `/v1/voice_broadcasts/{id}/` | Public | Permanently delete a voice broadcast campaign. |
| `updateVoiceBroadcastCampaign` | PUT | `/v1/voice_broadcasts/{id}/` | Public | Update a voice broadcast campaign. |
| `createVoiceBroadcastTemplate` | POST | `/v1/vb_template/` | Public | Create a voice broadcast template. |
| `listVoiceBroadcastTemplates` | GET | `/v1/vb_template/` | Public | List voice broadcast templates. |

## Text Broadcast (SMS Campaigns / Broadcasts)

"Text broadcast" is CallHub's bulk-SMS campaign feature. The v1
`sms_campaigns` resource is the public API; the v2 `sms_broadcast` family
used for create/get/update/duplicate is internal.

| Tool | Method | Endpoint | Access | Purpose |
|---|---|---|---|---|
| `listTextBroadcasts` | GET | `/v1/sms_campaigns/` | Public | List SMS campaigns. |
| `updateSmsCampaignStatus` | PATCH | `/v1/sms_campaigns/{id}/` | Public | Start/pause/abort/end an SMS campaign. |
| `deleteTextBroadcast` | DELETE | `/v1/sms_campaigns/{id}/` | Public | Permanently delete an SMS/text broadcast campaign. |
| `exportTextBroadcastReport` | GET | `/v1/sms_campaign/sms_report/export/` | Extended | Export an SMS report for a campaign. |
| `createTextBroadcast` | POST | `/v2/sms_broadcast/create/` | Extended | Create an SMS broadcast campaign. |
| `getTextBroadcast` | GET | `/v2/sms_broadcast/{id}/` | Extended | Get details of an SMS broadcast campaign. |
| `updateTextBroadcastStatus` | PATCH | `/v2/sms_broadcast/{id}/` | Extended | Start/pause/abort/end an SMS broadcast. |
| `duplicateTextBroadcast` | POST | `/v2/sms_broadcast/{id}/duplicate/` | Extended | Duplicate an SMS broadcast campaign. |

## P2P (Peer-to-Peer Texting)

The v1 `p2p_campaigns` resource (list/create/duplicate/get) is public; the
v2 "snowflake" and `collective_texting` endpoint families used for status
updates, agent assignment, and surveys are internal.

| Tool | Method | Endpoint | Access | Purpose |
|---|---|---|---|---|
| `listP2pCampaigns` | GET | `/v1/p2p_campaigns/` | Public | List P2P campaigns. |
| `createP2pCampaign` | POST | `/v1/p2p_campaigns/` | Public | Create a P2P campaign with full script structure. |
| `getP2pCampaign` | GET | `/v1/p2p_campaigns/{id}/` | Public | Get a single P2P campaign. |
| `duplicateP2pCampaign` | POST | `/v1/p2p_campaigns/{id}/duplicate/` | Public | Duplicate a P2P campaign. |
| `updateP2pCampaignStatus` | PUT | `/v2/sms_campaign/snowflake/{id}/` | Extended | Start/pause/abort/end a P2P campaign. |
| `listP2pCampaignAgents` | GET | `/v2/collective_texting/{id}/agents/` | Extended | Get agents assigned to a P2P campaign. |
| `addAgentsToP2pCampaign` | POST | `/v2/collective_texting/{id}/agents/add/` | Extended | Add agents to a P2P campaign. |
| `reassignP2pAgents` | POST | `/v2/collective_texting/{id}/agents/reassign/` | Extended | Reassign agents in a P2P campaign. |
| `listP2pSurveys` | GET | `/v2/sms_campaign/snowflake/survey-list/[{id}/]` | Extended | Get surveys for a P2P campaign. |

## Relational Organizing

All relational-organizing endpoints live under the internal
`/email/v_1/relational-campaign/` path family.

| Tool | Method | Endpoint | Access | Purpose |
|---|---|---|---|---|
| `createRelationalCampaign` | POST | `/email/v_1/relational-campaign/create/` | Extended | Create a relational organizing campaign. |
| `getRelationalCampaign` | GET | `/email/v_1/relational-campaign/{id}/` | Extended | Get a relational organizing campaign. |
| `updateRelationalCampaign` | PUT | `/email/v_1/relational-campaign/{id}/edit/` | Extended | Update a relational organizing campaign. |
| `updateRelationalCampaignStatus` | POST | `/email/v_1/relational-campaign/{id}/update-status/` | Extended | Update campaign status. |
| `duplicateRelationalCampaign` | POST | `/email/v_1/relational-campaign/{id}/duplicate/` | Extended | Duplicate a relational organizing campaign. |
| `assignRelationalCampaignAgents` | PUT | `/email/v_1/relational-campaign/agents/{id}/` | Extended | Assign or remove agents on a relational organizing campaign. |

## DNC & Suppression

| Tool | Method | Endpoint | Access | Purpose |
|---|---|---|---|---|
| `addToDnc` | POST | `/v1/dnc_contacts/` | Public | Add a phone number to the DNC list. |
| `listDncContacts` | GET | `/v1/dnc_contacts/` | Public | List DNC contacts. |
| `updateDncContact` | PUT | `/v1/dnc_contacts/{id}/` | Public | Update a DNC contact. |
| `removeFromDnc` | DELETE | `/v1/dnc_contacts/{id}/` | Public | Remove a DNC contact. |
| `createDncList` | POST | `/v1/dnc_lists/` | Public | Create a DNC list. |
| `listDncLists` | GET | `/v1/dnc_lists/` | Public | List DNC lists. |
| `updateDncList` | PUT | `/v1/dnc_lists/{id}/` | Public | Update a DNC list. |
| `deleteDncList` | DELETE | `/v1/dnc_lists/{id}/` | Public | Delete a DNC list. |
| `addToSuppressionList` | POST | `/suppression-lists/{id}/contacts/` | Extended | Bulk-add numbers to a Call Center suppression list (max 10/call). |

## Numbers

The base `/v1/numbers/` actions (rent, list rented, list validated) are
public; area-code lookup, rent rates, auto-unrent, revalidation, and the
combined/SMS-specific number listings are internal.

| Tool | Method | Endpoint | Access | Purpose |
|---|---|---|---|---|
| `listRentedCallingNumbers` | GET | `/v1/numbers/rented_calling_numbers/` | Public | List rented caller-ID numbers. |
| `listValidatedNumbers` | GET | `/v1/numbers/validated_numbers/` | Public | List validated personal numbers usable as caller IDs. |
| `rentNumber` | POST | `/v1/numbers/rent/` | Public | Rent a new phone number. |
| `getAreaCodes` | GET | `/v2/get_area_code/` | Extended | Get available area codes for a country. |
| `getNumberRentRates` | GET | `/v1/number_rent_rates/` | Extended | Get number rent rates for a country. |
| `getAutoUnrentSettings` | GET | `/v2/auto_unrent/settings/` | Extended | Get auto-unrent settings. |
| `updateAutoUnrentSettings` | POST | `/v2/auto_unrent/settings/` | Extended | Update auto-unrent settings. |
| `revalidateNumber` | POST | `/v1/revalidate_numbers/` | Extended | Trigger revalidation of phone numbers. |
| `listNumbersNeedingRevalidation` | GET | `/v1/revalidate_numbers/` | Extended | List numbers that need revalidation. |
| `listSmsOnlyNumbers` | GET | `/v2/sms_number/show_rented_number/` | Extended | List SMS-only rented numbers. |
| `listCombinedSmsNumbers` | GET | `/v2/validated_and_rented_numbers/` | Extended | List combined validated + rented SMS numbers. |
| `autoRentSmsNumber` | POST | `/v2/sms_number/sms_rent_number/` | Extended | Auto-rent an SMS number. |

## Media

| Tool | Method | Endpoint | Access | Purpose |
|---|---|---|---|---|
| `listMedia` | GET | `/v2/media/` | Extended | List uploaded media files (audio/image/video), with filtering. |
| `uploadMediaFile` | POST | `/v1/media/upload/` | Extended | Upload a local media file to the CallHub media library. |

## Webhooks

| Tool | Method | Endpoint | Access | Purpose |
|---|---|---|---|---|
| `listWebhooks` | GET | `/v1/webhooks/` | Public | List webhooks. |
| `getWebhook` | GET | `/v1/webhooks/` (client-side filter by ID) | Public | Get a single webhook — the API has no single-resource endpoint, so this lists all and filters. |
| `createWebhook` | POST | `/v1/webhooks/` | Public | Create a webhook (`vb.transfer`, `sb.reply`, `cc.notes`, or `agent.activation`). |
| `deleteWebhook` | DELETE | `/v1/webhooks/{id}/` | Public | Delete a webhook. |

## Survey Templates & Questions

| Tool | Method | Endpoint | Access | Purpose |
|---|---|---|---|---|
| `listSurveyTemplates` | GET | `/v1/templates/` | Public | List survey templates. |
| `getSurveyTemplate` | GET | `/v1/templates/{id}/` | Public | Get a single survey template. |
| `createSurveyTemplate` | POST | `/v1/templates/` | Public | Create a survey template with questions. |
| `updateSurveyTemplate` | PATCH | `/v1/templates/{id}/` | Public | Update a survey template. |
| `deleteSurveyTemplate` | DELETE | `/v1/templates/{id}/` | Public | Delete a survey template. |
| `listQuestions` | GET | `/v1/questions/` | Public | List questions (optionally filtered by type). |
| `getQuestion` | GET | `/v1/questions/{id}/` | Public | Get a single question. |
| `listIntegrationFields` | GET | `/v1/integration_fields/` | Public | List integration fields. |
| `getIntegrationField` | GET | `/v1/integration_fields/{id}/` | Public | Get a single integration field. |

## Reporting & Exports

| Tool | Method | Endpoint | Access | Purpose |
|---|---|---|---|---|
| `getExportJobStatus` | GET | `/v1/export_data/export_{job_id}/` | Extended | Poll an export job started by one of the export tools. |
| `getShortenedUrlStats` | GET | `/v2/shortened-urls/{short_code}/` | Extended | Get stats/details for a shortened URL. |
| `listShortenedUrls` | GET | `/v2/shortened-urls/` | Extended | List shortened URLs. |

## Agent Activation

These tools help a user manually export/upload pending-agent-activation
data; they build a browser URL and parse locally supplied CSV content — no
tool here calls the CallHub API directly.

| Tool | Method | Endpoint | Access | Purpose |
|---|---|---|---|---|
| `exportAgentActivationUrls` | — | *(constructs a browser URL from account config)* | Local | Give the user a link to the Agents page's export-pending-activations flow. |
| `getAgentActivationExportUrl` | — | *(constructs a browser URL from account config)* | Local | Same as above — a direct export URL for manual download. |
| `processAgentActivationCsv` | — | *(parses provided CSV text)* | Local | Parse activation-URL data from CSV content already in the conversation. |
| `processUploadedActivationCsv` | — | *(parses a local uploaded file)* | Local | Parse an uploaded activation CSV file from disk. |
| `processUploadedCsv` | — | *(parses a local uploaded file)* | Local | Generic CSV-upload processing helper (file discovery + parsing). |

---

## Backward-compatible aliases

These 39 old tool names still work — they resolve transparently (via
`TOOL_ALIASES` in `src/server.py`) to a canonical tool listed above, but are
intentionally hidden from the tool catalogue so new integrations don't pick
them up.

| Old name | Canonical tool |
|---|---|
| `createPhonebook` | `createContactList` |
| `getPhonebook` | `getContactList` |
| `updatePhonebook` | `updateContactList` |
| `deletePhonebook` | `deleteContactList` |
| `listPhonebooks` | `listContactLists` |
| `addContactsToPhonebook` | `addContactsToContactList` |
| `removeContactFromPhonebook` | `removeContactsFromContactList` |
| `getPhonebookContacts` | `getContactListContacts` |
| `getPhonebookCount` | `getContactListCount` |
| `createVbCampaign` | `createVoiceBroadcastCampaign` |
| `getVbCampaign` | `getVoiceBroadcastCampaign` |
| `duplicateVbCampaign` | `duplicateVoiceBroadcastCampaign` |
| `createVbCampaignTemplate` | `createVoiceBroadcastTemplate` |
| `createSmsBroadcast` | `createTextBroadcast` |
| `getSmsBroadcast` | `getTextBroadcast` |
| `duplicateSmsBroadcast` | `duplicateTextBroadcast` |
| `updateSmsBroadcast` | `updateTextBroadcastStatus` |
| `listSmsCampaigns` | `listTextBroadcasts` |
| `exportSmsReport` | `exportTextBroadcastReport` |
| `updateSmsCampaign` | `updateSmsCampaignStatus` |
| `addAgentsToPowerCampaign` | `addAgentsToCallCenterCampaign` |
| `duplicatePowerCampaign` | `duplicateCallCenterCampaign` |
| `exportPowerCampaign` | `exportCallCenterCampaign` |
| `updateCallCenterCampaign` | `updateCallCenterCampaignStatus` |
| `createP2PCampaign` | `createP2pCampaign` |
| `getP2pCampaignAgents` | `listP2pCampaignAgents` |
| `updateP2pCampaign` | `updateP2pCampaignStatus` |
| `getP2pSurveys` | `listP2pSurveys` |
| `assignAgentsToRelationalCampaign` | `assignRelationalCampaignAgents` |
| `createContactsBulk` | `bulkCreateContacts` |
| `addTagToContact` | `addTagsToContact` |
| `updateContactCustomField` | `setContactCustomField` |
| `getMediaFiles` | `listMedia` |
| `listRentedNumbers` | `listRentedCallingNumbers` |
| `revalidateNumbers` | `revalidateNumber` |
| `getShortenedUrl` | `getShortenedUrlStats` |
| `createDncContact` | `addToDnc` |
| `deleteDncContact` | `removeFromDnc` |
| `fetchAgents` | `listAgents` |

## Notes

- **Extended** endpoints are internal to CallHub — they are not published
  on developer.callhub.io, are not subject to any API stability guarantee,
  and may change or be removed without notice. Prefer the **Public**
  equivalent where one exists for the same resource.
- A **contact list** in this server's tool names is the same object the
  CallHub API itself calls a **phonebook** — the two terms are used
  interchangeably in tool descriptions and in the API responses.
