"""Tests for MCP tool registration completeness."""
import os
import sys
import re

def test_all_tool_names_unique():
    """Every @server.tool name must be unique."""
    server_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'server.py')
    with open(server_path) as f:
        content = f.read()

    names = re.findall(r'@server\.tool\(name="([^"]+)"', content)
    duplicates = [n for n in names if names.count(n) > 1]
    assert not duplicates, f"Duplicate tool names: {set(duplicates)}"


def test_minimum_tool_count():
    """Server should register at least 140 tools."""
    server_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'server.py')
    with open(server_path) as f:
        content = f.read()

    count = len(re.findall(r'@server\.tool\(', content))
    assert count >= 140, f"Expected at least 140 tools, found {count}"


def test_extended_api_tools_marked():
    """All extended API tools should have [Extended API] in description."""
    server_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'server.py')
    with open(server_path) as f:
        content = f.read()

    extended_count = content.count('[Extended API]')
    assert extended_count >= 30, \
        f"Expected at least 30 [Extended API] markers, found {extended_count}"


def test_no_dsafdsf_function():
    """Regression: no debug function names should exist."""
    server_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'server.py')
    with open(server_path) as f:
        content = f.read()

    assert 'dsafdsf' not in content, "Debug function name 'dsafdsf' still present"
