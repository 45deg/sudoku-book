from __future__ import annotations

import shutil
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "examples" / "common"))

from solve import solve  # noqa: E402
from sudoku import boards_are_distinct, load_board, validate_solution  # noqa: E402

MINIZINC = shutil.which("minizinc")

@unittest.skipUnless(MINIZINC, "MiniZinc (minizinc) binary not found")
class MiniZincSudokuTest(unittest.TestCase):
    def test_shidoku_board(self) -> None:
        board = load_board(ROOT / "fixtures" / "shidoku-4x4.sdk")
        status, solutions, _ = solve(board)
        self.assertEqual(status, "solved")
        self.assertTrue(validate_solution(solutions[0], board)[0])

    def test_standard_board(self) -> None:
        board = load_board(ROOT / "fixtures" / "standard-9x9.sdk")
        status, solutions, output = solve(board, limit=2)
        self.assertEqual(status, "solved")
        self.assertEqual(len(solutions), 1)
        self.assertTrue(validate_solution(solutions[0], board)[0])
        self.assertIn("==========", output)

    def test_unsatisfiable_board(self) -> None:
        board = load_board(ROOT / "fixtures" / "unsat-9x9.sdk")
        status, solutions, _ = solve(board)
        self.assertEqual(status, "unsat")
        self.assertEqual(solutions, [])

    def test_two_distinct_solutions(self) -> None:
        board = load_board(ROOT / "fixtures" / "multiple-9x9.sdk")
        status, solutions, _ = solve(board, limit=2)
        self.assertEqual(status, "solved")
        self.assertEqual(len(solutions), 2)
        self.assertTrue(boards_are_distinct(solutions))
        for solution in solutions:
            self.assertTrue(validate_solution(solution, board)[0])


if __name__ == "__main__":
    unittest.main()
