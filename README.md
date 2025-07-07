# Collapsi Python Implementation

A Python implementation of the Collapsi board game with a graphical user interface and support for AI players.

## Features

- Full implementation of Collapsi game rules
- Graphical user interface using tkinter
- Support for Human vs Human, Human vs AI, or AI vs AI games
- Multiple AI player types:
  - Random AI: Makes random valid moves
  - Greedy AI: Maximizes board control and position
  - Defensive AI: Minimizes risk and avoids dangerous positions
- Move visualization and animation
- Clean architecture for easy extension with custom AI players

## Requirements

- Python 3.7+
- tkinter (usually comes with Python)

## Usage

Run the game:
```bash
python collapsi_gui.py
```

## Creating Custom AI Players

To create your own AI player, extend the `Player` class from `player_interface.py`:

```python
from player_interface import Player
from collapsi_core import Game, Position
from typing import List, Optional

class MyCustomAI(Player):
    def __init__(self, player_id: int, name: str = None):
        super().__init__(player_id, name or f"Custom AI {player_id + 1}")
        
    def get_move(self, game: Game, valid_moves: List[List[Position]]) -> Optional[List[Position]]:
        # Implement your AI logic here
        # Return one of the valid_moves or None
        pass
```

Then import your AI in `collapsi_gui.py` and add it to the player options.

## Architecture

- `collapsi_core.py`: Core game logic, board management, and move validation
- `player_interface.py`: Player interface and basic player implementations
- `example_ai_player.py`: Example AI implementations (Greedy and Defensive)
- `collapsi_gui.py`: Tkinter-based graphical user interface

## Game Rules

Collapsi is a 2-player strategy game where players move around a 4x4 grid of cards. The last player able to make a legal move wins. Key rules:

- Players start on Jack cards and must move the number of spaces shown on their current card
- After moving, the starting card "collapses" and cannot be used again
- Movement is orthogonal (up/down/left/right) and the board wraps around
- Players cannot land on collapsed cards or their opponent's position
- The game ends when a player cannot complete their required move