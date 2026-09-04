"""Tool-registration contract tests: the server imports cleanly, every tool
registers, aliases resolve without cluttering the listing, and the tools we
deliberately removed stay gone."""
import asyncio
import collections

import server as srv


def _tool_names():
    tools = asyncio.run(srv.server.list_tools())
    return [t.name for t in tools]


def test_server_registers_many_tools():
    names = _tool_names()
    assert len(names) >= 130


def test_no_duplicate_tool_names():
    names = _tool_names()
    dupes = [n for n, c in collections.Counter(names).items() if c > 1]
    assert not dupes, f"duplicate tool names: {dupes}"


def test_canonical_names_present():
    names = set(_tool_names())
    for expected in [
        "createContactList", "listContactLists", "getContactListCount",
        "createVoiceBroadcastCampaign", "createTextBroadcast",
        "addAgentsToCallCenterCampaign", "createP2pCampaign",
        "searchContacts", "addContactNotes", "addToDnc", "removeFromDnc",
        "deleteVoiceBroadcastCampaign", "shareCredits", "uploadMediaFile",
    ]:
        assert expected in names, f"missing canonical tool: {expected}"


def test_removed_selenium_tools_absent():
    names = set(_tool_names())
    for removed in [
        "activateAgentsWithPassword", "activateAgentsWithBatchPassword",
        "getActivationStatus", "resetActivationState", "prepareAgentActivation",
        "processLocalActivationCsv",
    ]:
        assert removed not in names, f"removed tool still registered: {removed}"


def test_aliases_are_hidden_but_map_to_real_tools():
    names = set(_tool_names())
    assert srv.TOOL_ALIASES, "expected backward-compatible aliases"
    for old, canonical in srv.TOOL_ALIASES.items():
        assert old not in names, f"alias {old} should not be listed"
        assert canonical in names, f"alias target {canonical} is not a real tool"


def test_known_aliases_point_to_expected_targets():
    assert srv.TOOL_ALIASES["createPhonebook"] == "createContactList"
    assert srv.TOOL_ALIASES["createVbCampaign"] == "createVoiceBroadcastCampaign"
    assert srv.TOOL_ALIASES["createSmsBroadcast"] == "createTextBroadcast"
    assert srv.TOOL_ALIASES["fetchAgents"] == "listAgents"
