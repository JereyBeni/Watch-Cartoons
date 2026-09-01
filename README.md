# Watch-Cartoons

Desktop GUI application for discovering cartoon videos and playlists using the **YouTube Data API v3**.

Styled after a **Windows XP compatibility layer** with a retro **2005-era YouTube player** (desktop chrome + local web shell).

## Features

- Search for cartoon videos and playlists
- Load playlist items
- View video details (title, channel, duration, views, likes, description)
- **Windows XP–inspired dark UI** (blue title bar, dark panels, Tahoma fonts)
- **2005 YouTube-style desktop player** chrome
- **Local web player** (`web/index.html` + `player.js`) that mimics the old watch page and embeds the modern YouTube player under a retro skin
- Configurable API key (environment variable or in-app entry)
- Automated Windows `.exe` build on every GitHub Actions run

## Requirements

- Python 3.10+
- A valid YouTube Data API v3 key ([Google Cloud Console](https://console.cloud.google.com/))
- A modern browser (for the web player)

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
2. Search for videos or playlists.
3. Select a video → **Load in Player** (or double-click).
4. Press **▶ Play** or **Web Player** / **Open Web Player** to open `web/index.html` with that video.

### Web player only

You can open the HTML shell directly in a browser:

```text
web/index.html?v=VIDEO_ID&title=My+Title&channel=Channel+Name
```

## About archived old players

Flash-based YouTube players from 2005–2010 (and most Wayback Machine snapshots of them) **no longer run** in current browsers. This project uses:

- A visual homage to the 2005 watch page (`web/index.html`, `style.css`, `player.js`)
- The modern YouTube iframe embed underneath for actual playback

## Windows Executable

Every push and pull request to `main` builds a standalone Windows GUI executable with **PyInstaller** (`--windowed`).

After a successful workflow run, download the **Watch-Cartoons-Windows** artifact from the Actions tab.

Local build:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name Watch-Cartoons --add-data "web;web" main.py
```

> On Linux/macOS packaging, use `--add-data "web:web"` instead.

## Project Structure

```
.
├── web/
│   ├── index.html     # 2005-style watch page
│   ├── style.css
│   └── player.js      # embed + controls
├── main.py            # XP GUI + bridge to web player
├── youtube_client.py
├── requirements.txt
└── .github/workflows/build.yml
```

## License

MIT
