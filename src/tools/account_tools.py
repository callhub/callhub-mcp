"""Tool wrappers for Account operations."""
from tools_callhub import (
    list_accounts,
    add_callhub_account,
    update_callhub_account,
    delete_callhub_account,
)


def register(server):
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
