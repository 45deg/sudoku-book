#!/usr/bin/env python3
"""Solve Sudoku as quantifier-free linear integer arithmetic with Z3Py."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from math import isqrt
from pathlib import Path

from z3 import Distinct, Int, Or, SolverFor, sat, unknown, unsat

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "examples" / "common"))

from sudoku import Board, format_board, load_board, validate_solution  # noqa: E402


@dataclass(frozen=True)
class SolveResult:
    status: str
    solutions: tuple[Board, ...]
    search_complete: bool
    reason_unknown: str | None = None


# BEGIN article-model
def build_solver(board: Board):
    """盤面をQF_LIAの式へ変換し、ソルバーと81個の整数変数を返します。"""
    side = isqrt(len(board))
    box = isqrt(side)
    cells = [[Int(f"cell_{row + 1}_{col + 1}") for col in range(side)] for row in range(side)]
    solver = SolverFor("QF_LIA")

    # 各マスは、盤面の大きさに応じた数字だけを取ります。
    for row in range(side):
        for col in range(side):
            solver.add(1 <= cells[row][col], cells[row][col] <= side)

    # 同じ行と列の整数を、すべて異なる値に制約します。
    for row in range(side):
        solver.add(Distinct(cells[row]))
    for col in range(side):
        solver.add(Distinct([cells[row][col] for row in range(side)]))

    # 各ブロックにも、行や列と同じDistinct制約を加えます。
    for box_row in range(0, side, box):
        for box_col in range(0, side, box):
            solver.add(
                Distinct(
                    [
                        cells[row][col]
                        for row in range(box_row, box_row + box)
                        for col in range(box_col, box_col + box)
                    ]
                )
            )

    # 初期配置があるマスは、その整数に固定します。
    for position, given in enumerate(board):
        if given:
            row, col = divmod(position, side)
            solver.add(cells[row][col] == given)

    return solver, cells
# END article-model


def board_from_model(model, cells) -> Board:
    # 数学的な整数値を、共通盤面形式のPython整数へ変換します。
    return tuple(model.eval(cell).as_long() for row in cells for cell in row)


# BEGIN article-enumeration
def solve(board: Board, limit: int = 1) -> SolveResult:
    solver, cells = build_solver(board)
    solutions: list[Board] = []

    while len(solutions) < limit:
        result = solver.check()
        if result == sat:
            # モデルを完成盤面として読み戻し、別の検証器でも確かめます。
            solution = board_from_model(solver.model(), cells)
            valid, errors = validate_solution(solution, board)
            if not valid:
                raise RuntimeError("invalid Z3 model: " + "; ".join(errors))
            solutions.append(solution)

            # 次のcheckでは、今の盤面と少なくとも一マス違う解を要求します。
            solver.add(
                Or(
                    [
                        cells[row][col] != solution[row * len(cells) + col]
                        for row in range(len(cells))
                        for col in range(len(cells))
                    ]
                )
            )
        elif result == unsat:
            status = "solved" if solutions else "unsat"
            return SolveResult(status, tuple(solutions), search_complete=True)
        elif result == unknown:
            # unknownをunsatとして扱わず、Z3が返す理由も保存します。
            status = "solved" if solutions else "unknown"
            return SolveResult(status, tuple(solutions), False, solver.reason_unknown())
        else:
            raise RuntimeError(f"unexpected Z3 result: {result}")

    return SolveResult("solved", tuple(solutions), search_complete=False)
# END article-enumeration


def describe_result(result: SolveResult) -> str:
    lines = [
        f"status: {result.status}",
        f"solutions: {len(result.solutions)}",
        f"search_complete: {'yes' if result.search_complete else 'no'}",
    ]
    if result.status == "unsat":
        lines.append("unique: not-applicable")
    elif len(result.solutions) >= 2:
        lines.append("unique: no")
    elif len(result.solutions) == 1 and result.search_complete:
        lines.append("unique: yes")
    else:
        lines.append("unique: undetermined")
    if result.reason_unknown:
        lines.append(f"reason_unknown: {result.reason_unknown}")
    for index, solution in enumerate(result.solutions, start=1):
        lines.append(f"solution {index}:")
        lines.append(format_board(solution))
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("board", type=Path)
    parser.add_argument("--limit", type=int, choices=(1, 2), default=1)
    args = parser.parse_args()

    board = load_board(args.board)
    print(describe_result(solve(board, args.limit)))


if __name__ == "__main__":
    main()
