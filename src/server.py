#!/usr/bin/env python3
"""CallHub MCP Server - Auto-builds dependencies if needed"""

import sys
from pathlib import Path

import logging
logger = logging.getLogger("callhub")
# Add server/lib to Python path
server_dir = Path( __file__ ).parent
lib_path = server_dir / "lib"
if lib_path.exists() :
    sys.path.insert( 0 , str( lib_path ) )


# Try to import required packages
def check_dependencies () :
    """Check if all dependencies are available"""
    try :
        import mcp
        import pydantic
        import dotenv
        import requests
        import urllib3
        return True
    except ImportError as e :
        logger.info( f"⚠️  Missing dependency: {e}" )
        return False


def build_dependencies () :
    """Build dependencies into server/lib"""
    import subprocess
    import shutil

    logger.info( "📦 Installing dependencies..." )

    project_root = Path( __file__ ).parent.parent
    lib_path = Path( __file__ ).parent / "lib"

    # Clean and create lib directory
    if lib_path.exists() :
        shutil.rmtree( lib_path )
    lib_path.mkdir( parents = True )

    # Install dependencies
    requirements_file = project_root / "requirements.txt"
    if requirements_file.exists() :
        subprocess.run( [ sys.executable , "-m" , "pip" , "install" , "--target" , str( lib_path ) , "-r" ,
            str( requirements_file ) ] , check = True,stdout=sys.stderr, stderr=sys.stderr )
        logger.info( "✅ Dependencies installed!" )
        return True
    else :
        logger.info( "❌ requirements.txt not found!" )
        return False


# Check and build if needed
if not check_dependencies() :
    logger.info( "🔧 Dependencies missing. Building..." )
    if build_dependencies() :
        # Add lib to path again after building
        sys.path.insert( 0 , str( lib_path ) )

        # Verify dependencies are now available
        if not check_dependencies() :
            logger.info( "❌ Failed to install dependencies!" )
            sys.exit( 1 )
    else :
        sys.exit( 1 )


from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load .env (for CALLHUB_ACCOUNT, etc.) before importing tool modules
load_dotenv()

# Initialize the MCP server
server = FastMCP(name="callhub-mcp-py")

# Register all tool modules
from tools import (
    account_tools,
    agent_tools,
    team_tools,
    contact_tools,
    phonebook_tools,
    tag_tools,
    custom_field_tools,
    webhook_tools,
    campaign_tools,
    vb_tools,
    sms_tools,
    p2p_tools,
    relational_tools,
    dnc_tools,
    number_tools,
    user_tools,
    media_tools,
    template_tools,
    url_tools,
    activation_tools,
)

for module in [
    account_tools,
    agent_tools,
    team_tools,
    contact_tools,
    phonebook_tools,
    tag_tools,
    custom_field_tools,
    webhook_tools,
    campaign_tools,
    vb_tools,
    sms_tools,
    p2p_tools,
    relational_tools,
    dnc_tools,
    number_tools,
    user_tools,
    media_tools,
    template_tools,
    url_tools,
    activation_tools,
]:
    module.register(server)


if __name__ == "__main__":
    server.run()
