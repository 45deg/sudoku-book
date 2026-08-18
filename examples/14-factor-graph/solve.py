#!/usr/bin/env python3
"""Solve 4x4 Sudoku approximately with loopy belief propagation."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from itertools import permutations
from math import prod
from pathlib import Path
from typing import Literal

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "examples" / "common"))

from sudoku import (  # noqa: E402
    Board,
    board_geometry,
    format_board,
    load_board,
    units,
    validate_solution,
)

Method = Literal["sum-product", "max-product"]
Message = tuple[float, ...]


@dataclass(frozen=True)
class SolveResult:
    status: str
    method: Method
    iterations: int
    converged: bool
    residual: float
    ties: int
    solution: Board | None = None
    reason_unknown: str | None = None


def normalize(values: list[float]) -> Message | None:
    total = sum(values)
    if total == 0.0:
        return None
    return tuple(value / total for value in values)


# BEGIN article-factor-message
def all_different_message(
    incoming: list[Message] | tuple[Message, ...],
    target_position: int,
    method: Method,
) -> Message | None:
    """all-different因子から一つの変数へ送るメッセージを計算します。"""
    side = len(incoming)
    outgoing = [0.0] * side

    # 一つの順列が、因子を満たす数字の割り当て一通りに対応します。
    for assignment in permutations(range(side)):
        weight = prod(
            incoming[position][assignment[position]]
            for position in range(side)
            if position != target_position
        )
        target_digit = assignment[target_position]
        if method == "sum-product":
            # 周囲の全割り当てから届く重みを足し合わせます。
            outgoing[target_digit] += weight
        else:
            # 周囲の割り当てのうち、最大の重みだけを残します。
            outgoing[target_digit] = max(outgoing[target_digit], weight)

    return normalize(outgoing)
# END article-factor-message


def damp(old: Message, proposed: Message, damping: float) -> Message:
    return tuple(
        damping * old_value + (1.0 - damping) * new_value
        for old_value, new_value in zip(old, proposed, strict=True)
    )


def difference(first: Message, second: Message) -> float:
    return max(abs(left - right) for left, right in zip(first, second, strict=True))


def make_priors(board: Board, side: int) -> tuple[Message, ...]:
    uniform = tuple(1.0 / side for _ in range(side))
    priors: list[Message] = []
    for given in board:
        if given:
            priors.append(tuple(1.0 if digit == given - 1 else 0.0 for digit in range(side)))
        else:
            priors.append(uniform)
    return tuple(priors)


def decode(
    beliefs: tuple[Message, ...],
    board: Board,
    tie_tolerance: float,
) -> tuple[Board | None, int, str | None]:
    values: list[int] = []
    ties = 0
    for belief in beliefs:
        ranking = sorted(range(len(belief)), key=belief.__getitem__, reverse=True)
        if belief[ranking[0]] - belief[ranking[1]] <= tie_tolerance:
            ties += 1
        values.append(ranking[0] + 1)

    solution = tuple(values)
    if ties:
        return None, ties, "最大のbeliefが同点またはほぼ同点のマスがあります"
    valid, errors = validate_solution(solution, board)
    if not valid:
        return None, 0, "独立に選んだ最大beliefの盤面が数独の制約を満たしません"
    return solution, 0, None


# BEGIN article-propagation
def solve(
    board: Board,
    method: Method = "sum-product",
    *,
    max_iterations: int = 200,
    tolerance: float = 1e-10,
    damping: float = 0.5,
    tie_tolerance: float = 1e-7,
) -> SolveResult:
    side, _ = board_geometry(board)
    if side != 4:
        raise ValueError("この実装は4×4数独だけを対象にします")

    # 行、列、ブロックを、それぞれ一つのall-different因子にします。
    factors = units(board)
    priors = make_priors(board, side)
    edges_by_variable: list[list[tuple[int, int]]] = [
        [] for _ in range(len(board))
    ]
    for factor_id, unit in enumerate(factors):
        for position, variable in enumerate(unit):
            edges_by_variable[variable].append((factor_id, position))
    neighbors = tuple(tuple(edges) for edges in edges_by_variable)
    uniform = tuple(1.0 / side for _ in range(side))

    # 変数から因子へは初期値を、因子から変数へは一様な重みを送って始めます。
    variable_to_factor = [
        [priors[variable] for variable in unit] for unit in factors
    ]
    factor_to_variable = [[uniform for _ in unit] for unit in factors]

    # BEGIN article-message-loop
    residual = float("inf")
    for iteration in range(1, max_iterations + 1):
        new_factor_to_variable = [[uniform for _ in unit] for unit in factors]
        residual = 0.0

        # 各因子は、同じ単位にいるほかのマスの重みをまとめます。
        for factor_id, unit in enumerate(factors):
            incoming = variable_to_factor[factor_id]
            for position, variable in enumerate(unit):
                proposed = all_different_message(incoming, position, method)
                if proposed is None:
                    return SolveResult(
                        "unknown",
                        method,
                        iteration,
                        False,
                        residual,
                        0,
                        reason_unknown="因子から送れる正の重みがなくなりました",
                    )
                old = factor_to_variable[factor_id][position]
                # ループで値が振動しにくいよう、前回の値を半分残します。
                message = damp(old, proposed, damping)
                new_factor_to_variable[factor_id][position] = message
                residual = max(residual, difference(old, message))

        new_variable_to_factor = [[uniform for _ in unit] for unit in factors]
        # 各マスは、送り先以外の因子から届いた重みを掛け合わせます。
        for variable, edges in enumerate(neighbors):
            for target_factor, target_position in edges:
                weights = [
                    priors[variable][digit]
                    * prod(
                        new_factor_to_variable[factor_id][position][digit]
                        for factor_id, position in edges
                        if factor_id != target_factor
                    )
                    for digit in range(side)
                ]
                proposed = normalize(weights)
                if proposed is None:
                    return SolveResult(
                        "unknown",
                        method,
                        iteration,
                        False,
                        residual,
                        0,
                        reason_unknown="変数から送れる正の重みがなくなりました",
                    )
                old = variable_to_factor[target_factor][target_position]
                message = damp(old, proposed, damping)
                new_variable_to_factor[target_factor][target_position] = message
                residual = max(residual, difference(old, message))

        factor_to_variable = new_factor_to_variable
        variable_to_factor = new_variable_to_factor
        if residual < tolerance:
            break
    else:
        return SolveResult(
            "unknown",
            method,
            max_iterations,
            False,
            residual,
            0,
            reason_unknown="反復上限までにメッセージが収束しませんでした",
        )
    # END article-message-loop

    # BEGIN article-decode
    # 各変数のbeliefは、初期値と隣接因子から届いた全メッセージの積です。
    beliefs: list[Message] = []
    for variable, edges in enumerate(neighbors):
        weights = [
            priors[variable][digit]
            * prod(
                factor_to_variable[factor_id][position][digit]
                for factor_id, position in edges
            )
            for digit in range(side)
        ]
        belief = normalize(weights)
        if belief is None:
            return SolveResult(
                "unknown",
                method,
                iteration,
                True,
                residual,
                0,
                reason_unknown="beliefを正規化できませんでした",
            )
        beliefs.append(belief)

    solution, ties, reason = decode(tuple(beliefs), board, tie_tolerance)
    if solution is None:
        return SolveResult(
            "unknown",
            method,
            iteration,
            True,
            residual,
            ties,
            reason_unknown=reason,
        )
    return SolveResult("solved", method, iteration, True, residual, ties, solution)
    # END article-decode
# END article-propagation


def describe_result(result: SolveResult) -> str:
    lines = [
        f"status: {result.status}",
        f"method: {result.method}",
        f"iterations: {result.iterations}",
        f"converged: {'yes' if result.converged else 'no'}",
        f"residual: {result.residual:.3e}",
        f"ties: {result.ties}",
        "unique: undetermined",
    ]
    if result.reason_unknown:
        lines.append(f"reason_unknown: {result.reason_unknown}")
    if result.solution:
        lines.append("solution:")
        lines.append(format_board(result.solution))
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("board", type=Path)
    parser.add_argument(
        "--method",
        choices=("sum-product", "max-product"),
        default="sum-product",
    )
    parser.add_argument("--max-iterations", type=int, default=200)
    parser.add_argument("--tolerance", type=float, default=1e-10)
    parser.add_argument("--damping", type=float, default=0.5)
    args = parser.parse_args()
    if args.max_iterations < 1:
        parser.error("--max-iterationsには1以上を指定してください")
    if not 0.0 <= args.damping < 1.0:
        parser.error("--dampingには0以上1未満を指定してください")
    if args.tolerance <= 0.0:
        parser.error("--toleranceには正の値を指定してください")

    board = load_board(args.board)
    print(
        describe_result(
            solve(
                board,
                args.method,
                max_iterations=args.max_iterations,
                tolerance=args.tolerance,
                damping=args.damping,
            )
        )
    )


if __name__ == "__main__":
    main()
