from PyQt5.QtWidgets import QPushButton, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Style for back button, shared across all game windows
BACK_BUTTON_STYLE = """
    QPushButton {
        background-color: #1a1a2e;
        color: #e94560;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
    }
    QPushButton:hover {
        background-color: #16213e;
        border: 2px solid #0f3460;
    }
"""

def create_back_button(parent=None):
    """Create a standardized back button for all game windows."""
    back_button = QPushButton("← Back to Dashboard", parent)
    back_button.setFont(QFont('Futura', 12))
    back_button.setStyleSheet(BACK_BUTTON_STYLE)
    return back_button

# Style for title label, shared across all game windows

def create_title_label(text, size=32):
    """Create a standardized title label."""
    title = QLabel(text)
    title.setFont(QFont('Futura', size, QFont.Bold))
    title.setAlignment(Qt.AlignCenter)
    title.setStyleSheet("color: #e94560; margin: 5px;")
    return title 