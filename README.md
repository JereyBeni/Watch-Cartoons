# Watch-Cartoons

Desktop GUI application for discovering cartoon videos and playlists using the **YouTube Data API v3**.

Styled after a **Windows XP compatibility layer** with a retro **2005-era YouTube player** panel.

## Features

- Search for cartoon videos and playlists
- Load playlist items
- View video details (title, channel, duration, views, likes, description)
- **Windows XP–inspired dark UI** (blue title bar, dark panels, Tahoma fonts)
- **2005 YouTube-style player** chrome (silver bezel, classic controls, progress bar)
- Open selected videos in the system browser from the player
- Configurable API key (environment variable or in-app entry)
- Automated Windows `.exe` build on every GitHub Actions run

## Requirements

- Python 3.10+
- A valid YouTube Data API v3 key ([Google Cloud Console](https://console.cloud.google.com/))

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

You can also paste the key directly in the application window.

## Usage

Launch the GUI:

```bash
python main.py
```

1. Enter (or load) your YouTube Data API key.
2. Type a search query (e.g. `Tom and Jerry`).
3. Choose **Videos** or **Playlists** and click **Search**.
4. Select a result to preview details in the lower pane.
5. Double-click a video (or click **Load in Player**) to send it to the 2005-style player.
6. Press **▶ Play** or **Open in Browser** to watch it.
7. Double-click a playlist (or use **Open Playlist Items**) to expand its videos.

## Windows Executable

Every push and pull request to `main` builds a standalone Windows GUI executable with **PyInstaller** (`--windowed`).

After a successful workflow run:

1. Open the repository on GitHub → **Actions**
2. Select the latest workflow run
3. Download the artifact **Watch-Cartoons-Windows**
4. Extract `Watch-Cartoons.exe`

Local build (Windows):

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name Watch-Cartoons main.py
```

The binary appears at `dist/Watch-Cartoons.exe`.

> The executable still needs a valid API key (environment variable or entered in the GUI).

## Project Structure

```
.
├── .github/
│   └── workflows/
│       └── build.yml      # CI validation + Windows .exe build
├── main.py                # XP-style GUI + 2005 YouTube player
├── youtube_client.py      # YouTube Data API wrapper (videos + playlists)
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Development

The GitHub Actions workflow:

- Lints with ruff
- Performs syntax and import checks
- Builds a windowed Windows `.exe` and uploads it as an artifact

## License

MIT
