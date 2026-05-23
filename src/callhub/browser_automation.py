"""
Browser automation helper for CallHub operations that require session authentication.

This module provides functions to automate browser-based tasks such as exporting
agent activation URLs or performing other operations that require session authentication
rather than API key authentication.
"""

import os
import time
import json
import sys
import tempfile
import csv
import platform
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from io import StringIO
from contextlib import contextmanager
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
from .auth import get_account_config
from .csv_processor import find_file

# Get the user's home directory
HOME_DIR = str(Path.home())

# Define Chrome user data directory based on platform
def get_chrome_user_data_dir():
    system = platform.system()
    if system == "Darwin":  # macOS
        return os.path.join(HOME_DIR, "Library", "Application Support", "Google", "Chrome")
    elif system == "Windows":
        return os.path.join(HOME_DIR, "AppData", "Local", "Google", "Chrome", "User Data")
    elif system == "Linux":
        return os.path.join(HOME_DIR, ".config", "google-chrome")
    else:
        return None

# Maximum time to wait for user login
LOGIN_TIMEOUT_SECONDS = 300  # 5 minutes

# Wait times for various operations
WAIT_TIMEOUT_SECONDS = 60
SHORT_WAIT_SECONDS = 3  # Reduced from 5 to 3 seconds for faster processing
POLL_INTERVAL_SECONDS = 1  # Reduced from 2 to 1 second

@contextmanager
def get_browser(headless: bool = True, use_profile: bool = True) -> webdriver.Chrome:
    """
    Initialize a Chrome browser instance.
    
    Args:
        headless: Whether to run Chrome in headless mode (no UI)
        use_profile: Whether to use the user's Chrome profile
        
    Yields:
        Chrome WebDriver instance
    """
    options = Options()
    if headless:
        options.add_argument("--headless")
    
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    
    # Don't use any user profile to avoid the "profile in use" error
    # This means users will need to log in each time, but it's more reliable
    options.add_argument("--incognito")  # Use incognito mode to avoid profile issues
    
    # Add helpful options to make automation smoother
    options.add_argument("--disable-extensions")  # For better stability
    options.add_argument("--disable-popup-blocking")  # Allow popups which might be part of the process
    options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection
    options.add_argument("--no-sandbox")  # Speed up browser startup
    options.add_argument("--disable-dev-shm-usage")  # Avoid memory issues
    
    # Experimental options
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    # Add download preferences
    prefs = {
        "download.default_directory": tempfile.gettempdir(),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "credentials_enable_service": True,  # Enable password saving
        "profile.password_manager_enabled": True,  # Enable password manager
        "disk-cache-size": 4096  # Small cache size for faster operation
    }
    options.add_experimental_option("prefs", prefs)
    
    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        sys.stderr.write("[callhub] Chrome browser initialized\n")
        sys.stderr.write("[callhub] You will need to enter your CallHub login credentials manually\n")
        
        try:
            yield driver
        finally:
            sys.stderr.write("[callhub] Closing Chrome browser\n")
            driver.quit()
    except Exception as e:
        sys.stderr.write(f"[callhub] Error initializing Chrome browser: {str(e)}\n")
        raise

