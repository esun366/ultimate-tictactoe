# Ultimate Tic-Tac-Toe

A 3×3 grid of mini tic-tac-toe boards (81 tiles total). Win a mini-board to
claim that big tile; win three big tiles in a row to win the whole game.

## Our rules

- On your turn you may play **any** empty tile in **any** mini-board that
  hasn't been decided yet (free placement — no forced board).
- Winning a mini-board claims that big tile for you.
- A mini-board that is won, or full with no winner (a draw), is **locked** —
  no more moves there.
- Win 3 big tiles in a row / column / diagonal to win the game. If every
  mini-board is decided and nobody has 3 in a row, it's a draw.

## Files

| File | What it is |
|------|------------|
| `ultimate_tictactoe.py` | The game engine. Pure logic, no UI. **This is the core.** |
| `play.py` | A throwaway terminal version so you can play right now. |
| `test_ultimate_tictactoe.py` | Tests for the engine. |

## Try it

```bash
python play.py                              # play in the terminal
python -m unittest test_ultimate_tictactoe  # run the tests
```

Boards and tiles are both numbered 0–8, left-to-right, top-to-bottom:

```
0 | 1 | 2
--+---+--
3 | 4 | 5
--+---+--
6 | 7 | 8
```

A move is a `board cell` pair, e.g. `4 0` = top-left tile of the center board.

## The engine API (for building a UI)

Everything a UI needs is on the `UltimateTicTacToe` class — it never prints or
asks for input, so any front-end (web, GUI, etc.) can sit on top:

```python
from ultimate_tictactoe import UltimateTicTacToe, Player

game = UltimateTicTacToe()

game.current_player   # Player.X or Player.O — whose turn
game.legal_moves()    # list of (board, cell) moves allowed right now
game.can_play(b, c)   # is this specific move legal?
game.make_move(b, c)  # play it (raises ValueError if illegal); advances turn
game.macro_cells      # the big 3x3: who owns each mini-board (Player or None)
game.boards[b].cells  # the 9 tiles of mini-board b (Player or None)
game.is_over          # game finished?
game.winner           # Player who won, or None
game.is_draw          # finished with no winner?
game.history          # every move so far, as (player, board, cell)
```
```
