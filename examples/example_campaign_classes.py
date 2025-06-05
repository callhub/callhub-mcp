#!/usr/bin/env python3
"""
Example script demonstrating the use of Campaign, SMSBroadcast, and VoiceBroadcast classes.

This script shows how to initialize and use the Campaign, SMSBroadcast, and VoiceBroadcast classes
to interact with CallHub's campaign APIs.
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add the parent directory to the path so we can import the callhub package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.callhub import Campaign, SMSBroadcast, VoiceBroadcast

def print_response(response, title=None):
    """Print a formatted API response."""
    if title:
        print(f"\n=== {title} ===")

    if response.get("isError"):
        print("ERROR:", response.get("content", [])[0].get("text", "Unknown error"))
        return False

    print(json.dumps(response, indent=2))
    return True

def campaign_example(account_name=None):
    """Example usage of the Campaign class."""
    print("\n\n=== Campaign Class Example ===\n")

    # Initialize the Campaign class
    campaign = Campaign(account_name)
    print(f"Initialized Campaign class with account: {campaign.account_name}")

    # List call center campaigns
    print("\nListing call center campaigns...")
    response = campaign.list_call_center_campaigns()
    if not print_response(response, "Call Center Campaigns"):
        return

    # The rest of the examples would require actual campaign IDs
    print("\nTo create, update, or delete campaigns, you would need actual campaign IDs.")
    print("Example code for these operations:")
    print("""
    # Create a new call center campaign
    response = campaign.create_call_center_campaign(
        name="Example Campaign",
        phonebook_ids=["phonebook-id-1", "phonebook-id-2"],
        script_id="script-id",
        team_id="team-id",
        caller_id="caller-id",
        agent_ids=["agent-id-1", "agent-id-2"]
    )

    # Update a call center campaign
    response = campaign.update_call_center_campaign(
        campaign_id="campaign-id",
        status="pause"  # Valid values: "pause", "resume", "stop", "restart"
    )

    # Delete a call center campaign
    response = campaign.delete_call_center_campaign(
        campaign_id="campaign-id"
    )
    """)

def sms_broadcast_example(account_name=None):
    """Example usage of the SMSBroadcast class."""
    print("\n\n=== SMSBroadcast Class Example ===\n")

    # Initialize the SMSBroadcast class
    sms_broadcast = SMSBroadcast(account_name)
    print(f"Initialized SMSBroadcast class with account: {sms_broadcast.account_name}")

    # List SMS broadcast campaigns
    print("\nListing SMS broadcast campaigns...")
    response = sms_broadcast.list_sms_broadcasts()
    if not print_response(response, "SMS Broadcast Campaigns"):
        return

    # The rest of the examples would require actual campaign IDs
    print("\nTo create, update, or delete SMS broadcast campaigns, you would need actual campaign IDs.")
    print("Example code for these operations:")
    print("""
    # Create a new SMS broadcast campaign
    response = sms_broadcast.create_sms_broadcast(
        name="Example SMS Broadcast",
        phonebook_ids=["phonebook-id-1", "phonebook-id-2"],
        message="Hello, this is a test message!",
        sender_id="sender-id",
        schedule_date="2023-06-01T12:00:00Z"  # Optional
    )

    # Update an SMS broadcast campaign
    response = sms_broadcast.update_sms_broadcast(
        campaign_id="campaign-id",
        status="start"  # Valid values: "start", "pause", "abort", "end" or 1-4
    )

    # Delete an SMS broadcast campaign
    response = sms_broadcast.delete_sms_broadcast(
        campaign_id="campaign-id"
    )
    """)

def voice_broadcast_example(account_name=None):
    """Example usage of the VoiceBroadcast class."""
    print("\n\n=== VoiceBroadcast Class Example ===\n")

    # Initialize the VoiceBroadcast class
    voice_broadcast = VoiceBroadcast(account_name)
    print(f"Initialized VoiceBroadcast class with account: {voice_broadcast.account_name}")

    # List voice broadcast campaigns
    print("\nListing voice broadcast campaigns...")
    response = voice_broadcast.list_voice_broadcasts()
    if not print_response(response, "Voice Broadcast Campaigns"):
        return

    # The rest of the examples would require actual campaign IDs
    print("\nTo create, update, or delete voice broadcast campaigns, you would need actual campaign IDs.")
    print("Example code for these operations:")
    print("""
    # Create a new voice broadcast campaign
    response = voice_broadcast.create_voice_broadcast(
        name="Example Voice Broadcast",
        phonebook_ids=["phonebook-id-1", "phonebook-id-2"],
        audio_file_id="audio-file-id",
        caller_id="caller-id",
        schedule_date="2023-06-01T12:00:00Z"  # Optional
    )

    # Update a voice broadcast campaign
    response = voice_broadcast.update_voice_broadcast(
        campaign_id="campaign-id",
        status="start"  # Valid values: "start", "pause", "abort", "end" or 1-4
    )

    # Delete a voice broadcast campaign
    response = voice_broadcast.delete_voice_broadcast(
        campaign_id="campaign-id"
    )
    """)

def main():
    """Main function to run the examples."""
    load_dotenv()  # Load environment variables from .env file

    # Get the account name from command line arguments or use None for default
    account_name = sys.argv[1] if len(sys.argv) > 1 else None

    # Run the examples
    campaign_example(account_name)
    sms_broadcast_example(account_name)
    voice_broadcast_example(account_name)

if __name__ == "__main__":
    main()
