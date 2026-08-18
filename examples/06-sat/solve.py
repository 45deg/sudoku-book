"""Encode 9x9 Sudoku as CNF and solve it with MiniSat 2.2."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path

from pysat.solvers import Minisat22

ROOT = Path(__file__).resolve().parents[2]
COMMON = ROOT / "examples" / "common"
sys.path.insert(0, str(COMMON))

from sudoku import Board, board_geometry, format_board, load_board, validate_solution  # noqa: E402

VARIABLES = 9 * 9 * 9
BASE_CLAUSES = 11_988


@dataclass(frozen=True)
class Result:
    status: str
    solutions: tuple[Board, ...]
    exhausted: bool
    variables: int
    base_clauses: int
    clue_clauses: int
    solve_calls: int


# BEGIN article-variable
def candidate_var(row: int, col: int, digit: int) -> int:
    """Return the SAT variable for ``cell[row, col] == digit``."""
    return row * 81 + col * 9 + digit
# END article-variable


# BEGIN article-exactly-one
def exactly_one(literals: list[int]) -> list[list[int]]:
    clauses = [literals]
    # どの2個も同時に真にならないよう、すべての組に禁止節を加えます。
    clauses.extend([-left, -right] for left, right in combinations(literals, 2))
    return clauses
# END article-exactly-one


# BEGIN article-encode
def sudoku_cnf(givens: Board) -> list[list[int]]:
    side, box_side = board_geometry(givens)
    if side != 9:
        raise ValueError("this example supports 9x9 Sudoku only")

    clauses: list[list[int]] = []

    # 各マスには、1〜9のうちちょうど一つが入ります。
    for row in range(side):
        for col in range(side):
            clauses.extend(
                exactly_one([candidate_var(row, col, digit) for digit in range(1, side + 1)])
            )

    # 各行では、それぞれの数字がちょうど一度だけ現れます。
    for row in range(side):
        for digit in range(1, side + 1):
            clauses.extend(
                exactly_one([candidate_var(row, col, digit) for col in range(side)])
            )

    # 各列にも、同じexactly-one制約を置きます。
    for col in range(side):
        for digit in range(1, side + 1):
            clauses.extend(
                exactly_one([candidate_var(row, col, digit) for row in range(side)])
            )

    # 各3×3ブロックでも、それぞれの数字を一つに絞ります。
    for box_row in range(0, side, box_side):
        for box_col in range(0, side, box_side):
            for digit in range(1, side + 1):
                block = [
                    candidate_var(row, col, digit)
                    for row in range(box_row, box_row + box_side)
                    for col in range(box_col, box_col + box_side)
                ]
                clauses.extend(exactly_one(block))

    # 初期配置は、対応する候補変数を真にする単位節です。
    for position, given in enumerate(givens):
        if given:
            row, col = divmod(position, side)
            clauses.append([candidate_var(row, col, given)])

    return clauses
# END article-encode


# BEGIN article-decode
def decode_model(model: list[int]) -> Board:
    positive = {literal for literal in model if literal > 0}
    cells: list[int] = []
    for row in range(9):
        for col in range(9):
            digits = [
                digit
                for digit in range(1, 10)
                if candidate_var(row, col, digit) in positive
            ]
            if len(digits) != 1:
                raise ValueError(f"model does not choose one digit at row {row}, col {col}")
            cells.append(digits[0])
    return tuple(cells)
# END article-decode


def block_board(board: Board) -> list[int]:
    """Return a clause that excludes exactly this completed board."""
    return [
        -candidate_var(row, col, board[row * 9 + col])
        for row in range(9)
        for col in range(9)
    ]


# BEGIN article-solve
def solve(givens: Board, limit: int = 2) -> Result:
    if limit < 1:
        raise ValueError("limit must be positive")

    clauses = sudoku_cnf(givens)
    clue_clauses = sum(value != 0 for value in givens)
    found: list[Board] = []
    solve_calls = 0

    with Minisat22(bootstrap_with=clauses) as solver:
        # 表示数より一つ多く探し、まだ別解があるかも確認します。
        while len(found) <= limit:
            solve_calls += 1
            if not solver.solve():
                exhausted = True
                break

            model = solver.get_model()
            if model is None:
                raise RuntimeError("MiniSat returned SAT without a model")
            board = decode_model(model)
            found.append(board)

            # 完成盤面を禁止して、同じCNFから次の解を探します。
            solver.add_clause(block_board(board))
        else:
            exhausted = False

    solutions = tuple(found[:limit])
    status = "solved" if solutions else "unsat"
    return Result(
        status=status,
        solutions=solutions,
        exhausted=exhausted,
        variables=VARIABLES,
        base_clauses=BASE_CLAUSES,
        clue_clauses=clue_clauses,
        solve_calls=solve_calls,
    )
# END article-solve


def uniqueness(result: Result) -> str:
    if not result.solutions:
        return "n/a"
    if len(result.solutions) >= 2:
        return "not unique"
    if result.exhausted:
        return "unique"
    return "not checked"


def describe_result(result: Result, givens: Board) -> str:
    lines = [
        f"status: {result.status}",
        "solver: MiniSat 2.2 via PySAT",
        f"variables: {result.variables}",
        f"base clauses: {result.base_clauses}",
        f"clue clauses: {result.clue_clauses}",
        f"total input clauses: {result.base_clauses + result.clue_clauses}",
        f"solve calls: {result.solve_calls}",
        f"solutions: {len(result.solutions)}",
        f"search exhausted: {'yes' if result.exhausted else 'no'}",
        f"uniqueness: {uniqueness(result)}",
    ]
    for number, solution in enumerate(result.solutions, start=1):
        valid, _ = validate_solution(solution, givens)
        lines.extend(
            [
                "",
                f"solution {number} (valid: {'yes' if valid else 'no'}):",
                format_board(solution),
            ]
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("board", type=Path)
    parser.add_argument("--limit", type=int, default=2)
    args = parser.parse_args()

    givens = load_board(args.board)
    print(describe_result(solve(givens, args.limit), givens))


if __name__ == "__main__":
    main()
