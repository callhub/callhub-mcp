# account_management.py
"""
Account management tools for CallHub API.
"""

import os
import sys
import requests
from dotenv import load_dotenv, set_key, find_dotenv
from .auth import _env_path, load_all_credentials, save_credentials
from .utils import build_url, get_auth_headers

def add_account(account_name: str, username: str, api_key: str, base_url: str) -> dict:
    """
    Add a new CallHub account to the .env file after verifying credentials.
    
    Args:
        account_name: Name of the account to add
        username: Username/email for the CallHub account
        api_key: API key for the account
        base_url: Base URL for the CallHub instance
        
    Returns:
        dict: Status of the operation
    """
    try:
        # --- Verification Step ---
        # Before saving, make a simple API call to verify credentials are valid
        verification_url = build_url(base_url, "/v1/users/")
        headers = get_auth_headers(api_key)
        
        response = requests.get(verification_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return {
                "success": False,
                "message": f"Failed to verify credentials for account '{account_name}'. The API call failed with status {response.status_code}. Please check the API key and base URL.",
                "error": response.text
            }
        # --- End Verification Step ---

        # Normalize account name to lowercase
        account_name = account_name.lower()
        
        # Load existing credentials
        try:
            creds = load_all_credentials()
        except FileNotFoundError:
            creds = {}
        
        # Check if account already exists
        if account_name in creds:
            return {
                "success": False,
                "message": f"Account '{account_name}' already exists. Use updateAccount to modify it.",
                "account": account_name
            }
        
        # Add the new account
        creds[account_name] = {
            "username": username,
            "api_key": api_key,
            "base_url": base_url
        }
        
        # Save updated credentials
        save_credentials(creds)
        
        return {
            "success": True,
            "message": f"Account '{account_name}' verified and added successfully.",
            "account": account_name
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": f"A network error occurred while trying to verify the account: {e}. Please check the base URL and your connection.",
            "error": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error adding account: {str(e)}",
            "error": str(e)
        }

def update_account(account_name: str, username: str = None, api_key: str = None, base_url: str = None) -> dict:
    """
    Update an existing CallHub account in the .env file.
    
    Args:
        account_name: Name of the account to update
        username: New username/email (optional)
        api_key: New API key (optional)
        base_url: New base URL (optional)
        
    Returns:
        dict: Status of the operation
    """
    try:
        # Normalize account name to lowercase
        account_name = account_name.lower()
        
        # Load existing credentials
        try:
            creds = load_all_credentials()
        except FileNotFoundError:
            return {
                "success": False,
                "message": f"No credentials file found. Use addAccount to create a new account.",
                "account": account_name
            }
        
        # Check if account exists
        if account_name not in creds:
            return {
                "success": False,
                "message": f"Account '{account_name}' does not exist. Use addAccount to create it.",
                "account": account_name
            }
        
        # Update fields that were provided
        if username:
            creds[account_name]["username"] = username
            
        if api_key:
            creds[account_name]["api_key"] = api_key
        
        if base_url:
            creds[account_name]["base_url"] = base_url
        
        # Save updated credentials
        save_credentials(creds)
        
        return {
            "success": True,
            "message": f"Account '{account_name}' updated successfully.",
            "account": account_name
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error updating account: {str(e)}",
            "error": str(e)
        }

def delete_account(account_name: str) -> dict:
    """
    Delete a CallHub account from the .env file.
    
    Args:
        account_name: Name of the account to delete
        
    Returns:
        dict: Status of the operation
    """
    try:
        # Normalize account name to lowercase
        account_name = account_name.lower()
        
        # Load existing credentials
        try:
            creds = load_all_credentials()
        except FileNotFoundError:
            return {
                "success": False,
                "message": f"No credentials file found.",
                "account": account_name
            }
        
        # Check if account exists
        if account_name not in creds:
            return {
                "success": False,
                "message": f"Account '{account_name}' does not exist.",
                "account": account_name
            }
        
        # Delete the account
        del creds[account_name]
        
        # Save updated credentials
        save_credentials(creds)
        
        return {
            "success": True,
            "message": f"Account '{account_name}' deleted successfully.",
            "account": account_name
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error deleting account: {str(e)}",
            "error": str(e)
        }
