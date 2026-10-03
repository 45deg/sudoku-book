"""9x9 Sudoku as a quadratic unconstrained binary optimization model."""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations
from typing import Iterable

import dimod

SIZE = 9
BOX = 3
Board = tuple[int, ...]
Variable = tuple[int, int, int]


def variable(row: int, column: int, digit: int) -> Variable:
    """Return the label for candidate ``digit`` at ``(row, column)``."""
    return row, column, digit


# BEGIN article-penalty-builder
def add_exactly_one(
    linear: dict[Variable, float],
    quadratic: dict[tuple[Variable, Variable], float],
    choices: Iterable[Variable],
    weight: float,
) -> float:
    """Add ``weight * (sum(choices) - 1)^2`` and return its offset."""
    variables = tuple(choices)

    # x^2 = x なので、各候補の一次係数は -weight になる。
    for item in variables:
        linear[item] += -weight

    # 二候補を同時に選んだ分は、2 * weight * x_i * x_j で数える。
    for first, second in combinations(variables, 2):
        pair = tuple(sorted((first, second)))
        quadratic[pair] += 2 * weight

    # 展開前の式に含まれる定数項 weight を返す。
    return weight
# END article-penalty-builder


# BEGIN article-build-model
def build_qubo(givens: Board, weight: float = 1.0) -> dimod.BinaryQuadraticModel:
    if len(givens) != SIZE * SIZE:
        raise ValueError("この例は9×9数独だけを扱います")

    linear: defaultdict[Variable, float] = defaultdict(float)
    quadratic: defaultdict[tuple[Variable, Variable], float] = defaultdict(float)
    offset = 0.0

    # 各マスでは、九つの数字候補から一つだけを選ぶ。
    for row in range(SIZE):
        for column in range(SIZE):
            offset += add_exactly_one(
                linear,
                quadratic,
                (variable(row, column, digit) for digit in range(1, SIZE + 1)),
                weight,
            )

    # 各行では、それぞれの数字を一度だけ選ぶ。
    for row in range(SIZE):
        for digit in range(1, SIZE + 1):
            offset += add_exactly_one(
                linear,
                quadratic,
                (variable(row, column, digit) for column in range(SIZE)),
                weight,
            )

    # 各列でも、それぞれの数字を一度だけ選ぶ。
    for column in range(SIZE):
        for digit in range(1, SIZE + 1):
            offset += add_exactly_one(
                linear,
                quadratic,
                (variable(row, column, digit) for row in range(SIZE)),
                weight,
            )

    # 各3×3ブロックでも、それぞれの数字を一度だけ選ぶ。
    for top in range(0, SIZE, BOX):
        for left in range(0, SIZE, BOX):
            for digit in range(1, SIZE + 1):
                offset += add_exactly_one(
                    linear,
                    quadratic,
                    (
                        variable(row, column, digit)
                        for row in range(top, top + BOX)
                        for column in range(left, left + BOX)
                    ),
                    weight,
                )

    # 初期配置の候補は1にする。(x - 1)^2 は二値変数なら 1 - x になる。
    for index, digit in enumerate(givens):
        if digit:
            row, column = divmod(index, SIZE)
            linear[variable(row, column, digit)] += -weight
            offset += weight

    return dimod.BinaryQuadraticModel(linear, quadratic, offset, dimod.BINARY)
# END article-build-model


# BEGIN article-fixed-candidates
def fixed_candidates(givens: Board) -> dict[Variable, int]:
    fixed: dict[Variable, int] = {}
    for row in range(SIZE):
        for column in range(SIZE):
            given = givens[row * SIZE + column]
            top, left = row // BOX * BOX, column // BOX * BOX
            used = set(givens[row * SIZE : (row + 1) * SIZE])
            used.update(givens[column::SIZE])
            used.update(
                givens[r * SIZE + c]
                for r in range(top, top + BOX)
                for c in range(left, left + BOX)
            )
            for digit in range(1, SIZE + 1):
                if given:
                    # 初期配置のマスは、指定数字だけを1に固定する。
                    fixed[variable(row, column, digit)] = int(digit == given)
                elif digit in used:
                    # 同じ行・列・ブロックの初期配置と衝突する候補は0にする。
                    fixed[variable(row, column, digit)] = 0
    return fixed
# END article-fixed-candidates
