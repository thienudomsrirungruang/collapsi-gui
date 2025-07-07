from enum import Enum
from typing import List, Tuple, Optional, Set
from dataclasses import dataclass
import random
from abc import ABC, abstractmethod


class CardValue(Enum):
    JACK = 1
    ACE = 1
    TWO = 2
    THREE = 3
    FOUR = 4


@dataclass
class Card:
    value: CardValue
    is_collapsed: bool = False
    
    def __str__(self):
        if self.is_collapsed:
            return "X"
        return {
            CardValue.JACK: "J",
            CardValue.ACE: "1",
            CardValue.TWO: "2",
            CardValue.THREE: "3",
            CardValue.FOUR: "4"
        }[self.value]


@dataclass
class Position:
    row: int
    col: int
    
    def __eq__(self, other):
        return self.row == other.row and self.col == other.col
    
    def __hash__(self):
        return hash((self.row, self.col))


class Board:
    def __init__(self, size: int = 4):
        self.size = size
        self.grid: List[List[Optional[Card]]] = [[None for _ in range(size)] for _ in range(size)]
        self.player_positions = {0: None, 1: None}
        
    def setup_standard_game(self):
        deck = self._create_standard_deck()
        random.shuffle(deck)
        
        jack_count = 0
        for i in range(self.size):
            for j in range(self.size):
                card = deck.pop()
                self.grid[i][j] = card
                
                if card.value == CardValue.JACK and jack_count < 2:
                    self.player_positions[jack_count] = Position(i, j)
                    jack_count += 1
    
    def _create_standard_deck(self) -> List[Card]:
        deck = []
        deck.extend([Card(CardValue.JACK) for _ in range(2)])
        deck.extend([Card(CardValue.ACE) for _ in range(4)])
        deck.extend([Card(CardValue.TWO) for _ in range(4)])
        deck.extend([Card(CardValue.THREE) for _ in range(4)])
        deck.extend([Card(CardValue.FOUR) for _ in range(2)])
        return deck
    
    def get_card(self, pos: Position) -> Optional[Card]:
        return self.grid[pos.row][pos.col]
    
    def collapse_card(self, pos: Position):
        card = self.get_card(pos)
        if card:
            card.is_collapsed = True
    
    def is_valid_position(self, pos: Position) -> bool:
        return 0 <= pos.row < self.size and 0 <= pos.col < self.size
    
    def wrap_position(self, pos: Position) -> Position:
        return Position(pos.row % self.size, pos.col % self.size)


class MoveValidator:
    @staticmethod
    def get_possible_moves(board: Board, start_pos: Position, steps: int, 
                          current_player: int) -> List[List[Position]]:
        all_paths = []
        visited = set()
        current_path = []
        
        def dfs(pos: Position, remaining_steps: int):
            if remaining_steps == 0:
                if pos != start_pos and not board.get_card(pos).is_collapsed:
                    opponent_pos = board.player_positions[1 - current_player]
                    if opponent_pos != pos:
                        all_paths.append(current_path[:])
                return
            
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            
            for dr, dc in directions:
                new_pos = Position(pos.row + dr, pos.col + dc)
                new_pos = board.wrap_position(new_pos)
                
                if new_pos not in visited:
                    card = board.get_card(new_pos)
                    if card and not card.is_collapsed:
                        visited.add(new_pos)
                        current_path.append(new_pos)
                        dfs(new_pos, remaining_steps - 1)
                        current_path.pop()
                        visited.remove(new_pos)
        
        visited.add(start_pos)
        dfs(start_pos, steps)
        return all_paths
    
    @staticmethod
    def is_valid_move(board: Board, start_pos: Position, path: List[Position], 
                     current_player: int) -> bool:
        if not path:
            return False
            
        visited = {start_pos}
        current_pos = start_pos
        
        for next_pos in path:
            dr = next_pos.row - current_pos.row
            dc = next_pos.col - current_pos.col
            
            if abs(dr) > 1:
                dr = 1 if dr < 0 else -1
            if abs(dc) > 1:
                dc = 1 if dc < 0 else -1
                
            if abs(dr) + abs(dc) != 1:
                return False
                
            if next_pos in visited:
                return False
                
            card = board.get_card(next_pos)
            if not card or card.is_collapsed:
                return False
                
            visited.add(next_pos)
            current_pos = next_pos
        
        final_pos = path[-1]
        if final_pos == start_pos:
            return False
            
        opponent_pos = board.player_positions[1 - current_player]
        if opponent_pos == final_pos:
            return False
            
        return True


class GameState(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class Game:
    def __init__(self, board_size: int = 4):
        self.board = Board(board_size)
        self.current_player = 0
        self.state = GameState.NOT_STARTED
        self.winner = None
        self.move_history = []
        
    def start_game(self):
        self.board.setup_standard_game()
        self.state = GameState.IN_PROGRESS
        self.current_player = 0
        
    def get_current_player_position(self) -> Position:
        return self.board.player_positions[self.current_player]
    
    def get_required_steps(self) -> int:
        pos = self.get_current_player_position()
        card = self.board.get_card(pos)
        return card.value.value if card else 0
    
    def get_valid_moves(self) -> List[List[Position]]:
        pos = self.get_current_player_position()
        steps = self.get_required_steps()
        return MoveValidator.get_possible_moves(self.board, pos, steps, self.current_player)
    
    def make_move(self, path: List[Position]) -> bool:
        start_pos = self.get_current_player_position()
        
        if not MoveValidator.is_valid_move(self.board, start_pos, path, self.current_player):
            return False
        
        self.board.collapse_card(start_pos)
        
        final_pos = path[-1]
        self.board.player_positions[self.current_player] = final_pos
        
        self.move_history.append({
            'player': self.current_player,
            'from': start_pos,
            'to': final_pos,
            'path': path[:]
        })
        
        self.current_player = 1 - self.current_player
        
        if not self.get_valid_moves():
            self.state = GameState.FINISHED
            self.winner = 1 - self.current_player
            
        return True
    
    def is_game_over(self) -> bool:
        return self.state == GameState.FINISHED