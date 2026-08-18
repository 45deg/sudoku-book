"""Solve Sudoku by enumerating stable models with clingo."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import clingo

HERE = Path(__file__).resolve().parent
COMMON = HERE.parent / "common"
sys.path.insert(0, str(COMMON))

from sudoku import Board, format_board, load_board, validate_solution  # noqa: E402

PROGRAM = HERE / "sudoku.lp"


@dataclass(frozen=True)
class AspResult:
    status: str
    solutions: tuple[Board, ...]
    exhausted: bool


def given_facts(board: Board) -> str:
    facts = []
    for position, digit in enumerate(board):
        if digit:
            row, column = divmod(position, 9)
            facts.append(f"given({row + 1},{column + 1},{digit}).")
    return "\n".join(facts)


def board_from_model(model: clingo.Model) -> Board:
    board = [0] * 81
    for symbol in model.symbols(shown=True):
        if symbol.name != "value" or len(symbol.arguments) != 3:
            continue
        row, column, digit = (argument.number for argument in symbol.arguments)
        board[(row - 1) * 9 + column - 1] = digit
    return tuple(board)


# BEGIN article-clingo-runner
def solve(board: Board, limit: int = 1) -> AspResult:
    if limit < 1:
        raise ValueError("limit must be positive")

    control = clingo.Control(["--warn=none"])
    control.configuration.solve.models = limit
    control.load(str(PROGRAM))
    # 初期配置をgiven/3の事実として、数独の規則と同じprogram partへ加える。
    control.add("base", [], given_facts(board))

    # 変数を具体的な定数へ展開してから、安定モデルを探索する。
    control.ground([("base", [])])
    solutions: list[Board] = []
    with control.solve(yield_=True) as handle:
        for model in handle:
            solutions.append(board_from_model(model))
        result = handle.get()

    status = "solved" if solutions else "unsat" if result.unsatisfiable else "unknown"
    return AspResult(status, tuple(solutions), result.exhausted)
# END article-clingo-runner


def checked_solve(board: Board, limit: int = 1) -> AspResult:
    result = solve(board, limit)
    for solution in result.solutions:
        valid, errors = validate_solution(solution, board)
        if not valid:
            raise AssertionError(errors)
    return result


def format_result(result: AspResult, limit: int) -> str:
    lines = [
        f"engine: clingo {clingo.__version__}",
        f"limit: {limit}",
        f"models: {len(result.solutions)}",
        f"exhausted: {'yes' if result.exhausted else 'no'}",
        f"status: {result.status}",
    ]
    for number, solution in enumerate(result.solutions, start=1):
        lines.extend([f"answer {number}:", format_board(solution)])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("board", type=Path)
    parser.add_argument("--limit", type=int, default=1)
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be positive")

    board = load_board(args.board)
    print(format_result(checked_solve(board, args.limit), args.limit), end="")


if __name__ == "__main__":
    main()