def wait_for_user_login(driver: webdriver.Chrome, base_url: str) -> bool:
    """
    Navigate to the login page and wait for the user to log in.
    
    Args:
        driver: WebDriver instance
        base_url: CallHub base URL to navigate to
        
    Returns:
        True if login was successful, False otherwise
    """
    try:
        # Extract the domain from the base_url
        # This handles cases like https://api-na1.callhub.io or https://app.callhub.io
        if '://' in base_url:
            domain = base_url.split('://')[1].split('/')[0]  # Get the domain part
        else:
            domain = base_url.split('/')[0]
            
        # Remove 'api-' prefix if present
        if domain.startswith('api-'):
            domain = domain[4:]  # Remove 'api-'
            
        # Construct the proper login URL - always using HTTPS
        login_url = f"https://{domain}/login/"
        sys.stderr.write(f"[callhub] Navigating to login page: {login_url}\n")
        driver.get(login_url)
        
        # Check if already logged in
        if is_logged_in(driver):
            sys.stderr.write("[callhub] Already logged in\n")
            return True
        
        # Wait for user to log in (check for presence of user menu or dashboard element)
        login_deadline = time.time() + LOGIN_TIMEOUT_SECONDS
        
        while time.time() < login_deadline:
            sys.stderr.write("[callhub] Waiting for user to complete login...\n")
            
            if is_logged_in(driver):
                sys.stderr.write("[callhub] Login successful\n")
                return True
                
            # Wait before checking again
            time.sleep(POLL_INTERVAL_SECONDS)
        
        sys.stderr.write("[callhub] Login timeout exceeded\n")
        return False
        
    except Exception as e:
        sys.stderr.write(f"[callhub] Error during login: {str(e)}\n")
        return False

def is_logged_in(driver: webdriver.Chrome) -> bool:
    """
    Check if the user is currently logged in to CallHub.
    
    Args:
        driver: WebDriver instance
        
    Returns:
        True if logged in, False otherwise
    """
    try:
        # Look for dashboard elements or user menu to determine if logged in
        # This may need to be adjusted based on CallHub's UI
        for selector in [
            ".dashboard-nav",            # Dashboard navigation
            ".user-menu",                # User menu dropdown
            "#sidebar-wrapper",          # Sidebar in dashboard
            ".agency-dashboard",         # Agency dashboard container
            ".callhub-dashboard"         # Dashboard container
        ]:
            try:
                if driver.find_elements(By.CSS_SELECTOR, selector):
                    return True
            except:
                continue
                
        return False
    except:
        return False

def navigate_to_agents_page(driver: webdriver.Chrome, base_url: str) -> bool:
    """
    Navigate to the agents management page.
    
    Args:
        driver: WebDriver instance
        base_url: CallHub base URL
        
    Returns:
        True if navigation was successful, False otherwise
    """
    try:
        # Extract the domain from the base_url
        if '://' in base_url:
            domain_parts = base_url.split('://')
            protocol = domain_parts[0]
            domain = domain_parts[1].split('/')[0]  # Get the domain part
        else:
            protocol = "https"
            domain = base_url.split('/')[0]
        
        # Remove 'api-' prefix if present
        if domain.startswith('api-'):
            domain = domain[4:]  # Remove 'api-'
            
        # Always use HTTPS
        protocol = "https"
        
        # Construct the base URL with the proper domain
        web_base_url = f"{protocol}://{domain}"
        
        # First check if we're already on the dashboard or redirect to it if needed
        current_url = driver.current_url
        sys.stderr.write(f"[callhub] Current URL: {current_url}\n")
        
        # If we're not on the dashboard or a subpage, go to the dashboard
        if not (web_base_url in current_url and ("/dashboard" in current_url or "/agent/" in current_url)):
            dashboard_url = f"{web_base_url}/dashboard/"
            sys.stderr.write(f"[callhub] Navigating to dashboard: {dashboard_url}\n")
            driver.get(dashboard_url)
            time.sleep(SHORT_WAIT_SECONDS)  # Give some time for the dashboard to load
        
        # Then navigate to the agents page
        agents_url = f"{web_base_url}/agent/"
        sys.stderr.write(f"[callhub] Navigating to agents page: {agents_url}\n")
        driver.get(agents_url)
        
        # Wait for the page to load - try different selectors that might appear on the agents page
        try:
            WebDriverWait(driver, WAIT_TIMEOUT_SECONDS).until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#agent-list-table")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".agent-list-container")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-action='create-agent']")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#agent-page")),
                    EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Agents')]"))
                )
            )
        except TimeoutException:
            # If we can't find specific elements, at least ensure we're on what appears to be the agents page
            if "/agent/" in driver.current_url:
                sys.stderr.write("[callhub] On agents page but couldn't detect specific elements\n")
            else:
                raise
        
        sys.stderr.write("[callhub] Successfully navigated to agents page\n")
        
        # Take a short pause to allow for any JavaScript or AJAX to complete
        time.sleep(SHORT_WAIT_SECONDS / 2)  # Reduced wait time
        
        return True
    except Exception as e:
        sys.stderr.write(f"[callhub] Error navigating to agents page: {str(e)}\n")
        return False

