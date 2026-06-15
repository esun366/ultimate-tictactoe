"""
Tkinter GUI for Ultimate Tic-Tac-Toe.

A simple point-and-click front-end on top of the pure game engine in
ultimate_tictactoe.py. Click any tile in any mini-board that hasn't been
decided yet to play it there.

Run:  python gui.py
"""

import tkinter as tk
from tkinter import font as tkfont

from ultimate_tictactoe import Player, UltimateTicTacToe, WIN_LINES

X_COLOR = "#1f6feb"
O_COLOR = "#e03131"
WIN_TINT = {Player.X: "#cfe6ff", Player.O: "#ffd6d6"}
DRAW_TINT = "#e3e3e3"
HIGHLIGHT_COLOR = "#ffd43b"
GRID_COLOR = "#222222"


class UltimateTicTacToeGUI:
    """A 9x9 grid of buttons (nine 3x3 mini-boards) wired to a game."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.game = UltimateTicTacToe()

        root.title("Ultimate Tic-Tac-Toe")
        root.resizable(False, False)

        cell_font = tkfont.Font(family="Segoe UI", size=14, weight="bold")
        overlay_font = tkfont.Font(family="Segoe UI", size=36, weight="bold")

        self.status_var = tk.StringVar()
        tk.Label(
            root, textvariable=self.status_var, font=("Segoe UI", 14, "bold")
        ).pack(pady=(10, 5))

        grid_frame = tk.Frame(root, bg=GRID_COLOR)
        grid_frame.pack(padx=10, pady=(0, 10))

        # buttons[board][cell] -> the tk.Button for that tile
        self.buttons: list[list[tk.Button]] = [[None] * 9 for _ in range(9)]  # type: ignore[list-item]
        # overlays[board] -> big label shown when that mini-board is decided
        self.overlays: list[tk.Label] = [None] * 9  # type: ignore[list-item]
        # wrappers[board] -> frame whose background acts as that mini-board's border
        self.wrappers: list[tk.Frame] = [None] * 9  # type: ignore[list-item]

        for board in range(9):
            br, bc = divmod(board, 3)
            wrapper = tk.Frame(grid_frame, bg=GRID_COLOR)
            wrapper.grid(row=br, column=bc, padx=3, pady=3)
            self.wrappers[board] = wrapper

            inner = tk.Frame(wrapper, bg="white")
            inner.pack(padx=2, pady=2)

            for cell in range(9):
                cr, cc = divmod(cell, 3)
                btn = tk.Button(
                    inner,
                    text="",
                    width=3,
                    height=1,
                    font=cell_font,
                    command=lambda b=board, c=cell: self.on_click(b, c),
                )
                btn.grid(row=cr, column=cc, padx=1, pady=1)
                self.buttons[board][cell] = btn

            overlay = tk.Label(inner, text="", font=overlay_font)
            self.overlays[board] = overlay

        tk.Button(root, text="New Game", command=self.reset).pack(pady=(0, 10))

        self.refresh()

    def on_click(self, board: int, cell: int) -> None:
        if not self.game.can_play(board, cell):
            return
        self.game.make_move(board, cell)
        self.refresh()

    def reset(self) -> None:
        self.game = UltimateTicTacToe()
        self.refresh()

    def refresh(self) -> None:
        """Redraw every tile, overlay, and the status line from game state."""
        for board in range(9):
            mini = self.game.boards[board]

            for cell in range(9):
                btn = self.buttons[board][cell]
                played = mini.cells[cell]
                if played is None:
                    state = tk.NORMAL if self.game.can_play(board, cell) else tk.DISABLED
                    btn.config(text="", state=state)
                else:
                    color = X_COLOR if played == Player.X else O_COLOR
                    btn.config(text=str(played), fg=color, disabledforeground=color, state=tk.DISABLED)

            overlay = self.overlays[board]
            if mini.is_decided:
                if mini.winner is not None:
                    overlay.config(
                        text=str(mini.winner),
                        fg=X_COLOR if mini.winner == Player.X else O_COLOR,
                        bg=WIN_TINT[mini.winner],
                    )
                else:
                    overlay.config(text="=", fg="#888888", bg=DRAW_TINT)
                overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
                overlay.lift()
            else:
                overlay.place_forget()

        self._highlight_winning_line()
        self._update_status()

    def _highlight_winning_line(self) -> None:
        """Mark the three mini-boards that complete the winning macro line, if any."""
        macro = self.game.macro_cells
        winning_boards: set[int] = set()
        if self.game.winner is not None:
            for a, b, c in WIN_LINES:
                if macro[a] is not None and macro[a] == macro[b] == macro[c]:
                    winning_boards = {a, b, c}
                    break
        for board, wrapper in enumerate(self.wrappers):
            wrapper.config(bg=HIGHLIGHT_COLOR if board in winning_boards else GRID_COLOR)

    def _update_status(self) -> None:
        if self.game.is_over:
            if self.game.is_draw:
                self.status_var.set("It's a draw!")
            else:
                self.status_var.set(f"Player {self.game.winner} wins the game!")
        else:
            self.status_var.set(f"Player {self.game.current_player}'s turn")


def main() -> None:
    root = tk.Tk()
    UltimateTicTacToeGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
