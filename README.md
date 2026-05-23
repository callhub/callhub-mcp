# CallHub MCP Server

A Model Context Protocol (MCP) server that exposes the CallHub API as Claude tools. Manage contacts, phonebooks, agents, teams, campaigns, and more through natural language.

## Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Tool Reference](#tool-reference)
- [API Key Setup](#api-key-setup)
- [Rate Limits](#rate-limits)
- [Agent Activation Guide](#agent-activation-guide)
- [Security](#security)
- [Contributing](#contributing)
- [License](#license)

---

## Quick Start

1. Clone the repo and install dependencies:
   ```bash
   git clone https://github.com/callhub/callhub-mcp.git
   cd callhub-mcp
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Add to your Claude Desktop `claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "callhub-mcp": {
         "command": "/path/to/callhub-mcp/.venv/bin/python",
         "args": ["/path/to/callhub-mcp/src/server.py"]
       }
     }
   }
   ```

3. Restart Claude Desktop. Ask Claude to configure your account:
   ```
   Set up my CallHub account: username user@example.com, API key abc123, base URL https://api-na1.callhub.io
   ```

---

## Installation

### Prerequisites

- Python 3.10+
- An active CallHub account with API access
- Claude Desktop (or any MCP-compatible client)

### Clone and Install

```bash
git clone https://github.com/callhub/callhub-mcp.git
cd callhub-mcp
python -m venv .venv
source .venv/bin/activate        # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Claude Desktop Configuration

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "callhub-mcp": {
      "command": "/absolute/path/to/callhub-mcp/.venv/bin/python",
      "args": [
        "/absolute/path/to/callhub-mcp/src/server.py"
      ]
    }
  }
}
```

Replace `/absolute/path/to/callhub-mcp` with the actual directory where you cloned the repository. Claude manages the server process automatically.

---

## Configuration

Credentials are stored in a `.env` file in the project root. The server supports multiple named accounts.

```dotenv
# Default account
CALLHUB_DEFAULT_USERNAME=user@example.com
CALLHUB_DEFAULT_API_KEY=your_api_key_here
CALLHUB_DEFAULT_BASE_URL=https://api-na1.callhub.io

# Additional accounts (any descriptive name)
CALLHUB_PERSONAL_USERNAME=personal@example.com
CALLHUB_PERSONAL_API_KEY=personal_api_key
CALLHUB_PERSONAL_BASE_URL=https://api-na1.callhub.io

CALLHUB_CLIENT_USERNAME=client@example.com
CALLHUB_CLIENT_API_KEY=client_api_key
CALLHUB_CLIENT_BASE_URL=https://api-na1.callhub.io
```

Account names are derived from the variable prefix (e.g. `CALLHUB_PERSONAL_*` creates an account named `personal`). Names may use letters, numbers, and underscores.

To target a specific account, mention it naturally:
```
List the teams in my personal account.
```

If no account is specified, the `default` account is used.

You can also manage accounts through Claude at runtime using `configureAccount`, `listAccounts`, and `deleteAccount`.

---

## Tool Reference

> **Note on Extended API tools:** Tools marked with **†** use endpoints that are functional but are not documented in the public API reference at [developer.callhub.io](https://developer.callhub.io). All other tools use the documented public API.

---

### Account Management

Local tools — no API call required.

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `listAccounts` | List all configured CallHub accounts | — |
| `configureAccount` | Add or update an account configuration | `accountName`, `username`, `apiKey`, `baseUrl` |
| `deleteAccount` | Remove an account from `.env` | `accountName` |

---

### Agents

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `listAgents` | List all agents; optional pending filter | `page`, `include_pending`, `account` |
| `fetchAgents` | Retrieve agents via direct API fetch | `account` |
| `getAgent` | Get a specific agent by ID | `agent_id`, `account` |
| `createAgent` | Create a new agent (starts in pending state) | `email`, `username`, `team` (name), `account` |
| `getLiveAgents` † | List all agents currently connected to a campaign | `account` |
| `getAgentKey` | Get an auth token for an agent | `username`, `password`, `account` |
| `getAgentStatus` | Get current status of account agents | `account` |

---

### Teams

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `listTeams` | List all teams | `account` |
| `getTeam` | Get a team by ID | `team_id`, `account` |
| `createTeam` | Create a new team | `name`, `account` |
| `updateTeam` | Rename a team | `team_id`, `name`, `account` |
| `deleteTeam` | Delete a team (agents become unassigned) | `team_id`, `account` |
| `getTeamAgents` | List agents assigned to a team | `team_id`, `account` |
| `getTeamAgentDetails` | Get details for a specific agent in a team | `team_id`, `agent_id`, `account` |
| `addAgentsToTeam` | Add one or more agents to a team | `team_id`, `agent_ids`, `account` |
| `removeAgentsFromTeam` | Remove one or more agents from a team | `team_id`, `agent_ids`, `account` |

---

### Contacts

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `listContacts` | List contacts with pagination or filtering | `page`, `search`, `account` |
| `getContact` | Get a contact by ID | `contact_id`, `account` |
| `createContact` | Create a new contact | `contact` (phone), `first_name`, `last_name`, `country_code`, `account` |
| `createContactsBulk` | Bulk-create contacts from CSV file or URL (1/min rate limit) | `phonebook_id`, `csv_url` or `file_path`, `country_choice`, `country_iso`, `account` |
| `updateContact` | Update a contact by phone number | `contact` (phone), fields as URL-encoded string, `account` |
| `deleteContact` | Delete a contact by ID | `contact_id`, `account` |
| `getContactFields` | List all available contact fields | `account` |
| `updateContactCustomField` | Set a custom field value on a contact | `contact_id`, `field_id`, `value`, `account` |

---

### Phonebooks

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `listPhonebooks` | List phonebooks with optional pagination | `page`, `account` |
| `getPhonebook` | Get a phonebook by ID | `phonebook_id`, `account` |
| `createPhonebook` | Create a new phonebook | `name`, `description`, `account` |
| `updatePhonebook` | Update a phonebook name or description | `phonebook_id`, fields, `account` |
| `deletePhonebook` | Delete a phonebook | `phonebook_id`, `account` |
| `addContactsToPhonebook` | Upsert contacts into a phonebook | `phonebook_id`, `contacts`, `account` |
| `removeContactFromPhonebook` | Remove a contact from a phonebook | `phonebook_id`, `contact_id`, `account` |
| `getPhonebookCount` | Get the total number of contacts in a phonebook | `phonebook_id`, `account` |
| `getPhonebookContacts` | List contacts in a phonebook with pagination | `phonebook_id`, `page`, `account` |

---

### Tags

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `listTags` | List all tags | `page`, `account` |
| `getTag` | Get a tag by ID | `tag_id`, `account` |
| `createTag` | Create a new tag | `name`, `account` |
| `updateTag` | Update an existing tag | `tag_id`, `name`, `account` |
| `deleteTag` | Delete a tag by ID | `tag_id`, `account` |
| `addTagToContact` | Add tags to a contact by tag name | `contact_id`, `tag_names`, `account` |
| `removeTagFromContact` | Remove a tag from a contact | `contact_id`, `tag_id`, `account` |

---

### Custom Fields

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `listCustomFields` | List all custom fields | `page`, `account` |
| `getCustomField` | Get a custom field by ID | `field_id`, `account` |
| `createCustomField` | Create a custom field | `name`, `type`, `choices` (for Multi-choice), `account` |
| `updateCustomField` | Update a custom field | `field_id`, `name`, `account` |
| `deleteCustomField` | Delete a custom field | `field_id`, `account` |

---

### Webhooks

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `listWebhooks` | List all webhooks | `page`, `account` |
| `getWebhook` | Get a webhook by ID | `webhook_id`, `account` |
| `createWebhook` | Create a webhook | `url`, `event` (`vb.transfer`, `sb.reply`, `cc.notes`, `agent.activation`), `account` |
| `deleteWebhook` | Delete a webhook | `webhook_id`, `account` |

---

### Call Center / Power Campaigns

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `listCallCenterCampaigns` | List all call center campaigns | `page`, `account` |
| `updateCallCenterCampaign` | Change campaign status | `campaign_id`, `status` (`pause`, `resume`, `stop`, `restart`), `name`, `account` |
| `deleteCallCenterCampaign` | Delete a call center campaign | `campaign_id`, `account` |
| `createCallCenterCampaign` † | Create a new call center campaign with script | `name`, `script`, `phonebook_id`, `account` |
| `duplicatePowerCampaign` † | Duplicate a power campaign | `campaign_id`, `account` |
| `addAgentsToPowerCampaign` † | Add agents to a power campaign | `campaign_id`, `agent_ids`, `account` |
| `exportPowerCampaign` † | Export a power campaign | `campaign_id`, `account` |
| `exportCampaignData` † | Export campaign data in a specified format | `campaign_id`, `format`, `account` |
| `getCampaignStatsAdvanced` † | Get enhanced campaign statistics | `campaign_id`, `account` |
| `getExportJobResult` | Retrieve the result of a previously initiated export | `job_id`, `account` |

---

### Voice Broadcast Campaigns

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `listVoiceBroadcastCampaigns` | List all voice broadcast campaigns | `page`, `account` |
| `getVbCampaign` | Get a voice broadcast campaign by ID | `campaign_id`, `account` |
| `createVbCampaign` | Create a new voice broadcast campaign | `name`, `phonebook_id`, `audio_file_id`, `account` |
| `updateVoiceBroadcastCampaign` | Update name, status, or frequency | `campaign_id`, `name`, `status`, `frequency`, `account` |
| `deleteVoiceBroadcastCampaign` | Delete a voice broadcast campaign | `campaign_id`, `account` |
| `duplicateVbCampaign` | Duplicate a voice broadcast campaign | `campaign_id`, `account` |
| `createVbCampaignTemplate` | Create a voice broadcast campaign template | `name`, `audio_file_id`, `account` |

---

### SMS Campaigns

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `listSmsCampaigns` | List all SMS campaigns | `page`, `account` |
| `updateSmsCampaign` | Update an SMS campaign status | `campaign_id`, `status` (`start`, `pause`, `abort`, `end`), `account` |
| `deleteSmsCampaign` | Delete an SMS campaign | `campaign_id`, `account` |

---

### SMS Broadcasts

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `createSmsBroadcast` | Create a new SMS broadcast campaign | `name`, `phonebook_id`, `message`, `account` |
| `getSmsBroadcast` † | Get details of an SMS broadcast campaign | `campaign_id`, `account` |
| `updateSmsBroadcast` † | Update an SMS broadcast status | `campaign_id`, `status` (`start`, `pause`, `abort`, `end`), `account` |
| `duplicateSmsBroadcast` | Duplicate an SMS broadcast campaign | `campaign_id`, `account` |
| `exportSmsReport` † | Export an SMS report for a campaign | `campaign_id`, `account` |

---

### P2P / Collective Texting Campaigns

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `listP2pCampaigns` | List all P2P campaigns | `page`, `account` |
| `createP2PCampaign` † | Create a new P2P campaign with script | `name`, `script`, `phonebook_id`, `account` |
| `updateP2pCampaign` † | Update a P2P campaign status | `campaign_id`, `status` (`start`, `pause`, `abort`, `end`), `account` |
| `duplicateP2pCampaign` † | Duplicate a P2P campaign | `campaign_id`, `account` |
| `getP2pCampaignAgents` † | List agents assigned to a P2P campaign | `campaign_id`, `account` |
| `addAgentsToP2pCampaign` † | Add agents to a P2P campaign | `campaign_id`, `agent_ids`, `account` |
| `reassignP2pAgents` † | Reassign agents within a P2P campaign | `campaign_id`, `account` |
| `getP2pSurveys` † | Get surveys for a P2P campaign | `campaign_id`, `account` |
| `getCollectiveTextingQuestions` | Get questions for a Collective Texting campaign | `campaign_id`, `account` |
| `getCollectiveTextingSavedReplies` | Get saved replies for a Collective Texting campaign | `campaign_id`, `account` |

---

### Relational Organizing Campaigns

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `createRelationalCampaign` | Create a new relational organizing campaign | `name`, `phonebook_id`, `account` |
| `getRelationalCampaign` | Get a relational organizing campaign by ID | `campaign_id`, `account` |
| `updateRelationalCampaign` | Update a relational organizing campaign | `campaign_id`, fields, `account` |
| `updateRelationalCampaignStatus` † | Update the status of a relational campaign | `campaign_id`, `status`, `account` |
| `duplicateRelationalCampaign` † | Duplicate a relational organizing campaign | `campaign_id`, `account` |
| `assignAgentsToRelationalCampaign` † | Assign or remove agents on a relational campaign | `campaign_id`, `agent_ids_to_assign`, `agent_ids_to_remove`, `account` |

---

### DNC (Do Not Contact)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `listDncContacts` | List DNC contacts | `page`, `account` |
| `createDncContact` | Add a phone number to the DNC list | `phone_number`, `account` |
| `updateDncContact` | Update a DNC contact by ID | `dnc_id`, fields, `account` |
| `deleteDncContact` | Remove a DNC contact by ID | `dnc_id`, `account` |
| `listDncLists` | List all DNC lists | `page`, `account` |
| `createDncList` | Create a new DNC list | `name`, `account` |
| `updateDncList` | Update a DNC list | `dnc_list_id`, `name`, `account` |
| `deleteDncList` | Delete a DNC list | `dnc_list_id`, `account` |

---

### Suppression Lists

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `addContactsToSuppressionList` | Add contacts to a suppression list (returns 207 Multi-Status) | `contacts` (list of `{phone_number, mobile_number}`), `account` |

---

### Phone Numbers

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `listRentedNumbers` | List all rented calling numbers (caller IDs) | `page`, `account` |
| `listValidatedNumbers` | List validated personal phone numbers usable as caller IDs | `page`, `account` |
| `rentNumber` | Rent a new phone number | `country_iso` (e.g. `US`), `phone_number_prefix`, `account` |
| `getAreaCodes` † | Get area codes for a country | `country_iso`, `account` |
| `getNumberRentRates` † | Get phone number rent rates by country | `country_iso`, `account` |
| `getAutoUnrentSettings` † | Get auto-unrent settings | `account` |
| `updateAutoUnrentSettings` † | Update auto-unrent settings | settings fields, `account` |
| `revalidateNumbers` † | Revalidate phone numbers | `number_ids`, `account` |
| `listSmsOnlyNumbers` † | List SMS-only rented numbers | `account` |
| `listCombinedSmsNumbers` † | List combined validated and rented SMS numbers | `account` |
| `autoRentSmsNumber` † | Auto-rent an SMS number | `country_iso`, `account` |

---

### Media

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `uploadMediaFile` | Upload a media file from a local path (.mp3, .wav, .ogg, .mp4, .mov, .jpg, .png, .gif) | `file_path`, `account` |
| `getMediaFiles` † | List uploaded media files with pagination | `page`, `account` |

---

### Users and Credits

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `getUsers` | List all users in the account | `account` |
| `getUserDetails` | Get details of the currently authenticated user | `account` |
| `getCreditUsage` | Get credit usage details | `account` |
| `shareCredits` | Share credits from an enterprise account to a subaccount | `subaccount_id`, `credits`, `account` |

---

### Survey Templates

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `listSurveyTemplates` | List all survey templates | `account` |
| `getSurveyTemplate` | Get a survey template by ID | `template_id`, `account` |
| `createSurveyTemplate` | Create a survey template with questions | `name`, `questions` (list of `{type, question, question_name, is_initial_message}`), `account` |
| `updateSurveyTemplate` | Update an existing survey template | `template_id`, fields, `account` |
| `deleteSurveyTemplate` | Delete a survey template | `template_id`, `account` |

---

### Questions

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `listQuestions` | List all questions with optional type filter | `type` (`PDI_QUESTION`, `VAN_QUESTION`), `account` |
| `getQuestion` | Get a question by ID | `question_id`, `account` |

---

### Integration Fields

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `listIntegrationFields` | List all integration fields | `account` |
| `getIntegrationField` | Get an integration field by ID | `field_id`, `account` |

---

### URLs

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `getShortenedUrl` † | Get details of a shortened URL by short code | `short_code`, `account` |
| `listShortenedUrls` † | List all shortened URLs | `page`, `account` |

---

### API Schema

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `getApiSchema` † | Retrieve the full API schema documentation | `account` |

---

### Agent Activation (Browser Automation)

These tools handle the activation workflow for newly created agents who must verify their email. Pending agents are not accessible via direct API — this workflow uses browser automation and CSV processing.

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `prepareAgentActivation` | Set up logs and display instructions — call this first | `account` |
| `exportAgentActivationUrls` | Export pending agent activation URLs (requires browser session) | `account` |
| `getAgentActivationExportUrl` | Get a direct URL for manual CSV download from the CallHub UI | `account` |
| `processAgentActivationCsv` | Process a downloaded activation CSV file | `csv_content` or `file_path`, `account` |
| `processLocalActivationCsv` | Search for and process a local CSV by filename | `filename`, `account` |
| `processUploadedActivationCsv` | Locate and process a CSV from a user file upload | `filename`, `account` |
| `processUploadedCsv` | Generic tool to locate and process any uploaded CSV | `filename`, `account` |
| `activateAgentsWithPassword` | Activate agents using their activation URLs and a shared password | `activation_data`, `password`, `account` |
| `activateAgentsWithBatchPassword` | Batch-activate agents with progress tracking (supports large CSVs) | `csv_data`, `password`, `batch_size`, `account` |
| `getActivationStatus` | Check the status of an in-progress or completed activation job | `job_id`, `account` |
| `resetActivationState` | Reset activation progress tracking (for troubleshooting) | `account` |

---

> **†** Extended API — these tools are functional but the underlying endpoints are not documented at [developer.callhub.io](https://developer.callhub.io).

---

## API Key Setup

1. Log in to your CallHub account at `https://app.callhub.io`.
2. Navigate to **Settings > API**.
3. Copy your API key.
4. Note your base URL — typically `https://api-na1.callhub.io` for North America accounts.
5. Use `configureAccount` to store credentials, or add them directly to `.env`.

The API key requires appropriate permissions for the operations you intend to perform. Account owners have full access; agent-level keys are restricted.

---

## Rate Limits

The server includes automatic retry with exponential backoff for rate-limited responses (HTTP 429). For most operations this is transparent.

The `createContactsBulk` endpoint has a hard limit of **1 call per minute** enforced by CallHub. Space bulk uploads accordingly.

---

## Agent Activation Guide

When agents are created via the API, they start in a `pending` state and must verify their email before becoming active. These pending agents are:

- Not visible through `listAgents` (even with `include_pending=true`)
- Not manageable through direct API calls
- Only accessible through the activation export workflow

Activation sequence:

1. Call `prepareAgentActivation` to set up the workflow.
2. Call `exportAgentActivationUrls` or `getAgentActivationExportUrl` to obtain the export URL.
3. Download the activation CSV from the URL shown in the CallHub UI.
4. Process the CSV using `processAgentActivationCsv`, `processLocalActivationCsv`, or `processUploadedActivationCsv`.
5. Activate agents using `activateAgentsWithPassword` (single batch) or `activateAgentsWithBatchPassword` (large files with progress tracking).
6. Monitor progress with `getActivationStatus`.

Do not create test agents to verify activation status — always use this workflow.

---

## Security

- Store credentials in `.env` — never commit this file to version control.
- Add `.env` to your `.gitignore`.
- Use the principle of least privilege when creating API keys.
- Be cautious with browser automation features (`exportAgentActivationUrls`, `activateAgentsWithPassword`) — they require a live browser session with your CallHub credentials.

---

## Contributing

Contributions are welcome. Please submit a pull request with a clear description of the change.

---

## License

[MIT License](LICENSE)