def initiate_agent_activation_export(driver: webdriver.Chrome) -> bool:
    """
    Initiate the export of agent activation URLs.
    
    Args:
        driver: WebDriver instance
        
    Returns:
        True if export initiated successfully, False otherwise
    """
    try:
        # Expanded list of selectors for the export button
        export_selectors = [
            # Direct link to reactivate export
            "a[href='/agent/reactivate_export/']",
            "a[href*='reactivate_export']",
            
            # Common button selectors
            "#export-pending-activations",
            ".export-pending-activations-btn",
            "button[data-action='export-activations']",
            ".export-activations-btn",
            ".export-btn",
            
            # Menu-based selectors
            ".dropdown-toggle[data-toggle='dropdown']",  # Drop-down menu button
            ".dropdown-menu a[href*='activation']",
            ".dropdown-menu a[href*='export']",
        ]
        
        xpath_selectors = [
            # Text-based XPath selectors
            "//button[contains(., 'Export')]",
            "//a[contains(., 'Export')]",
            "//button[contains(., 'Activation')]",
            "//a[contains(., 'Activation')]",
            "//button[contains(., 'Pending')]",
            "//a[contains(., 'Pending')]",
            "//span[contains(., 'Export')]/parent::button",
            "//span[contains(., 'Export')]/parent::a",
            "//a[normalize-space(text())='Export']",
            "//button[normalize-space(text())='Export']",
        ]
        
        # Try direct navigation first (most reliable)
        try:
            direct_url = driver.current_url.split('/agent')[0] + '/agent/reactivate_export/'
            sys.stderr.write(f"[callhub] Trying direct navigation to export page: {direct_url}\n")
            driver.get(direct_url)
            time.sleep(SHORT_WAIT_SECONDS)  # Reduced wait time
            
            # Check if we landed on a progress page
            progress_elements = driver.find_elements(By.CSS_SELECTOR, ".modal-dialog, .progress")
            if progress_elements or "Exporting Data" in driver.page_source:
                sys.stderr.write("[callhub] Direct navigation to export URL successful\n")
                return True
        except Exception as e:
            sys.stderr.write(f"[callhub] Direct navigation failed: {str(e)}\n")
            
        # Try each CSS selector
        for selector in export_selectors:
            try:
                sys.stderr.write(f"[callhub] Looking for export button with CSS selector: {selector}\n")
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                if elements:
                    for element in elements:
                        try:
                            # Click the element
                            element.click()
                            sys.stderr.write(f"[callhub] Clicked element: {selector}\n")
                            
                            # Wait for the export modal or progress indicator
                            try:
                                WebDriverWait(driver, SHORT_WAIT_SECONDS).until(
                                    EC.any_of(
                                        EC.visibility_of_element_located((By.CSS_SELECTOR, ".modal-dialog")),
                                        EC.visibility_of_element_located((By.CSS_SELECTOR, ".progress")),
                                        EC.title_contains("Export"),
                                        EC.url_contains("export")
                                    )
                                )
                                sys.stderr.write("[callhub] Export initiated successfully\n")
                                return True
                            except TimeoutException:
                                # If no success indicators, see if this click took us to a new page
                                if 'reactivate_export' in driver.current_url or 'export' in driver.current_url:
                                    sys.stderr.write("[callhub] Navigation to export URL successful\n")
                                    return True
                        except Exception as click_error:
                            sys.stderr.write(f"[callhub] Error clicking element: {str(click_error)}\n")
            except Exception as selector_error:
                continue
        
        # Try each XPath selector
        for xpath in xpath_selectors:
            try:
                sys.stderr.write(f"[callhub] Looking for export button with XPath: {xpath}\n")
                elements = driver.find_elements(By.XPATH, xpath)
                
                if elements:
                    for element in elements:
                        try:
                            # Click the element
                            element.click()
                            sys.stderr.write(f"[callhub] Clicked element: {xpath}\n")
                            
                            # Wait for indicators that export has started
                            try:
                                WebDriverWait(driver, SHORT_WAIT_SECONDS).until(
                                    EC.any_of(
                                        EC.visibility_of_element_located((By.CSS_SELECTOR, ".modal-dialog")),
                                        EC.visibility_of_element_located((By.CSS_SELECTOR, ".progress")),
                                        EC.title_contains("Export"),
                                        EC.url_contains("export")
                                    )
                                )
                                sys.stderr.write("[callhub] Export initiated successfully\n")
                                return True
                            except TimeoutException:
                                # If no success indicators, see if this click took us to a new page
                                if 'reactivate_export' in driver.current_url or 'export' in driver.current_url:
                                    sys.stderr.write("[callhub] Navigation to export URL successful\n")
                                    return True
                        except Exception as click_error:
                            sys.stderr.write(f"[callhub] Error clicking element: {str(click_error)}\n")
            except Exception as xpath_error:
                continue
        
        # If we couldn't find any export button, log the current page for debugging
        sys.stderr.write("[callhub] Could not find the export button. Current page source:\n")
        sys.stderr.write(f"Current URL: {driver.current_url}\n")
        sys.stderr.write(f"Page title: {driver.title}\n")
        
        return False
    except Exception as e:
        sys.stderr.write(f"[callhub] Error initiating export: {str(e)}\n")
        return False

