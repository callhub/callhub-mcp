# CallHub MCP (Model Control Panel)

A Claude-powered tool for managing CallHub resources via API

## Overview

CallHub MCP is a Python-based tool that allows you to interact with the CallHub API through Claude. This tool provides a comprehensive set of functions for managing contacts, phonebooks, agents, teams, campaigns, and other CallHub resources.

## Features

- **Account Management**: Configure and manage multiple CallHub accounts
- **Contact Management**: Create, retrieve, update, and delete contacts
- **Phonebook Management**: Create and manage phonebooks and their contacts
- **Agent Management**: Create, activate, and manage agents
- **Team Management**: Create and manage teams and team memberships
- **Campaign Management**: Manage call center, voice broadcast, and SMS campaigns
- **DNC Management**: Create and manage Do Not Call lists
- **Bulk Operations**: Upload and process CSV files for bulk operations
- **Error Handling**: Robust error handling with retries and rate limit awareness

## Installation

### Prerequisites

- Python 3.9+ 
- An active CallHub account with API access
- API credentials (username, API key, base URL)
- Claude access with MCP capability

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/callhub/callhub-mcp-py.git
   cd callhub-mcp-py
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure credentials using the setup wizard:
   ```bash
   python setup.py
   ```

## Claude Configuration

To use the CallHub MCP with Claude, you need to add it to Claude's configuration:

1. **Add the MCP to Claude's Configuration File**:
   - Locate your Claude configuration file
   - Add the following configuration:

   ```json
   "callhub-mcp-py": {
     "command": "/path/to/callhub-mcp-py/.venv/bin/python",
     "args": [
       "/path/to/callhub-mcp-py/src/server.py"
     ]
   }
   ```

   Make sure to replace:
   - `/path/to/callhub-mcp-py` with the actual path where you cloned the repository
   
   Note: Claude will automatically start and manage the MCP server process. You don't need to manually start or stop it.

2. **Using the MCP in Claude**:
   - After adding the configuration, Claude will automatically load the CallHub MCP
   - When you start a conversation with Claude, the CallHub tools will be available
   - You can use the `configureAccount` tool to set up your CallHub credentials the first time

3. **First-time Setup**:
   - Once connected, ask Claude to configure your CallHub account:
     ```
     I need to set up my CallHub account credentials. Can you help me?
     ```
   - Claude will guide you through using the `configureAccount` tool

4. **Starting to Use the MCP**:
   - Ask Claude about available functions:
     ```
     What CallHub tools are available?
     ```
   - Claude will show you the available tools and how to use them

## Configuration

CallHub MCP supports multiple accounts with descriptive names. Configuration is stored in the `.env` file:

```
# Default account
CALLHUB_DEFAULT_USERNAME=your_username
CALLHUB_DEFAULT_API_KEY=your_api_key
CALLHUB_DEFAULT_BASE_URL=https://api-na1.callhub.io

# Personal account
CALLHUB_PERSONAL_USERNAME=personal_username
CALLHUB_PERSONAL_API_KEY=personal_api_key
CALLHUB_PERSONAL_BASE_URL=https://api-na1.callhub.io

# Client account
CALLHUB_CLIENT_USERNAME=client_username
CALLHUB_CLIENT_API_KEY=client_api_key
CALLHUB_CLIENT_BASE_URL=https://api-na1.callhub.io
```

You can use any descriptive name for your accounts (letters, numbers, and underscores only). The account name is extracted from the environment variable name - for example, `CALLHUB_PERSONAL_API_KEY` creates an account named "personal" that you can reference in API calls.

To use a specific account for an API call, just mention the account name to Claude in natural language:
```
Claude, can you list the teams in my personal account?
```

If no account is specified, the "default" account is used.

## Example Conversations with Claude

Here are some example prompts to get started with Claude and the CallHub MCP:

### Configuring an Account
```
I need to set up my CallHub account. My username is user@example.com, my API key is abc123def456, and the base URL is https://api-na1.callhub.io. Can you configure this for me?
```

### Creating and Managing Contacts
```
I'd like to create a new contact with phone number 1234567890, first name John, and last name Doe. After that, can you add this contact to a new phonebook called "VIP Customers"?
```

### Agent Management
```
Can you show me all the teams in my CallHub account? I'd like to create a new agent in the "Sales" team.
```

### Using Multiple Accounts
```
First, I need to check the teams in my client account. Then, create a similar team structure in my personal account.
```

## Server Restart Guidelines

The CallHub MCP server must be restarted manually by the user after any code changes.
If you're using Claude or another AI assistant to modify this code:

1. The AI should NEVER assume a restart has occurred
2. The AI should ALWAYS pause after suggesting code changes
3. The AI should explicitly ask the user to restart the server
4. The AI should wait for confirmation before proceeding with testing

This is critical for ensuring code changes take effect before testing.

## Error Handling

The MCP implements robust error handling with automatic retries for transient errors and rate limiting. Error responses include detailed information about what went wrong and potential solutions.

## Agent Activation Workflow

When new agents are created via the API, they exist in a 'pending' state and must verify their email before becoming active. These pending agents are:
- NOT visible through the standard listAgents API (even with include_pending=true)
- NOT manageable through direct API calls
- Only accessible through the activation exports workflow

To activate pending agents:
1. Use exportAgentActivationUrls or getAgentActivationExportUrl to obtain the export URL
2. User downloads the activation CSV file from the CallHub UI
3. Process the CSV using processAgentActivationCsv or related functions
4. Activate agents using activateAgentsWithPassword or activateAgentsWithBatchPassword

IMPORTANT: NEVER create new test agents to check activation status - this workflow is specifically designed because pending agents are not accessible through direct API calls.

## Security Considerations

- Store your credentials securely
- Do not share your `.env` file
- Be cautious with browser automation features
- Follow the principle of least privilege when creating API keys

## Troubleshooting

- If you encounter rate limits, the tool will automatically retry with backoff
- For persistent errors, check your credentials and network connectivity
- Log files are written to logs directory with automatic rotation

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)
