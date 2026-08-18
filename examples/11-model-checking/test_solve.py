from __future__ import annotations

import os
import shutil
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "examples" / "common"))

import solve as solve_module  # noqa: E402
from solve import InvariantResult, build_model, solve  # noqa: E402
from sudoku import boards_are_distinct, load_board, validate_solution  # noqa: E402

NUXMV = os.environ.get("NUXMV") or shutil.which("nuXmv.sh") or shutil.which("nuXmv")


class ModelConstructionTest(unittest.TestCase):
    def test_model_contains_state_transition_and_property(self) -> None:
        board = load_board(ROOT / "fixtures" / "shidoku-4x4.sdk")
        model = build_model(board)
        self.assertIn("init(step) := 0", model)
        self.assertIn("next(step)", model)
        self.assertIn("INVAR cell_1_1", model)
        self.assertIn("LTLSPEC NAME goal_is_unreachable := G !goal", model)

    def test_unknown_is_not_reported_as_unsat(self) -> None:
        board = load_board(ROOT / "fixtures" / "shidoku-4x4.sdk")
        with patch.object(
            solve_module,
            "check_invariant",
            return_value=InvariantResult("unknown", "unknown"),
        ):
            result = solve(board, "unused")
        self.assertEqual(result.status, "unknown")
        self.assertFalse(result.search_complete)


@unittest.skipUnless(NUXMV, "nuXmvが見つかりません。NUXMVにnuXmv.shを指定してください")
class NuXmvSudokuTest(unittest.TestCase):
    def test_shidoku_board(self) -> None:
        board = load_board(ROOT / "fixtures" / "shidoku-4x4.sdk")
        result = solve(board, NUXMV, limit=2)
        self.assertEqual(result.status, "solved")
        self.assertEqual(len(result.solutions), 2)
        self.assertTrue(boards_are_distinct(result.solutions))
        for solution in result.solutions:
            self.assertTrue(validate_solution(solution, board)[0])

    def test_standard_board_is_unique(self) -> None:
        board = load_board(ROOT / "fixtures" / "standard-9x9.sdk")
        result = solve(board, NUXMV, limit=2)
        self.assertEqual(result.status, "solved")
        self.assertEqual(len(result.solutions), 1)
        self.assertTrue(result.search_complete)
        self.assertTrue(validate_solution(result.solutions[0], board)[0])

    def test_unsatisfiable_board(self) -> None:
        board = load_board(ROOT / "fixtures" / "unsat-9x9.sdk")
        result = solve(board, NUXMV, limit=2)
        self.assertEqual(result.status, "unsat")
        self.assertEqual(result.solutions, ())
        self.assertTrue(result.search_complete)

    def test_two_distinct_solutions(self) -> None:
        board = load_board(ROOT / "fixtures" / "multiple-9x9.sdk")
        result = solve(board, NUXMV, limit=2)
        self.assertEqual(result.status, "solved")
        self.assertEqual(len(result.solutions), 2)
        self.assertTrue(boards_are_distinct(result.solutions))
        for solution in result.solutions:
            self.assertTrue(validate_solution(solution, board)[0])


if __name__ == "__main__":
    unittest.main()