def wait_for_export_completion(driver: webdriver.Chrome) -> Union[str, None]:
    """
    Wait for the export process to complete and return the download URL.
    
    Args:
        driver: WebDriver instance
        
    Returns:
        Download URL if export completed successfully, None otherwise
    """
    try:
        sys.stderr.write("[callhub] Waiting for export to complete...\n")
        
        # Wait for the export process to finish (look for success message or download link)
        try:
            # First wait for the modal to be fully visible
            WebDriverWait(driver, SHORT_WAIT_SECONDS).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".modal-dialog"))
            )
            
            # Then wait for the export to complete
            WebDriverWait(driver, WAIT_TIMEOUT_SECONDS).until(
                EC.any_of(
                    EC.text_to_be_present_in_element((By.ID, "stateid"), "Completed"),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/exports/']"))
                )
            )
            
            # Try to find the download link
            download_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/exports/']")
            if download_links:
                download_url = download_links[0].get_attribute("href")
                sys.stderr.write(f"[callhub] Found download URL: {download_url}\n")
                return download_url
            
            # If download link not found, check for the URL in JavaScript variables
            script = "return window.r_url || '';"
            redirect_url = driver.execute_script(script)
            if redirect_url and '/exports/' in redirect_url:
                sys.stderr.write(f"[callhub] Found download URL in JS: {redirect_url}\n")
                base_url = driver.current_url.split('/agent/')[0]
                return f"{base_url}{redirect_url}"
                
            sys.stderr.write("[callhub] Export completed but could not find download URL\n")
            return None
        except TimeoutException:
            sys.stderr.write("[callhub] Timed out waiting for export to complete\n")
            return None
            
    except Exception as e:
        sys.stderr.write(f"[callhub] Error waiting for export: {str(e)}\n")
        return None

