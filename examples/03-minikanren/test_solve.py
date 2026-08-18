from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "03-minikanren"
COMMON = ROOT / "examples" / "common"
sys.path[:0] = [str(EXAMPLE), str(COMMON)]

from relation_demo import append_examples, choice_example  # noqa: E402
from solve import solve  # noqa: E402
from sudoku import (  # noqa: E402
    Board,
    boards_are_distinct,
    is_consistent_partial,
    load_board,
    validate_solution,
)


class MiniKanrenTests(unittest.TestCase):
    def puzzle(self, name: str) -> Board:
        return load_board(EXAMPLE / "puzzles" / name)

    def assert_valid_solutions(self, result, givens) -> None:
        for solution in result.solutions:
            valid, errors = validate_solution(solution, givens)
            self.assertTrue(valid, errors)
        self.assertTrue(boards_are_distinct(result.solutions))

    def test_appendo_runs_in_both_directions(self) -> None:
        joined, splits = append_examples()
        self.assertEqual(joined, ((1, 2, 3),))
        self.assertEqual(
            set(splits),
            {
                ((), (1, 2, 3)),
                ((1,), (2, 3)),
                ((1, 2), (3,)),
                ((1, 2, 3), ()),
            },
        )

    def test_conde_produces_both_choices(self) -> None:
        self.assertEqual(choice_example(), (1, 2))

    def test_unique_puzzle(self) -> None:
        givens = self.puzzle("unique-4x4.sdk")
        result = solve(givens, limit=2)
        self.assertEqual(result.status, "solved")
        self.assertEqual(len(result.solutions), 1)
        self.assertTrue(result.exhausted)
        self.assert_valid_solutions(result, givens)

    def test_consistent_but_unsatisfiable_puzzle(self) -> None:
        givens = self.puzzle("unsat-4x4.sdk")
        self.assertTrue(is_consistent_partial(givens))
        result = solve(givens, limit=2)
        self.assertEqual(result.status, "unsat")
        self.assertEqual(result.solutions, ())
        self.assertTrue(result.exhausted)

    def test_multiple_puzzle(self) -> None:
        givens = load_board(ROOT / "fixtures" / "shidoku-4x4.sdk")
        result = solve(givens, limit=2)
        self.assertEqual(result.status, "solved")
        self.assertEqual(len(result.solutions), 2)
        self.assertTrue(result.exhausted)
        self.assert_valid_solutions(result, givens)

    def test_rejects_9x9_board(self) -> None:
        givens = load_board(ROOT / "fixtures" / "standard-9x9.sdk")
        with self.assertRaisesRegex(ValueError, "4x4"):
            solve(givens)


if __name__ == "__main__":
    unittest.main()
