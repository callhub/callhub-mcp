"""Shared test fixtures for CallHub MCP tests."""
import os
import sys
import pytest

# Add src to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Set dummy env vars so auth module doesn't fail
os.environ.setdefault('CALLHUB_DEFAULT_API_KEY', 'test-key-12345')
os.environ.setdefault('CALLHUB_DEFAULT_USERNAME', 'test@example.com')
os.environ.setdefault('CALLHUB_DEFAULT_BASE_URL', 'https://api-na1.callhub.io')
