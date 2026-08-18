from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "examples" / "common"))

from sudoku import Board, load_board, validate_solution  # noqa: E402

from qubo import build_qubo, variable  # noqa: E402
from solve import sample_sudoku  # noqa: E402


def exact_solution_count(givens: Board, limit: int = 3) -> int:
    """Small reference search used only to classify the test boards."""
    side = 4
    board = list(givens)
    count = 0

    def candidates(index: int) -> set[int]:
        row, column = divmod(index, side)
        used = set(board[row * side : (row + 1) * side])
        used.update(board[column::side])
        top, left = row // 2 * 2, column // 2 * 2
        used.update(board[r * side + c] for r in range(top, top + 2) for c in range(left, left + 2))
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
    def test_solution_has_zero_energy(self) -> None:
        givens = load_board(HERE / "boards" / "unique-4x4.sdk")
        solution = (1, 2, 3, 4, 3, 4, 1, 2, 2, 1, 4, 3, 4, 3, 2, 1)
        sample = {
            variable(row, column, digit): int(solution[row * 4 + column] == digit)
            for row in range(4)
            for column in range(4)
            for digit in range(1, 5)
        }
        self.assertAlmostEqual(build_qubo(givens).energy(sample), 0.0)

    def test_one_hot_violation_has_positive_energy(self) -> None:
        givens = (0,) * 16
        sample = {item: 0 for item in build_qubo(givens).variables}
        self.assertGreater(build_qubo(givens).energy(sample), 0.0)

    def test_reference_board_categories(self) -> None:
        unique = load_board(HERE / "boards" / "unique-4x4.sdk")
        multiple = load_board(HERE / "boards" / "multiple-4x4.sdk")
        unsat = load_board(HERE / "boards" / "unsat-4x4.sdk")
        self.assertEqual(exact_solution_count(unique), 1)
        self.assertGreaterEqual(exact_solution_count(multiple), 2)
        self.assertEqual(exact_solution_count(unsat), 0)

    def test_sampler_finds_valid_unique_solution(self) -> None:
        givens = load_board(HERE / "boards" / "unique-4x4.sdk")
        result = sample_sudoku(givens, seed=20260808, reads=500, sweeps=2000)
        self.assertEqual(result.status, "solved")
        self.assertEqual(len(result.solutions), 1)
        self.assertTrue(validate_solution(result.solutions[0], givens)[0])

    def test_sampler_finds_two_solutions_for_empty_board(self) -> None:
        givens = load_board(HERE / "boards" / "multiple-4x4.sdk")
        result = sample_sudoku(givens, seed=20260808, reads=500, sweeps=2000)
        self.assertEqual(result.status, "solved")
        self.assertGreaterEqual(len(result.solutions), 2)
        self.assertTrue(all(validate_solution(board, givens)[0] for board in result.solutions))

    def test_no_sample_is_reported_as_unknown(self) -> None:
        givens = load_board(HERE / "boards" / "unsat-4x4.sdk")
        result = sample_sudoku(givens, seed=20260808, reads=500, sweeps=2000)
        self.assertEqual(result.status, "unknown")
        self.assertEqual(result.solutions, ())


if __name__ == "__main__":
    unittest.main()
