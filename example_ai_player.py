from typing import List, Optional
from collapsi_core import Position, Game
from player_interface import Player


class GreedyAIPlayer(Player):
    def __init__(self, player_id: int, name: str = None):
        if name is None:
            name = f"Greedy AI {player_id + 1}"
        super().__init__(player_id, name)
        
    def get_move(self, game: Game, valid_moves: List[List[Position]]) -> Optional[List[Position]]:
        if not valid_moves:
            return None
            
        best_move = None
        best_score = -1
        
        for move in valid_moves:
            score = self.evaluate_move(game, move)
            if score > best_score:
                best_score = score
                best_move = move
                
        return best_move
    
    def evaluate_move(self, game: Game, move: List[Position]) -> float:
        score = 0.0
        final_pos = move[-1]
        
        opponent_id = 1 - self.player_id
        opponent_pos = game.board.player_positions[opponent_id]
        
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if abs(dr) + abs(dc) == 1:
                    check_pos = Position(
                        (final_pos.row + dr) % game.board.size,
                        (final_pos.col + dc) % game.board.size
                    )
                    
                    card = game.board.get_card(check_pos)
                    if card and not card.is_collapsed and check_pos != opponent_pos:
                        score += 2.0
                        
        center = game.board.size // 2
        distance_to_center = abs(final_pos.row - center) + abs(final_pos.col - center)
        score += (game.board.size - distance_to_center) * 0.5
        
        distance_to_opponent = min(
            abs(final_pos.row - opponent_pos.row),
            game.board.size - abs(final_pos.row - opponent_pos.row)
        ) + min(
            abs(final_pos.col - opponent_pos.col),
            game.board.size - abs(final_pos.col - opponent_pos.col)
        )
        score += distance_to_opponent * 0.3
        
        return score


class DefensiveAIPlayer(Player):
    def __init__(self, player_id: int, name: str = None):
        if name is None:
            name = f"Defensive AI {player_id + 1}"
        super().__init__(player_id, name)
        
    def get_move(self, game: Game, valid_moves: List[List[Position]]) -> Optional[List[Position]]:
        if not valid_moves:
            return None
            
        best_move = None
        best_score = float('inf')
        
        for move in valid_moves:
            score = self.evaluate_risk(game, move)
            if score < best_score:
                best_score = score
                best_move = move
                
        return best_move
    
    def evaluate_risk(self, game: Game, move: List[Position]) -> float:
        risk = 0.0
        final_pos = move[-1]
        
        temp_board = self._simulate_move(game, move)
        
        high_value_cards_nearby = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if abs(dr) + abs(dc) == 1:
                    check_pos = Position(
                        (final_pos.row + dr) % game.board.size,
                        (final_pos.col + dc) % game.board.size
                    )
                    
                    card = temp_board.get_card(check_pos)
                    if card and not card.is_collapsed:
                        if card.value.value >= 3:
                            high_value_cards_nearby += 1
                            
        risk += high_value_cards_nearby * 10
        
        opponent_id = 1 - self.player_id
        opponent_pos = game.board.player_positions[opponent_id]
        opponent_card = game.board.get_card(opponent_pos)
        
        if opponent_card and not opponent_card.is_collapsed:
            opponent_reach = opponent_card.value.value
            distance = min(
                abs(final_pos.row - opponent_pos.row),
                game.board.size - abs(final_pos.row - opponent_pos.row)
            ) + min(
                abs(final_pos.col - opponent_pos.col),
                game.board.size - abs(final_pos.col - opponent_pos.col)
            )
            
            if distance <= opponent_reach:
                risk += 5
                
        return risk
    
    def _simulate_move(self, game: Game, move: List[Position]):
        from copy import deepcopy
        temp_board = deepcopy(game.board)
        start_pos = game.get_current_player_position()
        temp_board.collapse_card(start_pos)
        return temp_board