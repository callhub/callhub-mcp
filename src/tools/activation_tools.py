"""Tool wrappers for Agent Activation operations."""
import sys
import datetime
from typing import Optional, List, Dict
from callhub.agent_activation_manual import (
    generate_export_url,
    process_activation_csv,
)
from callhub.csv_processor import (
    process_uploaded_csv,
    process_agent_activation_csv_from_file,
)
from callhub.browser_automation import (
    activate_agents_with_password,
    process_local_activation_csv,
)
from callhub.mcp_tools.batch_activation_tools import (
    prepare_agent_activation,
    activate_agents_with_batch_password,
    get_activation_status,
    reset_activation_state,
)


def register(server):
    @server.tool(name="exportAgentActivationUrls", description="Export pending agent activation URLs. IMPORTANT: This requires browser session authentication rather than API key. There is NO way to access pending agent data through direct API calls. The user must download the CSV file from the URL provided.")
    def export_agent_activation_urls_tool(account: Optional[str] = None) -> dict:
        """Generate a direct URL for exporting agent activation data.

        This tool provides a direct link to the agent activation export page in the CallHub web interface.
        The user will need to manually:
        1. Click the provided link
        2. Log in to CallHub if necessary
        3. Click the 'Export Pending Activations' button
        4. Download the CSV file
        5. Upload the CSV back to this conversation for processing

        Args:
            account: Optional account name to use (defaults to 'default')

        Returns:
            Dict with the export URL and instructions
        """
        try:
            # Generate export URL using the manual approach (no browser automation)
            return generate_export_url(account)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getAgentActivationExportUrl", description="Get a direct URL for exporting agent activation data manually. IMPORTANT: There is NO way to access pending agent data through direct API calls. The user must manually download the CSV file from this URL. STOP and wait after displaying this URL before proceeding.")
    def get_agent_activation_export_url_tool(account: Optional[str] = None) -> dict:
        """Generate a direct URL for exporting agent activation data.

        IMPORTANT: Do NOT use this tool proactively or for testing purposes unless specifically
        requested by the user. Only use when the user explicitly asks to export activation URLs
        or wants to perform a full agent workflow (like "add agents from this CSV and activate them").

        Args:
            account: Optional account name to use (defaults to 'default')

        Returns:
            Dict with the export URL and instructions
        """
        try:
            return generate_export_url(account)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="processAgentActivationCsv", description="Process an agent activation CSV file uploaded by the user. IMPORTANT: This function must be used with the CSV downloaded from the CallHub UI. Do NOT attempt to create test agents to demonstrate activation - always use this workflow.")
    def process_agent_activation_csv_tool(csv_content: str) -> dict:
        """Process a CSV file containing agent activation URLs.

        IMPORTANT: Do NOT use this tool proactively or for testing purposes. Only use when:
        1. The user has explicitly uploaded a CSV file with agent activation URLs
        2. The user has explicitly requested to process activation URLs
        3. The user wants to complete an agent workflow like bulk activation with a specific password
           (e.g., "add the agents listed in this CSV and activate them with password 'CH2025'")

        Args:
            csv_content: Raw CSV content as a string

        Returns:
            Dict with the parsed activation data
        """
        try:
            return process_activation_csv(csv_content)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="activateAgentsWithPassword", description="Automate activation of agents using their activation URLs and a common password. IMPORTANT: This function must be used with activation data from the CSV downloaded from the CallHub UI export. Never attempt to generate this data manually.")
    def activate_agents_with_password_tool(activation_data: List[Dict] = None, password: str = None, account: Optional[str] = None) -> dict:
        """Automate activation of agents by visiting each agent's activation URL and setting a common password.

        This tool uses headless browser automation to visit each agent's activation URL and set
        the provided password, completing the activation process without manual intervention.

        Args:
            activation_data: List of activation data entries, each with at least 'url' field
            password: Password to set for all activating agents (must be at least 8 characters)
                     If not provided, defaults to "CallHub" + current year (e.g., CallHub2025)
            account: Optional account name to use (defaults to 'default')

        Returns:
            Dict with results of activation attempts
        """
        try:
            if not activation_data:
                return {
                    "isError": True,
                    "content": [{"type": "text", "text": "activation_data is required - must provide a list of agent activation data"}]
                }

            # If no password provided, use the default scheme: CallHub + current year
            if not password:
                current_year = datetime.datetime.now().year
                password = f"CallHub{current_year}"
                sys.stderr.write(f"[callhub] Using default password scheme: {password}\n")

            # Check password length - CallHub requires at least 8 characters
            if len(password) < 8:
                return {
                    "isError": True,
                    "content": [
                        {"type": "text", "text": f"Password '{password}' is too short. CallHub requires passwords to be at least 8 characters long."},
                        {"type": "text", "text": "Please provide a longer password that meets the minimum requirements."}
                    ]
                }

            return activate_agents_with_password(activation_data, password, account)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="processLocalActivationCsv", description="Process a local CSV file containing agent activation URLs. IMPORTANT: When a user uploads a CSV, Claude can only see the filename but cannot read its contents. This tool searches for the file by name in the user's local system (Downloads, Desktop, etc.) and processes the actual local file.")
    def process_local_activation_csv_tool(file_path: str) -> dict:
        """
        Process a local CSV file containing agent activation URLs.

        IMPORTANT WORKFLOW:
        1. When a user uploads a CSV file to the conversation, Claude can only see the filename
           but CANNOT access the content of the uploaded file
        2. This tool uses the filename to search for the actual file on the user's local system
           (Downloads folder, Desktop, Documents, etc.)
        3. The actual CSV content is read and processed from the local file system, not from
           the uploaded file

        Args:
            file_path: Name or path of the CSV file containing agent activations

        Returns:
            Dict with the parsed activation data from the LOCAL file (not the uploaded file)
        """
        try:
            return process_local_activation_csv(file_path)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="processUploadedActivationCsv", description="IMPORTANT: When a user uploads a CSV file, Claude CANNOT read its contents directly. This tool takes the filename from the upload and searches for the actual file in the user's local system (Downloads, Desktop, etc.)")
    def process_uploaded_activation_csv_tool(file_path: str) -> dict:
        """
        IMPORTANT: Claude CANNOT read the content of uploaded files.

        When a user uploads a CSV file to the conversation:
        1. Claude can only see the filename but NOT the content
        2. This tool uses that filename to search for the actual file in standard locations
           (Downloads folder, Desktop, Documents, etc.)
        3. The CSV is processed from the local file system, NOT from the upload

        Args:
            file_path: Name or path of the CSV file

        Returns:
            Dict with parsed activation data from the LOCAL file (not directly from the upload)
        """
        try:
            return process_agent_activation_csv_from_file(file_path)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="processUploadedCsv", description="IMPORTANT: When a user uploads a CSV file, Claude CANNOT read its contents directly. This tool takes the filename from the upload and searches for the actual file in the user's local system (Downloads, Desktop, etc.)")
    def process_uploaded_csv_tool(file_path: str) -> dict:
        """
        IMPORTANT: Claude CANNOT read the content of uploaded files.

        When a user uploads a CSV file to the conversation:
        1. Claude can only see the filename but NOT the content
        2. This tool uses that filename to search for the actual file in standard locations
           (Downloads folder, Desktop, Documents, etc.)
        3. The CSV is processed from the local file system, NOT from the upload

        Args:
            file_path: Name or path of the CSV file

        Returns:
            Dict with parsed CSV data from the LOCAL file (not directly from the upload)
        """
        try:
            return process_uploaded_csv(file_path)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="prepareAgentActivation", description="Prepare for agent activation by setting up logs and showing instructions. IMPORTANT: Always call this first before activating agents.")
    def prepare_agent_activation_tool(
        account: str,
        password: str,
        activation_data: List[Dict],
        batch_size: int = 10
    ) -> dict:
        """
        Prepare for agent activation by setting up the log file and showing instructions.
        This MUST be called BEFORE actually activating agents to ensure the user knows
        where to look for progress updates.

        Args:
            account: CallHub account name
            password: Password to set for all agents (must be at least 8 characters)
            activation_data: List of activation data entries
            batch_size: Number of agents to process in each batch

        Returns:
            Dict with log file path and instructions
        """
        try:
            return prepare_agent_activation(
                account=account,
                password=password,
                activation_data=activation_data,
                batch_size=batch_size
            )
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="activateAgentsWithBatchPassword", description="Activate agents in batches with real-time progress updates. Supports large CSV files and provides resumability.")
    def activate_agents_with_batch_password_tool(
        account: str,
        password: str,
        activation_data: List[Dict],
        batch_size: int = 10
    ) -> dict:
        """
        Activate a large number of agents in batches with progress updates and resumability.
        This tool is designed to handle hundreds of agent activations while providing:
        1. Real-time progress updates during processing
        2. Batch processing to avoid overwhelming the server
        3. Resumability if the process is interrupted or the context window is exceeded

        Args:
            account: CallHub account name
            password: Password to set for all agents (must be at least 8 characters)
            activation_data: List of activation data entries
            batch_size: Number of agents to process in each batch

        Returns:
            Dict with activation results and progress information
        """
        try:
            return activate_agents_with_batch_password(
                account=account,
                password=password,
                activation_data=activation_data,
                batch_size=batch_size
            )
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getActivationStatus", description="Get the current status of an in-progress or completed agent activation job.")
    def get_activation_status_tool(account: str = None) -> dict:
        """
        Get the current status of an agent activation job.

        Use this tool to check:
        1. If an activation job is currently in progress
        2. How many agents have been activated so far
        3. When the last update occurred

        This is useful when activation was interrupted and you need to resume,
        or when dealing with a large number of agents being activated.

        Args:
            account: CallHub account name

        Returns:
            Dict with current status information
        """
        try:
            return get_activation_status(account)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="resetActivationState", description="Reset the progress tracking state for agent activation (for troubleshooting or restarting).")
    def reset_activation_state_tool(account: str = None) -> dict:
        """
        Reset the progress tracking state for agent activation.

        Use this tool if:
        1. You want to restart an activation process from the beginning
        2. You're having issues with a previous activation job
        3. You want to clear saved state from a completed job

        Args:
            account: CallHub account name

        Returns:
            Dict with reset result
        """
        try:
            return reset_activation_state(account)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}
