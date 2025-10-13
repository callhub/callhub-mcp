"""
Agent activation helper functions for CallHub API.

These functions handle the export and processing of agent activation URLs.
Note: Some of these endpoints may require session-based authentication
rather than API key authentication.
"""

import io
import csv
import time
import sys
import json
import re
from typing import Dict, Any, Optional

from .auth import get_account_config
from .utils import build_url, get_auth_headers, api_call

def export_agent_activation_urls(account_name: Optional[str] = None, max_retries: int = 20,
                                 retry_interval: int = 3) -> Dict:
    """
    Export and retrieve agent activation URLs from CallHub.
    
    Args:
        account_name: The CallHub account name to use
        max_retries: Maximum number of status check retries (default: 20)
        retry_interval: Seconds between retry attempts (default: 3)
        
    Returns:
        Dict with activation URLs or error information
    """
    # Start the export job
    job_result = start_activation_export(account_name)
    
    # Check for errors in starting the job
    if job_result.get("isError"):
        return job_result
    
    job_id = job_result.get("job_id")
    if not job_id:
        return {
            "isError": True, 
            "content": [{"type": "text", "text": "Failed to get export job ID"}]
        }
    
    # Poll for job completion
    for attempt in range(max_retries):
        sys.stderr.write(f"[callhub] Checking export progress (attempt {attempt+1}/{max_retries})...\n")
        
        status_result = check_export_status(account_name, job_id)
        
        # Check for errors in status check
        if status_result.get("isError"):
            return status_result
        
        state = status_result.get("state")
        
        if state == "SUCCESS":
            # Job completed successfully
            download_url = status_result.get("download_url")
            
            if not download_url:
                return {
                    "isError": True, 
                    "content": [{"type": "text", "text": "Export completed but no download URL found"}]
                }
            
            # Download the CSV file
            csv_result = download_activation_csv(account_name, download_url)
            
            # Check for errors in download
            if csv_result.get("isError"):
                return csv_result
            
            # Parse and return the CSV data
            return parse_activation_csv(csv_result.get("csv_data", ""))
        
        elif state == "PROGRESS":
            # Job still in progress
            progress = status_result.get("progress", {})
            current = progress.get("current", 0)
            total = progress.get("total", 1)
            percentage = (current / total) * 100 if total > 0 else 0
            
            sys.stderr.write(f"[callhub] Export progress: {current}/{total} ({percentage:.1f}%)\n")
            
            # Wait before checking again
            time.sleep(retry_interval)
            
        else:
            # Unknown or error state
            return {
                "isError": True, 
                "content": [{
                    "type": "text", 
                    "text": f"Export job in unexpected state: {state}"
                }]
            }
    
    # If we get here, we've exceeded max retries
    return {
        "isError": True, 
        "content": [{
            "type": "text", 
            "text": f"Export timed out after {max_retries} attempts"
        }]
    }

def start_activation_export(account_name: Optional[str] = None) -> Dict:
    """
    Start the export process for pending agent activation URLs.
    
    Args:
        account_name: The CallHub account name to use
        
    Returns:
        Dict with the job ID for tracking export progress
    """
    account, api_key, base_url = get_account_config(account_name)
    
    # Endpoint for initiating export
    url = build_url(base_url, "/agent/reactivate_export/")
    headers = get_auth_headers(api_key)
    
    sys.stderr.write(f"[callhub] Starting agent activation export...\n")

    # Make the request to start the export
    response = api_call("GET", url, headers)
    sys.stderr.write( f"[callhub] Activation export response: {response}\n" )

    if response.get("isError"):
        return

    # Try to extract the job ID from the response HTML
    text = response.get("message", "")
    if not text and response.get("content"):
        text = response["content"][0].get("text", "")

    if not text:
        return {"isError": True, "content": [{"type": "text", "text": "Could not find response text."}]}

    # Look for the progress_job_id in the JavaScript variables in the HTML
    job_id_match = re.search(r'var progress_job_id = "([^"]+)";', text)
    
    if not job_id_match:
        return {
            "isError": True, 
            "content": [{"type": "text", "text": "Could not find export job ID in response. This may indicate an authentication issue."}]
        }
    
    job_id = job_id_match.group(1)
    sys.stderr.write(f"[callhub] Export job ID: {job_id}\n")

    # Return the job ID for tracking
    return {"job_id": job_id}

