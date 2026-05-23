"""Tool wrappers for URL Shortening and API Schema operations."""
from typing import Optional
from callhub.urls import (
    get_shortened_url,
    list_shortened_urls,
)
from callhub.api_utils import getApiSchema


def register(server):
    @server.tool(name="getShortenedUrl", description="[Extended API] Get details of a shortened URL by its short code.")
    def get_shortened_url_tool(
        account: Optional[str] = None,
        shortCode: Optional[str] = None
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if shortCode:
                params["shortCode"] = shortCode

            return get_shortened_url(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="listShortenedUrls", description="[Extended API] List all shortened URLs with optional pagination.")
    def list_shortened_urls_tool(
        account: Optional[str] = None,
        page: Optional[int] = None,
        pageSize: Optional[int] = None
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if page is not None:
                params["page"] = page
            if pageSize is not None:
                params["pageSize"] = pageSize

            return list_shortened_urls(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="getApiSchema", description="[Extended API] Get the complete API schema documentation.")
    def get_api_schema_tool(
        account: Optional[str] = None
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account

            return getApiSchema(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}
