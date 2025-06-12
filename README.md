# LinkedIn Puzzle Solvers

A unified dashboard application for solving various LinkedIn puzzles, including Queens, Tango, and Zip puzzles. Built with Python and PyQt5, this application provides an intuitive interface for puzzle solving with visual feedback and animations.

## Features

### Dashboard
- Modern, responsive interface with game selection cards
- Consistent styling across all solvers
- Easy navigation between different puzzle types

### Queens Puzzle Solver
- Interactive grid for creating regions
- Click-and-drag interface for region creation
- Automatic color assignment for distinct regions
- Visual solution display with crown emojis (👑)
- Enforces puzzle rules:
  - One queen per row
  - One queen per column
  - One queen per region
  - No adjacent queens (including diagonals)

### Tango Puzzle Solver
- 6x6 grid for sun (☀) and moon (🌙) placement
- Interactive constraint setting between cells
- Visual feedback for constraints (= and ×)
- Automatic solution finding
- Enforces puzzle rules:
  - Equal number of suns and moons in each row/column
  - No three consecutive same symbols
  - Respects cell constraints

### Zip Puzzle Solver
- Customizable grid size
- Interactive number placement
- Barrier creation between cells
- Animated solution path
- Enforces puzzle rules:
  - Path must visit all cells
  - Numbers must be visited in sequence
  - Barriers prevent movement

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/LinkedinSolver.git
cd LinkedinSolver
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Launch the dashboard:
```bash
python dashboard.py
```

2. Select a puzzle type from the dashboard:
   - Click on the Queens card to solve region-based queen placement puzzles
   - Click on the Tango card to solve sun/moon placement puzzles
   - Click on the Zip card to solve path-finding puzzles

3. Use the back button (←) in any solver to return to the dashboard

## Requirements

- Python 3.6 or higher
- PyQt5
- Futura font (system font on MacOS)

## Project Structure

```
LinkedinSolver/
├── dashboard.py      # Main dashboard application
├── queens.py         # Queens puzzle solver
├── tango.py          # Tango puzzle solver
├── zip.py            # Zip puzzle solver
├── requirements.txt  # Python dependencies
└── resources/        # Icons and assets
```

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 