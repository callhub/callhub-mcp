# callhub package
"""
CallHub API integration modules.
"""

from .auth import (
    load_all_credentials,
    save_credentials
)

from .sms_broadcast import SMSBroadcast
from .voice_broadcast import VoiceBroadcast

from .utils import (
    build_url,
    parse_input_fields,
    api_call
)

from .contacts import (
    list_contacts,
    get_contact,
    create_contact,
    create_contacts_bulk,
    update_contact,
    delete_contact,
    get_contact_fields,
    find_duplicate_contacts
)

from .phonebooks import (
    list_phonebooks,
    get_phonebook,
    create_phonebook,
    update_phonebook,
    delete_phonebook,
    add_contacts_to_phonebook,
    remove_contact_from_phonebook,
    get_phonebook_count,
    get_phonebook_contacts
)

from .tags import (
    list_tags,
    get_tag,
    create_tag,
    update_tag,
    delete_tag,
    add_tag_to_contact,
    remove_tag_from_contact
)

from .custom_fields import (
    list_custom_fields,
    get_custom_field,
    create_custom_field,
    update_custom_field,
    delete_custom_field,
    update_contact_custom_field
)

from .webhooks import (
    list_webhooks,
    get_webhook,
    create_webhook,
    delete_webhook
)

from .campaigns import (
    list_call_center_campaigns,
    update_call_center_campaign,
    delete_call_center_campaign,
    create_call_center_campaign
)

from .numbers import (
    list_rented_numbers,
    list_validated_numbers,
    rent_number
)
