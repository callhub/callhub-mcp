"""Tests for MCP tool registration completeness."""
import os
import re
from pathlib import Path


def _read_all_tool_sources():
    """Read all tool source files (server.py + tools/*.py)."""
    src_dir = Path(os.path.dirname(__file__)) / '..' / 'src'
    content = ""
    # Read server.py
    server_path = src_dir / 'server.py'
    if server_path.exists():
        content += server_path.read_text()
    # Read all tool modules
    tools_dir = src_dir / 'tools'
    if tools_dir.exists():
        for f in tools_dir.glob('*.py'):
            content += f.read_text()
    return content


def test_all_tool_names_unique():
    """Every @server.tool name must be unique."""
    content = _read_all_tool_sources()
    names = re.findall(r'@server\.tool\(name="([^"]+)"', content)
    duplicates = [n for n in names if names.count(n) > 1]
    assert not duplicates, f"Duplicate tool names: {set(duplicates)}"


def test_minimum_tool_count():
    """Server should register at least 140 tools."""
    content = _read_all_tool_sources()
    count = len(re.findall(r'@server\.tool\(', content))
    assert count >= 140, f"Expected at least 140 tools, found {count}"


def test_extended_api_tools_marked():
    """All extended API tools should have [Extended API] in description."""
    content = _read_all_tool_sources()
    extended_count = content.count('[Extended API]')
    assert extended_count >= 30, \
        f"Expected at least 30 [Extended API] markers, found {extended_count}"


def test_no_dsafdsf_function():
    """Regression: no debug function names should exist."""
    content = _read_all_tool_sources()
    assert 'dsafdsf' not in content, "Debug function name 'dsafdsf' still present"
