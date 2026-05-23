"""Tool wrappers for Media File operations."""
from typing import Optional
from callhub.campaigns import (
    get_media_files,
    upload_media_file,
)


def register(server):
    @server.tool(name="getMediaFiles", description="[Extended API] Retrieve a list of media files (audio, images, videos) uploaded to CallHub. Supports pagination.")
    def get_media_files_tool(
        account: Optional[str] = None,
        page: Optional[int] = None,
        pageSize: Optional[int] = None,
        file_type: Optional[str] = None, # 'audio', 'image', 'video'
        search: Optional[str] = None # Search by file name
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if page is not None:
                params["page"] = page
            if pageSize is not None:
                params["pageSize"] = pageSize
            if file_type:
                params["file_type"] = file_type
            if search:
                params["search"] = search

            # Assuming a function `list_media_files` exists in `callhub.media`
            return get_media_files(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}

    @server.tool(name="uploadMediaFile", description="Upload a media file to CallHub from a local file path. Supported formats: .mp3, .wav, .ogg, .mp4, .mov, .3gp, .3gpp, .jpg, .jpeg, .png, .gif. Returns media_file_id (sync) or job_id (async for video/GIF).")
    def upload_media_file_tool(
        account: Optional[str] = None,
        file_path: str = None,
        name: Optional[str] = None,
        generate_gif: Optional[bool] = None,
    ) -> dict:
        try:
            params = {}
            if account:
                params["accountName"] = account
            if file_path:
                params["file_path"] = file_path
            if name is not None:
                params["name"] = name
            if generate_gif is not None:
                params["generate_gif"] = generate_gif
            return upload_media_file(params)
        except Exception as e:
            return {"isError": True, "content": [{"type": "text", "text": str(e)}]}
