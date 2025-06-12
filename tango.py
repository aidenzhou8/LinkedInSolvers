import sys
from typing import Dict, List, Optional, Tuple

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QApplication, QFrame, QGridLayout, QHBoxLayout, QLabel, QMessageBox, QPushButton, QVBoxLayout, QWidget

from utils import create_back_button

# Constants and icons
BOARD_SIZE = 6           
CELL_PX = 56                # pixel size of each square
LINE_PX = 12                # grid line has to be thick enough to click and display "=" or "x"
LINE_COLOR = "#e6ddc6"      # subtle beige
EDGE_HITBOX = LINE_PX       # match hitbox to line thickness
SUN, MOON = 1, 0
SYMBOLS = {None: "", SUN: "☀", MOON: "🌙"}

# ConstraintKey is a tuple of two tuples, each representing a square of the board
ConstraintKey = Tuple[Tuple[int, int], Tuple[int, int]]

def key_of(a: Tuple[int, int], b: Tuple[int, int]) -> ConstraintKey:
    # Canonicalise cell pair so (p,q) == (q,p)
    return tuple(sorted((a, b)))

class TangoSolver:
    # Initialize the solver with the board size, board state, and constraints
    def __init__(self, n: int, board, constraints):
        self.n = n
        self.half = n // 2
        self.b = [row[:] for row in board]
        self.c = constraints.copy()

    # Check if a row has more than half its squares as sun or moon
    def _row_ok(self, r):
        row = self.b[r]
        if row.count(SUN) > self.half or row.count(MOON) > self.half:
            return False
        return all(row[i] == row[i + 1] == row[i + 2] is None or not (row[i] == row[i + 1] == row[i + 2]) for i in range(self.n - 2))

    # Check if a col has more than half its squares as sun or moon
    def _col_ok(self, c):
        col = [self.b[r][c] for r in range(self.n)]
        if col.count(SUN) > self.half or col.count(MOON) > self.half:
            return False
        return all(col[i] == col[i + 1] == col[i + 2] is None or not (col[i] == col[i + 1] == col[i + 2]) for i in range(self.n - 2))

    # Check if a given constraint is valid
    def _constraint_ok(self, r, c):
        # Check four directions (up, right, down, left)
        for dr, dc in ((0, 1), (1, 0), (0, -1), (-1, 0)):
            nr, nc = r + dr, c + dc
            if not (0 <= nr < self.n and 0 <= nc < self.n):
                continue
            k = key_of((r, c), (nr, nc))
            if k not in self.c:
                continue
            a, b = self.b[r][c], self.b[nr][nc]
            if a is None or b is None:
                continue
            rel = self.c[k]
            if rel == "=" and a != b:
                return False
            if rel == "x" and a == b:
                return False
        return True

    # Using the above helper functions, check if a given cell is valid
    def _valid(self, r, c):
        return self._row_ok(r) and self._col_ok(c) and self._constraint_ok(r, c)

    # Solve the board using backtracking
    def solve(self):
        for r in range(self.n):
            for c in range(self.n):
                if self.b[r][c] is None:
                    for v in (SUN, MOON):
                        self.b[r][c] = v
                        if self._valid(r, c):
                            res = self.solve()
                            if res is not None:
                                return res
                        self.b[r][c] = None
                    return None
                    
        if any(row.count(SUN) != self.half for row in self.b):
            return None
        if any([self.b[r][c] for r in range(self.n)].count(SUN) != self.half for c in range(self.n)):
            return None
        return [row[:] for row in self.b]

# GUI components

# Cell class

class Cell(QPushButton):
    # A single sun/moon/empty square.
    # Click on its edges once or twice to toggle the "=" or "x" constraint.

    def __init__(self, r: int, c: int, parent: "TangoBoard"):
        super().__init__("", parent)
        self.r, self.c = r, c
        self.val: Optional[int] = None
        self.setFixedSize(CELL_PX, CELL_PX)
        self.setStyleSheet("background:#fff; border:none;")
        self.setFont(parent.big_font)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.board = parent
        self.setText("")  # Ensure initial text is empty

    # Cycle through sun, moon, and empty
    def _cycle_val(self):
        if self.val is None:
            self.val = SUN
        elif self.val == SUN:
            self.val = MOON
        else:
            self.val = None
        self.setText(SYMBOLS[self.val])
        # Update color based on value
        if self.val == SUN:
            self.setStyleSheet("background:#fff; border:none; color: red;")
        else:
            self.setStyleSheet("background:#fff; border:none;")
        self.update()  

    def mousePressEvent(self, ev):  
        if ev.button() != Qt.MouseButton.LeftButton:
            return super().mousePressEvent(ev)

        x, y = ev.pos().x(), ev.pos().y()
        hit = EDGE_HITBOX
        # if right edge click
        if x >= CELL_PX - hit and self.c < BOARD_SIZE - 1:
            self.board.toggle_edge((self.r, self.c), (self.r, self.c + 1))
            return
        # if bottom edge click
        if y >= CELL_PX - hit and self.r < BOARD_SIZE - 1:
            self.board.toggle_edge((self.r, self.c), (self.r + 1, self.c))
            return
        # square click -> cycle sun/moon
        mods = QApplication.keyboardModifiers()
        if mods & Qt.KeyboardModifier.ShiftModifier:
            self.val = SUN
        elif mods & Qt.KeyboardModifier.ControlModifier:
            self.val = MOON
        else:
            self._cycle_val()
        self.setText(SYMBOLS[self.val])
        # Update color based on value
        if self.val == SUN:
            self.setStyleSheet("background:#fff; border:none; color: red;")
        else:
            self.setStyleSheet("background:#fff; border:none;")
        self.update()  # Force immediate update

