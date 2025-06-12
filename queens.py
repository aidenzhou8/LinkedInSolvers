import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QTableWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt

from utils import create_back_button

class QueensSolver:
    # Initialize the solver with board size (n) and regions
    def __init__(self, n, regions):
        self.n = n
        self.regions = regions
        self.solution = [None] * n
        self.used_cols = set()
        self.used_regions = set()
        self.queen_positions = []

    # Check if (r, c) is adjacent (including diagonals) to any placed Q
    def is_adjacent_conflict(self, r, c):
        for qr, qc in self.queen_positions:
            if abs(qr - r) <= 1 and abs(qc - c) <= 1:
                return True
        return False

    # Backtracking algo to get a solution
    def backtrack(self, row=0):
        if row == self.n:
            return True

        for col in range(self.n):
            region_id = self.regions[row][col]

            # One Q per column
            if col in self.used_cols:
                continue

            # One Q per region
            if region_id in self.used_regions:
                continue

            # No adjacent Qs
            if self.is_adjacent_conflict(row, col):
                continue

            # Place Q
            self.solution[row] = col
            self.used_cols.add(col)
            self.used_regions.add(region_id)
            self.queen_positions.append((row, col))

            if self.backtrack(row + 1):
                return True

            # Undo place
            self.solution[row] = None
            self.used_cols.remove(col)
            self.used_regions.remove(region_id)
            self.queen_positions.pop()

        return False

    def solve(self):
        if self.backtrack(0):
            return list(self.solution)
        return None


# A subclass of QTableWidget to support "click‐and‐drag" painting of cells.
class RegionTable(QTableWidget):

    def __init__(self, n, parent_window):
        super().__init__(n, n)
        self.window_ref = parent_window
        self.is_painting = False

    # When the left mouse button is pressed and moved, it notifies the parent window
    # to paint every cell that the cursor passes over.
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_painting = True
            idx = self.indexAt(event.pos())
            if idx.isValid():
                self.window_ref.paint_cell(idx.row(), idx.column())
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_painting:
            idx = self.indexAt(event.pos())
            if idx.isValid():
                self.window_ref.paint_cell(idx.row(), idx.column())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_painting = False
        super().mouseReleaseEvent(event)

# Main PyQt5 window that allows the user to:
# Enter grid size and initialize an empty grid.
# "Paint" colored regions by selecting cells (click‐and‐drag).
# Once every cell has a region, solve and display queens (👑).

