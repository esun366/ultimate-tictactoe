"""
Tests for the Ultimate Tic-Tac-Toe engine.

Run all tests:   python -m unittest test_ultimate_tictactoe
(No external libraries needed — just Python's built-in unittest.)
"""

import unittest

from ultimate_tictactoe import UltimateTicTacToe, MiniBoard, Player, _winner_of


class TestMiniBoard(unittest.TestCase):
    def test_row_win(self):
        mb = MiniBoard()
        mb.place(0, Player.X)
        mb.place(1, Player.X)
        self.assertIsNone(mb.winner)
        mb.place(2, Player.X)
        self.assertEqual(mb.winner, Player.X)
        self.assertTrue(mb.is_decided)

    def test_cannot_play_taken_cell(self):
        mb = MiniBoard()
        mb.place(4, Player.O)
        self.assertFalse(mb.can_play(4))
        with self.assertRaises(ValueError):
            mb.place(4, Player.X)

    def test_cannot_play_decided_board(self):
        mb = MiniBoard()
        for c in (0, 1, 2):
            mb.place(c, Player.X)          # X wins this mini-board
        self.assertTrue(mb.is_decided)
        self.assertFalse(mb.can_play(3))   # locked even though cell 3 is empty

    def test_draw_locks_board(self):
        mb = MiniBoard()
        # Fill with no winner:  X O X / X O O / O X X
        order = [Player.X, Player.O, Player.X,
                 Player.X, Player.O, Player.O,
                 Player.O, Player.X, Player.X]
        for c, p in enumerate(order):
            mb.place(c, p)
        self.assertIsNone(mb.winner)
        self.assertTrue(mb.is_full)
        self.assertTrue(mb.is_decided)


class TestUltimate(unittest.TestCase):
    def test_turn_alternates(self):
        game = UltimateTicTacToe()
        self.assertEqual(game.current_player, Player.X)
        game.make_move(0, 0)
        self.assertEqual(game.current_player, Player.O)
        game.make_move(0, 1)
        self.assertEqual(game.current_player, Player.X)

    def test_free_placement_across_boards(self):
        """A player may play in any undecided board — not constrained."""
        game = UltimateTicTacToe()
        game.make_move(0, 0)   # X
        game.make_move(5, 8)   # O, totally different board — allowed
        game.make_move(2, 4)   # X, yet another board — allowed
        self.assertEqual(len(game.history), 3)

    def test_illegal_move_raises(self):
        game = UltimateTicTacToe()
        game.make_move(0, 0)
        with self.assertRaises(ValueError):
            game.make_move(0, 0)          # cell already taken

    def test_winning_a_miniboard_claims_macro_cell(self):
        game = UltimateTicTacToe()
        # X wins mini-board 0 by taking its top row; O plays elsewhere.
        game.make_move(0, 0)   # X
        game.make_move(8, 8)   # O
        game.make_move(0, 1)   # X
        game.make_move(8, 7)   # O
        game.make_move(0, 2)   # X wins mini-board 0
        self.assertEqual(game.boards[0].winner, Player.X)
        self.assertEqual(game.macro_cells[0], Player.X)
        self.assertFalse(game.is_over)

    def test_winning_three_macro_cells_wins_game(self):
        game = UltimateTicTacToe()
        # Drive X to win mini-boards 0, 1, 2 (the top macro row). O plays into
        # boards 6, 7, 8 at cells {0,1,5} — deliberately NOT a winning line, so
        # O never claims a macro cell and never ends the game early.
        # Each block below is 6 moves (X,O,X,O,X,O) so X always starts the next.
        o_moves = iter([(6, 0), (7, 0), (8, 0),
                        (6, 1), (7, 1), (8, 1),
                        (6, 5), (7, 5), (8, 5)])

        def x_wins_board(b):
            game.make_move(b, 0)            # X
            game.make_move(*next(o_moves))  # O, harmless
            game.make_move(b, 1)            # X
            game.make_move(*next(o_moves))  # O, harmless
            game.make_move(b, 2)            # X completes board b's top row
            if not game.is_over:            # last block ends the game here
                game.make_move(*next(o_moves))  # O, harmless (keeps parity even)

        x_wins_board(0)
        self.assertFalse(game.is_over)
        x_wins_board(1)
        self.assertFalse(game.is_over)
        x_wins_board(2)
        self.assertTrue(game.is_over)
        self.assertEqual(game.winner, Player.X)
        # No more moves allowed once the game is over.
        self.assertEqual(game.legal_moves(), [])
        with self.assertRaises(ValueError):
            game.make_move(4, 4)

    def test_legal_moves_excludes_decided_boards(self):
        game = UltimateTicTacToe()
        game.make_move(0, 0)   # X
        game.make_move(1, 0)   # O
        game.make_move(0, 1)   # X
        game.make_move(1, 1)   # O
        game.make_move(0, 2)   # X wins board 0
        moves = game.legal_moves()
        self.assertTrue(all(b != 0 for (b, c) in moves))  # board 0 now locked


class TestWinnerHelper(unittest.TestCase):
    def test_diagonal(self):
        cells = [Player.O, None, None,
                 None, Player.O, None,
                 None, None, Player.O]
        self.assertEqual(_winner_of(cells), Player.O)

    def test_no_winner(self):
        self.assertIsNone(_winner_of([None] * 9))


if __name__ == "__main__":
    unittest.main()
