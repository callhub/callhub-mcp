# utils.py
"""
Utility functions for CallHub API.
"""

import json
import time
import random
import urllib.parse
import requests
import os
from typing import Dict, List, Union, Optional, Any

# Import our custom logger
from callhub.logging import logger, is_debug_enabled

# Get configuration from environment or use defaults
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "3"))
INITIAL_BACKOFF = float(os.environ.get("INITIAL_BACKOFF", "2"))
MAX_BACKOFF = float(os.environ.get("MAX_BACKOFF", "60"))
BACKOFF_FACTOR = float(os.environ.get("BACKOFF_FACTOR", "2"))

def build_url(base_url: str, path: str, *args) -> str:
    """
    Build URL with proper path joining and parameter substitution.
    
    Args:
        base_url: The base URL of the API
        path: The path portion, can contain format placeholders
        args: Values to substitute into path placeholders
        
    Returns:
        A properly joined URL
    """
    full_path = path.format(*args) if args else path
    return f"{base_url.rstrip('/')}/{full_path.lstrip('/')}"

def parse_input_fields(fields_str: str) -> Dict[str, str]:
    """
    Parse string input as either JSON or URL-encoded parameters.
    
    Args:
        fields_str: String in either JSON or URL-encoded format
        
    Returns:
        Dictionary of parsed key-value pairs
        
    Raises:
        ValueError: If JSON format is invalid
    """
    if not fields_str:
        return {}
        
    if fields_str.startswith("{") and fields_str.endswith("}"):
        try:
            return json.loads(fields_str)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format for fields")
    else:
        result = {}
        for pair in fields_str.split("&"):
            if "=" in pair:
                key, value = pair.split("=", 1)
                result[key] = urllib.parse.unquote(value)
        return result

def retry_with_backoff(func, *args, max_retries=None, initial_backoff=None, max_backoff=None, backoff_factor=None, **kwargs):
    """
    Retry a function with exponential backoff to handle temporary failures and rate limiting.
    
    Args:
        func: The function to call
        *args: Arguments to pass to the function
        max_retries: Maximum number of retry attempts (default from env or 3)
        initial_backoff: Initial backoff time in seconds (default from env or 2)
        max_backoff: Maximum backoff time in seconds (default from env or 60)
        backoff_factor: Factor to increase backoff time on each retry (default from env or 2)
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        The result of the function call
        
    Raises:
        The final exception if all retries fail
    """
    # Use provided values or defaults from environment variables
    max_retries = max_retries if max_retries is not None else MAX_RETRIES
    initial_backoff = initial_backoff if initial_backoff is not None else INITIAL_BACKOFF
    max_backoff = max_backoff if max_backoff is not None else MAX_BACKOFF
    backoff_factor = backoff_factor if backoff_factor is not None else BACKOFF_FACTOR
    
    retries = 0
    backoff = initial_backoff
    
    while True:
        try:
            return func(*args, **kwargs)
        except requests.exceptions.RequestException as e:
            retries += 1
            
            # If we've exceeded max retries or it's not a retryable error, re-raise
            if retries > max_retries or not _is_retryable_error(e):
                raise
            
            # Get recommended retry delay from headers if available
            retry_after = _get_retry_after(e.response.headers if hasattr(e, 'response') and e.response else None)
            
            # If retry_after is specified, always use it
            if retry_after:
                delay = retry_after
                logger.info(f"Server requested delay of {delay} seconds via retry-after header")
            else:
                # Add jitter to prevent all clients retrying simultaneously
                jitter = random.uniform(0.8, 1.2)
                delay = min(backoff * jitter, max_backoff)
                backoff = min(backoff * backoff_factor, max_backoff)
            
            logger.warning(f"Request failed with {e}. Retrying in {delay:.2f} seconds (attempt {retries}/{max_retries})")
            time.sleep(delay)

def _is_retryable_error(exception):
    """
    Determine if an exception is retryable.
    
    Args:
        exception: The exception to check
        
    Returns:
        bool: True if the exception is retryable, False otherwise
    """
    # Only retry for certain error codes
    if hasattr(exception, 'response') and exception.response is not None:
        status_code = exception.response.status_code
        
        # Always retry rate limit errors
        if status_code == 429:
            return True
            
        # Retry server errors
        if 500 <= status_code < 600:
            return True
            
        # Don't retry client errors (except 429)
        if 400 <= status_code < 500:
            return False
    
    # Retry connection errors and timeouts
    if isinstance(exception, (requests.exceptions.ConnectionError, 
                              requests.exceptions.Timeout)):
        return True
        
    return False

def _get_retry_after(headers):
    """
    Get the recommended retry delay from response headers.
    
    Args:
        headers: The response headers
        
    Returns:
        float: The recommended delay in seconds, or None if not specified
    """
    if not headers:
        return None
        
    # Check for both 'retry-after' and 'Retry-After' - header names are case-insensitive
    retry_after = headers.get('retry-after') or headers.get('Retry-After')
    if not retry_after:
        return None
        
    # Log the value for debugging
    logger.debug(f"Found retry-after header: {retry_after}")
    
    try:
        # Handle numeric value (seconds)
        return float(retry_after)
    except ValueError:
        # Handle HTTP date format (unlikely, but possible)
        try:
            from email.utils import parsedate_to_datetime
            from datetime import datetime
            date = parsedate_to_datetime(retry_after)
            delay = (date - datetime.now(date.tzinfo)).total_seconds()
            return max(0, delay)  # Don't return negative delays
        except Exception as e:
            logger.error(f"Error parsing retry-after header: {e}")
            return None

