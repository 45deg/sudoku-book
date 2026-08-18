from __future__ import annotations

import sys
import unittest
from pathlib import Path

from sympy import Integer, QQ, groebner, symbols

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "examples" / "common"))

from sudoku import boards_are_distinct, load_board, validate_solution  # noqa: E402

from solve import build_polynomial_model, solve  # noqa: E402


class GroebnerBasisTests(unittest.TestCase):
    def test_small_exactly_one_basis(self) -> None:
        x, y = symbols("x y")
        basis = groebner(
            (x**2 - x, y**2 - y, x + y - 1),
            x,
            y,
            order="lex",
            domain=QQ,
        )
        self.assertEqual(
            tuple(poly.as_expr() for poly in basis.polys),
            (x + y - 1, y**2 - y),
        )

    def test_model_contains_boolean_equation_for_each_variable(self) -> None:
        givens = load_board(HERE / "boards" / "multiple-4x4.sdk")
        model = build_polynomial_model(givens)
        equations = set(model.polynomials)
        self.assertTrue(all(variable * (variable - 1) in equations for variable in model.variables))

    def test_preprocessing_counts_are_recorded(self) -> None:
        expected = {
            "unique-4x4.sdk": (24, 72),
            "multiple-4x4.sdk": (8, 24),
            "unsat-4x4.sdk": (28, 76),
        }
        for name, counts in expected.items():
            with self.subTest(board=name):
                model = build_polynomial_model(load_board(HERE / "boards" / name))
                self.assertEqual((len(model.variables), len(model.polynomials)), counts)

    def test_unique_board(self) -> None:
        givens = load_board(HERE / "boards" / "unique-4x4.sdk")
        result = solve(givens)
        self.assertEqual(result.status, "solved")
        self.assertEqual(len(result.solutions), 1)
        self.assertTrue(validate_solution(result.solutions[0], givens)[0])

    def test_multiple_board(self) -> None:
        givens = load_board(HERE / "boards" / "multiple-4x4.sdk")
        result = solve(givens)
        self.assertEqual(result.status, "solved")
        self.assertEqual(len(result.solutions), 2)
        self.assertTrue(boards_are_distinct(result.solutions))
        self.assertTrue(all(validate_solution(board, givens)[0] for board in result.solutions))

    def test_unsat_basis_is_one(self) -> None:
        givens = load_board(HERE / "boards" / "unsat-4x4.sdk")
        result = solve(givens)
        self.assertEqual(result.status, "unsat")
        self.assertEqual(result.basis, (Integer(1),))
        self.assertEqual(result.solutions, ())


if __name__ == "__main__":
    unittest.main()
