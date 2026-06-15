"""
Tiny terminal front-end for Ultimate Tic-Tac-Toe.

This is a *placeholder* UI just so you can play and test the engine in a
terminal. Your friend can replace this entirely with a real UI — all the
game rules live in ultimate_tictactoe.py, not here.

Run:  python play.py
"""

from ultimate_tictactoe import UltimateTicTacToe, Player


def render(game: UltimateTicTacToe) -> str:
    """Draw all 9 mini-boards side by side as ASCII art.

    Empty tiles show their cell index (0..8) so it's easy to see what to type.
    A mini-board that's been won is shown filled with the winner's letter.
    """
    def tile(board_idx: int, cell_idx: int) -> str:
        mini = game.boards[board_idx]
        if mini.winner is not None:
            return str(mini.winner)            # won board: show the claimer
        played = mini.cells[cell_idx]
        return str(played) if played else str(cell_idx)

    lines = []
    for big_row in range(3):                   # 3 rows of mini-boards
        for sub_row in range(3):               # 3 tile-rows per mini-board
            row_parts = []
            for big_col in range(3):
                b = big_row * 3 + big_col
                cells = [tile(b, sub_row * 3 + sc) for sc in range(3)]
                row_parts.append(" ".join(cells))
            lines.append("   ".join(row_parts))
        if big_row < 2:
            lines.append("")                   # blank line between board rows
    return "\n".join(lines)


def main() -> None:
    game = UltimateTicTacToe()
    print(__doc__)
    print("Boards and tiles are both numbered 0..8 (left-to-right, top-to-bottom).\n")

    while not game.is_over:
        print(render(game))
        print(f"\nPlayer {game.current_player}, enter your move as: board cell")
        raw = input("> ").strip()

        try:
            board_str, cell_str = raw.split()
            board, cell = int(board_str), int(cell_str)
        except ValueError:
            print("  Please type two numbers, e.g.  4 0\n")
            continue

        try:
            game.make_move(board, cell)
        except ValueError as err:
            print(f"  {err}\n")
            continue

        print()

    print(render(game))
    if game.is_draw:
        print("\nIt's a draw!")
    else:
        print(f"\nPlayer {game.winner} wins the whole game!")


if __name__ == "__main__":
    main()
