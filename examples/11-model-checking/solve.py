#!/usr/bin/env python3
"""Solve Sudoku as a reachability problem checked by nuXmv."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from math import isqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "examples" / "common"))

from sudoku import (  # noqa: E402
    Board,
    boards_are_distinct,
    format_board,
    load_board,
    units,
    validate_solution,
)


@dataclass(frozen=True)
class InvariantResult:
    outcome: str
    output: str


@dataclass(frozen=True)
class SolveResult:
    status: str
    solutions: tuple[Board, ...]
    search_complete: bool
    checks: int
    reason_unknown: str | None = None


def cell_name(index: int, side: int) -> str:
    row, column = divmod(index, side)
    return f"cell_{row + 1}_{column + 1}"


def exclusion_expression(solution: Board) -> str:
    side = isqrt(len(solution))
    equalities = [
        f"{cell_name(index, side)} = {digit}"
        for index, digit in enumerate(solution)
    ]
    return "(" + " & ".join(equalities) + ")"


# BEGIN article-model
def build_model(board: Board, excluded: tuple[Board, ...] = ()) -> str:
    """盤面を有限状態機械として表すnuXmvモデルを作ります。"""
    side = isqrt(len(board))
    empty_cells = [index for index, value in enumerate(board) if value == 0]
    order = {index: step for step, index in enumerate(empty_cells)}
    choices = "{" + ", ".join(str(digit) for digit in range(1, side + 1)) + "}"

    lines = ["MODULE main", "", "VAR", f"  step : 0..{len(empty_cells)};"]
    lines.extend(
        f"  {cell_name(index, side)} : 0..{side};"
        for index in range(len(board))
    )

    lines.extend(("", "ASSIGN", "  init(step) := 0;"))
    if empty_cells:
        lines.extend(
            (
                "  next(step) := case",
                f"    step < {len(empty_cells)} : step + 1;",
                "    TRUE : step;",
                "  esac;",
            )
        )
    else:
        lines.append("  next(step) := step;")

    for index, given in enumerate(board):
        name = cell_name(index, side)
        lines.append(f"  init({name}) := {given};")
        if given:
            lines.append(f"  next({name}) := {name};")
        else:
            # このマスの手番だけ、1から盤面サイズまでの値を非決定的に選びます。
            lines.extend(
                (
                    f"  next({name}) := case",
                    f"    step = {order[index]} : {choices};",
                    f"    TRUE : {name};",
                    "  esac;",
                )
            )

    # 同じ行、列、ブロックにある二マスは、0以外の同じ値を取れません。
    peer_pairs = {
        tuple(sorted((first, second)))
        for unit in units(board)
        for offset, first in enumerate(unit)
        for second in unit[offset + 1 :]
    }
    lines.append("")
    for first, second in sorted(peer_pairs):
        left = cell_name(first, side)
        right = cell_name(second, side)
        lines.append(f"INVAR {left} = 0 | {right} = 0 | {left} != {right};")

    # 全空きマスを埋めた状態のうち、既に見つけた盤面は目標から外します。
    goal = f"step = {len(empty_cells)}"
    for solution in excluded:
        goal += f" & !{exclusion_expression(solution)}"
    lines.extend(
        (
            "",
            "DEFINE",
            f"  goal := {goal};",
            "",
            "-- goalへ到達しないという安全性を、既知の最大深さで検査します。",
            "LTLSPEC NAME goal_is_unreachable := G !goal;",
        )
    )
    return "\n".join(lines) + "\n"
# END article-model


def find_nuxmv(explicit: str | None = None) -> str:
    candidates = [
        explicit,
        os.environ.get("NUXMV"),
        shutil.which("nuXmv.sh"),
        shutil.which("nuXmv"),
    ]
    for candidate in candidates:
        if candidate:
            return candidate
    raise FileNotFoundError(
        "nuXmvが見つかりません。--nuxmvまたは環境変数NUXMVでnuXmv.shを指定してください"
    )


# BEGIN article-check
def check_invariant(model_text: str, nuxmv: str, bound: int) -> InvariantResult:
    """指定した深さで、目標へ到達しないという性質を検査します。"""
    with tempfile.TemporaryDirectory(prefix="sudoku-nuxmv-") as directory:
        model_path = Path(directory) / "sudoku.smv"
        model_path.write_text(model_text, encoding="utf-8")
        commands = "\n".join(
            (
                f"read_model -i {model_path}",
                "go_bmc",
                f"check_ltlspec_bmc_onepb -P goal_is_unreachable -k {bound} -l X",
                "quit",
                "",
            )
        )
        try:
            completed = subprocess.run(
                [nuxmv, "-int"],
                input=commands,
                text=True,
                capture_output=True,
                timeout=120,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return InvariantResult("unknown", "nuXmv timed out after 120 seconds")

    output = completed.stdout + completed.stderr
    if completed.returncode != 0:
        raise RuntimeError(f"nuXmv exited with {completed.returncode}:\n{output}")
    if re.search(r"-- specification .* is false", output):
        return InvariantResult("counterexample", output)
    if "-- no counterexample found with bound" in output:
        return InvariantResult("no_counterexample", output)
    if re.search(r"-- specification .* is unknown", output):
        return InvariantResult("unknown", output)
    raise RuntimeError("nuXmvの検査結果を読み取れませんでした:\n" + output)
# END article-check


def solution_from_trace(output: str, board: Board) -> Board:
    side = isqrt(len(board))
    values = list(board)
    pattern = re.compile(r"cell_(\d+)_(\d+) = (\d+)")
    for row_text, column_text, value_text in pattern.findall(output):
        row = int(row_text) - 1
        column = int(column_text) - 1
        values[row * side + column] = int(value_text)
    solution = tuple(values)
    valid, errors = validate_solution(solution, board)
    if not valid:
        raise RuntimeError("nuXmvの反例から復元した盤面が不正です: " + "; ".join(errors))
    return solution


# BEGIN article-enumeration
def solve(board: Board, nuxmv: str, limit: int = 1) -> SolveResult:
    solutions: list[Board] = []
    checks = 0
    bound = sum(value == 0 for value in board)

    while len(solutions) < limit:
        # 見つけた盤面を目標から除き、別の完成状態へ到達できるか再検査します。
        model = build_model(board, tuple(solutions))
        result = check_invariant(model, nuxmv, bound)
        checks += 1

        if result.outcome == "counterexample":
            # 「到達しない」が偽なので、反例は完成状態までの実行経路です。
            solution = solution_from_trace(result.output, board)
            if solution in solutions:
                raise RuntimeError("除外した盤面が再び返されました")
            solutions.append(solution)
        elif result.outcome == "no_counterexample":
            status = "solved" if solutions else "unsat"
            return SolveResult(status, tuple(solutions), True, checks)
        else:
            status = "solved" if solutions else "unknown"
            return SolveResult(status, tuple(solutions), False, checks, "BMC returned unknown")

    return SolveResult("solved", tuple(solutions), False, checks)
# END article-enumeration


def describe_result(result: SolveResult) -> str:
    lines = [
        f"status: {result.status}",
        "engine: nuXmv BMC",
        f"checks: {result.checks}",
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
    parser.add_argument("--nuxmv")
    args = parser.parse_args()

    try:
        nuxmv = find_nuxmv(args.nuxmv)
    except FileNotFoundError as error:
        parser.error(str(error))
    board = load_board(args.board)
    result = solve(board, nuxmv, args.limit)
    if not boards_are_distinct(result.solutions):
        raise RuntimeError("同じ盤面が複数回返されました")
    print(describe_result(result))


if __name__ == "__main__":
    main()
