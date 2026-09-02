"""Regressions for the Greptile PR #6 findings: server tool wrappers must pass
the parameter keys their module functions actually read, and uploadMediaFile
must confine reads to an approved directory."""
import os

import server as srv


def test_media_wrapper_maps_pagination_and_filters(monkeypatch):
    captured = {}
    monkeypatch.setattr(srv, "get_media_files", lambda p: captured.update(p) or {})
    srv.get_media_files_tool(account="acct", page=3, pageSize=10, file_type="audio", search="promo")
    assert captured["accountName"] == "acct"
    assert captured["limit"] == 10
    assert captured["offset"] == 20          # (page-1) * pageSize
    assert captured["media_type"] == "audio"
    assert captured["name"] == "promo"
    # The old, ignored keys must not be sent.
    for stale in ("page", "pageSize", "file_type", "search"):
        assert stale not in captured


def test_export_wrapper_passes_campaign_id(monkeypatch):
    captured = {}
    monkeypatch.setattr(srv, "export_power_campaign", lambda p: captured.update(p) or {})
    srv.export_power_campaign_tool(account="acct", campaign_id="123")
    assert captured["campaign_id"] == "123"   # module reads campaign_id, not campaignId
    assert captured["accountName"] == "acct"


def test_duplicate_vb_wrapper_passes_account(monkeypatch):
    captured = {}
    monkeypatch.setattr(srv, "duplicate_vb_campaign", lambda p: captured.update(p) or {})
    srv.duplicate_vb_campaign_tool(account="acct", campaign_id=7)
    assert captured["account"] == "acct"      # module reads account, not accountName
    assert captured["campaignId"] == 7


def test_upload_media_disabled_without_media_dir(monkeypatch):
    # With no approved directory configured, media upload is disabled entirely
    # (no host-wide default root).
    monkeypatch.delenv("CALLHUB_MEDIA_DIR", raising=False)
    result = srv.upload_media_file_tool(file_path="/etc/hosts")
    assert result.get("isError") is True
    assert "not enabled" in str(result).lower()


def test_upload_media_file_refuses_outside_approved_dir(tmp_path, monkeypatch):
    # A file outside the approved directory is refused even when one is set.
    monkeypatch.setenv("CALLHUB_MEDIA_DIR", str(tmp_path))
    outside = tmp_path.parent / "outside.png"
    outside.write_text("x")
    result = srv.upload_media_file_tool(file_path=str(outside))
    assert result.get("isError") is True
    assert "outside the approved upload directory" in str(result).lower()


def test_upload_media_file_allows_inside_approved_dir(tmp_path, monkeypatch):
    # A file inside the approved directory passes confinement, then is rejected
    # on extension (proving confinement let it through).
    monkeypatch.setenv("CALLHUB_MEDIA_DIR", str(tmp_path))
    f = tmp_path / "note.txt"
    f.write_text("x")
    result = srv.upload_media_file_tool(file_path=str(f))
    assert result.get("isError") is True
    assert "unsupported file extension" in str(result).lower()
