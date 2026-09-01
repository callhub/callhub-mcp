# CallHub MCP Extension

Manage your CallHub account from Claude, in natural language — contacts and
contact lists, tags and custom fields, agents and teams, campaigns (call center,
voice broadcast, text broadcast, P2P, relational), DNC lists, phone numbers,
webhooks, and reporting.

This is a local [MCP](https://modelcontextprotocol.io) server packaged as a
Claude Desktop extension (`.mcpb`). It talks to the CallHub REST API using an
API key.

## Install (Claude Desktop)

1. Download `callhub.mcpb` from the
   [latest release](https://github.com/callhub/callhub-mcp/releases).
2. Open **Claude Desktop → Settings → Extensions** and drag the file in
   (or double-click it).
3. When prompted, enter your extension settings. The API Key and API Domain are
   both in your CallHub dashboard under **Settings → Account → API Key**:
   - **API Key** — the key shown there.
   - **API Domain** — the API Domain shown there (region-specific), e.g.
     `https://api-na1.callhub.io`.
   - **Username** *(optional)* — your CallHub login email.
4. Enable the extension. The CallHub tools are now available in your chats.

**Requirements:** Claude Desktop, and Python 3.10+ available on your system.
The current released bundle is built for **macOS (Apple Silicon)**; for other
platforms, build from source (below).

## Usage

Talk to Claude naturally:

- "Create a contact with phone 1234567890, first name John, last name Doe, and
  add them to a new contact list called VIP Customers."
- "Show me all my teams, then create a new agent in the Sales team."
- "List my voice broadcast campaigns and duplicate the one called Fall Drive."
- "Search my contacts for jane@example.com."

### Multiple accounts

The API key you enter in settings is your **`default`** account. To work with
more accounts, ask Claude to configure one by name:

> "Configure a CallHub account called *personal* with API key … and base URL …"

Then refer to it by name — "list the teams in my *personal* account." Requests
with no account named use `default`.

## Tool naming

Tools follow CallHub's product vocabulary (verb + noun), e.g. `createContactList`,
`listCallCenterCampaigns`, `createVoiceBroadcastCampaign`, `createTextBroadcast`,
`addTagsToContact`. A *contact list* is the same thing the API sometimes calls a
*phonebook*.

Older tool names from earlier versions (e.g. `createPhonebook`, `createVbCampaign`,
`createSmsBroadcast`) still work as **hidden aliases**, so existing saved flows
keep functioning; new work should use the canonical names.

## Agent activation

Newly created agents start in a *pending* state and must verify their email
before they appear in `listAgents`. Pending agents are managed through the
activation-export workflow:

1. `exportAgentActivationUrls` (or `getAgentActivationExportUrl`) to obtain the
   export.
2. Download the activation CSV from the CallHub UI.
3. `processAgentActivationCsv` (or `processUploadedActivationCsv`) to read it.

> Note: earlier versions bundled a Selenium/Chrome browser-automation flow that
> set agent passwords automatically. That has been removed to keep the extension
> lightweight and reliable. Distribute the activation URLs to agents, or activate
> them through the CallHub UI.

## Build from source

Building produces a `callhub.mcpb` for the platform you build on (Python and OS
of the build machine), because some dependencies ship compiled wheels.

```bash
git clone https://github.com/callhub/callhub-mcp.git
cd callhub-mcp
./build.sh          # vendors deps into src/lib, validates the manifest, packs callhub.mcpb
```

Requirements: `python3` (3.10+) and the [`mcpb`](https://github.com/anthropics/mcpb)
CLI (invoked via `npx @anthropic-ai/mcpb`, so Node.js is needed at build time).

### Project layout

- `manifest.json` — MCPB extension manifest (server entry, `user_config`).
- `src/server.py` — registers every tool and starts the MCP server (stdio).
- `src/callhub/` — API client, auth, and one module per resource
  (contacts, phonebooks, campaigns, numbers, dnc, teams, …).
- `build.sh` — reproducible bundle build.

## Error handling

Requests retry transient errors with backoff and respect rate limits. Errors
return a structured message describing what went wrong.

## Security

- Your API key is stored by Claude Desktop's extension settings; it is passed to
  the server as an environment variable, not committed to disk in this repo.
- Use an API key scoped to the least privilege you need.

## License

[MIT](LICENSE)
