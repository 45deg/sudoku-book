from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from math import isqrt
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "examples" / "common"))

from sudoku import Board, board_geometry, format_board, load_board, validate_solution  # noqa: E402

FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class Result:
    status: str
    seed: int
    beta: float
    tolerance: float
    max_iterations: int
    iterations: int
    initial_residual: float
    final_residual: float
    solution: Board | None
    validation_errors: tuple[str, ...] = ()


# BEGIN article-divide
def project_divide(values: FloatArray, givens: Board) -> FloatArray:
    """四種類の局所制約を、複製ごとに独立して満たす。"""
    _, side, _, _ = values.shape
    box_side = isqrt(side)
    projected = np.zeros_like(values)

    # 複製0では、各マスで最も大きな候補を一つだけ残す。
    for row in range(side):
        for column in range(side):
            given = givens[row * side + column]
            digit = given - 1 if given else int(np.argmax(values[0, row, column]))
            projected[0, row, column, digit] = 1.0

    # 複製1では、行ごとに各数字を置く列を一つだけ選ぶ。
    for row in range(side):
        for digit in range(side):
            column = int(np.argmax(values[1, row, :, digit]))
            projected[1, row, column, digit] = 1.0

    # 複製2では、列ごとに各数字を置く行を一つだけ選ぶ。
    for column in range(side):
        for digit in range(side):
            row = int(np.argmax(values[2, :, column, digit]))
            projected[2, row, column, digit] = 1.0

    # 複製3では、ブロックごとに各数字を置くマスを一つだけ選ぶ。
    for top in range(0, side, box_side):
        for left in range(0, side, box_side):
            for digit in range(side):
                block = values[
                    3,
                    top : top + box_side,
                    left : left + box_side,
                    digit,
                ]
                offset = int(np.argmax(block))
                row_offset, column_offset = divmod(offset, box_side)
                projected[3, top + row_offset, left + column_offset, digit] = 1.0

    return projected
# END article-divide


# BEGIN article-concur
def project_concur(values: FloatArray) -> FloatArray:
    """同じ候補に対する四つの複製を平均し、同じ値にそろえる。"""
    consensus = values.mean(axis=0, keepdims=True)
    return np.broadcast_to(consensus, values.shape).copy()
# END article-concur


def decode(values: FloatArray) -> Board:
    """合意した実数配列から、各マスで最大の候補を数字へ戻す。"""
    consensus = values.mean(axis=0)
    digits = np.argmax(consensus, axis=2) + 1
    return tuple(int(digit) for digit in digits.ravel())


# BEGIN article-difference-map
def solve(
    givens: Board,
    *,
    seed: int,
    max_iterations: int,
    tolerance: float,
    beta: float,
) -> Result:
    side, _ = board_geometry(givens)
    rng = np.random.default_rng(seed)
    values = rng.normal(size=(4, side, side, side))
    initial_residual = float("nan")
    final_residual = float("inf")

    for iteration in range(1, max_iterations + 1):
        # 局所制約を満たす点で反射し、その点を合意集合へ射影する。
        divided = project_divide(values, givens)
        concurred = project_concur(2.0 * divided - values)
        difference = concurred - divided
        final_residual = float(np.max(np.abs(difference)))
        if iteration == 1:
            initial_residual = final_residual

        # Difference Mapの一回分。残差0なら二つの射影結果が一致する。
        values = values + beta * difference
        if final_residual <= tolerance:
            candidate = decode(divided)
            valid, errors = validate_solution(candidate, givens)
            if valid:
                return Result(
                    status="solved",
                    seed=seed,
                    beta=beta,
                    tolerance=tolerance,
                    max_iterations=max_iterations,
                    iterations=iteration,
                    initial_residual=initial_residual,
                    final_residual=final_residual,
                    solution=candidate,
                )
            return Result(
                status="unknown",
                seed=seed,
                beta=beta,
                tolerance=tolerance,
                max_iterations=max_iterations,
                iterations=iteration,
                initial_residual=initial_residual,
                final_residual=final_residual,
                solution=None,
                validation_errors=errors,
            )

    # 反復上限までに交点へ到達しなくても、解なしとは結論しない。
    return Result(
        status="unknown",
        seed=seed,
        beta=beta,
        tolerance=tolerance,
        max_iterations=max_iterations,
        iterations=max_iterations,
        initial_residual=initial_residual,
        final_residual=final_residual,
        solution=None,
    )
# END article-difference-map


def describe(result: Result) -> str:
    lines = [
        f"status: {result.status}",
        f"seed: {result.seed}",
        f"beta: {result.beta:.9g}",
        f"tolerance: {result.tolerance:.9g}",
        f"max_iterations: {result.max_iterations}",
        f"iterations: {result.iterations}",
        f"initial_residual: {result.initial_residual:.9g}",
        f"final_residual: {result.final_residual:.9g}",
    ]
    if result.solution is not None:
        lines.extend(("solution:", format_board(result.solution)))
    if result.validation_errors:
        lines.append("validation_errors: " + "; ".join(result.validation_errors))
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Difference Mapで数独を解きます")
    parser.add_argument("board", type=Path)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--max-iterations", type=int, default=20_000)
    parser.add_argument("--tolerance", type=float, default=1e-8)
    parser.add_argument("--beta", type=float, default=0.5)
    args = parser.parse_args()
    if args.max_iterations < 1:
        parser.error("--max-iterationsには1以上を指定してください")
    if args.tolerance < 0:
        parser.error("--toleranceには0以上を指定してください")
    if not 0 < args.beta <= 1:
        parser.error("--betaには0より大きく1以下の値を指定してください")

    givens = load_board(args.board)
    result = solve(
        givens,
        seed=args.seed,
        max_iterations=args.max_iterations,
        tolerance=args.tolerance,
        beta=args.beta,
    )
    print(describe(result))


if __name__ == "__main__":
    main()
