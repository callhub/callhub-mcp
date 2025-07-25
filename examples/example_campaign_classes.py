#!/usr/bin/env python3
"""
Example script demonstrating CallHub MCP broadcast campaign functions.

Fixed version that focuses on SMS and Voice broadcast campaigns only.
Call center campaigns have their own dedicated example file.
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add the parent directory to the path so we can import the callhub package
sys.path.insert( 0 , os.path.abspath( os.path.join( os.path.dirname( __file__ ) , '..' , 'src' ) ) )

from src.callhub.sms_broadcasts import (list_sms_broadcasts)
from src.callhub.voice_broadcasts import (list_voice_broadcasts )


def print_response (response , title=None) :
    """Print formatted API response."""
    if title :
        print( f"\n=== {title} ===" )

    if response.get( "isError" ) :
        print( "ERROR:" , response.get( "content" , [ ] )[ 0 ].get( "text" , "Unknown error" ) )
        return False

    print( json.dumps( response , indent = 2 ) )
    return True


def sms_broadcast_example (account_name=None) :
    """Example using SMS broadcast MCP functions."""
    print( "\n=== SMS Broadcast MCP Functions ===\n" )

    response = list_sms_broadcasts( { "account" : account_name } )
    print_response( response , "SMS Broadcasts" )

    print( "\nExample SMS operations:" )
    print( """
    # Create SMS broadcast
    sms_data = {
        "name": "GOTV SMS Campaign",
        "phonebook_ids": ["3629573562324486094"],
        "message": "Don't forget to vote on November 5th!",
        "sender_id": "15551234567",
        "schedule_date": "2025-11-05T09:00:00Z"  # Optional
    }
    create_sms_broadcast({"account": account_name, **sms_data})

    # Update SMS status
    update_sms_broadcast({"account": account_name, "campaignId": "123", "status": "start"})
    """ )


def voice_broadcast_example (account_name=None) :
    """Example using voice broadcast MCP functions."""
    print( "\n=== Voice Broadcast MCP Functions ===\n" )

    response = list_voice_broadcasts( { "account" : account_name } )
    print_response( response , "Voice Broadcasts" )

    print( "\nExample voice operations:" )
    print( """
    # Note: No create_voice_broadcast function available in current implementation
    # Only list, update, and delete operations are supported

    # Update voice broadcast status
    update_voice_broadcast_campaign({"account": account_name, "campaignId": "123", "status": "start"})

    # Delete voice broadcast
    delete_voice_broadcast_campaign({"account": account_name, "campaignId": "123"})
    """ )


def main () :
    """Run broadcast examples only."""
    load_dotenv()

    account_name = sys.argv[ 1 ] if len( sys.argv ) > 1 else None
    print( f"Using account: {account_name or 'default'}" )
    print( "📢 Broadcast Campaign Examples (Call center example in separate file)" )

    # Run broadcast examples only
    sms_broadcast_example( account_name )
    voice_broadcast_example( account_name )

    print( "\n✅ Fixed: Now uses actual MCP functions instead of non-existent classes" )
    print( "✅ Added: create_sms_broadcast function for SMS campaigns" )
    print( "ℹ️  Note: Voice broadcasts only support list/update/delete (no create function)" )
    print( "ℹ️  Parameter names: SMS/Voice use 'account' parameter" )
    print( "📁 Call center examples: See example_call_center_campaign.py" )


if __name__ == "__main__" :
    main()
