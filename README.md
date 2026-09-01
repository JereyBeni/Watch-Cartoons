# Watch-Cartoons

Python client for discovering and fetching cartoon-related videos using the **YouTube Data API v3**.

## Features

- Search for cartoons, episodes, or related content on YouTube
- Retrieve video details, playlists, and channel information
- Simple command-line interface
- Configurable via environment variables
- Automated Windows `.exe` build on every GitHub Actions run

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

## Windows Executable

Every push and pull request to `main` triggers a GitHub Actions job that builds a standalone Windows executable using **PyInstaller**.

After a successful workflow run:

1. Open the repository on GitHub → **Actions**
2. Select the latest workflow run
3. Download the artifact named **Watch-Cartoons-Windows**
4. Extract `Watch-Cartoons.exe`

You can also build the executable locally on Windows:

```bash
pip install pyinstaller
pyinstaller --onefile --name Watch-Cartoons --console main.py
```

The resulting binary will be located at `dist/Watch-Cartoons.exe`.

> **Note:** The executable still requires a valid `YOUTUBE_API_KEY` environment variable (or a `.env` file in the same directory).

## Project Structure

```
.
├── .github/
│   └── workflows/
│       └── build.yml      # CI validation + Windows .exe build
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
- Builds a Windows `.exe` with PyInstaller and uploads it as an artifact

## License

MIT
