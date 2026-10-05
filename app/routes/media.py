"""Media library routes."""

from __future__ import annotations

from typing import Any

from fasthtml.common import Div
from starlette.responses import JSONResponse

try:
    from ..infrastructure.media_repository import list_media_files, upload_media, delete_media
    from ..presentation.page_helpers import oob_alert, toast_fragment
    from ..presentation.shell import page_frame
    from ..presentation.pages.media import media_page, media_picker_modal_fragment
except ImportError:
    from app.infrastructure.media_repository import list_media_files, upload_media, delete_media
    from app.presentation.page_helpers import oob_alert, toast_fragment
    from app.presentation.shell import page_frame
    from app.presentation.pages.media import media_page, media_picker_modal_fragment


def register_media_routes(app: Any) -> None:

    @app.get("/media")
    def media_list():
        files = list_media_files()
        return page_frame(*media_page(files), current="/media", title="Media")

    @app.get("/media/picker-modal")
    def media_picker_modal():
        """HTMX: return media picker gallery for insertion into forms."""
        files = list_media_files()
        return media_picker_modal_fragment(files)

    @app.post("/media/upload")
    def media_upload(req=None, session=None, file: Any = None):
        """HTMX: upload a media file."""
        if not file:
            return oob_alert("No file provided.", variant="danger", target="media-upload-result"), toast_fragment("No file provided.", variant="danger")

        try:
            from app.infrastructure.audit_repository import log_activity
            content = file.file.read()
            url = upload_media(file.filename, content, file.content_type or "image/jpeg")
            if url:
                log_activity(req, session, "UPLOAD_MEDIA", "media", str(file.filename), f"Uploaded media file '{file.filename}'")
                return oob_alert("File uploaded successfully to storage!", variant="success", target="media-upload-result"), toast_fragment(f"Uploaded '{file.filename}' to storage!", variant="success")
        except Exception as e:
            print(f"Error uploading media: {e}")

        return oob_alert("Upload failed. Please check connection.", variant="danger", target="media-upload-result"), toast_fragment("Upload failed. Please check storage connection.", variant="danger")

    @app.post("/media/delete")
    def media_delete(req=None, session=None, file_name: str = ""):
        """HTMX: delete a media file — returns empty HTML so card is removed via outerHTML swap."""
        if not file_name:
            return JSONResponse({"error": "Missing file_name"}, status_code=400)
        from app.infrastructure.audit_repository import log_activity
        success = delete_media(file_name)
        if success:
            log_activity(req, session, "DELETE_MEDIA", "media", str(file_name), f"Deleted media file '{file_name}'")
            # Empty Div replaces the card (outerHTML swap removes it); toast confirms action
            return Div(), toast_fragment(f"'{file_name}' deleted.", variant="success")
        return oob_alert("Failed to delete file.", variant="danger", target="media-upload-result"), toast_fragment("Failed to delete file.", variant="danger")
