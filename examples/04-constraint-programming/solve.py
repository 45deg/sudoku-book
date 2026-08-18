#!/usr/bin/env python3
"""Run the MiniZinc finite-domain Sudoku model and validate its solutions."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "examples" / "common"))

from sudoku import Board, format_board, load_board, validate_solution  # noqa: E402

MODEL = Path(__file__).with_name("sudoku.mzn")


def minizinc_data(board: Board) -> str:
    side = int(len(board) ** 0.5)
    box = int(side**0.5)
    values = ", ".join(str(value) for value in board)
    return (
        f"n = {side};\n"
        f"box = {box};\n"
        f"givens = array2d(1..n, 1..n, [{values}]);\n"
    )


def parse_solutions(output: str, side: int) -> list[Board]:
    """Read boards separated by MiniZinc's solution markers."""
    solutions: list[Board] = []
    for section in output.split("----------"):
        rows = [line for line in section.splitlines() if re.fullmatch(rf"[1-{side}]{{{side}}}", line)]
        if len(rows) == side:
            solutions.append(tuple(int(char) for row in rows for char in row))
    return solutions


# BEGIN article-runner
def solve(board: Board, limit: int = 1) -> tuple[str, list[Board], str]:
    """MiniZincをGecodeで実行し、状態、解、統計情報を返します。"""
    with tempfile.TemporaryDirectory() as directory:
        # 盤面をMiniZincのデータファイルへ変換します。
        data_path = Path(directory) / "board.dzn"
        data_path.write_text(minizinc_data(board), encoding="utf-8")

        command = [
            "minizinc",
            "--solver",
            "gecode",
            "--num-solutions",
            str(limit),
            "--statistics",
            str(MODEL),
            str(data_path),
        ]
        completed = subprocess.run(command, check=True, text=True, capture_output=True)

    solutions = parse_solutions(completed.stdout, int(len(board) ** 0.5))
    for solution in solutions:
        # ソルバーの出力を、共通検証器でも確認します。
        valid, errors = validate_solution(solution, board)
        if not valid:
            raise RuntimeError("invalid MiniZinc solution: " + "; ".join(errors))

    if solutions:
        status = "solved"
    elif "=====UNSATISFIABLE=====" in completed.stdout:
        status = "unsat"
    else:
        status = "unknown"
    return status, solutions, completed.stdout
# END article-runner


def statistic(output: str, name: str) -> str | None:
    match = re.search(rf"^%%%mzn-stat: {re.escape(name)}=(.+)$", output, re.MULTILINE)
    return match.group(1) if match else None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("board", type=Path)
    parser.add_argument("--limit", type=int, choices=(1, 2), default=1)
    args = parser.parse_args()

    board = load_board(args.board)
    status, solutions, raw_output = solve(board, args.limit)
    print(f"status: {status}")
    print(f"solutions: {len(solutions)}")
    search_complete = "==========" in raw_output or "=====UNSATISFIABLE=====" in raw_output
    print(f"search_complete: {'yes' if search_complete else 'no'}")
    if status == "unsat":
        print("unique: not-applicable")
    elif len(solutions) >= 2:
        print("unique: no")
    elif len(solutions) == 1 and search_complete:
        print("unique: yes")
    else:
        print("unique: undetermined")
    for index, solution in enumerate(solutions, start=1):
        print(f"solution {index}:")
        print(format_board(solution))
    for name in ("nodes", "failures", "propagations"):
        value = statistic(raw_output, name)
        if value is not None:
            print(f"{name}: {value}")


if __name__ == "__main__":
    main()
