from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from dd.autoref import BDD, Function

from bdd_utils import decision_node_count, exactly_one

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "examples" / "common"))

from sudoku import validate_solution as validate_common_solution  # noqa: E402

SIZE = 4
BOX = 2
VariableOrder = Literal["cell", "digit"]
Board = list[list[int]]


def variable_name(row: int, column: int, digit: int) -> str:
    return f"x_{row + 1}_{column + 1}_{digit}"


def variable_names(order: VariableOrder) -> list[str]:
    if order == "cell":
        return [
            variable_name(row, column, digit)
            for row in range(SIZE)
            for column in range(SIZE)
            for digit in range(1, SIZE + 1)
        ]
    return [
        variable_name(row, column, digit)
        for digit in range(1, SIZE + 1)
        for row in range(SIZE)
        for column in range(SIZE)
    ]


@dataclass
class CompiledSudoku:
    bdd: BDD
    rules: Function
    names: list[str]


# BEGIN article-rules
def build_rules(order: VariableOrder = "cell") -> CompiledSudoku:
    bdd = BDD()
    names = variable_names(order)
    bdd.declare(*names)
    rules = bdd.true

    # 各マスには、1から4のうち一つだけを入れる。
    for row in range(SIZE):
        for column in range(SIZE):
            rules &= exactly_one(
                bdd,
                (variable_name(row, column, digit) for digit in range(1, SIZE + 1)),
            )

    # 各行では、それぞれの数字を一度だけ使う。
    for row in range(SIZE):
        for digit in range(1, SIZE + 1):
            rules &= exactly_one(
                bdd,
                (variable_name(row, column, digit) for column in range(SIZE)),
            )

    # 各列でも、それぞれの数字を一度だけ使う。
    for column in range(SIZE):
        for digit in range(1, SIZE + 1):
            rules &= exactly_one(
                bdd,
                (variable_name(row, column, digit) for row in range(SIZE)),
            )

    # 2×2ブロックでも、それぞれの数字を一度だけ使う。
    for top in range(0, SIZE, BOX):
        for left in range(0, SIZE, BOX):
            for digit in range(1, SIZE + 1):
                rules &= exactly_one(
                    bdd,
                    (
                        variable_name(row, column, digit)
                        for row in range(top, top + BOX)
                        for column in range(left, left + BOX)
                    ),
                )

    return CompiledSudoku(bdd=bdd, rules=rules, names=names)
# END article-rules


def read_board(path: Path) -> Board:
    rows = [line.strip() for line in path.read_text().splitlines() if line.strip()]
    if len(rows) != SIZE or any(len(row) != SIZE for row in rows):
        raise ValueError("盤面は4文字の行を4行指定してください")

    board: Board = []
    for row in rows:
        values = [0 if char == "." else int(char) for char in row]
        if any(value < 0 or value > SIZE for value in values):
            raise ValueError("盤面には0、.、1から4だけを指定してください")
        board.append(values)
    return board


# BEGIN article-givens
def add_givens(compiled: CompiledSudoku, board: Board) -> Function:
    formula = compiled.rules
    for row in range(SIZE):
        for column in range(SIZE):
            digit = board[row][column]
            if digit:
                # 初期配置に対応する候補を真に固定する。
                formula &= compiled.bdd.var(variable_name(row, column, digit))
    return formula
# END article-givens


def decode_model(model: dict[str, bool]) -> Board:
    board = [[0 for _ in range(SIZE)] for _ in range(SIZE)]
    for row in range(SIZE):
        for column in range(SIZE):
            selected = [
                digit
                for digit in range(1, SIZE + 1)
                if model[variable_name(row, column, digit)]
            ]
            if len(selected) != 1:
                raise ValueError("モデルがマスのexactly-one制約を満たしていません")
            board[row][column] = selected[0]
    return board


def validate_solution(puzzle: Board, solution: Board) -> None:
    expected = set(range(1, SIZE + 1))
    for row in range(SIZE):
        for column in range(SIZE):
            if puzzle[row][column] and puzzle[row][column] != solution[row][column]:
                raise ValueError("完成盤面が初期配置を保っていません")
    if any(set(row) != expected for row in solution):
        raise ValueError("完成盤面の行が1から4の順列ではありません")
    if any({solution[row][column] for row in range(SIZE)} != expected for column in range(SIZE)):
        raise ValueError("完成盤面の列が1から4の順列ではありません")
    for top in range(0, SIZE, BOX):
        for left in range(0, SIZE, BOX):
            values = {
                solution[row][column]
                for row in range(top, top + BOX)
                for column in range(left, left + BOX)
            }
            if values != expected:
                raise ValueError("完成盤面のブロックが1から4の順列ではありません")


def format_board(board: Board) -> str:
    return "\n".join("".join(str(value) for value in row) for row in board)


def flatten_board(board: Board) -> tuple[int, ...]:
    return tuple(value for row in board for value in row)


# BEGIN article-solving
def solve(path: Path, limit: int, order: VariableOrder) -> str:
    puzzle = read_board(path)
    compiled = build_rules(order)
    formula = add_givens(compiled, puzzle)

    # BDDの各経路が表す真偽割り当てを数え、解数を正確に得る。
    count = int(compiled.bdd.count(formula, nvars=len(compiled.names)))

    # care_varsを指定し、省略された変数も含む完全な割り当てを復元する。
    solutions = []
    if limit:
        models = compiled.bdd.pick_iter(formula, care_vars=set(compiled.names))
        for model in models:
            board = decode_model(model)
            validate_solution(puzzle, board)
            valid, errors = validate_common_solution(flatten_board(board), flatten_board(puzzle))
            if not valid:
                raise ValueError("共通検証器が完成盤面を拒否しました: " + "; ".join(errors))
            solutions.append(board)
            if len(solutions) == limit:
                break

    status = "unsat" if count == 0 else "solved"
    lines = [
        f"status: {status}",
        f"order: {order}",
        f"variables: {len(compiled.names)}",
        f"rule_nodes: {decision_node_count(compiled.bdd, compiled.rules)}",
        f"query_nodes: {decision_node_count(compiled.bdd, formula)}",
        f"solution_count: {count}",
        f"shown: {len(solutions)}",
    ]
    for index, board in enumerate(solutions, start=1):
        lines.extend((f"solution {index}:", format_board(board)))
    return "\n".join(lines)
# END article-solving


def main() -> None:
    parser = argparse.ArgumentParser(description="ROBDDで4×4数独を数え上げます")
    parser.add_argument("board", type=Path)
    parser.add_argument("--limit", type=int, default=2)
    parser.add_argument("--order", choices=("cell", "digit"), default="cell")
    args = parser.parse_args()
    if args.limit < 0:
        parser.error("--limitには0以上を指定してください")
    print(solve(args.board, args.limit, args.order))


if __name__ == "__main__":
    main()