class QueensWindow(QWidget):

    CELL_SIZE = 40  # size (px) of each cell

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Queens Solver")

        # Layouts
        main_layout = QVBoxLayout()
        controls_layout = QHBoxLayout()
        region_layout = QHBoxLayout()

        # Add back button using utility function
        back_button = create_back_button(self)
        back_button.clicked.connect(self.close)
        controls_layout.addWidget(back_button)
        controls_layout.addStretch()

        # Grid size controls
        controls_layout.addWidget(QLabel("Grid size:"))
        self.size_edit = QLineEdit()
        self.size_edit.setFixedWidth(40)
        self.size_edit.setText("6")
        controls_layout.addWidget(self.size_edit)

        self.init_button = QPushButton("Make Grid")
        self.init_button.clicked.connect(self.initialize_grid)
        controls_layout.addWidget(self.init_button)

        # Region controls
        self.add_region_button = QPushButton("Add Region")
        self.add_region_button.setEnabled(False)
        self.add_region_button.clicked.connect(self.start_new_region)
        region_layout.addWidget(self.add_region_button)

        self.done_region_button = QPushButton("Done Region")
        self.done_region_button.setEnabled(False)
        self.done_region_button.clicked.connect(self.finish_region)
        region_layout.addWidget(self.done_region_button)

        self.solve_button = QPushButton("Solve")
        self.solve_button.setEnabled(False)
        self.solve_button.clicked.connect(self.run_solver)
        region_layout.addWidget(self.solve_button)

        self.current_label = QLabel("No region")
        region_layout.addWidget(self.current_label)

        # Placeholder for the table, until initialize_grid() is used
        self.table = None

        # Add layouts to main layout
        main_layout.addLayout(controls_layout)
        main_layout.addLayout(region_layout)
        self.setLayout(main_layout)

        # Track internal state
        self.n = 0
        self.region_ids = []       # 2D array of integers (0 until assigned)
        self.region_colors = []    # 2D array of hex‐strings for background
        self.regions_defined = 0   # # of regions that are started so far
        self.current_region_id = None
        self.current_color = None  

    # Create an empty n×n RegionTable with white QLabel‐cells,
    # disable the default gridlines (we'll draw our own),
    # and prepare for region‐painting.
    def initialize_grid(self):
        # Get grid size from user input
        try:
            n = int(self.size_edit.text())
            if n <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.critical(self, "Error", "Grid size must be a positive integer.")
            return

        self.n = n
        self.region_ids = [[0] * n for _ in range(n)]
        self.region_colors = [["white"] * n for _ in range(n)]
        self.regions_defined = 0
        self.current_region_id = None
        self.current_color = None
        self.current_label.setText("No region")
        self.current_label.setStyleSheet("color: black;")

        # Delete any existing table
        if self.table:
            self.layout().removeWidget(self.table)
            self.table.deleteLater()

        # Create RegionTable
        self.table = RegionTable(n, self)
        self.table.setFixedSize(self.CELL_SIZE * n + 2, self.CELL_SIZE * n + 2)
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.setShowGrid(False)  # disable default gridlines

        # Populate cells with QLabel widgets
        for r in range(n):
            self.table.setRowHeight(r, self.CELL_SIZE)
            for c in range(n):
                self.table.setColumnWidth(c, self.CELL_SIZE)
                label = QLabel()
                label.setAlignment(Qt.AlignCenter)
                # Initial style: white bg, 1px lightgray border on all sides
                label.setStyleSheet(
                    "background-color: white; "
                    "border: 1px solid lightgray;"
                )
                self.table.setCellWidget(r, c, label)

        # Insert table into layout
        self.layout().addWidget(self.table)

        # Enable region buttons
        self.add_region_button.setEnabled(True)
        self.done_region_button.setEnabled(False)
        self.solve_button.setEnabled(False)
      
    # Assign a distinct color for each region by parsing through the hue wheel
    def start_new_region(self):

        if self.current_region_id is not None:
            QMessageBox.warning(self, "Warning", "Finish the current region first.")
            return

        self.regions_defined += 1
        self.current_region_id = self.regions_defined

        # Golden‐angle spacing round the hue wheel
        hue = int((self.regions_defined * 137.508) % 360)
        # Use high saturation/value for vivid color
        self.current_color = QColor.fromHsv(hue, 200, 255)

        self.current_label.setText(f"Region {self.current_region_id} ▶ {self.current_color.name()}")
        self.current_label.setStyleSheet(f"color: {self.current_color.name()};")

        self.add_region_button.setEnabled(False)
        self.done_region_button.setEnabled(True)

    # Finalize the current region:
    # Ensure at least one cell was painted, reset current state.
    # If all cells are assigned, enable "Solve."
    # Also recalculate borders since a region has just been closed.
    def finish_region(self):
        if self.current_region_id is None:
            return

        # Verify at least one cell was assigned this region
        found = any(
            self.region_ids[r][c] == self.current_region_id
            for r in range(self.n) for c in range(self.n)
        )
        if not found:
            QMessageBox.warning(self, "Warning", "You must paint at least one cell for this region.")
            return

        # Reset current region info
        self.current_region_id = None
        self.current_color = None
        self.current_label.setText("No region")
        self.current_label.setStyleSheet("color: black;")
        self.done_region_button.setEnabled(False)
        self.add_region_button.setEnabled(True)

        # Re‐draw all borders to outline each region
        self.update_all_borders()

        # Check if all cells have nonzero region_id
        all_assigned = all(
            self.region_ids[r][c] != 0
            for r in range(self.n) for c in range(self.n)
        )
        if all_assigned:
            self.solve_button.setEnabled(True)

    def paint_cell(self, row, col):
        if self.current_region_id is None:
            return
        if self.region_ids[row][col] != 0:
            return

        # Assign region ID and color
        self.region_ids[row][col] = self.current_region_id
        self.region_colors[row][col] = self.current_color.name()
        widget = self.table.cellWidget(row, col)
        widget.setStyleSheet(f"background-color: {self.current_color.name()};")

        # Re‐draw borders (light‐gray gridlines + black region borders)
        self.update_all_borders()

    # Loop through cells and assign a stylesheet that
    # Sets the background to the region's color and paints region edges
    def update_all_borders(self):
        for r in range(self.n):
            for c in range(self.n):
                rid = self.region_ids[r][c]
                bgcolor = self.region_colors[r][c]
                borders = []

                # Top edge
                if r == 0 or self.region_ids[r - 1][c] != rid:
                    borders.append("border-top: 1px solid black;")
                else:
                    borders.append("border-top: 1px solid lightgray;")

                # Right edge
                if c == self.n - 1 or self.region_ids[r][c + 1] != rid:
                    borders.append("border-right: 1px solid black;")
                else:
                    borders.append("border-right: 1px solid lightgray;")

                # Bottom edge
                if r == self.n - 1 or self.region_ids[r + 1][c] != rid:
                    borders.append("border-bottom: 1px solid black;")
                else:
                    borders.append("border-bottom: 1px solid lightgray;")

                # Left edge
                if c == 0 or self.region_ids[r][c - 1] != rid:
                    borders.append("border-left: 1px solid black;")
                else:
                    borders.append("border-left: 1px solid lightgray;")

                style = f"background-color: {bgcolor}; {' '.join(borders)}"
                widget = self.table.cellWidget(r, c)
                widget.setStyleSheet(style)

    def run_solver(self):
        # Double‐check all cells are assigned to a region
        for r in range(self.n):
            for c in range(self.n):
                if self.region_ids[r][c] == 0:
                    QMessageBox.critical(self, "Error", "All cells must be assigned to a region.")
                    return

        solver = QueensSolver(self.n, self.region_ids)
        solution = solver.solve()

        if solution is None:
            QMessageBox.information(
                self,
                "No solution",
                "No valid queen placement exists for this region layout."
            )
            return

        # Display queens
        crown_font = QFont("Arial", int(self.CELL_SIZE / 1.5))
        for r, c in enumerate(solution):
            widget = self.table.cellWidget(r, c)
            widget.setText("👑")
            widget.setFont(crown_font)
            widget.setAlignment(Qt.AlignCenter)
            widget.setStyleSheet(widget.styleSheet() + "color: black;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QueensWindow()
    window.show()
    sys.exit(app.exec_())