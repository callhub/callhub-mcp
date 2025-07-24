#!/usr/bin/env python3
"""Test script for new CallHub MCP tools."""

import sys
sys.path.insert(0, '/Users/mitulrawat/Documents/GitHub/callhub-mcp/src')

from callhub.urls import createShortenedUrl, getShortenedUrl, listShortenedUrls
from callhub.api_utils import getApiSchema, getApiVersion, getApiStatus

def test_shortened_urls():
    """Test shortened URL endpoints."""
    print("\n=== Testing Shortened URL Tools ===\n")
    
    # Test listing shortened URLs
    print("1. Testing listShortenedUrls:")
    try:
        result = listShortenedUrls({"accountName": "default"})
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test creating a shortened URL
    print("\n2. Testing createShortenedUrl:")
    try:
        result = createShortenedUrl({
            "accountName": "default",
            "url": "https://www.callhub.io/features"
        })
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test getting a specific shortened URL (if we have a short code)
    print("\n3. Testing getShortenedUrl:")
    try:
        # This will fail unless you have a valid short code
        result = getShortenedUrl({
            "accountName": "default",
            "shortCode": "test123"
        })
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")

def test_api_utils():
    """Test API utilities endpoints."""
    print("\n=== Testing API Utilities Tools ===\n")
    
    # Test getting API schema
    print("1. Testing getApiSchema:")
    try:
        result = getApiSchema({"accountName": "default"})
        print(f"Result type: {type(result)}")
        if isinstance(result, dict):
            print(f"Keys: {list(result.keys())[:5]}...")  # Show first 5 keys
    except Exception as e:
        print(f"Error: {e}")
    
    # Test getting API version
    print("\n2. Testing getApiVersion:")
    try:
        result = getApiVersion({"accountName": "default"})
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test getting API status
    print("\n3. Testing getApiStatus:")
    try:
        result = getApiStatus({"accountName": "default"})
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing new CallHub MCP tools...")
    print("Note: These tests use the 'default' account.")
    
    test_shortened_urls()
    test_api_utils()
    
    print("\n=== Test Complete ===")
