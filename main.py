"""Watch-Cartoons GUI – discover cartoons and playlists via YouTube Data API."""

from __future__ import annotations

import os
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any

from dotenv import load_dotenv

from youtube_client import YouTubeClient

# Exceptions raised by YouTubeClient
ClientError = (ValueError, RuntimeError)


class WatchCartoonsApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Watch-Cartoons")
        self.geometry("900x620")
        self.minsize(700, 500)

        self.client: YouTubeClient | None = None
        self._current_results: list[dict[str, Any]] = []
        self._mode = tk.StringVar(value="videos")

        self._build_ui()
        self._try_load_api_key()

    def _build_ui(self) -> None:
        # --- Top: API key ---
        top = ttk.Frame(self, padding=8)
        top.pack(fill=tk.X)

        ttk.Label(top, text="API Key:").pack(side=tk.LEFT)
        self.api_key_var = tk.StringVar()
        self.api_entry = ttk.Entry(top, textvariable=self.api_key_var, width=50, show="*")
        self.api_entry.pack(side=tk.LEFT, padx=(4, 8), fill=tk.X, expand=True)
        ttk.Button(top, text="Set Key", command=self._set_api_key).pack(side=tk.LEFT)

        # --- Search bar ---
        search_frame = ttk.Frame(self, padding=(8, 0, 8, 8))
        search_frame.pack(fill=tk.X)

        self.query_var = tk.StringVar()
        query_entry = ttk.Entry(search_frame, textvariable=self.query_var)
        query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        query_entry.bind("<Return>", lambda _e: self._run_search())

        ttk.Radiobutton(
            search_frame, text="Videos", variable=self._mode, value="videos"
        ).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(
            search_frame, text="Playlists", variable=self._mode, value="playlists"
        ).pack(side=tk.LEFT, padx=2)

        self.search_btn = ttk.Button(
            search_frame, text="Search", command=self._run_search
        )
        self.search_btn.pack(side=tk.LEFT, padx=(8, 0))

        # --- Results list ---
        mid = ttk.Frame(self, padding=(8, 0))
        mid.pack(fill=tk.BOTH, expand=True)

        columns = ("title", "channel", "id")
        self.tree = ttk.Treeview(
            mid, columns=columns, show="headings", selectmode="browse"
        )
        self.tree.heading("title", text="Title")
        self.tree.heading("channel", text="Channel")
        self.tree.heading("id", text="ID")
        self.tree.column("title", width=420, stretch=True)
        self.tree.column("channel", width=180, stretch=False)
        self.tree.column("id", width=140, stretch=False)

        scrollbar = ttk.Scrollbar(mid, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", self._on_double_click)

        # --- Detail / status area ---
        bottom = ttk.Frame(self, padding=8)
        bottom.pack(fill=tk.BOTH)

        self.detail = tk.Text(bottom, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.detail.pack(fill=tk.BOTH, expand=True)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W).pack(
            fill=tk.X, side=tk.BOTTOM
        )

        action_bar = ttk.Frame(self, padding=(8, 4))
        action_bar.pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Button(
            action_bar, text="Open Playlist Items", command=self._fetch_playlist_items
        ).pack(side=tk.LEFT)
        ttk.Button(
            action_bar, text="Video Details", command=self._show_video_details
        ).pack(side=tk.LEFT, padx=6)

    def _try_load_api_key(self) -> None:
        load_dotenv()
        key = os.getenv("YOUTUBE_API_KEY", "")
        if key:
            self.api_key_var.set(key)
            try:
                self.client = YouTubeClient(api_key=key)
                self.status_var.set("API key loaded from environment")
            except ClientError as exc:
                self.status_var.set(f"Failed to init client: {exc}")

    def _set_api_key(self) -> None:
        key = self.api_key_var.get().strip()
        if not key:
            messagebox.showwarning("API Key", "Please enter a YouTube Data API key.")
            return
        try:
            self.client = YouTubeClient(api_key=key)
            self.status_var.set("API key set successfully")
        except ClientError as exc:
            messagebox.showerror("API Key", str(exc))

    def _ensure_client(self) -> bool:
        if self.client is None:
            messagebox.showwarning(
                "API Key Required",
                "Please set a valid YouTube Data API key first.",
            )
            return False
        return True

    def _run_search(self) -> None:
        if not self._ensure_client():
            return
        query = self.query_var.get().strip()
        if not query:
            messagebox.showinfo("Search", "Enter a search query.")
            return

        self.search_btn.configure(state=tk.DISABLED)
        self.status_var.set("Searching…")
        self._clear_results()

        mode = self._mode.get()

        def worker() -> None:
            try:
                assert self.client is not None
                if mode == "playlists":
                    results = self.client.search_playlists(query)
                else:
                    results = self.client.search_videos(query)
                self.after(0, lambda: self._populate_results(results, mode))
            except ClientError as exc:
                msg = str(exc)
                self.after(0, lambda m=msg: self._search_failed(m))

        threading.Thread(target=worker, daemon=True).start()

    def _clear_results(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._current_results = []
        self._set_detail("")

    def _populate_results(self, results: list[dict[str, Any]], mode: str) -> None:
        self._current_results = results
        self.search_btn.configure(state=tk.NORMAL)

        if not results:
            self.status_var.set("No results found")
            return

        for item in results:
            snippet = item.get("snippet", {})
            title = snippet.get("title", "No title")
            channel = snippet.get("channelTitle", "Unknown")
            id_obj = item.get("id", {})
            if mode == "playlists":
                item_id = id_obj.get("playlistId", "")
            else:
                item_id = id_obj.get("videoId", "")
            self.tree.insert("", tk.END, values=(title, channel, item_id))

        self.status_var.set(f"Found {len(results)} {mode}")

    def _search_failed(self, message: str) -> None:
        self.search_btn.configure(state=tk.NORMAL)
        self.status_var.set("Search failed")
        messagebox.showerror("Search Error", message)

    def _selected_index(self) -> int | None:
        selection = self.tree.selection()
        if not selection:
            return None
        return self.tree.index(selection[0])

    def _on_select(self, _event: Any = None) -> None:
        idx = self._selected_index()
        if idx is None or idx >= len(self._current_results):
            return
        item = self._current_results[idx]
        snippet = item.get("snippet", {})
        desc = snippet.get("description", "") or "(no description)"
        text = (
            f"Title: {snippet.get('title', '')}\n"
            f"Channel: {snippet.get('channelTitle', '')}\n"
            f"Published: {snippet.get('publishedAt', '')}\n\n"
            f"{desc[:800]}"
        )
        self._set_detail(text)

    def _on_double_click(self, _event: Any = None) -> None:
        if self._mode.get() == "playlists":
            self._fetch_playlist_items()
        else:
            self._show_video_details()

    def _fetch_playlist_items(self) -> None:
        if not self._ensure_client():
            return
        idx = self._selected_index()
        if idx is None:
            messagebox.showinfo("Playlist", "Select a playlist first.")
            return

        item = self._current_results[idx]
        playlist_id = item.get("id", {}).get("playlistId")
        if not playlist_id:
            messagebox.showinfo(
                "Playlist",
                "Selected item is not a playlist. "
                "Switch to Playlists mode and search again.",
            )
            return

        self.status_var.set("Loading playlist items…")

        def worker() -> None:
            try:
                assert self.client is not None
                items = self.client.get_playlist_items(playlist_id)
                self.after(0, lambda: self._show_playlist_items(items, playlist_id))
            except ClientError as exc:
                msg = str(exc)
                self.after(
                    0,
                    lambda m=msg: messagebox.showerror("Playlist Error", m),
                )
                self.after(0, lambda: self.status_var.set("Failed to load playlist"))

        threading.Thread(target=worker, daemon=True).start()

    def _show_playlist_items(
        self, items: list[dict[str, Any]], playlist_id: str
    ) -> None:
        self._clear_results()
        self._mode.set("videos")
        converted: list[dict[str, Any]] = []
        for it in items:
            snippet = it.get("snippet", {})
            video_id = snippet.get("resourceId", {}).get("videoId") or it.get(
                "contentDetails", {}
            ).get("videoId", "")
            converted.append(
                {
                    "id": {"videoId": video_id},
                    "snippet": {
                        "title": snippet.get("title", "No title"),
                        "channelTitle": snippet.get("channelTitle", "Unknown"),
                        "publishedAt": snippet.get("publishedAt", ""),
                        "description": snippet.get("description", ""),
                    },
                }
            )
        self._populate_results(converted, "videos")
        self.status_var.set(f"Playlist {playlist_id}: {len(converted)} video(s)")

    def _show_video_details(self) -> None:
        if not self._ensure_client():
            return
        idx = self._selected_index()
        if idx is None:
            messagebox.showinfo("Video", "Select a video first.")
            return

        item = self._current_results[idx]
        video_id = item.get("id", {}).get("videoId")
        if not video_id:
            messagebox.showinfo("Video", "Selected item has no video ID.")
            return

        self.status_var.set("Loading video details…")

        def worker() -> None:
            try:
                assert self.client is not None
                details = self.client.get_video_details(video_id)
                self.after(0, lambda: self._display_video_details(details))
            except ClientError as exc:
                msg = str(exc)
                self.after(
                    0, lambda m=msg: messagebox.showerror("Video Error", m)
                )
                self.after(0, lambda: self.status_var.set("Failed to load video"))

        threading.Thread(target=worker, daemon=True).start()

    def _display_video_details(self, details: dict[str, Any] | None) -> None:
        if not details:
            self.status_var.set("Video not found")
            self._set_detail("Video not found.")
            return

        snippet = details.get("snippet", {})
        stats = details.get("statistics", {})
        content = details.get("contentDetails", {})

        text = (
            f"Title      : {snippet.get('title')}\n"
            f"Channel    : {snippet.get('channelTitle')}\n"
            f"Published  : {snippet.get('publishedAt')}\n"
            f"Duration   : {content.get('duration')}\n"
            f"Views      : {stats.get('viewCount', 'N/A')}\n"
            f"Likes      : {stats.get('likeCount', 'N/A')}\n\n"
            f"Description:\n{snippet.get('description', '')}"
        )
        self._set_detail(text)
        self.status_var.set("Video details loaded")

    def _set_detail(self, text: str) -> None:
        self.detail.configure(state=tk.NORMAL)
        self.detail.delete("1.0", tk.END)
        self.detail.insert(tk.END, text)
        self.detail.configure(state=tk.DISABLED)


def main() -> None:
    load_dotenv()
    app = WatchCartoonsApp()
    app.mainloop()


if __name__ == "__main__":
    main()
