"""Regression test for the DNC crash.

The server tool wrappers once called the DNC module functions with keyword
args (e.g. create_dnc_contact(account=..., dnc=...)), but those functions take
a single params dict -> every DNC tool raised TypeError when invoked. Call the
wrappers directly (the real code path) and assert they return a structured
validation error instead of crashing. Each has only optional parameters, so an
empty call short-circuits on a required-field check before any network I/O.
"""
import asyncio

import pytest

import server as srv


# (wrapper callable, substring expected in its required-field error)
WRAPPER_CASES = [
    (srv.create_dnc_contact_tool, "dnc"),
    (srv.update_dnc_contact_tool, "contactId"),
    (srv.delete_dnc_contact_tool, "contactId"),
    (srv.create_dnc_list_tool, "name"),
    (srv.update_dnc_list_tool, "listId"),
    (srv.delete_dnc_list_tool, "listId"),
]


@pytest.mark.parametrize("wrapper,needle", WRAPPER_CASES)
def test_dnc_wrapper_does_not_crash(wrapper, needle):
    result = wrapper()  # must not raise TypeError
    assert isinstance(result, dict)
    assert result.get("isError") is True
    assert needle.lower() in str(result).lower()


def test_suppression_list_wrapper_does_not_crash():
    result = srv.add_to_suppression_list_tool(listId="L1", records=[])
    assert isinstance(result, dict)
    assert result.get("isError") is True
    assert "records" in str(result).lower()


def test_old_dnc_alias_resolves_via_call_tool():
    # createDncContact was renamed to addToDnc; the old name must still resolve.
    result = asyncio.run(
        srv.server._tool_manager.call_tool("createDncContact", {})
    )
    assert "dnc" in str(result).lower()
