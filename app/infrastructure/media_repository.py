"""Media repository — Supabase Storage operations."""

from __future__ import annotations

import os
from typing import Any

from app.infrastructure.supabase_client import get_service_client, has_supabase


BUCKET_NAME = "admin-media"


def list_media_files() -> list[dict]:
    """List all files in the admin-media bucket."""
    if not has_supabase():
        return []
    client = get_service_client()
    if not client:
        return []
    try:
        result = client.storage.from_(BUCKET_NAME).list()
        files = []
        for item in (result or []):
            if isinstance(item, dict) and item.get("name"):
                files.append({
                    "name": item["name"],
                    "id": item.get("id", ""),
                    "size": item.get("metadata", {}).get("size", 0),
                    "created_at": item.get("created_at", ""),
                })
        return files
    except Exception:
        return []


def upload_media(file_name: str, file_content: bytes, content_type: str = "image/jpeg") -> str | None:
    """Upload a file to the admin-media bucket. Returns public URL."""
    if not has_supabase():
        return None
    client = get_service_client()
    if not client:
        return None
    try:
        result = client.storage.from_(BUCKET_NAME).upload(
            path=file_name,
            file=file_content,
            file_options={"content-type": content_type},
        )
        if result:
            # Get public URL
            public_url = client.storage.from_(BUCKET_NAME).get_public_url(file_name)
            return public_url
    except Exception as e:
        print(f"Error uploading media: {e}")
    return None


def delete_media(file_name: str) -> bool:
    """Delete a file from the admin-media bucket."""
    if not has_supabase():
        return False
    client = get_service_client()
    if not client:
        return False
    try:
        client.storage.from_(BUCKET_NAME).remove([file_name])
        return True
    except Exception as e:
        print(f"Error deleting media: {e}")
        return False


def get_media_url(file_name: str) -> str | None:
    """Get the public URL for a media file."""
    if not has_supabase():
        return None
    client = get_service_client()
    if not client:
        return None
    try:
        return client.storage.from_(BUCKET_NAME).get_public_url(file_name)
    except Exception:
        return None
