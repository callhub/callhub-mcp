"""
Logging module for CallHub MCP.

This module handles all logging for the CallHub MCP, including:
- Configurable log levels
- Log file rotation
- Console output formatting
- File output formatting
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional

# Default log format
DEFAULT_FORMAT = "[callhub] %(asctime)s - %(levelname)s - %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Default log directory - use a relative path within the project directory
DEFAULT_LOG_DIR = "logs"

class CallHubLogger:
    """Logger for CallHub MCP."""
    
    def __init__(self):
        """Initialize the logger."""
        self.logger = logging.getLogger("callhub")
        self.log_file = None
        self.debug_mode = False
        self.console_handler = None
        self.file_handler = None
        
        # Set up the logger
        self.setup()
    
    def get_log_directory(self, log_dir=None):
        """
        Get the log directory path, ensuring it's a valid, writable location.
        
        Args:
            log_dir: Directory specified by the user, or None to use default
            
        Returns:
            str: Path to the log directory
        """
        # If log_dir is specified, try to use it
        if log_dir:
            return log_dir
            
        # Try project directory first
        try:
            # Get the directory where this file is located
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up to the src directory
            src_dir = os.path.dirname(current_dir)
            # Go up to the project root
            project_dir = os.path.dirname(src_dir)
            
            # Try to create logs directory in project root
            logs_dir = os.path.join(project_dir, DEFAULT_LOG_DIR)
            # Test if we can write to this directory by creating it
            os.makedirs(logs_dir, exist_ok=True)
            return logs_dir
        except (OSError, PermissionError):
            # If we can't write to project directory, try user home directory
            pass
            
        # Fallback to user home directory
        home_dir = os.path.expanduser("~")
        logs_dir = os.path.join(home_dir, ".callhub", "logs")
        
        return logs_dir
    
    def setup(self, 
              level: Optional[str] = None, 
              log_dir: Optional[str] = None,
              log_to_file: bool = True,
              log_to_console: bool = True,
              max_file_size: int = 10 * 1024 * 1024,  # 10 MB
              backup_count: int = 5):
        """
        Set up the logger with the specified configuration.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: Directory to store log files
            log_to_file: Whether to log to file
            log_to_console: Whether to log to console
            max_file_size: Maximum log file size in bytes before rotation
            backup_count: Number of backup log files to keep
        """
        # Reset logger
        self.logger.handlers = []
        self.logger.setLevel(logging.INFO)  # Default level
        
        # Determine log level from environment or parameter
        log_level = level or os.environ.get("LOG_LEVEL", "INFO")
        numeric_level = getattr(logging, log_level.upper(), None)
        if not isinstance(numeric_level, int):
            numeric_level = logging.INFO
            print(f"Invalid log level: {log_level}, using INFO", file=sys.stderr)
        
        self.logger.setLevel(numeric_level)
        
        # Set debug mode
        self.debug_mode = numeric_level == logging.DEBUG
        
        # Create formatters
        console_formatter = logging.Formatter(DEFAULT_FORMAT, DEFAULT_DATE_FORMAT)
        file_formatter = logging.Formatter(DEFAULT_FORMAT, DEFAULT_DATE_FORMAT)
        
        # Console handler
        if log_to_console:
            self.console_handler = logging.StreamHandler(sys.stderr)
            self.console_handler.setFormatter(console_formatter)
            self.logger.addHandler(self.console_handler)
        
        # File handler (with rotation)
        if log_to_file:
            try:
                # Get appropriate log directory
                log_directory = self.get_log_directory(log_dir)
                
                # Create log directory if it doesn't exist
                os.makedirs(log_directory, exist_ok=True)
                
                # Create log file name with date
                current_date = datetime.now().strftime("%Y-%m-%d")
                log_file = os.path.join(log_directory, f"callhub_{current_date}.log")
                self.log_file = log_file
                
                # Set up rotating file handler
                self.file_handler = RotatingFileHandler(
                    log_file, 
                    maxBytes=max_file_size, 
                    backupCount=backup_count
                )
                self.file_handler.setFormatter(file_formatter)
                self.logger.addHandler(self.file_handler)
                
                self.logger.info(f"Log file: {log_file}")
            except (OSError, PermissionError) as e:
                # If we can't create a log file, just log to console
                self.logger.warning(f"Could not create log file: {e}. Logging to console only.")
                self.log_file = None
    
    def get_logger(self):
        """Get the configured logger."""
        return self.logger
    
    def set_level(self, level: str):
        """
        Set the log level.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        numeric_level = getattr(logging, level.upper(), None)
        if not isinstance(numeric_level, int):
            self.logger.warning(f"Invalid log level: {level}, ignoring")
            return
        
        self.logger.setLevel(numeric_level)
        self.debug_mode = numeric_level == logging.DEBUG
        self.logger.info(f"Log level set to {level}")
    
    def enable_debug(self):
        """Enable debug mode (sets log level to DEBUG)."""
        self.set_level("DEBUG")
    
    def disable_debug(self):
        """Disable debug mode (sets log level to INFO)."""
        self.set_level("INFO")

# Create a global logger instance
_logger_instance = CallHubLogger()

# Export the logger for use in other modules
logger = _logger_instance.get_logger()

# Export helper functions
def get_logger():
    """Get the configured logger."""
    return logger

def setup_logging(level=None, log_dir=None, log_to_file=True, log_to_console=True):
    """Set up logging with the specified configuration."""
    _logger_instance.setup(level, log_dir, log_to_file, log_to_console)

def set_log_level(level):
    """Set the log level."""
    _logger_instance.set_level(level)

def enable_debug():
    """Enable debug mode."""
    _logger_instance.enable_debug()

def disable_debug():
    """Disable debug mode."""
    _logger_instance.disable_debug()

def is_debug_enabled():
    """Check if debug mode is enabled."""
    return _logger_instance.debug_mode

# Initialize logging from environment variables
setup_logging()