def api_call(method: str, url: str, headers: dict, data: Any = None, params: Dict = None, 
             json_data: Any = None, max_retries: int = None) -> Dict:
    """
    Make an API call with consistent error handling and automatic retries.
    
    Args:
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        url: Full URL to call
        headers: HTTP headers
        data: Form data (for POST/PUT)
        params: Query parameters (for GET)
        json_data: JSON body data (for POST/PUT with JSON content type)
        max_retries: Maximum number of retry attempts (default from env or 3)
        
    Returns:
        Dictionary with API response or error information
    """
    try:
        # Use default from environment if not provided
        max_retries = max_retries if max_retries is not None else MAX_RETRIES
        
        # Prepare the request
        logger.info(f"{method} request to {url}")
        
        # Log detailed request info in debug mode
        if is_debug_enabled():
            if data:
                logger.debug(f"Request data: {data}")
            if json_data:
                logger.debug(f"Request JSON: {json_data}")
            if params:
                logger.debug(f"Request params: {params}")
            logger.debug(f"Request headers: {headers}")
        
        # Define the function to make the request with error handling
        def make_request():
            resp = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                params=params,
                json=json_data,verify=False
            )
            
            # Log the response status
            logger.info(f"Response status: {resp.status_code}")
            
            # Handle 4xx/5xx errors (except 429 which is handled by retry mechanism)
            if resp.status_code >= 400 and resp.status_code != 429:
                logger.warning(f"API error: {resp.status_code} {resp.reason}")
                
                # Try to get and log the response body
                try:
                    error_body = resp.text
                    logger.debug(f"Response body: {error_body}")
                    
                    # Try to parse error as JSON and format it nicely
                    try:
                        error_json = resp.json()
                        error_messages = []
                        
                        for field, messages in error_json.items():
                            if isinstance(messages, list):
                                for msg in messages:
                                    error_messages.append(f"{field}: {msg}")
                            else:
                                error_messages.append(f"{field}: {messages}")
                        
                        if error_messages:
                            # Instead of raising, store our parsed error and return it
                            # This prevents retry attempts for client errors
                            return {
                                "isError": True,
                                "content": [{"type": "text", "text": "; ".join(error_messages)}]
                            }
                    except json.JSONDecodeError:
                        # Not JSON, go ahead and raise the exception
                        pass
                except Exception as e:
                    logger.error(f"Error getting response body: {str(e)}")
                
                # If we get here, either there was no error detail or we couldn't parse it
                resp.raise_for_status()
            
            # For 429 rate limit, pass along the exception for retry handling
            if resp.status_code == 429:
                logger.warning(f"Rate limit exceeded: {resp.status_code} {resp.reason}")
                # Extract Retry-After header if present
                retry_after = resp.headers.get('Retry-After')
                if retry_after:
                    logger.info(f"Retry-After: {retry_after} seconds")
                resp.raise_for_status()
            
            # Handle 204 No Content or empty responses
            if resp.status_code == 204 or not resp.text:
                return {"success": True, "message": "Operation successful"}
                
            # Parse and return JSON response
            try:
                result = resp.json()
                # Log response in debug mode
                if is_debug_enabled():
                    logger.debug(f"Response JSON: {json.dumps(result, indent=2)}")
                return result
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing response as JSON: {str(e)}")
                # Return a success with the raw text for non-JSON responses
                return {"success": True, "message": resp.text}
        
        # Use the retry mechanism for the request
        return retry_with_backoff(make_request, max_retries=max_retries)
            
    except requests.exceptions.RequestException as e:
        # If we've already retried the maximum number of times or it's not retryable
        # Build a user-friendly error response
        status_code = e.response.status_code if hasattr(e, 'response') and e.response else None
        error_message = str(e)
        
        # Add more detailed error info if available
        if hasattr(e, 'response') and e.response and hasattr(e.response, 'text'):
            error_body = e.response.text
            logger.debug(f"Detailed error response: {error_body}")
            
            # Try to parse the error body as JSON
            try:
                error_json = json.loads(error_body)
                if isinstance(error_json, dict):
                    # Format the error message in a more readable way
                    error_messages = []
                    for field, messages in error_json.items():
                        if isinstance(messages, list):
                            for msg in messages:
                                error_messages.append(f"{field}: {msg}")
                        else:
                            error_messages.append(f"{field}: {messages}")
                    
                    if error_messages:
                        return {
                            "isError": True,
                            "content": [{"type": "text", "text": "; ".join(error_messages)}]
                        }
            except json.JSONDecodeError:
                # Not JSON, use the raw text
                error_message = f"{error_message} - Response: {error_body}"
        
        # Special handling for rate limiting errors
        if status_code == 429:
            # Extract retry information if available
            retry_after = _get_retry_after(e.response.headers if hasattr(e, 'response') and e.response else None)
            retry_msg = f" Please retry after {retry_after} seconds." if retry_after else ""
            
            return {
                "isError": True, 
                "content": [{
                    "type": "text", 
                    "text": f"Rate limit exceeded (429). The API has a limit of calls per minute.{retry_msg}"
                }]
            }
        
        # Generic error response
        logger.error(f"Request exception: {error_message}")
        return {"isError": True, "content": [{"type": "text", "text": error_message}]}
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def get_auth_headers(api_key: str, content_type: str = "application/json") -> Dict[str, str]:
    """
    Create standard authorization headers for API requests.
    
    Args:
        api_key: API key for authentication
        content_type: Content type header value
        
    Returns:
        Dictionary of HTTP headers
    """
    return {
        "Authorization": f"Token {api_key}",
        "Content-Type": content_type
    }
