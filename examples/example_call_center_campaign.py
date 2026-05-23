#!/usr/bin/env python3
"""
Example script for creating a Call Center Campaign using the CallHub API integration.

This demonstrates how to structure the campaign data correctly and call the API.
"""

import json
from src.callhub.campaigns import create_call_center_campaign

# Example campaign data structure that conforms to CallHub's expected format
example_campaign = {
    "name": "GOTV Campaign Example",
    "phonebook_ids": ["YOUR_PHONEBOOK_ID"],  # Replace with actual phonebook IDs
    "callerid": "15551234567",  # Replace with an actual caller ID
    
    # Script structure as an array of objects with different types
    "script": [
        {
            "type": "12",  # Type 12 is for introductory/script text
            "script_text": "Hello, my name is {agent_name}. I'm calling from Example Organization about the upcoming election. We're checking in with voters to see if you have a plan to vote. Is this {first_name} {last_name}?"
        },
        {
            "type": "1",  # Type 1 is for multiple-choice questions
            "question": "Do you plan to vote in the upcoming election?",
            "choices": [
                {"answer": "Yes"},
                {"answer": "No"},
                {"answer": "Maybe"},
                {"answer": "Already Voted"}
            ]
        },
        {
            "type": "1",  
            "question": "How do you plan to vote?",
            "choices": [
                {"answer": "In person on election day"},
                {"answer": "Early voting"},
                {"answer": "Mail ballot"},
                {"answer": "Not sure yet"}
            ]
        },
        {
            "type": "3",  # Type 3 is for free-form text input
            "question": "Is there anything you need help with regarding voting?"
        },
        {
            "type": "12",
            "script_text": "Thank you for your time today! Your vote matters. Remember, election day is November 5, 2024. Have a great day!"
        }
    ],
    
    # Campaign settings
    "recording": True,
    "notes_required": True,
    "assign_all_agents": True,
    
    # Schedule settings
    "monday": True,
    "tuesday": True,
    "wednesday": True,
    "thursday": True,
    "friday": True,
    "saturday": True,
    "startingdate": "2025-05-15 09:00:00",  
    "expirationdate": "2025-11-05 20:00:00",
    "daily_start_time": "09:00",
    "daily_end_time": "20:00",
    "timezone": "America/New_York",
    
    # Call settings
    "use_contact_timezone": True,
    "block_cellphone": False,
    "block_litigators": True,
    "sort_order": "phonebook",
    
    # Call disposition options
    "call_dispositions": [
        "Will Vote", 
        "Will Not Vote", 
        "Already Voted",
        "Needs Information",
        "Wrong Number", 
        "Call Back Later",
        "Do Not Call",
        "Not Interested",
        "Busy", 
        "No Answer"
    ],
    "create_missing_dispositions": True
}

def main():
    """Run the example to create a Call Center Campaign."""
    print("Creating a Call Center Campaign using the CallHub API")
    print("Here's the campaign structure:")
    print(json.dumps(example_campaign, indent=2))
    
    print("\nTo actually create this campaign, modify this script to:")
    print("1. Replace 'phonebook_ids' with actual phonebook IDs")
    print("2. Replace 'callerid' with a valid caller ID")
    print("3. Uncomment the API call below")
    
    # Uncomment and modify to actually create the campaign
    # response = create_call_center_campaign({
    #     "accountName": "default",  # Replace with your account name if not using default
    #     "campaign_data": example_campaign
    # })
    # print("API Response:")
    # print(json.dumps(response, indent=2))

if __name__ == "__main__":
    main()