def check_export_status(account_name: Optional[str] = None, job_id: str = None) -> Dict:
    """
    Check the status of an export job.
    
    Args:
        account_name: The CallHub account name to use
        job_id: The export job ID to check
        
    Returns:
        Dict with the current state and progress information
    """
    if not job_id:
        return {"isError": True, "content": [{"type": "text", "text": "Job ID is required"}]}
    
    account, api_key, base_url = get_account_config(account_name)
    
    # Endpoint for checking export progress
    # Add a timestamp to prevent caching
    timestamp = int(time.time() * 1000)
    url = build_url(base_url, f"/exported_file/progress/{job_id}/?_={timestamp}")
    headers = get_auth_headers(api_key)


    # Make the request to check progress
    result = api_call("GET", url, headers)
    sys.stderr.write( f"[callhub] Status check response: {result}\n" )

    if result.get("isError"):
        return result

    sys.stderr.write(f"[callhub] Status check result: {json.dumps(result)}\n")
    
    state = result.get("state")

    # If success, extract the download URL
    if state == "SUCCESS":
        data = result.get("data", {})
        url = data.get("url")
        
        if not url:
            return {
                "isError": True, 
                "content": [{"type": "text", "text": "No download URL found in response"}]
            }
        
        return {
            "state": state,
            "download_url": url
        }

    # If still in progress, return progress information
    elif state == "PROGRESS":
        data = result.get("data", {})
        
        return {
            "state": state,
            "progress": data
        }

    # Any other state is treated as an error
    else:
        return {
            "isError": True, 
            "content": [{"type": "text", "text": f"Unknown export state: {state}"}]
        }

def download_activation_csv(account_name: Optional[str] = None, download_url: str = None) -> Dict:
    """
    Download the activation CSV file.
    
    Args:
        account_name: The CallHub account name to use
        download_url: The relative URL for downloading the CSV
        
    Returns:
        Dict with the CSV data or error information
    """
    if not download_url:
        return {"isError": True, "content": [{"type": "text", "text": "Download URL is required"}]}
    
    account, api_key, base_url = get_account_config(account_name)
    
    # Construct the full URL for downloading the CSV
    if download_url.startswith("/"):
        url = base_url + download_url
    else:
        url = base_url + "/" + download_url
        
    headers = get_auth_headers(api_key)

    # Make the request to download the CSV
    response = api_call("GET", url, headers)
    sys.stderr.write( f"[callhub] CSV download response status: {response.status_code}\n" )
    if response.get("isError"):
        return response

    csv_data = response.get("message", "")
    if not csv_data and response.get("content"):
        csv_data = response["content"][0].get("text", "")

    if not csv_data:
        return {"isError": True, "content": [{"type": "text", "text": "Failed to get CSV data."}]}

    # Return the CSV data
    return {"csv_data": csv_data}

def parse_activation_csv(csv_data: str) -> Dict:
    """
    Parse the activation CSV to extract URLs and other information.
    
    Args:
        csv_data: The CSV data as a string
        
    Returns:
        Dict with the parsed activation data
    """
    if not csv_data:
        return {"isError": True, "content": [{"type": "text", "text": "No CSV data to parse"}]}
    
    try:
        # Parse the CSV data
        reader = csv.reader(io.StringIO(csv_data))
        
        # Extract the header row
        try:
            headers = next(reader)
        except StopIteration:
            return {"isError": True, "content": [{"type": "text", "text": "CSV file is empty"}]}
        
        # Find the URL column index
        url_col = -1
        username_col = -1
        email_col = -1
        
        for i, header in enumerate(headers):
            h = header.lower()
            if "url" in h or "link" in h:
                url_col = i
            elif "username" in h:
                username_col = i
            elif "email" in h:
                email_col = i
        
        if url_col == -1:
            return {
                "isError": True, 
                "content": [{"type": "text", "text": "Could not find URL column in CSV file"}]
            }
        
        # Extract activation data from each row
        activations = []
        
        for row in reader:
            if len(row) <= url_col:
                continue  # Skip incomplete rows
                
            activation = {
                "url": row[url_col].strip()
            }
            
            # Add username if available
            if username_col != -1 and len(row) > username_col:
                activation["username"] = row[username_col].strip()
                
            # Add email if available
            if email_col != -1 and len(row) > email_col:
                activation["email"] = row[email_col].strip()
                
            activations.append(activation)
        
        # Return the parsed activation data
        return {
            "success": True,
            "message": f"Successfully extracted {len(activations)} activation URLs",
            "activations": activations,
            "raw_csv": csv_data  # Include the raw CSV in case direct parsing is needed
        }
        
    except Exception as e:
        sys.stderr.write(f"[callhub] Exception in parse_activation_csv: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}
