"""Watch-Cartoons GUI – XP-style interface with 2005 YouTube player."""

from __future__ import annotations

import os
import threading
import tkinter as tk
import webbrowser
from tkinter import messagebox, ttk
from typing import Any

from dotenv import load_dotenv

from youtube_client import YouTubeClient

# Exceptions raised by YouTubeClient
ClientError = (ValueError, RuntimeError)

# --- Windows XP / dark theme palette (inspired by xp-layer) ---
BG = "#1e1e1e"
BG_PANEL = "#2a2a2a"
BG_LIST = "#252526"
HEADER_BG = "#003399"  # classic XP title-bar blue
HEADER_FG = "#ffffff"
ACCENT = "#3a6ea5"
FG = "#e0e0e0"
FG_DIM = "#9a9a9a"
SELECT_BG = "#0a64a8"
BORDER = "#3c3c3c"
STATUS_BG = "#1a1a1a"

# 2005 YouTube player colours
YT_CHROME = "#cccccc"
YT_CHROME_DARK = "#999999"
YT_VIDEO_BG = "#000000"
YT_RED = "#cc0000"
YT_TEXT = "#333333"


class YouTube2005Player(tk.Frame):
    """Retro player chrome modelled on the 2005 YouTube Flash player."""

    def __init__(self, master: tk.Misc, **kwargs: Any) -> None:
        super().__init__(master, bg=YT_CHROME, **kwargs)
        self._video_id: str | None = None
        self._title = "No video selected"
        self._playing = False

        # Outer silver bezel
        outer = tk.Frame(self, bg=YT_CHROME_DARK, bd=2, relief=tk.RAISED)
        outer.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Title bar (old YouTube style)
        title_bar = tk.Frame(outer, bg="#eeeeee", height=22)
        title_bar.pack(fill=tk.X)
        title_bar.pack_propagate(False)
        self.title_label = tk.Label(
            title_bar,
            text="YouTube - Broadcast Yourself",
            bg="#eeeeee",
            fg=YT_TEXT,
            font=("Tahoma", 8, "bold"),
            anchor=tk.W,
            padx=6,
        )
        self.title_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Black video stage
        self.stage = tk.Frame(outer, bg=YT_VIDEO_BG, height=220)
        self.stage.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        self.stage.pack_propagate(False)

        self.stage_label = tk.Label(
            self.stage,
            text="▶\n\nSelect a video and press Play",
            bg=YT_VIDEO_BG,
            fg="#666666",
            font=("Tahoma", 11),
            justify=tk.CENTER,
        )
        self.stage_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Control bar (classic silver)
        controls = tk.Frame(outer, bg=YT_CHROME, height=32)
        controls.pack(fill=tk.X)
        controls.pack_propagate(False)

        self.play_btn = tk.Button(
            controls,
            text="▶ Play",
            command=self._toggle_play,
            bg="#e8e8e8",
            fg=YT_TEXT,
            font=("Tahoma", 8, "bold"),
            relief=tk.RAISED,
            bd=1,
            padx=8,
            activebackground="#d0d0d0",
        )
        self.play_btn.pack(side=tk.LEFT, padx=4, pady=4)

        # Fake progress bar
        prog_frame = tk.Frame(controls, bg=YT_CHROME)
        prog_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4, pady=6)
        self.progress = ttk.Progressbar(
            prog_frame, orient=tk.HORIZONTAL, mode="determinate", maximum=100
        )
        self.progress.pack(fill=tk.X)
        self.progress["value"] = 0

        self.time_label = tk.Label(
            controls,
            text="0:00 / 0:00",
            bg=YT_CHROME,
            fg=YT_TEXT,
            font=("Tahoma", 8),
            width=12,
        )
        self.time_label.pack(side=tk.LEFT, padx=2)

        tk.Button(
            controls,
            text="Open in Browser",
            command=self._open_browser,
            bg="#e8e8e8",
            fg=YT_TEXT,
            font=("Tahoma", 8),
            relief=tk.RAISED,
            bd=1,
            padx=6,
            activebackground="#d0d0d0",
        ).pack(side=tk.RIGHT, padx=4, pady=4)

        # Info strip under player
        info = tk.Frame(self, bg="#f5f5f5", height=48)
        info.pack(fill=tk.X, padx=4, pady=(0, 4))
        info.pack_propagate(False)
        self.info_title = tk.Label(
            info,
            text="No video selected",
            bg="#f5f5f5",
            fg="#111111",
            font=("Tahoma", 9, "bold"),
            anchor=tk.W,
            padx=6,
        )
        self.info_title.pack(fill=tk.X, pady=(4, 0))
        self.info_meta = tk.Label(
            info,
            text="",
            bg="#f5f5f5",
            fg="#666666",
            font=("Tahoma", 8),
            anchor=tk.W,
            padx=6,
        )
        self.info_meta.pack(fill=tk.X)

    def load_video(
        self,
        video_id: str,
        title: str,
        channel: str = "",
        published: str = "",
    ) -> None:
        self._video_id = video_id
        self._title = title
        self._playing = False
        self.play_btn.configure(text="▶ Play")
        self.progress["value"] = 0
        self.time_label.configure(text="0:00 / --:--")
        self.stage_label.configure(
            text=f"▶\n\n{title[:60]}\n\nPress Play to open",
            fg="#aaaaaa",
        )
        self.info_title.configure(text=title[:80])
        meta = channel
        if published:
            meta = f"{channel}  ·  {published[:10]}" if channel else published[:10]
        self.info_meta.configure(text=meta)
        self.title_label.configure(text=f"YouTube – {title[:40]}")

    def _toggle_play(self) -> None:
        if not self._video_id:
            messagebox.showinfo("Player", "Select a video first.")
            return
        if not self._playing:
            self._playing = True
            self.play_btn.configure(text="❚❚ Pause")
            self.stage_label.configure(
                text=f"▶ Now playing\n\n{self._title[:50]}\n\n"
                "(opens in your browser)",
                fg="#cc3333",
            )
            self.progress["value"] = 15
            self._open_browser()
        else:
            self._playing = False
            self.play_btn.configure(text="▶ Play")
            self.stage_label.configure(
                text=f"❚❚ Paused\n\n{self._title[:50]}",
                fg="#aaaaaa",
            )

    def _open_browser(self) -> None:
        if not self._video_id:
            messagebox.showinfo("Player", "Select a video first.")
            return
        url = f"https://www.youtube.com/watch?v={self._video_id}"
        webbrowser.open(url)


class WatchCartoonsApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Watch-Cartoons – Windows XP Compatibility Layer")
        self.geometry("1020x680")
        self.minsize(860, 560)
        self.configure(bg=BG)

        self.client: YouTubeClient | None = None
        self._current_results: list[dict[str, Any]] = []
        self._mode = tk.StringVar(value="videos")

        self._apply_style()
        self._build_ui()
        self._try_load_api_key()

    def _apply_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(".", background=BG, foreground=FG, fieldbackground=BG_LIST)
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=FG, font=("Tahoma", 9))
        style.configure(
            "TButton",
            background=BG_PANEL,
            foreground=FG,
            font=("Tahoma", 9),
            padding=4,
        )
        style.map(
            "TButton",
            background=[("active", ACCENT), ("pressed", SELECT_BG)],
            foreground=[("active", HEADER_FG)],
        )
        style.configure(
            "TEntry",
            fieldbackground=BG_LIST,
            foreground=FG,
            insertcolor=FG,
        )
        style.configure(
            "TRadiobutton",
            background=BG,
            foreground=FG,
            font=("Tahoma", 9),
        )
        style.map("TRadiobutton", background=[("active", BG)])
        style.configure(
            "Treeview",
            background=BG_LIST,
            foreground=FG,
            fieldbackground=BG_LIST,
            font=("Tahoma", 9),
            rowheight=22,
        )
        style.configure(
            "Treeview.Heading",
            background=BG_PANEL,
            foreground=FG,
            font=("Tahoma", 9, "bold"),
            relief=tk.FLAT,
        )
        style.map(
            "Treeview",
            background=[("selected", SELECT_BG)],
            foreground=[("selected", HEADER_FG)],
        )
        style.configure(
            "Horizontal.TProgressbar",
            troughcolor="#888888",
            background=YT_RED,
            thickness=10,
        )
        style.configure(
            "Status.TLabel",
            background=STATUS_BG,
            foreground=FG_DIM,
            font=("Tahoma", 8),
            padding=3,
        )

    def _build_ui(self) -> None:
        # --- XP-style title header ---
        header = tk.Frame(self, bg=HEADER_BG, height=36)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(
            header,
            text="  Watch-Cartoons",
            bg=HEADER_BG,
            fg=HEADER_FG,
            font=("Tahoma", 11, "bold"),
            anchor=tk.W,
        ).pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(
            header,
            text="Windows XP compatibility layer   ",
            bg=HEADER_BG,
            fg="#a0c4ff",
            font=("Tahoma", 8),
            anchor=tk.E,
        ).pack(side=tk.RIGHT, fill=tk.Y)

        # --- API key row ---
        top = ttk.Frame(self, padding=6)
        top.pack(fill=tk.X)
        ttk.Label(top, text="API Key:").pack(side=tk.LEFT)
        self.api_key_var = tk.StringVar()
        self.api_entry = ttk.Entry(
            top, textvariable=self.api_key_var, width=42, show="*"
        )
        self.api_entry.pack(side=tk.LEFT, padx=(4, 8), fill=tk.X, expand=True)
        ttk.Button(top, text="Set Key", command=self._set_api_key).pack(side=tk.LEFT)

        # --- Search bar ---
        search_frame = ttk.Frame(self, padding=(6, 0, 6, 6))
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

        # --- Main split: list | player ---
        body = ttk.Frame(self, padding=(6, 0))
        body.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(body)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Applications-style list header
        list_header = tk.Frame(left, bg=BG_PANEL, height=24)
        list_header.pack(fill=tk.X)
        list_header.pack_propagate(False)
        tk.Label(
            list_header,
            text="  Results",
            bg=BG_PANEL,
            fg=FG,
            font=("Tahoma", 9, "bold"),
            anchor=tk.W,
        ).pack(side=tk.LEFT, fill=tk.Y)

        columns = ("title", "channel", "id")
        self.tree = ttk.Treeview(
            left, columns=columns, show="headings", selectmode="browse"
        )
        self.tree.heading("title", text="Title")
        self.tree.heading("channel", text="Channel")
        self.tree.heading("id", text="ID")
        self.tree.column("title", width=280, stretch=True)
        self.tree.column("channel", width=130, stretch=False)
        self.tree.column("id", width=110, stretch=False)

        scrollbar = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", self._on_double_click)

        # Right: 2005 player
        right = tk.Frame(body, bg=BG, width=380)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(8, 0))
        right.pack_propagate(False)

        player_header = tk.Frame(right, bg=BG_PANEL, height=24)
        player_header.pack(fill=tk.X)
        player_header.pack_propagate(False)
        tk.Label(
            player_header,
            text="  Player  (YouTube 2005 style)",
            bg=BG_PANEL,
            fg=FG,
            font=("Tahoma", 9, "bold"),
            anchor=tk.W,
        ).pack(side=tk.LEFT, fill=tk.Y)

        self.player = YouTube2005Player(right)
        self.player.pack(fill=tk.BOTH, expand=True, pady=(0, 4))

        # Detail text under list
        detail_frame = ttk.Frame(self, padding=6)
        detail_frame.pack(fill=tk.X)
        self.detail = tk.Text(
            detail_frame,
            height=5,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg=BG_LIST,
            fg=FG,
            insertbackground=FG,
            font=("Tahoma", 8),
            relief=tk.FLAT,
            bd=1,
            highlightbackground=BORDER,
            highlightthickness=1,
        )
        self.detail.pack(fill=tk.X)

        # Action bar
        action_bar = ttk.Frame(self, padding=(6, 2))
        action_bar.pack(fill=tk.X)
        ttk.Button(
            action_bar,
            text="Open Playlist Items",
            command=self._fetch_playlist_items,
        ).pack(side=tk.LEFT)
        ttk.Button(
            action_bar, text="Video Details", command=self._show_video_details
        ).pack(side=tk.LEFT, padx=6)
        ttk.Button(
            action_bar, text="▶ Load in Player", command=self._load_into_player
        ).pack(side=tk.LEFT, padx=6)

        # Status bar (xp-layer style)
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(
            self, textvariable=self.status_var, style="Status.TLabel", anchor=tk.W
        ).pack(fill=tk.X, side=tk.BOTTOM)

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
            f"{desc[:600]}"
        )
        self._set_detail(text)

    def _on_double_click(self, _event: Any = None) -> None:
        if self._mode.get() == "playlists":
            self._fetch_playlist_items()
        else:
            self._load_into_player()

    def _load_into_player(self) -> None:
        idx = self._selected_index()
        if idx is None:
            messagebox.showinfo("Player", "Select a video first.")
            return
        item = self._current_results[idx]
        video_id = item.get("id", {}).get("videoId")
        if not video_id:
            messagebox.showinfo(
                "Player",
                "Selected item is not a video. Open a playlist or search videos.",
            )
            return
        snippet = item.get("snippet", {})
        self.player.load_video(
            video_id=video_id,
            title=snippet.get("title", "Untitled"),
            channel=snippet.get("channelTitle", ""),
            published=snippet.get("publishedAt", ""),
        )
        self.status_var.set(f"Loaded into player: {video_id}")

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
                self.after(0, lambda m=msg: messagebox.showerror("Video Error", m))
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

        # Also push into the retro player
        video_id = details.get("id", "")
        if video_id:
            self.player.load_video(
                video_id=video_id,
                title=snippet.get("title", "Untitled"),
                channel=snippet.get("channelTitle", ""),
                published=snippet.get("publishedAt", ""),
            )

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
