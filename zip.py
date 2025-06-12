# This solver handles boards of size up to 8x8 depending on your device;
# larger boards won't be instantaneous and probably require a faster algorithm. 

import sys
from typing import List, Optional, Tuple, Dict, Set
from PyQt5.QtCore import Qt, QRectF, QTimer
from PyQt5.QtGui import QPainter, QPen, QBrush, QFont
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QMessageBox, QLineEdit

from utils import create_back_button

Coord = Tuple[int, int]

# Depth-first back-tracking solver with simple pruning.
class ZipSolver:
    DIRS = [(-1, 0, "h"), (1, 0, "h"), (0, -1, "v"), (0, 1, "v")]

    def __init__(
        self,
        numbers: List[List[Optional[int]]],
        barriers_h: List[List[bool]],
        barriers_v: List[List[bool]],
    ):
        self.H, self.W = len(numbers), len(numbers[0])
        self.numbers = numbers
        self.bh = barriers_h               # between rows r-1 and r
        self.bv = barriers_v               # between cols c-1 and c
        self.total = self.H * self.W

        self.start: Optional[Coord] = None
        self.max_num = 0
        for r in range(self.H):
            for c in range(self.W):
                v = numbers[r][c]
                if v is not None:
                    self.max_num = max(self.max_num, v)
                    if v == 1:
                        self.start = (r, c)

        if self.start is None:
            raise ValueError("Place a '1' on the grid before solving.")

        self._found_path: List[Coord] = []
        self._visited = [[False] * self.W for _ in range(self.H)]

    # Overarching solve function
    def solve(self) -> Optional[List[Coord]]:
        self._dfs(self.start[0], self.start[1], 1, [])
        return self._found_path or None

    # Helper function: DFS to find a path that visits all cells in order
    def _dfs(
        self,
        r: int,
        c: int,
        expected_num: int,          # next mandatory number to hit
        path: List[Coord],
    ):
        if self._found_path:        # early exit once solution found
            return
        self._visited[r][c] = True
        path.append((r, c))

        cell_num = self.numbers[r][c]
        if cell_num is not None:            # must match expectation
            if cell_num != expected_num:
                self._visited[r][c] = False
                path.pop()
                return
            expected_num += 1               # next number to chase

        # All cells used?
        if len(path) == self.total:
            if expected_num - 1 == self.max_num:
                self._found_path = path.copy()
            self._visited[r][c] = False
            path.pop()
            return

        for nr, nc, kind in self._neigh(r, c):
            if self._visited[nr][nc]:
                continue
            self._dfs(nr, nc, expected_num, path)
            if self._found_path:
                break

        self._visited[r][c] = False
        path.pop()

    # Get neighbors of a cell (r, c)
    def _neigh(self, r: int, c: int):
        for dr, dc, etype in self.DIRS:
            nr, nc = r + dr, c + dc
            if not (0 <= nr < self.H and 0 <= nc < self.W):
                continue
            # Is a barrier between (r,c) and (nr,nc)?
            if etype == "h":
                row = min(r, nr) + 1
                if self.bh[row][c]:
                    continue
            else:
                col = min(c, nc) + 1
                if self.bv[r][col]:
                    continue
            yield nr, nc, etype


# PyQt GUI

# Interactive grid, enabling user to add numbers and barriers
# Displays solution path afterwards

