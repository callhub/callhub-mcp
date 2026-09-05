# CallHub MCP Server

An [MCP](https://modelcontextprotocol.io) server that exposes the CallHub API as
tools for any MCP-compatible AI assistant — manage contacts and contact lists,
tags and custom fields, agents and teams, campaigns (call center, voice
broadcast, text broadcast, P2P, relational organizing), DNC and suppression
lists, phone numbers, webhooks, media, and reporting, all through natural
language.

It runs locally over stdio and authenticates to CallHub with an API key. It
works with any MCP client — Claude Desktop, Cursor, Windsurf, Cline, Continue,
OpenAI Codex, Gemini CLI, and others — and ships as a one-click `.mcpb` bundle
for Claude Desktop.

[CallHub](https://callhub.io) is a calling and texting platform for campaigns,
nonprofits, and organizing teams — voice broadcasts, call center / phone
banking, P2P and bulk texting, and contact management. This server wraps the
CallHub REST API as MCP tools — mostly public endpoints, plus some
internal/extended ones (each is flagged in the tool reference).

**Links**
- [callhub.io](https://callhub.io) — product home
- [developer.callhub.io](https://developer.callhub.io/) — official CallHub REST API reference
- [`docs/API_REFERENCE.md`](docs/API_REFERENCE.md) — this server's tools mapped to their endpoints

## Contents

- [Install — Claude Desktop](#install--claude-desktop)
- [Install — other MCP clients](#install--other-mcp-clients)
- [Configuration](#configuration)
- [Multiple accounts](#multiple-accounts)
- [Tool reference](#tool-reference)
- [Rate limits](#rate-limits)
- [Agent activation](#agent-activation)
- [Build from source](#build-from-source)
- [Security](#security)
- [License](#license)

## Install — Claude Desktop

1. Download the bundle for your platform from [`dist/`](dist/) (or the
   [latest release](https://github.com/callhub/callhub-mcp/releases)):
   - macOS (Apple Silicon): `callhub-macos-arm64.mcpb`
   - macOS (Intel): `callhub-macos-x64.mcpb`
   - Windows (x64): `callhub-win-x64.mcpb`
   - Linux (x64): `callhub-linux-x64.mcpb`
2. Open **Claude Desktop → Settings → Extensions** and drag the file in
   (or double-click it).
3. Enter your extension settings (see [Configuration](#configuration)).
4. Enable the extension. The CallHub tools are now available.

**Requirements:** Python 3.10–3.14 available on the system. Each bundle vendors
its dependencies for every Python version in that range, so any of them works.

## Install — other MCP clients

Any MCP client that launches a local command can run this server. Clone and
install the dependencies, then point the client at `src/server.py`:

```bash
git clone https://github.com/callhub/callhub-mcp.git
cd callhub-mcp
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Then register the server with your client. Most clients use an `mcpServers`
JSON block — pass credentials as environment variables:

```json
{
  "mcpServers": {
    "callhub": {
      "command": "python3",
      "args": ["/absolute/path/to/callhub-mcp/src/server.py"],
      "env": {
        "CALLHUB_API_KEY": "your-api-key",
        "CALLHUB_BASE_URL": "https://api-na1.callhub.io"
      }
    }
  }
}
```

Client-specific quick commands:

- **Gemini CLI:** `gemini mcp add callhub python3 /absolute/path/to/callhub-mcp/src/server.py` (then set the `CALLHUB_*` env vars).
- **OpenAI Codex:** add an `[mcp_servers.callhub]` block to `~/.codex/config.toml` with `command = "python3"` and `args = ["/absolute/path/.../src/server.py"]`.
- **Cursor / Windsurf / Cline / Continue:** add the `mcpServers` block above to the client's MCP config file.

> Use the venv's Python (`.venv/bin/python3`) as the `command` if the server's
> dependencies aren't on your system Python.

## Configuration

You need two values, both from your CallHub dashboard under
**Settings → Account → API Key**:

- **API Key** — the key shown there.
- **API Domain** — the base URL shown there, which is region-specific
  (e.g. `https://api-na1.callhub.io`).

In Claude Desktop these are the extension settings. For other clients, set them
as the `CALLHUB_API_KEY` and `CALLHUB_BASE_URL` environment variables.

**Media uploads (optional):** `uploadMediaFile` is disabled unless you point it
at an approved folder — the **Media upload directory** setting, or the
`CALLHUB_MEDIA_DIR` environment variable. The tool can then read files **only**
from inside that folder (in addition to a media-extension check), so it can
never read arbitrary files on the host.

## Multiple accounts

The key you configure is your **`default`** account. To use more accounts, ask
the assistant to configure one by name (the `configureAccount` tool), then refer
to it by name in requests — for example, "list the teams in my *personal*
account." Requests that don't name an account use `default`.

Credentials for additional accounts are stored in a local `.env` file using the
pattern `CALLHUB_<ACCOUNT>_API_KEY` / `_BASE_URL` / `_USERNAME`.

## Tool reference

The server registers ~135 tools across all CallHub resources. See
[`docs/API_REFERENCE.md`](docs/API_REFERENCE.md) for the full tool-to-endpoint
mapping, and the [CallHub API reference](https://developer.callhub.io/) for the
underlying API. By area:

- **Contacts** — create/get/update/delete, `listContacts`, `searchContacts`, `bulkCreateContacts`, `addContactNotes`, custom fields, tags.
- **Contact lists** (a.k.a. phonebooks) — create/get/update/delete/list, add/remove contacts, counts.
- **Agents & teams** — create/get/list agents, live agents, team CRUD and membership, activation-URL export.
- **Campaigns** — Call Center, Voice Broadcast, Text Broadcast, P2P, and Relational: create, get, list, update status, duplicate, delete, assign agents.
- **DNC & suppression** — DNC lists and contacts, `addToDnc`/`removeFromDnc`, `addToSuppressionList`.
- **Numbers** — rent, auto-rent SMS numbers, list rented/validated, revalidation.
- **Media, webhooks, reporting** — media list/upload, webhook CRUD, campaign stats, credit usage, export-job polling, shortened-URL stats, `shareCredits`.

Tool names follow CallHub's product vocabulary (`createContactList`,
`createVoiceBroadcastCampaign`, `createTextBroadcast`, `addTagsToContact`).
Older names from earlier versions (`createPhonebook`, `createVbCampaign`,
`createSmsBroadcast`, …) still work as **hidden aliases**, so existing saved
flows keep functioning; new work should use the canonical names.

## Rate limits

The CallHub API enforces rate limits; the server surfaces `429` responses rather
than masking them. Notably, `searchContacts` is limited to roughly **one request
per second** — prefer a single `searchContacts` call over rapidly paging
`listContacts`. For bulk work, use the bulk endpoints (`bulkCreateContacts`)
instead of many single calls.

## Agent activation

Newly created agents start in a *pending* state and must verify their email
before they appear in `listAgents`. Manage them through the activation-export
workflow:

1. `exportAgentActivationUrls` (or `getAgentActivationExportUrl`) to obtain the export.
2. Download the activation CSV from the CallHub UI.
3. `processAgentActivationCsv` (or `processUploadedActivationCsv`) to read it.

> Earlier versions bundled a Selenium/Chrome flow that set agent passwords
> automatically. It was removed to keep the server lightweight and reliable —
> distribute the activation URLs to agents, or activate them in the CallHub UI.

## Build from source

Building produces a `callhub.mcpb` for the platform you build on (some
dependencies ship compiled wheels, so the bundle is OS/architecture-specific).

```bash
./build.sh          # single bundle for the current platform (vendors deps into src/lib, packs callhub.mcpb)
./build-all.sh      # all four platform bundles into dist/ (multi-Python: 3.10-3.14)
```

`build-all.sh` cross-downloads platform wheels (no execution needed) and packs
one bundle per platform, each containing the compiled dependencies for every
supported Python version side by side.

Requirements: `python3` (3.10+) and the [`mcpb`](https://github.com/anthropics/mcpb)
CLI (invoked via `npx @anthropic-ai/mcpb`, so Node.js is needed at build time).

### Project layout

- `manifest.json` — MCPB extension manifest (server entry, `user_config`).
- `src/server.py` — registers every tool and starts the MCP server (stdio).
- `src/callhub/` — API client, auth, and one module per resource.
- `docs/API_REFERENCE.md` — tool-to-endpoint reference.
- `build.sh` — reproducible bundle build.

## Security

- Your API key is provided via extension settings (Claude Desktop) or an
  environment variable, and is not committed to this repo.
- Use an API key scoped to the least privilege you need.

## License

[MIT](LICENSE)