def download_csv_file(driver: webdriver.Chrome, download_url: str) -> Union[str, None]:
    """
    Download the CSV file from the given URL.
    
    Args:
        driver: WebDriver instance
        download_url: URL to download the CSV from
        
    Returns:
        CSV content as a string if successful, None otherwise
    """
    try:
        sys.stderr.write(f"[callhub] Downloading CSV from: {download_url}\n")
        
        # Navigate to the download URL
        driver.get(download_url)
        
        # Wait a moment for the download to begin
        time.sleep(SHORT_WAIT_SECONDS / 2)  # Reduced wait time
        
        # Get the page content (should be CSV)
        content = driver.page_source
        
        # If content is HTML (not CSV), try to extract the CSV content
        if content.strip().startswith('<!DOCTYPE html>') or content.strip().startswith('<html'):
            # The CSV might be in a <pre> tag
            pre_elements = driver.find_elements(By.TAG_NAME, "pre")
            if pre_elements:
                content = pre_elements[0].text
            else:
                sys.stderr.write("[callhub] Downloaded content is HTML, not CSV\n")
                return None
        
        # Basic validation - check if it looks like CSV content
        if ',' in content and '\n' in content and content.count(',') > content.count('\n'):
            sys.stderr.write(f"[callhub] Successfully downloaded CSV ({len(content)} bytes)\n")
            return content
        else:
            sys.stderr.write("[callhub] Downloaded content does not appear to be CSV\n")
            return None
            
    except Exception as e:
        sys.stderr.write(f"[callhub] Error downloading CSV: {str(e)}\n")
        return None

def parse_activation_csv(csv_content: str) -> Dict:
    """
    Parse the CSV content to extract activation URLs and other information.
    
    Args:
        csv_content: CSV content as a string
        
    Returns:
        Dict with parsed activation data
    """
    if not csv_content:
        return {
            "isError": True, 
            "content": [{"type": "text", "text": "No CSV content to parse"}]
        }
    
    try:
        reader = csv.reader(StringIO(csv_content))
        
        # Extract the header row
        try:
            headers = next(reader)
        except StopIteration:
            return {
                "isError": True, 
                "content": [{"type": "text", "text": "CSV file is empty"}]
            }
        
        # Find the URL column index
        url_col = -1
        username_col = -1
        email_col = -1
        
        for i, header in enumerate(headers):
            h = header.lower()
            if "url" in h or "link" in h or "activation" in h:
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
            "headers": headers,
            "raw_csv": csv_content  # Include the raw CSV in case direct parsing is needed
        }
        
    except Exception as e:
        sys.stderr.write(f"[callhub] Exception in parse_activation_csv: {str(e)}\n")
        return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