class GridWidget(QWidget):
    # Constants
    GRID = 6              # default 6×6 board (can be changed by user)
    PAD = 40              # outer padding (pixels)
    CELL = 60             # square size  (pixels)
    BAR_W = 6             # barrier thickness
    # The constants below determine the animation speed and smoothness respectively 
    ANIMATION_SPEED = 5   # in ms
    ANIMATION_STEPS = 10  

    def __init__(self, rows: int = GRID, cols: int = GRID):
        super().__init__()
        self.rows, self.cols = rows, cols
        self.setFixedSize(
            self.PAD * 2 + self.cols * self.CELL,
            self.PAD * 2 + self.rows * self.CELL,
        )
        # model state
        self.numbers = [[None] * cols for _ in range(rows)]
        self.bh = [[False] * cols for _ in range(rows + 1)]      # horiz
        self.bv = [[False] * (cols + 1) for _ in range(rows)]    # vert
        self.path: List[Coord] = []
        self.next_number = 1  # Track the next number to place
        
        # Animation state
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._update_animation)
        self.animated_path: List[Coord] = []
        self.current_segment = 0
        self.interpolation_step = 0

    def _update_animation(self):
        if self.current_segment < len(self.path) - 1:
            if self.interpolation_step < self.ANIMATION_STEPS:
                self.interpolation_step += 1
            else:
                self.interpolation_step = 0
                self.current_segment += 1
            self.update()
        else:
            self.animation_timer.stop()

    def start_animation(self):
        self.animated_path = []
        self.current_segment = 0
        self.interpolation_step = 0
        self.animation_timer.start(self.ANIMATION_SPEED)

    # Helper functions

    # Find the cell at a given position
    def _cell_at(self, pos) -> Optional[Coord]:
        x = pos.x() - self.PAD
        y = pos.y() - self.PAD
        if x < 0 or y < 0:
            return None
        c, r = x // self.CELL, y // self.CELL
        if c >= self.cols or r >= self.rows:
            return None
        return int(r), int(c)

    # Find the closest edge to a given position
    def _closest_edge(self, pos) -> Optional[Tuple[str, int, int]]:
        """Return ('h', row, col) or ('v', row, col) for nearest edge
        within BAR_W px; else None."""
        x = pos.x() - self.PAD
        y = pos.y() - self.PAD
        if x < -self.BAR_W or y < -self.BAR_W:
            return None
        # horiz lines (between rows)
        r_line = round(y / self.CELL)
        dist_h = abs(y - r_line * self.CELL)
        # vert lines (between cols)
        c_line = round(x / self.CELL)
        dist_v = abs(x - c_line * self.CELL)

        if dist_h <= self.BAR_W and 0 <= r_line <= self.rows:
            c = int(x // self.CELL)
            if c < self.cols:
                return ("h", int(r_line), c)
        if dist_v <= self.BAR_W and 0 <= c_line <= self.cols:
            r = int(y // self.CELL)
            if r < self.rows:
                return ("v", r, int(c_line))
        return None

    # Mouse events
    def mousePressEvent(self, ev):
        self.path.clear()          # any click clears displayed path
        edge = self._closest_edge(ev.pos())
        if edge:
            kind, r, c = edge
            if kind == "h":
                self.bh[r][c] = not self.bh[r][c]
            else:
                self.bv[r][c] = not self.bv[r][c]
            self.update()
            return

        cell = self._cell_at(ev.pos())
        if not cell:
            return
        r, c = cell
        if ev.modifiers() & Qt.ControlModifier:
            self.numbers[r][c] = None
            # If we clear a number, update next_number to be the max + 1
            max_num = 0
            for row in self.numbers:
                for num in row:
                    if num is not None:
                        max_num = max(max_num, num)
            self.next_number = max_num + 1
        else:
            self.numbers[r][c] = self.next_number
            self.next_number += 1
        self.update()

    # Solution path animation
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)  # Enable antialiasing
        p.setRenderHint(QPainter.SmoothPixmapTransform)  # Smooth transformations
        p.setRenderHint(QPainter.HighQualityAntialiasing)  # Highest quality antialiasing
        # board background
        p.fillRect(self.rect(), QBrush(Qt.white))

        # draw path (if any) first, so grid is on top
        if self.path:
            pen = QPen(Qt.blue, 4)
            pen.setCapStyle(Qt.RoundCap)  # Round line endings
            pen.setJoinStyle(Qt.RoundJoin)  # Round line joins
            p.setPen(pen)
            
            # Draw completed segments
            for i in range(1, self.current_segment + 1):
                r0, c0 = self.path[i - 1]
                r1, c1 = self.path[i]
                p.drawLine(
                    int(self.PAD + c0 * self.CELL + self.CELL / 2),
                    int(self.PAD + r0 * self.CELL + self.CELL / 2),
                    int(self.PAD + c1 * self.CELL + self.CELL / 2),
                    int(self.PAD + r1 * self.CELL + self.CELL / 2),
                )
            
            # Draw interpolated current segment if animation is in progress
            if self.current_segment < len(self.path) - 1:
                r0, c0 = self.path[self.current_segment]
                r1, c1 = self.path[self.current_segment + 1]
                progress = self.interpolation_step / self.ANIMATION_STEPS
                
                x0 = self.PAD + c0 * self.CELL + self.CELL / 2
                y0 = self.PAD + r0 * self.CELL + self.CELL / 2
                x1 = self.PAD + c1 * self.CELL + self.CELL / 2
                y1 = self.PAD + r1 * self.CELL + self.CELL / 2
                
                current_x = x0 + (x1 - x0) * progress
                current_y = y0 + (y1 - y0) * progress
                
                p.drawLine(
                    int(x0),
                    int(y0),
                    int(current_x),
                    int(current_y)
                )
            # Draw remaining segments if animation is complete
            elif self.current_segment == len(self.path) - 1:
                for i in range(self.current_segment + 1, len(self.path)):
                    r0, c0 = self.path[i - 1]
                    r1, c1 = self.path[i]
                    p.drawLine(
                        int(self.PAD + c0 * self.CELL + self.CELL / 2),
                        int(self.PAD + r0 * self.CELL + self.CELL / 2),
                        int(self.PAD + c1 * self.CELL + self.CELL / 2),
                        int(self.PAD + r1 * self.CELL + self.CELL / 2),
                    )

        # grid lines
        thin_pen = QPen(Qt.black, 1)
        p.setPen(thin_pen)
        for r in range(self.rows + 1):
            y = self.PAD + r * self.CELL
            p.drawLine(self.PAD, y, self.PAD + self.cols * self.CELL, y)
        for c in range(self.cols + 1):
            x = self.PAD + c * self.CELL
            p.drawLine(x, self.PAD, x, self.PAD + self.rows * self.CELL)

        # barriers
        barrier_pen = QPen(Qt.black, self.BAR_W)
        p.setPen(barrier_pen)
        # horizontal
        for r in range(self.rows + 1):
            for c in range(self.cols):
                if self.bh[r][c]:
                    x1 = self.PAD + c * self.CELL
                    x2 = x1 + self.CELL
                    y = self.PAD + r * self.CELL
                    p.drawLine(x1, y, x2, y)
        # vertical
        for r in range(self.rows):
            for c in range(self.cols + 1):
                if self.bv[r][c]:
                    y1 = self.PAD + r * self.CELL
                    y2 = y1 + self.CELL
                    x = self.PAD + c * self.CELL
                    p.drawLine(x, y1, x, y2)

        # numbers
        font = QFont("Arial", 16, QFont.Bold)
        p.setFont(font)
        for r in range(self.rows):
            for c in range(self.cols):
                v = self.numbers[r][c]
                if v is not None:
                    rect = QRectF(
                        self.PAD + c * self.CELL,
                        self.PAD + r * self.CELL,
                        self.CELL,
                        self.CELL,
                    )
                    p.drawText(rect, Qt.AlignCenter, str(v))

    # Keyboard events
    def keyPressEvent(self, ev):
        if ev.key() in (Qt.Key_S, Qt.Key_Return):
            self.try_solve()
        elif ev.key() == Qt.Key_C:
            self.path.clear()
            self.animated_path.clear()
            self.animation_timer.stop()
            self.update()

    # Solve the puzzle
    def try_solve(self):
        try:
            solver = ZipSolver(self.numbers, self.bh, self.bv)
            res = solver.solve()
            if not res:
                QMessageBox.information(self, "Zip Solver", "No solution.")
                return
            self.path = res
            self.start_animation()
        except ValueError as e:
            QMessageBox.warning(self, "Zip Solver", str(e))


# Necessary to toggle between screens (size selection and game)
def create_zip_window(app=None):
    # Create the main window
    root = QWidget()
    root.setWindowTitle("Zip Solver")
    
    # Create stacked layout for switching between screens
    main_layout = QVBoxLayout()
    
    # Add back button using utility function
    back_button = create_back_button(root)
    back_button.clicked.connect(root.close)
    main_layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignLeft)
    
    # Size selection screen
    size_layout = QVBoxLayout()
    
    # Add size selection controls
    controls_layout = QHBoxLayout()
    controls_layout.addWidget(QLabel("Grid size:"))
    size_edit = QLineEdit()
    size_edit.setFixedWidth(40)
    size_edit.setText("6")
    controls_layout.addWidget(size_edit)
    
    start_button = QPushButton("Start")
    controls_layout.addWidget(start_button)
    
    size_layout.addLayout(controls_layout)
    
    # Game screen (initially empty)
    game_layout = QVBoxLayout()
    
    # Add both layouts to main layout
    main_layout.addLayout(size_layout)
    main_layout.addLayout(game_layout)
    root.setLayout(main_layout)
    
    def start_game():
        """Initialize the game with the selected grid size."""
        try:
            size = int(size_edit.text())
            if size <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.critical(root, "Error", "Grid size must be a positive integer.")
            return
        
        # Remove size selection layout
        main_layout.removeItem(size_layout)
        size_layout.setParent(None)
        
        # Create and add the grid
        grid = GridWidget(rows=size, cols=size)
        main_layout.addWidget(grid, alignment=Qt.AlignHCenter)
        
        # Add buttons
        btn_row = QHBoxLayout()
        solve_btn = QPushButton("Solve")
        clear_btn = QPushButton("Clear Path")
        btn_row.addWidget(solve_btn)
        btn_row.addWidget(clear_btn)
        main_layout.addLayout(btn_row)
        
        solve_btn.clicked.connect(grid.try_solve)
        clear_btn.clicked.connect(lambda: (grid.path.clear(), grid.update()))
    
    start_button.clicked.connect(start_game)
    return root

def main():
    app = QApplication(sys.argv)
    root = create_zip_window(app)
    root.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