# A thin beige line that can be clicked to toggle constraints.
class GridLine(QFrame):
    def __init__(self, horiz: bool, parent: QWidget, grid_row: int, grid_col: int):
        super().__init__(parent)
        self.setStyleSheet(f"background:{LINE_COLOR}; border:none;")
        self.setFixedSize(CELL_PX if horiz else LINE_PX, LINE_PX if horiz else CELL_PX)
        self.horiz = horiz
        self.grid_row = grid_row
        self.grid_col = grid_col
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

    def mousePressEvent(self, ev):  
        if ev.button() != Qt.MouseButton.LeftButton:
            return super().mousePressEvent(ev)
        
        # Convert grid position to square coordinates
        if self.horiz:
            # For horizontal lines, connect squares in same col
            row = self.grid_row // 2
            col = self.grid_col // 2
            self.parent().toggle_edge((row, col), (row + 1, col))
        else:
            # For vertical lines, connect squares in same row
            row = self.grid_row // 2
            col = self.grid_col // 2
            self.parent().toggle_edge((row, col), (row, col + 1))

# Board class

class TangoBoard(QWidget):
    def __init__(self):
        super().__init__()
        self.constraints: Dict[ConstraintKey, str] = {}
        self.big_font = self.font()
        self.big_font.setPointSize(22)

        layout = QGridLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.cells: List[List[Cell]] = []
        n = BOARD_SIZE
        for r in range(n):
            row: List[Cell] = []
            for c in range(n):
                cell = Cell(r, c, self)
                layout.addWidget(cell, 2 * r, 2 * c)
                row.append(cell)
                # vertical line to the right (except last column)
                if c < n - 1:
                    line = GridLine(False, self, 2 * r, 2 * c + 1)
                    layout.addWidget(line, 2 * r, 2 * c + 1)
                # horizontal line below (except last row)
                if r < n - 1:
                    line = GridLine(True, self, 2 * r + 1, 2 * c)
                    layout.addWidget(line, 2 * r + 1, 2 * c)
            self.cells.append(row)

    # Edge toggling
    def toggle_edge(self, a: Tuple[int, int], b: Tuple[int, int]):
        k = key_of(a, b)
        rel = self.constraints.get(k)
        rel = {None: "=", "=": "x", "x": None}[rel]
        if rel is None:
            self.constraints.pop(k, None)
        else:
            self.constraints[k] = rel
        # display icon near middle of the line using QLabel overlay
        self._paint_edge_label(a, b, rel)

    def _paint_edge_label(self, a: Tuple[int, int], b: Tuple[int, int], rel: Optional[str]):
        # find the line widget position in the layout and (re)label it
        r1, c1 = a
        r2, c2 = b
        horiz = r1 == r2
        row = 2 * r1 + (1 if not horiz else 0)
        col = 2 * c1 + (1 if horiz else 0)
        item = self.layout().itemAtPosition(row, col)
        if item is None:
            return
        line_w = item.widget()  
        # Remove previous label child, if any exists
        for child in line_w.children():
            if isinstance(child, QLabel):
                child.deleteLater()
        if rel is None:
            return
        lab = QLabel(rel, line_w)
        lab.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lab.setFont(self.font())
        lab.setStyleSheet("color: black; background: transparent;")
        lab.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        lab.raise_()  # Ensure the label is on top
        lab.resize(line_w.size())
        lab.show()

    # Utility functions
    def snapshot(self):
        return [[cell.val for cell in row] for row in self.cells]

    def clear(self):
        for row in self.cells:
            for cell in row:
                cell.val = None
                cell.setText("")
        self.constraints.clear()
        # Clear any edge labels
        for i in range(self.layout().count()):
            w = self.layout().itemAt(i).widget()
            for child in w.children():
                if isinstance(child, QLabel):
                    child.deleteLater()

# Main window

class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tango Solver")

        v = QVBoxLayout(self)
        
        # Add back button using utility function
        back_button = create_back_button(self)
        back_button.clicked.connect(self.close)
        v.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignLeft)
        
        self.board = TangoBoard()
        v.addWidget(self.board, alignment=Qt.AlignmentFlag.AlignCenter)

        btns = QHBoxLayout()
        solve = QPushButton("Solve")
        solve.clicked.connect(self._solve)
        clr = QPushButton("Clear")
        clr.clicked.connect(self.board.clear)
        btns.addWidget(solve)
        btns.addWidget(clr)
        v.addLayout(btns)

    def _solve(self):
        solver = TangoSolver(BOARD_SIZE, self.board.snapshot(), self.board.constraints)
        sol = solver.solve()
        if sol is None:
            QMessageBox.information(self, "Tango", "No solution found / invalid constraints.")
            return
        for r, row in enumerate(sol):
            for c, v in enumerate(row):
                cell = self.board.cells[r][c]
                cell.val = v
                cell.setText(SYMBOLS[v])
                # Apply red color for sun cells
                if v == SUN:
                    cell.setStyleSheet("background:#fff; border:none; color: red;")
                else:
                    cell.setStyleSheet("background:#fff; border:none;")
                cell.update()

# Run the app

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # consistent look across dark / light themes
    w = Main()
    w.show()
    sys.exit(app.exec())
