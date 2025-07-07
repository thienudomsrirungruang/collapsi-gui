import tkinter as tk
from tkinter import messagebox, ttk
from typing import List, Optional, Tuple
import threading
import time

from collapsi_core import Game, Position, GameState, CardValue
from player_interface import Player, HumanPlayer, RandomAIPlayer
from example_ai_player import GreedyAIPlayer, DefensiveAIPlayer


class CollapsiGUI:
    def __init__(self, master: tk.Tk):
        self.master = master
        self.master.title("Collapsi")
        self.master.configure(bg='#2b2b2b')
        
        self.game = Game()
        self.players = [None, None]
        self.current_valid_moves = []
        self.selected_path = []
        self.hovering_path = []
        self.animating = False
        
        self.cell_size = 80
        self.board_margin = 20
        
        self.colors = {
            'bg': '#2b2b2b',
            'board_bg': '#1e1e1e',
            'card_bg': '#f0f0f0',
            'collapsed': '#404040',
            'player1': '#3498db',
            'player2': '#e74c3c',
            'valid_move': '#2ecc71',
            'path': '#f39c12',
            'hover': '#95a5a6',
            'text': '#2c3e50'
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = tk.Frame(self.master, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        control_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        control_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        tk.Button(
            control_frame, 
            text="New Game", 
            command=self.show_new_game_dialog,
            bg='#3498db',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        self.status_label = tk.Label(
            control_frame,
            text="Click 'New Game' to start",
            bg=self.colors['bg'],
            fg='white',
            font=('Arial', 12)
        )
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        canvas_size = self.cell_size * 4 + self.board_margin * 2
        self.canvas = tk.Canvas(
            main_frame,
            width=canvas_size,
            height=canvas_size,
            bg=self.colors['board_bg'],
            highlightthickness=0
        )
        self.canvas.pack()
        
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        
        info_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        info_frame.pack(side=tk.TOP, fill=tk.X, pady=(10, 0))
        
        self.info_label = tk.Label(
            info_frame,
            text="",
            bg=self.colors['bg'],
            fg='white',
            font=('Arial', 10),
            justify=tk.LEFT
        )
        self.info_label.pack()
        
    def show_new_game_dialog(self):
        dialog = tk.Toplevel(self.master)
        dialog.title("New Game Setup")
        dialog.configure(bg=self.colors['bg'])
        dialog.geometry("400x300")
        
        tk.Label(
            dialog,
            text="Select Players",
            bg=self.colors['bg'],
            fg='white',
            font=('Arial', 14, 'bold')
        ).pack(pady=10)
        
        player_frames = []
        player_vars = []
        
        for i in range(2):
            frame = tk.Frame(dialog, bg=self.colors['bg'])
            frame.pack(pady=10)
            
            tk.Label(
                frame,
                text=f"Player {i + 1}:",
                bg=self.colors['bg'],
                fg='white',
                font=('Arial', 12)
            ).pack(side=tk.LEFT, padx=5)
            
            var = tk.StringVar(value="Human")
            player_vars.append(var)
            
            ttk.Combobox(
                frame,
                textvariable=var,
                values=["Human", "Random AI", "Greedy AI", "Defensive AI"],
                state="readonly",
                width=15
            ).pack(side=tk.LEFT)
            
            player_frames.append(frame)
        
        button_frame = tk.Frame(dialog, bg=self.colors['bg'])
        button_frame.pack(pady=20)
        
        def start_game():
            self.players[0] = self.create_player(0, player_vars[0].get())
            self.players[1] = self.create_player(1, player_vars[1].get())
            dialog.destroy()
            self.start_new_game()
        
        tk.Button(
            button_frame,
            text="Start Game",
            command=start_game,
            bg='#27ae60',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            bg='#e74c3c',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
    def create_player(self, player_id: int, player_type: str) -> Player:
        if player_type == "Human":
            player = HumanPlayer(player_id, f"Human Player {player_id + 1}")
            player.set_move_callback(self.on_human_turn)
            return player
        elif player_type == "Random AI":
            return RandomAIPlayer(player_id, f"Random AI {player_id + 1}")
        elif player_type == "Greedy AI":
            return GreedyAIPlayer(player_id)
        elif player_type == "Defensive AI":
            return DefensiveAIPlayer(player_id)
        
    def start_new_game(self):
        self.game = Game()
        self.game.start_game()
        self.current_valid_moves = []
        self.selected_path = []
        self.update_display()
        self.play_turn()
        
    def play_turn(self):
        if self.game.is_game_over():
            self.show_game_over()
            return
            
        current_player = self.players[self.game.current_player]
        self.current_valid_moves = self.game.get_valid_moves()
        
        if not self.current_valid_moves:
            self.game.state = GameState.FINISHED
            self.game.winner = 1 - self.game.current_player
            self.show_game_over()
            return
        
        self.update_status()
        
        if isinstance(current_player, HumanPlayer):
            self.highlight_valid_moves()
        else:
            self.master.after(500, self.ai_make_move)
            
    def ai_make_move(self):
        if self.animating:
            return
            
        current_player = self.players[self.game.current_player]
        move = current_player.get_move(self.game, self.current_valid_moves)
        
        if move:
            self.animate_move(move)
            
    def on_human_turn(self, valid_moves: List[List[Position]]):
        self.current_valid_moves = valid_moves
        self.highlight_valid_moves()
        
    def on_click(self, event):
        if self.animating:
            return
            
        if self.game.state != GameState.IN_PROGRESS:
            return
            
        current_player = self.players[self.game.current_player]
        if not isinstance(current_player, HumanPlayer):
            return
            
        x = (event.x - self.board_margin) // self.cell_size
        y = (event.y - self.board_margin) // self.cell_size
        
        if 0 <= x < 4 and 0 <= y < 4:
            clicked_pos = Position(y, x)
            
            for move in self.current_valid_moves:
                if move[-1] == clicked_pos:
                    self.animate_move(move)
                    return
                    
    def on_mouse_move(self, event):
        if self.animating or self.game.state != GameState.IN_PROGRESS:
            return
            
        current_player = self.players[self.game.current_player]
        if not isinstance(current_player, HumanPlayer):
            return
            
        x = (event.x - self.board_margin) // self.cell_size
        y = (event.y - self.board_margin) // self.cell_size
        
        if 0 <= x < 4 and 0 <= y < 4:
            hover_pos = Position(y, x)
            
            for move in self.current_valid_moves:
                if move[-1] == hover_pos:
                    if self.hovering_path != move:
                        self.hovering_path = move
                        self.update_display()
                    return
                    
        if self.hovering_path:
            self.hovering_path = []
            self.update_display()
            
    def animate_move(self, move: List[Position]):
        self.animating = True
        
        def animate():
            for i, pos in enumerate(move):
                self.selected_path = move[:i+1]
                self.update_display()
                time.sleep(0.2)
                
            self.game.make_move(move)
            self.selected_path = []
            self.hovering_path = []
            self.animating = False
            
            self.master.after(100, self.after_move)
            
        thread = threading.Thread(target=animate)
        thread.daemon = True
        thread.start()
        
    def after_move(self):
        self.update_display()
        self.play_turn()
        
    def highlight_valid_moves(self):
        self.update_display()
        
    def update_display(self):
        self.canvas.delete("all")
        
        for row in range(4):
            for col in range(4):
                x = col * self.cell_size + self.board_margin
                y = row * self.cell_size + self.board_margin
                
                pos = Position(row, col)
                card = self.game.board.get_card(pos)
                
                if card.is_collapsed:
                    color = self.colors['collapsed']
                else:
                    color = self.colors['card_bg']
                    
                is_valid_end = any(move[-1] == pos for move in self.current_valid_moves)
                if is_valid_end and isinstance(self.players[self.game.current_player], HumanPlayer):
                    color = self.colors['valid_move']
                    
                if pos in self.selected_path:
                    color = self.colors['path']
                elif pos in self.hovering_path:
                    color = self.colors['hover']
                
                self.canvas.create_rectangle(
                    x + 2, y + 2,
                    x + self.cell_size - 2, y + self.cell_size - 2,
                    fill=color,
                    outline='#666666',
                    width=2
                )
                
                if not card.is_collapsed:
                    self.canvas.create_text(
                        x + self.cell_size // 2,
                        y + self.cell_size // 2,
                        text=str(card),
                        font=('Arial', 24, 'bold'),
                        fill=self.colors['text']
                    )
                
                for player_id, player_pos in self.game.board.player_positions.items():
                    if player_pos == pos:
                        player_color = self.colors['player1'] if player_id == 0 else self.colors['player2']
                        # Draw smaller player piece in the corner
                        piece_size = 25
                        offset = 5
                        self.canvas.create_oval(
                            x + self.cell_size - piece_size - offset,
                            y + offset,
                            x + self.cell_size - offset,
                            y + piece_size + offset,
                            fill=player_color,
                            outline='white',
                            width=2
                        )
                        self.canvas.create_text(
                            x + self.cell_size - piece_size//2 - offset,
                            y + piece_size//2 + offset,
                            text=f"P{player_id + 1}",
                            font=('Arial', 10, 'bold'),
                            fill='white'
                        )
                        
    def update_status(self):
        if self.game.state == GameState.IN_PROGRESS:
            player = self.players[self.game.current_player]
            steps = self.game.get_required_steps()
            self.status_label.config(
                text=f"{player.name}'s turn - Must move {steps} steps"
            )
            
            pos = self.game.get_current_player_position()
            card = self.game.board.get_card(pos)
            valid_count = len(self.current_valid_moves)
            
            self.info_label.config(
                text=f"Current card: {card} | Valid moves: {valid_count}"
            )
            
    def show_game_over(self):
        winner = self.players[self.game.winner]
        self.status_label.config(text=f"Game Over! {winner.name} wins!")
        
        messagebox.showinfo(
            "Game Over",
            f"{winner.name} wins!\n\nTotal moves: {len(self.game.move_history)}"
        )


def main():
    root = tk.Tk()
    app = CollapsiGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()