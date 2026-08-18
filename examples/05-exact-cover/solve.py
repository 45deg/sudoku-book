"""Convert Sudoku to exact cover and solve it with Algorithm X."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
COMMON = HERE.parent / "common"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(COMMON))

from exact_cover import ExactCoverResult, solve_exact_cover  # noqa: E402
from sudoku import Board, board_geometry, format_board, load_board, validate_solution  # noqa: E402

Choice = tuple[int, int, int]
Constraint = tuple[str, int, int]


@dataclass(frozen=True)
class SudokuModel:
    rows: dict[Choice, tuple[Constraint, ...]]
    columns: tuple[Constraint, ...]
    side: int


@dataclass(frozen=True)
class SudokuResult:
    solutions: tuple[Board, ...]
    exhausted: bool
    candidate_rows: int
    constraint_columns: int
    search: ExactCoverResult[Choice]

    @property
    def status(self) -> str:
        return "solved" if self.solutions else "unsat"


# BEGIN article-sudoku-model
def build_sudoku_model(givens: Board) -> SudokuModel:
    side, box_side = board_geometry(givens)
    columns: list[Constraint] = []
    for row in range(side):
        for column in range(side):
            columns.append(("cell", row, column))
    for unit in range(side):
        for digit in range(1, side + 1):
            columns.extend(
                [
                    ("row-digit", unit, digit),
                    ("column-digit", unit, digit),
                    ("box-digit", unit, digit),
                ]
            )

    rows: dict[Choice, tuple[Constraint, ...]] = {}
    for position, given in enumerate(givens):
        row, column = divmod(position, side)
        box = (row // box_side) * box_side + column // box_side
        digits = (given,) if given else range(1, side + 1)
        for digit in digits:
            # 「このマスへこの数字を置く」という候補は、四つの条件を覆う。
            rows[(row, column, digit)] = (
                ("cell", row, column),
                ("row-digit", row, digit),
                ("column-digit", column, digit),
                ("box-digit", box, digit),
            )

    return SudokuModel(rows, tuple(columns), side)
# END article-sudoku-model


def decode_solution(choices: tuple[Choice, ...], side: int) -> Board:
    board = [0] * (side * side)
    for row, column, digit in choices:
        board[row * side + column] = digit
    return tuple(board)


def solve(givens: Board, limit: int = 1) -> SudokuResult:
    model = build_sudoku_model(givens)
    search = solve_exact_cover(model.rows, limit, model.columns)
    solutions = tuple(decode_solution(choice_rows, model.side) for choice_rows in search.solutions)
    for solution in solutions:
        valid, errors = validate_solution(solution, givens)
        if not valid:
            raise AssertionError(errors)
    return SudokuResult(
        solutions,
        search.exhausted,
        len(model.rows),
        len(model.columns),
        search,
    )


def format_result(result: SudokuResult, limit: int) -> str:
    lines = [
        "method: Algorithm X with Python sets",
        f"candidate rows: {result.candidate_rows}",
        f"constraint columns: {result.constraint_columns}",
        f"limit: {limit}",
        f"solutions: {len(result.solutions)}",
        f"exhausted: {'yes' if result.exhausted else 'no'}",
        f"nodes: {result.search.stats.nodes}",
        f"branches: {result.search.stats.branches}",
        f"dead ends: {result.search.stats.dead_ends}",
        f"status: {result.status}",
    ]
    for number, solution in enumerate(result.solutions, start=1):
        lines.extend([f"solution {number}:", format_board(solution)])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("board", type=Path)
    parser.add_argument("--limit", type=int, default=1)
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be positive")

    result = solve(load_board(args.board), args.limit)
    print(format_result(result, args.limit), end="")


if __name__ == "__main__":
    main()

