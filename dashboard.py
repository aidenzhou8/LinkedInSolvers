import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QFrame, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon, QPixmap

# Import the game solvers
import queens
import tango
import zip
from utils import create_title_label

class GameButton(QPushButton):
    def __init__(self, title, description, image_path, parent=None):
        super().__init__(parent)
        self.setFixedSize(240, 265)
        self.setStyleSheet("""
            QPushButton {
                background-color: #1a1a2e;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 12px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #16213e;
                border: 2px solid #0f3460;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # Add image
        image_label = QLabel()
        pixmap = QPixmap(image_path)
        scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        image_label.setPixmap(scaled_pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(image_label)
        
        # Add title
        title_label = QLabel(title)
        title_label.setFont(QFont('Futura', 18, QFont.Bold))
        title_label.setStyleSheet("color: #e94560;")
        title_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addStretch()
        
        self.setLayout(layout)

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LinkedIn Puzzle Solvers")
        self.setMinimumSize(800, 300)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f3460;
            }
            QLabel {
                color: #e94560;
            }
        """)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Add title using utility function
        title = create_title_label("LinkedIn Puzzle Solvers")
        main_layout.addWidget(title)
        
        # Create grid for game buttons
        grid = QGridLayout()
        grid.setSpacing(15)
        
        # Create game buttons with images
        queens_btn = GameButton("Queens", "", "resources/queens.png")
        tango_btn = GameButton("Tango", "", "resources/tango.png")
        zip_btn = GameButton("Zip", "", "resources/Zip.png")
        
        # Connect buttons to their respective solvers
        queens_btn.clicked.connect(self.launch_queens)
        tango_btn.clicked.connect(self.launch_tango)
        zip_btn.clicked.connect(self.launch_zip)
        
        # Add buttons to grid
        grid.addWidget(queens_btn, 0, 0)
        grid.addWidget(tango_btn, 0, 1)
        grid.addWidget(zip_btn, 0, 2)
        
        # Add grid to main layout
        main_layout.addLayout(grid)
        main_layout.addStretch(1)
        
        # Center the window
        self.center()
    
    def center(self):
        frame_geometry = self.frameGeometry()
        screen_center = QApplication.desktop().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())
    
    def launch_queens(self):
        self.hide()
        queens_window = queens.QueensWindow()
        queens_window.show()
        # Wait for the window to close before showing dashboard again
        while queens_window.isVisible():
            QApplication.processEvents()
        self.show()
    
    def launch_tango(self):
        self.hide()
        tango_window = tango.Main()
        tango_window.show()
        # Wait for the window to close before showing dashboard again
        while tango_window.isVisible():
            QApplication.processEvents()
        self.show()
    
    def launch_zip(self):
        self.hide()
        zip_window = zip.create_zip_window()
        zip_window.show()
        # Wait for the window to close before showing dashboard again
        while zip_window.isVisible():
            QApplication.processEvents()
        self.show()

def main():
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 
