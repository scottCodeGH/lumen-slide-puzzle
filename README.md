# Lumen Slide Puzzle Game

A beautiful and polished sliding tile puzzle game built with Python and Pygame. Perfect for casual gamers who enjoy a quick, engaging puzzle challenge!

## Features

- **Classic 4x4 Sliding Puzzle**: Rearrange scrambled tiles to complete the picture
- **Smooth Animations**: Polished tile sliding animations for a satisfying experience
- **Move Counter & Timer**: Track your performance and challenge yourself to improve
- **Beautiful Visuals**: Eye-catching gradient design with geometric patterns
- **Responsive Controls**: Click tiles or use arrow keys to play
- **Instant Reset**: Start a new game anytime with the "New Game" button
- **Guaranteed Solvable**: Puzzles are always generated with valid solutions

## How to Play

1. The puzzle starts with a scrambled 4x4 grid of tiles
2. One space is empty - click an adjacent tile or use arrow keys to slide it into the empty space
3. Continue sliding tiles until the picture is complete
4. Try to solve it in as few moves as possible!

### Controls

- **Mouse**: Click on any tile adjacent to the empty space to slide it
- **Arrow Keys**: Press arrow keys to move tiles (↑ ↓ ← →)
- **New Game Button**: Click to shuffle and start a fresh puzzle

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd lumen-slide-puzzle
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Game

Simply run the main Python file:

```bash
python sliding_puzzle.py
```

Or make it executable (Linux/Mac):

```bash
chmod +x sliding_puzzle.py
./sliding_puzzle.py
```

## Customization

You can easily adjust the difficulty by changing the grid size in `sliding_puzzle.py`:

- **Easy Mode (3x3)**: Change `game = SlidingPuzzle(grid_size=4)` to `grid_size=3`
- **Classic Mode (4x4)**: Default setting
- **Hard Mode (5x5)**: Change to `grid_size=5` (requires window size adjustment)

## Game Design

This game follows casual gaming principles:
- Quick sessions (solvable in a few minutes)
- Clear, intuitive interface
- Immediate feedback on actions
- Beautiful, relaxing visuals
- Simple but engaging gameplay

## Technical Details

- **Language**: Python 3
- **Framework**: Pygame 2.5+
- **Architecture**: Object-oriented design with clean separation of concerns
- **Animation**: Smooth interpolation for professional feel
- **Solvability**: Puzzles generated using valid move sequences to guarantee solutions

## License

MIT License - feel free to use and modify!

## Credits

Created with Pygame - a set of Python modules designed for writing video games.
