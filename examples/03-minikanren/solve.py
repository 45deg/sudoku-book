"""Solve 4x4 Sudoku as a collection of kanren relations."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from kanren import eq, permuteq, run, vars

ROOT = Path(__file__).resolve().parents[2]
COMMON = ROOT / "examples" / "common"
sys.path.insert(0, str(COMMON))

from sudoku import Board, board_geometry, format_board, load_board, units, validate_solution  # noqa: E402


@dataclass(frozen=True)
class Result:
    status: str
    solutions: tuple[Board, ...]
    exhausted: bool


# BEGIN article-relation
def sudoku_relation(givens: Board):
    side, _ = board_geometry(givens)
    if side != 4:
        raise ValueError("this example supports 4x4 Sudoku only")

    cells = tuple(vars(len(givens)))
    digits = tuple(range(1, side + 1))
    goals = []

    for cell, given in zip(cells, givens):
        if given:
            # 初期配置を、セルと数字が等しいというゴールにします。
            goals.append((eq, cell, given))

    for unit in units(givens):
        unit_cells = tuple(cells[index] for index in unit)
        # 各行・列・ブロックを1〜4の順列と単一化します。
        goals.append((permuteq, unit_cells, digits))

    return cells, tuple(goals)
# END article-relation


# BEGIN article-solve
def solve(givens: Board, limit: int = 2) -> Result:
    if limit < 1:
        raise ValueError("limit must be positive")

    cells, goals = sudoku_relation(givens)

    # 表示数より一つ多く要求し、まだ別解が残っているか確かめます。
    found = tuple(tuple(answer) for answer in run(limit + 1, cells, *goals))
    exhausted = len(found) <= limit
    solutions = found[:limit]
    status = "solved" if solutions else "unsat"
    return Result(status, solutions, exhausted)
# END article-solve


def uniqueness(result: Result) -> str:
    if not result.solutions:
        return "n/a"
    if len(result.solutions) >= 2:
        return "not unique"
    if result.exhausted:
        return "unique"
    return "not checked"


def describe_result(result: Result, givens: Board, limit: int) -> str:
    lines = [
        f"status: {result.status}",
        "method: kanren permutation relations",
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
    if len(result.solutions) == limit and not result.exhausted:
        lines.extend(["", f"stopped after {limit} displayed solutions"])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("board", type=Path)
    parser.add_argument("--limit", type=int, default=2)
    args = parser.parse_args()

    givens = load_board(args.board)
    result = solve(givens, args.limit)
    print(describe_result(result, givens, args.limit))


if __name__ == "__main__":
    main()