def activate_agents_with_password(activation_data: List[Dict], password: str, account_name: Optional[str] = None) -> Dict:
    """
    Automate the activation of agents by visiting each activation URL and setting the provided password.

    Args:
        activation_data: List of activation data entries, each with at least 'url' field
        password: Password to set for all activating agents
        account_name: Optional account name (not used for this function, but included for consistency)

    Returns:
        Dict with results of activation attempts
    """
    if not SELENIUM_AVAILABLE:
        return {
            "isError": True,
            "content": [{"type": "text", "text": "Selenium is required for browser automation. Install with: pip install selenium webdriver-manager"}]
        }

    if not activation_data:
        return {
            "isError": True,
            "content": [{"type": "text", "text": "No activation data provided. Please first upload a CSV with activation URLs."}]
        }
        
    # CallHub requires passwords of at least 8 characters (based on UI validation)
    if not password or len(password) < 8:
        return {
            "isError": True,
            "content": [{
                "type": "text", 
                "text": "Password must be at least 8 characters long. CallHub requires passwords of at least 8 characters."
            }]
        }
    
    results = {
        "total": len(activation_data),
        "successful": 0,
        "failed": 0,
        "activation_results": []
    }
    
    # Launch the browser for automation
    with get_browser(headless=True, use_profile=False) as driver:
        sys.stderr.write(f"[callhub] Beginning activation of {len(activation_data)} agents with password: {password}\n")
        
        # Process each activation URL
        for i, activation in enumerate(activation_data):
            url = activation.get("url")
            username = activation.get("username", "Unknown")
            email = activation.get("email", "Unknown")
            
            if not url:
                sys.stderr.write(f"[callhub] Skipping activation {i+1}: No URL provided\n")
                results["failed"] += 1
                results["activation_results"].append({
                    "username": username,
                    "email": email,
                    "success": False,
                    "message": "Missing activation URL"
                })
                continue
                
            try:
                sys.stderr.write(f"[callhub] Processing activation {i+1}/{len(activation_data)}: {username} ({email})\n")
                
                # Go to activation URL
                driver.get(url)
                time.sleep(SHORT_WAIT_SECONDS / 2)  # Reduced wait time
                
                # Log the current URL to help debug
                sys.stderr.write(f"[callhub] Current URL: {driver.current_url}\n")
                
                # First try to find the password field by specific selectors from the HTML inspection
                password_field = None
                password_selectors = [
                    'input[name="new_password1"]',  # Exact match from the HTML
                    'input.set-password-input',     # Class selector from the HTML
                    'input[placeholder="Must be 8 characters"]',  # Placeholder text from the HTML
                    'input[type="password"]',      # Generic type selector
                    '*[id*="password"]',           # Any element with password in ID
                    '*[class*="password"]'         # Any element with password in class
                ]
                
                # Debug: Log the page source for troubleshooting
                sys.stderr.write(f"[callhub] Page URL: {driver.current_url}\n")
                sys.stderr.write(f"[callhub] Page title: {driver.title}\n")
                
                # Try JavaScript approach to set password (more reliable and faster)
                js_set_password = f"""
                var inputs = document.getElementsByTagName('input');
                var passwordField = null;
                
                // Find the password field
                for (var i = 0; i < inputs.length; i++) {{
                    var input = inputs[i];
                    if (input.type === 'password' || 
                        (input.name && input.name.toLowerCase().includes('password')) || 
                        (input.id && input.id.toLowerCase().includes('password')) || 
                        (input.className && input.className.toLowerCase().includes('password')) ||
                        (input.placeholder && input.placeholder.toLowerCase().includes('must be'))) {{
                        passwordField = input;
                        break;
                    }}
                }}
                
                // If we found a password field, set its value
                if (passwordField) {{
                    passwordField.value = "{password}";
                    return true;
                }}
                
                return false;
                """
                
                set_password_result = driver.execute_script(js_set_password)
                if set_password_result:
                    sys.stderr.write(f"[callhub] Successfully set password using JavaScript\n")
                    
                    # Try to find and click the submit button using JavaScript
                    js_click_submit = """
                    // Find potential submit buttons or elements that look like them
                    function findSubmitElement() {
                        // Look for inputs with type submit
                        var submitInputs = document.querySelectorAll('input[type="submit"]');
                        if (submitInputs.length > 0) return submitInputs[0];
                        
                        // Look for buttons
                        var buttons = document.getElementsByTagName('button');
                        for (var i = 0; i < buttons.length; i++) {
                            var btn = buttons[i];
                            if (btn.type === 'submit' || 
                                btn.textContent.toLowerCase().includes('done') ||
                                btn.textContent.toLowerCase().includes('submit') ||
                                btn.textContent.toLowerCase().includes('activate')) {
                                return btn;
                            }
                        }
                        
                        // Look for elements with 'done' text
                        var doneElements = document.querySelectorAll('.btn, .button, [role="button"]');
                        for (var i = 0; i < doneElements.length; i++) {
                            if (doneElements[i].textContent.toLowerCase().includes('done')) {
                                return doneElements[i];
                            }
                        }
                        
                        // Look for any input with value="Done"
                        var doneInputs = document.querySelectorAll('input[value="Done"]');
                        if (doneInputs.length > 0) return doneInputs[0];
                        
                        return null;
                    }
                    
                    var submitElement = findSubmitElement();
                    if (submitElement) {
                        submitElement.click();
                        return true;
                    }
                    
                    return false;
                    """
                    
                    click_result = driver.execute_script(js_click_submit)
                    if click_result:
                        sys.stderr.write(f"[callhub] Successfully clicked submit button using JavaScript\n")
                        time.sleep(SHORT_WAIT_SECONDS)
                        # Set password_field to a dummy value so we continue with checking for success
                        password_field = True
                    else:
                        # Try the traditional approach if JavaScript click didn't work
                        for selector in password_selectors:
                            try:
                                fields = driver.find_elements(By.CSS_SELECTOR, selector)
                                if fields:
                                    password_field = fields[0]
                                    sys.stderr.write(f"[callhub] Found password field with selector: {selector}\n")
                                    break
                            except Exception as e:
                                continue
                        
                        if password_field and password_field is not True:
                            password_field.clear()
                            password_field.send_keys(password)
                            sys.stderr.write(f"[callhub] Entered password for {username}\n")
                            
                            # Look for the Done button
                            done_button = None
                            submit_selectors = [
                                'input#agent-sign-up-button',
                                'input[value="Done"]',
                                'input[type="submit"]', 
                                'button[type="submit"]',
                                '.btn-primary',
                                '.btn-success'
                            ]
                            
                            for selector in submit_selectors:
                                try:
                                    buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                                    if buttons:
                                        done_button = buttons[0]
                                        break
                                except Exception as e:
                                    continue
                            
                            if done_button:
                                done_button.click()
                                sys.stderr.write(f"[callhub] Clicked Done button for {username}\n")
                                time.sleep(SHORT_WAIT_SECONDS)
                else:
                    sys.stderr.write(f"[callhub] Could not find password field with JavaScript\n")
                    
                    # Try traditional approach if JavaScript failed
                    for selector in password_selectors:
                        try:
                            fields = driver.find_elements(By.CSS_SELECTOR, selector)
                            if fields:
                                password_field = fields[0]
                                sys.stderr.write(f"[callhub] Found password field with selector: {selector}\n")
                                break
                        except Exception as e:
                            continue
                    
                    if password_field and password_field is not True:
                        password_field.clear()
                        password_field.send_keys(password)
                        sys.stderr.write(f"[callhub] Entered password for {username}\n")
                        
                        # Look for the Done button
                        done_button = None
                        submit_selectors = [
                            'input#agent-sign-up-button',
                            'input[value="Done"]',
                            'input[type="submit"]', 
                            'button[type="submit"]',
                            '.btn-primary',
                            '.btn-success'
                        ]
                        
                        for selector in submit_selectors:
                            try:
                                buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                                if buttons:
                                    done_button = buttons[0]
                                    break
                            except Exception as e:
                                continue
                        
                        if done_button:
                            done_button.click()
                            sys.stderr.write(f"[callhub] Clicked Done button for {username}\n")
                            time.sleep(SHORT_WAIT_SECONDS)
                
                # Check for success indicators or errors
                success = False
                page_source = driver.page_source.lower()
                
                # Success indicators
                success_indicators = ['success', 'activated', 'thank you', 'welcome', 'dashboard']
                for indicator in success_indicators:
                    if indicator in page_source:
                        success = True
                        break
                        
                # Check if we were redirected to the dashboard
                if 'dashboard' in driver.current_url:
                    success = True
                
                if success:
                    sys.stderr.write(f"[callhub] Successfully activated agent: {username} ({email})\n")
                    # Add this line to emit an event for individual agent activation
                    print(f"[CALLHUB-AGENT-ACTIVATED] {username} ({email}): SUCCESS")
                    results["successful"] += 1
                    results["activation_results"].append({
                        "username": username,
                        "email": email,
                        "success": True,
                        "message": "Successfully activated"
                    })
                else:
                    # Look for error messages
                    error_message = "Activation completed but no success confirmation found"
                    error_selectors = [
                        '.set-password-error',  # From the screenshot
                        '.error',
                        '.alert',
                        '.message'
                    ]
                    
                    for selector in error_selectors:
                        try:
                            error_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                            if error_elements and error_elements[0].text.strip():
                                error_message = error_elements[0].text.strip()
                                sys.stderr.write(f"[callhub] Found error: {error_message}\n")
                                break
                        except:
                            pass
                    
                    sys.stderr.write(f"[callhub] Activation may have failed for {username}: {error_message}\n")
                    # Add this line to emit an event for individual agent activation failure
                    print(f"[CALLHUB-AGENT-ACTIVATED] {username} ({email}): FAILED - {error_message}")
                    results["failed"] += 1
                    results["activation_results"].append({
                        "username": username,
                        "email": email,
                        "success": False,
                        "message": error_message
                    })
            except Exception as e:
                sys.stderr.write(f"[callhub] Error activating {username}: {str(e)}\n")
                results["failed"] += 1
                results["activation_results"].append({
                    "username": username,
                    "email": email,
                    "success": False,
                    "message": str(e)
                })
                
            # Brief pause between activations to avoid overloading the server
            time.sleep(0.5)  # Reduced from 1 second to 0.5 second
    
    # Summarize results
    success_rate = (results["successful"] / results["total"]) * 100 if results["total"] > 0 else 0
    sys.stderr.write(f"[callhub] Activation completed. Success: {results['successful']}/{results['total']} ({success_rate:.1f}%)\n")
    
    return {
        "success": True,
        "total_agents": results["total"],
        "successful_activations": results["successful"],
        "failed_activations": results["failed"],
        "success_rate": f"{success_rate:.1f}%",
        "message": f"Processed {results['total']} agent activations with {results['successful']} successful and {results['failed']} failed",
        "details": results["activation_results"]
    }

