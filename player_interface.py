from abc import ABC, abstractmethod
from typing import List, Optional, Callable
from collapsi_core import Position, Game


class Player(ABC):
    def __init__(self, player_id: int, name: str):
        self.player_id = player_id
        self.name = name
        
    @abstractmethod
    def get_move(self, game: Game, valid_moves: List[List[Position]]) -> Optional[List[Position]]:
        pass
    
    def on_game_start(self, game: Game):
        pass
    
    def on_game_end(self, game: Game, winner: int):
        pass


class HumanPlayer(Player):
    def __init__(self, player_id: int, name: str):
        super().__init__(player_id, name)
        self.selected_move = None
        self.move_callback = None
        
    def set_move_callback(self, callback: Callable):
        self.move_callback = callback
        
    def get_move(self, game: Game, valid_moves: List[List[Position]]) -> Optional[List[Position]]:
        self.selected_move = None
        
        if self.move_callback:
            self.move_callback(valid_moves)
            
        return self.selected_move
    
    def select_move(self, move: List[Position]):
        self.selected_move = move


class RandomAIPlayer(Player):
    def __init__(self, player_id: int, name: str):
        super().__init__(player_id, name)
        
    def get_move(self, game: Game, valid_moves: List[List[Position]]) -> Optional[List[Position]]:
        if not valid_moves:
            return None
            
        import random
        return random.choice(valid_moves)