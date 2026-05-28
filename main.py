import sys
import os
import requests
import io
import cadquery as cq
from PySide6.QtWidgets import (
    QApplication, QLabel, QMainWindow, QPushButton,
    QVBoxLayout, QWidget, QLineEdit, QProgressBar
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QThread, Signal
from PIL import Image
import utils


def get_next_filename(directory, prefix='model', extension='stl'):
    """Generate a unique filename with an incrementing number."""
    i = 1
    while True:
        filename = f"{prefix}_{i}.{extension}"
        if not os.path.exists(os.path.join(directory, filename)):
            return filename
        i += 1


class GenerateWorker(QThread):
    """Worker thread so the GUI doesn't freeze during generation."""
    finished = Signal(str)   # success: filename
    error = Signal(str)      # error message
    progress = Signal(str)   # status text

    def __init__(self, share_link):
        super().__init__()
        self.share_link = share_link

    def run(self):
        try:
            self.progress.emit("Parsing spotify link...")
            data = utils.get_link_data(self.share_link)
            if not data or len(data) != 2:
                self.error.emit("Failed to parse the Spotify link. Please ensure it's a valid Spotify link.")
                return

            item_type, item_id = data
            self.progress.emit("Downloading Spotify code...")

            # Official Spotify scannables endpoint
            code_url = (
                f"https://scannables.scdn.co/uri/plain/jpeg"
                f"/000000/white/640/spotify:{item_type}:{item_id}"
            )
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            }
            r = requests.get(code_url, headers=headers, timeout=15)

            if not r.ok or len(r.content) < 500:
                # Fallback to spotifycodes.com
                self.progress.emit("Trying alternative source...")
                fallback_url = (
                    f"https://www.spotifycodes.com/downloadCode.php?"
                    f"uri=jpeg%2F000000%2Fwhite%2F640%2Fspotify%3A{item_type}%3A{item_id}"
                )
                r = requests.get(fallback_url, headers=headers, timeout=15)
                if not r.ok or len(r.content) < 500:
                    self.error.emit(
                        "Failed to download Spotify code.\n"
                        "Check your internet connection and the link's validity."
                    )
                    return

            self.progress.emit("Analyzing code image...")
            try:
                img = Image.open(io.BytesIO(r.content)).convert("RGB")
            except Exception as e:
                self.error.emit(f"Error opening image: {e}")
                return

            # Crop: remove Spotify logo on the left and padding on the right
            # Image is 640px wide; logo area ~160px, right padding ~31px
            w, h = img.size
            crop_left = int(w * 0.25)
            crop_right = int(w * 0.95)
            img = img.crop((crop_left, 0, crop_right, h))
            w, h = img.size
            pix = img.load()

            bar_heights = []
            x = 0
            while x < w:
                # Skip black columns
                while x < w and _is_dark(pix[x, h // 2]):
                    x += 1
                if x >= w:
                    break
                # Collect a bar (white columns)
                bar_x_start = x
                while x < w and not _is_dark(pix[x, h // 2]):
                    x += 1
                # Measure bar height: scan middle column of this bar segment
                mid_x = (bar_x_start + x) // 2
                bar_h = 0
                for y in range(h):
                    if not _is_dark(pix[mid_x, y]):
                        bar_h += 1
                if bar_h > 0:
                    bar_heights.append(bar_h / h)  # normalize 0-1

            if not bar_heights:
                self.error.emit("No bars detected in the Spotify code. Please try again.")
                return

            self.progress.emit(f"Generating 3D model ({len(bar_heights)} bars)...")

            models_dir = 'models'
            os.makedirs(models_dir, exist_ok=True)

            try:
                model = cq.importers.importStep('base_model.step')
            except Exception as e:
                self.error.emit(
                    f"Error loading base_model.step: {e}\n"
                    "Make sure the base_model.step file is in the same folder as the script."
                )
                return

            max_h = max(bar_heights) if bar_heights else 1
            for i, bar in enumerate(bar_heights):
                normalized = bar / max_h  # 0-1
                bar_mm = 2.0 + normalized * 4.0  # 2-6mm range; slot = 3.6-10.8mm, fits within Y 0-15

                try:
                    model = (
                        model
                        .pushPoints([(15.5 + i * 1.88, 7.5)])
                        .sketch()
                        .slot(9 / 5 * bar_mm, 1, 90)
                        .finalize()
                        .extrude(4)
                    )
                except Exception as e:
                    self.error.emit(f"Error generating model for bar {i}: {e}")
                    return

            filename = get_next_filename(models_dir, 'model', 'stl')
            output_path = os.path.join(models_dir, filename)

            self.progress.emit("Exporting STL file...")
            try:
                cq.exporters.export(model, output_path)
            except Exception as e:
                self.error.emit(f"Error exporting STL: {e}")
                return

            self.finished.emit(output_path)

        except requests.exceptions.ConnectionError:
            self.error.emit("No internet connection.")
        except requests.exceptions.Timeout:
            self.error.emit("Timeout while waiting for server response.")
        except Exception as e:
            self.error.emit(f"Unexpected error: {e}")


def _is_dark(pixel, threshold=60):
    """Return True if the pixel is dark (part of background)."""
    return pixel[0] < threshold and pixel[1] < threshold and pixel[2] < threshold


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.generated_path = None
        self._build_ui()

    def _build_ui(self):
        self.setWindowTitle("Spotify Keychain STL Generator")
        self.setFixedSize(520, 320)
        self.setStyleSheet("background-color: #121212; color: #ffffff;")

        title = QLabel("🎵 Spotify Keychain Generator")
        title.setFont(QFont("Arial", 15, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1DB954; padding: 10px;")

        subtitle = QLabel("Paste Spotify track/album/playlist link to create a 3D model of its code")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #aaaaaa; font-size: 11px;")

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(
            "e.g., https://open.spotify.com/track/4R1bPIiMEr5xfejy05H7cW"
        )
        self.url_input.setStyleSheet(
            "QLineEdit {"
            "  background-color: #1f1f1f; color: #ffffff;"
            "  padding: 8px; border-radius: 6px;"
            "  border: 1px solid #333; font-size: 12px;"
            "}"
            "QLineEdit:focus { border: 1px solid #1DB954; }"
        )
        self.url_input.returnPressed.connect(self._generate)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 11))
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("color: #ffcc00; min-height: 36px;")

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # indeterminate
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(
            "QProgressBar { border: 1px solid #333; border-radius: 4px; background: #1f1f1f; }"
            "QProgressBar::chunk { background-color: #1DB954; border-radius: 4px; }"
        )

        self.generate_btn = self._make_button("⚙️  Generate STL", self._generate)
        self.open_btn = self._make_button("📂  Open Model Folder", self._open_folder)
        self.open_btn.setEnabled(False)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.url_input)
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.generate_btn)
        layout.addWidget(self.open_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def _make_button(self, text, func):
        btn = QPushButton(text)
        btn.setStyleSheet(
            "QPushButton {"
            "  background-color: #1f1f1f; color: #ffffff;"
            "  border: 1px solid #444; padding: 10px;"
            "  margin: 2px; border-radius: 6px; font-size: 13px;"
            "}"
            "QPushButton:hover { background-color: #2a2a2a; border-color: #1DB954; }"
            "QPushButton:pressed { background-color: #0d0d0d; }"
            "QPushButton:disabled { color: #555; border-color: #333; }"
        )
        btn.clicked.connect(func)
        return btn

    def _generate(self):
        link = self.url_input.text().strip()
        if not link:
            self._set_status("Paste a Spotify link before generating.", error=True)
            return

        self.generate_btn.setEnabled(False)
        self.open_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self._set_status("Initializing...")

        self.worker = GenerateWorker(link)
        self.worker.progress.connect(lambda msg: self._set_status(msg))
        self.worker.finished.connect(self._on_success)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_success(self, path):
        self.generated_path = path
        self.progress_bar.setVisible(False)
        self.generate_btn.setEnabled(True)
        self.open_btn.setEnabled(True)
        fname = os.path.basename(path)
        self._set_status(f"✅ Done! File saved: models/{fname}", success=True)

    def _on_error(self, msg):
        self.progress_bar.setVisible(False)
        self.generate_btn.setEnabled(True)
        self._set_status(f"❌ {msg}", error=True)

    def _set_status(self, msg, error=False, success=False):
        if success:
            color = "#1DB954"
        elif error:
            color = "#ff4444"
        else:
            color = "#ffcc00"
        self.status_label.setStyleSheet(
            f"color: {color}; min-height: 36px; font-size: 11px;"
        )
        self.status_label.setText(msg)

    def _open_folder(self):
        if self.generated_path:
            folder = os.path.abspath(os.path.dirname(self.generated_path))
            if sys.platform == "win32":
                os.startfile(folder)
            elif sys.platform == "darwin":
                os.system(f'open "{folder}"')
            else:
                os.system(f'xdg-open "{folder}"')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
