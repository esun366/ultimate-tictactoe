"""
Ultimate Tic-Tac-Toe — game engine (no UI).

The board is a 3x3 grid of mini tic-tac-toe boards (81 tiles total).

Rules implemented here:
  * Win a mini-board (3 in a row inside it) -> you claim that big tile.
  * Win 3 big tiles in a row / column / diagonal -> you win the whole game.
  * Free placement: on your turn you may play ANY empty tile inside ANY
    mini-board that has not yet been decided.
  * A mini-board is "decided" once it is won OR it is full with no winner
    (a draw). Decided mini-boards are locked: no more moves allowed there.
  * The whole game is a draw if every mini-board is decided and no player
    has 3 big tiles in a row.

This module is pure logic. It has no print statements and no input(): a UI
(text, web, GUI...) sits on top of it and only calls the public methods.

Coordinate system
------------------
Everything uses two indices in the range 0..8, laid out row-major:

        0 | 1 | 2
        --+---+--
        3 | 4 | 5
        --+---+--
        6 | 7 | 8

`board` is which mini-board (0..8) and `cell` is which tile inside it (0..8).
So a full move is the pair (board, cell).
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional, Tuple


# The 8 winning lines on any 3x3 grid (indices into a length-9 list).
WIN_LINES: Tuple[Tuple[int, int, int], ...] = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),   # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),   # columns
    (0, 4, 8), (2, 4, 6),              # diagonals
)


class Player(Enum):
    """The two players. `.other` flips to the opponent."""
    X = "X"
    O = "O"

    @property
    def other(self) -> "Player":
        return Player.O if self is Player.X else Player.X

    def __str__(self) -> str:
        return self.value


def _winner_of(cells: List[Optional[Player]]) -> Optional[Player]:
    """Return the Player occupying a full winning line, or None."""
    for a, b, c in WIN_LINES:
        if cells[a] is not None and cells[a] == cells[b] == cells[c]:
            return cells[a]
    return None


class MiniBoard:
    """A single 3x3 tic-tac-toe board (one of the nine)."""

    def __init__(self) -> None:
        # cells[i] is the Player who played tile i, or None if empty.
        self.cells: List[Optional[Player]] = [None] * 9
        self.winner: Optional[Player] = None

    @property
    def is_full(self) -> bool:
        return all(cell is not None for cell in self.cells)

    @property
    def is_decided(self) -> bool:
        """True if this board is won or drawn — i.e. no longer playable."""
        return self.winner is not None or self.is_full

    def can_play(self, cell: int) -> bool:
        """True if `cell` (0..8) is a legal move on this mini-board."""
        if not 0 <= cell <= 8:
            return False
        return not self.is_decided and self.cells[cell] is None

    def place(self, cell: int, player: Player) -> None:
        """
        Place `player` on `cell`. Raises ValueError if the move is illegal.
        Updates `winner` if this move completes a line.
        """
        if not self.can_play(cell):
            raise ValueError(f"Illegal move on cell {cell} of this mini-board")
        self.cells[cell] = player
        self.winner = _winner_of(self.cells)


class UltimateTicTacToe:
    """
    The full game: a 3x3 grid of MiniBoards plus turn tracking.

    Typical UI usage:
        game = UltimateTicTacToe()
        while not game.is_over:
            board, cell = ask_user(game.current_player, game.legal_moves())
            game.make_move(board, cell)
        show_result(game.winner)
    """

    def __init__(self, starting_player: Player = Player.X) -> None:
        self.boards: List[MiniBoard] = [MiniBoard() for _ in range(9)]
        self.current_player: Player = starting_player
        self.winner: Optional[Player] = None
        # Full move history as (player, board, cell) — handy for UI/undo/replay.
        self.history: List[Tuple[Player, int, int]] = []

    # ----- derived state ---------------------------------------------------

    @property
    def macro_cells(self) -> List[Optional[Player]]:
        """The 3x3 'big board': who owns each mini-board (winner), else None."""
        return [b.winner for b in self.boards]

    @property
    def is_over(self) -> bool:
        """True once someone has won or every mini-board is decided (draw)."""
        return self.winner is not None or all(b.is_decided for b in self.boards)

    @property
    def is_draw(self) -> bool:
        return self.is_over and self.winner is None

    def can_play(self, board: int, cell: int) -> bool:
        """True if (board, cell) is a legal move for the current player."""
        if self.is_over:
            return False
        if not 0 <= board <= 8:
            return False
        return self.boards[board].can_play(cell)

    def legal_moves(self) -> List[Tuple[int, int]]:
        """Every legal (board, cell) move available right now."""
        if self.is_over:
            return []
        moves: List[Tuple[int, int]] = []
        for b, mini in enumerate(self.boards):
            if mini.is_decided:
                continue
            for c in range(9):
                if mini.cells[c] is None:
                    moves.append((b, c))
        return moves

    # ----- mutation --------------------------------------------------------

    def make_move(self, board: int, cell: int) -> None:
        """
        Play the current player's move at (board, cell), then advance the turn.
        Raises ValueError if the move is illegal.
        """
        if self.is_over:
            raise ValueError("The game is already over")
        if not 0 <= board <= 8:
            raise ValueError(f"Board index {board} out of range 0..8")

        player = self.current_player
        self.boards[board].place(cell, player)  # raises if cell is illegal
        self.history.append((player, board, cell))

        # Did claiming that big tile win the whole game?
        self.winner = _winner_of(self.macro_cells)

        # Hand the turn over (even if the game just ended; is_over guards it).
        self.current_player = player.other
