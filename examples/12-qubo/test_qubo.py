from __future__ import annotations

import sys
import unittest
from random import Random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "examples" / "common"))

from sudoku import Board, load_board, validate_solution  # noqa: E402

from qubo import build_qubo, fixed_candidates, variable  # noqa: E402
from solve import sample_sudoku  # noqa: E402


def exact_solution_count(givens: Board, limit: int = 3) -> int:
    """Small reference search used only to classify the test boards."""
    side = 9
    board = list(givens)
    count = 0

    def candidates(index: int) -> set[int]:
        row, column = divmod(index, side)
        used = set(board[row * side : (row + 1) * side])
        used.update(board[column::side])
        top, left = row // 3 * 3, column // 3 * 3
        used.update(board[r * side + c] for r in range(top, top + 3) for c in range(left, left + 3))
        return set(range(1, side + 1)) - used

    def search() -> None:
        nonlocal count
        if count >= limit:
            return
        empty = [index for index, digit in enumerate(board) if digit == 0]
        if not empty:
            valid, _ = validate_solution(tuple(board), givens)
            count += int(valid)
            return
        index = min(empty, key=lambda item: len(candidates(item)))
        for digit in sorted(candidates(index)):
            board[index] = digit
            search()
            board[index] = 0

    search()
    return count


class QuboTests(unittest.TestCase):
    def test_substitution_preserves_energy(self) -> None:
        givens = load_board(ROOT / "fixtures" / "standard-9x9.sdk")
        full = build_qubo(givens)
        fixed = fixed_candidates(givens)
        reduced = full.copy()
        reduced.fix_variables(fixed)
        self.assertEqual(len(full.variables), 729)
        self.assertEqual(len(full.quadratic), 10206)
        self.assertEqual(len(reduced.variables), 223)
        rng = Random(7)
        for _ in range(10):
            sample = {item: rng.randrange(2) for item in reduced.variables}
            self.assertAlmostEqual(reduced.energy(sample), full.energy(sample | fixed))

    def test_completed_board_with_no_free_variables(self) -> None:
        board = tuple(map(int, "534678912672195348198342567859761423426853791713924856961537284287419635345286179"))
        result = sample_sudoku(board, seed=20260808, reads=5, sweeps=10)
        self.assertEqual(result.status, "solved")
        self.assertEqual(result.sampled_variables, 0)
        self.assertEqual(result.solutions, (board,))

    def test_conflicting_givens_keep_positive_energy(self) -> None:
        board = tuple(map(int, "554678912672195348198342567859761423426853791713924856961537284287419635345286179"))
        result = sample_sudoku(board, seed=20260808, reads=5, sweeps=10)
        self.assertEqual(result.status, "unknown")
        self.assertGreater(result.best_energy, 0)
        self.assertEqual(result.solutions, ())

    def test_solution_has_zero_energy(self) -> None:
        givens = load_board(ROOT / "fixtures" / "standard-9x9.sdk")
        solution = tuple(map(int, "534678912672195348198342567859761423426853791713924856961537284287419635345286179"))
        sample = {
            variable(row, column, digit): int(solution[row * 9 + column] == digit)
            for row in range(9)
            for column in range(9)
            for digit in range(1, 10)
        }
        self.assertAlmostEqual(build_qubo(givens).energy(sample), 0.0)

    def test_one_hot_violation_has_positive_energy(self) -> None:
        givens = (0,) * 81
        sample = {item: 0 for item in build_qubo(givens).variables}
        self.assertGreater(build_qubo(givens).energy(sample), 0.0)

    def test_reference_board_categories(self) -> None:
        unique = load_board(ROOT / "fixtures" / "standard-9x9.sdk")
        multiple = load_board(ROOT / "fixtures" / "multiple-9x9.sdk")
        unsat = load_board(ROOT / "fixtures" / "unsat-9x9.sdk")
        self.assertEqual(exact_solution_count(unique), 1)
        self.assertGreaterEqual(exact_solution_count(multiple), 2)
        self.assertEqual(exact_solution_count(unsat), 0)

    def test_sampler_finds_valid_unique_solution(self) -> None:
        givens = load_board(ROOT / "fixtures" / "standard-9x9.sdk")
        result = sample_sudoku(givens, seed=20260808, reads=500, sweeps=2000)
        self.assertEqual(result.status, "solved")
        self.assertEqual(len(result.solutions), 1)
        self.assertTrue(validate_solution(result.solutions[0], givens)[0])

    def test_sampler_finds_two_solutions_for_multiple_board(self) -> None:
        givens = load_board(ROOT / "fixtures" / "multiple-9x9.sdk")
        result = sample_sudoku(givens, seed=20260808, reads=500, sweeps=2000)
        self.assertEqual(result.status, "solved")
        self.assertGreaterEqual(len(result.solutions), 2)
        self.assertTrue(all(validate_solution(board, givens)[0] for board in result.solutions))

    def test_no_sample_is_reported_as_unknown(self) -> None:
        givens = load_board(ROOT / "fixtures" / "unsat-9x9.sdk")
        result = sample_sudoku(givens, seed=20260808, reads=500, sweeps=2000)
        self.assertEqual(result.status, "unknown")
        self.assertEqual(result.solutions, ())


if __name__ == "__main__":
    unittest.main()
