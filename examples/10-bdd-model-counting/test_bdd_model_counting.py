from __future__ import annotations

import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "examples" / "common"))

from sudoku import parse_board, validate_solution  # noqa: E402

from bdd_utils import decision_node_count  # noqa: E402
from small_bdd import build_mux  # noqa: E402
from solve import add_givens, build_rules, decode_model, flatten_board, read_board  # noqa: E402


class SmallBDDTest(unittest.TestCase):
    def test_mux_has_four_models(self) -> None:
        bdd, formula = build_mux(("x", "y", "z"))
        self.assertEqual(bdd.count(formula, nvars=3), 4)

    def test_variable_order_changes_node_count(self) -> None:
        first_bdd, first = build_mux(("x", "y", "z"))
        second_bdd, second = build_mux(("y", "z", "x"))
        self.assertNotEqual(
            decision_node_count(first_bdd, first),
            decision_node_count(second_bdd, second),
        )


class SudokuBDDTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.compiled = build_rules("cell")

    def count(self, path: Path) -> int:
        board = read_board(path)
        formula = add_givens(self.compiled, board)
        return int(self.compiled.bdd.count(formula, nvars=len(self.compiled.names)))

    def test_empty_grid_has_288_completions(self) -> None:
        self.assertEqual(
            self.compiled.bdd.count(self.compiled.rules, nvars=len(self.compiled.names)),
            288,
        )

    def test_unique_grid(self) -> None:
        path = HERE / "boards" / "unique-4x4.sdk"
        puzzle = read_board(path)
        formula = add_givens(self.compiled, puzzle)
        self.assertEqual(
            self.compiled.bdd.count(formula, nvars=len(self.compiled.names)),
            1,
        )
        model = next(
            self.compiled.bdd.pick_iter(
                formula, care_vars=set(self.compiled.names)
            )
        )
        valid, errors = validate_solution(
            flatten_board(decode_model(model)),
            parse_board(path.read_text()),
        )
        self.assertTrue(valid, errors)

    def test_unsat_grid(self) -> None:
        self.assertEqual(self.count(HERE / "boards" / "unsat-4x4.sdk"), 0)

    def test_multiple_grid_and_two_restored_solutions(self) -> None:
        path = ROOT / "fixtures" / "shidoku-4x4.sdk"
        puzzle = read_board(path)
        formula = add_givens(self.compiled, puzzle)
        self.assertEqual(
            self.compiled.bdd.count(formula, nvars=len(self.compiled.names)),
            2,
        )

        models = self.compiled.bdd.pick_iter(
            formula, care_vars=set(self.compiled.names)
        )
        solutions = [decode_model(next(models)), decode_model(next(models))]
        common_puzzle = parse_board(path.read_text())
        for solution in solutions:
            valid, errors = validate_solution(flatten_board(solution), common_puzzle)
            self.assertTrue(valid, errors)
        self.assertNotEqual(solutions[0], solutions[1])


if __name__ == "__main__":
    unittest.main()
