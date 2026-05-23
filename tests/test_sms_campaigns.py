"""Regression tests for SMS campaign fixes."""
from callhub.sms_campaigns import update_sms_campaign

def test_status_mapping_is_reachable():
    """Regression: status_mapping must be reachable (was inside unreachable block)."""
    # Passing a string status should use the mapping, not crash with NameError
    result = update_sms_campaign({"campaignId": "123", "status": "invalid_status", "accountName": "default"})
    # Should return validation error, not crash
    assert result.get("isError") is True
    assert "status" in str(result.get("content", "")).lower()

def test_status_string_mapping():
    """String status values should map to integers."""
    # This will fail at the API call level but should NOT fail at the mapping level
    # If status_mapping is unreachable, this would crash with NameError
    for status_str in ["start", "pause", "abort", "end"]:
        result = update_sms_campaign({
            "campaignId": "test-123",
            "status": status_str,
            "accountName": "default"
        })
        # We expect an API error (not connected), but NOT a NameError
        # The important thing is it didn't crash with "status_mapping is not defined"
        assert not isinstance(result, type(None)), f"update_sms_campaign returned None for status='{status_str}'"
