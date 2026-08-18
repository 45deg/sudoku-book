"""Two exact backtracking solvers used by the first article."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

COMMON = Path(__file__).resolve().parents[1] / "common"
sys.path.insert(0, str(COMMON))

from sudoku import (  # noqa: E402
    Board,
    board_geometry,
    format_board,
    is_consistent_partial,
    load_board,
    validate_solution,
)


@dataclass
class SearchStats:
    nodes: int = 0
    branches: int = 0
    backtracks: int = 0
    eliminations: int = 0


@dataclass
class SolveResult:
    solutions: tuple[Board, ...]
    exhausted: bool
    stats: SearchStats

    @property
    def status(self) -> str:
        return "solved" if self.solutions else "unsat"


def legal_values(board: list[int], position: int, side: int, box_side: int) -> tuple[int, ...]:
    row, column = divmod(position, side)
    used = set(board[row * side : (row + 1) * side])
    used.update(board[column::side])
    box_row = (row // box_side) * box_side
    box_column = (column // box_side) * box_side
    used.update(
        board[r * side + c]
        for r in range(box_row, box_row + box_side)
        for c in range(box_column, box_column + box_side)
    )
    return tuple(value for value in range(1, side + 1) if value not in used)


# BEGIN article-naive-search
def naive_search(
    board: list[int],
    side: int,
    box_side: int,
    limit: int,
    solutions: list[Board],
    stats: SearchStats,
) -> bool:
    """空きマスを順に埋め、必要な個数の解が見つかったらTrueを返す。"""
    stats.nodes += 1

    # 左上から見て最初の空きマスを、次に仮置きする場所に選ぶ。
    try:
        position = board.index(0)
    except ValueError:
        # 空きマスがなければ完成している。
        solutions.append(tuple(board))
        return len(solutions) >= limit

    candidates = legal_values(board, position, side, box_side)
    for value in candidates:
        stats.branches += 1
        solutions_before = len(solutions)

        # 候補を一つ仮置きし、残りの空きマスを同じ方法で調べる。
        board[position] = value
        stop = naive_search(board, side, box_side, limit, solutions, stats)

        # 次の候補を試せるように、盤面を仮置き前へ戻す。
        board[position] = 0
        if stop:
            return True
        if len(solutions) == solutions_before:
            # この候補からは解が見つからなかった。
            stats.backtracks += 1
    return False
# END article-naive-search


def solve_naive(givens: Board, limit: int = 1) -> SolveResult:
    """Search the first empty cell without maintaining candidate sets."""
    if limit < 1:
        raise ValueError("limit must be positive")
    if not is_consistent_partial(givens):
        return SolveResult((), True, SearchStats())

    side, box_side = board_geometry(givens)
    board = list(givens)
    solutions: list[Board] = []
    stats = SearchStats()

    stopped_at_limit = naive_search(board, side, box_side, limit, solutions, stats)
    return SolveResult(tuple(solutions), not stopped_at_limit, stats)


@lru_cache(maxsize=4)
def _topology(side: int, box_side: int) -> tuple[tuple[tuple[int, ...], ...], tuple[tuple[int, ...], ...]]:
    all_units: list[tuple[int, ...]] = []
    all_units.extend(tuple(row * side + col for col in range(side)) for row in range(side))
    all_units.extend(tuple(row * side + col for row in range(side)) for col in range(side))
    for box_row in range(0, side, box_side):
        for box_col in range(0, side, box_side):
            all_units.append(
                tuple(
                    row * side + col
                    for row in range(box_row, box_row + box_side)
                    for col in range(box_col, box_col + box_side)
                )
            )

    units_by_position = tuple(
        tuple(unit for unit in all_units if position in unit)
        for position in range(side * side)
    )
    peers = tuple(
        tuple(sorted({peer for unit in units_by_position[position] for peer in unit} - {position}))
        for position in range(side * side)
    )
    return units_by_position, peers


@dataclass
class PropagationContext:
    units_by_position: tuple[tuple[tuple[int, ...], ...], ...]
    peers: tuple[tuple[int, ...], ...]
    givens: Board
    limit: int
    stats: SearchStats
    solutions: list[Board]


def eliminate(
    context: PropagationContext, state: list[int], position: int, bit: int
) -> bool:
    if not state[position] & bit:
        return True

    state[position] &= ~bit
    context.stats.eliminations += 1
    remaining = state[position]
    if remaining == 0:
        return False

    if remaining.bit_count() == 1:
        for peer in context.peers[position]:
            if not eliminate(context, state, peer, remaining):
                return False

    for unit in context.units_by_position[position]:
        places = [cell for cell in unit if state[cell] & bit]
        if not places:
            return False
        if len(places) == 1 and not assign(context, state, places[0], bit):
            return False
    return True


# BEGIN article-propagate
def assign(
    context: PropagationContext, state: list[int], position: int, bit: int
) -> bool:
    """一つの数字を確定し、候補の変化を周囲のマスへ伝える。"""
    # 確定する数字以外を、このマスの候補から一つずつ除く。
    other_bits = state[position] & ~bit
    while other_bits:
        removed = other_bits & -other_bits
        if not eliminate(context, state, position, removed):
            return False
        other_bits &= other_bits - 1
    return True
# END article-propagate


# BEGIN article-mrv-search
def propagating_search(context: PropagationContext, state: list[int]) -> bool:
    context.stats.nodes += 1

    # 候補が二つ以上あるマスだけが、これから仮置きする対象になる。
    unresolved = [
        (mask.bit_count(), position)
        for position, mask in enumerate(state)
        if mask.bit_count() > 1
    ]
    if not unresolved:
        # すべてのマスが一つの数字に決まったので、完成盤面を取り出す。
        solution = tuple(mask.bit_length() for mask in state)
        valid, _ = validate_solution(solution, context.givens)
        if valid:
            context.solutions.append(solution)
        return len(context.solutions) >= context.limit

    # 候補が最も少ないマスを選ぶ（MRV）。
    _, position = min(unresolved)
    candidates = state[position]
    while candidates:
        # 候補を一つ取り出して仮置きする。
        bit = candidates & -candidates
        candidates &= candidates - 1
        context.stats.branches += 1
        solutions_before = len(context.solutions)

        # 候補一覧を複製し、失敗した分岐の変更がほかへ混ざらないようにする。
        trial = state.copy()
        if assign(context, trial, position, bit) and propagating_search(context, trial):
            return True
        if len(context.solutions) == solutions_before:
            # この候補からは解が見つからなかった。
            context.stats.backtracks += 1
    return False
# END article-mrv-search


def solve_propagating(givens: Board, limit: int = 1) -> SolveResult:
    """Use singleton propagation, hidden singles, and MRV search."""
    if limit < 1:
        raise ValueError("limit must be positive")
    side, box_side = board_geometry(givens)
    units_by_position, peers = _topology(side, box_side)
    full_mask = (1 << side) - 1
    masks = [full_mask] * (side * side)
    stats = SearchStats()
    solutions: list[Board] = []
    context = PropagationContext(
        units_by_position, peers, givens, limit, stats, solutions
    )

    for position, value in enumerate(givens):
        if value and not assign(context, masks, position, 1 << (value - 1)):
            return SolveResult((), True, stats)

    stopped_at_limit = propagating_search(context, masks)
    return SolveResult(tuple(solutions), not stopped_at_limit, stats)


def describe_result(method: str, result: SolveResult, givens: Board, limit: int) -> str:
    lines = [
        f"status: {result.status}",
        f"method: {method}",
        f"solutions: {len(result.solutions)}",
        f"search exhausted: {'yes' if result.exhausted else 'no'}",
    ]
    if len(result.solutions) >= 2:
        lines.append("uniqueness: not unique")
    elif len(result.solutions) == 1 and result.exhausted:
        lines.append("uniqueness: unique")
    elif len(result.solutions) == 1 and limit == 1:
        lines.append("uniqueness: not checked")

    lines.extend(
        [
            f"nodes: {result.stats.nodes}",
            f"branches: {result.stats.branches}",
            f"backtracks: {result.stats.backtracks}",
            f"eliminations: {result.stats.eliminations}",
        ]
    )
    for number, solution in enumerate(result.solutions, start=1):
        valid, errors = validate_solution(solution, givens)
        lines.extend(["", f"solution {number} (valid: {'yes' if valid else 'no'}):", format_board(solution)])
        lines.extend(f"validation error: {error}" for error in errors)
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("board", type=Path)
    parser.add_argument("--method", choices=("naive", "propagate"), default="propagate")
    parser.add_argument("--limit", type=int, default=1)
    args = parser.parse_args()

    givens = load_board(args.board)
    solver = solve_naive if args.method == "naive" else solve_propagating
    result = solver(givens, limit=args.limit)
    print(describe_result(args.method, result, givens, args.limit))


if __name__ == "__main__":
    main()
