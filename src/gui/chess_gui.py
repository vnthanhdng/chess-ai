"""Tkinter-based GUI for chess board visualization."""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import chess
import threading
import time
from typing import Optional, Callable
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.agents.base_agent import BaseAgent
from evaluation import evaluate


class ChessGUI:
    """GUI application for displaying and interacting with chess games."""
    
    # Unicode chess piece symbols
    PIECE_SYMBOLS = {
        chess.PAWN: {'white': '♙', 'black': '♟'},
        chess.ROOK: {'white': '♖', 'black': '♜'},
        chess.KNIGHT: {'white': '♘', 'black': '♞'},
        chess.BISHOP: {'white': '♗', 'black': '♝'},
        chess.QUEEN: {'white': '♕', 'black': '♛'},
        chess.KING: {'white': '♔', 'black': '♚'},
    }
    
    # Colors for light and dark squares
    LIGHT_SQUARE = '#f0d9b5'
    DARK_SQUARE = '#b58863'
    SELECTED_SQUARE = '#f6f669'
    LAST_MOVE_SQUARE = '#cdd26a'
    
    def __init__(self, board: Optional[chess.Board] = None, title: str = "Chess Game"):
        """
        Initialize the chess GUI.
        
        Args:
            board: Initial chess board state (default: starting position)
            title: Window title
        """
        if board is None:
            self.board = chess.Board()
        else:
            self.board = board.copy()  # Use a copy to avoid modifying the original
        self.root = tk.Tk()
        self.root.title(title)
        self.root.resizable(False, False)
        
        # Game state
        self.selected_square = None
        self.last_move = None
        self.last_move_san = None  # Store SAN of last move to avoid recalculating
        self.move_history_sans = []  # Store SANs of moves as they're made
        self.move_callback = None
        self.auto_play = False
        self.auto_play_delay = 1.0  # seconds between moves
        
        # Create UI
        self._create_widgets()
        self._update_display()
        
    def _create_widgets(self):
        """Create and layout all GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Left side: Board
        board_frame = ttk.Frame(main_frame)
        board_frame.grid(row=0, column=0, padx=10)
        
        # Board canvas
        self.board_canvas = tk.Canvas(
            board_frame, 
            width=480, 
            height=480,
            highlightthickness=2,
            highlightbackground='black'
        )
        self.board_canvas.grid(row=0, column=0)
        self.board_canvas.bind('<Button-1>', self._on_square_click)
        
        # Right side: Controls and info
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=0, column=1, padx=10, sticky=(tk.N, tk.W))
        
        # Game info
        info_label = ttk.Label(control_frame, text="Game Information", font=('Arial', 12, 'bold'))
        info_label.grid(row=0, column=0, pady=(0, 10))
        
        self.status_label = ttk.Label(control_frame, text="", font=('Arial', 10))
        self.status_label.grid(row=1, column=0, pady=5, sticky=tk.W)
        
        self.turn_label = ttk.Label(control_frame, text="", font=('Arial', 10))
        self.turn_label.grid(row=2, column=0, pady=5, sticky=tk.W)
        
        self.eval_label = ttk.Label(control_frame, text="", font=('Arial', 10))
        self.eval_label.grid(row=3, column=0, pady=5, sticky=tk.W)
        
        # Move input
        move_frame = ttk.LabelFrame(control_frame, text="Enter Move", padding=10)
        move_frame.grid(row=4, column=0, pady=10, sticky=(tk.W, tk.E))
        
        self.move_entry = ttk.Entry(move_frame, width=20, font=('Arial', 11))
        self.move_entry.grid(row=0, column=0, padx=5, pady=5)
        self.move_entry.bind('<Return>', lambda e: self._make_move_from_entry())
        
        move_button = ttk.Button(move_frame, text="Make Move", command=self._make_move_from_entry)
        move_button.grid(row=0, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=5, column=0, pady=10, sticky=(tk.W, tk.E))
        
        self.undo_button = ttk.Button(button_frame, text="Undo Move", command=self._undo_move)
        self.undo_button.grid(row=0, column=0, padx=5, pady=5)
        
        reset_button = ttk.Button(button_frame, text="Reset Board", command=self._reset_board)
        reset_button.grid(row=0, column=1, padx=5, pady=5)
        
        # Move history
        history_label = ttk.Label(control_frame, text="Move History", font=('Arial', 10, 'bold'))
        history_label.grid(row=6, column=0, pady=(10, 5), sticky=tk.W)
        
        self.history_text = scrolledtext.ScrolledText(
            control_frame, 
            width=30, 
            height=15,
            font=('Courier', 9),
            wrap=tk.WORD
        )
        self.history_text.grid(row=7, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Auto-play controls (for watching agents)
        auto_frame = ttk.LabelFrame(control_frame, text="Auto-Play", padding=10)
        auto_frame.grid(row=8, column=0, pady=10, sticky=(tk.W, tk.E))
        
        self.auto_play_var = tk.BooleanVar()
        auto_check = ttk.Checkbutton(
            auto_frame, 
            text="Auto-play moves", 
            variable=self.auto_play_var,
            command=self._toggle_auto_play
        )
        auto_check.grid(row=0, column=0, sticky=tk.W)
        
        delay_frame = ttk.Frame(auto_frame)
        delay_frame.grid(row=1, column=0, pady=5, sticky=tk.W)
        
        ttk.Label(delay_frame, text="Delay (s):").grid(row=0, column=0, padx=5)
        self.delay_var = tk.DoubleVar(value=1.0)
        delay_spin = ttk.Spinbox(
            delay_frame, 
            from_=0.1, 
            to=5.0, 
            increment=0.1, 
            width=8,
            textvariable=self.delay_var,
            command=self._update_delay
        )
        delay_spin.grid(row=0, column=1, padx=5)
        
    def _draw_board(self):
        """Draw the chess board on the canvas."""
        # Clear the canvas completely
        self.board_canvas.delete("all")
        
        square_size = 60
        
        # Draw squares with white at bottom (rank 0 = a1 at bottom, rank 7 = a8 at top)
        # Visual: visual_rank 0 at top shows chess rank 7 (black), visual_rank 7 at bottom shows chess rank 0 (white)
        for visual_rank in range(8):
            for file in range(8):
                x1 = file * square_size
                y1 = visual_rank * square_size  # visual rank 0 at top (y=0), visual rank 7 at bottom (y=420)
                x2 = x1 + square_size
                y2 = y1 + square_size
                
                # Map visual rank to chess rank: visual 0 (top) = chess 7 (black), visual 7 (bottom) = chess 0 (white)
                chess_rank = 7 - visual_rank
                square = chess.square(file, chess_rank)
                
                # Determine square color based on chess coordinates (not visual)
                is_light = (chess_rank + file) % 2 == 0
                color = self.LIGHT_SQUARE if is_light else self.DARK_SQUARE
                if self.selected_square == square:
                    color = self.SELECTED_SQUARE
                elif self.last_move and (square == self.last_move.from_square or square == self.last_move.to_square):
                    # Only highlight last move if no square is selected
                    if self.selected_square is None:
                        color = self.LAST_MOVE_SQUARE
                
                # Draw square
                self.board_canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline='black',
                    width=1,
                    tags=f"square_{square}"
                )
                
                # Draw piece if present
                piece = self.board.piece_at(square)
                if piece:
                    symbol = self.PIECE_SYMBOLS[piece.piece_type][
                        'white' if piece.color == chess.WHITE else 'black'
                    ]
                    center_x = x1 + square_size // 2
                    center_y = y1 + square_size // 2
                    self.board_canvas.create_text(
                        center_x, center_y,
                        text=symbol,
                        font=('Arial', 36, 'bold'),
                        fill='white' if piece.color == chess.WHITE else 'black'
                    )
        
        # Draw file labels (a-h)
        for file in range(8):
            label = chr(ord('a') + file)
            x = file * square_size + square_size // 2
            self.board_canvas.create_text(x, 470, text=label, font=('Arial', 10))
        
        # Draw rank labels (1-8) - visual rank 0 shows as 8 (black's rank), visual rank 7 shows as 1 (white's rank)
        for visual_rank in range(8):
            chess_rank = 7 - visual_rank  # Flip: visual 0 = chess 7, visual 7 = chess 0
            label = str(chess_rank + 1)  # chess rank 0 -> "1", chess rank 7 -> "8"
            y = visual_rank * square_size + square_size // 2  # Match board orientation
            self.board_canvas.create_text(470, y, text=label, font=('Arial', 10))
    
    def _update_display(self):
        """Update all display elements."""
        self._draw_board()
        
        # Update status
        if self.board.is_checkmate():
            status = "Checkmate!"
            winner = "Black" if self.board.turn == chess.WHITE else "White"
            status += f" - {winner} wins!"
        elif self.board.is_stalemate():
            status = "Stalemate - Draw"
        elif self.board.is_check():
            status = "Check!"
        elif self.board.is_game_over():
            status = "Game Over - Draw"
        else:
            status = "In Progress"
        
        self.status_label.config(text=f"Status: {status}")
        
        # Update turn
        turn = "White" if self.board.turn == chess.WHITE else "Black"
        self.turn_label.config(text=f"Turn: {turn}")
        
        # Update evaluation
        try:
            score = evaluate(self.board)
            score_display = score / 100.0
            if score > 0:
                eval_text = f"Evaluation: +{score_display:.2f} (White advantage)"
            elif score < 0:
                eval_text = f"Evaluation: {score_display:.2f} (Black advantage)"
            else:
                eval_text = "Evaluation: 0.00 (Equal)"
            self.eval_label.config(text=eval_text)
        except:
            self.eval_label.config(text="Evaluation: N/A")
    
    def _on_square_click(self, event):
        """Handle mouse click on board square."""
        square_size = 60
        file = event.x // square_size
        visual_rank = event.y // square_size  # Visual rank (0=top on screen, 7=bottom)
        rank = 7 - visual_rank  # Convert visual rank to chess rank (0=bottom, 7=top)
        
        print(f"[_on_square_click] Click at screen ({event.x}, {event.y}) -> file={file}, visual_rank={visual_rank}, chess_rank={rank}")
        
        if 0 <= file < 8 and 0 <= rank < 8:
            square = chess.square(file, rank)
            print(f"[_on_square_click] Square: {square} ({chess.square_name(square)})")
            print(f"[_on_square_click] Current turn: {'White' if self.board.turn == chess.WHITE else 'Black'}")
            print(f"[_on_square_click] Selected square: {self.selected_square}")
            
            if self.selected_square is None:
                # Select square
                piece = self.board.piece_at(square)
                print(f"[_on_square_click] Piece at square: {piece}")
                if piece and piece.color == self.board.turn:
                    print(f"[_on_square_click] Selecting square {square} (piece: {piece})")
                    self.selected_square = square
                    self._update_display()
                else:
                    if piece:
                        print(f"[_on_square_click] Cannot select: piece color {piece.color} != turn {self.board.turn}")
                    else:
                        print(f"[_on_square_click] Cannot select: no piece at square")
            else:
                # Try to make move
                print(f"[_on_square_click] Attempting move from {self.selected_square} to {square}")
                move = chess.Move(self.selected_square, square)
                
                # Check for pawn promotion (rank 0 or 7 in chess coordinates)
                if (self.board.piece_at(self.selected_square) and
                    self.board.piece_at(self.selected_square).piece_type == chess.PAWN and
                    (rank == 0 or rank == 7)):
                    # Default to queen promotion
                    move = chess.Move(self.selected_square, square, promotion=chess.QUEEN)
                
                if move in self.board.legal_moves:
                    print(f"[_on_square_click] Making move: {move}")
                    self._make_move(move)
                    print(f"[_on_square_click] Move completed. Turn now: {'White' if self.board.turn == chess.WHITE else 'Black'}")
                else:
                    print(f"[_on_square_click] Invalid move: {move}. Legal moves: {list(self.board.legal_moves)[:5]}...")
                    # Invalid move, just change selection
                    piece = self.board.piece_at(square)
                    if piece and piece.color == self.board.turn:
                        self.selected_square = square
                    else:
                        self.selected_square = None
                    self._update_display()
    
    def _make_move_from_entry(self):
        """Make a move from the text entry field."""
        move_str = self.move_entry.get().strip()
        if not move_str:
            return
        
        print(f"[_make_move_from_entry] Parsing move: '{move_str}'")
        try:
            # Try UCI format
            if len(move_str) in [4, 5]:
                move = chess.Move.from_uci(move_str)
            else:
                # Try SAN format
                move = self.board.parse_san(move_str)
            
            print(f"[_make_move_from_entry] Parsed move: {move}")
            if move in self.board.legal_moves:
                print(f"[_make_move_from_entry] Move is legal, calling _make_move()")
                self._make_move(move)
                self.move_entry.delete(0, tk.END)
            else:
                print(f"[_make_move_from_entry] Move is not legal!")
                messagebox.showerror("Invalid Move", "That move is not legal.")
        except (ValueError, chess.InvalidMoveError, chess.IllegalMoveError) as e:
            print(f"[_make_move_from_entry] ERROR parsing move: {e}")
            messagebox.showerror("Invalid Move", f"Could not parse move: {move_str}\n{e}")
    
    def _make_move(self, move: chess.Move):
        """Make a move on the board and update display."""
        print(f"[_make_move] ENTER: move={move}, turn={'White' if self.board.turn == chess.WHITE else 'Black'}, legal_moves_count={len(list(self.board.legal_moves))}")
        print(f"[_make_move] Board FEN before: {self.board.fen()}")
        
        # Verify move is legal before proceeding
        if move not in self.board.legal_moves:
            print(f"[_make_move] ERROR: Move {move} is not legal! Legal moves: {list(self.board.legal_moves)[:5]}...")
            return
        
        # Get SAN notation BEFORE pushing the move
        try:
            move_san = self.board.san(move)
            print(f"[_make_move] Got SAN: {move_san}")
        except Exception as e:
            print(f"[_make_move] ERROR getting SAN: {e}")
            print(f"[_make_move] Move: {move}, Board FEN: {self.board.fen()}")
            return
        
        move_num_before = len(self.board.move_stack)
        is_white_move = self.board.turn == chess.WHITE
        print(f"[_make_move] move_num_before={move_num_before}, is_white_move={is_white_move}")
        
        # Push the move
        print(f"[_make_move] Pushing move {move} to board...")
        self.board.push(move)
        self.last_move = move
        self.last_move_san = move_san  # Store SAN
        self.selected_square = None
        print(f"[_make_move] Move pushed. New FEN: {self.board.fen()}")
        print(f"[_make_move] New turn: {'White' if self.board.turn == chess.WHITE else 'Black'}")
        print(f"[_make_move] Move stack length: {len(self.board.move_stack)}")
        
        # Add to history - use stored SANs to avoid recalculating
        move_num = len(self.board.move_stack)
        if move_num > 0:
            # Store this move's SAN
            self.move_history_sans.append(move_san)
            
            # Format move history
            if is_white_move:
                # White move - start new move pair
                move_number = (move_num + 1) // 2
                history_text = f"{move_number}. {move_san}"
            else:
                # Black move - complete the move pair
                move_number = move_num // 2
                # Get previous move's SAN from our stored list
                if len(self.move_history_sans) >= 2:
                    prev_move_san = self.move_history_sans[-2]  # Previous move's SAN
                    history_text = f"{move_number}. {prev_move_san} {move_san}"
                else:
                    history_text = f"{move_number}... {move_san}"
            
            self.history_text.insert(tk.END, history_text + "\n")
            self.history_text.see(tk.END)
        
        # Update display immediately and force refresh
        self._update_display()
        # Force immediate GUI update
        self.root.update_idletasks()
        self.board_canvas.update_idletasks()
        
        # Call callback if set
        if self.move_callback:
            self.move_callback(move)
    
    def _undo_move(self):
        """Undo the last move."""
        if len(self.board.move_stack) > 0:
            self.board.pop()
            self.last_move = None
            self.last_move_san = None
            self.selected_square = None
            
            # Remove from stored SANs
            if self.move_history_sans:
                self.move_history_sans.pop()
            
            # Remove from history
            content = self.history_text.get("1.0", tk.END)
            lines = content.strip().split('\n')
            if lines:
                self.history_text.delete("1.0", tk.END)
                self.history_text.insert("1.0", '\n'.join(lines[:-1]))
            
            self._update_display()
    
    def _reset_board(self):
        """Reset the board to starting position."""
        if messagebox.askyesno("Reset Board", "Reset to starting position?"):
            self.board.reset()
            self.last_move = None
            self.selected_square = None
            self.history_text.delete("1.0", tk.END)
            self._update_display()
    
    def _toggle_auto_play(self):
        """Toggle auto-play mode."""
        self.auto_play = self.auto_play_var.get()
        self.auto_play_delay = self.delay_var.get()
    
    def _update_delay(self):
        """Update auto-play delay."""
        self.auto_play_delay = self.delay_var.get()
    
    def set_move_callback(self, callback: Callable[[chess.Move], None]):
        """Set a callback function to be called when a move is made."""
        self.move_callback = callback
    
    def make_move(self, move: chess.Move):
        """Programmatically make a move (for agents)."""
        if move in self.board.legal_moves:
            self._make_move(move)
            return True
        return False
    
    def run(self):
        """Start the GUI event loop."""
        self.root.mainloop()
    
    def update(self):
        """Update the GUI (call this from other threads)."""
        self.root.update_idletasks()


def play_game_with_gui(
    white_agent: Optional[BaseAgent] = None,
    black_agent: Optional[BaseAgent] = None,
    board: Optional[chess.Board] = None
):
    """
    Play a game with GUI, optionally with AI agents.
    
    Args:
        white_agent: Agent playing white (None for human)
        black_agent: Agent playing black (None for human)
        board: Initial board state (default: starting position)
    """
    gui = ChessGUI(board=board, title="Chess Game")
    last_move_count = [len(gui.board.move_stack)]  # Track move count
    
    def game_loop():
        """Run the game loop in a separate thread."""
        print("[game_loop] Starting game loop thread")
        iteration = 0
        while True:
            iteration += 1
            time.sleep(0.1)  # Small delay to avoid busy waiting
            
            # Check if game is over
            if gui.board.is_game_over():
                print("[game_loop] Game is over, exiting")
                break
            
            # Get current turn and agent (check fresh each time)
            current_turn = gui.board.turn
            current_agent = white_agent if current_turn == chess.WHITE else black_agent
            current_move_count = len(gui.board.move_stack)
            
            if iteration % 50 == 0 and current_agent:  # Print every 5 seconds
                print(f"[game_loop] Iteration {iteration}: turn={'White' if current_turn == chess.WHITE else 'Black'}, "
                      f"agent={current_agent.name if current_agent else 'Human'}, "
                      f"move_count={current_move_count}, last_move_count={last_move_count[0]}")
            
            if current_agent is None:
                # Human turn - wait for move from GUI
                # Check if move count increased (human made a move)
                if current_move_count != last_move_count[0]:
                    # Human made a move, update counter and continue
                    print(f"[game_loop] Human made a move! Move count: {last_move_count[0]} -> {current_move_count}")
                    print(f"[game_loop] New turn: {'White' if gui.board.turn == chess.WHITE else 'Black'}")
                    last_move_count[0] = current_move_count
                    time.sleep(0.2)  # Small delay after human move
                # Otherwise, just continue waiting
                continue
            
            # AI turn - show thinking status
            print(f"[game_loop] AI turn! Agent: {current_agent.name}, Turn: {'White' if current_turn == chess.WHITE else 'Black'}")
            print(f"[game_loop] Board FEN: {gui.board.fen()}")
            print(f"[game_loop] Legal moves: {len(list(gui.board.legal_moves))}")
            
            gui.root.after(0, lambda a=current_agent, t=current_turn: gui.status_label.config(
                text=f"Status: {a.name} is thinking... ({'White' if t == chess.WHITE else 'Black'} to move)"
            ))
            time.sleep(0.2)  # Let status update
            
            # Get move from agent (make a copy of board state for thread safety)
            try:
                print(f"[game_loop] Calling {current_agent.name}.choose_move()...")
                move = current_agent.choose_move(gui.board)
                print(f"[game_loop] Agent returned move: {move}")
            except Exception as e:
                print(f"[game_loop] ERROR getting move from agent: {e}")
                import traceback
                traceback.print_exc()
                break
            
            if move is None:
                print(f"[game_loop] Agent returned None (no moves available)")
                gui.root.after(0, lambda: gui.status_label.config(
                    text=f"Status: {current_agent.name} has no legal moves"
                ))
                break
            
            if gui.board.is_game_over():
                print(f"[game_loop] Game ended while agent was thinking")
                break
            
            # Verify move is still legal (board state might have changed)
            if move not in gui.board.legal_moves:
                print(f"[game_loop] ERROR: Move {move} is no longer legal! Legal moves: {list(gui.board.legal_moves)[:5]}...")
                print(f"[game_loop] Board FEN: {gui.board.fen()}")
                continue
            
            # Get SAN notation before making the move
            try:
                move_san = gui.board.san(move)
                print(f"[game_loop] Got SAN notation: {move_san}")
            except Exception as e:
                print(f"[game_loop] ERROR getting SAN: {e}")
                print(f"[game_loop] Move: {move}, Board FEN: {gui.board.fen()}")
                import traceback
                traceback.print_exc()
                continue
            
            current_move_count_before = len(gui.board.move_stack)
            print(f"[game_loop] Move count before: {current_move_count_before}")
            
            # Make move on GUI (thread-safe)
            def make_ai_move(m=move, san=move_san, agent=current_agent, move_count_before=current_move_count_before):
                print(f"[make_ai_move] CALLED in GUI thread. Move: {m}, SAN: {san}")
                print(f"[make_ai_move] Board FEN: {gui.board.fen()}")
                print(f"[make_ai_move] Move in legal_moves? {m in gui.board.legal_moves}")
                print(f"[make_ai_move] Move count: {len(gui.board.move_stack)}")
                
                if m not in gui.board.legal_moves:
                    print(f"[make_ai_move] ERROR: Move {m} is not legal! Legal moves: {list(gui.board.legal_moves)[:5]}...")
                    return
                
                print(f"[make_ai_move] Calling gui.make_move({m})...")
                gui.make_move(m)
                print(f"[make_ai_move] gui.make_move() completed")
                gui.status_label.config(text=f"Status: {agent.name} played {san}")
                new_move_count = len(gui.board.move_stack)
                print(f"[make_ai_move] New move count: {new_move_count}")
                last_move_count[0] = new_move_count
            
            print(f"[game_loop] Scheduling make_ai_move via root.after(0, ...)")
            gui.root.after(0, make_ai_move)
            
            # Wait for the move to be processed (move count should increase)
            timeout = 0
            print(f"[game_loop] Waiting for move to complete (current count: {current_move_count_before})...")
            while len(gui.board.move_stack) == current_move_count_before:
                if gui.board.is_game_over():
                    print(f"[game_loop] Game ended while waiting")
                    return
                time.sleep(0.05)
                timeout += 1
                if timeout > 200:  # 10 second timeout
                    print(f"[game_loop] TIMEOUT waiting for AI move to complete! Move count still: {len(gui.board.move_stack)}")
                    break
            
            # Update move count
            final_move_count = len(gui.board.move_stack)
            print(f"[game_loop] Move completed! Final move count: {final_move_count}")
            last_move_count[0] = final_move_count
            print(f"[game_loop] New turn: {'White' if gui.board.turn == chess.WHITE else 'Black'}")
            
            # Small delay before next iteration
            time.sleep(0.2)
    
    # Start game loop in separate thread
    game_thread = threading.Thread(target=game_loop, daemon=True)
    game_thread.start()
    
    # Run GUI
    gui.run()


def watch_agents_play(
    white_agent: BaseAgent,
    black_agent: BaseAgent,
    board: Optional[chess.Board] = None,
    move_delay: float = 1.0
):
    """
    Watch two agents play against each other with GUI visualization.
    
    Args:
        white_agent: Agent playing white
        black_agent: Agent playing black
        board: Initial board state (default: starting position)
        move_delay: Delay between moves in seconds
    """
    gui = ChessGUI(board=board, title=f"{white_agent.name} vs {black_agent.name}")
    gui.auto_play_var.set(True)
    gui.auto_play = True
    gui.auto_play_delay = move_delay
    gui.delay_var.set(move_delay)
    
    def game_loop():
        """Run the game loop in a separate thread."""
        while not gui.board.is_game_over():
            current_agent = white_agent if gui.board.turn == chess.WHITE else black_agent
            
            # Show thinking status
            gui.root.after(0, lambda a=current_agent: gui.status_label.config(
                text=f"Status: {a.name} is thinking..."
            ))
            
            move = current_agent.choose_move(gui.board)
            
            if move is None:
                break
            
            # Make move on GUI (thread-safe)
            move_san = gui.board.san(move)
            gui.root.after(0, lambda m=move, san=move_san: (
                gui.make_move(m),
                gui.status_label.config(text=f"Status: {current_agent.name} played {san}")
            ))
            
            time.sleep(move_delay)
        
        # Game over
        if gui.board.is_checkmate():
            winner = black_agent if gui.board.turn == chess.WHITE else white_agent
            gui.root.after(0, lambda: gui.status_label.config(
                text=f"Status: Checkmate! {winner.name} wins!"
            ))
        elif gui.board.is_stalemate():
            gui.root.after(0, lambda: gui.status_label.config(
                text="Status: Stalemate - Draw"
            ))
    
    # Start game loop in separate thread
    game_thread = threading.Thread(target=game_loop, daemon=True)
    game_thread.start()
    
    # Run GUI
    gui.run()

