# 📦 LinkedIn Puzzle Solvers

## 🌟 Highlights

- A local app for solving LinkedIn's daily puzzles, particularly Queens, Tango, and Zip.
- Uses backtracking and graph traversal techniques to quickly decode any puzzle board. 
- Includes a unified dashboard, interactive GUIs, and animations, built with PyQt5. 

## 🚀 Usage

```py
>>> import mypackage
>>> mypackage.do_stuff()
'Oh yeah!'
```


## ⬇️ Installation

Simple, understandable installation instructions!

```bash
pip install my-package
```

And be sure to specify any other minimum requirements like Python versions or operating systems.

*You may be inclined to add development instructions here, don't.*


## 💭 Feedback and Contributing

Add a link to the Discussions tab in your repo and invite users to open issues for bugs/feature requests.

This is also a great place to invite others to contribute in any ways that make sense for your project. Point people to your DEVELOPMENT and/or CONTRIBUTING guides if you have them.


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
