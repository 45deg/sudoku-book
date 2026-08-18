#!/usr/bin/env python3
"""Solve Sudoku as a binary integer linear program with HiGHS."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from math import isqrt
from pathlib import Path

import highspy

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
def build_model(board: Board):
    """数独を0-1整数計画モデルへ変換します。"""
    side = isqrt(len(board))
    box = isqrt(side)
    model = highspy.Highs()
    model.setOptionValue("output_flag", False)

    # x[r,c,d]は、マス(r,c)へ数字dを置くときだけ1になります。
    x = {
        (row, col, digit): model.addBinary(name=f"x_{row + 1}_{col + 1}_{digit + 1}")
        for row in range(side)
        for col in range(side)
        for digit in range(side)
    }

    # 各マスでは、候補となる数字をちょうど一つ選びます。
    for row in range(side):
        for col in range(side):
            model.addConstr(sum(x[row, col, digit] for digit in range(side)) == 1)

    # 各行と各列では、それぞれの数字をちょうど一回使います。
    for digit in range(side):
        for row in range(side):
            model.addConstr(sum(x[row, col, digit] for col in range(side)) == 1)
        for col in range(side):
            model.addConstr(sum(x[row, col, digit] for row in range(side)) == 1)

    # 各ブロックでも、それぞれの数字をちょうど一回使います。
    for digit in range(side):
        for box_row in range(0, side, box):
            for box_col in range(0, side, box):
                model.addConstr(
                    sum(
                        x[row, col, digit]
                        for row in range(box_row, box_row + box)
                        for col in range(box_col, box_col + box)
                    )
                    == 1
                )

    # 初期配置に対応する二値変数は1に固定します。
    for position, given in enumerate(board):
        if given:
            row, col = divmod(position, side)
            model.addConstr(x[row, col, given - 1] == 1)

    # 目的係数はすべて0です。今回は制約を満たす点だけを探します。
    return model, x
# END article-model


def board_from_solution(model, x, side: int) -> Board:
    values = model.vals(x)
    result: list[int] = []
    for row in range(side):
        for col in range(side):
            chosen = [digit for digit in range(side) if values[row, col, digit] > 0.5]
            if len(chosen) != 1:
                raise RuntimeError(f"cell ({row}, {col}) does not have one selected digit")
            result.append(chosen[0] + 1)
    return tuple(result)


# BEGIN article-enumeration
def solve(board: Board, limit: int = 1) -> SolveResult:
    side = isqrt(len(board))
    model, x = build_model(board)
    solutions: list[Board] = []

    while len(solutions) < limit:
        model.run()
        model_status = model.getModelStatus()

        if model_status == highspy.HighsModelStatus.kOptimal:
            # 目的値0の最適解は、数独の全制約を満たす実行可能解です。
            solution = board_from_solution(model, x, side)
            valid, errors = validate_solution(solution, board)
            if not valid:
                raise RuntimeError("invalid HiGHS solution: " + "; ".join(errors))
            solutions.append(solution)

            # 完成盤面で選ばれた変数のうち、次の解では少なくとも一つを0にします。
            selected = [
                x[row, col, solution[row * side + col] - 1]
                for row in range(side)
                for col in range(side)
            ]
            model.addConstr(sum(selected) <= side * side - 1)

        elif model_status == highspy.HighsModelStatus.kInfeasible:
            status = "solved" if solutions else "unsat"
            return SolveResult(status, tuple(solutions), search_complete=True)
        else:
            # 制限到達や中断を、実行不能と取り違えないようにします。
            status = "solved" if solutions else "unknown"
            reason = model.modelStatusToString(model_status)
            return SolveResult(status, tuple(solutions), False, reason)

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
