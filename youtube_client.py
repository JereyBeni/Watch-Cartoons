"""YouTube Data API v3 client for cartoon-related video discovery."""

from __future__ import annotations

import os
from typing import Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class YouTubeClient:
    """Thin wrapper around the YouTube Data API v3."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "YouTube API key is required. "
                "Set YOUTUBE_API_KEY environment variable or pass api_key."
            )
        self.youtube = build("youtube", "v3", developerKey=self.api_key)

    def search(
        self,
        query: str,
        max_results: int = 10,
        channel_id: str | None = None,
        order: str = "relevance",
    ) -> list[dict[str, Any]]:
        """Search for videos matching the query.

        Args:
            query: Search terms (e.g. cartoon title).
            max_results: Maximum number of results to return (1-50).
            channel_id: Optional channel ID to restrict the search.
            order: Sort order (relevance, date, viewCount, rating, title).

        Returns:
            List of video result dictionaries.
        """
        request_params: dict[str, Any] = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": min(max(max_results, 1), 50),
            "order": order,
            "videoCategoryId": "1",  # Film & Animation (helps focus on cartoons)
        }
        if channel_id:
            request_params["channelId"] = channel_id

        try:
            response = self.youtube.search().list(**request_params).execute()
            return response.get("items", [])
        except HttpError as exc:
            raise RuntimeError(f"YouTube API search failed: {exc}") from exc

    def get_video_details(self, video_id: str) -> dict[str, Any] | None:
        """Retrieve detailed information for a single video."""
        try:
            response = (
                self.youtube.videos()
                .list(part="snippet,contentDetails,statistics", id=video_id)
                .execute()
            )
            items = response.get("items", [])
            return items[0] if items else None
        except HttpError as exc:
            raise RuntimeError(f"YouTube API video lookup failed: {exc}") from exc

    def get_channel_videos(
        self, channel_id: str, max_results: int = 10
    ) -> list[dict[str, Any]]:
        """List recent videos uploaded by a channel."""
        try:
            # First resolve the uploads playlist
            channels = (
                self.youtube.channels()
                .list(part="contentDetails", id=channel_id)
                .execute()
            )
            items = channels.get("items", [])
            if not items:
                return []

            uploads_playlist = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

            playlist_items = (
                self.youtube.playlistItems()
                .list(
                    part="snippet",
                    playlistId=uploads_playlist,
                    maxResults=min(max(max_results, 1), 50),
                )
                .execute()
            )
            return playlist_items.get("items", [])
        except HttpError as exc:
            raise RuntimeError(f"YouTube API channel lookup failed: {exc}") from exc
