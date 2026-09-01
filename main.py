"""CLI entry point for Watch-Cartoons YouTube Data API client."""

from __future__ import annotations

import argparse
import json
import sys

from dotenv import load_dotenv

from youtube_client import YouTubeClient


def format_search_result(item: dict) -> str:
    snippet = item.get("snippet", {})
    video_id = item.get("id", {}).get("videoId", "N/A")
    title = snippet.get("title", "No title")
    channel = snippet.get("channelTitle", "Unknown channel")
    published = snippet.get("publishedAt", "")[:10]
    return f"[{video_id}] {title}\n    Channel: {channel} | Published: {published}"


def cmd_search(args: argparse.Namespace) -> None:
    client = YouTubeClient()
    results = client.search(
        query=args.query,
        max_results=args.max_results,
        channel_id=args.channel_id,
        order=args.order,
    )

    if not results:
        print("No results found.")
        return

    print(f"Found {len(results)} result(s):\n")
    for item in results:
        print(format_search_result(item))
        print()


def cmd_video(args: argparse.Namespace) -> None:
    client = YouTubeClient()
    details = client.get_video_details(args.video_id)

    if not details:
        print(f"Video '{args.video_id}' not found.")
        sys.exit(1)

    if args.json:
        print(json.dumps(details, indent=2))
        return

    snippet = details.get("snippet", {})
    stats = details.get("statistics", {})
    content = details.get("contentDetails", {})

    print(f"Title      : {snippet.get('title')}")
    print(f"Channel    : {snippet.get('channelTitle')}")
    print(f"Published  : {snippet.get('publishedAt')}")
    print(f"Duration   : {content.get('duration')}")
    print(f"Views      : {stats.get('viewCount', 'N/A')}")
    print(f"Likes      : {stats.get('likeCount', 'N/A')}")
    print(f"Description:\n{snippet.get('description', '')[:500]}...")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Watch-Cartoons – discover cartoons via YouTube Data API"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # search
    search_parser = subparsers.add_parser("search", help="Search for cartoon videos")
    search_parser.add_argument("query", help="Search query (e.g. 'Tom and Jerry')")
    search_parser.add_argument(
        "--max-results", type=int, default=10, help="Number of results (1-50)"
    )
    search_parser.add_argument(
        "--channel-id", help="Restrict search to a specific channel ID"
    )
    search_parser.add_argument(
        "--order",
        default="relevance",
        choices=["relevance", "date", "viewCount", "rating", "title"],
        help="Sort order",
    )
    search_parser.set_defaults(func=cmd_search)

    # video
    video_parser = subparsers.add_parser("video", help="Get details for a video ID")
    video_parser.add_argument("video_id", help="YouTube video ID")
    video_parser.add_argument(
        "--json", action="store_true", help="Output full JSON response"
    )
    video_parser.set_defaults(func=cmd_video)

    return parser


def main() -> None:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
