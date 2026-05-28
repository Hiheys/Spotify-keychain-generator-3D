# 🎵 Spotify Keychain Generator 3D

Generates a personalized Spotify code keychain ready for 3D printing.  
Paste a link to a song, album, artist, or playlist — get a `.stl` file.

---

## System Requirements

| Component | Minimum version |
|---|---|
| Python | **3.10 – 3.13** |
| OS | Windows 10/11, macOS 12+, Linux |
| Internet connection | required (fetching the Spotify code) |

> ✅ Works with Python 3.10, 3.11, 3.12 and 3.13.  
> 💡 **Python 3.12** is recommended — most stable choice. Python 3.13 works too, but if `pip install cadquery` fails to compile, fall back to 3.12.  
> ⚠️ Python **3.9.x** (required by the old code) is **no longer needed**.

---

## Installing Python

If you don't have Python installed yet, do this before anything else.

### Windows

> ⚠️ **Do not use Python from the Microsoft Store.** The Store version has a broken `pip`, PATH issues, and may not support all packages (e.g. `cadquery`). If you already have the Store version, install the python.org version alongside it — they can coexist.

1. Go to [python.org/downloads/release/python-31210](https://www.python.org/downloads/release/python-31210/) and download **Windows installer (64-bit)**.
2. Run the downloaded `.exe`.
3. ⚠️ **Critical:** on the first screen, check **"Add Python to PATH"** before clicking Install Now.

   ```
   ☑ Add Python 3.12 to PATH   ← check this!
   ```

4. Click **Install Now** and wait for it to finish.
5. Open a **new** PowerShell or CMD window and verify:

   ```powershell
   py -3.12 --version
   ```

   You should see `Python 3.12.x`. The `py` command is the Windows Python Launcher — it lets you pick a specific version when you have multiple installed.

**If you have multiple Python versions (e.g. Store + python.org)**, always use `py -3.12` instead of just `python`:

```powershell
py -3.12 -m pip install -r requirements.txt
py -3.12 main.py
```

> 💡 **VS Code users:** after installing Python, kill all terminals in VS Code (`Ctrl+Shift+P` → `Terminal: Kill All Terminals`) and open a new one. VS Code caches the old PATH and won't see the new Python until you do this.

---

### macOS

macOS often ships with a system Python 2.7 — **don't use it**. Install a fresh one:

1. Go to [python.org/downloads](https://www.python.org/downloads/) and download the macOS installer (`.pkg`).
2. Run the file and follow the installer steps.
3. Open **Terminal** (Spotlight: `Cmd + Space` → type "Terminal") and verify:

   ```bash
   python3 --version
   ```

   You should see e.g. `Python 3.12.3`.

Alternatively, install via [Homebrew](https://brew.sh):

```bash
brew install python
```

---

### Linux (Ubuntu / Debian)

Python 3 is usually pre-installed. Check your version:

```bash
python3 --version
```

If the version is older than 3.10 or Python is missing:

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

---

### Verifying pip

`pip` is Python's package manager — you need it to install dependencies. Check it works:

```bash
# Windows
pip --version

# macOS / Linux
pip3 --version
```

If `pip` is missing:

```bash
# Windows (run CMD as administrator)
python -m ensurepip --upgrade

# macOS / Linux
sudo apt install python3-pip   # Ubuntu/Debian
```

---

## Installation

### 1. Download the project files

Clone the repository or download the ZIP:

```bash
git clone https://github.com/Hiheys/Spotify-keychain-generator-3D.git
cd Spotify-keychain-generator-3D
```

Or download as ZIP from GitHub → `Code → Download ZIP` and extract it.

---

### 2. (Optional) Create a virtual environment

Recommended — keeps dependencies isolated from the rest of your system:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

This installs: `cadquery`, `PySide6`, `requests`, `Pillow`.

> ⏳ The first install may take a few minutes — `cadquery` is a large package (~300 MB).

---

### 4. Make sure the base model is in place

The project folder must contain:

```
base_model.step
```

It's included in the repository. **Do not delete it** — it's the keychain base that the Spotify code gets added onto.

---

## Running the App

```bash
# Windows (python.org install)
python main.py

# Windows (if you have multiple Python versions, e.g. alongside Store Python)
py -3.12 main.py

# macOS / Linux
python3 main.py
```

An application window will open.

---

## How to Use

1. Open Spotify and navigate to a song, album, artist, or playlist.
2. Click `···` → **Share** → **Copy link**.
3. Paste the link into the text field in the app.
4. Click **Generate STL**.
5. After a moment, a success message will appear with the filename. Click **Open model folder** to find the file.

The `.stl` file is saved to the `models/` folder inside the project directory (e.g. `models/model_1.stl`).

---

## Supported Link Formats

The app understands all Spotify link variants:

```
https://open.spotify.com/track/4R1bPIiMEr5xfejy05H7cW
https://open.spotify.com/intl-pl/track/4R1bPIiMEr5xfejy05H7cW?si=abc123
https://open.spotify.com/album/1DFixLWuPkv3KT3TnV35m3
https://open.spotify.com/artist/06HL4z0CvFAxyc27GXpf02
https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
spotify:track:4R1bPIiMEr5xfejy05H7cW
```

---

## 3D Printing

Open the generated `.stl` in any slicer (Cura, PrusaSlicer, Bambu Studio, etc.).

**Recommended settings:**
- Material: PLA or PETG
- Layer height: 0.15–0.2 mm (fine details in the code)
- Infill: 20–30%
- Supports: not needed
- Two-color print: print the base in one color and the code bars in a contrasting color (e.g. grey + white as shown in the photo)

---

## Project Structure

```
Spotify-keychain-generator-3D/
├── main.py            # Main application with GUI
├── utils.py           # Spotify link parser
├── base_model.step    # Base keychain model (do not modify)
├── requirements.txt   # Python dependencies
├── models/            # Generated STL files go here (created automatically)
└── README.md
```

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'cadquery'`**  
Dependencies are not installed. Run `pip install -r requirements.txt`.

**`Error importing base_model.step`**  
The `base_model.step` file is not in the same folder as `main.py`. Check the project structure.

**"Failed to fetch Spotify code"**  
Check your internet connection. Make sure the link is valid and points to public content (not a private playlist).

**App won't start on Linux (Qt/display error)**  
You need a graphical desktop environment. The app won't run on a headless server — it's designed for desktop use.

**Old Python version (3.9)**  
Install Python 3.10+ from [python.org](https://www.python.org/downloads/). The old version is no longer required.

**`pip` not recognized on Windows**  
Use `python -m pip` instead of `pip` directly, or reinstall Python from python.org with the "Add to PATH" option checked.

---

## Changes from the Original Code

- Replaced **PyQt5** with **PySide6** (newer, actively maintained)
- Model generation runs in a **separate thread** — the window no longer freezes
- Fixed **bar parsing logic** for more accurate height detection
- Added support for `intl-xx` prefixed links (e.g. `intl-pl`)
- Added fallback to a secondary API if the primary is unavailable
- "Open folder" button works on Windows, macOS and Linux
- Better error handling with descriptive messages

---

## Credits

Original project: [ricdigi/spotify_keychain_3D_model](https://github.com/ricdigi/spotify_keychain_3D_model)  
GUI + generator: [Hiheys/Spotify-keychain-generator-3D](https://github.com/Hiheys/Spotify-keychain-generator-3D)  
