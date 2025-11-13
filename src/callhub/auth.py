# auth.py
"""
Authentication and credential handling for CallHub API.
"""

import os
import sys
import re
import logging
from dotenv import load_dotenv, find_dotenv, set_key

# Setup basic logging
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="[callhub] %(asctime)s - %(levelname)s - %(message)s"  # Important!
)
logger = logging.getLogger("callhub")

def _env_path() -> str:
    """
    Walk up from this file's directory looking for .env.
    If found, use that. Otherwise fall back to ~/.env.
    """
    curr = os.path.dirname(os.path.abspath(__file__))
    # Go one directory up since we're now in callhub/
    curr = os.path.dirname(curr)
    while True:
        candidate = os.path.join(curr, ".env")
        if os.path.exists(candidate):
            logger.info(f"Using .env from: {candidate}")
            return candidate
        parent = os.path.dirname(curr)
        if parent == curr:
            break
        curr = parent

    # If we didn't find a .env file, look in the home directory
    home = os.path.expanduser("~/.env")
    if os.path.exists(home):
        logger.info(f"Using .env from: {home}")
        return home
    
    # If no .env exists, use the default location for later saving
    default_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    logger.info(f"No .env found. Will create at: {default_path}")
    return default_path

def load_all_credentials() -> dict:
    """
    Load credentials from .env file.
    
    The format in .env is:
    CALLHUB_{ACCOUNT}_USERNAME=username
    CALLHUB_{ACCOUNT}_API_KEY=key
    CALLHUB_{ACCOUNT}_BASE_URL=url
    
    For backward compatibility, also looks for:
    CALLHUB_API_KEY=key (mapped to 'default' account)
    
    Returns:
        dict: Dictionary with account names as keys and their credentials as values
    """
    # Ensure .env is loaded
    env_path = _env_path()
    load_dotenv(env_path)
    
    # Find all CallHub credentials in environment variables
    creds = {}
    pattern = r"^CALLHUB_(.+)_API_KEY$"
    
    # First pass to find all accounts
    account = None
    for key in os.environ:
        match = re.match(pattern, key)
        if match:
            account = match.group(1).lower()
            if account != "account":  # Skip CALLHUB_ACCOUNT env var
                username_key = f"CALLHUB_{match.group(1)}_USERNAME"
                base_url_key = f"CALLHUB_{match.group(1)}_BASE_URL"
                
                creds[account] = {
                    "username": os.environ.get(username_key, ""),
                    "api_key": os.environ[key],
                    "base_url": os.environ.get(base_url_key, "https://api.callhub.io")
                }
    
    # Check for the legacy format (no account prefix)
    default_api_key = os.environ.get("CALLHUB_API_KEY")
    if default_api_key and "default" not in creds:
        creds["default"] = {
            "username": os.environ.get("CALLHUB_USERNAME", ""),
            "api_key": default_api_key,
            "base_url": os.environ.get("CALLHUB_BASE_URL", "https://api.callhub.io")
        }
    if not creds:
        logger.warning(f"No CallHub credentials found in .env file at {env_path}")
        logger.info("Use the setup wizard or configureAccount tool to set up your credentials")
    elif "default" not in creds:
        creds["default"] = creds[account]  # Use the last account as default if not set
        
    return creds

def save_credentials(creds: dict) -> None:
    """
    Save the credentials dict to .env file.
    
    Args:
        creds: Dictionary with account names as keys and their credentials as values
    """
    env_path = _env_path()
    
    # Create parent directories if needed
    os.makedirs(os.path.dirname(env_path), exist_ok=True)
    
    # Add credentials to .env file
    for account, config in creds.items():
        # Make sure account name is uppercase in .env vars
        account_upper = account.upper()
        # Add or update username
        set_key(env_path, f"CALLHUB_{account_upper}_USERNAME", config.get("username", ""))
        # Add or update API key
        set_key(env_path, f"CALLHUB_{account_upper}_API_KEY", config.get("api_key", ""))
        # Add or update base URL
        set_key(env_path, f"CALLHUB_{account_upper}_BASE_URL", config.get("base_url", "https://api.callhub.io"))
    
    logger.info(f"Wrote credentials to: {env_path}")

def get_account_config(account: str = None) -> tuple:
    """
    Get the API key and base URL for the specified account.
    
    Args:
        account: The account name to get config for, defaults to CALLHUB_ACCOUNT
                 environment variable or "default"
                 
    Returns:
        tuple: (account_name, api_key, base_url)
        
    Raises:
        ValueError: If the account is not found or missing required fields
    """
    creds = load_all_credentials()
    account = account or os.getenv("CALLHUB_ACCOUNT", "default")
    account = account.lower()  # Normalize account name to lowercase
    
    if not creds:
        raise ValueError("No CallHub credentials found. Please run setup.py or use the configureAccount tool.")
    
    if account not in creds:
        raise ValueError(f"Account '{account}' not found in credentials.")
    
    cfg = creds[account]
    
    # Username is stored but not returned
    base_url = cfg.get("base_url") or cfg.get("baseUrl")
    api_key = cfg.get("api_key")
    
    if not base_url:
        raise ValueError(f"Missing 'base_url' for account '{account}' in credentials.")
    if not api_key:
        raise ValueError(f"Missing 'api_key' for account '{account}' in credentials.")
        
    return account, api_key, base_url

def check_configuration():
    """
    Check if CallHub MCP is configured properly.
    
    Returns:
        bool: True if configured, False otherwise
    """
    try:
        creds = load_all_credentials()
        return bool(creds)
    except Exception:
        return False