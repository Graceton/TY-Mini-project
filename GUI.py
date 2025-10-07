import sys
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel,
    QHBoxLayout, QSizePolicy
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QEvent, QPoint


class AccessibilityApp(QWidget):
    def __init__(self):
        super().__init__()
        self.magnifier_process = None  # store running magnifier process
        self.initUI()

    def createButton(self, emoji, tooltip, color, size=60):
        btn = QPushButton(emoji)
        btn.setToolTip(tooltip)
        btn.setFont(QFont("Arial", 22, QFont.Bold))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border-radius: 10px;
                padding: 10px;
            }}
            QPushButton:hover {{
                border: 2px solid black;
            }}
        """)
        btn.setFixedHeight(size)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn.installEventFilter(self)
        return btn

    def initUI(self):
        self.setWindowTitle("AI Accessibility Application")
        self.setGeometry(200, 200, 400, 50)
        self.layout = QVBoxLayout()

        self.hover_label = QLabel(self)
        self.hover_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                color: black;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.hover_label.setFont(QFont("Arial", 10))
        self.hover_label.setAlignment(Qt.AlignCenter)
        self.hover_label.setVisible(False)

        # Main buttons
        self.zoom_btn = self.createButton("🔍", "Zoom Options", "#3498db")
        self.reader_btn = self.createButton("🔊", "Reader Options", "#2ecc71")
        self.voice_btn = self.createButton("🎙️", "Voice Assistant", "#e74c3c")
        self.settings_btn = self.createButton("⚙️", "Settings", "#95a5a6", 50)
        self.exit_btn = self.createButton("❌", "Exit / Minimize", "#2c3e50", 50)

        # Sub-menus
        self.zoom_options = self.createZoomOptions()
        self.reader_options = self.createReaderOptions()
        self.voice_options = self.createVoiceOptions()
        self.settings_options = self.createSettingsOptions()
        self.exit_options = self.createExitOptions()

        # Connect buttons
        self.zoom_btn.clicked.connect(self.expandZoomButtons)
        self.reader_btn.clicked.connect(lambda: self.toggleMenu(self.reader_options))
        self.voice_btn.clicked.connect(lambda: self.toggleMenu(self.voice_options))
        self.settings_btn.clicked.connect(lambda: self.toggleMenu(self.settings_options))
        self.exit_btn.clicked.connect(lambda: self.toggleMenu(self.exit_options))

        # Add main buttons
        self.layout.addWidget(self.zoom_btn)
        self.layout.addLayout(self.zoom_options)
        self.layout.addWidget(self.reader_btn)
        self.layout.addLayout(self.reader_options)
        self.layout.addWidget(self.voice_btn)
        self.layout.addLayout(self.voice_options)
        self.layout.addWidget(self.settings_btn)
        self.layout.addLayout(self.settings_options)
        self.layout.addWidget(self.exit_btn)
        self.layout.addLayout(self.exit_options)

        self.setLayout(self.layout)

    def expandZoomButtons(self):
        """Replace zoom button with +, reset, - buttons inline"""
        # Hide original zoom button
        self.layout.removeWidget(self.zoom_btn)
        self.zoom_btn.setVisible(False)

        zoom_inline_layout = QHBoxLayout()
        plus_btn = self.createButton("➕", "Zoom In", "#2980b9", 50)
        reset_btn = self.createButton("🔄", "Reset Zoom", "#2980b9", 50)
        minus_btn = self.createButton("➖", "Zoom Out", "#2980b9", 50)

        for btn in [plus_btn, reset_btn, minus_btn]:
            zoom_inline_layout.addWidget(btn)

        self.current_zoom_inline_layout = zoom_inline_layout
        self.layout.insertLayout(0, zoom_inline_layout)

        for i in range(self.zoom_options.count()):
            self.zoom_options.itemAt(i).widget().setVisible(True)

        # Reset button closes magnifier and restores original button
        reset_btn.clicked.connect(self.restoreZoomButton)

        # +/- send zoom commands to magnifier
        plus_btn.clicked.connect(lambda: self.send_zoom_command("zoom_in"))
        minus_btn.clicked.connect(lambda: self.send_zoom_command("zoom_out"))

        # Connect magnifier scripts to buttons
        upper_btn = self.zoom_options.itemAt(0).widget()
        full_btn = self.zoom_options.itemAt(1).widget()
        hover_btn = self.zoom_options.itemAt(2).widget()

        upper_btn.clicked.connect(lambda: self.launch_magnifier("upper_window.py"))
        full_btn.clicked.connect(lambda: self.launch_magnifier("full_window.py"))
        hover_btn.clicked.connect(lambda: self.launch_magnifier("hover_magnify.py"))

    def restoreZoomButton(self):
        # Close magnifier if running
        if self.magnifier_process and self.magnifier_process.poll() is None:
            self.magnifier_process.terminate()
            self.magnifier_process = None

        # Hide zoom inline layout
        if hasattr(self, "current_zoom_inline_layout"):
            for i in range(self.current_zoom_inline_layout.count()):
                w = self.current_zoom_inline_layout.itemAt(i).widget()
                if w:
                    w.setVisible(False)
                    self.current_zoom_inline_layout.removeWidget(w)

        # Show original zoom button
        self.zoom_btn.setVisible(True)
        self.layout.insertWidget(0, self.zoom_btn)

        # Hide magnifier type buttons
        for i in range(self.zoom_options.count()):
            self.zoom_options.itemAt(i).widget().setVisible(False)

    def launch_magnifier(self, script_path):
        # Close previous magnifier
        if self.magnifier_process and self.magnifier_process.poll() is None:
            self.magnifier_process.terminate()

        # Launch new magnifier with stdin enabled
        self.magnifier_process = subprocess.Popen(
            [sys.executable, script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    def send_zoom_command(self, command):
        if self.magnifier_process and self.magnifier_process.poll() is None:
            try:
                self.magnifier_process.stdin.write((command + "\n").encode())
                self.magnifier_process.stdin.flush()
            except Exception as e:
                print(f"Failed to send zoom command: {e}")

    def toggleMenu(self, menu_layout):
        if menu_layout.count() > 0:
            is_visible = menu_layout.itemAt(0).widget().isVisible()
            for i in range(menu_layout.count()):
                widget = menu_layout.itemAt(i).widget()
                if widget:
                    widget.setVisible(not is_visible)
            self.hover_label.setVisible(False)

    def eventFilter(self, obj, event):
        if isinstance(obj, QPushButton):
            if event.type() == QEvent.Enter:
                self.hover_label.setText(obj.toolTip())
                self.hover_label.adjustSize()
                button_pos = obj.mapToGlobal(QPoint(0, 0))
                label_x = button_pos.x() + (obj.width() - self.hover_label.width()) // 2
                label_y = button_pos.y() - self.hover_label.height() - 5
                self.hover_label.move(self.mapFromGlobal(QPoint(label_x, label_y)))
                self.hover_label.setVisible(True)
                self.hover_label.raise_()
            elif event.type() == QEvent.Leave:
                self.hover_label.setVisible(False)
        return super().eventFilter(obj, event)

    def createZoomOptions(self):
        layout = QHBoxLayout()
        upper = self.createButton("🪟", "Upper Window Magnifier", "#2980b9", 50)
        full = self.createButton("🖥️", "Full Window + Cursor Navigation", "#2980b9", 50)
        hover = self.createButton("🖱️", "Hover Zoom Mode", "#2980b9", 50)
        for btn in [upper, full, hover]:
            btn.setVisible(False)
            layout.addWidget(btn)
        return layout

    def createReaderOptions(self):
        layout = QHBoxLayout()
        hover = self.createButton("🖱️", "Hover to Read", "#27ae60", 50)
        para = self.createButton("📑", "Paragraph Selection", "#27ae60", 50)
        line = self.createButton("📏", "Line-wise Reader", "#27ae60", 50)
        ocr = self.createButton("📷", "OCR Overlay", "#27ae60", 50)
        for btn in [hover, para, line, ocr]:
            btn.setVisible(False)
            layout.addWidget(btn)
        return layout

    def createVoiceOptions(self):
        layout = QHBoxLayout()
        start = self.createButton("🎙️", "Start Voice Assistant", "#c0392b", 50)
        stop = self.createButton("🔇", "Stop Voice Assistant", "#c0392b", 50)
        for btn in [start, stop]:
            btn.setVisible(False)
            layout.addWidget(btn)
        return layout

    def createSettingsOptions(self):
        layout = QHBoxLayout()
        audio = self.createButton("🔈", "Audio Settings", "#7f8c8d", 50)
        display = self.createButton("🖼️", "Display Settings", "#7f8c8d", 50)
        general = self.createButton("⚙️", "General Settings", "#7f8c8d", 50)
        for btn in [audio, display, general]:
            btn.setVisible(False)
            layout.addWidget(btn)
        return layout

    def createExitOptions(self):
        layout = QHBoxLayout()
        minimize = self.createButton("➖", "Minimize App", "#34495e", 50)
        quit_app = self.createButton("❌", "Quit App", "#34495e", 50)
        quit_app.clicked.connect(self.close)
        for btn in [minimize, quit_app]:
            btn.setVisible(False)
            layout.addWidget(btn)
        return layout


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AccessibilityApp()
    window.show()
    sys.exit(app.exec_())