def process_local_activation_csv(file_path: str) -> Dict:
    """
    Process a local CSV file containing agent activation URLs.
    
    IMPORTANT: This is used when a user uploads a CSV to the conversation.
    Claude cannot read the uploaded file's contents directly - it only gets the filename.
    This function searches for that file in the user's local system and processes it.
    
    Args:
        file_path: Path or filename of the CSV file
        
    Returns:
        Dict with parsed activation data from the LOCAL file
    """
    # First check if the file exists directly
    if not os.path.isfile(file_path):
        # Try to find the file in common locations
        found_path = find_file(file_path)
        if found_path:
            file_path = found_path
        else:
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"Could not find file: {file_path}"}]
            }
    
    try:
        # Read the CSV file
        with open(file_path, 'r', encoding='utf-8') as f:
            csv_content = f.read()
        
        # Parse the CSV content
        return parse_activation_csv(csv_content)
    except Exception as e:
        return {
            "isError": True,
            "content": [{"type": "text", "text": f"Error reading or parsing CSV file: {str(e)}"}]
        }

def export_agent_activation_urls_browser(account_name: Optional[str] = None) -> Dict:
    """
    Generate and return a direct URL for exporting agent activation URLs.

    Args:
        account_name: The CallHub account name to use

    Returns:
        Dict with the export URL and instructions
    """
    if not SELENIUM_AVAILABLE:
        return {
            "isError": True,
            "content": [{"type": "text", "text": "Selenium is required for browser automation. Install with: pip install selenium webdriver-manager"}]
        }

    # Get the account configuration
    account, api_key, base_url = get_account_config(account_name)
    
    if not base_url:
        return {
            "isError": True,
            "content": [{"type": "text", "text": f"Invalid account configuration for '{account}'"}]
        }
    
    # Extract the domain from the base_url
    if '://' in base_url:
        domain = base_url.split('://')[1].split('/')[0]  # Get the domain part
    else:
        domain = base_url.split('/')[0]
    
    # Remove 'api-' prefix if present
    if domain.startswith('api-'):
        domain = domain[4:]  # Remove 'api-'
    
    # Construct the direct export URL - always using HTTPS
    export_url = f"https://{domain}/agent/#export"
    
    # Return the URL with instructions
    return {
        "success": True,
        "export_url": export_url,
        "instructions": [
            "1. Click the link below to open the Agents page in your browser:",
            f"   {export_url}",
            "2. If prompted, log in with your CallHub credentials",
            "3. Look for the 'Export Pending Activations' button on the page",
            "4. Click this button to start the export process",
            "5. Once complete, download the CSV file",
            "6. Upload the downloaded CSV file back to this conversation",
            "7. We'll automatically process the file and show you the activation data"
        ]
    }
