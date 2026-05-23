#!/usr/bin/env python3
"""
CallHub MCP Setup Wizard

This script helps you configure your CallHub MCP installation by setting up your API credentials.
It will guide you through the process of adding one or more CallHub accounts.
"""

import os
import sys
import re
from dotenv import load_dotenv, set_key, find_dotenv

def get_input(prompt, default=None, validator=None, password=False):
    """Get user input with validation and default value."""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    while True:
        if password:
            import getpass
            value = getpass.getpass(prompt)
        else:
            value = input(prompt)
        
        # Use default if empty
        if not value and default:
            value = default
        
        # Validate if needed
        if validator and not validator(value):
            continue
            
        return value

def validate_url(url):
    """Validate a URL."""
    if not url:
        print("URL cannot be empty.")
        return False
    
    if not url.startswith(('http://', 'https://')):
        print("URL must start with http:// or https://")
        return False
    
    return True

def validate_not_empty(value):
    """Validate that a value is not empty."""
    if not value:
        print("Value cannot be empty.")
        return False
    
    return True

def validate_account_name(name):
    """Validate account name format."""
    if not name:
        print("Account name cannot be empty.")
        return False
    
    if not re.match(r'^[a-zA-Z0-9_]+$', name):
        print("Account name can only contain letters, numbers, and underscores.")
        return False
    
    return True

def add_account(env_file, is_default=False):
    """Add a new CallHub account configuration."""
    # Get account details from user
    if is_default:
        account_name = "DEFAULT"
        print("\nConfiguring DEFAULT CallHub account:")
    else:
        print("\nConfiguring additional CallHub account:")
        account_name = get_input(
            "Account name (letters, numbers, and underscores only)",
            validator=validate_account_name
        ).upper()
    
    username = get_input("CallHub username (email)", validator=validate_not_empty)
    
    api_key = get_input(
        "CallHub API key", 
        validator=validate_not_empty,
        password=True
    )
    
    base_url = get_input(
        "CallHub API base URL",
        default="https://api.callhub.io",
        validator=validate_url
    )
    
    # Save to .env file
    set_key(env_file, f"CALLHUB_{account_name}_USERNAME", username)
    set_key(env_file, f"CALLHUB_{account_name}_API_KEY", api_key)
    set_key(env_file, f"CALLHUB_{account_name}_BASE_URL", base_url)
    
    print(f"Account '{account_name}' successfully configured.")
    return True

def main():
    """Main setup wizard function."""
    print("="*60)
    print("Welcome to the CallHub MCP Setup Wizard!")
    print("="*60)
    print("\nThis wizard will help you configure your CallHub MCP installation.")
    print("You'll need your CallHub API credentials to proceed.")
    print("\nYou can find your API key in the CallHub web interface under:")
    print("  Settings > Integrations > API Key")
    
    # Check for existing .env
    env_file = find_dotenv()
    if not env_file:
        env_file = os.path.join(os.getcwd(), '.env')
        if not os.path.exists(env_file):
            # Create empty .env file
            with open(env_file, 'w') as f:
                pass
    
    # Load existing environment
    load_dotenv(env_file)
    
    # Check if we have existing configuration
    existing_accounts = []
    for key in os.environ:
        match = re.match(r'^CALLHUB_(.+)_API_KEY$', key)
        if match:
            existing_accounts.append(match.group(1))
    
    if existing_accounts:
        print("\nExisting CallHub accounts detected:")
        for account in existing_accounts:
            print(f"  - {account}")
        
        overwrite = get_input("Do you want to overwrite existing configuration? (y/n)", default="n")
        if overwrite.lower() != 'y':
            print("\nSetup canceled. Existing configuration preserved.")
            return
    
    # Configure default account
    add_account(env_file, is_default=True)
    
    # Configure additional accounts
    while True:
        add_another = get_input("\nDo you want to add another account? (y/n)", default="n")
        if add_another.lower() != 'y':
            break
        
        add_account(env_file)
    
    # Add configuration options
    print("\nConfiguring MCP settings:")
    
    log_level = get_input(
        "Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
        default="INFO"
    )
    set_key(env_file, "LOG_LEVEL", log_level)
    
    max_retries = get_input("Maximum API retries", default="3")
    set_key(env_file, "MAX_RETRIES", max_retries)
    
    print("\nConfiguration complete! You're ready to use CallHub MCP.")
    print("You can start the server with: python src/server.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())