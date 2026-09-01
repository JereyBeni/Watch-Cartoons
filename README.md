# Watch-Cartoons

Python client for discovering and fetching cartoon-related videos using the **YouTube Data API v3**.

## Features

- Search for cartoons, episodes, or related content on YouTube
- Retrieve video details, playlists, and channel information
- Simple command-line interface
- Configurable via environment variables

## Requirements

- Python 3.10+
- A valid YouTube Data API v3 key (obtain one from the [Google Cloud Console](https://console.cloud.google.com/))

## Installation

```bash
git clone https://github.com/JereyBeni/Watch-Cartoons.git
cd Watch-Cartoons
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

## Configuration

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Edit `.env` and set your API key:

```
YOUTUBE_API_KEY=your_api_key_here
```

## Usage

Search for cartoons:

```bash
python main.py search "Tom and Jerry" --max-results 10
```

Get details of a specific video:

```bash
python main.py video VIDEO_ID
```

Search within a channel:

```bash
python main.py search "cartoon" --channel-id CHANNEL_ID
```

## Project Structure

```
.
├── .github/
│   └── workflows/
│       └── build.yml      # CI build & validation
├── main.py                # Main CLI entry point
├── youtube_client.py      # YouTube Data API wrapper
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Development

The repository includes a GitHub Actions workflow (`.github/workflows/build.yml`) that:

- Installs dependencies
- Runs linting (ruff)
- Performs a basic syntax and import check

## License

MIT
